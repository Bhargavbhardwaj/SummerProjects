import scapy.all as scapy  # whenever we work with networking, we use this module
# it is a powerful networking tool to create, send ,and receive packets
import  socket  #  Built-in Python module to get info like hostnames from IP addresses.
import threading  #  Parallel IP scanning (muliple tasks)
from queue import Queue # thread-safe queue to store results form multiple threads
import ipaddress  #  Handles and splits IP ranges like 192.168.1.0/24.

def scan(ip, result_queue):
    arp_request = scapy.ARP(pdst=ip) # Creates an ARP packet asking "Who hss this IP?" pdst is packet destination
    brodcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")  # Builds an Ethernet frame to send the ARP request to everyone on the network (ff:ff:ff:ff:ff:ff is the broadcast MAC).
    packet = brodcast/arp_request # Combines both ARP and Ethernet into a single packet.
    answer = scapy.srp(packet, timeout=1, verbose=False)[0] # Sends the packet and waits for a reply.
    # timeout=1 means don’t wait too long for a reply. verbose=False hides output and keeps the terminal clean.


  # Extracting info from the answer
    clients = []
    for client in answer: # answer contains replies from devices that responded
        client_info = {'IP': client[1].psrc, 'MAC': client[1].hwsrc}
        # client[1].psrc	Source IP address of the reply.
        # client[1].hwsrc	Source MAC address of the reply.
        try:
            hostname = socket.gethostbyaddr(client_info['IP'])[0]  # tries to find the hostname of the IP
            client_info['Hostname'] = hostname
        except socket.herror:  # If no hostname is found, sets it to “Unknown.”
            client_info['Hostname'] = 'Unknown'
        clients.append(client_info)
    result_queue.put(clients) # Stores the result in a queue so the main program can access it.

def print_result(result):
    print('IP' + " "*20 + 'MAC' + " "*20 + 'Hostname')
    print('-'*80)
    for client in result:
        print(client['IP'] + '\t\t' + client['MAC'] + '\t\t' + client['Hostname'])

def main(cidr):  # cidr is representation of IP address
    result_queue = Queue()
    threads = [] # Stores all scanning threads to wait for them later.
    network = ipaddress.ip_network(cidr, strict = False) # Breaks that CIDR into individual IPs.
# The strict mode decides how picky Python should be about your input.

    for ip in network.hosts(): # scan will not go one by one but it will take all ip addresses at once and scan it and will put the result in the Queue
        thread = threading.Thread(target=scan, args = (str(ip), result_queue))  # Creates a thread that runs the scan() function for each IP.
        thread.start()
        threads.append(thread)


        for thread in threads:
            thread.join()

        all_clients = []
        while not result_queue.empty():
            all_clients.extend(result_queue.get()) # Pulls results from the Queue and combines them into one list.

        print_result(all_clients)


if __name__ == '__main__':
    cidr = input("Enter network IP address: ") # Asks the user to input the network range (CIDR format).
    main(cidr)
