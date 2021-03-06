import numpy as np

from beeclust.heatmap import HeatMap
from beeclust.constants import Constant

class BeeClust:

    def __init__(self, map, p_changedir=0.2, p_wall=0.8, p_meet=0.8, k_temp=0.9,
                 k_stay=50, T_ideal=35, T_heater=40, T_cooler=5, T_env=22, min_wait=2):

        if not isinstance(map, np.ndarray):
            raise TypeError('ERROR map')
        if map.ndim != 2:
            raise ValueError('Value Error, map should be 2dim!')
        self.map = map

        if not (isinstance(p_changedir, float) or isinstance(p_changedir, int)):
            raise TypeError('ERROR p_changedir')
        if not (0. <= p_changedir <= 1.):
            raise ValueError('Value Error, probability p_changedir cannot be negative or grater than 1.')
        self.p_changedir = p_changedir

        if not (isinstance(p_wall, float) or isinstance(p_wall, int)):
            raise TypeError('ERROR p_wall')
        if not (0. <= p_wall <= 1.):
            raise ValueError('Value Error, probability p_wall cannot be negative or grater than 1.')
        self.p_wall = p_wall

        if not (isinstance(p_meet, float) or isinstance(p_meet, int)):
            raise TypeError('ERROR p_meet')
        if not (0. <= p_meet <= 1.):
            raise ValueError('Value Error, probability p_meet cannot be negative or grater than 1.')
        self.p_meet = p_meet

        if not (isinstance(k_temp, float) or isinstance(k_temp, int)):
            raise TypeError('ERROR k_temp')
        if not (0 < k_temp):
            raise ValueError('Value Error, coef cannot be negative.')
        self.k_temp = k_temp

        if not (isinstance(k_stay, float) or isinstance(k_stay, int)):
            raise TypeError('ERROR k_stay')
        if not (0 < k_stay):
            raise ValueError('Value Error, coef cannot be negative.')
        self.k_stay = k_stay

        if not (isinstance(T_ideal, float) or isinstance(T_ideal, int)):
            raise TypeError('ERROR T_ideal')
        self.T_ideal = T_ideal

        if not (isinstance(T_heater, float) or isinstance(T_heater, int)):
            raise TypeError('ERROR T_heater')
        self.T_heater = T_heater

        if not (isinstance(T_cooler, float) or isinstance(T_cooler, int)):
            raise TypeError('ERROR T_cooler')
        self.T_cooler = T_cooler

        if not (isinstance(T_env, float) or isinstance(T_env, int)):
            raise TypeError('ERROR T_env')
        self.T_env = T_env

        if not (isinstance(min_wait, float) or isinstance(min_wait, int)):
            raise TypeError('ERROR min_wait')
        if min_wait < 0:
            raise ValueError('Value Error, min_wait cannot be negative!')
        self.min_wait = min_wait


        if (T_heater < T_cooler):
            raise ValueError('Value Error, T_heater is not colder than cooler')
        if (T_heater < T_env):
            raise ValueError('Value Error, T_env cannot be colder than heater')
        if (T_cooler > T_env):
            raise ValueError('Value Error, T_cooler cannot be colder than cooler')


        self.heatmap_obj = HeatMap(map, T_heater, T_cooler, T_env, k_temp)

    @property
    def heatmap(self):
        return self.heatmap_obj.heatmap

    @property
    def bees(self):
        bees = []
        for x in range(self.map.shape[0]):
            for y in range(self.map.shape[1]):
                if Constant.BEE_UP <= self.map[x, y] <= Constant.BEE_LEFT or self.map[x, y] < 0:
                    bees.append((x, y))
        return bees


    @property
    def swarms(self):

        swarms = []
        bees = self.bees
        visited, queue = set(), []

        for bee in bees:
            if not bee in visited:
                queue.append(bee)
                cluster = []
                while len(queue) > 0:
                    cur_bee = queue.pop()
                    if cur_bee not in cluster:

                        visited.add(cur_bee)
                        cluster.append(cur_bee)

                        for adj_bee in self.adjacent_bees(cur_bee[0], cur_bee[1], bees):
                            queue.append(adj_bee)

                swarms.append(cluster)

        return swarms

    @property
    def score(self):

        sum_temp = 0
        bees = self.bees

        if len(bees) == 0:
            return 0.0

        for bee in bees:
            sum_temp += self.heatmap[bee[0], bee[1]]

        return sum_temp/len(bees)


    def tick(self):

        bees = self.bees

        moved = 0

        for bee in bees:
            x, y = bee[0], bee[1]
            map_value = self.map[x, y]

            if np.random.rand() < self.p_changedir or map_value == -1:
                moves = [Constant.BEE_UP, Constant.BEE_DOWN, Constant.BEE_LEFT, Constant.BEE_RIGHT]
                if map_value in moves:
                    moves.remove(map_value)
                bee_direction = np.random.choice(moves)
                self.map[x, y] = bee_direction
                if map_value == -1:
                    continue
                map_value = bee_direction

            if map_value == Constant.BEE_UP:
                moved += self.move_bee(bee=bee, to_x=bee[0] - 1, to_y=bee[1])
            elif map_value == Constant.BEE_DOWN:
                moved += self.move_bee(bee=bee, to_x=bee[0] + 1, to_y=bee[1])
            elif map_value == Constant.BEE_RIGHT:
                moved += self.move_bee(bee=bee, to_x=bee[0], to_y=bee[1] + 1)
            elif map_value == Constant.BEE_LEFT:
                moved += self.move_bee(bee=bee, to_x=bee[0], to_y=bee[1] - 1)
            elif map_value < -1:
                self.map[x,y] += 1

        return moved

    def forget(self):
        bees = self.bees
        for bee in bees:
            self.map[bee[0], bee[1]] = -1


    def recalculate_heat(self):
        return self.heatmap_obj.calculate_heatmap()


    def adjacent_bees(self, x, y, bees):
        adj_bees = []

        if (x + 1, y) in bees:
            adj_bees.append((x+1, y))
        if (x - 1, y) in bees:
            adj_bees.append((x-1, y))
        if (x, y + 1) in bees:
            adj_bees.append((x, y+1))
        if (x, y - 1) in bees:
            adj_bees.append((x, y-1))

        return adj_bees


    def move_bee(self, bee, to_x, to_y):

        x, y = bee[0], bee[1]
        new_x, new_y = to_x, to_y

        is_moving = False

        if new_x < 0 or new_x >= self.map.shape[0] or new_y < 0 or new_y >= self.map.shape[1] or self.map[new_x, new_y] in [Constant.WALL, Constant.COOLER, Constant.HEATER]:
            self.hit_obstacle(bee)
        elif self.map[new_x, new_y] < 0 or Constant.BEE_UP <= self.map[new_x, new_y] <= Constant.BEE_LEFT:
            self.hit_bee(bee)
        else:
            is_moving = True
            self.map[new_x, new_y] = self.map[x, y]
            self.map[x, y] = Constant.EMPTY

        return is_moving


    def hit_obstacle(self, bee):
        if np.random.rand() < self.p_wall:
            self.map[bee[0], bee[1]] = self.wait(bee)
        else:
            if self.map[bee[0], bee[1]] == Constant.BEE_RIGHT:

                self.map[bee[0], bee[1]] = Constant.BEE_LEFT

            elif self.map[bee[0], bee[1]] == Constant.BEE_LEFT:

                self.map[bee[0], bee[1]] = Constant.BEE_RIGHT

            elif self.map[bee[0], bee[1]] == Constant.BEE_UP:

                self.map[bee[0], bee[1]] = Constant.BEE_DOWN

            elif self.map[bee[0], bee[1]] == Constant.BEE_DOWN:

                self.map[bee[0], bee[1]] = Constant.BEE_UP

    def hit_bee(self, bee):
        if np.random.rand() < self.p_meet:
            self.map[bee[0], bee[1]] = self.wait(bee)

    def wait(self, bee):
        T_local = self.heatmap[bee[0], bee[1]]

        return max(int(self.k_stay / (1 + abs(self.T_ideal - T_local))), self.min_wait)*(-1)
