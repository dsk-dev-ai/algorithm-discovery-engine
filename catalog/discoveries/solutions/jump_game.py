def discovered_jump_game(arg):
    s0 = 0
    s1 = 0
    for i, x in enumerate(arg):
        n = len(arg)
        s1 = max(s1, i - s0)
        s0 = max(s0, i + x)
    return s1 == 0
