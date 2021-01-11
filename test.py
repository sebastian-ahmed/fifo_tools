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