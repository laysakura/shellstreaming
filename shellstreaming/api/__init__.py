# -*- coding: utf-8 -*-
"""
    shellstreaming.api
    ~~~~~~~~~~~~~~~~~~

    :synopsis: Provides APIs users call for describing stream processings
"""
from shellstreaming.jobgraph import JobGraph


_job_graph    = JobGraph()  # api.* functions modify this graph structure
_num_job_node = 0           # used for unique job node id


def IStream(inputstream, inputstream_args):
    """Create an inputstream.

    :param inputstream:      reference to an inputsteram class
    :param inputsteram_args: tuple of args to :param:`inputsteram`.__init__()
    :returns: stream object (`node_id` internally)

    **Example**

    .. code-block:: python
        randint_stream = InputStream(RandInt, (0, 100))
        ...
    """
    return _reg_job(inputstream, inputstream_args, None)


def OStream(outputstream, outputstream_args, pred_stream, dest):    # [fix] - `dest` のワーカにostream instanceを立てるようにする
    return _reg_job(outputstream, outputstream_args, pred_stream)


def _reg_job(job_class, job_class_args, pred_job_id):
    """Update :data:`_job_graph`

    :returns: job_id of registered one
    """
    global _job_graph, _num_job_node
    job_id = "%s_%d" % (job_class.__name__, _num_job_node)
    _num_job_node += 1

    _job_graph.add_node(job_id, attr_dict={
        'class' : job_class,
        'args'  : job_class_args,
    })
    if pred_job_id:
        _job_graph.add_edge(pred_job_id, job_id)

    return job_id
