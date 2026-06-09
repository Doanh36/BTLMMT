####################################################
# LSrouter.py
# Name:
# HUID:
#####################################################

from router import Router
from packet import Packet 
import json
import heapq


class LSrouter(Router):
    """Link state routing protocol implementation.

    Add your own class fields and initialization code (e.g. to create forwarding table
    data structures). See the `Router` base class for docstrings of the methods to
    override.
    """

    def __init__(self, addr, heartbeat_time):

        Router.__init__(self, addr)

        self.heartbeat_time = heartbeat_time
        self.last_time = 0

        self.neighbors = {}

        self.lsdb = {}

        self.forwarding_table = {}

        self.seq_num = 0

        self.lsdb[self.addr] = {
            "seq": self.seq_num,
            "links": {}
        }
    
    def create_lsp(self, router):

        data = self.lsdb[router]

        return json.dumps({
            "router": router,
            "seq": data["seq"],
            "links": data["links"]
        })

    def flood_packet(self, packet, exclude_port=None):

        for port in self.neighbors:

            if port != exclude_port:

                self.send(port, packet)
    
    
    def run_dijkstra(self):

        graph = {}

        for router, data in self.lsdb.items():

            if router not in graph:
                graph[router] = {}

            for neighbor, cost in data["links"].items():

                graph[router][neighbor] = cost

                if neighbor not in graph:
                    graph[neighbor] = {}

                graph[neighbor][router] = cost

        dist = {self.addr: 0}
        prev = {}

        pq = [(0, self.addr)]

        while pq:

            current_dist, node = heapq.heappop(pq)

            if current_dist > dist[node]:
                continue

            for neighbor, cost in graph.get(node, {}).items():

                new_dist = current_dist + cost

                if neighbor not in dist or new_dist < dist[neighbor]:

                    dist[neighbor] = new_dist
                    prev[neighbor] = node

                    heapq.heappush(pq, (new_dist, neighbor))

        self.forwarding_table = {}

        for destination in dist:

            if destination == self.addr:
                continue

            current = destination

            while prev.get(current) != self.addr:

                if current not in prev:
                    current = None
                    break

                current = prev[current]

            if current is None:
                continue

            next_hop = current

            for port, (neighbor, _) in self.neighbors.items():

                if neighbor == next_hop:

                    self.forwarding_table[destination] = port
                    break
                    
                
    def handle_packet(self, port, packet):

        if packet.is_traceroute:

            if packet.dst_addr == self.addr:
                return

            if packet.dst_addr in self.forwarding_table:

                out_port = self.forwarding_table[packet.dst_addr]

                self.send(out_port, packet)

        else:

            data = json.loads(packet.content)

            router = data["router"]
            seq = data["seq"]
            links = data["links"]

            if (router not in self.lsdb or
                    seq > self.lsdb[router]["seq"]):

                self.lsdb[router] = {
                    "seq": seq,
                    "links": links
                }

                self.run_dijkstra()

                self.flood_packet(packet, exclude_port=port)

    def handle_new_link(self, port, endpoint, cost):

        self.neighbors[port] = (endpoint, cost)

        # update own LSP
        self.lsdb[self.addr]["links"][endpoint] = cost

        self.seq_num += 1
        self.lsdb[self.addr]["seq"] = self.seq_num

        self.run_dijkstra()

        payload = self.create_lsp(self.addr)

        packet = Packet(
            Packet.ROUTING,
            self.addr,
            None,
            payload
        )

        self.flood_packet(packet)
    def handle_remove_link(self, port):

        if port not in self.neighbors:
            return

        endpoint, _ = self.neighbors[port]

        del self.neighbors[port]

        if endpoint in self.lsdb[self.addr]["links"]:

            del self.lsdb[self.addr]["links"][endpoint]

        self.seq_num += 1
        self.lsdb[self.addr]["seq"] = self.seq_num

        self.run_dijkstra()

        payload = self.create_lsp(self.addr)

        packet = Packet(
            Packet.ROUTING,
            self.addr,
            None,
            payload
        )

        self.flood_packet(packet)

    def handle_time(self, time_ms):

        if time_ms - self.last_time >= self.heartbeat_time:

            self.last_time = time_ms

            payload = self.create_lsp(self.addr)

            packet = Packet(
                Packet.ROUTING,
                self.addr,
                None,
                payload
            )

            self.flood_packet(packet)

    def __repr__(self):

        return f"LSrouter(addr={self.addr}, table={self.forwarding_table})"