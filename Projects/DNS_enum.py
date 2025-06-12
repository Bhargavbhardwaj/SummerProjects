import dns.resolver  # this module helps perform DNS queries in python

target_domain = 'youtube.com'
records_type = ['A', 'AAAA', 'CNAME', 'MX', 'TXT', 'SOA']

# 'A' record is IPv4 and 'AAAA' record is IPv6 address , CNAME is canonical name, MX is mail exchange and SOA is start of authority which defines the primary name server and zone details
# Each record type serves a specific purpose—such as mapping a domain to an IP address, defining email servers, or verifying ownership.


resolver = dns.resolver.Resolver()  # creates a DNS resolver object which handles DNS queries using system-configured or custom nameservers.
for record_type in records_type:
    try:
        answer = resolver.resolve(target_domain, record_type)
    except dns.resolver.NoAnswer:
        continue # if no such record exists then skip to the next one using continue

    print(f'{record_type} records for {target_domain}') # if records are found, it prints the type and the records
    for data in answer: # loop over the answer object and prints each record line by line
        print(f'{data}')

