def unoptimised_loop(data):
    import math
    res=0
    for item in data:
        res+=math.sqrt(item)
        # LOAD_GLOBAL (global vars)
    return res

def optimised_loop(data):
    from math import sqrt
    # LOAD_FAST (local vars)
    res=0
    for item in data:
        res+=sqrt(item)
    return res