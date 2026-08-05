"""Cross-platform, dependency-free query for currently available RAM.

Used by core._validate's memory-based iteration budget: the amount of
work iterate_polygon is willing to do is derived from how much memory
is actually free right now, not a machine-independent guess. Every
platform path degrades gracefully to a conservative fallback rather
than raising -- a failed memory query must never itself break
rendering.
"""

import os
import sys


def available_memory_bytes() -> int:
    """Return an estimate of currently available physical RAM, in bytes.

    Tries, in order:
      1. Windows: GlobalMemoryStatusEx (ctypes, stdlib only) -- gives a
         true "available right now" figure.
      2. Linux: /proc/meminfo's MemAvailable field -- also a true
         "available right now" figure (accounts for reclaimable cache,
         unlike MemFree).
      3. Any other POSIX platform (e.g. macOS): os.sysconf reports only
         *total* physical memory, not what's currently free -- treated
         as an upper bound and scaled down, since assuming all of it is
         free would be optimistic.
      4. If nothing above works: a conservative fixed fallback, so a
         failed query never raises or blocks rendering.

    Returns:
        Estimated available RAM in bytes.
    """
    if sys.platform == "win32":
        result = _windows_available_memory()
        if result is not None:
            return result
    elif sys.platform.startswith("linux"):
        result = _linux_available_memory()
        if result is not None:
            return result

    result = _posix_total_memory_estimate()
    if result is not None:
        return result

    # Nothing worked (exotic platform, sandboxed environment, permission
    # errors, ...) -- fall back to a conservative, fixed assumption
    # rather than letting a memory query failure break rendering.
    return 2 * 1024**3  # 2 GiB


def _windows_available_memory() -> int | None:
    try:
        import ctypes

        class MEMORYSTATUSEX(ctypes.Structure):
            _fields_ = [
                ("dwLength", ctypes.c_ulong),
                ("dwMemoryLoad", ctypes.c_ulong),
                ("ullTotalPhys", ctypes.c_ulonglong),
                ("ullAvailPhys", ctypes.c_ulonglong),
                ("ullTotalPageFile", ctypes.c_ulonglong),
                ("ullAvailPageFile", ctypes.c_ulonglong),
                ("ullTotalVirtual", ctypes.c_ulonglong),
                ("ullAvailVirtual", ctypes.c_ulonglong),
                ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
            ]

        stat = MEMORYSTATUSEX()
        stat.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
        if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(stat)):
            return None
        return int(stat.ullAvailPhys)
    except (OSError, AttributeError, ValueError):
        return None


def _linux_available_memory() -> int | None:
    try:
        with open("/proc/meminfo") as f:
            for line in f:
                if line.startswith("MemAvailable:"):
                    # Format: "MemAvailable:   12345678 kB"
                    kb = int(line.split()[1])
                    return kb * 1024
        return None
    except (OSError, ValueError, IndexError):
        return None


def _posix_total_memory_estimate() -> int | None:
    try:
        page_size = os.sysconf("SC_PAGE_SIZE")
        page_count = os.sysconf("SC_PHYS_PAGES")
        total = page_size * page_count
        # This is *total* physical memory, not what's actually free right
        # now (other processes, the OS itself, etc. are already using
        # some of it) -- scale down rather than assume it's all available.
        return total // 2
    except (OSError, ValueError, AttributeError):
        return None
