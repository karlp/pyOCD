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

import sys, os
import logging, array

from time import sleep
from board import Board
from pyOCD.interface import INTERFACE

TARGET_TYPE = {"1010": "lpc1768",
               "0200": "kl25z",
               "1040": "lpc11u24",
               "0300": "lpc800",
               }


usb_backend = ""
if os.name == "nt":
    usb_backend = "pywinusb"
elif os.name == "posix":
    usb_backend = "pyusb"
    
_usb_vid = 0x0483
_usb_pid = 0x3748

class DiscoBoard(Board):
    """
    This class inherits from Board and is specific to STM32 Discovery boards.
    """
    def __init__(self, target, flash, interface, transport = "stlinkv2"):
        """
        Init the board
        """
        Board.__init__(self, target, flash, interface, transport)
        self.unique_id = ""
        self.target_type = ""
    
    def getUniqueID(self):
        """
        Return the unique id of the board
        """
        return self.unique_id
    
    def getTargetType(self):
        """
        Return the type of the board
        """
        return self.target_type
    
    def getInfo(self):
        """
        Return info on the board
        """
        return Board.getInfo(self) + " [" + self.target_type + "]"

    @staticmethod
    def getAllConnectedBoards(transport = "stlinkv2", close = False, blocking = True):
        """
        Return an array of all mbed boards connected
        """
        first = True
        while True:
            while True:
                all_boards = INTERFACE[usb_backend].getAllConnectedInterface(_usb_vid, _usb_pid, interfaceClass=0xff)
                if all_boards != None or not blocking:
                    break
                if (first == True):
                    logging.info("Waiting for a USB device connected")
                    first = False
                sleep(0.2)
                
            boards = []
            for board in all_boards:
                ### FIXME - this isn't right!
                #board.write([0x80])
                #u_id_ = board.read()
                try:
                    #target_type = array.array('B', [i for i in u_id_[2:6]]).tostring()
                    #target_type = TARGET_TYPE[target_type]
                    # XXX FIXME this isn't good enough! Can this even be done now?
                    new_board = DiscoBoard("target_stm32l1", None, board, transport)
                    new_board.target_type = "unknown"
                    #new_board.unique_id = array.array('B', [i for i in u_id_[2:2+u_id_[1]]]).tostring()
                    logging.info("new board id detected: %s", board)
                    boards.append(new_board)
                    if close:
                        board.close()
                except Exception as e:
                    print "received exception: %s" % e
                    board.close()
            
            if len(boards) > 0 or not blocking:
                return boards
            
            if (first == True):
                logging.info("Waiting for a USB device connected")
                first = False
    
    @staticmethod
    def chooseBoard(transport = "stlinkv2", blocking = True, return_first = False):
        """
        Allow you to select a board among all boards connected
        """
        all_boards = DiscoBoard.getAllConnectedBoards(transport, False, blocking)
        
        if all_boards == None:
            return None
        
        index = 0
        for board in all_boards:
            print "%d => %s" % (index, board.getInfo())
            index += 1
        
        if len(all_boards) == 1:
            all_boards[0].init()
            return all_boards[0]
        
        try:
            ch = 0
            if not return_first:
                while True:
                    ch = sys.stdin.readline()
                    sys.stdin.flush()
                    if (int(ch) < 0) or (int(ch) >= len(all_boards)):
                        logging.info("BAD CHOICE: %d", int(ch))
                        index = 0
                        for board in all_boards:
                            print "%d => %s" % ( index, board.getInfo())
                            index += 1
                    else:
                        break
            # close all others mbed connected
            for board in all_boards:
                if board != all_boards[int(ch)]:
                    board.interface.close()
        
            all_boards[int(ch)].init()
            return all_boards[int(ch)]
        except Exception as e:
            try:
                print e
            except:
                pass
            finally:
                for board in all_boards:
                    board.interface.close()
