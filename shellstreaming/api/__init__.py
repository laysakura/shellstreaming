# -*- coding: utf-8 -*-
"""
    shellstreaming.api
    ~~~~~~~~~~~~~~~~~~

    :synopsis: Provides APIs users call for describing stream processings
"""
from shellstreaming.jobgraph import JobGraph, StreamEdge


_job_graph       = JobGraph()  # api.* functions modify this graph structure
_num_job_node    = 0           # used for unique job node id
_num_stream_edge = 0           # used for unique stream edge id


def IStream(istream, istream_args):
    """Create an istream.

    :param istream:      reference to an inputsteram class
    :param inputsteram_args: tuple of args to :param:`inputsteram`.__init__()
    :returns: stream object (`node_id` internally)

    **Example**

    .. code-block:: python
        randint_stream = Istream(RandInt, (0, 100))
        ...
    """
    stream = _reg_job(istream, istream_args, 'istream', None)
    return stream


def OStream(ostream, ostream_args, in_stream, dest):    # [fix] - `dest` のワーカにostream instanceを立てるようにする
    _reg_job(ostream, ostream_args, 'ostream', in_stream)


def _reg_job(job_class, job_class_args, job_type, in_stream):
    """Update :data:`_job_graph`
    """
    global _job_graph, _num_job_node, _num_stream_edge

    # add node
    job_id = "%d: %s" % (_num_job_node, job_class.__name__)
    _num_job_node += 1
    _job_graph.add_node(job_id, attr_dict={
        'class' : job_class,
        'args'  : job_class_args,
    })

    if job_type in ('operator', 'ostream'):
        # edge from pred job to this job
        assert(in_stream is not None)
        to_from = (in_stream.src_job_id, job_id)
        _job_graph.add_edge(*to_from)
        _job_graph.edge_labels[to_from] = in_stream.id

    if job_type == 'ostream':
        return

    # prepare edge from this job
    # opの時は，edge_id の元になる文字列(エッジが複数なので複数)を，op_classに聞く
    stream_id = "%d: %s" % (_num_stream_edge, '')
    _num_stream_edge += 1
    stream = StreamEdge(stream_id, src_job_id=job_id)

    return stream
