def discovered_contains_duplicate(arg):
    seen = set()
    for x in arg:
        if x in seen:
            return True
        seen.add(x)
    return False
