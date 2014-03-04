# -*- coding: utf-8 -*-


from subprocess import check_call


def test_shellstreaming_help():
    check_call(["shellstreaming", "--help"])
