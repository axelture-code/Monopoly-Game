"""
UI implementation for Monopoly game client.
Handles display (LCD screen or mocked window) and user input.
This is for a physical board game with an LCD control panel.
Uses Pygame for a colorful, game-like interface.
"""
import pygame
import sys
import threading
import time
import logging
import random
import os
from typing import Dict, List, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('monopoly-ui')

# Define colors
COLORS = {
    "white": (255, 255, 255),
    "black": (0, 0, 0),
    "dark_blue": (1, 50, 67),
    "light_blue": (0, 168, 232),
    "red": (232, 32, 37),
    "green": (30, 180, 30),
    "yellow": (255, 210, 0),
    "orange": (255, 128, 0),
    "purple": (134, 42, 140),
    "pink": (255, 130, 171),
    "brown": (120, 69, 26),
    "light_gray": (220, 220, 220),
    "dark_gray": (100, 100, 100),
    "bg_color": (239, 239, 239),
    "monopoly_red": (213, 24, 31),
    "monopoly_dark": (15, 61, 62),
    "monopoly_light": (204, 223, 214),
    "button_color": (213, 24, 31),
    "button_hover": (233, 44, 51),
    "button_text": (255, 255, 255),
    "disabled_button": (150, 150, 150),
    "player1": (255, 0, 0),
    "player2": (0, 0, 255),
    "player3": (0, 150, 0),
    "player4": (255, 165, 0),
    "player5": (128, 0, 128),
    "player6": (165, 42, 42)
}

# Player token colors
PLAYER_COLORS = [
    COLORS["player1"], COLORS["player2"], COLORS["player3"],
    COLORS["player4"], COLORS["player5"], COLORS["player6"]
]

class Button:
    """A button class for pygame UI."""
    
    def __init__(self, x, y, width, height, text, color=COLORS["button_color"], 
                 hover_color=COLORS["button_hover"], text_color=COLORS["button_text"],
                 font_size=20, action=None, disabled=False):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.original_color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.font_size = font_size
        self.action = action
        self.disabled = disabled
        self.hovered = False
    
    def draw(self, surface):
        """Draw the button on the given surface."""
        # Choose the right color based on state
        if self.disabled:
            color = COLORS["disabled_button"]
        elif self.hovered:
            color = self.hover_color
        else:
            color = self.color
            
        # Draw button rectangle
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        pygame.draw.rect(surface, COLORS["black"], self.rect, 2, border_radius=10)
        
        # Draw text
        font = pygame.font.SysFont("Arial", self.font_size, bold=True)
        text_surf = font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
    
    def check_hover(self, pos):
        """Check if mouse is hovering over button."""
        if self.disabled:
            self.hovered = False
            return False
            
        if self.rect.collidepoint(pos):
            self.hovered = True
            return True
        else:
            self.hovered = False
            return False
    
    def handle_event(self, event):
        """Handle mouse events for the button."""
        if self.disabled:
            return False
            
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.rect.collidepoint(event.pos):
                if self.action:
                    self.action()
                return True
        return False


