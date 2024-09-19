import heapq


# defining the class for each node
class Node:
    def __init__(self):
        # parent node's column index
        self.parent_q = 0
        # parent node's row index
        self.parent_r = 0

        # actual step cost from start node to this node [g(n)]
        self.step_g = float("inf")
        # estimated step cost from this node to treasure node [h(n)]
        self.step_h = 0.0
        # function of total step cost of this node [f(n) = g(n) + h(n)]
        self.step_f = float("inf")

        # actual energy cost from start node to this node [g(n)]
        self.energy_g = float("inf")
        # estimated energy cost from this node to treasure node [h(n)]
        self.energy_h = 0.0
        # function of total energy cost of this node [f(n) = g(n) + h(n)]
        self.energy_f = float("inf")

        # total path cost taking into account both step and energy
        self.total_g = float("inf")
        self.total_h = 0.0
        self.total_f = float("inf")

        # set trap and reward effect
        self.t1_effect = 1.0
        self.t2_effect = 1.0
        self.r1_effect = 1.0
        self.r2_effect = 1.0

        # set nodes to move to
        # is current node by default
        # add movement if trigger trap 3
        self.movement_list = []


# check if node n is valid (within the boundaries of the map)
def is_valid(q, r, max_q, max_r):
    if (q >= 0) and (q < max_q) and (r >= 0) and (r < max_r):
        return True


# calc h for energy and steps
def calc_h(q, r, tsr):
    # euclidean distance
    energy_h = ((q - tsr[0]) ** 2 + (r - tsr[1]) ** 2) ** 0.5
    step_h = ((q - tsr[0]) ** 2 + (r - tsr[1]) ** 2) ** 0.5

    return energy_h, step_h


# check if node n is reward 1 or reward 2
def is_reward(q, r, map):
    if map[r][q] == "r1" or map[r][q] == "r2":
        return True


# check if node n is trap 1 or trap 2 or trap 3
def is_trap(q, r, map):
    if map[r][q] == "t1" or map[r][q] == "t2" or map[r][q] == "t3":
        return True


def handle_reward(new_q, new_r, q, r, map, nodes, r1_effect_new, r2_effect_new):
    # half energy cost if reward 1
    if map[new_r][new_q] == "r1":
        r1_effect_new = nodes[r][q].r1_effect * 0.5
    # half step cost if reward 2
    elif map[new_r][new_q] == "r2":
        r2_effect_new = nodes[r][q].r2_effect * 0.5

    return r1_effect_new, r2_effect_new


def handle_trap_1_2(new_q, new_r, q, r, map, nodes, t1_effect_new, t2_effect_new):
    # double energy cost if trap 1
    if map[new_r][new_q] == "t1":
        t1_effect_new = nodes[r][q].t1_effect * 2
    # double energy cost if trap 2
    elif map[new_r][new_q] == "t2":
        t2_effect_new = nodes[r][q].t2_effect * 2

    return t1_effect_new, t2_effect_new


# push player back 2 nodes if trap 3
def handle_trap_3(q, r, map, i, j, nodes):
    # empty movement_list to update
    nodes[r][q].movement_list = []

    if q % 2 == 0:
        # push player in the opposite direction [S, SW, NW, N, NE, SE]
        dir_push = [[(0, -1), (0, 1), (0, 1)], [(1, 0), (-1, 1), (-1, 0)],
                    [(1, 1), (-1, 0), (-1, -1)],
                    [(0, 1), (0, -1), (0, -1)], [(-1, 1), (1, 0), (1, -1)],
                    [(-1, 0), (1, 1), (1, 0)]]
    else:
        # push player in opposite direction [S, SW, NW, N, NE, SE]
        dir_push = [[(0, -1), (0, 1), (0, 1)], [(1, -1), (-1, 0), (-1, 1)],
                    [(1, 0), (-1, -1), (-1, 0)],
                    [(0, 1), (0, -1), (0, -1)], [(-1, 0), (1, -1), (1, 0)],
                    [(-1, -1), (1, 0), (1, 1)]]

    # make copy of q and r to keep track of original
    new_q = q
    new_r = r

    # move player one node at a time to check each node after singular movement
    for count in range(1, 3):
        for d in dir_push:
            if (i, j) == d[0]:
                temp_q = new_q + d[count][0]
                temp_r = new_r + d[count][1]
                # check if node is within map boundaries and not obstacle
                if is_valid(temp_q, temp_r, len(map[0]), len(map)) and not is_obstacle(temp_q, temp_r, map):
                    new_q = temp_q
                    new_r = temp_r
                    # insert valid node into movement list
                    nodes[r][q].movement_list.append((new_q, new_r))


