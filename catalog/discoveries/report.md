# Discovery report

Fuzz cases per target: 10  ·  solved catalog problems: 10

| target | status | strategy | size | novelty |
| --- | --- | --- | ---: | --- |
| max_subarray | verified |  | 4 | rediscovered |
| max_circular_subarray | verified | Kadane + minimum-window wrap (two passes) | 24 | new-to-catalog |
| best_time_buy_sell | verified |  | 4 | new-to-catalog |
| jump_game | verified |  | 6 | new-to-catalog |
| contains_duplicate | verified | hash-set membership trace | 8 | new-to-catalog |
| majority_element | verified | Boyer-Moore majority voting | 15 | new-to-catalog |
| climbing_stairs | verified | two-token linear recurrence (Fibonacci) | 9 | new-to-catalog |

## max_subarray  (`scan`)

`max_subarray(nums: list[int]) -> int`

- Complexity: O(n), O(1) extra space
- Novelty: rediscovered — target already solved in the shared (4-language) catalog; this candidate matches the same contract all tier runners assert
- Verified on all curated examples and 10 fuzz inputs.

```python
def discovered_max_subarray(arg):
    if not arg:
        return 0
    s0 = arg[0]
    s1 = 0
    for i, x in enumerate(arg):
        n = len(arg)
        s1 = max(x, s1 + x)
        s0 = max(s0, s1)
    return s0
```

## max_circular_subarray  (`template:circular-kadane`)

`max_circular_subarray(nums: list[int]) -> int`

- Complexity: O(n), O(1) extra space
- Novelty: new-to-catalog — not part of the shared catalog yet - a candidate worth porting to the language tiers
- Verified on all curated examples and 10 fuzz inputs.

```python
def discovered_max_circular_subarray(arg):
    if not arg:
        return 0
    best_end = arg[0]
    best = arg[0]
    for x in arg[1:]:
        best_end = max(x, best_end + x)
        best = max(best, best_end)
    total = sum(arg)
    min_end = 0
    min_wrap = 0
    for x in arg:
        min_end = min(0, min_end + x)
        min_wrap = min(min_wrap, min_end)
    return max(best, total - min_wrap, 0)
```

## best_time_buy_sell  (`scan`)

`best_time_buy_sell(prices: list[int]) -> int`

- Complexity: O(n), O(1) extra space
- Novelty: new-to-catalog — not part of the shared catalog yet - a candidate worth porting to the language tiers
- Verified on all curated examples and 10 fuzz inputs.

```python
def discovered_best_time_buy_sell(arg):
    if not arg:
        return 0
    s0 = arg[0]
    s1 = 0
    for i, x in enumerate(arg):
        n = len(arg)
        s0 = min(s0, x)
        s1 = max(s1, x - s0)
    return s1
```

## jump_game  (`scan`)

`jump_game(nums: list[int]) -> bool`

- Complexity: O(n), O(1) extra space
- Novelty: new-to-catalog — not part of the shared catalog yet - a candidate worth porting to the language tiers
- Verified on all curated examples and 10 fuzz inputs.

```python
def discovered_jump_game(arg):
    s0 = 0
    s1 = 0
    for i, x in enumerate(arg):
        n = len(arg)
        s1 = max(s1, i - s0)
        s0 = max(s0, i + x)
    return s1 == 0
```

## contains_duplicate  (`seen`)

`contains_duplicate(nums: list[int]) -> bool`

- Complexity: O(n), O(n) extra space
- Novelty: new-to-catalog — not part of the shared catalog yet - a candidate worth porting to the language tiers
- Verified on all curated examples and 10 fuzz inputs.

```python
def discovered_contains_duplicate(arg):
    seen = set()
    for x in arg:
        if x in seen:
            return True
        seen.add(x)
    return False
```

## majority_element  (`vote`)

`majority_element(nums: list[int]) -> int`

- Complexity: O(n), O(1) extra space
- Novelty: new-to-catalog — not part of the shared catalog yet - a candidate worth porting to the language tiers
- Verified on all curated examples and 10 fuzz inputs.

```python
def discovered_majority_element(arg):
    candidate = arg[0]
    count = 1
    for x in arg[1:]:
        if x == candidate:
            count += 1
        elif count == 0:
            candidate = x
            count = 1
        else:
            count -= 1
    return candidate
```

## climbing_stairs  (`fib`)

`climbing_stairs(n: int) -> int`

- Complexity: O(n), O(1) extra space
- Novelty: new-to-catalog — not part of the shared catalog yet - a candidate worth porting to the language tiers
- Verified on all curated examples and 10 fuzz inputs.

```python
def discovered_climbing_stairs(arg):
    a, b = 1, 1
    for _ in range(arg):
        a, b = b, a + b
    return a
```

