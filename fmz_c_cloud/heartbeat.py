"""No-op in the cloud (the desktop restarter reads a heartbeat file; the cloud lane has none)."""


def beat(note=""):
    return None
