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

from fifo_pkg.Fifo import Fifo

class FifoSimulator(object):
    '''
    Class which simulates a Fifo object using independent producer and consumer threads.
    Each thread operates on the same Fifo object and uses a binary random distrubtion for
    its operation based on the relative read/write bandwidths
    '''
    def __init__(self,fifoHandle:Fifo,pl_size:int=128,writeBandwidth:int=100,readBandwidth:int=100,initLevel:int=None):
        self._fifo       = fifoHandle
        self._pl_size    = pl_size
        self._wrate      = writeBandwidth
        self._rrate      = readBandwidth
        self._init_level = initLevel
        if initLevel:
            assert initLevel<self._fifo.depth, f"Specified init_level={initLevel} greater or equal to depth={self._fifo.depth}"
            self._fifo.bulk_pushes(initLevel)
        else:
            self._fifo.bulk_pushes(1) # Always assume one entry in the FIFO before we start the sim

    def producer_thread(self):
        rem_pl = self._pl_size - self._init_level
        while rem_pl>0 and not self._fifo.error:
            if FifoSimulator.getRandomBool([self._wrate,self._rrate])==True:
                self._fifo.push()
                rem_pl -= 1
            else:
                self._fifo.wnop()

    def consumer_thread(self):
        rem_pl = self._pl_size
        while rem_pl>0 and not self._fifo.error:
            if FifoSimulator.getRandomBool([self._rrate,self._wrate])==True:
                self._fifo.pop()
                rem_pl -= 1
            else:
                self._fifo.rnop()

    def simulate(self):
        producer_fhandle = lambda : self.producer_thread()
        consumer_fhandle = lambda : self.consumer_thread()

        threadList = [producer_fhandle, consumer_fhandle]

        with concurrent.futures.ThreadPoolExecutor(max_workers=None) as executor:
            _ = {executor.submit(x): x for x in threadList}

    @staticmethod
    def getRandomBool(probs:list)->bool:
        return random.choices([True,False],probs,k=1)[0]
