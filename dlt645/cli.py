"""Main module to declare CLI commands. Those commands should be declared as
script entry points in the ``[tool.poetry.script]`` section (see `poetry
documentation <https://python-poetry.org/docs/pyproject/#scripts>`_) of
``pyproject.toml``.
"""
import argparse
import sys

import serial

from . import get_active_energy, get_addr


def ser_args(parser):
    parser.add_argument(
        "-p",
        "--port",
        default="/dev/ttyUSB0",
        type=str,
        help="Serial port to use, defaults to '/dev/ttyUSB0'",
    )
    parser.add_argument(
        "-b", "--baudrate", default=1200, type=int, help="Baud rate, defaults to 1200"
    )
    parser.add_argument(
        "-B",
        "--bytesize",
        default=serial.EIGHTBITS,
        type=int,
        help=f"Number of data bits, defaults to {serial.EIGHTBITS}",
    )
    parser.add_argument(
        "-P",
        "--parity",
        default=serial.PARITY_EVEN,
        type=str,
        help=f"Parity check, defaults to '{serial.PARITY_EVEN}' (even)",
    )
    parser.add_argument(
        "-s",
        "--stopbits",
        default=serial.STOPBITS_ONE,
        type=int,
        help=f"Number of stop bits, defaults to {serial.STOPBITS_ONE}",
    )
    parser.add_argument(
        "-t",
        "--timeout",
        default=5,
        type=float,
        help="Read/write timeout value in seconds, defaults to 5",
    )


def getaddr():
    """Entry point for CLI requesting a station's address through serial port.

    By default, use the USB port '``/dev/ttyUSB0``' and common serial
    communication definition: 1200 baud, 8bits, parity even, 1 stop bit.

    Usage:

    .. code-block:: shell

        $ dlt645_getaddr
        Station address: 000022076396
    """
    description = "Get station's DL/T645 address through serial port"
    parser = argparse.ArgumentParser(description=description)
    ser_args(parser)
    args = parser.parse_args()

    try:
        ser = serial.Serial(
            args.port,
            baudrate=args.baudrate,
            bytesize=args.bytesize,
            parity=args.parity,
            stopbits=args.stopbits,
            timeout=args.timeout,
            write_timeout=args.timeout,
        )
    except serial.serialutil.SerialException as e:
        sys.stderr.write("{}\n".format(str(e)))
        sys.exit(1)

    addr = get_addr(ser)
    sys.stdout.write(f"Station address: {addr}\n")


def getaen():
    """Entry point for CLI requesting a station's active energy through serial port.

    By default, use the USB port '``/dev/ttyUSB0``' and common serial
    communication definition: 1200 baud, 8bits, parity even, 1 stop bit.

    Usage:

    .. code-block:: shell

        $ dlt645_getaen
        Active energy: 259.7 kWh
    """
    description = "Get station's active energy through serial port"
    description = "Get station's DL/T645 address through serial port"
    parser = argparse.ArgumentParser(description=description)
    ser_args(parser)
    parser.add_argument(
        "address",
        nargs="?",
        type=str,
        help="Station's address, if not provided, request it.",
    )
    args = parser.parse_args()

    try:
        ser = serial.Serial(
            args.port,
            baudrate=args.baudrate,
            bytesize=args.bytesize,
            parity=args.parity,
            stopbits=args.stopbits,
            timeout=args.timeout,
            write_timeout=args.timeout,
        )
    except serial.serialutil.SerialException as e:
        sys.stderr.write("{}\n".format(str(e)))
        sys.exit(1)

    if args.address is None:
        addr = get_addr(ser)
        sys.stdout.write(f"Station address: {addr}\n")
    else:
        addr = args.address

    value = get_active_energy(addr, ser)
    sys.stdout.write(f"Active energy: {value} kWh\n")
