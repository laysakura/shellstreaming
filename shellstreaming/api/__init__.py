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


def IStream(istream, *istream_args, **istream_kw):
    """Create an istream.

    :param istream:      reference to an istream class
    :param *istream_args: args to :param:`istream`.__init__()
    :param **istream_kw: keyword args to :param:`istream`.__init__()
    :returns: stream object (`node_id` internally)

    **Example**

    .. code-block:: python
        randint_stream = Istream(RandInt, (0, 100))
        ...
    """
    stream = _reg_job('istream', None, istream, istream_args, istream_kw)
    return stream


def Operator(in_stream, operator, *operator_args, **operator_kw):
    streams = _reg_job('operator', in_stream, operator, operator_args, operator_kw)
    assert(len(streams) >= 1)
    if len(streams) == 1:
        streams = streams[0]
    return streams


def OStream(in_stream, ostream, *ostream_args, **ostream_kw):
    _reg_job('ostream', in_stream, ostream, ostream_args, ostream_kw)


def _reg_job(job_type, in_stream, job_class, job_class_args, job_class_kw):
    """Update :data:`_job_graph`
    """
    global _job_graph, _num_job_node, _num_stream_edge

    # add node
    job_id = "%d: %s" % (_num_job_node, job_class.__name__)
    _num_job_node += 1
    fixed_to = None
    if 'fixed_to' in job_class_kw:
        fixed_to = job_class_kw['fixed_to']
        del job_class_kw['fixed_to']
    _job_graph.add_node(job_id, job_type, job_class, job_class_args, job_class_kw, fixed_to)

    if job_type in ('operator', 'ostream'):
        # edge from pred job to this job
        assert(in_stream is not None)
        to_from = (in_stream.src_job_id, job_id)
        _job_graph.add_edge(*to_from, stream_edge_id=in_stream.id)
        _job_graph.edge_labels[to_from] = in_stream.id

    if job_type == 'ostream':
        return

    # prepare edge from this job
    if job_type == 'istream':
        stream_id = "%d: %s" % (_num_stream_edge, '')
        _num_stream_edge += 1
        return StreamEdge(stream_id, src_job_id=job_id)
    else:
        # some operator has multiple output streams
        assert(job_type == 'operator')
        streams = []
        for s in job_class.out_stream_edge_id_suffixes(job_class_args):
            stream_id = "%d: %s" % (_num_stream_edge, s)
            _num_stream_edge += 1
            streams.append(StreamEdge(stream_id, src_job_id=job_id))
        return tuple(streams)
