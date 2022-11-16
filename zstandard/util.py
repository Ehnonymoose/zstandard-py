from binascii import hexlify

def prindent(indent: int, string: str) -> None:
    print('  ' * indent + string)

def is_ascii(s: str):
    return all(ord(c) < 128 for c in s)

def stringify(b: bytes, max_len: int = 20) -> str:
    # Trim the bytes so we're not trying to print too much.
    if len(b) > max_len:
        b = b[:max_len]
        dots = '...'
    else:
        dots = ''

    # Always convert the bytes to hex for display
    result = hexlify(b).decode('ascii') + dots

    # If the bytes are all ASCII, annotate the result with that string too.
    if all(c < 128 for c in b):
        ascii_str = b.decode('ascii')
        result += f'    [{repr(ascii_str) + dots}]'
    
    return result
