# -*- coding: utf-8 -*-
"""
    shellstreaming.config
    ~~~~~~~~~~~~~~~~~~~~~

    :synopsis: Provides default configs
"""
from ConfigParser import SafeConfigParser


def get_default_conf():
    """Return :class:`SafeConfigParser` object with default values
    """
    return SafeConfigParser({
        'parallel_deploy'            : 'False',
        'ssh_private_key'            : 'None',
        'send_latest_codes_on_start' : 'True',
        'job_graph_path'             : '',
        'single_process_debug'       : 'False',
        'master_scheduler_module'    : 'shellstreaming.scheduler.master_sched_localhost',
        'reschedule_interval_sec'    : '10',
    })
