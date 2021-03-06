# Copyright 2021 Sebastian Ahmed
# This file, and derivatives thereof are licensed under the Apache License, Version 2.0 (the "License");
# Use of this file means you agree to the terms and conditions of the license and are in full compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software distributed under the License is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, EITHER EXPRESSED OR IMPLIED.
# See the License for the specific language governing permissions and limitations under the License.

import threading
import concurrent.futures
import random
import math
import numpy as np
import time

from fifo_pkg.Fifo import Fifo

class FifoSimulator(object):
    '''
    Class which simulates a Fifo object using independent producer and consumer threads with
    a simple simulation kernel with a configurable simulation quantum
    Each thread operates on the same Fifo object and uses a weighted random distrubtion for
    its operation based on the relative read/write bandwidths
    '''
    def __init__(
        self,
        fifoHandle:Fifo,
        pl_size:int=128,
        writeBandwidth:int=100,
        readBandwidth:int=100,
        initLevel:int=None,
        nosim:bool=False,
        simQuantum:int=1):
        self._fifo       = fifoHandle
        self._pl_size    = pl_size
        self._wrate      = writeBandwidth
        self._rrate      = readBandwidth
        self._init_level = initLevel
        self._nosim      = nosim

        assert pl_size > simQuantum, f"simQuantum ({simQuantum}) > pl_size({pl_size})"
        assert initLevel<self._pl_size, f"Specified init_level={initLevel} greater or equal to pl_size={self._pl_size}"

        if simQuantum <= 0:
            self._simQuantum = self.autoQuantum()
            print(f"Auto quantum-mode selected. Caclulated quantum={self._simQuantum}\n")
        else:
            self._simQuantum = simQuantum

        if initLevel:
            assert initLevel<self._fifo.depth, f"Specified init_level={initLevel} greater or equal to depth={self._fifo.depth}"
            self._fifo.bulk_pushes(initLevel)
        else:
            self._fifo.bulk_pushes(1) # Always assume one entry in the FIFO before we start the sim

        # We create a single event object per thread. Each thread communicates with the kernel by
        # pushing its inactive event into a pend-queue and then blocking by waiting for that event
        # to become active.
        self._kernelEvents = {
            'e_producer' : threading.Event(),
            'e_consumer' : threading.Event()
        }

        self._maxqlen = 0     # Stat variable to track maximum size of sim kernel event queue
        self._evcount = 0     # Stat variable to track total number of simulation events
        self._pendq = []      # Pended events queue
        self._threadCount = 0 # Number of active sim kernel threads

        # Thread synchronization lock (bound)
        self.__lock = threading.Lock()

        # Thread call handles
        self._threadList = []

        # Flag to reflect that all pushes are done which allows consumer thread to no longer
        # block and just finish consuming
        self._pushesDone = False

    def autoQuantum (self)->int:
        '''
        Determines automatic sim quantum based on payload size
        '''
        return int(max(1,self._pl_size/1000))

    def threadStart(self):
        self.__lock.acquire()
        self._threadCount += 1
        self.__lock.release()

    def threadEnd(self):
        self.__lock.acquire()
        self._threadCount -= 1
        self.__lock.release()

    def threadPend(self,ev:threading.Event):
        '''
        This method places a blocking thread's event into a pend queue
        '''
        self.__lock.acquire()
        self._pendq.append(ev)
        self.__lock.release()

    def kernel_thread(self):
        '''
        This thread implements a simple simulator kernel which sequences thread events
        based on the pend queue order. As pended events are popped from the queue, they
        are set to unblock each thread.
        '''
        time.sleep(0.1) # Block time for threads to register active state
        print("Starting kernel thread...")
        while self._threadCount > 0:
            if len(self._pendq) > 0:
                if len(self._pendq) > self._maxqlen:
                    self._maxqlen = len(self._pendq)
                cur_ev = self._pendq.pop(0)
                self._evcount += 1
                # The below assertion checks that any event pulled from queue must be inactive
                assert not cur_ev.is_set(), "Event queue ERROR, active event found"
                cur_ev.set()
                cur_ev.clear()
        print("Ending kernel thread, no more client threads.")
        assert len(self._pendq) == 0, "Kernel ERROR, event queue has entries without active threads"

    def producer_thread(self,ev:threading.Event):
        self.threadStart()
        print("Started Fifo producer thread...")
        rem_pl = self._pl_size - self._init_level
        quant_count = self._simQuantum
        while rem_pl>0 and not self._fifo.error:
            if FifoSimulator.getRandomBool([self._wrate,self._rrate])==True:
                self._fifo.push()
                rem_pl -= 1
            else:
                self._fifo.wnop() # no-operation
            if quant_count == 1:
                quant_count = self._simQuantum # reset the quantum
                self.threadPend(ev)
                ev.wait()
            else:
                quant_count -= 1
        self._pushesDone = True # Tell consumer, we are done pushing
        self.threadEnd()

    def consumer_thread(self,ev:threading.Event):
        self.threadStart()
        print("Started Fifo consumer thread...")
        rem_pl = self._pl_size
        quant_count = self._simQuantum
        while rem_pl>0 and not self._fifo.error:
            # Don't call the randomizer if producer is done as this skewes the effective
            # bandwidth ratio metrics
            if self._pushesDone or FifoSimulator.getRandomBool([self._rrate,self._wrate])==True:
                self._fifo.pop()
                rem_pl -= 1
            else:
                self._fifo.rnop() # no-operation
            # Only pend if the producer thread is still active
            if not self._pushesDone:
                if quant_count == 1:
                    quant_count = self._simQuantum # reset the quantum
                    self.threadPend(ev)
                    ev.wait()
                else:
                    quant_count -= 1
        self.threadEnd()

    def calcDepth(self):
        '''
        Calculates required FIFO depth based on simple rate ratio formula.
        The formula does not take into account any latencies
        '''
        # The required depth of the FIFO depends on whether the read or write rate is higher
        wdepth = self._pl_size * (1.0 - float(self._rrate)/float(self._wrate))
        rdepth = self._pl_size * (1.0 - float(self._wrate)/float(self._rrate))
        return math.ceil(max((wdepth),(rdepth)))
    
    def simulate(self):
        '''
        Performs the multi-threaded simulation and formulaic calculation
        '''

        if self._nosim:
            print("Skipping simulation...\n")
        else:
            print("Running simulation...")

            # Define all thread call handles and add them to the thread-list
            self._threadList.append(lambda : self.kernel_thread()) 
            self._threadList.append(lambda : self.producer_thread(ev=self._kernelEvents['e_producer']))
            self._threadList.append(lambda : self.consumer_thread(ev=self._kernelEvents['e_consumer']))

            # max_workers=None essentially does not constrain things
            with concurrent.futures.ThreadPoolExecutor(max_workers=None) as executor:
                futures = {executor.submit(x): x for x in self._threadList}

                # The future handle provides an iterator of all threads.
                # The order of the iterator follows completion.
                for future in concurrent.futures.as_completed(futures):
                    try:
                        _ = future.result()
                    except Exception as exc:
                        print(f"{future} : {exc}")

            print("\nFIFO Simulation Summary:")
            print("-------------------------")
            print(self._fifo)
            print("Simulation metrics:")
            print("-------------------")
            print(f"Simulation event queue peak size  = {self._maxqlen}")
            print(f"Simulation quantum size           = {self._simQuantum}")
            print(f"Total number of simulation events = {self._evcount}")
            print(f"Total simulation time (seconds)   = {time.process_time():.1f}\n")
            if self._fifo.error:
                print("Simulation FAILED!")
            else:
                print("Simulation PASSED")

        print(f"\nRequired Fifo depth per formulaic calculation = {self.calcDepth()}")

    @staticmethod
    def getRandomBool(freqs:list)->bool:
        '''
        Generate a random boolean based on the absolute frequencies of input list freqs
        Uses a weighted discrete distribution
        '''
        # We use a simple Binomial distribution but with trials=1. This should be
        # equivalent to a Bernoulli distribution. Note that the size parameter when 
        # set to None, enables the returning of a scalar. When choosing a shape of 1
        # the results did not seem to behave very well.
        p = float(freqs[0]/sum(freqs))
        return np.random.binomial(1,p,size=None)
