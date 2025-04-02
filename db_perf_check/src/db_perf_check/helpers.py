from time import time

class Timer:
    def __init__(self):
        self.start = None
        self.end = None
    def __enter__(self):
        self.start = time()
        return self
    def __exit__(self, *args, **kwargs):
        self.end = time()
        self.elapsed = self.end - self.start
