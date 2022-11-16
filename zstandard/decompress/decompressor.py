from common.frame import Frame

# Convenience function for accessing decompression
def decompress(data: bytes) -> bytes:
    decompressor = ZstandardDecompressor()
    return decompressor.decompress(data)


class ZstandardDecompressor:
    def decompress(self, data: bytes) -> bytes:
        # Zstandard-compressed files consist of a series of frames.
        # The decompressed file is the concatenation of the decompressed frames.
        frames = []
        offset = 0

        while offset < len(data):
            frame = Frame(data, offset=offset)
            frame.print()

            frames.append(frame)
            offset += frame.size()

        return b''

