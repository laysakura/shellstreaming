# -*- coding: utf-8 -*-
"""
    shellstreaming.util.parse
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    :synopsis: Parse complex values
"""


def parse_hostname_port(hostname_port, default_port):
    """
    **Examples**

    .. code-block:: python
        >>> parse_hostname_port('machine00:10000', 18871)
        ('machine00', 10000)
        >>> # using default port
        >>> parse_hostname_port('machine00', 18871)
        ('machine00', 18871)
        >>> # invalid format
        >>> import nose.tools as ns
        >>> with ns.assert_raises(AssertionError):
        ...     parse_hostname_port('machine00:1234:??', 18871)
    """
    v = hostname_port.split(':')
    if len(v) == 1:
        return (v[0], default_port)
    elif len(v) == 2:
        return (v[0], int(v[1]))
    else:
        raise AssertionError('"%s" is invalid format (in `worker_hosts` config value)' % (v))
