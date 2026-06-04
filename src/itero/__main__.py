"""Console entrypoint for the itero command-line application.

This module is executed when the package is run with the Python -m switch.
It simply delegates execution to the CLI implementation in itero.cli.
"""

from itero.cli import cli


cli()