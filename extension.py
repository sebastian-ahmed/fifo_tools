#!/usr/bin/env python3

'''
This module provides an example of how OOP concepts could be used to extend the Fifo class using
higher-level semantics to describe synthesizable hardware.

First, we extend the semantics of Fifo to create BetterFifo which is more robust, adds a bulk_pop operation
and actually implements data-storage so push and pop methods are overriden.
We then use a couple of BetterFifo objects to run through push and pop operations on two different types of data.

'''

# Copyright 2021 Sebastian Ahmed
# This file, and derivatives thereof are licensed under the Apache License, Version 2.0 (the "License");
# Use of this file means you agree to the terms and conditions of the license and are in full compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software distributed under the License is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, EITHER EXPRESSED OR IMPLIED.
# See the License for the specific language governing permissions and limitations under the License.

import random
import string

from fifo_pkg.Fifo import Fifo

class BetterFifo(Fifo):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)

        self._data = [] # This FiFo actually holds data of any type

    @property
    def bwratio(self)->float:
        '''
        Override property to handle case where nop-counts result in a zero-division exception
        '''
        try:
            return super().bwratio
        except ZeroDivisionError:
            return 0.0
        except:
            raise

    def bulk_pops(self,num_pops:int):
        '''
        Class extension which adds the ability to do a bulk set of pops 
        '''
        for _ in range(num_pops):
            self.pop()

    def pop(self):
        '''
        Override:
        Since this Fifo actually holds data we attempt to return whatever data
        is available to pop from the internal store
        '''
        if not self.empty:
            super().pop()
            popped_data = self._data.pop(0)
            print(f"Popped data = {popped_data}")
            return popped_data
        else:
            super().pop()

    def push(self,data=None):
        '''
        Override/overload:
        Since this Fifo actually holds data we push data in
        '''
        if not self.full:
            print(f"Pushed data = {data}")
            self._data.append(data)
        super().push()

def randstr()->str:
    '''
    Returns a random 16-character upper-case ASCII string
    '''
    return ''.join(random.choices(string.ascii_uppercase,k=16))

def randFloat()->float:
    '''
    Returns a random float from a normal distribution with a median of 50.0 and std-dev of 10.0
    '''
    return random.gauss(50.0,10.0)

FIFO_SIZE = 5

def doFifoStuff(fifo:BetterFifo,datagenfunc):
    print(f"Doing Fifo stuff with {datagenfunc}")


    for _ in range(FIFO_SIZE):
        fifo.push(datagenfunc())

    fifo.bulk_pops(FIFO_SIZE)
    assert fifo.level == 0, f"Expected to have zero entries, but got {fifo.level} instead"
    assert fifo.error == False, f"Got a FIFO error ({fifo.errorType})"

    print(fifo) # Won't get a ZeroDivisionError exception

def test():
    print(__doc__)

    # Note we only create two separate objects because in a synthesizable HDL scenario it
    # is unlikely we can get the lazy evaluation of Python typing. With Python we could have
    # just re-used the same Fifo object, but that may confuse things.
    fifo_of_strings = BetterFifo(depth=FIFO_SIZE,verbose=True)
    fifo_of_floats  = BetterFifo(depth=FIFO_SIZE,verbose=True)

    doFifoStuff(fifo_of_strings,randstr)   # Use a BetterFifo to handle strings
    doFifoStuff(fifo_of_floats,randFloat)  # Use a BetterFifo to handle floats

if __name__ == '__main__':
    test()
