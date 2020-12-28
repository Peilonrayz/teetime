"""
Teetime - adding tee like functionality to Popen.

Conveniently allow Popen to pass data to any number of sinks.
Sinks can be shared between both stdout and std err and be handled correctly.

.. code-block::

    import sys
    import teetime

    with open('log.txt', 'wb') as f:
        teetime.popen_call(
            ['python', 'test.py'],
            stdout=(sys.stdout.buffered, f),
            stderr=(sys.stderr.buffered, f),
        )

The :code:`popen_call` function is a convenience over :code:`Sinks`.
If you need to interact with the process when it's live then you can
modify the following to suite your needs.

.. code-block::

    import sys
    import teetime

    with open('log.txt', 'wb') as f:
        sinks = Sinks(
            (sys.stdout.buffered, f),
            (sys.stderr.buffered, f),
        )
        process = sinks.popen(['python', 'test.py'])
        with self.make_threads(process) as threads:
            threads.join()
        self.reset_head()
"""

from __future__ import annotations

import collections
import io
import queue
import subprocess
import threading
from typing import Any, Callable, Iterator, List, Optional, Sequence, Tuple, Type

QUEUE_SENTINEL = object()
FILE_SENTINEL = b""

TSink = Callable[[bytes], None]
_Threads = collections.namedtuple("Threads", "out, err, both, queue")
_Sinks = collections.namedtuple("Sinks", "out, err, both")


class Threads(_Threads):
    """
    Thread manager and interface.

    Because we need to listen to stdout and stderr at the same time we
    need to put the listeners in threads. This is so we can handle
    changes when they happen. This comes with two benifits:

    1.  We don't have to store all the print information in memory.
    2.  We can display changes as soon as they happen.

    To allow stdout and stderr to merge correctly we have to use an
    atomic queue. :code:`queue.Queue` is one such example. If we have
    no need of combining output as there are no both sinks then the
    queue and associated thread won't be created.

    This object holds the three threads and the message queue.
    """

    out: threading.Thread
    err: threading.Thread
    both: threading.Thread
    queue: queue.Queue

    def __new__(
        cls, process: subprocess.Popen, sinks: Sinks, flush: bool = True,
    ) -> Threads:
        """
        Create Threads from an active process and sinks.

        This creates the required threads to handle the output and sinks.
        These threads are created as daemons and started on creation.
        This also creates the message queue that merges both stdout and
        stderr when needed.

        :param process: Process to tee output from.
        :param sinks: Places to tee output to.
        :param flush: Whether to force flush flushable sinks.
        :return: A thread manager for the process and sinks.
        """
        o_thread = None
        e_thread = None
        b_thread = None
        _queue: Optional[queue.Queue] = None
        out, err, both = sinks.as_callbacks(flush=flush)

        if both:
            _queue = queue.Queue()
            b_thread = cls._make_thread(
                target=cls._handle_sinks, args=(iter(_queue.get, QUEUE_SENTINEL), both)
            )
            if out is None:
                raise ValueError("both is defined, but out is None")
            if err is None:
                raise ValueError("both is defined, but err is None")
            out += (_queue.put,)
            err += (_queue.put,)

        if out:
            o_thread = cls._make_thread(
                target=cls._handle_sinks,
                args=(iter(process.stdout.readline, FILE_SENTINEL), out),
            )

        if err:
            e_thread = cls._make_thread(
                target=cls._handle_sinks,
                args=(iter(process.stderr.readline, FILE_SENTINEL), err),
            )

        return _Threads.__new__(cls, o_thread, e_thread, b_thread, _queue)

    def __enter__(self) -> Threads:
        """Context manager pattern."""
        return self

    def __exit__(self, _1: Any, _2: Any, _3: Any) -> None:
        """Context manager pattern."""
        self.end_queue()

    @staticmethod
    def _make_thread(*args: Any, **kwargs: Any) -> threading.Thread:
        """Make thread."""
        thread = threading.Thread(*args, **kwargs)
        thread.daemon = True
        thread.start()
        return thread

    @staticmethod
    def _handle_sinks(_input: Iterator[bytes], sinks: List[TSink]) -> None:
        """Threaded function to pass data between source and sink."""
        for segment in _input:
            for sink in sinks:
                sink(segment)

    def join(self, out: bool = True, err: bool = True, both: bool = False,) -> None:
        """Conveniently join threads."""
        if out and self.out is not None:
            self.out.join()
        if err and self.err is not None:
            self.err.join()
        if both and self.both is not None:
            self.both.join()

    def end_queue(self) -> None:
        """Send exit signal to the both thread."""
        if self.queue is not None:
            self.queue.put(QUEUE_SENTINEL)


