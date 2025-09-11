"""
Game state module for Monopoly game.
Contains data models for the board, players, properties, etc.
"""
from typing import Dict, List, Optional, Tuple
from enum import Enum

class PropertyGroup(Enum):
    """Color groups for properties."""
    BROWN = "brown"
    LIGHT_BLUE = "light_blue"
    PINK = "pink"
    ORANGE = "orange"
    RED = "red"
    YELLOW = "yellow"
    GREEN = "green"
    DARK_BLUE = "dark_blue"
    RAILROAD = "railroad"
    UTILITY = "utility"

class Property:
    """Represents a property on the Monopoly board."""
    
    def __init__(self, id: int, name: str, price: int, group: PropertyGroup,
                 rent_values: List[int], mortgage_value: int):
        self.id = id
        self.name = name
        self.price = price
        self.group = group
        self.rent_values = rent_values  # [base, 1 house, 2 houses, 3 houses, 4 houses, hotel]
        self.mortgage_value = mortgage_value
        self.owner_id: Optional[str] = None
        self.is_mortgaged: bool = False
        self.houses: int = 0
        self.has_hotel: bool = False
    
    def get_rent(self) -> int:
        """Calculate rent based on development level."""
        if self.is_mortgaged:
            return 0
            
        if self.houses == 0 and not self.has_hotel:
            return self.rent_values[0]
        elif self.has_hotel:
            return self.rent_values[5]
        else:
            return self.rent_values[self.houses]
    
    def to_dict(self) -> Dict:
        """Convert property to dictionary for serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "price": self.price,
            "group": self.group.value,
            "rent_values": self.rent_values,
            "mortgage_value": self.mortgage_value,
            "owner_id": self.owner_id,
            "is_mortgaged": self.is_mortgaged,
            "houses": self.houses,
            "has_hotel": self.has_hotel
        }

class Player:
    """Represents a player in the Monopoly game."""
    
    def __init__(self, id: str, name: str):
        self.id = id
        self.name = name
        self.position = 0  # Board position (0-39)
        self.money = 1500  # Starting money
        self.owned_properties: List[int] = []  # List of property IDs
        self.is_in_jail = False
        self.jail_turns = 0
        self.get_out_of_jail_cards = 0
    
    def to_dict(self) -> Dict:
        """Convert player to dictionary for serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "position": self.position,
            "money": self.money,
            "owned_properties": self.owned_properties,
            "is_in_jail": self.is_in_jail,
            "jail_turns": self.jail_turns,
            "get_out_of_jail_cards": self.get_out_of_jail_cards
        }

class BoardSpace(Enum):
    """Types of spaces on the Monopoly board."""
    PROPERTY = "property"
    CHANCE = "chance"
    COMMUNITY_CHEST = "community_chest"
    TAX = "tax"
    GO = "go"
    JAIL = "jail"
    FREE_PARKING = "free_parking"
    GO_TO_JAIL = "go_to_jail"

class Board:
    """Represents the Monopoly game board."""
    
    def __init__(self):
        # Initialize the 40 spaces on the board
        self.spaces: List[Dict] = self._create_board_spaces()
        self.properties: Dict[int, Property] = self._create_properties()
    
    def _create_board_spaces(self) -> List[Dict]:
        """Create the board spaces structure."""
        # This would contain all 40 spaces on the board with their types and properties
        spaces = []
        # Example of first few spaces
        spaces.append({"type": BoardSpace.GO, "name": "GO", "position": 0})
        spaces.append({"type": BoardSpace.PROPERTY, "property_id": 1, "position": 1})
        spaces.append({"type": BoardSpace.COMMUNITY_CHEST, "name": "Community Chest", "position": 2})
        spaces.append({"type": BoardSpace.PROPERTY, "property_id": 2, "position": 3})
        spaces.append({"type": BoardSpace.TAX, "name": "Income Tax", "amount": 200, "position": 4})
        # ... more spaces would be defined here
        
        # This is just a placeholder - you'd need to define all 40 spaces
        return spaces
    
    def _create_properties(self) -> Dict[int, Property]:
        """Create all properties on the board."""
        properties = {}
        
        # Just a few examples of properties - you'd need to define them all
        properties[1] = Property(
            id=1,
            name="Mediterranean Avenue",
            price=60,
            group=PropertyGroup.BROWN,
            rent_values=[2, 10, 30, 90, 160, 250],
            mortgage_value=30
        )
        
        properties[2] = Property(
            id=2,
            name="Baltic Avenue",
            price=60,
            group=PropertyGroup.BROWN,
            rent_values=[4, 20, 60, 180, 320, 450],
            mortgage_value=30
        )
        
        # ... more properties would be defined here
        
        return properties
    
    def to_dict(self) -> Dict:
        """Convert board to dictionary for serialization."""
        return {
            "spaces": self.spaces,
            "properties": {id: prop.to_dict() for id, prop in self.properties.items()}
        }

class GameState:
    """Represents the complete state of a Monopoly game."""
    
    def __init__(self):
        self.board = Board()
        self.players: Dict[str, Player] = {}
        self.current_player_id: Optional[str] = None
        self.dice_roll: Tuple[int, int] = (0, 0)
        self.game_phase = "waiting_for_players"  # waiting_for_players, playing, game_over
        self.turn_number = 0
    
    def add_player(self, player_id: str, player_name: str) -> Player:
        """Add a new player to the game."""
        player = Player(player_id, player_name)
        self.players[player_id] = player
        
        # If this is the first player, make them the current player
        if not self.current_player_id and self.game_phase == "waiting_for_players":
            self.current_player_id = player_id
            self.game_phase = "playing"
            
        return player
    
    def remove_player(self, player_id: str) -> bool:
        """Remove a player from the game."""
        if player_id in self.players:
            del self.players[player_id]
            
            # If the current player was removed, move to the next player
            if player_id == self.current_player_id:
                self._advance_to_next_player()
            
            # If no players left, reset game state
            if not self.players:
                self.game_phase = "waiting_for_players"
                self.current_player_id = None
                self.turn_number = 0
                
            return True
        return False
    
    def _advance_to_next_player(self):
        """Move to the next player in turn order."""
        player_ids = list(self.players.keys())
        if not player_ids:
            self.current_player_id = None
            return
            
        if self.current_player_id in player_ids:
            current_idx = player_ids.index(self.current_player_id)
            next_idx = (current_idx + 1) % len(player_ids)
        else:
            next_idx = 0
            
        self.current_player_id = player_ids[next_idx]
    
    def move_player(self, player_id: str, steps: int) -> int:
        """Move a player a number of steps and return the new position."""
        if player_id not in self.players:
            return -1
            
        player = self.players[player_id]
        old_position = player.position
        player.position = (player.position + steps) % 40
        
        # Check if player passed GO
        if player.position < old_position:
            player.money += 200  # $200 for passing GO
            
        return player.position
    
    def roll_dice(self) -> Tuple[int, int]:
        """Roll dice for the current player."""
        import random
        dice1 = random.randint(1, 6)
        dice2 = random.randint(1, 6)
        self.dice_roll = (dice1, dice2)
        return self.dice_roll
    
    def to_dict(self) -> Dict:
        """Convert game state to dictionary for serialization."""
        return {
            "board": self.board.to_dict(),
            "players": {id: player.to_dict() for id, player in self.players.items()},
            "current_player_id": self.current_player_id,
            "dice_roll": self.dice_roll,
            "game_phase": self.game_phase,
            "turn_number": self.turn_number
        }