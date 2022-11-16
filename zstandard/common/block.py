from enum import Enum
from util import prindent, stringify

class BlockType(Enum):
    RAW = 0
    RLE = 1
    COMPRESSED = 2
    RESERVED = 3

class Block:
    # TODO: declare instance variables


    @staticmethod
    def from_bytes(data: bytes, offset: int):
        block = Block()

        # The first three bytes comprise the Block Header.
        block_header_bytes = data[offset:offset + 3]
        offset += 3

        block_header = int.from_bytes(block_header_bytes, byteorder='little')

        # The lowest-order bit is set if this is the last block.
        block.is_last = True if block_header & 0b1 else False

        # The next two bits represent the block type.
        block_type_bits = (block_header & 0b110) >> 1
        block.type = BlockType(block_type_bits)

        # Decoders are required to reject blocks of type RESERVED
        assert block.type is not BlockType.RESERVED, 'reserved blocks are not allowed'

        # The remaining 21 bits represent a data size of some type.
        #
        # For Raw and Compressed blocks, this is just the number of
        # bytes of data in the block.
        #
        # RLE blocks always contain only a single byte; the data size
        # represents the number of times that byte should be repeated
        # when the block is decompressed.
        block.data_size = block_header >> 3

        # Read in the block data. Again, this differs depending on block type.
        if block.type is BlockType.RLE:
            block.data = data[offset:offset + 1]
        else:
            block.data = data[offset:offset + block.data_size]
        
        return block

    def size(self) -> int:
        if self.type is BlockType.RLE:
            # 3 bytes of header, one byte of content.
            return 4
        else:
            # 3 bytes of header, data_size bytes of content
            return 3 + self.data_size
    
    def print(self, indent=0) -> None:
        prindent(indent, 'Block {')
        prindent(indent + 1, f'Type  = {self.type.name}')

        # As ever, handle RLE blocks differently.
        if self.type is BlockType.RLE:
            prindent(indent + 1, f'Count = {self.data_size}')
            prindent(indent + 1, f'Value = {stringify(self.data)}')
        else:
            prindent(indent + 1, f'Size  = {self.data_size}')
            prindent(indent + 1, f'Data  = {stringify(self.data)}')

        if self.is_last:
            prindent(indent + 1, f'Last  = {self.is_last}')

        prindent(indent, '}')