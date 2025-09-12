"""Setup screen for the Monopoly game."""

import pygame
from typing import List
from client.ui.screens.base import Screen
from client.ui.theme import COLORS, PLAYER_COLORS
from client.ui.components import HorrorButton, TextInput

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
