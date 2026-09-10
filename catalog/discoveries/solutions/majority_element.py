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
