pyOCD
=====
pyOCD is an Open Source python library or programming and debugging 
ARM Cortex-M microcontrollers using CMSIS-DAP.

You can use the following interfaces:

1. From a python interpretor:
  * halt, step, resume execution
  * read/write memory
  * read/write block memory
  * read-write core register
  * set/remove hardware breakpoints
  * flash new binary
  * reset
2. From a GDB client, you have all the features provided by gdb:
  * load a .elf file
  * read/write memory
  * read/write core register
  * set/remove hardware breakpoints
  * high level stepping
  * ...

Dependencies
------------
pyOCD relies on external libraries:

* Windows: [pyWinUSB](https://github.com/rene-aguirre/pywinusb):

```
$ cd /path-to-pywinusb/
$ python setup.py install
```

* Linux: [pyUSB](https://github.com/walac/pyusb):

```
$ sudo apt-get install python libusb-1.0-0-dev
$ cd /path-to-pyusb/
$ sudo python setup.py install
```

Fedora: "yum install pyusb" is sufficient.  On Ubuntu, the packaged
version of pyusb is still 0.4, which is NOT sufficient!

* Mac:
    So far Mac OS X is not supported
    
    
Installation
------------
```
$ cd /path-to-pyOCD/
$ python setup.py install
```
    
Examples
--------
### Tests
A series of tests are on the test directory:
* basic_test.py: simple test that checks:
  * read/write core registers
  * read/write memory
  * stop/resume/step the execution
  * reset the target
  * flash a binary
* gdb_test.py: launch a gdbserver

### Hello World example
```python
from pyOCD.board import MbedBoard

import logging
logging.basicConfig(level=logging.INFO)

board = MbedBoard.chooseBoard()

target = board.target
flash = board.flash
target.resume()
target.halt()

print "pc: 0x%X" % target.readCoreRegister("pc")
    pc: 0xA64

target.step()
print "pc: 0x%X" % target.readCoreRegister("pc")
    pc: 0xA30

target.step()
print "pc: 0x%X" % target.readCoreRegister("pc")
   pc: 0xA32

flash.flashBinary("binaries/l1_lpc1768.bin")
print "pc: 0x%X" % target.readCoreRegister("pc")
   pc: 0x10000000

target.reset()
target.halt()
print "pc: 0x%X" % target.readCoreRegister("pc")
   pc: 0xAAC

board.uninit()
```

###GDB server example
Python:
```python
from pyOCD.gdbserver import GDBServer
from pyOCD.board import MbedBoard

import logging
logging.basicConfig(level=logging.INFO)

board = MbedBoard.chooseBoard()

# start gdbserver
gdb = GDBServer(board, 3333)
```
gdb server:
```
arm-none-eabi-gdb basic.elf

<gdb> target remote localhost:3333
<gdb> load
<gdb> continue

```

Architecture
------------

### Interface
An interface does the link between the target and the computer.
This module contains basic functionalities to write and read data to and from
an interface. You can inherit from ```Interface``` and overwrite ```read()```, ```write()```,...

Then declare your interface in ```INTERFACE``` (in ```pyOCD.interface.__init__.py```)

### Target
A target defines basic functionalities such as ```step```, ```resume```, ```halt```, ```readMemory```,...
You can inherit from Target to implement your own methods.

Then declare your target in TARGET (in ```pyOCD.target.__init__.py```)

### Transport
Defines the transport used to communicate. In particular, you can find CMSIS-DAP. 
Implements methods such as ```memWriteAP```, ```memReadAP```, ```writeDP```, ```readDP```, ...

You can inherit from ```Transport``` and implement your own methods.
Then declare your transport in ```TRANSPORT``` (in ```pyOCD.transport.__init__.py```)

### Flash
Contains flash algorithm in order to flash a new binary into the target.

### gdbserver
Start a GDB server. The server listens on a specific port. You can then
connect a GDB client to it and debug/program the target

Then you can debug a board which is composed by an interface, a target, a transport and a flash

For further information on the GDB server: see
[http://www.embecosm.com/appnotes/ean4/embecosm-howto-rsp-server-ean4-issue-2.html#id3033275]
Alternative pieces: [http://code.google.com/p/pydevtools/source/browse/trunk/bintools/gdb/rsp.py]
http://mspgcc.cvs.sourceforge.net/viewvc/mspgcc/msp430simu/gdbserver.py?view=markup

