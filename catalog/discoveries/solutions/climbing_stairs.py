def discovered_climbing_stairs(arg):
    a, b = 1, 1
    for _ in range(arg):
        a, b = b, a + b
    return a
