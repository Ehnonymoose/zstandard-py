import argparse
import os.path
from decompress.decompressor import decompress

def main():
    parser = argparse.ArgumentParser(prog = 'python -m zstandard')
    parser.add_argument('file')

    # TODO: arguments for compressing/decompressing, output, verbosity, etc.

    args = parser.parse_args()
    
    if not os.path.isfile(args.file):
        # TODO: put together proper exceptions
        raise Exception(f'file not found: {file}')
    
    with open(args.file, 'rb') as f:
        compressed = f.read()
    
    decompressed = decompress(compressed)

if __name__ == '__main__':
    main()