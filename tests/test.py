"""Test file."""

import random
import sys
import time


def main():
    """Test main."""
    random.seed(42401)
    for _ in range(10):
        f = random.choice([sys.stdout, sys.stderr])
        word = random.sample("Hello World!", random.randrange(1, 12))
        f.write("".join(word) + "\n")
        f.flush()
        time.sleep(random.randrange(3))


if __name__ == "__main__":
    main()
