# -*- coding: utf-8 -*-
"""
    shellstreaming.config
    ~~~~~~~~~~~~~~~~~~~~~

    :synopsis: Provides default configs
"""
from os.path import join, expanduser
from tempfile import gettempdir


DEFAULT_CONFIG_LOCATION = (expanduser(join('~', '.shellstreaming.cnf')), )
"""Path from which default config file is searched (from left)"""

DEFAULT_CONFIG = {
    # master
    'job_graph_path'                 : '',
    'job_graph_dpi'                  : '600',
    'master_scheduler_module'        : 'shellstreaming.scheduler.master_sched_allworker',
    'master_reschedule_interval_sec' : '10000',

    # worker
    'worker_default_port'            : '18871',
    'worker_log_path'                : join(gettempdir(), 'shellstreaming-worker-HOSTNAME-PORT.log'),
    # `master_scheduler_module` is more important for performance
    'worker_scheduler_module'        : 'shellstreaming.scheduler.worker_sched_single_thread',
    'worker_reschedule_interval_sec' : '0.1',
    'worker_set_cpu_affinity'        : 'False',
    'in_queue_selection_module'      : 'shellstreaming.scheduler.worker_select_queue_random',

    # auto_deploy
    'parallel_deploy'             : 'True',
    'ssh_private_key'             : 'None',
    'send_latest_config_on_start' : 'True',
    'send_latest_codes_on_start'  : 'True',

    # debug
    'log_level'       : 'DEBUG',
    'localhost_debug' : 'False',
    'check_datatype'  : 'True',

    # optimization parameter
    'min_records_in_aggregated_batches' : '1',
}
"""Default config values"""
