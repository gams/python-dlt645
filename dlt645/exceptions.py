class DLT645Error(Exception):
    pass


class ReadTimeoutError(DLT645Error):
    pass


class FrameStructureError(DLT645Error):
    pass


class FrameChecksumError(DLT645Error):
    pass
