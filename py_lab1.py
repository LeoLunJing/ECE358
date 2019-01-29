import argparse
import random
import math
import heapq

####################################################
############### Event type constants ###############
####################################################
ARRIVAL = 0
DEPARTURE = 1
OBSERVER = 2

####################################################
############### Parameter Constants ################
####################################################
L = 2000
C = 1000000
T = 100

# Generate exponential random variable
# Generate a variable based on a Poisson distribution following:
# var = -(1/lambda_para) * ln(1 - U)
# @param lambda_para - float: Lambda parameter for random variable from
#                           the equation mentioned above.
# @return float: exponential random variable.
def generate_random(lambda_para):
    return - (1 / lambda_para) * math.log(1 - random.uniform(0, 1))

# Generate array of exponential random variables
# Generate a list of length 1000 consisting of random variables following
# a Poisson distribution following: var = -(1/lambda_para) * ln(1 - U)
# @param lambda_para - float: Lambda parameter for random variables from
#                           the equation mentioned above.
# @return list[float]: list of exponential random variables.
def generate_random_array(lambda_para):
    expo_random_array = []

    for _ in range(0, 1000):
        uni_ran = random.uniform(0, 1)
        expo_random = - (1 / lambda_para) * math.log(1 - uni_ran)
        expo_random_array.append(expo_random)

    return expo_random_array

# Simulate an M/M/1 queue
# Simulate a queue/buffer with an infinite length that processes arrival,
# departure, and observer event packets.
# @param rho - float: Rho parameter for utilization of the queue.
# @return (float, float): A tuple of (E[N], P(IDLE))
def infinite_buffer(rho):
    arrival_rate = (rho * C)/L
    observer_rate = 5 * arrival_rate

    packet_arrival_time = 0
    departure_time = 0
    observer_time = 0

    arrival_array = []
    departure_array = []
    observer_array = []
    event_array = []
    packets_in_queue = []

    # Generate observer array, arrival array, and departure array 
    while packet_arrival_time < T:
        packet_arrival_time += generate_random(arrival_rate)
        arrival_array.append(packet_arrival_time)
        service_time = (generate_random(1/L))/C
        if packet_arrival_time > departure_time:
            departure_time = packet_arrival_time + service_time
        else: 
            departure_time+=service_time

        departure_array.append(departure_time)

    while observer_time < T:
        observer_time += generate_random(observer_rate)
        observer_array.append(observer_time)

    # Generate Event array
    for arrival in arrival_array:
        event_array.append((arrival, ARRIVAL))
    
    for departure in departure_array:
        event_array.append((departure, DEPARTURE))
    
    for observer in observer_array:
        event_array.append((observer, OBSERVER))
    
    event_array.sort(key=lambda x: x[0])

    # Begin simulation

    # Counters
    c_arrival = 0
    c_departure = 0
    c_observation = 0
    c_idle = 0

    for event in event_array:
        # print(event)
        if event[1] == ARRIVAL:
            c_arrival+=1
        elif event[1] == DEPARTURE:
            c_departure+=1
        elif event[1] == OBSERVER:
            c_observation+=1
            packets_in_queue.append(c_arrival-c_departure)
            # If all packets that arrived have departed, then queue is empty
            if c_arrival == c_departure:
                c_idle+=1
    
    average_pkts_in_queue = sum(packets_in_queue) / len(packets_in_queue)
    p_idle = c_idle/c_observation

    return average_pkts_in_queue, p_idle

