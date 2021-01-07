# Overview
This project includes useful tools to aid designers in the education of the sizing of FIFO constructs. It was originally created to provide an example simulator for an article on sizing hardware FIFOs (see [here](https://sebastian-ahmed.medium.com/a-primer-on-sizing-hardware-fifos-c1db97b9a25e))

# System Requirements
- Python 3.6 or later version
- Numpy library

# Key Features
- Simulation and parameter calculation of arbitrary FIFO sizes, payloads and consumer/producer relative bandwidths
- Ability to bypass simulation and perform formulaic analysis only
- Simulation 'speed vs short-term accuracy' control via simulator kernel *quantum* size setting, including auto-sizing mode based on payload size

# FIFO Simulator Usage
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
  --quantum <integer>   Number of sim steps per sim quantum
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
Sim quantum        = 1

Running simulation...
Started Fifo producer thread...
Started Fifo consumer thread...
Starting kernel thread...
depth = 2000
push-count = 1000
pop-count = 1000
write port nop-count = 879
read port nop-count = 923
total op-count = 3802
Fifo max-level reached = 144
Effective push:pop bandwidth ratio = 1.05
error-status = False ()

Simulation metrics:
Simulation event queue peak size  = 2
Simulation quantum size           = 1
Total number of simulation events = 3659
Total simulation time (seconds)   = 19.8

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
Sim quantum        = 1

Skipping simulation...


Required Fifo depth per formulaic calculation = 91
```
 
## Initial FIFO level
Because the simulator uses a weighted random distribution, there is no guarantee that over a small set of initial samples, the distribution will reflect the relative read and write bandwidths. As such, it is possible to sometimes see *underrun* simulation errors  (or *overrun* when selecting small max FIFO sizes). A typical FIFO based interface should have some level or initial FIFO priming especially when the read size is faster than the write side. As such it is important to choose reasonable initial priming levels.

## Simulation "quantum" size (speed vs accuracy)
The `--quantum` command-line option provides a way to **speed up a simulation** at some cost of *short term* accuracy. The default setting is `1` which is the maximum accuracy setting. Increasing this value increases the number of push and pop operations to occur with the consumer/producers simulator threads before yielding to the simulation kernel thread. By increasing this number, this reduces the number of simulation events generated by the threads over the entire simulation which reduces the inter-thread communication overheads.

Increasing this number should be done with larger payload sizes. Consider the following:
- A payload size of 1000 with `--quantum 1` will generate at least 2000 simulation events (1 per thread including stalls)
- A payload size of 100000 with `--quantum 100` will **also** generate at lease 2000 simulation events

Setting `--quantum 0` (zero) enables the **automatic quantum** selection which is based on the `--plsize` parameter using the following formula:
```python
max(1,plsize/1000)
```

# FIFO Simulator Design
This section is not necessary to understand in order to use the simulator. The purpose is to provide some details on the design of the simulator for the curious.

The simulation is comprised of a DUT (Device Under Test) which is an abstract model of a FIFO encapsulated in the `Fifo` class and a simple **multi-threaded** simulator encapsulated in the `FifoSimulator` class.

## Fifo Class
The Fifo class is a very simple and abstract model of a FIFO. It provides methods to **push** and **pop** and maintains counts to determine the level. It also detects errors (such as *underruns* and *overruns*). Because the Fifo class is designed to work with multiple threads calling its methods, it utilizes a bound **threading lock** for critical sections such as determining the FIFO level.

## FifoSimulator Class
There are four main pieces to this class: 
- A *producer* thread which performs **push** operations on the *shared* Fifo object based on a target statistical distribution of the write bandwidth. This thread performs a *quantum* worth of operations before blocking to the kernel
- A *consumer* thread which performs **pop** operations on the *shared* Fifo object based on a target statistical distribution of the read bandwidth. This thread performs a *quantum* worth of operations before blocking to the kernel
- A simulator *kernel* thread which controls the simulation by managing an **event queue**. When the producer and consumer threads **block**, their associated pending-status events are pushed to the event queue. The kernel enables thread events in the order they were pended, which ends up resulting in a fair distribution of thread operations
- A simulation method which configures and initiates the threads via a thread-pool context manager object. This method also assigns thread management events to each thread

Each thread registers itself with the kernel which allows the kernel to monitor the number of active threads. This allows the kernel thread to complete once all client threads finish. This particular design can thus support more than the two threads in the simulator.

It can thus be noted that increasing the *quantum* value allows each of the producer/consumer threads to perform their operations in "zero-time" without being blocked for a larger sequence of their operations. Operations within the quantum are thus not sequenced by the kernel, and there can be no assumptions on the relative ordering of push and pop operations within the quantum (which is the source of short-term innacuracy). Increasing the quantum size does not however change the overall bandwidth ratio, but can result in underrun or overrun errors that otherwise may not have occurred. 