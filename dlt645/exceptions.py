class DLT645Error(Exception):
    """Base parent exception"""

    pass


class ReadTimeoutError(DLT645Error):
    """Raised when a read timeout occurs"""

    pass


class FrameFormatError(DLT645Error):
    """Raised when a frame is not following the standard format"""

    pass


class FrameChecksumError(DLT645Error):
    """Raised when the checksum test fails"""

    pass