def _flushed_write(sink: Any) -> TSink:
    """Flush on write."""

    def write(value: bytes) -> None:
        sink.write(value)
        sink.flush()

    return write


def _closable_write(write_func: Callable[[bytes], ...]) -> TSink:
    """Try to write, but fail silently if the file is already closed."""

    def write(value: bytes) -> None:
        try:
            write_func(value)
        except ValueError:
            # the file is already closed
            pass

    return write



class Sinks(_Sinks):
    """
    Ease creation and usage of sinks.

    This handles where the output should be copied to.
    It also contains a few convenience functions to ease usage.
    These convenience functions are purely optional and the raw form
    is still available to some extent.
    """

    out: Optional[Tuple[Any, ...]]
    err: Optional[Tuple[Any, ...]]
    both: Tuple[Any, ...]

    def __new__(cls, out: Sequence[Any], err: Sequence[Any]):
        """Create new sinks."""
        both: Tuple[Any, ...] = ()
        if out and err:
            _out = set(out)
            _err = set(err)
            _both = _out & _err
            _out -= _both
            _err -= _both
            out = tuple(_out)
            err = tuple(_err)
            both = tuple(_both)
        return _Sinks.__new__(cls, out, err, both)

    def run(
        self, *args, flush: bool = True, threads: Type[Threads] = Threads, **kwargs,
    ) -> subprocess.Popen:
        """Conveniently create and execute a process and threads."""
        process = self.popen(*args, **kwargs)
        self.run_threads(process, flush=flush, threads=threads)
        return process

    def popen(self, *args: Any, **kwargs: Any,) -> subprocess.Popen:
        """Conveniently create a process with out and err defined."""
        return subprocess.Popen(  # type: ignore
            *args, stdout=self.popen_out, stderr=self.popen_err, **kwargs,
        )

    @property
    def popen_out(self) -> Optional[int]:
        """Conveniently get the Popen output argument."""
        return subprocess.PIPE if self.out is not None else None

    @property
    def popen_err(self) -> Optional[int]:
        """Conveniently get the Popen error argument."""
        return subprocess.PIPE if self.err is not None else None

    def run_threads(
        self,
        process: subprocess.Popen,
        flush: bool = True,
        threads: Type[Threads] = Threads,
    ) -> None:
        """Conveniently create the threads and execute process."""
        with self.make_threads(process, flush=flush, threads=threads,) as _threads:
            _threads.join()
        self.flush()
        self.reset_head()

    def make_threads(
        self,
        process: subprocess.Popen,
        flush: bool = True,
        threads: Type[Threads] = Threads,
    ) -> Threads:
        """Conveniently create threads."""
        return threads(process, self, flush=flush)

    def flush(self) -> None:
        """Flush all sinks."""
        for sinks in self:
            if sinks is None:
                continue
            for sink in sinks:
                if hasattr(sink, "flush"):
                    sink.flush()

    def reset_head(self) -> None:
        """Reset the head of all sinks."""
        for sinks in self:
            for sink in sinks or []:
                if hasattr(sink, "seek"):
                    try:
                        sink.seek(0)
                    except io.UnsupportedOperation:
                        pass

    @staticmethod
    def _to_callback(
        sinks: Optional[List[Any]], flush: bool = True, closable: bool = True,
    ) -> Optional[Tuple[TSink, ...]]:
        """Convert sinks to a callback."""
        if sinks is None:
            return None
        callbacks: List[TSink] = []
        for sink in sinks:
            if isinstance(sink, queue.Queue):
                callbacks.append(sink.put)
            elif hasattr(sink, "write"):
                write = sink.write
                if flush and hasattr(sink, "flush"):
                    write = _flushed_write(sink)
                if closable and (hasattr(sink, "writable") or hasattr(sink, "closed")):
                    write = _closable_write(write)
                callbacks.append(write)
            else:
                raise ValueError(f"Unknown sink type {type(sink)} for {sink}")
        return tuple(callbacks)

    def as_callbacks(
        self, flush: bool = True, closable: bool = True,
    ) -> Tuple[Optional[Tuple[TSink, ...]], ...]:
        """Convert all sinks to their callbacks."""
        return tuple(self._to_callback(sinks, flush=flush, closable=closable) for sinks in self)


def popen_call(*args, stdout=None, stderr=None, **kwargs) -> subprocess.Popen:
    """Initialize process and wait for IO to complete."""
    return Sinks(stdout, stderr).run(*args, **kwargs)
