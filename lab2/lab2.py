##########################################################################
# Persistent/Non-Persistent CSMA/CD Simulation
# ECE 358 Lab 2 (Winter 2019)
# Authors: Lun Jing, Victor Yan
#
# Simulation of N nodes transmitting packets of equal length L with packets
# arriving at a rate of A, with transmission rate R and propagation speed S,
# and equi-distant adjacent nodes of distance D. Output data includes
# efficiency and throughput.
##########################################################################

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

# Packet class
# Class encapsulating all data regarding an individual packet, including
# the node it belongs to. All "node" data is contained within the head
# packets instead (e.g. collision/channel busy counters).
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

# Generate value from a random distribution
# Generate a random value from the Poisson distribution given parameter
# lambda (typically the arrival rate of the simulation).
# @param lambda_para - float:   Parameter for the random distribution.
# @return float:                Random value following the distribution.
def generate_random(lambda_para):
    return - (1 / lambda_para) * math.log(1 - random.uniform(0, 1))

# Check if all nodes are empty
# Check if all nodes have no more packets to transmit.
# @param node_head - list[Packet]:  List of the nodes' packet queue heads.
# @return bool:                     True if all nodes are empty; false otherwise.
def allNodesEmpty(node_head):
    empty = True
    for i in range(N):
        empty = empty and node_head[i] is None
    return empty

# Find the next packet to transmit
# Find the node with the next packet that has the lowest transmission start
# time within the packet neads and return its node index and transmission
# start time.
# @param node_head - list[Packet]:  List of the nodes' packet queue heads.
# @return (int, float):             The next node's index and the transmission start
#                                   time respectively.
def findNextPacket(node_head):
    trans_time = None
    for i in range(N):
        if node_head[i] is not None:
            if trans_time == None or trans_time >= node_head[i].t_trans:
                trans_time = node_head[i].t_trans
                next_node = i

    return next_node, trans_time

# Get the propagation delay
# Get the appropriate propagation delay between two nodes.
# @param src - int: Source node's index.
# @param des - int: Destination node's index.
# @return int:      Propagation delay between src and des.
def getPropagationDelay(src, des):
    return abs(des-src) * T_prop

# Get the next packet in the queue
# Get the next packet to put into a node's head of the queue. This packet
# is generated on the fly and the "initial" arrival time is based on the
# previous packet's "initial" arrival time. This should act the same as if
# the nodes were all generated beforehand, and should only serve the
# purpose of saving memory.
# @param node_head - list[Packet]:  List of the nodes' packet queue heads.
# @param i - int:                   Index of the node to get a new packet for.
# @param previous_pkt_done - float: Current time of when the previous packet
#                                   was "done" (successfully transmitted or
#                                   dropped) and when the new packet is to
#                                   be the new head of the node's queue.
# @return Packet:                   New packet for the head of the node's queue.
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

# Calculate exponential backoff time
# Calculate the random (exponential) backoff time given an index.
# @param index - int:   Index for the exponential backoff.
# @return float:        Backoff time.
def calcExpBackoff(index):
    rand = random.uniform(0, (2 ** index) - 1)
    # Tp = 512 bit-time wait (512 / R)
    return (rand * 512 / R)

# Simulate CSMA/CD
# Begin the CSMA/CD simulation with the specified global parameters.
# @sideeffect:  Print data regarding the simulation's efficiency and
#               throughput in CSV format.
def simulate():
    global c_tx_attempts
    global c_tx_success    

    c_tx_success = 0
    c_tx_attempts = 0

    # N number of nodes, all heads begin empty
    node_head = [None,] * N
    end_time = 0

    for i in range(N):
        node_head[i] = Packet(i, generate_random(A))

    while(not allNodesEmpty(node_head)):
        # Find the earliest node_head
        trans_node, trans_start_at_src = findNextPacket(node_head)
        # Transmit the targeted head packet
        trans_packet = node_head[trans_node]
        trans_end_at_src = trans_start_at_src + trans_packet.t_trans_delay
        c_tx_attempts+=1
        node_head[trans_node].c_channel_busy = 0

        # Flag to check if collision occur
        f_collision = False
        collision_nodes = []
        t_collision_detected = -1

        # Check possible collisions for each node
        for i in range(N):
            if i != trans_node and node_head[i] is not None:
                # Here is the time for each node to check the bus is busy or collision happen.
                # For 1-persistent, it keep checking the bus, as long as no collision, its t_trans will not be updated.

                # Bus busy or node idle through entire transmission
                if node_head[i].t_trans > trans_start_at_src + getPropagationDelay(trans_node, i):

                    # Bus detected to be busy
                    if node_head[i].t_trans < trans_end_at_src + getPropagationDelay(trans_node, i):
                        if persistent_simulation:
                            # Greedy; set start of transmission time immediately to when the current transmission seems to end
                            node_head[i].t_trans = trans_end_at_src + getPropagationDelay(trans_node, i)

                        if not persistent_simulation:
                            # It is possible that despite adding some backoff/waiting time, the channel is still detected to be busy
                            # due to the same transmitting node. In this case, loop until the wait time is sufficiently large.
                            while node_head[i] is not None and node_head[i].t_trans < trans_end_at_src + getPropagationDelay(trans_node, i):
                                node_head[i].c_channel_busy += 1

                                # This implementation does not cap the backoff for the channel busy counter
                                node_head[i].t_trans += calcExpBackoff(node_head[i].c_channel_busy)

                                # This implementation caps the backoff for the channel busy counter similar to the backoff for the collision counter
#                                if node_head[i].c_channel_busy <= 10:
#                                    node_head[i].t_trans += calcExpBackoff(node_head[i].c_channel_busy)
#                                else:
#                                    node_head[i] = getNextPacket(node_head, i, node_head[i].t_trans)

                # Collision
                else:
                    f_collision = True
                    collision_nodes.append(i)
                    c_tx_attempts+=1
                    # Node i has sensed the channel to be idle and so began transmission before colliding into the currently-transmitting node
                    # The channel busy counter is reset since the channel was sensed as idle
                    node_head[i].c_channel_busy = 0
                    # This determines when the currently-transmitting node first detects a collision - through the earliest time
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
            c_tx_success += 1
            end_time = trans_end_at_src
            node_head[trans_node] = getNextPacket(node_head, trans_node, trans_end_at_src)

    efficiency = c_tx_success / c_tx_attempts
    throughput = float(c_tx_success * L) / (1000000.0 * end_time)
    print(str(N) + ',' + str(efficiency) + ',' + str(throughput) + ', ' + str(end_time))

def main():
    global N
    global A
    global T
    global persistent_simulation

    parser = argparse.ArgumentParser(description='Simulate CSMA/CD of nodes (ECE358 Lab 2)')
    parser.add_argument('-A', '--arrival_rate', metavar='a', type=float, default=5.0,
                        help='Average packet arrival rate [packets/second]')
    parser.add_argument('-T', '--time', metavar='t', type=int, default=1000,
                        help='Time of the simulation')    
    parser.add_argument('-P', '--non_persistent', action='store_true',
                        help='Non-persistent CSMA/CD simulation (default: persistent)')

    args = parser.parse_args()
    A = args.arrival_rate
    T = args.time    
    persistent_simulation = not args.non_persistent

    print('# Nodes (N),Efficiency,Throughput [Mbps],End time [s]')
    for n in range(20, 101, 20):
        N = n
        simulate()       

#    N=1
#    simulate()

# END MAIN

if __name__ == '__main__':
   main()
