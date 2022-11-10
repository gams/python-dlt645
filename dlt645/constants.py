BROADCAST_ADDR = b"\xaa\xaa\xaa\xaa\xaa\xaa"
AWAKEN = 0xFE
START = 0x68
END = 0x16

# DL/T645 version / compatibility
DLT645_2007 = 2007
DLT645_1997 = 1997

# Control code values
MAIN = 0
STATION = 1
RESPONSE_CORRECT = 0
RESPONSE_INCORRECT = 1
NO_MORE_DATA = 0
MORE_DATA = 1


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
