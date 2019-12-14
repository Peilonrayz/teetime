# Teetime

[![Master Build Status](https://travis-ci.org/Peilonrayz/teetime.svg?branch=master)](https://travis-ci.org/Peilonrayz/teetime)

Adding tee like functionally to `subprocess.Popen`.

## Installation

```bash
$ pip install teetime
```

## How to use

There is some documentation in the code, and can be generated with `tox -e docs`. Common usage is:

```python
import sys
import teetime

with open('log.txt', 'wb') as f:
    process = teetime.popen_call(
        ['python', 'test.py'],
        stdout=(sys.stdout.buffered, f),
        stderr=(sys.stderr.buffered, f),
    )
    process.wait()
```

**Note**: `popen_call` blocks until IO is complete. If you have no IO, `stdout=()`, then it will not block. This is why you still need `process.wait()`.

# Development

All tests use are run via tox. This includes running static analysis tools, unit tests and generating documentation.

```bash
$ tox
```
