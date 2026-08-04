"""Shared pytest configuration.

Forces Matplotlib's non-interactive Agg backend before anything else in
the test session imports pyplot, so rendering tests never try to pop up
a real window (which would hang or fail in CI / headless environments).
"""

import matplotlib

matplotlib.use("Agg")
