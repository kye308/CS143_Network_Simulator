import Queue

''' 
Wrapper around the built-in priority queue for the global event queue

Global variables:
    - event_queue: The global event queue

Functions:
    - empty():  Checks if the event queue is empty
    - enqueue(Event e):  Enqueues event e
    - dequeue():  Removes the event with the smallest end_time from 
                  event_queue. Assumes that event_queue is not-empty,
                  raises an AssertionError if not.
'''

event_queue = Queue.PriorityQueue()
global_time = 0.0

def enqueue(evt):
    event_queue.put((evt.start_time, evt.priority, evt))

def dequeue():
    assert(not event_queue.empty())
    return event_queue.get()[2]

def qempty():
    return event_queue.empty()

def set_global_time(t):
    global global_time
    global_time = t

def get_global_time():
    return global_time