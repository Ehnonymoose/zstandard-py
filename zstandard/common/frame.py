from common.frame_header import FrameHeader
from common.block import Block
from typing import Optional
from util import prindent, stringify

class Frame:
    def __init__(self, data: bytes, offset: int = 0) -> None:
        # Every frame must start with the correct magic number
        assert data[offset:offset + 4] == b'\x28\xB5\x2F\xFD', f'bad magic number at offset {offset}'
        offset += 4

        self._header = FrameHeader(data, offset)
        offset += self._header.size()

        block = Block.from_bytes(data, offset)
        self._data_blocks = [ block ]
        offset += block.size()

        while not block.is_last:
            block = Block.from_bytes(data, offset)
            self._data_blocks.append(block)
            offset += block.size()

        if self._header._descriptor.content_checksum_flag:
            self.checksum = data[offset:offset + 4]
        else:
            self.checksum = None


    def size(self) -> int:
        # Magic number + header + data blocks + checksum (if present)
        return 4 +                                                \
               self._header.size() +                              \
               sum(block.size() for block in self._data_blocks) + \
               (4 if self.checksum else 0)

    def print(self, indent=0) -> None:
        prindent(indent, 'Frame {')
        self._header.print(indent + 1)

        for block in self._data_blocks:
            block.print(indent + 1)
        
        if self._header._descriptor.content_checksum_flag:
            prindent(indent + 1, f'Checksum = {stringify(self.checksum)}')
        
        prindent(indent, '}')
        
