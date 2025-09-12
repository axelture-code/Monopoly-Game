"""
Screen implementations for the Monopoly game UI.
Each screen handles a different part of the game flow.
"""
import pygame
import random
import math
from typing import Dict, List, Any, Optional

from client.ui.theme import COLORS, PLAYER_COLORS
from client.ui.components import HorrorButton, TextInput, PlayerCard, DiceDisplay
from client.ui.effects import BloodTitle, HauntedSkyline, SlowCobweb

class Screen:
    """Base class for all screens."""
    
    def __init__(self, ui):
        self.ui = ui
        self.width = ui.width
        self.height = ui.height
        self.elements = {}
    
    def handle_event(self, event):
        """Handle pygame events."""
        pass
    
    def update(self):
        """Update screen elements."""
        pass
    
    def draw(self, surface):
        """Draw the screen on the given surface."""
        pass


class LandingScreen(Screen):
    """Landing screen with title and start button."""
    
    def __init__(self, ui):
        super().__init__(ui)
        self._create_elements()
        
        # Create background elements
        self.skyline = HauntedSkyline(self.width, self.height)
        
        # Create slow cobwebs in corners
        self.cobwebs = [
            SlowCobweb(0, 0, 100, 'tl'),  # Top left
            SlowCobweb(self.width, 0, 100, 'tr'),  # Top right
            SlowCobweb(0, self.height, 100, 'bl'),  # Bottom left
            SlowCobweb(self.width, self.height, 100, 'br')  # Bottom right
        ]
    
    def _create_elements(self):
        """Create UI elements for the landing screen."""
        # Title with blood dripping effect - with larger font size
        self.elements["title"] = BloodTitle(
            self.width // 2, 
            self.height // 3,
            "REAL ESTATE MASSACRE",
            font_size=64,  # Increased from 54
            multiline=True  # Enable multiline
        )
        
        # Start button to go to setup page
        self.elements["start_button"] = HorrorButton(
            self.width // 2 - 100,
            self.height * 2 // 3,
            200, 60, 
            "START",
            font_size=36,
            action=lambda: self.ui.change_screen("setup")
        )
    
    def handle_event(self, event):
        """Handle pygame events."""
        # Handle mouse position for button hover
        if event.type == pygame.MOUSEMOTION:
            if "start_button" in self.elements:
                self.elements["start_button"].check_hover(event.pos)
        
        # Handle button clicks
        if event.type == pygame.MOUSEBUTTONDOWN:
            if "start_button" in self.elements:
                self.elements["start_button"].handle_event(event)
    
    def update(self):
        """Update screen elements."""
        # Update blood title animation
        if "title" in self.elements:
            self.elements["title"].update()
            
        # Update button animation
        if "start_button" in self.elements:
            self.elements["start_button"].update()
            
        # Update background
        self.skyline.update()
        
        # Update cobwebs
        for cobweb in self.cobwebs:
            cobweb.update()
    
    def draw(self, surface):
        """Draw the screen on the given surface."""
        # Draw the haunted skyline background
        self.skyline.draw(surface)
        
        # Draw cobwebs in corners
        for cobweb in self.cobwebs:
            cobweb.draw(surface)
        
        # Draw the title with blood dripping effect
        if "title" in self.elements:
            self.elements["title"].draw(surface)
        
        # Draw the start button
        if "start_button" in self.elements:
            self.elements["start_button"].draw(surface)


