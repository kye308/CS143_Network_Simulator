from pqueue import event_queue, enqueue
import router
import link
from metrics import cprint

HALF_DUPLEX = False

class Event:
    ''' Generic Event class, default priority 3'''
    def __init__(self, start_time, priority = 3):
        self.start_time = start_time
        self.priority = priority
        
#def process(self): pass

class SendPacket(Event):
    def __init__(self, start_time, packet, link, sender):
        self.start_time = start_time
        # Set priority to favour SendPacket events in order of packet number
        self.priority = 5 + (1 - 1.0/(packet.number + 1))
        self.link = link
        self.packet = packet
        self.sender = sender

    def process(self):
        self.link.buffer_add((self.packet, self.sender))
        enqueue(CheckBuffer(self.start_time, self.link))

class CheckBuffer(Event):
    def __init__(self, start_time, link):
        self.start_time = start_time
        self.priority = 2
        self.link = link

    def process(self):
        if (self.link.buf_processing or self.link.buffer_empty()):
            return
        else:    
            self.link.buf_processing = True
            assert(self.link.buffer_empty() == False)
            packet, src = self.link.buffer_get()

            send_time = packet.size / self.link.rate + self.link.prop_delay
            receiver = self.link.get_receiver(src)
            enqueue(ReceivePacket(self.start_time + send_time, packet, \
                self.link, receiver))

            next_pkt, next_src = self.link.buffer_peek()
            if next_src is not None:
                next_dest = self.link.get_receiver(next_src)
            else:
                next_dest = None

            # if next_dest is None or self.link.curr_recipient != next_dest:
            if next_dest is not None and self.link.curr_recipient != next_dest and HALF_DUPLEX:
                self.link.curr_recipient = next_dest
                done_time = packet.size / self.link.rate + self.link.prop_delay
            else:
                done_time = packet.size / self.link.rate

            enqueue(BufferDoneProcessing(self.start_time + done_time, self.link))

class BufferDoneProcessing(Event):
    def __init__(self, start_time, link):
        self.start_time = start_time
        self.priority = 1
        self.link = link

    def process(self):
        self.link.buf_processing = False
        self.link.size_in_transit = 0
        enqueue(CheckBuffer(self.start_time, self.link))

class ReceivePacket(Event):
    def __init__(self, start_time, packet, link, receiver):
        self.start_time = start_time
        self.priority = 3
        self.packet = packet
        self.link = link
        self.receiver = receiver

    def process(self):
        enqueue(CheckBuffer(self.start_time, self.link,))
        self.receiver.receive(self.packet, self.start_time)

class RtPktTimeout(Event):
    def __init__(self, start_time, router, rtpkt):
        self.start_time = start_time
        self.router = router
        self.rtpkt = rtpkt
        self.priority = 2

    def process(self):
        self.rtpkt.sender.handle_timeout(self.start_time, self.rtpkt)


class Reroute(Event):
    WAIT_INTERVAL = 5
    def __init__(self, start_time, round_no):
        self.start_time = start_time
        self.round_no = round_no
        self.priority = 5  #rerouting should happen after any simultaneous events

    def process(self):
        # Debugging output
        cprint ("==================================")
        cprint ("Rerouting round %d" % self.round_no)
        
        # Update link costs, trigger rerouting, and enqueue the event
        # for the next rerouting
        link.set_linkcosts()
        router.reset_bf(self.start_time, self.round_no)
        enqueue(Reroute(self.start_time + Reroute.WAIT_INTERVAL, self.round_no + 1))

        # Debugging output
        cprint ("Link costs:")
        coststr = ""
        for l_id in link.Link.ids:
            coststr += "%s: %d " % (l_id, link.Link.l_map[l_id].bf_lcost)
        cprint (coststr)
        cprint ("\nRouting tables:")
        for r_id in router.Router.ids:
            cprint (r_id + str(router.Router.r_map[r_id].routing_table))
        cprint ("==================================")

class PacketTimeout(Event):
    def __init__(self, start_time, packet):
        self.start_time = start_time
        self.packet = packet
        self.priority = 3

    def process(self):
        self.packet.flow.handleTimeout(self.packet, self.start_time)


# Used specifically for TCP FAST.
class UpdateWindow(Event):
    def __init__(self, start_time, flow):
        self.start_time = start_time
        self.priority = 3
        self.flow = flow

    def process(self):
        self.flow.window_size = self.flow.fast_window()
        enqueue(UpdateWindow(self.start_time + self.flow.update_period, \
            self.flow))
        cprint ('%s updated window to %d' % (self.flow.id, self.flow.window_size))