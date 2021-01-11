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

class Fifo(object):
    '''
    A simple class to model a FIFO construct which can be
    simulated with independent producer/consumer threads.
    '''

    def __init__(self,depth:int,verbose:bool=False):
        self._depth = depth
        self._verbose = verbose

        self._popCount  = 0     # Total pops on this object
        self._pushCount = 0     # Total pushes on this object
        self._error     = False # Error flag
        self._errorType = ''    # Error cause string
        self._wnopCount = 0     # Write(push) no-operation count
        self._rnopCount = 0     # Read(pop)   no-operation count
        self._maxLevel  = 0     # Maximum level of Fifo during its lifetime
    
        # Thread synchronization lock (bound)
        self.__lock = threading.Lock()

    def bulk_pushes(self,num_pushes:int):
        self._pushCount = num_pushes

    @property
    def depth(self)->int:
        return self._depth

    @property
    def empty(self)->bool:
        return self.level == 0

    @property
    def full(self)->bool:
        return self.level == self._depth
    
    @property
    def error(self)->bool:
        return self._error

    @property
    def level(self)->int:
        self.__lock.acquire()
        tmp = self._pushCount - self._popCount
        if tmp > self._maxLevel:
            self._maxLevel = tmp 
        self.__lock.release()
        return tmp
        
    def push(self):
        if self.full:
            print("Error: FIFO is full!")
            self._error = True
            self._errorType = 'overrun'
        else:
            if self._verbose:
                print(f"Pushed entry (level = {self.level})\n")
            self._pushCount +=1

    def pop(self):
        if self.empty:
            print("Error: FIFO is empty!")
            self._error = True
            self._errorType = 'underrun'
        else:
            if self._verbose:
                print(f"Popped entry (level = {self.level})\n")
            self._popCount +=1

    def wnop(self):
        self._wnopCount += 1

    def rnop(self):
        self._rnopCount += 1

    def __str__(self):
        rstr  = f"depth                  = {self._depth}\n"
        rstr += f"push-count             = {self._pushCount}\n"
        rstr += f"pop-count              = {self._popCount}\n"
        rstr += f"write port nop-count   = {self._wnopCount}\n"
        rstr += f"read port nop-count    = {self._rnopCount}\n"
        rstr += f"total op-count         = {self._wnopCount+self._rnopCount+self._pushCount+self._popCount}\n"
        rstr += f"Fifo max-level reached = {self._maxLevel}\n"
        rstr += f"Simulated W:R BW ratio = {self._rnopCount/self._wnopCount:.2f}\n"
        rstr += f"error-status flag      = {self.error} ({self._errorType})\n"
        return rstr