# check if node n is obstacle
# trap 4 is considered an obstacle because it will end the game and cause the player to lose
def is_obstacle(q, r, map):
    if map[r][q] == "o" or map[r][q] == "t4":
        return True


# check if node n is treasure
def is_treasure(q, r, tsr):
    if q == tsr[0] and r == tsr[1]:
        return True


# to find the closest treasure node to prioritise
def prioritise_treasure(q, r, treasures):
    tsr_with_h = []
    tsr_h = []

    # calculate estimated distance h(n) to each treasure node
    for tsr in treasures:
        energy_h, step_h = calc_h(q, r, tsr)
        total_h = energy_h * step_h

        tsr_with_h.append([tsr, total_h])
        tsr_h.append(total_h)

    # return treasure with the lowest h(n)
    for [tsr, h] in tsr_with_h:
        if h == min(tsr_h):
            return tsr


# print the map and results
def print_map(map):
    print("     ", end="")
    for i in range(0, 5):
        print(" ____", end="     ")
    for r in map:
        if map.index(r) != 0:
            print("\n\\", end="")
        else:
            print("\n ", end="")
        for i in range(1, 10, 2):
            if r[i] == "t1" or r[i] == "t2" or r[i] == "r1" or r[i] == "r2" or r[i] == "t3" or r[i] == "t4":
                print("____/ " + r[i] + " \\", end="")
            else:
                print("____/  " + r[i] + " \\", end="")
        print("\n/", end="")

        for i in range(0, 10, 2):
            if r[i] == "t1" or r[i] == "t2" or r[i] == "r1" or r[i] == "r2" or r[i] == "t3" or r[i] == "t4":
                print(" " + r[i] + " \\____/", end="")
            else:
                print("  " + r[i] + " \\____/", end="")
    print()
    for i in range(0, 5):
        print("\\____/", end="    ")
    print()


# to draw the path taken to the treasure node at each iteration
def draw_path(nodes, tsr):
    path = []
    r = tsr[1]
    q = tsr[0]

    # draw path from treasure node to the start node
    while not (nodes[r][q].parent_r == r and nodes[r][q].parent_q == q):
        path.append((q, r))
        temp_r = nodes[r][q].parent_r
        temp_q = nodes[r][q].parent_q
        q = temp_q
        r = temp_r

    # add start node
    path.append((q, r))
    # reverse to draw path from start node to treasure node
    path.reverse()

    # print path
    for i in path:
        print("->", i, end=" ")
    print()

    return path


# update energy consumed
def update_energy(nodes, new_q, new_r, energy_g_new, energy_h_new, energy_f_new):
    nodes[new_r][new_q].energy_g = energy_g_new
    nodes[new_r][new_q].energy_h = energy_h_new
    nodes[new_r][new_q].energy_f = energy_f_new


# update steps used
def update_step(nodes, new_q, new_r, step_g_new, step_h_new, step_f_new):
    nodes[new_r][new_q].step_g = step_g_new
    nodes[new_r][new_q].step_h = step_h_new
    nodes[new_r][new_q].step_f = step_f_new


# update total path cost
def update_total(nodes, new_q, new_r, total_g_new, total_h_new, total_f_new):
    nodes[new_r][new_q].total_g = total_g_new
    nodes[new_r][new_q].total_h = total_h_new
    nodes[new_r][new_q].total_f = total_f_new


