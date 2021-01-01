# FIFO Tools
This project includes useful tools to aid designers in the education of the sizing of FIFO constructs.

# Quick set-up
This project uses Python and requires version 3.6 or newer. Everything needed to run the tools is includid in this repo

# FIFO Simulator
The FIFO simulator is invoked with `fifo_sim.py`. Specifying the `--help` command-line argument shows all the options. The simulator uses the Python threading/concurrency libraries to emulate concurrent FIFO consumer/producer threads operating on the simulated FIFO objet

The order of read/write operations on the threads is based upon a random distribution which is based on the read and write relative bandwidths

The simulation prints out a summary of statistics of the simulation and also any error conditions that occurred such as a FIFO *underrun* or *overrun*
