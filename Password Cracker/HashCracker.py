# a Python-based tool that attempts to crack hashed
# passwords using either a wordlist or brute-force techniques.

import hashlib  # For hash functions like md5, sha1, sha256, etc
import itertools #  For generating all possible combinations of characters.
import string
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm # or showing progress bars in loops
import argparse  # For parsing command-line arguments.


# List of hash types that the code supports
hash_name = [
    'md5',
    'sha1',
    'sha224',
    'sha256',
    'sha384',
    'sha3_224',
    'sha3_256',
    'sha3_384',
    'sha3_512',
    'sha512'
]


# 1. Functions to generate passwords
#  This function generates all possible passwords between min_length and max_length using the specified characters (e.g., A-Z, 0–9).
def generate_passwords(min_length, max_length, charcaters):
    for length in range(min_length, max_length + 1):
        for pwd in itertools.product(charcaters, repeat=length): # itertools.product generates all combinations with repetition.
            yield ''.join(pwd) # yield is used instead of return to create a generator that saves memory.

# 3. working with wordlists - check if password matches the hash
def check_hash(hash_fn, password, target_hash):
    return hash_fn(password.encode()).hexdigest() == target_hash


# 2. Function to verify hash - main cracking function
def crack_hash(hash, wordlist=None, hash_type='md5', min_length=0, max_length=0, characters=string.ascii_letters + string.digits, max_workers=4):
    hash_fn = getattr(hashlib, hash_type, None)
    if hash_fn is None or hash_type not in hash_name:
        raise ValueError(f'[!] Invalid hash type: {hash_type} supported are {hash_name}')

# wordlist method
    if wordlist:
        with open(wordlist, 'r') as f:
            lines = f.readlines()
            total_lines = len(lines)
            print(f"[*] Cracking hash {hash} using {hash_type} with a list of {total_lines} passwords.")

            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = {executor.submit(check_hash, hash_fn, line.strip(), hash): line for line in lines} # schedules the password checking task.
                for future in tqdm(futures, total=total_lines, desc="Cracking hash"): # The dictionary futures maps each thread to the password it is checking.
                    if future.result():
                        return futures[future].strip()
# brute force method
    elif min_length > 0 and max_length > 0:
        total_combinations = sum(len(characters) ** length for length in range(min_length, max_length + 1))  # Calculates the total number of combinations to show progress.
        print(f'[*] Cracking hash {hash} using {hash_type} with generated passwords of lengths from {min_length} to {max_length}. Total combinations: {total_combinations}.')

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = []
            with tqdm(total=total_combinations, desc='Generating and cracking hash') as pbar:
                for pwd in generate_passwords(min_length, max_length, characters):
                    future = executor.submit(check_hash, hash_fn, pwd, hash)
                    futures.append(future)
                    pbar.update(1)
                    if future.result():
                        return pwd

    return None


# taking input from the users
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Hash cracker')
    parser.add_argument('hash', help='The hash to crack.')
    parser.add_argument('-w','--wordlist', help='The path to the wordlist.')
    parser.add_argument('--hash_type', help='The hash to use', default='md5')
    parser.add_argument('--min_length', type=int, help='The minimum length of password to generate.')
    parser.add_argument('--max_length', type=int, help='The maximum length of password to generate.')
    parser.add_argument('-c', '--characters', help='The characters to use for password generation.')
    parser.add_argument('--max_workers', type=int, help='The maximum number of threads.')

    args = parser.parse_args()

    cracked_password = crack_hash(args.hash, args.wordlist, args.hash_type, args.min_length, args.max_length, args.characters, args.max_workers)

    if cracked_password:
        print(f"[+] Found password: {cracked_password}")
    else:
        print("[!] Password not found.")