# update parent node
def update_parent(nodes, new_q, new_r, q, r):
    nodes[new_r][new_q].parent_q = q
    nodes[new_r][new_q].parent_r = r


# set trap and reward effect
def update_t_r_effect(nodes, new_q, new_r, r1_effect_new, r2_effect_new, t1_effect_new, t2_effect_new):
    nodes[new_r][new_q].r1_effect = r1_effect_new
    nodes[new_r][new_q].r2_effect = r2_effect_new
    nodes[new_r][new_q].t1_effect = t1_effect_new
    nodes[new_r][new_q].t2_effect = t2_effect_new


# update map and player status after each iteration
def status_update(result_path, map, nodes):
    # notify when trigger any trap or reward
    for (q, r) in result_path:
        if is_trap(q, r, map):
            if map[r][q] == "t1":
                print("Trap 1 triggered at node (" + str(q) + ", " + str(r) +
                      ")! Energy required per step is doubled! :c")
                print("Energy multiplier is now " + str(nodes[r][q].r1_effect) + ".")
            elif map[r][q] == "t2":
                print("Trap 2 triggered at node (" + str(q) + ", " + str(r) +
                      ")! Step required per movement is doubled! :c")
                print("Step multiplier is now " + str(nodes[r][q].r1_effect) + ".")
            elif map[r][q] == "t3":
                print("Trap 3 triggered at node (" + str(q) + ", " + str(r) +
                      ")! Pushed back two nodes. :c")

        if is_reward(q, r, map):
            if map[r][q] == "r1":
                print("Reward 1 obtained at node (" + str(q) + ", " + str(r) +
                      ")! Energy required per step is halved! :D")
                print("Energy multiplier is now " + str(nodes[r][q].r1_effect) + ".")
            elif map[r][q] == "r2":
                print("Reward 2 obtained at node (" + str(q) + ", " + str(r) +
                      ")! Step required per movement is halved! :D")
                print("Step multiplier is now " + str(nodes[r][q].r1_effect) + ".")

        # edit map based on path
        if (q, r) == result_path[-1]:
            map[r][q] = "p"
        else:
            map[r][q] = "x"


