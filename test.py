# Copyright 2021 Sebastian Ahmed
# This file, and derivatives thereof are licensed under the Apache License, Version 2.0 (the "License");
# Use of this file means you agree to the terms and conditions of the license and are in full compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software distributed under the License is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, EITHER EXPRESSED OR IMPLIED.
# See the License for the specific language governing permissions and limitations under the License.

import math
from fifo_pkg.Fifo import Fifo
from fifo_pkg.FifoSimulator import FifoSimulator

def init_level(pl_size:int,wrbw:int,rdbw:int)->int:
    # The required depth of the FIFO depends on whether the read or write rate is higher
    wdepth = pl_size * (1.0 - float(rdbw)/float(wrbw))
    rdepth = pl_size * (1.0 - float(wrbw)/float(rdbw))
    return math.ceil(max((wdepth),(rdepth)))

def test(depth:int,pl_size:int,wrbw:int,rdbw:int,il:int,simQuantum:int,tol=0.30):
    fifo = Fifo(depth=depth,verbose=False)
    sim  = FifoSimulator(
        fifoHandle=fifo,
        pl_size=pl_size,
        writeBandwidth=wrbw,
        readBandwidth=rdbw,
        initLevel=il,
        simQuantum=simQuantum)

    sim.simulate()

    assert not fifo.error, f"FIFO error ({fifo.errorType})"
    assert fifo.level == 0, f"FIFO not emptied (remaining entries={fifo.level})"
    bw_ltol = float((1.0-tol) * wrbw/rdbw)
    bw_utol = float((1.0+tol) * wrbw/rdbw)
    assert fifo.bwratio > bw_ltol, f"Simulated W:R bandwidth ratio out of lower-bound ({bw_ltol:.3f})"
    assert fifo.bwratio < bw_utol, f"Simulated W:R bandwidth ratio out of upper-bound ({bw_utol:.3f})"

def main():
    for _ in range(5):
        test(depth=400,pl_size=200,wrbw=110,rdbw=100,il=40,simQuantum=1)
        il = init_level(200,100,110)
        test(depth=400,pl_size=200,wrbw=100,rdbw=110,il=math.ceil(il*3),simQuantum=1)

if __name__ == '__main__':
    main()