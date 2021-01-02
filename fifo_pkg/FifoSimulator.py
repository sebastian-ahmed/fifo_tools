# Copyright 2021 Sebastian Ahmed
# This file, and derivatives thereof are licensed under the Apache License, Version 2.0 (the "License");
# Use of this file means you agree to the terms and conditions of the license and are in full compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software distributed under the License is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, EITHER EXPRESSED OR IMPLIED.
# See the License for the specific language governing permissions and limitations under the License.

import concurrent.futures
import random
import math
import numpy as np

from fifo_pkg.Fifo import Fifo

class FifoSimulator(object):
    '''
    Class which simulates a Fifo object using independent producer and consumer threads.
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
        nosim:bool=False):
        self._fifo       = fifoHandle
        self._pl_size    = pl_size
        self._wrate      = writeBandwidth
        self._rrate      = readBandwidth
        self._init_level = initLevel
        self._nosim      = nosim

        if initLevel:
            assert initLevel<self._fifo.depth, f"Specified init_level={initLevel} greater or equal to depth={self._fifo.depth}"
            self._fifo.bulk_pushes(initLevel)
        else:
            self._fifo.bulk_pushes(1) # Always assume one entry in the FIFO before we start the sim

    def producer_thread(self):
        print("Started Fifo producer thread...")
        rem_pl = self._pl_size - self._init_level
        while rem_pl>0 and not self._fifo.error:
            if FifoSimulator.getRandomBool([self._wrate,self._rrate])==True:
                self._fifo.push()
                rem_pl -= 1
            else:
                self._fifo.wnop()

    def consumer_thread(self):
        print("Started Fifo consumer thread...")
        rem_pl = self._pl_size
        while rem_pl>0 and not self._fifo.error:
            if FifoSimulator.getRandomBool([self._rrate,self._wrate])==True:
                self._fifo.pop()
                rem_pl -= 1
            else:
                self._fifo.rnop()

    def calcDepth(self):
        '''
        Calculates required FIFO depth based on simple rate ratio formula.
        The forumula does not take into account any latencies
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
            print("Running simulation...\n")

            producer_fhandle = lambda : self.producer_thread()
            consumer_fhandle = lambda : self.consumer_thread()

            threadList = [producer_fhandle, consumer_fhandle]

            with concurrent.futures.ThreadPoolExecutor(max_workers=None) as executor:
                _ = {executor.submit(x): x for x in threadList}

            print(self._fifo)
            if self._fifo.error:
                print("Simulation FAILED!")
            else:
                print("Simulation PASSED")

        print(f"\nRequired Fifo depth per formulaic calculation = {self.calcDepth()}")

    @staticmethod
    def getRandomBool(freqs:list)->bool:
        '''
        Generate a random boolean based on the absolute frequencies of input list freqs
        '''
        # Note: I have found little difference between using the numpy RNG and the 
        # random.choices built-in library. In each case there appears to be a bias
        # for the first element in the sequence.
        problist = [float(x/sum(freqs)) for x in freqs]
        rng = np.random.default_rng()
        return rng.choice(a=[True,False], size=1, replace=True, p=problist)[0]
        #return random.choices([True,False],weights=freqs,k=1)[0]