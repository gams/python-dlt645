"""Definitions of constants used by DL/T645 protocol

Some constants are specific to 1997/2007 implementations.
"""

#: brodcast address - used when requesting a device address
BROADCAST_ADDR = b"\xaa\xaa\xaa\xaa\xaa\xaa"
#: bytes used as prefix to a request to wake up the device
#:
#: :meta hide-value:
AWAKEN = 0xFE
#: byte marking start of a frame or start of data block
#:
#: :meta hide-value:
START = 0x68
#: end of frame byte
#:
#: :meta hide-value:
END = 0x16

# DL/T645 version / compatibility
DLT645_2007 = 2007
DLT645_1997 = 1997

#: Transimission direction flag - comes from main
#:
#: :meta hide-value:
MAIN = 0
#: Transimission direction flag - comes from station
#:
#: :meta hide-value:
STATION = 1
#: station reponse flag - correct response
#:
#: :meta hide-value:
RESPONSE_CORRECT = 0
#: station reponse flag - incorrect response
#:
#: :meta hide-value:
RESPONSE_INCORRECT = 1
#: Follow up frame flag - No more data
#:
#: :meta hide-value:
NO_MORE_DATA = 0
#: Follow up frame flag - More data frames after this one
#:
#: :meta hide-value:
MORE_DATA = 1

#: Function codes for 2007 and 1997 implementations
#:
#: :meta hide-value:
FUNCTION_CODES = {
    DLT645_2007: {
        "READ_DATA": 0b10001,
        "READ_ADDR": 0b10011,
        "WRITE_DATA": 0b10100,
        "WRITE_ADDR": 0b10101,
        "SET_SPEED": 0b10111,
        "SET_PWD": 0b11000,
        "RESET_PWR": 0b11010,
    },
    DLT645_1997: {
        "READ_DATA": 0b00001,
        "READ_MORE": 0b00010,
        "READ_AGAIN": 0b00011,
        "WRITE_DATA": 0b00100,
        "BROADCAST_TIME": 0b01000,
        "WRITE_ADDR": 0b01010,
        "SET_SPEED": 0b01100,
        "SET_PWD": 0b01111,
        "RESET_DEMAND": 0b10000,
    },
}
