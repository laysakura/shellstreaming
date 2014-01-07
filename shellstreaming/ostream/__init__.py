# -*- coding: utf-8 -*-
"""
    shellstreaming.ostream
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :synopsis: Export pre-defined OStreams
"""
from shellstreaming.ostream import localfile, stdout


LocalFileOStream = localfile.LocalFile
StdoutOStream    = stdout.Stdout
