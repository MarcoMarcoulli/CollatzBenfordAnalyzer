import math
from collections import Counter

def collatz_orbit(n: int) -> list[int]:
    """Compute the Collatz orbit of n."""
    if n <= 0:
        raise ValueError("n must be > 0")

    seq = [n]
    while n != 1:
        n = 3*n + 1 if n % 2 else n // 2
        seq.append(n)
    return seq

def leading_digit(n: int) -> int:
    """Return the first (leading) digit of n."""
    return int(str(abs(n))[0])


def leading_digit_frequencies(numbers: list[int]) -> list[float]:
    """Return relative frequency of leading digits 1..9."""
    freqs = Counter(leading_digit(n) for n in numbers)
    digits = list(range(1, 10))
    counts = [freqs.get(d, 0) for d in digits]

    total = sum(counts)
    if total == 0:
        return [0]*9

    return [c / total for c in counts]

def expected_benford():
    """Return expected Benford frequencies for digits 1..9."""
    digits = list(range(1, 10))
    probs = [math.log10(1 + 1/d) for d in digits]
    return digits, probs