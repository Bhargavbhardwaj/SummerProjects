# A port-scanner tool that identifies open ports on a target machine and
# optionally extracts service banners (Apache httpd or OpenSSH) from the open ports

import socket # Core module for network communication in Python (used to connect to IPs and ports).
import  concurrent.futures
import sys # Used here to write real-time progress to the terminal without jumping to new lines.

# Text colors for output - ANSI escape codes to color the output in the  terminal
RED = "\033[91m" # used for open ports(highlight them)
GREEN = "\033[92m"  # Used for banner ino
RESET = "\033[0m" # Reset color to normal after colored text


# 4. Formatting our results. This function takes a list of scan results and creates a cleanly formatted string.
def format_port_results(results):
    formatted_results = "Port Scan Results:\n"
    formatted_results += "{:<8} {:<15} {:<10}\n".format("Port", "Service", "Status") # This function takes a list of scan results and creates a cleanly formatted string.
    formatted_results += '-' * 85 + "\n"
    for port, service, banner, status in results:
        if status:
            formatted_results += f"{RED}{port:<8} {service:<15} {'Open':<10}{RESET}\n" # If the port is open, it prints it in red along with the port number and service.
            if banner:
                banner_lines = banner.split('\n')
                for line in banner_lines:
                    formatted_results += f"{GREEN}{'':<8}{line}{RESET}\n" #If there’s a banner (like a message from the server), print it below in green.
    return formatted_results


# 2. Extracting banner from our target
def get_banner(sock): # When a port is open, sometimes the server sends back an identifying message (e.g., "SSH-2.0-OpenSSH_8.2").
    try:
        sock.settimeout(1)  # This function waits up to 1 second and tries to read up to 1024 bytes from the port.
        banner = sock.recv(1024).decode().strip()
        return banner
    except:
        return " "  # If nothing comes back, it returns a blank string.



# 1. Creating main function of the program
def scan_port(target_ip, port): # this creates a TCP socket.
    sock = None
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((target_ip, port))  # connect_ex() tries to connect to the target. It returns:
        # 0 if the connection was successful (port is open)
        #
        # Non-zero if the connection failed (closed/filtered)
        if result == 0:
            try:
                service = socket.getservbyport(port, 'tcp') # If the port is open, this line guesses what common service might run on it (22 → ssh, 80 → http).
            except:
                service = 'Unknown'
            banner = get_banner(sock)
            return port, service, banner, True # Returns a tuple with all info collected.
        else:
            return port, "", "", False
    except:
        return port, "", "", False
    finally:
        if sock:
            sock.close()

# 3. Working with threads
def port_scan(target_host, start_port, end_port):
    target_ip = socket.gethostbyname(target_host) # Converts the domain (like google.com) into an IP.
    print(f"Starting scan on host: {target_ip}")

    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers = 400) as executor:  # Uses multi-threading to scan ports fast — up to 400 at a time.
        futures = {executor.submit(scan_port, target_ip, port): port for port in range(start_port, end_port)}

        total_ports = end_port - start_port + 1
        for i,  future in enumerate(concurrent.futures.as_completed(futures), start = 1):
            port, service, banner, status = future.result()
            results.append((port, service, banner, status))
            sys.stdout.write(f"\rProgress: {i}/{total_ports} ports scanned")
            sys.stdout.flush()

    sys.stdout.write("\n")
    print(format_port_results(results))

if __name__ == '__main__':
    target_host = input("Enter your target ip: ")
    start_port = int(input("Enter your start port: "))
    end_port = int(input("Enter your end port here: "))

    port_scan(target_host, start_port,  end_port)
