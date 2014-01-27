# -*- coding: utf-8 -*-
"""
    shellstreaming.api
    ~~~~~~~~~~~~~~~~~~

    :synopsis: Provides APIs users call for describing stream processings
"""
# standard modules
import logging

# my modules
from relshell.recorddef import RecordDef
from relshell.timestamp import Timestamp
from shellstreaming.util.parse import parse_hostname_port
import shellstreaming.master.master_struct as ms
from shellstreaming.jobgraph import JobGraph, StreamEdge


DEFAULT_PORT     = None        # master sets this
_job_graph       = JobGraph()  # api.* functions modify this graph structure
_num_job_node    = 0           # used for unique job node id
_num_stream_edge = 0           # used for unique stream edge id
_num_istream     = 0           # used to decide which worker to launch non-fixed istream


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
    logger = logging.getLogger('TerminalLogger')

    if 'fixed_to' not in istream_kw:
        logger.info('When "fixed_to" parameter is not given to api.IStream(), istream is instanciated only on 1 node (not parallelised)')
        # fix istream to a worker (round-robine)
        global _num_istream
        worker = ms.WORKER_IDS[_num_istream % len(ms.WORKER_IDS)]
        istream_kw['fixed_to'] = ['%s:%d' % (worker[0], worker[1])]
        _num_istream += 1

    stream = _reg_job('istream', [], istream, istream_args, istream_kw)
    return stream


def Operator(in_streams, operator, *operator_args, **operator_kw):
    """Create an operator.

    :param istreams: list of streams
    """
    streams = _reg_job('operator', in_streams, operator, operator_args, operator_kw)
    assert(len(streams) >= 1)
    if len(streams) == 1:
        streams = streams[0]
    return streams


def OStream(in_stream, ostream, *ostream_args, **ostream_kw):
    _reg_job('ostream', [in_stream], ostream, ostream_args, ostream_kw)


def _reg_job(job_type, in_streams, job_class, job_class_args, job_class_kw):
    """Update :data:`_job_graph`
    """
    logger = logging.getLogger('TerminalLogger')
    global _job_graph, _num_job_node, _num_stream_edge

    # add node
    job_id = "%d: %s" % (_num_job_node, job_class.__name__)
    _num_job_node += 1
    fixed_to = None

    if 'fixed_to' in job_class_kw:
        fixed_to = [parse_hostname_port(w, DEFAULT_PORT) for w in job_class_kw['fixed_to']]
        del job_class_kw['fixed_to']

    # partition_by 指定のついたキューの下のジョブは固定数でなければ，
    # partition キューを何個作れば良いかわからなくなる．
    # fixed_to 指定がなければ全並列を選ぶ．
    for in_stream in in_streams:
        if in_stream and in_stream.partition_key and not fixed_to:
            fixed_to = ms.WORKER_IDS
            logger.info('"%s" is executed on every node in parallel since upstream edge has `partition_by` spec' % (job_id))
            break

    _job_graph.add_node(job_id, job_type, job_class, job_class_args, job_class_kw, fixed_to)

    if job_type == 'ostream':
        # edge from pred job to this job
        assert(len(in_streams) == 1)
        in_stream = in_streams[0]
        to_from = (in_stream.src_job_id, job_id)
        _job_graph.add_edge(*to_from, stream_edge_id=in_stream.id, partition_key=in_stream.partition_key)
        _job_graph.edge_labels[to_from] = in_stream.id
        return
    elif job_type == 'istream':
        # prepare edge from this job
        stream_id = "%d: %s" % (_num_stream_edge, '')
        _num_stream_edge += 1
        return StreamEdge(stream_id, src_job_id=job_id)
    else:
        assert(job_type == 'operator')
        # input: some operators have multiple input streams
        for in_stream in in_streams:
            to_from = (in_stream.src_job_id, job_id)
            _job_graph.add_edge(*to_from, stream_edge_id=in_stream.id, partition_key=in_stream.partition_key)
            _job_graph.edge_labels[to_from] = in_stream.id
        # output: some operators have multiple output streams
        streams = []
        for s in job_class.out_stream_edge_id_suffixes(job_class_args):
            stream_id = "%d: %s" % (_num_stream_edge, s)
            _num_stream_edge += 1
            streams.append(StreamEdge(stream_id, src_job_id=job_id))
        return tuple(streams)
