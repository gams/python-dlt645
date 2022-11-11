"""Main implementation of DL/T645 protocol and utilities

Usage:

.. code-block:: python

    import serial
    import dlt645


    ser = serial.Serial(
        "/dev/ttyUSB0",
        baudrate=1200,
        bytesize=serial.EIGHTBITS,
        parity=serial.PARITY_EVEN,
        stopbits=serial.STOPBITS_ONE,
        timeout=1
    )

    ser.write(dlt645.get_addr())

    frame = dlt645.read_frame(dlt645.iogen(ser))
    station_addr = frame.addr

    frame = dlt645.Frame(station_addr)
    frame.data = "00000000"
    framedata = dlt645.read_frame(serialgen(ser))
    print(framedata.data)

"""
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
from .exceptions import FrameChecksumError, FrameFormatError, ReadTimeoutError

b_awaken = AWAKEN.to_bytes(1, byteorder="big")
b_start = START.to_bytes(1, byteorder="big")
b_end = END.to_bytes(1, byteorder="big")


def iogen(flo):
    """Simple data generator for a file-like object, returns bytes one by one.

    :param flo: a file-like object instance
    """
    while True:
        byte = flo.read(1)
        if byte == b"":
            break
        yield byte


def read_frame(readgen):
    """Read a frame from a data generator, return a :class:`Frame` instance.

    :param generator readgen: a generator returning data one byte at a time
    """
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
    """Write a frame to byte form to be written on a data line

    :param dlt645.Frame frame: a :class:`Frame` instance
    :param bool awaken: whether to prefix the message with wake up bytes
    """
    if awaken is True:
        return 4 * b_awaken + frame.dump()
    else:
        return frame.dump()


class Frame:
    """DL/T645 frame representation with mechanisms to load/dump a frame
    from/into a data byte string.

    :param str addr: station address
    :param dict control: a constrol code representation
    """

    #: Protocol compatibitilty
    #:
    #: :meta hide-value:
    compat = DLT645_2007
    #: Raw frame data
    #:
    #: :meta hide-value:
    frame = None
    #: Station address
    #:
    #: :meta hide-value:
    addr = None
    #: Structure representing the control code portion of a frame in a more
    #: human readable way
    #:
    #: :meta hide-value:
    control = {
        "direction": MAIN,
        "response": RESPONSE_CORRECT,
        "more": NO_MORE_DATA,
        "function": FUNCTION_CODES[DLT645_2007]["READ_DATA"],
    }
    #: data portion of a frame
    #:
    #: :meta hide-value:
    data = None

    def __init__(self, addr=None, control=None):
        self.addr = addr
        if control is not None:
            self.control = control

    def __str__(self):
        return bytetostr(self.frame)

    def load(self, framedata):
        """Load a payload into a frame.

        :param bytearray framedata: a byte-like object holding a payload
        """
        if framedata[0] != START or framedata[7] != START or framedata[-1] != END:
            raise FrameFormatError(f"Format error in frame ({framedata})")

        self.frame = framedata
        if self.is_valid() is False:
            raise FrameChecksumError(f"Checksum error in frame ({framedata})")
        self.addr = bytetostr(load_addr(framedata[1:7]))
        self.control = load_ctrl(framedata[8])
        length = framedata[9]
        self.data = bytetostr(load_data(framedata[10 : 10 + length]))

    def dump(self):
        """Dump a frame as a byte-like object."""
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
        """Frame checksum"""
        if self.frame is None:
            return None

        return checksum(self.frame[:-2])

    def is_valid(self, cs=None):
        """Checksum validation

        :param cs: checksum byte
        """
        if cs is None:
            cs = self.frame[-2]

        return self.checksum == cs


def get_addr():
    """Return a byte-like payload to request an address from an unknown station"""
    return b"\xfe\xfe\xfe\xfe\x68\xaa\xaa\xaa\xaa\xaa\xaa\x68\x13\x00\xdf\x16"


def checksum(data):
    """Return the checksum of a byte-like object

    :param bytearray data: a byte-like object containing data to use for the checksum
    """
    return sum(data) & 0xFF


def bytetostr(bdata):
    """Convert a byte-like object to a string

    :param bytearray bdata: a byte-like payload
    """
    data = ""
    for byte in bdata:
        hex_str = hex(byte)[2:]
        data += hex_str.zfill(2)
    return data


def load_addr(data):
    """Read an address from a byte-like object, return a byte-like object
    representing the address.

    :param bytearray data: a byte-like payload
    """
    bdata = bytearray(data)
    bdata.reverse()
    return bdata


def dump_addr(addr):
    """Dump an address to a byte-like object.

    :param str addr: a station address
    """
    bdata = bytearray([int(addr[i : i + 2], 16) for i in range(0, len(addr), 2)])
    bdata.reverse()
    return bdata


def load_ctrl(data):
    """Read control code information, return a dict structure representing the
    different control code parts.

    :param bytearray data: a byte-like payload
    """
    ctrl = bytearray(data)[0]
    return {
        "direction": ctrl >> 7,
        "response": ctrl >> 6 & 0b01,
        "more": ctrl >> 5 & 0b001,
        "function": ctrl & 0b00011111,
    }


def dump_ctrl(control):
    """Dump a control code representation to a byte-like object.

    :param dict control: a control code representation
    """
    dir = control["direction"] << 7
    resp = control["response"] << 6
    more = control["more"] << 5
    func = control["function"]
    ctrl = dir + resp + more + func
    return ctrl.to_bytes(1, byteorder="big")


def load_data(data):
    """Read data information, return a byte-like structure representing the
    data.

    :param bytearray data: a byte-like payload
    """
    bdata = bytearray(data)
    bdata.reverse()
    retdata = bytearray()
    for byte in bdata:
        retdata.append(byte - 0x33)

    return retdata


def dump_data(data):
    """Dump a data payload to a byte-like object.

    :param str data: a data payload
    """
    if data is None:
        return b""

    bdata = bytearray([int(data[i : i + 2], 16) + 0x33 for i in range(0, len(data), 2)])
    bdata.reverse()
    return bdata
