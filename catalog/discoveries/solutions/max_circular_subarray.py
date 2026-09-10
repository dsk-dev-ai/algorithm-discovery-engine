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
