import random
import math
import bisect

ARRIVAL = 0
DEPARTURE = 1
OBSERVER = 2

L = 2000
# arrival_rate = 75
C = 1000000
T = 1000

# observer_rate = 50
# queue_utilization = L * arrival_rate / C

# public_size = 1000

# z_lambda = 75
o_average_pkts = []
o_p_idle = []
o_p_drop = []

def generate_random(lambda_para):
    return - (1 / lambda_para) * math.log(1 - random.uniform(0, 1))

def generate_random_array(lambda_para):
    expo_random_array = []

    for _ in range(0, 1000):
        uni_ran = random.uniform(0, 1)
        expo_random = - (1 / lambda_para) * math.log(1 - uni_ran)
        expo_random_array.append(expo_random)

    return expo_random_array
            
def infinite_buffer(rho):
    # Generate observer array, arrival array, and departure array 
    arrival_rate = (rho * C)/L
    packet_arrival = 0
    observer_time = 0
    departure_time = 0
    arrival_array = []
    departure_array = []
    observer_array = []
    event_array = []
    packets_in_queue = []
    observer_rate = 5 * arrival_rate

    while packet_arrival < T:
        packet_arrival += generate_random(arrival_rate)
        arrival_array.append(packet_arrival)
        service_time = (generate_random(1/L))/C
        if packet_arrival > departure_time:
            departure_time = packet_arrival + service_time
        else: 
            departure_time+=service_time

        departure_array.append(departure_time)

    while observer_time < T:
        observer_time += generate_random(observer_rate)
        observer_array.append(observer_time)

    # Generate Event array
    for arrival in arrival_array:
        event_array.append((ARRIVAL, arrival))
    
    for departure in departure_array:
        event_array.append((DEPARTURE, departure))
    
    for observer in observer_array:
        event_array.append((OBSERVER, observer))
    
    event_array.sort(key=lambda x: x[1])

    # Simulation start here
    c_arrival = 0
    c_departure = 0
    c_observation = 0
    c_idle = 0


    for event in event_array:
        # print(event)
        if event[0] == ARRIVAL:
            c_arrival+=1
        if event[0] == DEPARTURE:
            c_departure+=1
        if event[0] == OBSERVER:
            c_observation+=1
            if c_arrival == c_departure:
                c_idle+=1

            packets_in_queue.append(c_arrival-c_departure)
    
    average_pkts_in_queue = sum(packets_in_queue) / len(packets_in_queue)
    p_idle = c_idle/c_observation

    return average_pkts_in_queue, p_idle

def insert_event(event_list, event_ctr, time):
    first = event_ctr
    last = len(event_list)-1
    while first <= last:            
        midpoint = (first + last)//2
        if first == last:
            if event_list[midpoint][1] < time:
                return midpoint+1
            else: 
                return midpoint
        else:
            if event_list[midpoint][1] < time:
                first = midpoint+1
            else:
                last = midpoint-1

    return first       
    # while event_array[index][1] is not None and event_array[index][1] < time and index < len(event_array)-1:
    #     index+=1

    # event_list.insert(index, (DEPARTURE, time))

def finite_buffer(rho, K):
    # Generate observer array, arrival array, and departure array 
    arrival_rate = (rho * C)/L
    packet_arrival = 0
    observer_time = 0
    arrival_array = []
    observer_array = []
    event_array = []
    packets_in_queue = []
    observer_rate = 5 * arrival_rate

    while packet_arrival < T:
        packet_arrival += generate_random(arrival_rate)
        arrival_array.append(packet_arrival)

    while observer_time < T:
        observer_time += generate_random(observer_rate)
        observer_array.append(observer_time)

    # Generate Event array
    for arrival in arrival_array:
        event_array.append((ARRIVAL, arrival))
    
    for observer in observer_array:
        event_array.append((OBSERVER, observer))
    
    event_array.sort(key=lambda x: x[1])

    # Simulation start here
    c_arrival = 0
    c_departure = 0
    c_observation = 0
    c_idle = 0
    c_generated = 0
    c_droped = 0

    queue = 0
    departure_time = 0

    evt_ctr = 0

    while evt_ctr < len(event_array):
        # print(len(event_array))
        if event_array[evt_ctr][0] == ARRIVAL:
            c_generated+=1
            packet_arrival = event_array[evt_ctr][1]
            if queue < K:
                c_arrival+=1
                queue+=1 
                # time = event_array[evt_ctr][1] + (generate_random(1/L))/C

                service_time = (generate_random(1/L))/C
                if packet_arrival > departure_time:
                    departure_time = packet_arrival + service_time
                else: 
                    departure_time+=service_time
                # index = 0
                # while event_array[index][1] is not None and event_array[index][1] < time and index < len(event_array)-1:
                #     index+=1
                
                event_array.insert(insert_event(event_array, evt_ctr, departure_time), [DEPARTURE, departure_time])

                # insert_event(event_array, packet_arrival + (generate_random(1/L))/C)
            else:
                c_droped+=1       
        if event_array[evt_ctr][0] == DEPARTURE:
            c_departure+=1
            queue-=1
        if event_array[evt_ctr][0] == OBSERVER:
            c_observation+=1
            if c_arrival == c_departure:
                c_idle+=1
            packets_in_queue.append(c_arrival-c_departure)

        evt_ctr += 1
    
    average_pkts_in_queue = sum(packets_in_queue) / len(packets_in_queue)
    p_idle = c_idle/c_observation

    return average_pkts_in_queue, p_idle, c_droped/c_generated

