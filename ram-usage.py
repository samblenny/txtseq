# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: Copyright 2024 Sam Blenny
"""
Calculate a table of RAM bytes per element of various list elements.
"""
import gc
from collections import namedtuple

def free():
    gc.collect()
    return gc.mem_free()

class Normal:
    def __init__(self, a, b, c):
        self.a = a
        self.b = b
        self.c = c

class WithSlots:
    __slots__ = ['a', 'b', 'c']
    def __init__(self, a, b, c):
        self.a = a
        self.b = b
        self.c = c

Named = namedtuple('Named', '1 2 3')

def A(n):
    a = free()
    list_ = [(i, i, i) for i in range(n)]
    return (a - free()) / n

def B(n):
    a = free()
    list_ = [[i, i, i] for i in range(n)]
    return (a - free()) / n

def C(n):
    a = free()
    list_ = [Named(i, i, i) for i in range(n)]
    return (a - free()) / n

def D(n):
    a = free()
    list_ = [Normal(i, i, i) for i in range(n)]
    return (a - free()) / n

def E(n):
    a = free()
    list_ = [WithSlots(i, i, i) for i in range(n)]
    return (a - free()) / n

print('n,tuple,list,namedtuple,class,slots')
for n in [i * 25 for i in range(1,40)]:
    gc.collect()
    a = A(n); gc.collect()
    b = B(n); gc.collect()
    c = C(n); gc.collect()
    d = D(n); gc.collect()
    e = E(n); gc.collect()
    print(f"{n},{a:.1f},{b:.1f},{c:.1f},{d:.1f},{e:.1f}")

while True:
    pass

"""
Average bytes per element:

  tuple  list  namedtuple  class  slotsclass
  43.2   43.2  43.2        60.8   60.8

Tuple, list, and namedtuple use the same amount of RAM across each size.
Class and class with __slots__ use the same amount of RAM across each size.
"""
