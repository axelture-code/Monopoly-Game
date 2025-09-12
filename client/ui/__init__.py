"""
UI package for Monopoly game client.
Provides a modular UI system with separate screens and components.
"""
import pygame
import sys
import threading
import logging
from typing import Dict, Any, Optional

from client.ui.theme import COLORS
from client.ui.screens import LandingScreen, SetupScreen, GameScreen
from client.ui.components import HorrorButton, TextInput

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('monopoly-ui')

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
        self.current_screen_name = "landing"  # "landing", "setup" or "game"
        self.player_count = 2
        self.player_names = ["Player 1", "Player 2", "Player 3", "Player 4", "Player 5", "Player 6"]
        self.server_ip = "localhost"
        
        # Screens
        self.screens = {}
        
        # Common UI state
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
        pygame.display.set_caption("Real Estate Massacre")
        
        # Initialize screens
        self._init_screens()
        
        # Play spooky sound if available
        self._play_background_sound()
        
        clock = pygame.time.Clock()
        
        running = True
        while running:
            # Process events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                self._handle_event(event)
            
            # Update current screen
            self.screens[self.current_screen_name].update()
            
            # Draw current screen
            self.screen.fill(COLORS["midnight"])
            self.screens[self.current_screen_name].draw(self.screen)
            
            # Draw status message at bottom
            if self.status_message:
                status_font = pygame.font.SysFont("Arial", 16)
                status_color = COLORS["bone"] if self.current_screen_name == "landing" else COLORS["black"]
                status_text = status_font.render(self.status_message, True, status_color)
                self.screen.blit(status_text, (10, self.height - 30))
            
            # Update display
            pygame.display.flip()
            clock.tick(60)
        
        pygame.quit()
        sys.exit()
    
    def _init_screens(self):
        """Initialize all screens."""
        self.screens = {
            "landing": LandingScreen(self),
            "setup": SetupScreen(self),
            "game": GameScreen(self)
        }
    
    def _play_background_sound(self):
        """Play background spooky ambient sound."""
        try:
            pygame.mixer.init()
            # In a real implementation, you would load actual sound files
            # sound = pygame.mixer.Sound("path/to/sound.wav")
            # sound.play(loops=-1)  # Loop indefinitely
        except:
            logger.warning("Pygame mixer not available, sounds disabled")
    
    def _handle_event(self, event):
        """Handle pygame events."""
        # Pass events to current screen
        self.screens[self.current_screen_name].handle_event(event)
    
    def change_screen(self, screen_name):
        """Change to a different screen."""
        if screen_name in self.screens:
            logger.info(f"Changing to screen: {screen_name}")
            self.current_screen_name = screen_name
        else:
            logger.error(f"Screen '{screen_name}' not found")
    
    def connect_to_server(self, server_ip):
        """Connect to the monopoly server."""
        self.server_ip = server_ip
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
            # Notify setup screen that connection succeeded
            if isinstance(self.screens["setup"], SetupScreen):
                self.screens["setup"].on_connect_success()
        else:
            self.status_message = "Failed to connect to server"
    
    def start_game(self, player_names):
        """Initialize the game with the specified players."""
        if not self.client.is_connected:
            self.status_message = "Not connected to server. Please connect first."
            return False
        
        # Check for duplicate names
        unique_names = set(name for name in player_names if name)
        if len(unique_names) != len([name for name in player_names if name]):
            self.status_message = "All players must have unique names"
            return False
        
        # Register players with the server
        for name in player_names:
            if name:
                self.client.register_player(name)
        
        # Switch to game screen
        self.game_started = True
        self.change_screen("game")
        self.status_message = "Game started! Waiting for first turn."
        return True
    
    def update_game_state(self, game_state: Dict[str, Any]):
        """Update the UI with the new game state."""
        if not self.game_started:
            return
        
        # Pass game state to game screen
        if isinstance(self.screens["game"], GameScreen):
            self.screens["game"].update_game_state(game_state)
        
        # Update game status message
        game_phase = game_state.get("game_phase", "waiting")
        current_player_id = game_state.get("current_player_id")
        players = game_state.get("players", {})
        
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

# Export the main UI class
__all__ = ['MonopolyUI']
