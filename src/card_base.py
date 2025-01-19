class CardBase:
    def __init__(self, name, cost, description, requires_target=True, **kwargs):
        self.name = name
        self.cost = cost
        self.description = description
        self.requires_target = requires_target
    async def on_play(self, state, being, target):
        """Default no-op (override in subclass)."""
        pass