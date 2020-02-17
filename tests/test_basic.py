"""Basic test."""

import sys
import tempfile
import os.path
import queue

import teetime

CWD = os.path.dirname(os.path.abspath(__file__))


def test_basic():
    """Basic test."""
    with tempfile.TemporaryFile() as fout,\
            tempfile.TemporaryFile() as ferr,\
            tempfile.TemporaryFile() as fboth:
        process = teetime.popen_call(
            ['python', os.path.join(CWD, 'test.py')],
            stdout=(sys.stdout.buffer, fout, fboth),
            stderr=(sys.stderr.buffer, ferr, fboth),
        )
        process.wait()

        assert fout.read() == (
            b'lHl o!lreo\r\n!\r\noWd H\r\nlHlWd\r\n!l\r\n'
        )
        assert ferr.read() == (
            b'doWlloHer\r\nHlWd\r\ndelWlHlor\r\n olrdl!He\r\nHolWlloe\r\n'
        )
        assert fboth.read() == (
            b'doWlloHer\r\nHlWd\r\nlHl o!lreo\r\n!\r\noWd H\r\n'
            b'lHlWd\r\ndelWlHlor\r\n olrdl!He\r\nHolWlloe\r\n!l\r\n'
        )


def _iter_queue(q):
    while not q.empty():
        yield q.get()


def test_queue():
    """Basic test."""
    q = queue.Queue()
    process = teetime.popen_call(
        ['python', os.path.join(CWD, 'test.py')],
        stdout=(q,),
        stderr=(q,),
    )
    process.wait()

    assert list(_iter_queue(q)) == [
        b'doWlloHer\r\n',
        b'HlWd\r\n',
        b'lHl o!lreo\r\n',
        b'!\r\n',
        b'oWd H\r\n',
        b'lHlWd\r\n',
        b'delWlHlor\r\n',
        b' olrdl!He\r\n',
        b'HolWlloe\r\n',
        b'!l\r\n',
    ]
