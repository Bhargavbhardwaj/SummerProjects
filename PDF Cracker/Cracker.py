# A PDF password cracker that attempts to decrypt password-protected PDF files using
# a wordlist or by generating passwords programmatically.

import itertools  #To generate combinations of characters (for password generation).
import pikepdf   # To try opening password-protected PDF files (handles encryption).
import string
from tqdm import tqdm  # Displays a progress bar to monitor cracking progress.
from concurrent.futures import ThreadPoolExecutor, as_completed  # Allows multithreading using ThreadPoolExecutor for faster cracking.
import argparse   # Parses command-line arguments provided by the user (PDF file, wordlist, etc).


# Generate all combinations of passwords of different lengths
def generate_passwords(chars, min_length, max_length):
    for length in range(min_length, max_length+1):
        for password in itertools.product(chars, repeat = length):
            yield ''.join(password)


# Loads passwords from a wordlist file, one line at a time.
def load_wordlist(wordlist_file):
    with open(wordlist_file, 'r') as file:
        for line in file:
            yield line.strip()

# attempts to open the PDF using a specific password. Returns the password if it works, else returns NONE.
def try_password(pdf_file, password):
    try:
        with pikepdf.open(pdf_file, password = password) as pdf:
            print(f'[+] Password found: {password}')
            return password

    except pikepdf._core.PasswordError: # raised when an incorrect password is used  to open an unencrypted file.
        return None

# Making the code faster
# this is the core cracking engine, creates a progress abr using tqbm.
#

def decrypt_pdf(pdf_file, passwords, total_passwords,max_workers = 4 ):
    with tqdm(total = total_passwords, desc = 'Decrypting PDF', unit = 'passwprd') as pbar: # pbar here is progress bar
        with ThreadPoolExecutor(max_workers = max_workers) as executor:  # Spawns a thread pool using ThreadPoolExecutor to try multiple passwords concurrently.
            future_to_passwords = {executor.submit(try_password,pdf_file, pwd): pwd for pwd in passwords}  # password is assigned to task to threads.
# max_workers=4 means up to 4 passwords are tested in parallel.
            for future in tqdm(future_to_passwords, total=total_passwords):
                if future.result():
                    return future.result()
                pbar.update(1)

# stops once thread finds the correct password.
    print('Unable to decrypt PDF. Password is not found.')
    return None

# Taking arguments from the users

if __name__ == '__main__':


# This lets user run the script flexibly from the terminal
    parser = argparse.ArgumentParser(description = "Decrypt a passoword-protected PDF file.")
    parser.add_argument('pdf_file', help='Path to the password-protected PDF file.')
    parser.add_argument('-w', '--wordlist', help='Path to the passwords list file.', default = None)
    parser.add_argument('-g', '--generate', action='store_true', help='Generate passwords on the fly')
    parser.add_argument('-min','--min_length', type=int, help='Minimum length of password to generate', default=1)
    parser.add_argument('-max','--max_length', type=int, help='Maximum length of password to generate', default=3)
    parser.add_argument('-c','--charset', type=str, help='Characters to use for passwords generation', default=string.ascii_letters + string.digits + string.punctuation)
    parser.add_argument('--max_workers', type=int, help='Maximum workers of parallel threads', default=4)

    args= parser.parse_args()

    if args.generate:
        passwords = generate_passwords(args.charset, args.min_length, args.max_length)
        total_passwords = sum(1 for _ in generate_passwords(args.charset, args.min_length, args.max_length))
    elif args.wordlist:
        passwords = load_wordlist(args.wordlist)
        total_passwords = sum(1 for _ in load_wordlist(args.wordlist))
    else:
        print("Either --wordlist must be provided or --generate must be specified.")
        exit(1)

    decrypted_password = decrypt_pdf(args.pdf_file, passwords, total_passwords, args.max_workers)

    if decrypted_password:
        print(f"PDF decrypted successfully with the password: {decrypted_password}")
    else:
        print("Unable to decrypt PDF. Password not found")