# A* search to find the treasure nodes
def a_star_search(start, closest_tsr, map, t1_effect, t2_effect, r1_effect, r2_effect):
    max_r = len(map)
    max_q = len(map[0])

    # initialize closed list (nodes visited)
    closed_list = [[False for _ in range(max_q)] for _ in range(max_r)]

    # initialize each node
    nodes = [[Node() for _ in range(max_q)] for _ in range(max_r)]

    # initialize start node
    q = start[0]
    r = start[1]
    # set energy consumed
    nodes[r][q].energy_f = 0.0
    nodes[r][q].energy_g = 0.0
    nodes[r][q].energy_h = 0.0
    # step steps used
    nodes[r][q].step_f = 0.0
    nodes[r][q].step_g = 0.0
    nodes[r][q].step_h = 0.0
    # set total path cost
    nodes[r][q].total_g = 0.0
    nodes[r][q].total_h = 0.0
    nodes[r][q].total_f = 0.0
    # set trap and reward effect
    nodes[r][q].r1_effect = r1_effect
    nodes[r][q].r2_effect = r2_effect
    nodes[r][q].t1_effect = t1_effect
    nodes[r][q].t2_effect = t2_effect
    # set parent node
    nodes[r][q].parent_q = q
    nodes[r][q].parent_r = r
    # set movement_list
    nodes[r][q].movement_list = [(0, 0)]

    # initialize open list (nodes to visit)
    open_list = []

    # insert start node
    # using priority queue to rank f(n)
    heapq.heappush(open_list, (0.0, q, r))

    # loop algorithm while there are still unexplored nodes
    while len(open_list) > 0:
        # pop the node with the smallest f value (lowest priority in heap)
        n = heapq.heappop(open_list)

        # mark node as visited
        q = n[1]
        r = n[2]
        closed_list[r][q] = True

        # check neighbours in all directions [N, NE, SE, S, SW, NW]
        # determine directional movements based on q
        if q % 2 == 0:
            directions = [(0, -1), (1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0)]
        else:
            directions = [(0, -1), (1, -1), (1, 0), (0, 1), (-1, 0), (-1, -1)]

        for (i, j) in directions:
            new_q = q + i
            new_r = r + j

            # check if node is within map boundaries and not obstacle
            if (is_valid(new_q, new_r, max_q, max_r) and not is_obstacle(new_q, new_r, map)
                    and not closed_list[new_r][new_q]):
                # if node is valid add to movement
                nodes[new_r][new_q].movement_list = [(new_q, new_r)]

                # default update of reward and trap effects
                r1_effect_new = nodes[r][q].r1_effect
                r2_effect_new = nodes[r][q].r2_effect
                t1_effect_new = nodes[r][q].t1_effect
                t2_effect_new = nodes[r][q].t2_effect

                # check if the node is a reward node and handle them
                if is_reward(new_q, new_r, map):
                    r1_effect_new, r2_effect_new = handle_reward(new_q, new_r, q, r, map, nodes,
                                                                 r1_effect_new, r2_effect_new)

                # check if the node is a trap node and handle them
                if is_trap(new_q, new_r, map):
                    t1_effect_new, t2_effect_new = handle_trap_1_2(new_q, new_r, q, r, map, nodes,
                                                                   t1_effect_new, t2_effect_new)
                if map[new_r][new_q] == "t3":
                    handle_trap_3(new_q, new_r, map, i, j, nodes)

                # loop for each node in movement
                # ensures cost for trap 3 is taken into account
                for (new_q, new_r) in nodes[new_r][new_q].movement_list:
                    # calculate new f, h and h
                    # actual cost [g(n)] is calculated with the current g[n] + the new energy cost//step cost
                    # energy cost and step cost are 1.0 unless affected by trap or reward effects
                    energy_g_new, step_g_new = (nodes[r][q].energy_g + 1 * nodes[r][q].t1_effect * nodes[r][q].r1_effect,
                                                nodes[r][q].step_g + 1 * nodes[r][q].t2_effect * nodes[r][q].r2_effect)

                    # estimated cost [h(n)] is calculated with the Euclidean distance from the player location to the
                    # treasure node
                    energy_h_new, step_h_new = calc_h(new_q, new_r, closest_tsr)
                    # include any trap or reward affect that may affect the path
                    energy_h_new = energy_h_new * r1_effect_new * t1_effect_new
                    step_h_new = step_h_new * r2_effect_new * t2_effect_new

                    # total cost [f(n)] for energy and step will be h(n) + g(n)
                    energy_f_new, step_f_new = energy_g_new + energy_h_new, step_g_new + step_h_new

                    # the following are the main h(n), g(n) and f(n) that will be used for decision-making
                    # using the product of both energy and step to get the cost
                    total_g_new = energy_g_new + step_g_new
                    total_h_new = energy_h_new + step_h_new

                    # f(n) = h(n) + g(n)
                    total_f_new = total_g_new + total_h_new

                    # check if current node is treasure node
                    if is_treasure(new_q, new_r, closest_tsr):
                        # set parent for treasure node
                        nodes[new_r][new_q].parent_r = r
                        nodes[new_r][new_q].parent_q = q

                        print("Treasure found!")

                        # save resulting path
                        result_path = (draw_path(nodes, closest_tsr))

                        # notify when trigger any trap or reward
                        status_update(result_path, map, nodes)

                        # print to show player location and path after each iteration
                        print_map(map)

                        # record energy consumption and number of steps taken
                        energy_consumed = energy_f_new
                        steps_taken = step_f_new

                        # print amount of energy consumed and steps taken on each iteration
                        print("Energy consumed:", energy_consumed)
                        print("Steps taken:", steps_taken)
                        print("Path cost:", energy_consumed + steps_taken)

                        # return the resulting path, amount of energy consumed, number of steps taken, new player
                        # position and reward and trap effects to be carried onto the next iteration
                        return (result_path, energy_consumed, steps_taken, (new_q, new_r), t1_effect_new, t2_effect_new,
                                r1_effect_new, r2_effect_new)

                    # check if node has been explored
                    elif nodes[new_r][new_q].total_f == float("inf") or nodes[new_r][new_q].total_f > total_f_new:
                        # add node to open list
                        heapq.heappush(open_list, (total_f_new, new_q, new_r))
                        # update node info
                        update_energy(nodes, new_q, new_r, energy_g_new, energy_h_new, energy_f_new)
                        update_step(nodes, new_q, new_r, step_g_new, step_h_new, step_f_new)
                        update_total(nodes, new_q, new_r, total_g_new, total_h_new, total_f_new)
                        update_parent(nodes, new_q, new_r, q, r)
                        update_t_r_effect(nodes, new_q, new_r, r1_effect_new, r2_effect_new, t1_effect_new,
                                          t2_effect_new)


