"""
Message definitions for communication between server and clients.
These define the protocol for the Monopoly game.
"""
import json
from enum import Enum, auto
from typing import Dict, List, Optional, Any, Union

class MessageType(Enum):
    """Types of messages that can be sent between server and client."""
    CONNECT = auto()           # Client connecting to server
    DISCONNECT = auto()        # Client disconnecting
    GAME_STATE = auto()        # Full game state update
    PLAYER_ACTION = auto()     # Player making a move/action
    DICE_ROLL = auto()         # Dice roll result
    PROPERTY_TRANSACTION = auto()  # Buying/selling properties
    PLAYER_STATUS = auto()     # Player money/position update
    GAME_EVENT = auto()        # Game events (cards, etc.)
    ERROR = auto()             # Error message

class Message:
    """Base class for all messages in the game."""
    
    def __init__(self, msg_type: MessageType, data: Dict[str, Any] = None):
        self.type = msg_type
        self.data = data or {}
    
    def to_json(self) -> str:
        """Convert message to JSON string."""
        message_dict = {
            "type": self.type.name,
            "data": self.data
        }
        return json.dumps(message_dict)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'Message':
        """Create a Message object from JSON string."""
        try:
            message_dict = json.loads(json_str)
            msg_type = MessageType[message_dict["type"]]
            return cls(msg_type, message_dict["data"])
        except (json.JSONDecodeError, KeyError) as e:
            return cls(MessageType.ERROR, {"error": f"Invalid message format: {str(e)}"})

# Specific message classes for different types
class ConnectMessage(Message):
    """Message sent when a client connects to the server."""
    def __init__(self, player_name: str):
        super().__init__(MessageType.CONNECT, {"player_name": player_name})

class DisconnectMessage(Message):
    """Message sent when a client disconnects from the server."""
    def __init__(self, player_id: str):
        super().__init__(MessageType.DISCONNECT, {"player_id": player_id})

class DiceRollMessage(Message):
    """Message containing dice roll results."""
    def __init__(self, player_id: str, values: List[int], is_doubles: bool = False):
        super().__init__(MessageType.DICE_ROLL, {
            "player_id": player_id,
            "values": values,
            "is_doubles": is_doubles
        })

class PlayerActionMessage(Message):
    """Message for player actions like buying property, paying rent, etc."""
    def __init__(self, player_id: str, action: str, action_data: Dict[str, Any] = None):
        super().__init__(MessageType.PLAYER_ACTION, {
            "player_id": player_id,
            "action": action,
            "action_data": action_data or {}
        })

class GameStateMessage(Message):
    """Message containing the full game state."""
    def __init__(self, game_state: Dict[str, Any]):
        super().__init__(MessageType.GAME_STATE, game_state)