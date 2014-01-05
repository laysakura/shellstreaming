# -*- coding: utf-8 -*-
"""
    shellstreaming.outputstream
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :synopsis: Export pre-defined OStreams
"""
from shellstreaming.outputstream import localfile, stdout


LocalFileOStream = localfile.LocalFile
StdoutOStream    = stdout.Stdout
