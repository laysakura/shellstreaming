# -*- coding: utf-8 -*-
"""
    shellstreaming.api
    ~~~~~~~~~~~~~~~~~~

    :synopsis: Provides APIs users call for describing stream processings
"""
from shellstreaming.jobgraph import JobGraph


_job_graph = JobGraph()  # api.* functions modify this graph structure


def IStream(inputstream, inputstream_args):
    """Create an inputstream.

    :param inputstream:      reference to an inputsteram class
    :param inputsteram_args: tuple of args to :param:`inputsteram`.__init__()
    :returns: stream object (`node_id` internally)

    **Example**

    .. code-block:: python
        randint_stream = InputStream(RandInt, ())
        ...
    """
    global _job_graph
    node_id = inputstream.__name__   # [fix] - unique id
    _job_graph.add_node(node_id, attr_dict={
        'class' : inputstream,
        'args'  : inputstream_args,
    })
    return node_id


def OutputStream(outputstream, outputstream_args, prev_stream, dest):
    global _job_graph
    node_id = outputstream.__name__  # [fix] - unique id
    _job_graph.add_node(node_id, attr_dict={
        'class' : outputstream,
        'args'  : outputstream_args,
    })
    _job_graph.add_edge(prev_stream, node_id)
