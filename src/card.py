from random import shuffle
from state import Being

class CardBase:
    def __init__(self, name, cost, description, requires_target=True, **kwargs):
        self.name = name
        self.cost = cost
        self.description = description
        self.requires_target = requires_target
    def on_play(self, state, being, target):
        """Default no-op (override in subclass)."""
        pass


def user_select_card_in_deck(game_state) -> CardBase:
    """
    Displays the cards in the player's deck, asks for user input,
    and returns the chosen card (or None on invalid).
    """
    deck = game_state.player.deck
    if not deck:
        print("No cards in deck!")
        return None
    
    print("\nCards in deck:")
    for i, card in enumerate(deck):
        print(f"[{i}] {card.name} ({card.cost}): {card.description}")

    while True:
        choice_str = input("Pick a card by index:")

        if choice_str.isdigit():
            choice = int(choice_str)
            if 0 <= choice < len(deck):
                return deck.pop(choice)

def user_select_card_in_hand(game_state) -> CardBase:
    """
    Displays the cards in the player's hand, asks for user input,
    and returns the chosen card (or None on invalid).
    """

    hand = game_state.player.hand
    if not hand:
        print("No cards in hand!")
        return None

    print("\nCards in hand:")
    for i, card in enumerate(hand):
        print(f"[{i}] {card.name} ({card.cost}): {card.description}")

    while True:
        choice_str = input("Pick a card by index:")
        
        if choice_str.isdigit():
            choice = int(choice_str)
            if 0 <= choice < len(hand):
                return hand.pop(choice)
            
def user_select_target(game_state) -> Being:
    """
    Displays the enemies, asks for user input,
    and returns the chosen enemy (or None on invalid).
    """
    for b in game_state.beings:
        print(f"[{b.name}] {b.hp} HP")

    while True:
        choice_str = input("Pick an target by index:")
        
        if choice_str.isdigit():
            choice = int(choice_str)
            if 0 <= choice < len(game_state.beings):
                return game_state.beings[choice]


class BasicAttack(CardBase):
    def __init__(self):
        super().__init__("Basic Attack", 1, "Deal 5 damage to an enemy.")

    def on_play(self, state, being, target):
        state.deal_damage(source=being, target=target, amount=5)

class BasicBlock(CardBase):
    def __init__(self):
        super().__init__("Basic Block", 1, "Gain 5 block.")

    def on_play(self, game_state, being, target ):
        being.block += self.block

class BasicHeal(CardBase):
    def __init__(self):
        super().__init__("Basic Heal", 1, "Heal 3 health.")

    def on_play(self, game_state, player, target ):
        player.hp += 3

class BasicDraw(CardBase):
    def __init__(self):
        super().__init__("Basic Draw", 1, "Draw 1 card.", requires_target=False)

    def on_play(self, game_state, player, target ):
        player.draw(1)

def default_deck():
    deck = []
    for _ in range(5):
        deck.append(BasicAttack())
    for _ in range(4):
        deck.append(BasicBlock())
    for _ in range(2):
        deck.append(BasicHeal())
        deck.append(BasicDraw())

    shuffle(deck)
    return deck