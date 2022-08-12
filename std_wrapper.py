from io import IOBase


class OutputWrapper(IOBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.output = ""

    def write(self, data):
        self.output += str(data)
    
    def read(self):
        return self.output

class StdinWrapper(IOBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def read(self, *args):
        raise IOError("Can't read from stdin in online mode")