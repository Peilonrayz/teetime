"""Basic test."""

import os.path
import queue
import sys
import tempfile

import teetime

CWD = os.path.dirname(os.path.abspath(__file__))
SEP = b'\n'  # Windows is b'\r\n'


class PeekIter:
    def __init__(self, values):
        self.values = iter(values)
        self.peek = next(self.values, None)
    
    def next(self):
        if self.peek is None:
            raise StopIteration()
        value = self.peek
        self.peek = next(self.values, None)
        return value


def order(expected, *peekers):
    for item in expected:
        for peeker in peekers:
            if peeker.peek == item:
                yield peeker.next()
                break
        else:
            for peeker in peekers:
                if peeker.peek is not None:
                    yield peeker.next()
                    break
            else:
                return


def build_output(expected, *values, sep=SEP, ext=[b""]):
    _order = order(
        expected.split(sep),
        *(
            PeekIter(value)
            for value in values
        ),
    )
    return sep.join(list(_order) + ext)


def test_basic():
    """Basic test."""
    STD_OUT = [b"lHl o!lreo", b"!", b"oWd H", b"lHlWd", b"!l"]
    STD_ERR = [b"doWlloHer", b"HlWd", b"delWlHlor", b" olrdl!He", b"HolWlloe"]

    with tempfile.TemporaryFile() as fout, tempfile.TemporaryFile() as ferr, tempfile.TemporaryFile() as fboth:
        process = teetime.popen_call(
            ["python", os.path.join(CWD, "test.py")],
            stdout=(sys.stdout.buffer, fout, fboth),
            stderr=(sys.stderr.buffer, ferr, fboth),
        )
        process.wait()

        assert fout.read() == SEP.join(STD_OUT + [b""])
        assert ferr.read() == SEP.join(STD_ERR + [b""])
        both = fboth.read()
        assert both == build_output(both, STD_OUT, STD_ERR)


def _iter_queue(q):
    while not q.empty():
        yield q.get()


def test_queue():
    """Basic test."""
    q = queue.Queue()
    process = teetime.popen_call(
        ["python", os.path.join(CWD, "test.py")], stdout=(q,), stderr=(q,),
    )
    process.wait()

    assert list(_iter_queue(q)) == [
        b"doWlloHer\n",
        b"HlWd\n",
        b"lHl o!lreo\n",
        b"!\n",
        b"oWd H\n",
        b"lHlWd\n",
        b"delWlHlor\n",
        b" olrdl!He\n",
        b"HolWlloe\n",
        b"!l\n",
    ]
