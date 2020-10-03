import argparse
import sys
import csv

class Queue:
    def __init__(self):
        self.items = []

    def is_empty(self):
        return self.items == []

    def enqueue(self, item):
        self.items.insert(0, item)

    def dequeue(self):
        return self.items.pop()

    def size(self):
        return len(self.items)

class Server:
    def __init__(self, pt):
        self.process_time = pt
        self.current_request = None
        self.time_remaining = 0

    def tick(self):
        if self.current_request != None:
            self.time_remaining = self.time_remaining - 1
            if self.time_remaining <= 0:
                self.current_request = None

    def busy(self):
        if self.current_request != None:
            return True
        else:
            return False

    def start_next(self, new_request):
        self.current_request = new_request
        self.time_remaining = new_request.get_process_time() * 60 / self.process_time


class Request:
    def __init__(self, time, process_time):
        self.timestamp = time
        self.p_time = process_time

    def get_stamp(self):
        return self.timestamp

    def get_process_time(self):
        return self.p_time

    def wait_time(self, current_time):
        return abs(current_time - self.timestamp)

def simulateOneServer(input_file):
    file_data           = []
    wait_times          = []
    requests_per_minute = 10
    simulation_run_time = 10000
    lab_server          = Server(requests_per_minute)
    server_queue        = Queue()

    with open(input_file) as csvfile:
        read = csv.reader(csvfile, delimiter=',', dialect=csv.excel_tab)
        for i, row in enumerate(read,start=1):
            simulation_second = int(row[0])
            req_file_path = row[1]
            process_time = int(row[2])
            file_data = file_data + [[simulation_second, req_file_path, process_time]]

    for current_second in range(simulation_run_time):
        if(current_second < len(file_data)):
            x = file_data[current_second]
            server_request = Request(x[0], x[2])
            server_queue.enqueue(server_request)

        if (not lab_server.busy()) and (not server_queue.is_empty()):
            new_request = server_queue.dequeue()
            wait_times.append(new_request.wait_time(current_second))
            lab_server.start_next(new_request)
        average_wait = sum(wait_times) / len(wait_times)
        print('Average wait time: %6.2f secs; %3d requests remaining' % (average_wait, server_queue.size()))
        lab_server.tick()

def simulateManyServers(input_file, server_num):
    file_data           = []
    requests_per_minute = 10
    simulation_run_time = 10000
    instance_time       = [0 for i in range(server_num)]
    wait_times          = [[] for i in range(server_num)]
    server_instances    = [Server(requests_per_minute) for i in range(server_num)]
    queue_instances     = [Queue() for i in range(server_num)]

    with open(input_file) as csvfile:
        read = csv.reader(csvfile, delimiter=',', dialect=csv.excel_tab)
        for i, row in enumerate(read,start=1):
            simulation_second = int(row[0])
            req_file_path = row[1]
            process_time = int(row[2])
            file_data = file_data + [[simulation_second, req_file_path, process_time]]

    for current_second in range(simulation_run_time):
        i = current_second % server_num
        if(current_second < len(file_data)):
            x = file_data[current_second]
            server_request = Request(x[0], x[2])
            queue_instances[i].enqueue(server_request)

        if (not server_instances[i].busy()) and (not queue_instances[i].is_empty()):
            new_request = queue_instances[i].dequeue()
            wait_times[i].append(new_request.wait_time(instance_time[i]))
            server_instances[i].start_next(new_request)
        average_wait = sum(wait_times[i]) / len(wait_times[i])
        print('Server Instance # %1d. Average wait time: %6.2f secs; %3d requests remaining' % (i+1, average_wait,queue_instances[i].size()))
        server_instances[i].tick()
        instance_time[i] += 1

def main(file_name, servers=0):
    if not servers:
        simulateOneServer(file_name)
    else:
        simulateManyServers(file_name, servers)

if len(sys.argv) <= 2:
    exit()
parser = argparse.ArgumentParser()
parser.add_argument('--file', help='Enter your file\'s path')
parser.add_argument('--server', help='Enter a number of server instances')
arg = parser.parse_args()

try:
    main(arg.file, int(arg.server))
except Exception as exception:
    print(str(exception))