# Simulate an M/M/1/K queue
# Simulate a queue/buffer with length K that processes arrival,
# departure, and observer event packets.
# @param rho - float: Rho parameter for utilization of the queue.
# @param K - int: K parameter for length of the queue/buffer.
# @return (float, float): A tuple of (E[N], P(IDLE), P(LOSS))
def finite_buffer(rho, K):
    arrival_rate = (rho * C)/L
    observer_rate = 5 * arrival_rate

    packet_arrival_time = 0
    observer_time = 0

    arrival_array = []
    observer_array = []
    event_array = []
    packets_in_queue = []

    # Generate observer array and arrival array
    while packet_arrival_time < T:
        packet_arrival_time += generate_random(arrival_rate)
        arrival_array.append(packet_arrival_time)

    while observer_time < T:
        observer_time += generate_random(observer_rate)
        observer_array.append(observer_time)

    # Generate Event array
    for arrival in arrival_array:
        heapq.heappush(event_array, (arrival, ARRIVAL))
    
    for observer in observer_array:
        heapq.heappush(event_array, (observer, OBSERVER))
    
    # Begin simulation

    # Counters
    c_arrival = 0
    c_departure = 0
    c_observation = 0
    c_idle = 0
    c_generated = 0
    c_dropped = 0

    queue = 0
    departure_time = 0

    while len(event_array) > 0:
        # print(len(event_array))
        event = heapq.heappop(event_array)
        if event[1] == ARRIVAL:
            c_generated+=1
            packet_arrival_time = event[0]
            # If queue is full, then drop the newly-arrived event
            if queue >= K:
                c_dropped+=1
            # Otherwise, calculate appropriate departure time and departure event add to list
            else:
                c_arrival+=1
                queue+=1 

                service_time = (generate_random(1/L))/C
                if packet_arrival_time > departure_time:
                    departure_time = packet_arrival_time + service_time
                else: 
                    departure_time+=service_time
                
                heapq.heappush(event_array, (departure_time, DEPARTURE))

        elif event[1] == DEPARTURE:
            c_departure+=1
            queue-=1
        elif event[1] == OBSERVER:
            c_observation+=1
            packets_in_queue.append(c_arrival-c_departure)
            # If all packets that arrived have departed, then queue is empty
            if c_arrival == c_departure:
                c_idle+=1
    
    average_pkts_in_queue = sum(packets_in_queue) / len(packets_in_queue)
    p_idle = c_idle/c_observation

    return average_pkts_in_queue, p_idle, c_dropped/c_generated

# Invoke the infinite_buffer() simulator, print the results
def simulate_infinite(rho):
    r_avrg_pkts, r_p_idle = infinite_buffer(rho)
    print(str(rho) + "," + str(r_avrg_pkts) + "," + str(r_p_idle))

# Invoke the finite_buffer() simulator, print the results
def simulate_finite(rho, K):
    r_avrg_pkts, r_p_idle, p_pkt_drop = finite_buffer(rho, K)
    print(str(rho) + "," + str(r_avrg_pkts) + "," + str(r_p_idle) + "," + str(p_pkt_drop))

# Run the M/M/1[/K] queue simulator based on the command line options provided
# Can call 'python [python_filename].py --help' to view all options.
def main():
    global T

    parser = argparse.ArgumentParser(description='Simulate networking packet buffer (ECE358 Lab1)')
    parser.add_argument('-K', '--queue_size', metavar='n', type=int, default=None,
                        help='Size of the queue/buffer (default: infinite)')
    parser.add_argument('-T', '--time_units', metavar='t', type=int, default=100,
                        help='Time units to run each simulation for')
    parser.add_argument('-R', '--rho', metavar='r', type=float, default=None,
                        help='Rho value to simulate (no value implies range from [0.4, 10])')

    parser.add_argument('-Q1', '--question1', action='store_true',
                        help='Calculate the values for question 1')

    args = parser.parse_args()
    K = args.queue_size
    T = args.time_units
    rho = args.rho

    # Calculate the mean/variance for lab 1 question 1
    if args.question1:
        expo_random_array = generate_random_array(75)

        mean = sum(expo_random_array) / 1000
        variance = sum([(number - mean)**2 for number in expo_random_array]) / 1000

        # print(expo_random_array)
        print('mean ' + str(mean))
        print('variance ' + str(variance))

        exit()

    # Header for the CSV format output indicating the type for each column
    header = '"Rho","E[N]","P(IDLE)"'
    # P(LOSS) is only needed for finite buffer simulations
    if K is not None:
        header += ',"P(LOSS)"'
    print(header)

    queue_utilization_array = list(range(40, 200, 10))
    queue_utilization_array.extend(list(range(200,500,20)))
    queue_utilization_array.extend(list(range(500,1000,40)))

    if K is None:
        if rho is None:
            for rho_index in queue_utilization_array:
                simulate_infinite(rho_index/100)
        else:
            simulate_infinite(rho)
    else:
        if rho is None:
            for rho_index in queue_utilization_array:
                simulate_finite(rho_index/100, K)
        else:
            simulate_finite(rho, K)

# END MAIN

if __name__ == '__main__':
   main()

