# -*- coding: utf-8 -*-
"""
    shellstreaming.util.resource
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :synopsis: Reports HW resource info
"""
# standard modules
import time

# 3rd party moduels
import psutil


_cpu_percent_called = False


def avail_cores():
    """Return number of available cores on the node"""
    # Since :func:`psutil.cpu_percent()` is implemented to compare cpu time of current & previous call,
    # 1st result of this function is not necessarily relavant to shellstreaming itself.
    global _cpu_percent_called
    if not _cpu_percent_called:
        psutil.cpu_percent(interval=0, percpu=True)
        _cpu_percent_called = True
        time.sleep(0.1)

    ret = 0
    for core_usage in psutil.cpu_percent(interval=0, percpu=True):
        if core_usage < 20.0:  # [todo] - change parameter to calc available cores?
            ret += 1
    return ret


def avail_memory_byte():
    # [todo] - after implementing memory controller (which evicts data into disk sometimes),
    # [todo] - file cache would be important. Then `free` is better to use than `available`
    return psutil.virtual_memory().available
