from itero._memory import (
    _linux_available_memory,
    _posix_total_memory_estimate,
    _windows_available_memory,
    available_memory_bytes,
)


def test_returns_a_positive_int():
    result = available_memory_bytes()

    assert isinstance(result, int)
    assert result > 0


def test_falls_back_to_a_fixed_conservative_value_when_every_path_fails(monkeypatch):
    """Regression: a failed memory query must never raise or block
    rendering -- it must always degrade to a conservative fixed
    estimate instead."""
    monkeypatch.setattr("itero._memory.sys.platform", "some-exotic-platform")
    monkeypatch.setattr("itero._memory._posix_total_memory_estimate", lambda: None)

    result = available_memory_bytes()

    assert result == 2 * 1024**3


def test_prefers_windows_path_on_win32(monkeypatch):
    monkeypatch.setattr("itero._memory.sys.platform", "win32")
    monkeypatch.setattr("itero._memory._windows_available_memory", lambda: 12345)

    assert available_memory_bytes() == 12345


def test_prefers_linux_path_on_linux(monkeypatch):
    monkeypatch.setattr("itero._memory.sys.platform", "linux")
    monkeypatch.setattr("itero._memory._linux_available_memory", lambda: 6789)

    assert available_memory_bytes() == 6789


def test_falls_back_to_posix_estimate_when_platform_specific_path_fails(monkeypatch):
    monkeypatch.setattr("itero._memory.sys.platform", "linux")
    monkeypatch.setattr("itero._memory._linux_available_memory", lambda: None)
    monkeypatch.setattr("itero._memory._posix_total_memory_estimate", lambda: 999)

    assert available_memory_bytes() == 999


def test_windows_path_handles_missing_windll_gracefully(monkeypatch):
    """Calling the Windows-specific path on a non-Windows machine (or
    any environment where ctypes.windll doesn't exist) must return None,
    not raise."""
    import ctypes

    if hasattr(ctypes, "windll"):
        # Actually on Windows -- nothing to simulate, just confirm it
        # returns a sane value without raising.
        result = _windows_available_memory()
        assert result is None or (isinstance(result, int) and result > 0)
    else:
        assert _windows_available_memory() is None


def test_linux_meminfo_parsing(tmp_path, monkeypatch):
    fake_meminfo = tmp_path / "meminfo"
    fake_meminfo.write_text("MemTotal:       16000000 kB\nMemAvailable:    4000000 kB\n")

    real_open = open

    def fake_open(path, *args, **kwargs):
        if path == "/proc/meminfo":
            return real_open(fake_meminfo, *args, **kwargs)
        return real_open(path, *args, **kwargs)

    monkeypatch.setattr("builtins.open", fake_open)

    assert _linux_available_memory() == 4_000_000 * 1024


def test_linux_meminfo_parsing_handles_missing_file(monkeypatch):
    def fake_open(path, *args, **kwargs):
        raise OSError("no such file")

    monkeypatch.setattr("builtins.open", fake_open)

    assert _linux_available_memory() is None


def test_posix_total_memory_estimate_handles_missing_sysconf(monkeypatch):
    """os.sysconf doesn't exist on Windows at all -- must degrade
    to None, not raise AttributeError."""
    import os

    if hasattr(os, "sysconf"):
        result = _posix_total_memory_estimate()
        assert result is None or (isinstance(result, int) and result > 0)
    else:
        assert _posix_total_memory_estimate() is None
