# -*- coding: utf-8 -*-
"""
    shellstreaming.config.parse
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :synopsis: Parse complex config values
"""
from shellstreaming.util.parse import parse_hostname_port


def parse_worker_hosts(worker_hosts, default_port):
    """
    :param worker_hosts: hostname[:port],hostname[:port],....
    :type worker_hosts: str
    :param default_port: default port number
    :raises: `ValueError` when duplicated host-port pair is used.
        `AssersionError` when :param worker_hosts: format is illegal.

    **Examples**

    .. code-block:: python
        >>> parse_worker_hosts('machine00:10000,machine01:10000', 18871)
        [('machine00', 10000), ('machine01', 10000)]
        >>> # using default port
        >>> parse_worker_hosts('machine00:10000,machine01', 18871)
        [('machine00', 10000), ('machine01', 18871)]
        >>> # duplicated host-port pair
        >>> import nose.tools as ns
        >>> with ns.assert_raises(ValueError):
        ...     parse_worker_hosts('machine00:18871,machine00', 18871)
    """
    ret = []
    workers = worker_hosts.split(',')
    for worker in workers:
        host_port = parse_hostname_port(worker, default_port)
        if host_port in ret:
            raise ValueError('"%s" is duplicated in `worker_hosts` config value' % (worker))
        ret.append(host_port)
    return ret


def parse_worker_path(path, hostname, port):
    """Replace HOSTNAME & PORT to :param:`hostname` & :param:`port` respectively.
    """
    return path.replace('HOSTNAME', hostname).replace('PORT', str(port))
