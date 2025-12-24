import math
from collections import Counter
from typing import Iterable


def collatz_step(n: int) -> int:
    """
    Compute a single Collatz iteration.

    Collatz map:
      - n -> 3n + 1  if n is odd
      - n -> n / 2   if n is even

    Parameters
    ----------
    n : int
        Positive integer.

    Returns
    -------
    int
        Next iterate of the Collatz map.

    Raises
    ------
    ValueError
        If n is not a positive integer.
    """
    if n <= 0:
        raise ValueError("n must be > 0")

    return 3 * n + 1 if (n % 2) else (n // 2)


def collatz_orbit(n: int) -> list[int]:
    """
    Compute the Collatz orbit starting from n until reaching 1 (inclusive).

    Parameters
    ----------
    n : int
        Positive integer initial value.

    Returns
    -------
    list[int]
        Sequence of iterates [n0, n1, ..., 1].

    Raises
    ------
    ValueError
        If n is not a positive integer.
    """
    if n <= 0:
        raise ValueError("n must be > 0")

    seq = [n]
    while n != 1:
        n = collatz_step(n)
        seq.append(n)
    return seq


def inverse_children(m: int) -> list[int]:
    """
    Return the valid inverse predecessors of m under the Collatz map.

    This function builds the inverse graph rooted at 1 by providing, for each node m,
    all integers n such that collatz_step(n) == m.

    There are up to two predecessors:
      1) Even-predecessor: n = 2m (always valid)
      2) Odd-predecessor:  n = (m - 1) / 3, valid only if:
           - (m - 1) is divisible by 3, and
           - n is odd (to ensure it belongs to the odd branch of the forward map)

    A practical equivalent condition for the odd-predecessor is:
      - m % 6 == 4

    Parameters
    ----------
    m : int
        Positive integer node value.

    Returns
    -------
    list[int]
        List of predecessors in ascending order (when present):
        [(m - 1) / 3 if valid, 2m]

    Raises
    ------
    ValueError
        If m is not a positive integer.
    """
    if m <= 0:
        raise ValueError("m must be > 0")

    preds: list[int] = []

    # Odd-predecessor candidate: (m - 1) / 3 must be an odd integer
    if m % 6 == 4:
        n = (m - 1) // 3
        # Defensive check: verify the candidate is indeed a valid odd predecessor.
        if n > 0 and (n % 2 == 1) and collatz_step(n) == m:
            preds.append(n)

    # Even-predecessor always exists: 2m
    preds.append(2 * m)
    return preds


def leading_digit(n: int) -> int:
    n = abs(n)
    if n == 0:
        return 0
    while n >= 10:
        n //= 10
    return n

def leading_digit_frequencies(numbers: Iterable[int]) -> list[float]:
    """
    Compute the relative frequency of leading digits in the range 1..9.

    Parameters
    ----------
    numbers : Iterable[int]
        Collection of integers from which leading digits are extracted.

    Returns
    -------
    list[float]
        Relative frequencies for digits 1..9, in order.
        If the input does not contribute any digits in 1..9, returns nine zeros.
    """

    # Count how many times each leading digit appears in the input sequence
    freqs = Counter(
        leading_digit(n)   # map each number to its leading digit
        for n in numbers   # iterate over all input values
    )

    digits = list(range(1, 10))

    counts = [freqs.get(d, 0) for d in digits]

    total = sum(counts)
    if total == 0:
        return [0] * 9

    return [c / total for c in counts]


def expected_benford() -> tuple[list[int], list[float]]:
    """
    Return Benford's Law expected probabilities for leading digits 1..9.

    Benford's Law:
        P(d) = log10(1 + 1/d), for d in {1,2,...,9}

    Returns
    -------
    tuple[list[int], list[float]]
        Digits (1..9) and their expected probabilities.
    """
    digits = list(range(1, 10))
    probs = [math.log10(1 + 1 / d) for d in digits]
    return digits, probs
