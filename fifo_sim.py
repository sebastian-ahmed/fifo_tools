#!/usr/bin/env python3

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
import sys

from fifo_pkg.WinWrap       import WinWrap
from fifo_pkg.Fifo          import Fifo
from fifo_pkg.FifoSimulator import FifoSimulator

def main():

    parser = argparse.ArgumentParser(description='Wrapper script to simulate a FIFO model')
    parser.add_argument('--depth',     metavar='<integer>', type=int,  help='Number of entries in the FIFO',       default=128)
    parser.add_argument('--plsize',    metavar='<integer>', type=int,  help='Payload size in number of datums',    default=512)
    parser.add_argument('--writebw',   metavar='<integer>', type=int,  help='Write bandwidth in datums/unit time', default=1024)
    parser.add_argument('--readbw',    metavar='<integer>', type=int,  help='Read bandwidth in datums/unit time',  default=1280)
    parser.add_argument('--initlevel', metavar='<integer>', type=int,  help='Initial FIFO level',                  default=1)
    parser.add_argument('--verbose',   action='store_true',            help='Report all operations',               default=False)

    args = parser.parse_args()

    print("FIFO sim condition summary")
    print(f"Max payload size   = {args.plsize}")
    print(f"Write Bandwidth    = {args.writebw}")
    print(f"Read Badwidth      = {args.readbw}")
    print(f"FIFO depth         = {args.depth}")
    print(f"Initial FIFO level = {args.initlevel}\n")

    fifo = Fifo(args.depth,verbose=args.verbose)

    simulator = FifoSimulator(fifoHandle=fifo,pl_size=args.plsize,writeBandwidth=args.writebw,readBandwidth=args.readbw,initLevel=args.initlevel)

    simulator.simulate()

if __name__ == '__main__':
    with WinWrap(main) as handle:
        handle()