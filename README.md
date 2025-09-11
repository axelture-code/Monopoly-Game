# Monopoly Game for Raspberry Pi

This project implements a digital version of the Monopoly board game using Raspberry Pi devices.

## Structure

- `server/`: Game logic and state management
  - `server.py`: Runs the game logic, keeps track of board, players, money
  - `game_state.py`: Data model for the board, players, properties

- `client/`: Client-side code for player interactions
  - `client.py`: Connects to server, acts as "tablet" controller
  - `ui.py`: Handles display (LCD or mocked window)

- `common/`: Shared code between server and clients
  - `messages.py`: Defines message formats (e.g. JSON schema)

## Setup

[Instructions will be added here]

## Usage

[Instructions will be added here]
