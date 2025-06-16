import PyPDF2  # Python library used to manipulate PDF files — read, merge, split, rotate, encrypt, etc.
import  sys  # This is a built-in Python module that lets you access command-line arguments, among other system-level operations.
from PyPDF2.errors import PdfReadError

def create_password_protected_pdf(input_pdf, output_pdf, password):
    try:
        with open(input_pdf, 'rb') as pdf_file:  # file is opened in read-binary mode
            pdf_reader = PyPDF2.PdfReader(pdf_file)  # Reads the PDF file and loads all its pages and metadata.
            pdf_writer = PyPDF2.PdfWriter()

            for page_num in range(len(pdf_reader.pages)):
                pdf_writer.add_page(pdf_reader.pages[page_num]) # Adds each page from the original PDF to the new writer object.

            pdf_writer.encrypt(password)  # A user password is applied here and the output file will require the password to be opened.

            with open(output_pdf, 'wb') as output_file: # Opens a new file in write-binary mode.
                pdf_writer.write(output_file) # Writes the encrypted pages to disk.

            print(f"Password-protected PDF saved as {output_pdf}")

    except FileNotFoundError:
        print(f"The file {input_pdf} was not found.")
    except PdfReadError:  # Triggered if the file isn’t a valid or readable PDF
        print(f"The file {input_pdf} is not a valid PDF file.")
    except Exception as e:
        print(f"Error: {e}")


def main():
    if len(sys.argv) != 4:  # A list containing command-line arguments.
        print("usage: python3 script.py <input_pdf> <output_pdf> <password>")
        sys.exit(1)


    input_pdf = sys.argv[1]
    output_pdf = sys.argv[2]
    password = sys.argv[3]


    create_password_protected_pdf(input_pdf, output_pdf, password)

if __name__ == "__main__":
    main()
