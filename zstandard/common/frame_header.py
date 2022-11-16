from util import prindent

class FrameHeaderDescriptor:
    def __init__(self, value: int) -> None:
        # Decode the bitfields from the descriptor.
        self.dictionary_id_flag      = (value & 0b00000011)
        self.content_checksum_flag   = (value & 0b00000100) >> 2
        self.reserved_bit            = (value & 0b00001000) >> 3
        self.unused_bit              = (value & 0b00010000) >> 4
        self.single_segment_flag     = (value & 0b00100000) >> 5
        self.frame_content_size_flag = (value & 0b11000000) >> 6

        # Size (in bytes) of the dictionary ID in the header, if any.
        self.did_field_size = [0, 1, 2, 4][self.dictionary_id_flag]

        # Size (in bytes) of the Frame Content Size header field.
        if self.frame_content_size_flag == 0:
            # If the Single Segment Flag is set, the FCS field is always
            # at least one byte, even if the FCS flag is 0.
            # If neither flag is set, the FCS field is omitted.
            self.fcs_field_size = 1 if self.single_segment_flag == 1 else 0
        else:
            self.fcs_field_size = 1 << self.frame_content_size_flag

    def print(self, indent=0):
        prindent(indent, 'FrameHeaderDescriptor {')
        prindent(indent + 1, f'Frame_Content_Size_Flag = {self.frame_content_size_flag} [fcs_field_size = {self.fcs_field_size}]')
        prindent(indent + 1, f'Single_Segment_Flag     = {self.single_segment_flag}')
        prindent(indent + 1, f'Content_Checksum_Flag   = {self.content_checksum_flag}')
        prindent(indent + 1, f'Dictionary_ID_Flag      = {self.dictionary_id_flag} [did_field_size = {self.did_field_size}]')
        prindent(indent, '}')

class FrameHeader:
    def __init__(self, data: bytes, offset: int = 0) -> None:
        # The first byte is the Frame Header Descriptor, and tells us
        # which fields are present in this frame (and header).
        self._descriptor = FrameHeaderDescriptor(data[offset])

        # The reserved bit MUST be zero.
        assert self._descriptor.reserved_bit == 0, \
            f'nonzero reserved bit in frame header descriptor at offset {offset}'

        offset += 1

        # If Single_Segment_Flag *isn't* set, the next byte is a Window Descriptor
        # that encodes the Window Size.
        if not self._descriptor.single_segment_flag:
            window_size_descriptor = data[offset]
            offset += 1

            self.window_size = self._compute_window_size(window_size_descriptor)
        
        if self._descriptor.did_field_size > 0:
            did_field = data[offset:offset + self._descriptor.did_field_size]
            offset += self._descriptor.did_field_size

            self.dictionary_id = int.from_bytes(did_field, byteorder='little')
        else:
            self.dictionary_id = None

        if self._descriptor.fcs_field_size > 0:
            fcs_field = data[offset:offset + self._descriptor.fcs_field_size]
            offset += self._descriptor.fcs_field_size

            self.frame_content_size = self._compute_frame_content_size(fcs_field)
        else:
            self.frame_content_size = None
        
        # If Single_Segment_Flag *is* set, Window_Descriptor is not present, and
        # Window_Size is set to Frame_Content_Size.
        if self._descriptor.single_segment_flag:
            self.window_size = self.frame_content_size

    def _compute_window_size(self, window_size_descriptor: int) -> int:
        mantissa = (window_size_descriptor & 0b00000111)
        exponent = (window_size_descriptor & 0b11111000) >> 3

        window_log =  10 + exponent
        window_base = 1 << window_log
        window_add =  (window_base // 8) * mantissa
        return window_base + window_add

    def _compute_frame_content_size(self, fcs_field: bytes) -> int:
        if self._descriptor.fcs_field_size in (1, 4, 8):
            return int.from_bytes(fcs_field, byteorder='little')
        elif self._descriptor.fcs_field_size == 2:
            return 256 + int.from_bytes(fcs_field, byteorder='little')

    def size(self) -> int:
        # descriptor (1 byte) + three optional fields
        return 1                                                        \
               + (1 if not self._descriptor.single_segment_flag else 0) \
               + self._descriptor.did_field_size                        \
               + self._descriptor.fcs_field_size
    
    def print(self, indent=0):
        prindent(indent, 'FrameHeader {')
        self._descriptor.print(indent + 1)
        prindent(indent + 1, f'Window_Size        = {self.window_size}')

        if self.dictionary_id:
            prindent(indent + 1, f'Dictionary_ID      = {self.dictionary_id}')
        
        if self.frame_content_size:
            prindent(indent + 1, f'Frame_Content_Size = {self.frame_content_size}')
        
        prindent(indent, '}')

