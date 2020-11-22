class Signal(list):

    def __init__(self, owner):
        super(Signal, self).__init__()
        self.owner = owner

    async def send(self, *args, **kwargs):
        """
        Sends data to all registered receivers.
        """
        for receiver in self:
            await receiver(*args, **kwargs)

    def freeze(self):
        pass
