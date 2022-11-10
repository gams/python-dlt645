from .__meta__ import __version__  # noqa: F401
from .constants import (
    AWAKEN,
    BROADCAST_ADDR,
    DLT645_2007,
    END,
    FUNCTION_CODES,
    MAIN,
    NO_MORE_DATA,
    RESPONSE_CORRECT,
    START,
)
from .exceptions import FrameChecksumError, FrameStructureError, ReadTimeoutError

b_awaken = AWAKEN.to_bytes(1, byteorder="big")
b_start = START.to_bytes(1, byteorder="big")
b_end = END.to_bytes(1, byteorder="big")


def read_frame(readgen):
    framedata = bytearray()
    for byte in readgen:
        if byte == b"":
            raise ReadTimeoutError

        if byte == b_awaken:
            continue

        framedata.extend(bytearray(byte))

        if byte == b_end:
            frame = Frame()
            frame.load(framedata)
            return frame


def write_frame(frame, awaken=True):
    if awaken is True:
        return b_awaken + frame.dump()
    else:
        return frame.dump()


class Frame:
    compat = DLT645_2007
    frame = None
    addr = None
    control = {
        "direction": MAIN,
        "response": RESPONSE_CORRECT,
        "more": NO_MORE_DATA,
        "function": FUNCTION_CODES[DLT645_2007]["READ_DATA"],
    }
    data = None

    def __init__(self, addr=None, control=None):
        self.addr = addr
        if control is not None:
            self.control = control

    def __str__(self):
        return bytetostr(self.frame)

    def load(self, framedata):
        if framedata[0] != START or framedata[7] != START or framedata[-1] != END:
            raise FrameStructureError(f"Structure error in frame ({framedata})")

        self.frame = framedata
        if self.is_valid() is False:
            raise FrameChecksumError(f"Checksum error in frame ({framedata})")
        self.addr = bytetostr(load_addr(framedata[1:7]))
        self.control = load_ctrl(framedata[8])
        length = framedata[9]
        self.data = bytetostr(load_data(framedata[10 : 10 + length]))

    def dump(self):
        if self.addr is None:
            addr = BROADCAST_ADDR
        else:
            addr = dump_addr(self.addr)

        ctrl = dump_ctrl(self.control)
        data = dump_data(self.data)
        length = len(data)
        b_length = length.to_bytes(1, byteorder="big")

        framedata = b_start + addr + b_start + ctrl + b_length + data
        cs = checksum(framedata)
        b_cs = cs.to_bytes(1, byteorder="big")
        return framedata + b_cs + b_end

    @property
    def checksum(self):
        if self.frame is None:
            return None

        return checksum(self.frame[:-2])

    def is_valid(self, cs=None):
        if cs is None:
            cs = self.frame[-2]

        return self.checksum == cs


def get_addr():
    return b"\xfe\xfe\xfe\xfe\x68\xaa\xaa\xaa\xaa\xaa\xaa\x68\x13\x00\xdf\x16"


def checksum(data):
    return sum(data) & 0xFF


def bytetostr(bdata):
    data = ""
    for byte in bdata:
        hex_str = hex(byte)[2:]
        data += hex_str.zfill(2)
    return data


def load_addr(data):
    bdata = bytearray(data)
    bdata.reverse()
    return bdata


def dump_addr(addr):
    bdata = bytearray([int(addr[i : i + 2], 16) for i in range(0, len(addr), 2)])
    bdata.reverse()
    return bdata


def load_ctrl(data):
    ctrl = bytearray(data)[0]
    return {
        "direction": ctrl >> 7,
        "response": ctrl >> 6 & 0b01,
        "more": ctrl >> 5 & 0b001,
        "function": ctrl & 0b00011111,
    }


def dump_ctrl(control):
    dir = control["direction"] << 7
    resp = control["response"] << 6
    more = control["more"] << 5
    func = control["function"]
    ctrl = dir + resp + more + func
    return ctrl.to_bytes(1, byteorder="big")


def load_data(data):
    bdata = bytearray(data)
    bdata.reverse()
    retdata = bytearray()
    for byte in bdata:
        retdata.append(byte - 0x33)

    return retdata


def dump_data(data):
    if data is None:
        return b""

    bdata = bytearray([int(data[i : i + 2], 16) + 0x33 for i in range(0, len(data), 2)])
    bdata.reverse()
    return bdata
