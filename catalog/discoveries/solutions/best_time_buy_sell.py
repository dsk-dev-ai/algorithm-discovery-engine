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
