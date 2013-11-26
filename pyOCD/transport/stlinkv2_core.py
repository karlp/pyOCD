import struct
__author__ = 'karlp'
# All magic numbers related to stlink, arm and stm32

STLINK_CMD_SIZE_V2          = 16

STLINK_GET_VERSION             = 0xF1
STLINK_DEBUG_COMMAND           = 0xF2
STLINK_DFU_COMMAND             = 0xF3
STLINK_SWIM_COMMAND            = 0xF4
STLINK_GET_CURRENT_MODE        = 0xF5
STLINK_GET_TARGET_VOLTAGE      = 0xF7

STLINK_MODE_DFU = 0
STLINK_MODE_MASS = 1
STLINK_MODE_DEBUG = 2
STLINK_MODE_SWIM = 3
STLINK_MODE_BOOTLOADER = 4

STLINK_DFU_EXIT = 0x7

STLINK_DEBUG_STATUS                = 0x01
STLINK_DEBUG_RESETSYS              = 0x03 # apiv1 from stlink-texane?!
STLINK_DEBUG_READMEM32             = 0x07
STLINK_DEBUG_WRITEMEM32            = 0x08
STLINK_DEBUG_RUNCORE               = 0x09
STLINK_DEBUG_ENTER_SWD             = 0xa3
STLINK_DEBUG_APIV2_ENTER           = 0x30
STLINK_DEBUG_APIV2_RESETSYS        = 0x32
STLINK_DEBUG_APIV2_READREG         = 0x33
STLINK_DEBUG_APIV2_WRITEREG        = 0x34
STLINK_DEBUG_APIV2_WRITEDEBUGREG   = 0x35
STLINK_DEBUG_APIV2_READDEBUGREG    = 0x36
STLINK_DEBUG_UNKNOWN_MAYBE_SYNC    = 0x3e
STLINK_DEBUG_EXIT                  = 0x21
STLINK_DEBUG_APIV2_START_TRACE_RX  = 0x40
STLINK_DEBUG_APIV2_STOP_TRACE_RX   = 0x41
STLINK_DEBUG_APIV2_GET_TRACE_NB    = 0x42


STLINK_EP_TRACE = 0x83
STLINK_EP_TX = 0x2
STLINK_EP_RX = 0x81


# ARM STUFF
SCS_LAR_KEY = 0xC5ACCE55
SCS_AIRCR = 0xe000ed0c
SCS_AIRCR_KEY = (0x05fa << 16)
SCS_AIRCR_VECTCLRACTIVE = (1<<1)

DCB_DEMCR = 0xE000EDFC
DCB_DEMCR_TRCENA = (1<<24)
DCB_DEMCR_VC_CORERESET = (1<<0)  # Enable Reset Vector Catch. This causes a Local reset to halt a running system.

DCB_DHCSR = 0xE000EDF0
DCB_DHCSR_DBGKEY = (0xA05F << 16)
DCB_DHCSR_C_DEBUGEN = (1<<0)
DCB_DHCSR_C_HALT = (1<<1)

TPIU_CSPSR = 0xe0040004
TPIU_ACPR = 0xE0040010
TPIU_SPPR = 0xE00400F0
TPIU_FFCR = 0xE0040304
TPIU_SPPR_TXMODE_PARALELL = 0
TPIU_SPPR_TXMODE_MANCHESTER = 1
TPIU_SPPR_TXMODE_NRZ = 2

ITM_LAR = 0xe0000fb0
ITM_TER = 0xe0000e00
ITM_TPR = 0xe0000e40
ITM_TCR = 0xe0000e80
ITM_TCR_SWOENA			= (1 << 4)
ITM_TCR_TXENA			= (1 << 3)
ITM_TCR_SYNCENA			= (1 << 2)
ITM_TCR_TSENA			= (1 << 1)
ITM_TCR_ITMENA			= (1 << 0)

DWT_CTRL = 0xE0001000

# STM32 stuff
DBGMCU_CR = 0xe0042004
DBGMCU_CR_DEBUG_SLEEP = (1<<0)
DBGMCU_CR_DEBUG_STOP = (1<<1)
DBGMCU_CR_DEBUG_STANDBY = (1<<2)
DBGMCU_CR_DEBUG_TRACE_IOEN = (1<<5)
DBGMCU_CR_RESERVED_MAGIC_UNKNOWN = (1<<8)
DBGMCU_APB1_FZ = 0xe0042008
DBGMCU_APB1_FZ_DBG_IWDG_STOP = (1<<12)


