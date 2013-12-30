# -*- coding: utf-8 -*-
"""
    shellstreaming.api
    ~~~~~~~~~~~~~~~~~~

    :synopsis: Provides APIs users call for describing stream processings
"""


def InputStream(job_graph, inputstream, inputstream_args):
    """Create an inputstream.

    :param inputstream:      reference to an inputsteram class
    :param inputsteram_args: tuple of args to :param:`inputsteram`.__init__()
    :returns: stream object (`node_id` internally)

    **Example**

    .. code-block:: python
        randint_stream = InputStream(RandInt, ())
        ...
    """
    print('%s called' % (inputstream.__name__))
    node_id = inputstream.__name__   # [fix] - unique id
    job_graph.add_node(node_id, attr_dict={
        'class' : inputstream,
        'args'  : inputstream_args,
    })
    return node_id


def OutputStream(job_graph, outputstream, outputstream_args, prev_stream, dest):
    print prev_stream
    print('%s called' % (outputstream.__name__))
    node_id = outputstream.__name__  # [fix] - unique id
    job_graph.add_node(node_id, attr_dict={
        'class' : outputstream,
        'args'  : outputstream_args,
    })
    job_graph.add_edge(prev_stream, node_id)
