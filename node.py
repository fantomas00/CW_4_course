import random

costs = [1, 2, 4, 5, 6, 7, 8, 10, 15, 21]


class Node(object):

    def __init__(self, shape, text, new_id, x, y, station=False):
        self.id = new_id
        self.__channels = []
        self.__connected_nodes = {}
        self.__distance_table = [[self.id, 0]]
        self.__graph = {self.id: self.__connected_nodes}
        self.enabled = True
        self.station = station

        self.x = x
        self.y = y
        self.shape = shape
        self.text = text

    def get_channels(self):
        return self.__channels

    def get_connected_nodes(self):
        return self.__connected_nodes

    def get_connection(self, node):
        for i in self.__channels:
            if i.node2.id == node.id or i.node1.id == node.id:
                return i
        return False

    def get_distance_table(self):
        return self.__distance_table

    def get_graph(self):
        return self.__graph

    def add_channel(self, channel):
        self.__channels.append(channel)

    def remove_channel(self, node):
        for i in self.__channels:
            if i.node2.id == node.id or i.node1.id == node.id:
                self.__channels.remove(i)
                return True
        print("Disconnect Error: Node {} has no channel to {}!".format(node.id, self.id))
        return False

    def connect(self, node, c_type, channel=None, satellite=False, random_gen=False):
        if node.id in self.__connected_nodes:
            print("Connect Error: {} already connected to {}!".format(node.id, self.id))
            return False
        err_prob = round(random.uniform(0.0, 0.3), 3)
        if random_gen:
            cost = random.randint(1, 50)
        else:
            cost = random.choice(costs)
        if not channel:
            self.add_channel(Channel(self.id, node.id, c_type, cost, err_prob, satellite))
            node.add_channel(Channel(node.id, self.id, c_type, cost, err_prob, satellite))
        else:
            channel.cost = cost
            channel.err_prob = err_prob
            channel.satellite = satellite
            self.add_channel(channel)
            node.add_channel(channel)
        self.__connected_nodes[node.id] = node
        node.__connected_nodes[self.id] = self
        if node.id not in (x[0] for x in self.__distance_table):
            print(self.__distance_table)
            self.__distance_table.append([node.id, float("inf")])
            node.__distance_table.append([self.id, float("inf")])
        if node.id not in self.__graph:
            self.__graph[node.id] = node.__connected_nodes
            node.__graph[self.id] = self.__connected_nodes
        self.announce([self])
        node.announce([node])
        print("Created connection between {} and {}, cost: {}".format(self.id, node.id, cost))

    def disconnect(self, node):
        if node.id in self.__connected_nodes:
            self.remove_channel(node)
            node.remove_channel(self)
            del self.__connected_nodes[node.id]
            del node.__connected_nodes[self.id]
            self.announce([self])
            node.announce([node])
            print("Disconnected {} and {}".format(self.id, node.id))
            return True
        print("Disconnect Error: {} is not connected to {}!".format(node.id, self.id))
        return False

    def announce(self, src):
        """recursive announcement of a node's connections to its neighbors"""
        for node_key in self.__connected_nodes:
            if node_key in (x.id for x in src):
                continue
            c_node = self.__connected_nodes[node_key]
            if not c_node.enabled:
                continue
            if not self.get_connection(c_node):
                continue
            elif not self.get_connection(c_node).enabled:
                continue
            print(c_node.id, c_node.__distance_table)
            c_node.__distance_table.extend([x[0], float("inf")] for x in self.__distance_table
                                           if x[0] not in (node[0] for node in c_node.__distance_table))
            c_node.__graph.update(self.__graph)
            src.append(c_node)
            c_node.announce(src)

    def dijkstra(self):
        """use the dijkstra algorithm to determine travel distances for all nodes in the network"""
        order = len(self.__graph)
        dist = [float("inf")] * order
        dist[self.id] = 0
        visited = [False] * order
        for _ in range(order):
            u = -1
            for i in range(order):
                if not visited[i] and (u == -1 or dist[i] < dist[u]):
                    u = i
            if dist[u] == -1:
                break
            visited[u] = True
            for node_id, node in self.__graph[u].items():
                if not node.enabled:
                    continue
                channel = node.get_connection(node.get_connected_nodes()[u])
                if not channel.enabled:
                    continue
                if dist[u] + channel.cost < dist[node_id]:
                    dist[node_id] = dist[u] + channel.cost
        self.__distance_table.sort(key=lambda x: x[0])
        for i in range(order):
            self.__distance_table[i][1] = dist[i]
        self.__distance_table = list((x for x in self.__distance_table if x[1] != float("inf")))

    def remove(self):
        for node in list(self.__connected_nodes.values()):
            self.disconnect(node)
        self.__graph.clear()
        self.__distance_table.clear()


    def send_message(self, type, msg_size, pkt_size, dest):
        pkt_list = []
        if type == "datagram":
            header_size = 40
        elif type == "virtual":
            header_size = 5
        else:
            header_size = 0
        for i in range(msg_size // pkt_size):
            pkt_list.append(Packet(pkt_size + header_size, i))
        if msg_size % pkt_size:
            pkt_list.append(Packet(msg_size % pkt_size + header_size, len(pkt_list)))
        for packet in pkt_list:
            print(packet.number, packet.size)


class Channel(object):
    def __init__(self, n_node1, n_node2, c_type, cost, err_prob, satellite):
        self.node1 = n_node1
        self.node2 = n_node2
        self.cost = cost
        self.c_type = c_type
        self.err_prob = err_prob
        self.satellite = satellite
        self.enabled = True

    def get_channel_info(self):
        return [self.node1, self.node2, self.cost, self.c_type, self.err_prob]


class Packet:
    def __init__(self, size, number):
        self.size = size
        self.number = number
        self.error = False
        self.cost_expended = 0

if __name__ == "__main__":
    node1 = Node("","", 0, 0, 0)
    node1.send_message("datagram", 50, 10, 10)