class TextInput:
    """A text input field for pygame UI."""
    
    def __init__(self, x, y, width, height, placeholder="", text="", 
                 font_size=20, max_length=20):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.placeholder = placeholder
        self.font_size = font_size
        self.max_length = max_length
        self.active = False
        self.font = pygame.font.SysFont("Arial", font_size)
    
    def draw(self, surface):
        """Draw the text input on the given surface."""
        # Draw background
        bg_color = COLORS["light_gray"] if self.active else COLORS["white"]
        pygame.draw.rect(surface, bg_color, self.rect, border_radius=5)
        pygame.draw.rect(surface, COLORS["black"], self.rect, 2, border_radius=5)
        
        # Draw text or placeholder
        if self.text:
            text_surf = self.font.render(self.text, True, COLORS["black"])
        else:
            text_surf = self.font.render(self.placeholder, True, COLORS["dark_gray"])
            
        # Position text with some padding
        text_rect = text_surf.get_rect(midleft=(self.rect.left + 10, self.rect.centery))
        surface.blit(text_surf, text_rect)
    
    def handle_event(self, event):
        """Handle events for the text input."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Toggle active state based on click
            if self.rect.collidepoint(event.pos):
                self.active = True
            else:
                self.active = False
                
        elif event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key == pygame.K_RETURN:
                self.active = False
            elif len(self.text) < self.max_length:
                # Only add printable characters
                if event.unicode.isprintable():
                    self.text += event.unicode
                    
        return self.active


class PlayerCard:
    """A card displaying player information."""
    
    def __init__(self, x, y, width, height, player_id, name, color):
        self.rect = pygame.Rect(x, y, width, height)
        self.player_id = player_id
        self.name = name
        self.color = color
        self.money = 1500
        self.position = 0
        self.is_current = False
        self.properties = []
    
    def draw(self, surface):
        """Draw the player card on the given surface."""
        # Draw card background with player color at top
        pygame.draw.rect(surface, COLORS["white"], self.rect, border_radius=10)
        
        # Draw colored header
        header_rect = pygame.Rect(self.rect.x, self.rect.y, self.rect.width, 40)
        pygame.draw.rect(surface, self.color, header_rect, border_top_left_radius=10, 
                         border_top_right_radius=10)
        
        # Add border (thicker if current player)
        border_width = 3 if self.is_current else 1
        pygame.draw.rect(surface, COLORS["black"], self.rect, border_width, border_radius=10)
        
        # Draw player name
        font = pygame.font.SysFont("Arial", 18, bold=True)
        name_surf = font.render(self.name, True, COLORS["white"])
        name_rect = name_surf.get_rect(center=(header_rect.centerx, header_rect.centery))
        surface.blit(name_surf, name_rect)
        
        # Draw money amount
        money_font = pygame.font.SysFont("Arial", 24, bold=True)
        money_text = f"${self.money}"
        money_surf = money_font.render(money_text, True, COLORS["black"])
        money_rect = money_surf.get_rect(center=(self.rect.centerx, self.rect.centery))
        surface.blit(money_surf, money_rect)
        
        # Draw position
        pos_font = pygame.font.SysFont("Arial", 16)
        pos_text = f"Position: {self.position}"
        pos_surf = pos_font.render(pos_text, True, COLORS["black"])
        pos_rect = pos_surf.get_rect(center=(self.rect.centerx, self.rect.centery + 30))
        surface.blit(pos_surf, pos_rect)
        
        # Draw "Current Player" indicator if applicable
        if self.is_current:
            current_font = pygame.font.SysFont("Arial", 14, bold=True)
            current_surf = current_font.render("CURRENT PLAYER", True, COLORS["monopoly_red"])
            current_rect = current_surf.get_rect(center=(self.rect.centerx, self.rect.bottom - 15))
            surface.blit(current_surf, current_rect)
    
    def update(self, money, position, is_current=False):
        """Update the player card information."""
        self.money = money
        self.position = position
        self.is_current = is_current


class DiceDisplay:
    """A display for dice rolls."""
    
    def __init__(self, x, y, size=60, gap=20):
        self.x = x
        self.y = y
        self.size = size
        self.gap = gap
        self.values = (1, 1)
        self.rolling = False
        self.roll_frames = 0
        self.max_roll_frames = 20
        
        # Dice pip positions (relative to dice top-left)
        self.pip_positions = {
            1: [(0.5, 0.5)],
            2: [(0.25, 0.25), (0.75, 0.75)],
            3: [(0.25, 0.25), (0.5, 0.5), (0.75, 0.75)],
            4: [(0.25, 0.25), (0.25, 0.75), (0.75, 0.25), (0.75, 0.75)],
            5: [(0.25, 0.25), (0.25, 0.75), (0.5, 0.5), (0.75, 0.25), (0.75, 0.75)],
            6: [(0.25, 0.25), (0.25, 0.5), (0.25, 0.75), 
                (0.75, 0.25), (0.75, 0.5), (0.75, 0.75)]
        }
    
    def start_roll(self):
        """Start a dice rolling animation."""
        self.rolling = True
        self.roll_frames = 0
    
    def update(self):
        """Update the dice state."""
        if self.rolling:
            # Generate random dice values during animation
            self.values = (random.randint(1, 6), random.randint(1, 6))
            self.roll_frames += 1
            
            if self.roll_frames >= self.max_roll_frames:
                self.rolling = False
    
    def set_values(self, values):
        """Set the final dice values."""
        self.values = values
        self.rolling = False
    
    def draw(self, surface):
        """Draw the dice on the given surface."""
        # Draw first die
        die1_rect = pygame.Rect(self.x, self.y, self.size, self.size)
        pygame.draw.rect(surface, COLORS["white"], die1_rect, border_radius=10)
        pygame.draw.rect(surface, COLORS["black"], die1_rect, 2, border_radius=10)
        
        # Draw second die
        die2_rect = pygame.Rect(self.x + self.size + self.gap, self.y, self.size, self.size)
        pygame.draw.rect(surface, COLORS["white"], die2_rect, border_radius=10)
        pygame.draw.rect(surface, COLORS["black"], die2_rect, 2, border_radius=10)
        
        # Draw pips on first die
        for pos in self.pip_positions[self.values[0]]:
            pip_x = self.x + pos[0] * self.size
            pip_y = self.y + pos[1] * self.size
            pygame.draw.circle(surface, COLORS["black"], (int(pip_x), int(pip_y)), self.size // 10)
        
        # Draw pips on second die
        for pos in self.pip_positions[self.values[1]]:
            pip_x = self.x + self.size + self.gap + pos[0] * self.size
            pip_y = self.y + pos[1] * self.size
            pygame.draw.circle(surface, COLORS["black"], (int(pip_x), int(pip_y)), self.size // 10)
        
        # Draw total
        total = sum(self.values)
        font = pygame.font.SysFont("Arial", 24, bold=True)
        total_surf = font.render(f"Total: {total}", True, COLORS["black"])
        total_rect = total_surf.get_rect(center=(self.x + self.size + self.gap/2, self.y + self.size + 30))
        surface.blit(total_surf, total_rect)


class MonopolyUI:
    """User interface for the Monopoly game LCD control panel."""
    
    def __init__(self, client):
        """Initialize the UI."""
        self.client = client
        self.screen = None
        self.width = 800
        self.height = 600
        self.game_started = False
        self.is_lcd_mode = False  # Set to True when running on Raspberry Pi with LCD
        
        # UI state
        self.current_page = "setup"  # "setup" or "game"
        self.player_count = 2
        self.player_names = ["Player 1", "Player 2", "Player 3", "Player 4", "Player 5", "Player 6"]
        self.server_ip = "localhost"
        
        # UI elements
        self.buttons = {}
        self.text_inputs = {}
        self.player_cards = {}
        self.dice_display = None
        self.status_message = ""
        
        # For direct hardware control on the Raspberry Pi
        self.gpio_initialized = False
    
    def run(self):
        """Start the UI."""
        if self.is_lcd_mode:
            self._initialize_hardware()
            self._run_lcd_interface()
        else:
            self._run_pygame_interface()
    
    def _initialize_hardware(self):
        """Initialize hardware components when running on Raspberry Pi."""
        try:
            # This would be implemented for the actual hardware
            # import RPi.GPIO as GPIO
            # ... setup GPIO pins for buttons, etc.
            self.gpio_initialized = True
            logger.info("GPIO initialized")
        except ImportError:
            logger.warning("RPi.GPIO not available, hardware control disabled")
    
    def _run_lcd_interface(self):
        """Run the UI on the LCD display (for Raspberry Pi)."""
        # This would be adjusted for the actual hardware
        # But we'll still use pygame for the display
        self._run_pygame_interface()
    
    def _run_pygame_interface(self):
        """Run the UI using pygame."""
        pygame.init()
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Monopoly Game Controller")
        
        clock = pygame.time.Clock()
        self._create_ui_elements()
        
        running = True
        while running:
            # Process events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                self._handle_event(event)
            
            # Update
            self._update()
            
            # Draw
            self._draw()
            
            # Update display
            pygame.display.flip()
            clock.tick(60)
        
        pygame.quit()
        sys.exit()
    
    def _create_ui_elements(self):
        """Create all UI elements."""
        # Setup page elements
        self._create_setup_elements()
        
        # Game page elements
        self._create_game_elements()
    
    def _create_setup_elements(self):
        """Create UI elements for the setup page."""
        # Server connection
        self.text_inputs["server_ip"] = TextInput(
            250, 50, 300, 40, 
            placeholder="Server IP (e.g. 192.168.1.100)",
            text=self.server_ip
        )
        
        self.buttons["connect"] = Button(
            560, 50, 140, 40, "Connect", 
            action=self._connect_to_server
        )
        
        # Player count selector
        self.buttons["player_minus"] = Button(
            250, 120, 40, 40, "-", 
            action=lambda: self._change_player_count(-1)
        )
        
        self.buttons["player_plus"] = Button(
            370, 120, 40, 40, "+", 
            action=lambda: self._change_player_count(1)
        )
        
        # Player name inputs
        for i in range(6):
            y_pos = 180 + i * 50
            self.text_inputs[f"player_{i+1}"] = TextInput(
                250, y_pos, 300, 40,
                placeholder=f"Player {i+1} Name",
                text=self.player_names[i]
            )
        
        # Start game button
        self.buttons["start_game"] = Button(
            300, 500, 200, 50, "Start Game",
            font_size=24, action=self._start_game,
            disabled=not self.client.is_connected
        )
    
    def _create_game_elements(self):
        """Create UI elements for the game page."""
        # Dice display
        self.dice_display = DiceDisplay(350, 50)
        
        # Game control buttons
        self.buttons["roll_dice"] = Button(
            250, 150, 150, 50, "Roll Dice",
            action=self._roll_dice
        )
        
        self.buttons["end_turn"] = Button(
            420, 150, 150, 50, "End Turn",
            action=self._end_turn
        )
        
        # Back to setup button
        self.buttons["back"] = Button(
            30, 30, 100, 40, "Back",
            action=lambda: self._change_page("setup")
        )
    
    def _change_page(self, page):
        """Change the current page."""
        self.current_page = page
    
    def _connect_to_server(self):
        """Connect to the monopoly server."""
        self.server_ip = self.text_inputs["server_ip"].text
        if not self.server_ip:
            self.status_message = "Please enter a server IP address"
            return
            
        self.client.server_host = self.server_ip
        threading.Thread(target=self._connect_thread, daemon=True).start()
    
    def _connect_thread(self):
        """Connect to server in a background thread."""
        # Using a dummy player name for initial connection
        success = self.client.connect("ControlPanel")
        if success:
            self.status_message = f"Connected to server at {self.client.server_host}"
            # Enable start game button
            self.buttons["start_game"].disabled = False
        else:
            self.status_message = "Failed to connect to server"
    
    def _change_player_count(self, change):
        """Change the number of players."""
        new_count = self.player_count + change
        if 2 <= new_count <= 6:
            self.player_count = new_count
    
    def _start_game(self):
        """Initialize the game with the specified players."""
        if not self.client.is_connected:
            self.status_message = "Not connected to server. Please connect first."
            return
            
        # Get player names from input fields
        for i in range(self.player_count):
            self.player_names[i] = self.text_inputs[f"player_{i+1}"].text
            if not self.player_names[i]:
                self.player_names[i] = f"Player {i+1}"
        
        # Check for duplicate names
        unique_names = set(self.player_names[:self.player_count])
        if len(unique_names) != self.player_count:
            self.status_message = "All players must have unique names"
            return
        
        # Register players with the server
        for i in range(self.player_count):
            self.client.register_player(self.player_names[i])
        
        # Switch to game page
        self.game_started = True
        self.current_page = "game"
        self.status_message = "Game started! Waiting for first turn."
    
    def _roll_dice(self):
        """Roll the dice for the current player."""
        if not self.game_started:
            self.status_message = "Game not started"
            return
            
        self.client.roll_dice()
        self.status_message = "Rolling dice..."
        self.dice_display.start_roll()
    
    def _end_turn(self):
        """End the current player's turn."""
        if not self.game_started:
            self.status_message = "Game not started"
            return
            
        self.client.end_turn()
        self.status_message = "Ending turn..."
    
    def _handle_event(self, event):
        """Handle pygame events."""
        # Handle mouse position for button hover
        if event.type == pygame.MOUSEMOTION:
            for button in self.buttons.values():
                button.check_hover(event.pos)
        
        # Handle button clicks
        if self.current_page == "setup":
            # Handle setup page events
            if event.type == pygame.MOUSEBUTTONDOWN:
                for name, button in self.buttons.items():
                    if name in ["connect", "player_minus", "player_plus", "start_game"]:
                        button.handle_event(event)
            
            # Handle text inputs
            active_inputs = ["server_ip"]
            for i in range(self.player_count):
                active_inputs.append(f"player_{i+1}")
                
            for name, text_input in self.text_inputs.items():
                if name in active_inputs:
                    text_input.handle_event(event)
                    
        elif self.current_page == "game":
            # Handle game page events
            if event.type == pygame.MOUSEBUTTONDOWN:
                for name, button in self.buttons.items():
                    if name in ["roll_dice", "end_turn", "back"]:
                        button.handle_event(event)
    
    def _update(self):
        """Update the game state."""
        # Update dice animation if rolling
        if self.dice_display and self.dice_display.rolling:
            self.dice_display.update()
    
    def _draw(self):
        """Draw the current UI page."""
        # Clear screen with background color
        self.screen.fill(COLORS["bg_color"])
        
        # Draw Monopoly header
        header_font = pygame.font.SysFont("Arial", 32, bold=True)
        header_text = header_font.render("MONOPOLY GAME CONTROLLER", True, COLORS["monopoly_red"])
        self.screen.blit(header_text, (self.width//2 - header_text.get_width()//2, 10))
        
        # Draw current page
        if self.current_page == "setup":
            self._draw_setup_page()
        elif self.current_page == "game":
            self._draw_game_page()
        
        # Draw status message at bottom
        if self.status_message:
            status_font = pygame.font.SysFont("Arial", 16)
            status_text = status_font.render(self.status_message, True, COLORS["black"])
            self.screen.blit(status_text, (10, self.height - 30))
    
    def _draw_setup_page(self):
        """Draw the setup page."""
        # Draw page title
        title_font = pygame.font.SysFont("Arial", 24, bold=True)
        title_text = title_font.render("Game Setup", True, COLORS["black"])
        self.screen.blit(title_text, (50, 50))
        
        # Draw server connection section
        server_font = pygame.font.SysFont("Arial", 18)
        server_text = server_font.render("Server IP:", True, COLORS["black"])
        self.screen.blit(server_text, (100, 60))
        
        # Draw server IP input
        self.text_inputs["server_ip"].draw(self.screen)
        
        # Draw connect button
        self.buttons["connect"].draw(self.screen)
        
        # Draw player count section
        player_count_font = pygame.font.SysFont("Arial", 18)
        player_count_text = player_count_font.render("Number of Players:", True, COLORS["black"])
        self.screen.blit(player_count_text, (100, 130))
        
        # Draw player count controls
        self.buttons["player_minus"].draw(self.screen)
        count_font = pygame.font.SysFont("Arial", 24, bold=True)
        count_text = count_font.render(str(self.player_count), True, COLORS["black"])
        self.screen.blit(count_text, (320, 130))
        self.buttons["player_plus"].draw(self.screen)
        
        # Draw player name inputs
        name_font = pygame.font.SysFont("Arial", 18)
        for i in range(6):
            if i < self.player_count:
                name_text = name_font.render(f"Player {i+1} Name:", True, COLORS["black"])
                self.screen.blit(name_text, (100, 190 + i * 50))
                self.text_inputs[f"player_{i+1}"].draw(self.screen)
        
        # Draw start game button
        self.buttons["start_game"].draw(self.screen)
        
        # Draw connection status
        conn_status = "Connected" if self.client.is_connected else "Not Connected"
        conn_color = COLORS["green"] if self.client.is_connected else COLORS["red"]
        conn_font = pygame.font.SysFont("Arial", 16)
        conn_text = conn_font.render(f"Status: {conn_status}", True, conn_color)
        self.screen.blit(conn_text, (10, self.height - 60))
    
    def _draw_game_page(self):
        """Draw the game page."""
        # Draw page title
        title_font = pygame.font.SysFont("Arial", 24, bold=True)
        title_text = title_font.render("Game Play", True, COLORS["black"])
        self.screen.blit(title_text, (self.width//2 - 50, 10))
        
        # Draw back button
        self.buttons["back"].draw(self.screen)
        
        # Draw dice
        if self.dice_display:
            self.dice_display.draw(self.screen)
        
        # Draw game control buttons
        self.buttons["roll_dice"].draw(self.screen)
        self.buttons["end_turn"].draw(self.screen)
        
        # Draw player cards
        self._draw_player_cards()
    
    def _draw_player_cards(self):
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
                card.draw(self.screen)
    
    def update_game_state(self, game_state: Dict[str, Any]):
        """Update the UI with the new game state."""
        if not self.game_started:
            return
            
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
            self.player_cards[player_id].update(money, position, is_current)
        
        # Update dice display with current roll
        dice_roll = game_state.get("dice_roll", (0, 0))
        if self.dice_display and not self.dice_display.rolling:
            self.dice_display.set_values(dice_roll)
        
        # Update game status message
        game_phase = game_state.get("game_phase", "waiting")
        current_player_id = game_state.get("current_player_id")
        
        if current_player_id and current_player_id in players:
            current_player_name = players[current_player_id].get("name", "Unknown")
            self.status_message = f"Game Phase: {game_phase} - Current Player: {current_player_name}"
        else:
            self.status_message = f"Game Phase: {game_phase}"
    
    def show_message(self, title: str, message: str):
        """Show an information message to the user."""
        self.status_message = f"{title}: {message}"
        logger.info(f"{title}: {message}")
    
    def show_error(self, message: str):
        """Show an error message to the user."""
        self.status_message = f"ERROR: {message}"
        logger.error(message)