class SetupScreen(Screen):
    """Game setup screen for server connection and player setup."""
    
    def __init__(self, ui):
        super().__init__(ui)
        self.player_count = 2
        self.player_text_inputs = []
        self._create_elements()
    
    def _create_elements(self):
        """Create UI elements for the setup screen."""
        # Server connection
        self.elements["server_ip"] = TextInput(
            250, 50, 300, 40, 
            placeholder="Server IP (e.g. 192.168.1.100)",
            text=self.ui.server_ip
        )
        
        self.elements["connect_button"] = HorrorButton(
            560, 50, 140, 40, "Connect", 
            action=lambda: self.ui.connect_to_server(self.elements["server_ip"].text)
        )
        
        # Player count selector
        self.elements["player_minus"] = HorrorButton(
            250, 120, 40, 40, "-", 
            action=lambda: self._change_player_count(-1)
        )
        
        self.elements["player_plus"] = HorrorButton(
            370, 120, 40, 40, "+", 
            action=lambda: self._change_player_count(1)
        )
        
        # Player name inputs
        self.player_text_inputs = []
        for i in range(6):
            y_pos = 180 + i * 50
            text_input = TextInput(
                250, y_pos, 300, 40,
                placeholder=f"Player {i+1} Name",
                text=self.ui.player_names[i] if i < len(self.ui.player_names) else ""
            )
            self.player_text_inputs.append(text_input)
            self.elements[f"player_{i+1}_input"] = text_input
        
        # Start game button
        self.elements["start_game"] = HorrorButton(
            300, 500, 200, 50, "Start Game",
            font_size=24, action=self._start_game,
            disabled=not self.ui.client.is_connected
        )
    
    def _change_player_count(self, change):
        """Change the number of players."""
        new_count = self.player_count + change
        if 2 <= new_count <= 6:
            self.player_count = new_count
    
    def _start_game(self):
        """Start the game with the current player configuration."""
        # Get player names from input fields
        player_names = [input_field.text for input_field in self.player_text_inputs[:self.player_count]]
        
        # Pass to UI to handle the game start
        self.ui.start_game(player_names)
    
    def on_connect_success(self):
        """Called when connection to server is successful."""
        if "start_game" in self.elements:
            self.elements["start_game"].disabled = False
    
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
        
        # Handle text inputs
        if "server_ip" in self.elements:
            self.elements["server_ip"].handle_event(event)
            
        # Only handle active player text inputs
        for i in range(self.player_count):
            if i < len(self.player_text_inputs):
                self.player_text_inputs[i].handle_event(event)
    
    def update(self):
        """Update screen elements."""
        # Update buttons
        for key, element in self.elements.items():
            if isinstance(element, HorrorButton):
                element.update()
    
    def draw(self, surface):
        """Draw the setup screen."""
        # Fill with darker background
        pygame.draw.rect(surface, COLORS["shadow"], pygame.Rect(0, 0, self.width, self.height))
        
        # Draw page title
        title_font = pygame.font.SysFont("Arial", 32, bold=True)
        title_text = title_font.render("PREPARE THE VICTIMS", True, COLORS["fresh_blood"])
        title_rect = title_text.get_rect(center=(self.width//2, 20))
        surface.blit(title_text, title_rect)
        
        # Draw server connection section
        server_font = pygame.font.SysFont("Arial", 18)
        server_text = server_font.render("Server IP:", True, COLORS["bone"])
        surface.blit(server_text, (100, 60))
        
        # Draw server IP input
        if "server_ip" in self.elements:
            self.elements["server_ip"].draw(surface)
        
        # Draw connect button
        if "connect_button" in self.elements:
            self.elements["connect_button"].draw(surface)
        
        # Draw player count section
        player_count_font = pygame.font.SysFont("Arial", 18)
        player_count_text = player_count_font.render("Number of Players:", True, COLORS["bone"])
        surface.blit(player_count_text, (100, 130))
        
        # Draw player count controls
        if "player_minus" in self.elements:
            self.elements["player_minus"].draw(surface)
        
        count_font = pygame.font.SysFont("Arial", 24, bold=True)
        count_text = count_font.render(str(self.player_count), True, COLORS["bone"])
        count_rect = count_text.get_rect(center=(320, 140))
        surface.blit(count_text, count_rect)
        
        if "player_plus" in self.elements:
            self.elements["player_plus"].draw(surface)
        
        # Draw player name inputs
        name_font = pygame.font.SysFont("Arial", 18)
        for i in range(self.player_count):
            name_text = name_font.render(f"Player {i+1} Name:", True, COLORS["bone"])
            surface.blit(name_text, (100, 190 + i * 50))
            
            # Draw colored indicator
            color_rect = pygame.Rect(230, 190 + i * 50, 15, 15)
            pygame.draw.rect(surface, PLAYER_COLORS[i], color_rect)
            
            if i < len(self.player_text_inputs):
                self.player_text_inputs[i].draw(surface)
        
        # Draw start game button
        if "start_game" in self.elements:
            self.elements["start_game"].draw(surface)
        
        # Draw connection status
        conn_status = "Connected" if self.ui.client.is_connected else "Not Connected"
        conn_color = COLORS["toxic_green"] if self.ui.client.is_connected else COLORS["fresh_blood"]
        conn_font = pygame.font.SysFont("Arial", 16)
        conn_text = conn_font.render(f"Status: {conn_status}", True, conn_color)
        surface.blit(conn_text, (10, self.height - 60))


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

__all__ = ['Screen', 'LandingScreen', 'SetupScreen', 'GameScreen']
