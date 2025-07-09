# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview
This is "Shoggoth", a Lovecraftian/Eldritch horror roguelike deckbuilding card game built with Python. The game features a terminal-based UI using the Textual library, AI-generated content (themes, enemies, cards) using pydantic-ai, and turn-based combat mechanics.

## Development Commands

### Running the Game
```bash
python src/shoggoth.py
```

### Running Tests
```bash
python src/test.py
```

### Installing Dependencies
```bash
pip install -r requirements.txt
```

## Core Architecture

### Game Flow
- **Entry Point**: `src/shoggoth.py` - Main Textual app with UI components
- **Game State**: `src/state.py` - Central game state management, turn logic, damage/healing systems
- **Beings**: `src/being.py` - Base classes for Player and Enemy with HP, deck, hand, status effects
- **Cards**: `src/card_base.py` and `src/card.py` - Card system with base class and concrete implementations
- **Status Effects**: `src/status.py` - Status effect system (poison, berserk, vulnerable, etc.)
- **AI Generation**: `src/agents.py` - AI agents for generating themes, enemies, and cards dynamically

### Key Components

#### UI Layer (shoggoth.py)
- Textual-based terminal interface
- Handles user input, card selection, and game display
- Manages async event handling for user acknowledgments and selections

#### Game State (state.py)
- Turn-based combat system
- Damage/healing with status effect modifiers
- Win/loss conditions
- Card playing mechanics with energy system

#### AI Content Generation (agents.py)
- Uses pydantic-ai with OpenAI models
- Generates level themes, enemy personalities, and dynamic cards
- Personality system based on Big 5 traits and Tarot arcana
- Dynamic card generation that creates new Python classes at runtime

#### Card System
- **CardBase**: Abstract base class with name, cost, description, targeting
- **Card implementations**: BasicAttack, BasicBlock, BasicHeal, etc.
- Energy-based cost system
- Target selection (self/enemy/none)

#### Status Effects System
- Base `Status` class with hooks for damage/healing modification
- Turn-based duration system
- Stackable effects (poison, confusion, frenzy)
- Modifiers for damage dealt/taken

## Key Development Patterns

### Adding New Cards
1. Inherit from `CardBase` in `src/card_base.py`
2. Implement `async def on_play(self, state, being, target)`
3. Set `requires_target=True/False` in constructor
4. Add to `default_deck()` in `src/card.py`

### Adding New Status Effects
1. Inherit from `Status` in `src/status.py`
2. Override relevant hooks: `on_deal_damage`, `on_take_damage`, `on_heal`, `on_game_loop`
3. Implement `__add__` method for stacking behavior

### AI Agent Customization
- Modify system prompts in `src/agents.py` 
- Agents use OpenAI models (o4-mini, gpt-4o)
- Temperature settings control creativity vs consistency

## Dependencies
- **langchain**: AI framework integration
- **openai**: OpenAI API client
- **textual**: Terminal UI framework
- **pydantic-ai**: AI agent framework with type safety

## File Structure
```
src/
├── shoggoth.py      # Main Textual app
├── state.py         # Game state and turn logic
├── being.py         # Player/Enemy base classes
├── card_base.py     # Abstract card class
├── card.py          # Concrete card implementations
├── status.py        # Status effect system
├── agents.py        # AI content generation
├── mechanics.py     # (Unused mechanic system)
├── test.py          # Test runner
└── test_cards.py    # Card tests
```

## Development Notes
- The game uses async/await patterns throughout for UI responsiveness
- Status effects use functional programming patterns with reduce() for modifier chains
- AI-generated cards are created by exec()ing dynamically generated Python code
- The game supports both player and AI decision-making through the same interface