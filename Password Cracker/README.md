# 🔐 Hash Cracker Tool (Python)

This is a Python-based hash cracking tool that uses either a **wordlist (dictionary attack)** or **brute-force** to crack password hashes.

## 💡 Features
- Supports multiple hash types:
  - MD5, SHA1, SHA256, SHA512, SHA3 variants
- Wordlist mode using common password lists
- Brute-force mode with customizable character set and password length
- Multithreaded for faster performance
- Command-line interface with clear arguments
- Progress bar via `tqdm`

## 🚀 Usage

### ▶️ Wordlist Mode
```bash
python Cracker.py <hash> -w wordlist.txt --hash_type sha256
