# Copyright 2021 Sebastian Ahmed
# This file, and derivatives thereof are licensed under the Apache License, Version 2.0 (the "License");
# Use of this file means you agree to the terms and conditions of the license and are in full compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software distributed under the License is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, EITHER EXPRESSED OR IMPLIED.
# See the License for the specific language governing permissions and limitations under the License.

import argparse

def proc_cla(iparser:argparse.ArgumentParser=None,descr:str='')->argparse.ArgumentParser:
    '''
    Process command line arguments and return a parser object. Optionally take in
    an existing argparse object and add parser options to it.
    '''
    if iparser:
        assert isinstance(iparser,argparse.ArgumentParser), "Object is not an argument parser"
        parser = iparser
    else:
        # Create a new object if one is not specified
        parser = argparse.ArgumentParser(description=descr)
    
    parser.add_argument('--depth',     metavar='<integer>', type=int,  help='Max number of entries in the FIFO (simulation only)', default=128)
    parser.add_argument('--plsize',    metavar='<integer>', type=int,  help='Payload size in number of datums',                    default=512)
    parser.add_argument('--writebw',   metavar='<integer>', type=int,  help='Write bandwidth in datums/unit time',                 default=1024)
    parser.add_argument('--readbw',    metavar='<integer>', type=int,  help='Read bandwidth in datums/unit time',                  default=1280)
    parser.add_argument('--initlevel', metavar='<integer>', type=int,  help='Initial FIFO level (simulation only)',                default=1)
    parser.add_argument('--quantum',   metavar='<integer>', type=int,  help='Number of sim steps per sim quantum (0=auto-mode)',   default=1)
    parser.add_argument('--nosim',     action='store_true',            help='Skip simulation, and only perform formulaic analysis')
    parser.add_argument('--verbose',   action='store_true',            help='Report all operations (simulation only)')

    return parser.parse_args()
