"""Game screen for the Monopoly game."""

import pygame
from typing import Dict, Any
from client.ui.screens.base import Screen
from client.ui.theme import COLORS, PLAYER_COLORS
from client.ui.components import HorrorButton, PlayerCard, DiceDisplay

class GameScreen(Screen):
    """Main game screen showing the game state and controls."""
    
    def __init__(self, ui):
        super().__init__(ui)
        self.player_cards = {}
        self._create_elements()
    
    def _create_elements(self):
        """Create UI elements for the game screen."""
        # Dice display
        self.elements["dice"] = DiceDisplay(350, 50)
        
        # Game control buttons
        self.elements["roll_dice"] = HorrorButton(
            250, 150, 150, 50, "Roll Dice",
            action=self._roll_dice
        )
        
        self.elements["end_turn"] = HorrorButton(
            420, 150, 150, 50, "End Turn",
            action=self._end_turn
        )
        
        # Back to setup button
        self.elements["back"] = HorrorButton(
            30, 30, 100, 40, "Back",
            action=lambda: self.ui.change_screen("setup")
        )
    
    def _roll_dice(self):
        """Roll the dice for the current player."""
        if not self.ui.game_started:
            self.ui.status_message = "Game not started"
            return
            
        self.ui.client.roll_dice()
        self.ui.status_message = "Rolling dice..."
        if "dice" in self.elements:
            self.elements["dice"].start_roll()
    
    def _end_turn(self):
        """End the current player's turn."""
        if not self.ui.game_started:
            self.ui.status_message = "Game not started"
            return
            
        self.ui.client.end_turn()
        self.ui.status_message = "Ending turn..."
    
    def handle_event(self, event):
        """Handle pygame events."""
        # Handle mouse position for button hover
        if event.type == pygame.MOUSEMOTION:
            for key, element in self.elements.items():
                if isinstance(element, HorrorButton):
                    element.check_hover(event.pos)
        
        # Handle button clicks
        if event.type == pygame.MOUSEBUTTONDOWN:
            for key, element in self.elements.items():
                if isinstance(element, HorrorButton):
                    element.handle_event(event)
    
    def update(self):
        """Update screen elements."""
        # Update dice animation
        if "dice" in self.elements:
            self.elements["dice"].update()
        
        # Update buttons
        for key, element in self.elements.items():
            if isinstance(element, HorrorButton):
                element.update()
                
        # Update player cards
        for card in self.player_cards.values():
            card.update()
    
    def draw(self, surface):
        """Draw the game screen."""
        # Fill with darker background
        pygame.draw.rect(surface, COLORS["shadow"], pygame.Rect(0, 0, self.width, self.height))
        
        # Draw page title
        title_font = pygame.font.SysFont("Arial", 32, bold=True)
        title_text = title_font.render("THE DEADLY GAME", True, COLORS["fresh_blood"])
        title_rect = title_text.get_rect(center=(self.width//2, 20))
        surface.blit(title_text, title_rect)
        
        # Draw back button
        if "back" in self.elements:
            self.elements["back"].draw(surface)
        
        # Draw dice
        if "dice" in self.elements:
            self.elements["dice"].draw(surface)
        
        # Draw game control buttons
        if "roll_dice" in self.elements:
            self.elements["roll_dice"].draw(surface)
            
        if "end_turn" in self.elements:
            self.elements["end_turn"].draw(surface)
        
        # Draw player cards
        self._draw_player_cards(surface)
    
    def _draw_player_cards(self, surface):
        """Draw player information cards."""
        if not self.player_cards:
            return
            
        # Draw all player cards in a grid
        grid_positions = [
            (50, 220), (300, 220), (550, 220),
            (50, 370), (300, 370), (550, 370)
        ]
        
        for i, (player_id, card) in enumerate(self.player_cards.items()):
            if i < len(grid_positions):
                x, y = grid_positions[i]
                card.rect.x = x
                card.rect.y = y
                card.draw(surface)
    
    def update_game_state(self, game_state: Dict[str, Any]):
        """Update the screen with the new game state."""
        # Get player information
        players = game_state.get("players", {})
        
        # Create or update player cards
        for player_id, player_data in players.items():
            name = player_data.get("name", "Unknown")
            money = player_data.get("money", 0)
            position = player_data.get("position", 0)
            
            if player_id not in self.player_cards:
                # Assign a color based on player index
                color_idx = len(self.player_cards) % len(PLAYER_COLORS)
                color = PLAYER_COLORS[color_idx]
                
                # Create new player card
                self.player_cards[player_id] = PlayerCard(
                    0, 0, 200, 120, player_id, name, color
                )
            
            # Check if this is the current player
            is_current = (player_id == game_state.get("current_player_id"))
            
            # Update card info
            self.player_cards[player_id].update_player_info(money, position, is_current)
        
        # Update dice display with current roll
        dice_roll = game_state.get("dice_roll", (0, 0))
        if "dice" in self.elements and not self.elements["dice"].rolling:
            self.elements["dice"].set_values(dice_roll)
