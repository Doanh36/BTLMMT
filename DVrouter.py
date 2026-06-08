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
            self.neighbor_vectors[port] = json.loads(packet.content)
 
            new_vectors = {self.addr: 0}
            new_ft = {}
 
            all_dsts = set(self.my_vectors.keys())
            for p in self.neighbor_vectors:
                all_dsts.update(self.neighbor_vectors[p].keys())
            for info in self.neighbor_costs.values():
                all_dsts.add(info['addr'])
 
            for dst in all_dsts:
                if dst == self.addr:
                    continue
                best_dist = self.INFINITY
                best_port = None
                for p, info in self.neighbor_costs.items():
                    if info['addr'] == dst and info['cost'] < best_dist:
                        best_dist = info['cost']
                        best_port = p
                   
                    if p in self.neighbor_vectors and dst in self.neighbor_vectors[p]:
                        total = info['cost'] + self.neighbor_vectors[p][dst]
                        if total < best_dist:
                            best_dist = total
                            best_port = p
                new_vectors[dst] = best_dist
                if best_port is not None and best_dist < self.INFINITY:
                    new_ft[dst] = best_port
            if new_vectors != self.my_vectors or new_ft != self.forwarding_table:
                self.my_vectors = new_vectors
                self.forwarding_table = new_ft
                
                for p in self.neighbor_costs:
                    vec_to_send = self.my_vectors.copy()
                    for dst, best_port in self.forwarding_table.items():
                        if best_port == p:
                            vec_to_send[dst] = self.INFINITY
                    pkt = Packet(Packet.ROUTING, self.addr, None)
                    pkt.content = json.dumps(vec_to_send)
                    self.send(p, pkt)

    def handle_new_link(self, port, endpoint, cost):
        """Handle new link."""
        # TODO
        #   update the distance vector of this router
        #   update the forwarding table
        #   broadcast the distance vector of this router to neighbors
        self.neighbor_costs[port] = {'addr': endpoint, 'cost': cost}
        new_vectors = {self.addr: 0}
        new_ft = {}
 
        all_dsts = set(self.my_vectors.keys())
        for p in self.neighbor_vectors:
            all_dsts.update(self.neighbor_vectors[p].keys())
        for info in self.neighbor_costs.values():
            all_dsts.add(info['addr'])
 
        for dst in all_dsts:
            if dst == self.addr:
                continue
            best_dist = self.INFINITY
            best_port = None
            for p, info in self.neighbor_costs.items():
                if info['addr'] == dst and info['cost'] < best_dist:
                    best_dist = info['cost']
                    best_port = p
                if p in self.neighbor_vectors and dst in self.neighbor_vectors[p]:
                    total = info['cost'] + self.neighbor_vectors[p][dst]
                    if total < best_dist:
                        best_dist = total
                        best_port = p
            new_vectors[dst] = best_dist
            if best_port is not None and best_dist < self.INFINITY:
                new_ft[dst] = best_port
                
        if new_vectors != self.my_vectors or new_ft != self.forwarding_table:
            self.my_vectors = new_vectors
            self.forwarding_table = new_ft
            for p in self.neighbor_costs:
                vec_to_send = self.my_vectors.copy()
                for dst, best_port in self.forwarding_table.items():
                    if best_port == p:
                        vec_to_send[dst] = self.INFINITY
                        
                pkt = Packet(Packet.ROUTING, self.addr, None)
                pkt.content = json.dumps(vec_to_send)
                self.send(p, pkt)
        pass

    def handle_remove_link(self, port):
        """Handle removed link."""
        # TODO
        #   update the distance vector of this router
        #   update the forwarding table
        #   broadcast the distance vector of this router to neighbors
        if port in self.neighbor_costs:
            del self.neighbor_costs[port]
        if port in self.neighbor_vectors:
            del self.neighbor_vectors[port]

        new_vectors = {self.addr: 0}
        new_ft = {}

        all_dsts = set(self.my_vectors.keys())
        for p in self.neighbor_vectors:
            all_dsts.update(self.neighbor_vectors[p].keys())
        for info in self.neighbor_costs.values():
            all_dsts.add(info['addr'])

        for dst in all_dsts:
            if dst == self.addr:
                continue
            best_dist = self.INFINITY
            best_port = None
           
            for p, info in self.neighbor_costs.items():
                if info['addr'] == dst and info['cost'] < best_dist:
                    best_dist = info['cost']
                    best_port = p
                if p in self.neighbor_vectors and dst in self.neighbor_vectors[p]:
                    total = info['cost'] + self.neighbor_vectors[p][dst]
                    if total < best_dist:
                        best_dist = total
                        best_port = p
           
            new_vectors[dst] = best_dist
            if best_port is not None and best_dist < self.INFINITY:
                new_ft[dst] = best_port

        self.my_vectors = new_vectors
        self.forwarding_table = new_ft

        for p in self.neighbor_costs:
            vec_to_send = self.my_vectors.copy()
            for dst, best_port in self.forwarding_table.items():
                if best_port == p:
                    vec_to_send[dst] = self.INFINITY
                    
            pkt = Packet(Packet.ROUTING, self.addr, None)
            pkt.content = json.dumps(vec_to_send)
            self.send(p, pkt)

    def handle_time(self, time_ms):
        """Handle current time."""
        if time_ms - self.last_time >= self.heartbeat_time:
            self.last_time = time_ms
            # TODO
            #   broadcast the distance vector of this router to neighbors
            for p in self.neighbor_costs:
                vec_to_send = self.my_vectors.copy()
                for dst, best_port in self.forwarding_table.items():
                    if best_port == p:
                        vec_to_send[dst] = self.INFINITY
                pkt = Packet(Packet.ROUTING, self.addr, None)
                pkt.content = json.dumps(vec_to_send)
                self.send(p, pkt)
            pass

    def __repr__(self):
        """Representation for debugging in the network visualizer."""
        # TODO
        #   NOTE This method is for your own convenience and will not be graded
        return json.dumps(self.my_vectors)
