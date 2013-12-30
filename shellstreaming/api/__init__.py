# -*- coding: utf-8 -*-
"""
    shellstreaming.api
    ~~~~~~~~~~~~~~~~~~

    :synopsis: Provides APIs users call for describing stream processings
"""


def InputStream(job_graph, inputstream):
    print('%s called' % (inputstream.__name__))
    job_node = inputstream.__name__
    job_graph.add_node(job_node)
    return {
        'job_node': job_node,
    }
    # return networkxのノード, その他の情報


def OutputStream(job_graph, outputstream, outputstream_args, prev_stream, dest):
    print prev_stream
    print('%s called' % (outputstream.__name__))
    job_node = outputstream.__name__
    job_graph.add_node(job_node)
    job_graph.add_edge(prev_stream['job_node'], job_node)
