from download import download_bills
from parsing import parse_pdf

def main():
    """Main function to download bills."""
    download_bills()
    parse_pdf()

if __name__ == "__main__":
    main()
