class FastTextModelNotFoundException(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class CommandNotFound(Exception):
    def __init__(self, message):
        self.message = "dateparser-download: {}".format(message)
        super().__init__(self.message)
