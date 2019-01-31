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
T = 1000

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
    arrival_rate = (rho * C)/L          # get lambad based on traffic intensity
    observer_rate = 5 * arrival_rate    # observer rate is at least 5 times of arrival rate

    packet_arrival_time = 0             # initialize arrival time of first packet
    departure_time = 0                  # initialize departure time of first packet
    observer_time = 0                   # initialize observer time of first observation event

    arrival_array = []                  # arrrival event list
    departure_array = []                # departure event list
    observer_array = []                 # observer event list
    event_array = []                    # event list of all three different events
    packets_in_queue = []               # array to store number of packets in the queue at differnt observation time

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
    c_arrival = 0           # number of arrived packets
    c_departure = 0         # number of departured packets
    c_observation = 0       # number of observations
    c_idle = 0              # number of idle status when observe

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
# @return (float, float, float): A tuple of (E[N], P(IDLE), P(LOSS))
def finite_buffer(rho, K):
    arrival_rate = (rho * C)/L              # get lambad based on traffic intensity
    observer_rate = 5 * arrival_rate        # observer rate is at least 5 times of arrival rate

    packet_arrival_time = 0                 # initialize arrival time of first packet
    observer_time = 0                       # initialize observer time of first observation event

    event_array = []                        # event list of all three different events
    packets_in_queue = []                   # array to store number of packets in the queue at differnt observation time

    # Generate arrival and observer events
    while packet_arrival_time < T:
        packet_arrival_time += generate_random(arrival_rate)
        heapq.heappush(event_array, (packet_arrival_time, ARRIVAL))

    while observer_time < T:
        observer_time += generate_random(observer_rate)
        heapq.heappush(event_array, (observer_time, OBSERVER))

    # Begin simulation

    # Counters
    c_arrival = 0           # number of packets that successfully enter the queue
    c_departure = 0         # number of packets departured from the queue
    c_observation = 0       # number of obervation points
    c_idle = 0              # number of idle cases occurred at observation point
    c_generated = 0         # number of all generated packets
    c_dropped = 0           # number of packets that are dropped

    queue = 0               # the current number of packets in queue
    departure_time = 0      # initiallize the departure time of the first packet    

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
    parser.add_argument('-T', '--time_units', metavar='t', type=int, default=1000,
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
        random_array = generate_random_array(75)

        mean = sum(random_array) / 1000
        t = 0
        for rannum in random_array:
            t += (rannum - mean)**2
        variance = t / 1000

        print("Mean: " + str(mean))
        print("Variance: " + str(variance))

        exit()

    # Header for the CSV format output indicating the type for each column
    header = 'Rho,E[N],P(IDLE)'
    # P(LOSS) is only needed for finite buffer simulations
    if K is not None:
        header += ',P(LOSS)'
    print(header)

    queue_utilization_array = []
    if rho is None:
        if K is None:
            queue_utilization_array.extend(list(range(25, 100, 10)))
        else:
            queue_utilization_array.extend(list(range(40, 200, 10)))
            queue_utilization_array.extend(list(range(200,500,20)))
            queue_utilization_array.extend(list(range(500,1000,40)))
    else:
        queue_utilization_array.append(rho * 100)

    if K is None:
        for rho_index in queue_utilization_array:
            simulate_infinite(rho_index/100)
    else:
        for rho_index in queue_utilization_array:
            simulate_finite(rho_index/100, K)

# END MAIN

if __name__ == '__main__':
   main()

