import math
from collections import Counter, deque, defaultdict
from typing import Iterable, Deque, Dict, List, Optional, Tuple
from enum import Enum
from dataclasses import dataclass

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


class EdgeType(str, Enum):
    EVEN = "DOUBLE"  # child = 2 * parent
    ODD = "ODD"  # child = (parent - 1) / 3 

@dataclass(frozen=True)
class Node:
    id: int
    value: int
    parent_id: Optional[int]
    depth: int
    parent_edge_type: Optional[EdgeType]  # None for root

def generate_inverse_collatz_tree(
    target: int,
    *,
    max_nodes: Optional[int] = 200_000,
) -> List[Node]:
    """
    Generate the inverse Collatz tree rooted at 1 using BFS until `target` appears.

    This variant:
      - does NOT use visited/deduplication
      - manually seeds the deterministic initial chain 1 -> 2 -> 4 -> 8 -> 16
      - starts the BFS expansion from node 16

    Notes:
      - Children here are "inverse predecessors" of a node m:
          - always: 2*m
          - sometimes: (m-1)/3 if m % 6 == 4
    """
    if target <= 0:
        raise ValueError("target must be a positive integer")

    nodes: List[Node] = []
    q: Deque[int] = deque()

    def add_node(
        value: int,
        parent_id: Optional[int],
        depth: int,
        edge_type: Optional[EdgeType],
        enqueue: bool = True,
    ) -> int:
        node_id = len(nodes)
        nodes.append(Node(node_id, value, parent_id, depth, edge_type))
        if enqueue:
            q.append(node_id)
        return node_id

    # ---- Seed fixed initial chain: 1 -> 2 -> 4 -> 8 -> 16 ----
    # root
    id_1 = add_node(1, None, 0, None, enqueue=False)
    if target == 1:
        return nodes

    id_2 = add_node(2, id_1, 1, EdgeType.EVEN, enqueue=False)
    if target == 2:
        return nodes

    id_4 = add_node(4, id_2, 2, EdgeType.EVEN, enqueue=False)
    if target == 4:
        return nodes

    id_8 = add_node(8, id_4, 3, EdgeType.EVEN, enqueue=False)
    if target == 8:
        return nodes

    id_16 = add_node(16, id_8, 4, EdgeType.EVEN, enqueue=True)  # start BFS from here
    if target == 16:
        return nodes

    # ---- BFS expansion starting from 16 ----
    while q:
        if max_nodes is not None and len(nodes) >= max_nodes:
            break

        u_id = q.popleft()
        u = nodes[u_id]
        next_depth = u.depth + 1

        # Child 1: 2*u (always)
        c1_val = 2 * u.value
        c1_id = add_node(c1_val, u_id, next_depth, EdgeType.EVEN, enqueue=True)
        if c1_val == target:
            break

        # Child 2: (u-1)/3 only if u % 6 == 4 (ensures integer and odd)
        if u.value % 6 == 4:
            c2_val = (u.value - 1) // 3
            add_node(c2_val, u_id, next_depth, EdgeType.ODD, enqueue=True)
            if c2_val == target:
                break

    return nodes


def map_top_down_tree(
    nodes: List[Node],
    *,
    x_spacing: float = 1.0,
    y_spacing: float = 1.0,
) -> Dict[int, Tuple[float, float]]:
    """
    Return coordinates for a classic top-down tree layout.

    - y = depth * y_spacing
    - x is assigned by a post-order traversal:
        * leaves get consecutive x slots
        * internal nodes are centered above their children (average of children's x)

    Works even if nodes contain duplicates in value (we layout by node_id).
    """

    if not nodes:
        return {}

    # 1) children lists
    children: Dict[int, List[int]] = defaultdict(list)
    root_id: Optional[int] = None

    for n in nodes:
        if n.parent_id is None:
            root_id = n.id
        else:
            children[n.parent_id].append(n.id)

    if root_id is None:
        # Fallback: assume 0 is root if missing parent_id None
        root_id = 0

    # 2) stable ordering for nicer drawings:
    #    - put DOUBLE child first (usually the "main chain"),
    #    - then ODD_PREIMAGE
    #    - then by value to keep it deterministic
    def child_sort_key(child_id: int):
        c = nodes[child_id]
        # parent_edge_type is the type of edge from parent -> child
        # We want DOUBLE first
        edge_rank = 0
        if c.parent_edge_type is not None:
            edge_rank = 0 if c.parent_edge_type.name.startswith("EVEN") else 1
        return (edge_rank, c.value, c.id)

    for pid, lst in children.items():
        lst.sort(key=child_sort_key)

    # 3) post-order assignment of x
    x_coord: Dict[int, float] = {}
    y_coord: Dict[int, float] = {}
    visited: set[int] = set()
    next_x = 0.0

    def dfs(u_id: int) -> None:
        nonlocal next_x

        if u_id in visited:
            return
        visited.add(u_id)

        # visit children first
        for v_id in children.get(u_id, []):
            dfs(v_id)

        # assign y always from depth
        y_coord[u_id] = nodes[u_id].depth * y_spacing

        # assign x
        kids = children.get(u_id, [])
        if not kids:
            # leaf
            x_coord[u_id] = next_x
            next_x += x_spacing
        else:
            # center above children
            xs = [x_coord[k] for k in kids]
            x_coord[u_id] = sum(xs) / len(xs)

    dfs(root_id)

    # In case the structure is forest-like (shouldn't, but with truncations / bugs it can),
    # lay out any unreachable nodes after the main component.
    for n in nodes:
        if n.id not in visited:
            dfs(n.id)

    return {nid: (x_coord[nid], y_coord[nid]) for nid in x_coord.keys()}