def main():
    # define the map
    # alphanumeric characters to represent nodes with reward, trap, treasure and obstacle
    # p - represent player location
    # g - represent treasure nodes
    # o - represent obstacle nodes
    # r1, r2 - represent reward nodes
    # t1, t2, t3, t4 - represent trap nodes
    # " " - represent empty nodes
    map = [
        ["p", " ", " ", " ", "r1", " ", " ", " ", " ", " "],
        [" ", "t2", " ", "t4", "g", " ", "t3", " ", "o", " "],
        [" ", " ", "o", " ", "o", " ", " ", "r2", "t1", " "],
        ["o", "r1", " ", "o", " ", "t3", "o", "g", " ", "g"],
        [" ", " ", "t2", "g", "o", " ", "o", "o", " ", " "],
        [" ", " ", " ", " ", " ", "r2", " ", " ", " ", " "]
    ]

    # make copy of map without reference
    i_map = [
        ["p", " ", " ", " ", "r1", " ", " ", " ", " ", " "],
        [" ", "t2", " ", "t4", "g", " ", "t3", " ", "o", " "],
        [" ", " ", "o", " ", "o", " ", " ", "r2", "t1", " "],
        ["o", "r1", " ", "o", " ", "t3", "o", "g", " ", "g"],
        [" ", " ", "t2", "g", "o", " ", "o", "o", " ", " "],
        [" ", " ", " ", " ", " ", "r2", " ", " ", " ", " "]
    ]

    # print map before algorithm is run
    print_map(map)
    print()

    # define start node [q, r]
    start = (0, 0)

    # define list of treasure nodes [q, r]
    treasures = [(3, 4), (4, 1), (7, 3), (9, 3)]

    # to store the total energy consumption and steps taken
    total_e = 0
    total_s = 0

    # to store the final path
    final_path = []

    # prioritise the closest treasure [lowest h(tsr)]
    closest_tsr = prioritise_treasure(0.0, 0.0, treasures)
    t1_effect, t2_effect, r1_effect, r2_effect = 1.0, 1.0, 1.0, 1.0

    # loop to find all treasure nodes
    while len(treasures) > 0:
        # A* search
        result_path, e, s, start, t1_effect, t2_effect, r1_effect, r2_effect \
            = a_star_search(start, closest_tsr, map, t1_effect, t2_effect, r1_effect, r2_effect)
        final_path.append(result_path)

        # total up total energy and steps used
        total_e += e
        total_s += s

        print()
        # remove treasure from treasure list after found
        treasures.remove(closest_tsr)
        # find the next closest treasure
        closest_tsr = prioritise_treasure(start[0], start[1], treasures)
    print("All treasures obtained. Algorithm terminated.\n")

    # print results
    # print initial map
    print("Initial map:")
    print_map(i_map)
    print()

    # print path on map
    print("Final map:")
    print_map(map)

    print("Final path:")
    # draw the final path
    for i in final_path:
        for n in i:
            if not (i.index(n) == 0 and final_path.index(i) != 0):
                print("->", n, end=" ")
    print()

    print("Total energy consumed:", total_e)
    print("Total steps taken:", total_s)
    print("Total path cost:", total_e + total_s)


main()
