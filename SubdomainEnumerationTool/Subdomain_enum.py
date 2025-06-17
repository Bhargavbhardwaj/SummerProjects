import requests  # used to send request to each constructed subdomains URL to check if it exists. It simplifies making GET/POST requests

import threading  # helps run multiple operation in parallel

domain = 'youtube.com'

with open('subdomain.txt') as file:  # Reads subdomains (like www, mail, blog, etc.) from a file line-by-line and stores them in a list.
    subdomains = file.read().splitlines()  # splitlines() removes \n characters and returns a list of strings.

discovered_subdomains = []

lock = threading.Lock() # Used to prevent multiple threads from modifying discovered_subdomains at the same time, which can cause race conditions or data corruption.

def check_subdomain(subdomain):

    url = f'http://{subdomain}.{domain}'
    try:
        requests.get(url)  # Sends a GET request. If the domain exists, it usually returns 200 OK; if not, it raises requests.ConnectionError.
    except requests.ConnectionError:
        pass
    else:
        print("[+] Discovered subdomain: ", url)
        with lock:  # ensures only one thread at a time appends to discovered_subdomains, avoiding issues in parallel execution.
            discovered_subdomains.append(url)

threads = []

for subdomain in subdomains:
    thread = threading.Thread(target = check_subdomain, args=(subdomain,))
    thread.start()
    threads.append(thread)

for thread in threads:
    thread.join()  # Ensures that the main thread waits for all subdomain-checking threads to complete before proceeding to write output.



with open("discovered_subdomains.txt", 'w') as f:
    for subdomain in discovered_subdomains:
        print(subdomain, file = f)