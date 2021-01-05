# Overview
This project includes useful tools to aid designers in the education of the sizing of FIFO constructs. It was originally created to provide an example simulator for an article on sizing hardware FIFOs (see [here](https://sebastian-ahmed.medium.com/a-primer-on-sizing-hardware-fifos-c1db97b9a25e))

# System Requirements
- Python 3.6 or later version
- Numpy library

# FIFO Simulator
The FIFO simulator is invoked with `fifo_sim.py`. Specifying the `--help` command-line argument shows all the options. The simulator uses the Python threading/concurrency libraries to emulate concurrent FIFO consumer/producer threads operating on the simulated FIFO object

The order and density of read/write operations on the threads is based upon a random distribution which is based on the read and write relative bandwidths

**Note**: Larger payload sizes yield more accurate simulator results because the Python random-number generator requires a sufficient amount of samples to reach the desired random distribution

The simulation prints out a summary of statistics of the simulation and also any error conditions that occurred such as a FIFO *underrun* or *overrun*

The simulator also calculates the theoretical FIFO size required based on standard rate ratio formulaic calculation. This can be compared to the simulated result.

## Usage Options
The output below is based on the `--help` option:

```
usage: fifo_sim.py [-h] [--depth <integer>] [--plsize <integer>] [--writebw <integer>] [--readbw <integer>]
                   [--initlevel <integer>] [--nosim] [--verbose]

A basic FIFO simulator and size calculator

optional arguments:
  -h, --help            show this help message and exit
  --depth <integer>     Max number of entries in the FIFO (simulation only)
  --plsize <integer>    Payload size in number of datums
  --writebw <integer>   Write bandwidth in datums/unit time
  --readbw <integer>    Read bandwidth in datums/unit time
  --initlevel <integer>
                        Initial FIFO level (simulation only)
  --nosim               Skip simulation, and only perform formulaic analysis
  --verbose             Report all operations (simulation only)
```

## Example Usage (Simulation)

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
Payload size       = 1000
Write Bandwidth    = 110
Read Bandwidth     = 100
Max FIFO depth     = 2000
Initial FIFO level = 4

Running simulation...

Started Fifo producer thread...
Started Fifo consumer thread...
depth = 2000
push-count = 1000
pop-count = 1000
write port nop-count = 945
read port nop-count = 1125
total op-count = 4070
Fifo max-level reached = 94
Effective push:pop bandwidth ratio = 1.19
error-status = False ()

Simulation PASSED

Required Fifo depth per formulaic calculation = 91
```

The *nop-count* values reflect the cycles during which the read or write port did not perform operations. The ratio of the read and write nop-counts should reflect the relative bandwidths of each port. You may find that you need to run a larger simulation payload to avoid seeing distributions which appear biased.

Note that when running with the `--verbose` command line option, all FIFO operations during the simulation are printed to the screen along with the run-time FIFO level.

## Example Usage (Formulaic-only)
In order to just run the formulaic analysis, the simulation can be skipped wih the `--nosim` option. In this case, some of the arguments do not need to be specified (see help via `--help` option). Below is the same example as before, but with `--nosim` specified and only with the necessary arguments for the formulaic analysis

```
 ./fifo_sim.py --plsize 1000 --writebw 110 --readbw 100 --nosim
```

The output of the simulator looks as follows:

```
FIFO sim condition summary
Payload size       = 1000
Write Bandwidth    = 110
Read Bandwidth     = 100
Max FIFO depth     = 2000
Initial FIFO level = 4

Skipping simulation...


Required Fifo depth per formulaic calculation = 91
```
 
## Initial FIFO level
Because the simulator uses a weighted random distribution, there is no guarantee that over a small set of initial samples, the distribution will reflect the relative read and write bandwidths. As such, it is possible to sometimes see *underrun* simulation errors  (or *overrun* when selecting small max FIFO sizes). A typical FIFO based interface should have some level or initial FIFO priming especially when the read size is faster than the write side. As such it is important to choose reasonable initial priming levels.