# def process_event(event):
#     event_switch = {
#         ARRIVAL : process_arrival,
#         DEPARTURE : process_departure,
#         OBSERVER : process_observation
#     }
#     event_switch[event[0]](event[1])

# def process_arrival(time):
#     return

# def process_observation(time):
#     return
    
# def process_departure(time):
#     return


def simulate_infinite(rho):
    r_avrg_pkts, r_p_idle = infinite_buffer(rho)
    o_average_pkts.append(r_avrg_pkts)
    o_p_idle.append(r_p_idle)
    print("==============================================")
    print("For rho = " + str(rho) + ":")
    print("Average packets in the queue: " + str(r_avrg_pkts))
    print("Possibility of idle case: " + str(r_p_idle))

    print(len(o_average_pkts))


def simulate_finite(rho, K):
    r_avrg_pkts, r_p_idle, p_pkt_drop = finite_buffer(rho, K)
    o_average_pkts.append(r_avrg_pkts)
    o_p_idle.append(r_p_idle)
    o_p_drop.append(p_pkt_drop)
    print("==============================================")
    print("For rho = " + str(rho) + ":")
    print("Average packets in the queue: " + str(r_avrg_pkts))
    print("Possibility of idle case: " + str(r_p_idle))
    print("Possibility of packet drop: " + str(p_pkt_drop))


def main():
    '''
        To run the result for a single rho, just do simulate_infinite(rho) or simulate_finite(rho, K)
    '''

# =============== Infinite Buffer Queue ==============
    # '''
    #     Command out this block if you want to test for customed rho 
    # '''
    # # o_average_pkts = []
    # # o_p_idle = []
    # queue_utilization_array = list(range(25, 105, 10))

    # for m_lambda in queue_utilization_array:
    #     simulate_infinite(m_lambda/100)

    
    # print(len(o_average_pkts))
    # print(o_average_pkts)

    # print("Average packets in the queue: ---------->")
    # for avrg_pkt in o_average_pkts:
    #     print(avrg_pkt) 
    
    # print("Possibility of idle case: ---------->")
    # for p_idle in o_p_idle:
    #     print(p_idle) 


# # =============== Finite Buffer Queue ==============
    '''
        Command out this blo`ck if you want to test for customed rho 
    '''

    K = [10, 25, 50]
    queue_utilization_array = list(range(40, 200, 10))
    queue_utilization_array.extend(list(range(200,500,20)))
    queue_utilization_array.extend(list(range(500,1000,40)))

    for m_lambda in queue_utilization_array:
        simulate_finite(m_lambda/100, 10)

    print("Average packets in the queue: ---------->")
    for avrg_pkt in o_average_pkts:
        print(avrg_pkt) 
    
    print("Possibility of idle case: ---------->")
    for p_idle in o_p_idle:
        print(p_idle) 

    print("Possibility of packet drops: ---------->")
    for p_drop in o_p_drop:
        print(p_drop) 


# END MAIN

if __name__ == '__main__':
   main()

        # observer_array = generate_random_array(observer_rate)


# mean = sum(expo_random_array) / 1000
# variance = sum([(number - mean)**2 for number in expo_random_array]) / 1000

# print(expo_random_array)
# print('mean ' + str(mean))
# print('variance ' + str(variance))
