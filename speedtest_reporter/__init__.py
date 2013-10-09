#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    This module tries to perform some speedtest on the local connection, 
    to store the result and publish them on a web page.

    This tool use the ookla speedtest an is heavily based on speedtest_cli
    
"""
 
__version__ = "0.0.1"

from speedtest_reporter import report, speedtest
