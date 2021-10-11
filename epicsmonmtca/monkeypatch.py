from pyipmi.errors import CompletionCodeError
from pyipmi.msgs.message import Message
from pyipmi.utils import ByteBuffer


def _decode(self, data):
    """Decode the bytestring message."""
    if not hasattr(self, '__fields__'):
        return

    data = ByteBuffer(data)
    cc = None
    for field in self.__fields__:
        try:
            field.decode(self, data)
        except CompletionCodeError as e:
            # stop decoding on completion code != 0
            cc = e.cc
            break


# Extra byte was found in the reply for command delete sel entry.
# This is to avoid raising an exception in that case
Message._decode = _decode
