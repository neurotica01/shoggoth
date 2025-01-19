import uuid


class CardBase:
    def __init__(self, name, cost, description, requires_target=True, **kwargs):
        self.id = uuid.uuid4()
        self.name = name
        self.cost = cost
        self.description = description
        self.requires_target = requires_target
    async def on_play(self, state, being, target):
        """Default no-op (override in subclass)."""
        pass
    async def on_discard(self, state, being, target):
        """Default no-op (override in subclass)."""
        pass
    def __str__(self):
        return f"{self.name} ({self.cost} energy): {self.description}"
