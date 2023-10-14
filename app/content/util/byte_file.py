class ByteFile:
    def __init__(self, data, content_type, size, name):
        self.data = data
        self.content_type = content_type
        self.size = size
        self.name = name

    def __call__(self):
        return self.data
