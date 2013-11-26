"""
 mbed CMSIS-DAP debugger
 Copyright (c) 2006-2013 ARM Limited

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

from interface import Interface
import logging, os

try:
    import usb.core
    import usb.util
except:
    if os.name == "posix":
        logging.error("PyUSB is required on a Linux Machine")

class PyUSB(Interface):
    """
    This class provides basic functions to access
    a USB HID device using pyusb:
        - write/read an endpoint
    """
    
    vid = 0
    pid = 0

    def __init__(self):
        self.ep_out = None
        self.ep_in = None
        self.dev = None
    
    @staticmethod
    def getAllConnectedInterface(vid, pid, interfaceClass=0x03):
        """
        returns all the connected devices which matches PyUSB.vid/PyUSB.pid,
        optionally, match a different usb interface class.
        CMSIS-DAP is HID =0x03, stlinkv2 is 0xff, vendor specific
        returns an array of PyUSB (Interface) objects
        """
        # find all devices matching the vid/pid specified
        all_devices = usb.core.find(find_all=True, idVendor=vid, idProduct=pid)
        
        if all_devices is None:
            logging.debug("No device connected")
            return None
        
        boards = []
        
        # iterate on all devices found
        for board in all_devices:
            intf_number = 0
            found = False
            
            # get active config
            config = board.get_active_configuration()
            
            # iterate on all interfaces:
            #    - if we found a suitable interface...
            for interface in config:
                if interface.bInterfaceClass == interfaceClass:
                    intf_number = interface.bInterfaceNumber
                    found = True
                    break
            
            if found == False:
                continue
            
            try:
                if board.is_kernel_driver_active(intf_number) is True:
                    board.detach_kernel_driver(intf_number)
            except Exception as e:
                print e
                pass
        
            intf = usb.util.find_descriptor(config, bInterfaceNumber = intf_number)
            # FIXME - this will need more work for stlinkv2 to get SWO working!
            for ep in intf:
                logging.info("karl - interface ep= %s=%s ", intf, ep)
            ep_out = usb.util.find_descriptor(intf,
                                              # match the first OUT endpoint
                                              custom_match = \
                                              lambda e: \
                                              usb.util.endpoint_direction(e.bEndpointAddress) == \
                                              usb.util.ENDPOINT_OUT
                                              )
            ep_in = usb.util.find_descriptor(intf,
                                             # match the first IN endpoint
                                             custom_match = \
                                             lambda e: \
                                             usb.util.endpoint_direction(e.bEndpointAddress) == \
                                             usb.util.ENDPOINT_IN
                                             )
            ep_trace = usb.util.find_descriptor(intf,
                                              custom_match = lambda e: usb.util.endpoint_address(e.bEndpointAddress) == 0x3
                                              )
            logging.info("karl - in = %s, out = %s, trace = %s", ep_in, ep_out, ep_trace)
            product_name = usb.util.get_string(board, 256, 2)
            vendor_name = usb.util.get_string(board, 256, 1)
            if ep_out is None or ep_in is None:
                logging.error('Endpoints not found')
                return None
            
            new_board = PyUSB()
            new_board.ep_in = ep_in
            new_board.ep_out = ep_out
            new_board.ep_trace = ep_trace
            new_board.dev = board
            new_board.vid = vid
            new_board.pid = pid
            new_board.product_name = product_name
            new_board.vendor_name = vendor_name
            boards.append(new_board)
            
        return boards
    
    def write(self, data):
        """
        write data on the OUT endpoint associated to the HID interface
        """
        if self.ep_out is None:
            raise ValueError('EP_OUT endpoint is NULL')
        
        self.ep_out.write(data)
        #logging.debug('sent: %s', data)
        return
        
    # FIXME - will need another method here for trace I guess?
    def read(self, timeout = -1, size = None):
        """
        read data on the IN endpoint associated to the HID interface
        optionally, specify a size to read, defaults to the IN endpoint's
        max packet size, which is appropriate for HID, but not necessarily correct for others
        """
        if self.ep_in is None:
            raise ValueError('EP_IN endpoint is NULL')
        if not size:
            size = self.ep_in.wMaxPacketSize
        
        data = self.ep_in.read(size, timeout)
        #logging.debug('received: %s', data)
        return data
