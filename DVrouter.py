####################################################
# DVrouter.py
# Name:
# HUID:
#####################################################

from router import Router
from packet import Packet  
import json


class DVrouter(Router):
    """Distance vector routing protocol implementation.

    Add your own class fields and initialization code (e.g. to create forwarding table
    data structures). See the `Router` base class for docstrings of the methods to
    override.
    """

    def __init__(self, addr, heartbeat_time):
        Router.__init__(self, addr)  # Initialize base class - DO NOT REMOVE
        self.heartbeat_time = heartbeat_time
        self.last_time = 0
        # TODO
        #   add your own class fields and initialization code here
        
        self.INFINITY = 16
        self.my_vectors = {self.addr: 0}
        self.forwarding_table = {}
        self.neighbor_costs = {}
        self.neighbor_vectors = {}

        pass

    def handle_packet(self, port, packet):
        """Process incoming packet."""
        # TODO
        if packet.is_traceroute:
            dst = packet.dst_addr
            if dst in self.forwarding_table:
                self.send(self.forwarding_table[dst], packet)
            return
        else:
            neighbor_vector = json.loads(packet.content)
            self.neighbor_vectors[port] = neighbor_vector

            changed = False
          
            for dst in neighbor_vector:
                if dst == self.addr:
                    continue 
                
                
                cost_to_neighbor = self.neighbor_costs[port]['cost']
                total_cost = cost_to_neighbor + neighbor_vector[dst]
                
 
                if dst not in self.my_vectors or total_cost < self.my_vectors[dst]:
                    self.my_vectors[dst] = total_cost
                    self.forwarding_table[dst] = port
                    changed = True
                if changed:
                for p in self.neighbor_costs:
                    pkt = Packet(Packet.ROUTING, self.addr, None)
                    pkt.content = json.dumps(self.my_vectors)
                    self.send(p, pkt)

    def handle_new_link(self, port, endpoint, cost):
        """Handle new link."""
        # TODO
        #   update the distance vector of this router
        #   update the forwarding table
        #   broadcast the distance vector of this router to neighbors
        self.neighbor_costs[port] = {'addr': endpoint, 'cost': cost}
        self.my_vectors[endpoint] = cost
        self.forwarding_table[endpoint] = port
        
        for p in self.neighbor_costs:
            pkt = Packet(Packet.ROUTING, self.addr, None)
            pkt.content = json.dumps(self.my_vectors)
            self.send(p, pkt)
        pass

    def handle_remove_link(self, port):
        """Handle removed link."""
        # TODO
        #   update the distance vector of this router
        #   update the forwarding table
        #   broadcast the distance vector of this router to neighbors
        self.neighbor_costs[port] = {'addr': endpoint, 'cost': cost}
        self.my_vectors[endpoint] = cost
        self.forwarding_table[endpoint] = port
        
        for p in self.neighbor_costs:
            pkt = Packet(Packet.ROUTING, self.addr, None)
            pkt.content = json.dumps(self.my_vectors)
            self.send(p, pkt)
        pass

    def handle_time(self, time_ms):
        """Handle current time."""
        if time_ms - self.last_time >= self.heartbeat_time:
            self.last_time = time_ms
            # TODO
            #   broadcast the distance vector of this router to neighbors
            pass

    def __repr__(self):
        """Representation for debugging in the network visualizer."""
        # TODO
        #   NOTE This method is for your own convenience and will not be graded
        return f"DVrouter(addr={self.addr})"
