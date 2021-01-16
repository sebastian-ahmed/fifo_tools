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

import sys

from fifo_pkg.WinWrap       import WinWrap
from fifo_pkg.Fifo          import Fifo
from fifo_pkg.FifoSimulator import FifoSimulator
from fifo_pkg.CLargs        import proc_cla

def main():

    args = proc_cla(iparser=None,descr='FIFO simulator and size calculator')

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