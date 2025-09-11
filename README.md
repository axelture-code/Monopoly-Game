# Monopoly Game for Raspberry Pi

This project implements a physical Monopoly board game assistant using Raspberry Pi devices. It doesn't digitize the board itself, but provides a colorful, engaging digital controller to manage player turns, dice rolls, and track player positions and money.

## Structure

- `server/`: Game logic and state management
  - `server.py`: Runs the game logic, keeps track of players, money, positions
  - `game_state.py`: Data model for the players and game state

- `client/`: Client-side code for player interactions
  - `client.py`: Connects to server, acts as "tablet" controller
  - `ui.py`: Handles display (LCD or mocked window) using Pygame

- `common/`: Shared code between server and clients
  - `messages.py`: Defines message formats (e.g. JSON schema)

## Prerequisites

Before running the game, you need to install the required dependencies:

```
pip install pygame
```

## Setup

1. Set up two Raspberry Pis on the same network.
2. On the first Raspberry Pi, run the server:
   ```
   python -m server.server
   ```
3. On the second Raspberry Pi (or a development machine), run the client:
   ```
   python -m client.client
   ```
4. In the client UI, enter the IP address of the server and connect.
5. Add players, set up the game, and start playing!

## Usage

1. Use the game setup screen to connect to the server and add players.
2. Click "Start Game" to begin.
3. On each player's turn:
   - Click "Roll Dice" to roll the dice (with animation)
   - Move the physical token on the board according to the roll
   - Perform any actions based on the space landed on
   - Click "End Turn" when done

The game controller keeps track of:
- Current player's turn
- Dice rolls (with visual dice)
- Player positions
- Player money

All physical game actions (moving tokens, buying properties, paying rent) are performed by the players on the physical board. The controller just helps manage the game flow.
