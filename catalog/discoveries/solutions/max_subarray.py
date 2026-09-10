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
