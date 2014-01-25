# -*- coding: utf-8 -*-
"""
    shellstreaming.util.parallel
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :synopsis: Provides parallel functions
"""
import multiprocessing


## Error occurs when using it ...
# def map(func, iterable, parallelism=None):
#     """Parallel map function.
#     Unlike multiprocessing.Pool.map, default parallelism is `len(iterable)`

#     *Example*

#     .. code-block:: python
#         >>> from shellstreaming.util import parallel
#         >>> parallel.map(lambda x: x**2, [1, 2, 3, 4, 5])
#         [1, 4, 9, 16, 25]
#     """
#     # unfortunately, multiprocessing.Pool.map cannot be used for implementation since it doesn't accept lambda ...
#     # => http://stackoverflow.com/questions/3288595/multiprocessing-using-pool-map-on-a-function-defined-in-a-class
#     def spawn(f):
#         def fun(q_in, q_out):
#             while True:
#                 i, x = q_in.get()
#                 if i is None:
#                     break
#                 q_out.put((i, f(x)))
#         return fun

#     if parallelism is None:
#         parallelism = len(iterable)

#     q_in  = multiprocessing.Queue(1)
#     q_out = multiprocessing.Queue()
#     proc  = [multiprocessing.Process(target=spawn(func), args=(q_in, q_out)) for _ in range(parallelism)]
#     for p in proc:
#         p.daemon = True
#         p.start()

#     sent = [q_in.put((i, x)) for i, x in enumerate(iterable)]
#     [q_in.put((None, None)) for _ in range(parallelism)]
#     res = [q_out.get() for _ in range(len(sent))]

#     [p.join() for p in proc]

#     return [x for i, x in sorted(res)]
