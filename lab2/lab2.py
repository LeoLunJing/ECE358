import argparse
import random
import math
import heapq


####################################################
############### Parameter Constants ################
# # N: The number of nodes/computers connected to the LAN (variable).
# N = 4
# # A: Average packet arrival rate (packets/second) (variable). Data packets arrive at the MAC layer following a Poisson process at ˜all nodes
# A = 5
# R: The speed of the LAN/channel/bus (fixed)
R = 1000000
# L: Packet length (fixed)
L = 1500
# D: Distance between adjacent nodes on the bus/channel
D = 10
# S: Propagation speed
S = 2 * 10**8
# T: Simulation time
T = 1000
# T_prop: The propagation delay between two neighboring nodes due to fixed propagation speed and distance (0.00000005)
T_prop = float(D) / S
# T_trans: The transmission delay for one packet due to fixed packet size and channal speed (0.0015)
T_trans = float(L) / R
# persistent_simulation: Indicates whether to simulate persistent or non-persistent CSMA/SD
persistent_simulation = True

########## Global Counters for Analysis ############

# c_tx_attempts: The counter for transmitted packets
c_tx_attempts = 0
# c_tx_success: number of packets that are transmitted successfully
c_tx_success = 0
# c_drop: the number of packets that been dropped
c_drop = 0

####################################################

# Node class
class Node:
    c_collision = 0
    packets_queue = list()

    def __init__(self):
        self.t_pre_arrival = 0

    def Drop(self):
        self.packets_queue.pop(0)
        self.c_collision = 0



# Packet class
class Packet:
    t_trans_delay = T_trans # transmission delay

    def __init__(self, node, t_arrival):
        self.t_arrival = t_arrival 
        self.node = node
        self.t_trans = t_arrival # the actual transmission start time
        self.c_collision = 0
        self.t_remove = 0
        self.c_channel_busy = 0

    def transmit(self):
        return 0


def generate_random(lambda_para):
    return - (1 / lambda_para) * math.log(1 - random.uniform(0, 1))


def allNodesEmpty(node_head):
    empty = True
    for i in range(N):
        empty = empty and node_head[i] is None
    return empty


def findNextPacket(node_head):
    trans_time = 2*T    # set to maximum
    for i in range(N):
        if node_head[i] is not None:
            if trans_time >= node_head[i].t_trans:
                trans_time = node_head[i].t_trans
                next_node = i


    return next_node, trans_time


def getPropagationDelay(src, des):
    return abs(des-src) * T_prop


def getNextPacket(node_head, i, previous_pkt_done):
    # Generate the next packet that arriving the node
    previous_pkt = node_head[i]
    next_pkt_arrival = previous_pkt.t_arrival + generate_random(A)
    next_pkt = Packet(i, next_pkt_arrival)

    # Check T exceed
    if next_pkt_arrival > T:
        return None
    else:
        # Check the arrival time with the transmit finish time
        if next_pkt_arrival < previous_pkt_done:
            next_pkt.t_trans = previous_pkt_done

    return next_pkt


def calcExpBackoff(index):
    rand = random.uniform(0, (2 ** index) - 1)
    # Tp = 512 bit-time wait (512 / R)
    return (rand * 512 / R)


def simulate():
    global c_tx_attempts
    global c_tx_success    

    c_tx_success = 0
    c_tx_attempts = 0

    node_head = [None,] * N
    end_time = 0
