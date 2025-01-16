class CardBase:
    def __init__(self, name, cost, description, flavor_text, **kwargs):
        self.name = name
        self.cost = cost
        self.description = description
        self.flavor_text = flavor_text
        
        # Additional optional fields
        self.damage = kwargs.get("damage", 0)
        self.heal = kwargs.get("heal", 0)
        self.special_effect = kwargs.get("special_effect", None)
    
    def on_play(self, game_state, player, targets):
        """Default no-op (override in subclass)."""
        pass