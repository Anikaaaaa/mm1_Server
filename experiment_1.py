"""
The task is to simulate an M/M/k system with a single queue.
Complete the skeleton code and produce results for three experiments.
The study is mainly to show various results of a queue against its ro parameter.
ro is defined as the ratio of arrival rate vs service rate.
For the sake of comparison, while plotting results from simulation, also produce the analytical results.
"""

import heapq
import random
from builtins import print

import matplotlib.pyplot as plt
MAX_TIME = 800000
#MAX_TIME = 10000

# Parameters
class Params:
    def __init__(self, lambd, mu, k):
        self.lambd = lambd  # interarrival rate
        self.mu = mu  # service rate
        self.k = k
    # Note lambd and mu are not mean value, they are rates i.e. (1/mean)

# Write more functions if required


# States and statistical counters
class States:
    def __init__(self):
        # States
        self.queue = []
        # Declare other states variables that might be needed
        self.server_status = 0
        self.delay = 0.0
        self.length = 0
        self.time_since_last_event = 0.0
        self.time_of_last_event = 0.0
        self.total_time_served = 0.0
        self.service_time=0.0
        self.no_of_cust_delayed = 0
        self.num_in_queue = 0
        self.area_num_in_queue = 0.0
        self.num_waited = 0
        self.servers_status = []
        #self.service_time = 0
        self.wait_time = 0
        #self.busy=1
        # Statistics
        self.util = 0.0
        self.avgQdelay = 0.0
        self.avgQlength = 0.0
        self.served = 0
        self.QueueLimit = 1000
        self.num_in_q=0
        self.no_of_q_avilable = 0



    def update(self, sim, event):
        # Complete this function
        self.time_since_last_event =  event.eventTime - self.time_of_last_event
        self.time_of_last_event = event.eventTime
        self.total_time_served += ( self.server_status * self.time_since_last_event )
        #self.total_time_served =
        self.area_num_in_queue += ( self.num_in_q * self.time_since_last_event)


    def finish(self, sim):
        self.avgQdelay = self.delay / self.served
        self.avgQlength = self.area_num_in_queue / sim.simclock
        self.util = self.total_time_served / sim.simclock


    def printResults(self, sim):
        # DO NOT CHANGE THESE LINES
        print('MMk Results: lambda = %lf, mu = %lf, k = %d' % (sim.params.lambd, sim.params.mu, sim.params.k))
        print('MMk Total customer served: %d' % (self.served))
        print('MMk Average queue length: %lf' % (self.avgQlength))
        print('MMk Average customer delay in queue: %lf' % (self.avgQdelay))
        print('MMk Time-average server utility: %lf' % (self.util))

    def getResults(self, sim):
        return (self.avgQlength, self.avgQdelay, self.util)

    def AnalyticalResults(self, sim):
        print('MMk AnalyticalResults  : lambda = %lf, mu = %lf, k = %d' % (sim.params.lambd, sim.params.mu, sim.params.k))
        #print('MMk Total customer served: %d' % (self.served))
        aql=0
        adq=0
        if sim.params.mu != sim.params.lambd :
            aql = float((sim.params.lambd ** 2) / (sim.params.mu * (sim.params.mu - sim.params.lambd)))
            adq = float(sim.params.lambd / (sim.params.mu * (sim.params.mu - sim.params.lambd)))
        uf = float(sim.params.lambd / sim.params.mu)
        print('MMk Average queue length: %lf' % (aql))
        print('MMk Average customer delay in queue: %lf' % (adq))
        print('MMk Time-average server utility: %lf' % (uf))

    # Write more functions if required


class Event:
    def __init__(self, sim):
        self.eventType = None
        self.sim = sim
        self.eventTime = None

    def process(self, sim):
        raise Exception('Unimplemented process method for the event!')

    def __repr__(self):
        return self.eventType


class StartEvent(Event):
    def __init__(self, eventTime, sim):
        self.eventTime = eventTime
        self.eventType = 'START'
        self.sim = sim

    def process(self, sim):
        Time = sim.simclock + random.expovariate(sim.params.lambd)
        #print('Scheduling Arrival event at start event at %f' %self.eventTime)
        sim.scheduleEvent(ArrivalEvent ( Time,sim ))
        sim.scheduleEvent(ExitEvent(MAX_TIME, sim))

class ExitEvent(Event):
    def __init__(self, eventTime, sim):
        self.eventTime = eventTime
        self.eventType = 'EXIT'
        self.sim = sim

    def process(self, sim):
        # Complete this function
        None


class ArrivalEvent(Event):
    def __init__(self, eventTime, sim):
        self.eventTime = eventTime
        self.eventType = 'ARRIVAL'
        self.sim = sim


    def process(self, sim):
        arrrval_time = sim.simclock + random.expovariate(sim.params.lambd)
        sim.scheduleEvent(ArrivalEvent(arrrval_time , sim))

        if sim.states.server_status == 0 :
            delay_1= 0.0
            sim.states.server_status = 1
            sim.states.delay += delay_1
            sim.states.served += 1
            departure_time = sim.simclock + random.expovariate(sim.params.mu)
            sim.scheduleEvent(DepartureEvent(departure_time, sim ))

        else:
            #####
            if len(sim.states.queue) > sim.states.QueueLimit:
                print('Queue out of limit')
                exit()
            sim.states.num_in_queue +=1
            sim.states.num_waited += 1
            sim.states.num_in_q += 1
            sim.states.queue.append(sim.simclock)



class DepartureEvent(Event):
    # Write __init__ function
    def __init__(self, eventTime, sim):
        self.eventTime = eventTime
        self.eventType = 'DEPARTURE'
        self.sim = sim

    def process(self, sim):

        if sim.states.num_in_q == 0 :
            sim.states.server_status = 0

        else:
            sim.states.num_in_q -= 1
            sim.states.served = sim.states.served + 1
            sim.states.no_of_cust_delayed += 1
            time = sim.states.queue.pop(0)
            depatrure_time = sim.simclock +  random.expovariate(sim.params.mu)
            delay =  sim.simclock - time
            sim.states.delay = sim.states.delay + delay
            sim.scheduleEvent(DepartureEvent(depatrure_time, sim))


        #None


class Simulator:
    def __init__(self, seed):
        self.eventQ = []
        self.simclock = 0
        self.seed = seed
        self.params = None
        self.states = None

    def initialize(self):
        self.simclock = 0
        self.scheduleEvent(StartEvent(0, self))


    def configure(self, params, states):
        self.params = params
        self.states = states

    def now(self):
        return self.simclock

    def scheduleEvent(self, event):
        heapq.heappush(self.eventQ, (event.eventTime, event))

    def run(self):
        random.seed(self.seed)
        self.initialize()

        while len(self.eventQ) > 0:


            time, event = heapq.heappop(self.eventQ)
            if event.eventType == 'EXIT':
                break

            if self.states != None:
                self.states.update(self, event)

            print(event.eventTime, 'Event', event)
            self.simclock = event.eventTime
            event.process(self)
        self.states.finish(self)


    def printResults(self):
        self.states.printResults(self)
        self.states.AnalyticalResults(self)

    def getResults(self):
        return self.states.getResults(self)


def experiment1():
    seed = 101
    sim = Simulator(seed)
    sim.configure(Params(5.0 / 60, 8.0 / 60, 1), States())
    sim.run()
    sim.printResults()


def main():
     experiment1()




main()