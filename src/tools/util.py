import time, random


def backoff(retry, base=0.5):
# jittered exponential backoff
    return base * (2 ** retry) + random.uniform(0, base)