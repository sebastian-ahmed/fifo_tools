# Overview
This project includes useful tools to aid designers in the education of the sizing of FIFO constructs.

# System Requirements
- Python 3.6 or later version
- Numpy library

# FIFO Simulator
The FIFO simulator is invoked with `fifo_sim.py`. Specifying the `--help` command-line argument shows all the options. The simulator uses the Python threading/concurrency libraries to emulate concurrent FIFO consumer/producer threads operating on the simulated FIFO objet

The order and density of read/write operations on the threads is based upon a random distribution which is based on the read and write relative bandwidths

**Note**: Larger payload sizes yield more accurate simulator results because the Python random-number generator requires a sufficient amount of samples to reach the desired random distribution

The simulation prints out a summary of statistics of the simulation and also any error conditions that occurred such as a FIFO *underrun* or *overrun*

The simulator also calculates the theoretical FIFO size required based on standard rate ratio calculation. This can be compared to the simulated result

## Example Usage

The example below shows usage to simulate a FIFO with the following characteristics:
- Maximum FIFO depth : 2000 entries
- Simulated payload size : 1000 samples/datums
- Relative write bandwidth : 110
- Relative read bandwidth  : 100
- Initial FIFO level (priming FIFO pushes) : 4
```
./fifo_sim.py --depth 2000 --plsize 1000 --writebw 110 --readbw 100 --initlevel 4
```

The output of the simulator looks as follows:

```
FIFO sim condition summary
Max payload size   = 1000
Write Bandwidth    = 110
Read Badwidth      = 100
FIFO depth         = 2000
Initial FIFO level = 4

Running simulation...

Started Fifo producer thread...
Started Fifo consumer thread...
depth = 2000
push-count = 1000
pop-count = 1000
write port nop-count = 905
read port nop-count = 1203
total op-count = 4108
Fifo max-level reached = 141
error-status = False ()

Simulation PASSED

Required Fifo depth per static calculation = 91
```

The *nop-count* values reflect the cycles during which the read or write port did not perform operations. The ratio of the read and write nop-counts should reflect the relative bandwidths of each port. You may find that you need to run a larger simulation payload to avoid seeing distributions which appear biased.

Note that when running with the `--verbose` command line option, all FIFO operations during the simulations are printed to the screen along with the run-time FIFO level.

## Initial FIFO level
Because the simulator uses a weighted random distribution, there is no guarantee that over a small set of initial samples, the distribution will reflect the relative read and write bandwidths. As such, it is possible to sometimes see *underrun* simulation errors  (or *overrun* when selecting small max FIFO sizes). A typical FIFO based interface should have some level or initial FIFO priming especially when the read size is faster than the write side. As such it is important to choose reasonable initial priming levels.
