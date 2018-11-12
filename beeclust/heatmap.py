import numpy as np
import collections

from beeclust.constants import Constant


class Vertex(collections.namedtuple("Vertex", ["x", "y", "steps"])):
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y
    def __hash__(self):
        return hash(f'{self.x}:{self.y}')

class HeatMap:

    def __init__(self, map, T_heater, T_cooler, T_env, k_temp):
        self.map = map
        self.T_heater = T_heater
        self.T_cooler = T_cooler
        self.T_env = T_env
        self.k_temp = k_temp

        self.calculate_heatmap()


    def __getitem__(self, key_tuple):
        return self.heatmap[key_tuple]

    def calculate_heatmap(self):

        heatmap = np.zeros(self.map.shape)

        for x in range(self.map.shape[0]):
            for y in range(self.map.shape[1]):

                map_value = self.map[x, y]

                if map_value == Constant.HEATER:
                    heatmap[x,y] = self.T_heater
                elif map_value == Constant.COOLER:
                    heatmap[x, y] = self.T_cooler
                elif map_value == Constant.WALL:
                    heatmap[x, y] = np.nan
                else:

                    dist_heater, dist_cooler = self.closest_device(x, y)

                    heating = (1 / dist_heater) * (self.T_heater - self.T_env)
                    cooling = (1 / dist_cooler) * (self.T_env - self.T_cooler)

                    print(self.T_env + self.k_temp * (max(heating, 0) - max(cooling, 0)))

                    heatmap[x, y] = self.T_env + self.k_temp * (max(heating, 0) - max(cooling, 0))

        self.heatmap = heatmap

        return heatmap


    def closest_device(self, start_x, start_y):
        """"
        Perfrom BFS on map to find min steps to closest heater/cooler
        """

        dist_cooler = np.inf
        dist_heater = np.inf

        visited, queue = set(), [Vertex(x=start_x, y=start_y, steps=0)]

        while len(queue) > 0:

            vertex = queue.pop(0)

            if vertex not in visited:

                visited.add(vertex)

                if self.map[vertex.x, vertex.y] == Constant.HEATER and vertex.steps < dist_heater:
                    dist_heater = vertex.steps
                elif self.map[vertex.x, vertex.y] == Constant.COOLER and vertex.steps < dist_cooler:
                    dist_cooler = vertex.steps
                elif self.map[vertex.x, vertex.y] == Constant.WALL:
                    continue

                adj_vertecies = self.adjacent_cells(vertex.x, vertex.y)

                for adj_vertex in adj_vertecies:
                    queue.append(Vertex(x=adj_vertex [0], y=adj_vertex[1], steps=vertex.steps + 1))

        return dist_heater, dist_cooler


    def adjacent_cells(self, x, y):

        cells = [(x, y + 1), (x + 1, y), (x, y - 1), (x - 1, y),
                 (x + 1, y + 1), (x - 1, y - 1), (x - 1, y + 1), (x + 1, y - 1)]

        max_x = self.map.shape[0]
        max_y = self.map.shape[1]

        my_cells = []
        for cell in cells:
            if cell[0] < max_x and cell[1] < max_y and cell[0] >= 0 and cell[1] >= 0:
                my_cells.append(cell)

        return my_cells


if __name__ == "__main__":

    print("TEST")

