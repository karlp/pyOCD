"""
 Copyright (c) 2013 Karl Palsson

 Licensed under the Apache License, Version 2.0 (the "License");
 you may not use this file except in compliance with the License.
 You may obtain a copy of the License at

     http://www.apache.org/licenses/LICENSE-2.0

 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License.
"""

from transport import Transport
import logging
import struct
from time import sleep

from stlinkv2_core import *

lame_py = None
def _lame_py_buffer_required(inp):
    return buffer(inp)

def _lame_py_buffer_not_required(inp):
    return inp

try:
    blob = [1,2,3,4]
    struct.unpack_from("<I", bytearray(blob))
    lame_py = _lame_py_buffer_not_required
    print("don't need lame pyt fix")
except TypeError:
    lame_py = _lame_py_buffer_required
    print(":( lame py required :(")


def stlink_pad(cmd):
    # Both actually seem to work....
    #return cmd
    return stlink_pad_real(cmd)

def stlink_pad_real(cmd):
    """
    make a zero buffer and fill the command in on top of it.  not very pretty :(
    """
    msg = [0 for x in range(STLINK_CMD_SIZE_V2)]
    for i,x in enumerate(cmd):
        msg[i] = x
    return msg

def xfer_normal_input(dev, cmd, expected_response_size, verbose=False):
    msg = stlink_pad(cmd)
    if verbose:
        print("Sending msg: ", msg)
    count = dev.write(msg)
    # pyOCD doesn't return count of bytes written....
    #assert count == len(msg), "Failed to write cmd to usb"
    if expected_response_size:
        res = dev.read(size=expected_response_size)
        if verbose:
            print("Received: ", res)
        return res

class STLinkVersion():
    def __init__(self, blob):
        # blob = [36, 0, 131, 4, 72, 55]
        # Info : STLINK v2 JTAG v16 API v2 SWIM v0 VID 0x0483 PID 0x3748
        # woo, different byte ordering!
        ver = struct.unpack_from(">H", lame_py(blob[:2]))[0]
        self.vid, self.pid = struct.unpack_from("<HH", lame_py(blob[2:]))

        self.major_ver = (ver >> 12) & 0x0f
        self.jtag_ver = (ver >> 6) & 0x3f
        self.swim_ver = ver & 0x3f
        self.api_ver = 1
        if self.jtag_ver > 11:
            self.api_ver = 2

    def __repr__(self):
        return "STLINK v%d JTAG v%d API v%d SWIM v%d, VID %#x PID %#x" % (
            self.major_ver,
            self.jtag_ver,
            self.api_ver,
            self.swim_ver,
            self.vid,
            self.pid
        )



class STLINKv2(Transport):
    """
    This class implements the stlinkv2 protocol
    """
    def __init__(self, interface):
        self.interface = interface
        self._current_mode = None
        return
    
    def init(self):
        self.version = self.get_version()
        print(self.version)
        self.get_mode()
        self.leave_state()

        if self.version.jtag_ver >= 13:
            volts = self.get_voltage()
            print("Voltage: ", volts)

        self.enter_state_debug()
        return

    def get_version(self):
        res = xfer_normal_input(self.interface, [STLINK_GET_VERSION, 0x80], 6)
        v = STLinkVersion(res)
        return v

    def get_mode(self):
        res = xfer_normal_input(self.interface, [STLINK_GET_CURRENT_MODE], 2)[0]
        logging.debug("Get mode returned: %d", res)
        self._current_mode = res
        return res

    def leave_state(self):
        cmd = None
        logging.debug("Current saved mode is %d" %  self._current_mode)
        if self._current_mode == STLINK_MODE_DFU:
            logging.debug("Leaving dfu mode")
            cmd = [STLINK_DFU_COMMAND, STLINK_DFU_EXIT]
            self._current_mode = 1 # "exit dfu" moves from mode 0 -> mode 1
        elif self._current_mode == STLINK_MODE_DEBUG:
            logging.debug("Leaving debug mode")
            cmd = [STLINK_DEBUG_COMMAND, STLINK_DEBUG_EXIT]
            self._current_mode = 1 # exit debug goes from mode 2 -> mode 1

        if cmd:
            xfer_normal_input(self.interface, cmd, 0)
        else:
            logging.debug("Ignoring mode we don't know how to leave/or need to leave")

    def get_voltage(self):
        res = xfer_normal_input(self.interface, [STLINK_GET_TARGET_VOLTAGE], 8)
        adc0, adc1 = struct.unpack_from("<II", lame_py(res))
        print(adc0, adc1)
        assert adc0 != 0
        return 2 * adc1 * (1.2 / adc0)

    def enter_state_debug(self):
        cmd = [STLINK_DEBUG_COMMAND, STLINK_DEBUG_APIV2_ENTER, STLINK_DEBUG_ENTER_SWD]
        res = xfer_normal_input(self.interface, cmd, 2)
        logging.debug("enter debug state returned: %s", res)
        # res[0] should be 0x80
        assert res[0] == 0x80, "enter state failed :("
        self._current_mode = 2

    def trace_off(self):
        cmd = [STLINK_DEBUG_COMMAND, STLINK_DEBUG_APIV2_STOP_TRACE_RX]
        res = xfer_normal_input(self.interface, cmd, 2)
        logging.debug("STOP TRACE")

    
    def uninit(self):
        self.trace_off()
        self.leave_state()
        s = self.get_mode()
        print("Disconnected with state in %d" % s)

        return
    
    def info(self, request):
        return self.version
    
