"""Helper for tests that check that an input of growing size is handled in
linear time.

A statement that takes quadratic time on a long input would keep the test run
busy for minutes, and a regular expression cannot be interrupted from inside
the process. The statements therefore run one after another in a fresh
interpreter: it stops at the first one that is too slow, and the test fails
without waiting for it once ``deadline`` seconds have passed. The time is the
CPU time of the child, so a loaded runner does not make a fast statement look
slow.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

import dateparser

_ROOT = str(Path(dateparser.__file__).resolve().parent.parent)

_RUNNER = """
import sys, time
limit = float(sys.argv[1])
namespace = {}
exec(sys.argv[2], namespace)
for statement in sys.argv[3:]:
    code = compile(statement, "<statement>", "exec")
    start = time.process_time()
    exec(code, namespace)
    elapsed = time.process_time() - start
    print(elapsed, flush=True)
    if elapsed >= limit:
        break
"""


def measure(
    setup: str, statements: list[str], limit: float, deadline: float
) -> list[float]:
    """Return the CPU seconds of each statement until one takes ``limit`` or more.

    Fail if the interpreter does not finish within ``deadline`` seconds or a
    statement raises.
    """
    env = {
        **os.environ,
        "PYTHONPATH": os.pathsep.join([_ROOT, os.environ.get("PYTHONPATH", "")]),
    }
    try:
        result = subprocess.run(
            [sys.executable, "-c", _RUNNER, str(limit), setup, *statements],
            capture_output=True,
            text=True,
            timeout=deadline,
            env=env,
            check=False,
        )
    except subprocess.TimeoutExpired as error:
        output = error.stdout or b""
        done = (
            len(output.decode().split())
            if isinstance(output, bytes)
            else len(output.split())
        )
        pytest.fail(
            f"did not finish within {deadline} s, stuck on: {statements[min(done, len(statements) - 1)]}"
        )
    if result.returncode:
        pytest.fail(f"statement failed:\n{result.stderr[-2000:]}")
    return [float(line) for line in result.stdout.split()]


def assert_fast(
    setup: str, statements: list[str], limit: float = 1.0, deadline: float = 20.0
) -> None:
    """Fail unless every statement takes less than ``limit`` CPU seconds."""
    times = measure(setup, statements, limit, deadline)
    for statement, elapsed in zip(statements, times, strict=False):
        assert elapsed < limit, f"{statement} took {elapsed:.2f} s"