#    prev_end_time = 0

    for i in range(N):
        node_head[i] = Packet(i, generate_random(A))

    while(not allNodesEmpty(node_head)):
        # Find the earliest node_head

        # for i in range(N):
        #     print("Node " + str(i) + " start tx at " + str(node_head[i].t_trans))

        trans_node, trans_start_at_src = findNextPacket(node_head)
        # Transmit the targeted head packet
        trans_packet = node_head[trans_node]
        trans_end_at_src = trans_start_at_src + trans_packet.t_trans_delay
        c_tx_attempts+=1
        node_head[trans_node].c_channel_busy += 1

        # print(str(c_tx_success) + " / " + str(c_tx_attempts)  )

        # Flag to check if collision occur
        f_collision = False
        collision_nodes = []
        t_collision_detected = -1

        # print("Txing node index: " + str(trans_node) + ", start: " + str(trans_start_at_src) + ", end: " + str(trans_end_at_src))

        # Check possible collisions for each node
        for i in range(N):
            if i != trans_node and node_head[i] is not None:
                # Here is the time for each node to check the bus is busy or collision happen.
                # For 1-persistent, it keep checking the bus, as long as no collision, its t_trans will not be updated.

                # Bus busy or node idle through entire transmission
                if node_head[i].t_trans > trans_start_at_src + getPropagationDelay(trans_node, i):

                    # Bus busy
                    if node_head[i].t_trans < trans_end_at_src + getPropagationDelay(trans_node, i):
                        node_head[i].t_trans = trans_end_at_src + getPropagationDelay(trans_node, i)

                        if not persistent_simulation:
                            node_head[i].c_channel_busy += 1
                            if node_head[i].c_channel_busy <= 10:
                                node_head[i].t_trans += calcExpBackoff(node_head[i].c_channel_busy)
                            else:
                                node_head[i] = getNextPacket(node_head, i, trans_start_at_src + getPropagationDelay(trans_node, i))

                # Collision
                else:
                    f_collision = True
                    collision_nodes.append(i)
                    c_tx_attempts+=1
                    node_head[i].c_channel_busy += 1
                    # print(str(c_tx_success) + " / " + str(c_tx_attempts)  )
                    if t_collision_detected == -1 or t_collision_detected > (node_head[i].t_trans + getPropagationDelay(i, trans_node)):
                        t_collision_detected = node_head[i].t_trans + getPropagationDelay(i, trans_node)
        
        # If a collision has occurred
        if f_collision == True:
            collision_nodes.append(trans_node)
            for i in collision_nodes:
            # update the wait time
                node_head[i].c_collision += 1
                if node_head[i].c_collision <= 10:
                    # Assuming all collision detections are relative to collision detected by
                    # transmitting node, + propagation delay from transmitting node to colliding nodes
                    node_head[i].t_trans = t_collision_detected + getPropagationDelay(i, trans_node) + calcExpBackoff(node_head[i].c_collision)

                else:
                    # Drop packet, move next packet to node head 
                    node_head[i] = getNextPacket(node_head, i, t_collision_detected + getPropagationDelay(i, trans_node))                                                                                                                        
        else:
            # if node_head[trans_node].c_collision == 0:
            c_tx_success += 1
            node_head[trans_node] = getNextPacket(node_head, trans_node, trans_end_at_src)
            end_time = trans_end_at_src
#            difference = end_time - prev_end_time
#            if difference < T_trans:
#                print('X: ' + str(end_time - prev_end_time))
#            else:
#                print('-: ' + str(end_time - prev_end_time))
#            prev_end_time = end_time
            # print(str(c_tx_success) + " / " + str(c_tx_attempts)  )

#    print('End time: ' + str(end_time) + ', c_tx_success: ' + str(c_tx_success))
    efficiency = c_tx_success / c_tx_attempts
    throughput = float(c_tx_success * L) / (1000000.0 * end_time)
    print(str(N) + ',' + str(efficiency) + ',' + str(throughput))

def main():
    global N
    global A
    global T
    global persistent_simulation

    parser = argparse.ArgumentParser(description='Simulate CSMA/CD of nodes (ECE358 Lab 2)')
    # parser.add_argument('-N', '--num_nodes', metavar='n', type=int, default=20,
    #                     help='Number of nodes in the simulation transmitting packets')
    parser.add_argument('-A', '--arrival_rate', metavar='a', type=float, default=5.0,
                        help='Average packet arrival rate [packets/second]')
    parser.add_argument('-T', '--time', metavar='t', type=int, default=1000,
                        help='Time of the simulation')    
    parser.add_argument('-P', '--non_persistent', action='store_true',
                        help='Non-persistent CSMA/CD simulation (default: persistent)')

    args = parser.parse_args()
    # N = args.num_nodes
    A = args.arrival_rate
    T = args.time    
    persistent_simulation = not args.non_persistent

    print('# Nodes (N),Efficiency,Throughput [Mbps]')
    for n in range(20, 120, 20):
        N = n
        # print(str("start N = ") + str(n))
        simulate()       

#    N=1
#    simulate()

# END MAIN

if __name__ == '__main__':
   main()
