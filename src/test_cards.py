import asyncio
from state import State
from being import Being, Player, Enemy
from card import *

async def mock_log(message: str, user_ack=False):
    """Mock log callback that does nothing"""
    pass

async def mock_select(message: str, options: dict, required=True):
    """Mock selection that always picks the first option"""
    if options:
        return list(options.values())[0]
    return None

async def mock_status_update():
    """Mock status bar update that does nothing"""
    pass

async def test_card(card: CardBase):
    """Test harness for a single card"""
    # Create a new game state with mock callbacks
    state = State(mock_log, mock_select, mock_status_update)
    
    print(f"\nTesting card: {card.name}")
    print(f"Initial state:")
    print(f"Player: {str(state.player)}")
    print(f"Enemy:  {str(state.enemy)}")
    
    try:
        # Play the card
        if card.requires_target:
            await card.on_play(state, state.player, state.enemy)
        else:
            await card.on_play(state, state.player, None)
            
        # Check results after card play
        print(f"\nState after card play:")
        print(f"Player: {str(state.player)}")
        print(f"Enemy:  {str(state.enemy)}")

        # Apply status effects for both beings
        for status in state.enemy.statuses:
            status.on_game_loop(state, state.enemy)
        for status in state.player.statuses:
            status.on_game_loop(state, state.player)

        print(f"\nState after status effects:")
        print(f"Player: {str(state.player)}")
        print(f"Enemy:  {str(state.enemy)}")

        # Test a basic attack to ensure status effects work properly
        test_attack = BasicAttack()
        await test_attack.on_play(state, state.player, state.enemy)

        print(f"\nFinal state after test attack:")
        print(f"Player: {str(state.player)}")
        print(f"Enemy:  {str(state.enemy)}")
        
        print("Test passed!")
        return True
        
    except Exception as e:
        print(f"Test failed with exception: {str(e)}")
        return False

async def test_all_cards():
    """Run tests for all cards"""
    cards = [
        BasicAttack(),
        BasicBlock(),
        BasicHeal(),
        BasicDraw(),
        PoisonFlask(),
        BerserkerPotion(),
        VoidEmbrace(),
        EldritchCurse(),
        BloodRitual(),
        NightmareVisions(),
        ToughShell(),
        WhispersOfMadness(),
        TemporalDistortion(),
        RealityTear(),
        ChaosEmbrace(),
        TimeLoop(),
        PurifyingLight(),
        EnergyInfusion(),
        StatusMirror(),
        TimeStop(),
        StatusThief()
    ]
    
    results = []
    for card in cards:
        result = await test_card(card)
        results.append((card.name, result))
    
    print("\nTest Summary:")
    print("-" * 40)
    for name, passed in results:
        status = "✓" if passed else "✗"
        print(f"{status} {name}")

if __name__ == "__main__":
    asyncio.run(test_all_cards()) 