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

    parser = argparse.ArgumentParser(description='A basic FIFO simulator and size calculator')
    parser.add_argument('--depth',     metavar='<integer>', type=int,  help='Max number of entries in the FIFO (simulation only)', default=128)
    parser.add_argument('--plsize',    metavar='<integer>', type=int,  help='Payload size in number of datums',                    default=512)
    parser.add_argument('--writebw',   metavar='<integer>', type=int,  help='Write bandwidth in datums/unit time',                 default=1024)
    parser.add_argument('--readbw',    metavar='<integer>', type=int,  help='Read bandwidth in datums/unit time',                  default=1280)
    parser.add_argument('--initlevel', metavar='<integer>', type=int,  help='Initial FIFO level (simulation only)',                default=1)
    parser.add_argument('--quantum',   metavar='<integer>', type=int,  help='Number of sim steps per sim quantum',                    default=1)
    parser.add_argument('--nosim',     action='store_true',            help='Skip simulation, and only perform formulaic analysis')
    parser.add_argument('--verbose',   action='store_true',            help='Report all operations (simulation only)')

    args = parser.parse_args()

    print("Simulation config summary:")
    print("--------------------------")
    print(f"Payload size           = {args.plsize}")
    print(f"Requested Write BW     = {args.writebw}")
    print(f"Requested Read BW      = {args.readbw}")
    print(f"Requested W:R BW ratio = {float(args.writebw/args.readbw):.2f}")
    print(f"Max FIFO depth         = {args.depth}")
    print(f"Initial FIFO level     = {args.initlevel}")
    print(f"Sim quantum            = {args.quantum}\n")

    fifo = Fifo(depth=args.depth,verbose=args.verbose)

    simulator = FifoSimulator(
        fifoHandle=fifo,
        pl_size=args.plsize,
        writeBandwidth=args.writebw,
        readBandwidth=args.readbw,
        initLevel=args.initlevel,
        nosim=args.nosim,
        simQuantum=args.quantum)

    simulator.simulate()

if __name__ == '__main__':
    with WinWrap(main) as wmain:
        wmain()