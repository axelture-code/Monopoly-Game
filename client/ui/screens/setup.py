"""Setup screen for the Monopoly game."""

import pygame
from typing import List, Dict
from client.ui.screens.base import Screen
from client.ui.theme import COLORS
from client.ui.components import HorrorButton, TextInput

class ColorSelector:
    """Color selection component for player setup."""
    
    def __init__(self, x, y, colors, initial_color_index=0):
        self.x = x
        self.y = y
        self.colors = colors
        self.selected_index = initial_color_index
        self.button_size = 30  # Slightly larger for better touch
        self.spacing = 10
        self.total_width = len(colors) * (self.button_size + self.spacing) - self.spacing
        
        # Color names for display
        self.color_names = ["Red", "Green", "Yellow", "Pink", "Purple", "Orange", "Blue", "Teal"]
        
        # Store the actual button rects for better hit detection
        self.button_rects = []
        self._update_button_rects()
    
    def _update_button_rects(self):
        """Update the button rectangles for accurate hit detection."""
        self.button_rects = []
        for i in range(len(self.colors)):
            button_x = self.x + i * (self.button_size + self.spacing)
            button_rect = pygame.Rect(button_x, self.y, self.button_size, self.button_size)
            self.button_rects.append(button_rect)
    
    def draw(self, surface):
        """Draw the color selector."""
        # Draw each color option
        for i, color in enumerate(self.colors):
            # Draw color button using the stored rect
            pygame.draw.rect(surface, color, self.button_rects[i])
            
            # Draw border (thicker for selected color)
            border_color = COLORS["bone"] if i == self.selected_index else COLORS["dark_gray"]
            border_width = 3 if i == self.selected_index else 1
            pygame.draw.rect(surface, border_color, self.button_rects[i], border_width)
        
        # Draw the name of the selected color
        if 0 <= self.selected_index < len(self.color_names):
            font = pygame.font.SysFont("Arial", 16)
            text = font.render(self.color_names[self.selected_index], True, COLORS["bone"])
            text_rect = text.get_rect(midleft=(self.x + self.total_width + 15, self.y + self.button_size // 2))
            surface.blit(text, text_rect)
    
    def handle_event(self, event):
        """Handle mouse events for color selection."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Check each button rect for collision
            mouse_pos = event.pos
            for i, rect in enumerate(self.button_rects):
                if rect.collidepoint(mouse_pos):
                    self.selected_index = i
                    return True
        
        return False
    
    def set_position(self, x, y):
        """Update the selector position and all button rects."""
        self.x = x
        self.y = y
        self._update_button_rects()
    
    def get_selected_color(self):
        """Get the currently selected color."""
        return self.colors[self.selected_index]
    
    def get_selected_color_name(self):
        """Get the name of the currently selected color."""
        return self.color_names[self.selected_index]
    
    def set_selected_color(self, index):
        """Set the selected color by index."""
        if 0 <= index < len(self.colors):
            self.selected_index = index


class ScrollArea:
    """A scrollable area for content that doesn't fit on screen."""
    
    def __init__(self, x, y, width, height, content_height):
        self.rect = pygame.Rect(x, y, width, height)
        self.content_height = content_height
        self.scroll_y = 0
        self.max_scroll = max(0, content_height - height)
        self.dragging = False
        self.last_mouse_y = 0
        
        # Scrollbar properties
        self.scrollbar_width = 15
        self.scrollbar_height = (height / content_height) * height if content_height > height else 0
        self.scrollbar_x = x + width - self.scrollbar_width
    
    def update_content_height(self, new_height):
        """Update the content height and recalculate scroll limits."""
        self.content_height = new_height
        self.max_scroll = max(0, new_height - self.rect.height)
        self.scrollbar_height = (self.rect.height / new_height) * self.rect.height if new_height > self.rect.height else 0
        # Adjust scroll position if it's out of bounds
        self.scroll_y = min(self.scroll_y, self.max_scroll)
    
    def handle_event(self, event):
        """Handle scrolling events."""
        if self.max_scroll <= 0:
            return False
            
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4:  # Scroll up
                self.scroll_y = max(0, self.scroll_y - 20)
                return True
            elif event.button == 5:  # Scroll down
                self.scroll_y = min(self.max_scroll, self.scroll_y + 20)
                return True
            elif event.button == 1:  # Left mouse button
                # Check if click is on scrollbar
                scrollbar_rect = pygame.Rect(
                    self.scrollbar_x,
                    self.rect.y + (self.scroll_y / self.max_scroll) * (self.rect.height - self.scrollbar_height),
                    self.scrollbar_width,
                    self.scrollbar_height
                )
                if scrollbar_rect.collidepoint(event.pos):
                    self.dragging = True
                    self.last_mouse_y = event.pos[1]
                    return True
                
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and self.dragging:
                self.dragging = False
                return True
                
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            # Update scroll position based on mouse movement
            dy = event.pos[1] - self.last_mouse_y
            self.last_mouse_y = event.pos[1]
            
            # Scale the movement relative to content height
            scroll_change = (dy / self.rect.height) * self.content_height
            self.scroll_y = max(0, min(self.max_scroll, self.scroll_y + scroll_change))
            return True
            
        return False
    
    def draw(self, surface):
        """Draw the scrollbar if needed."""
        if self.max_scroll <= 0:
            return
            
        # Draw scrollbar background
        scrollbar_bg_rect = pygame.Rect(
            self.scrollbar_x,
            self.rect.y,
            self.scrollbar_width,
            self.rect.height
        )
        pygame.draw.rect(surface, COLORS["dark_gray"], scrollbar_bg_rect)
        
        # Draw scrollbar handle
        scrollbar_handle_rect = pygame.Rect(
            self.scrollbar_x,
            self.rect.y + (self.scroll_y / self.max_scroll) * (self.rect.height - self.scrollbar_height),
            self.scrollbar_width,
            self.scrollbar_height
        )
        pygame.draw.rect(surface, COLORS["bone"], scrollbar_handle_rect)


class SetupScreen(Screen):
    """Game setup screen for server connection and player setup."""
    
    def __init__(self, ui):
        super().__init__(ui)
        self.player_count = 2
        self.color_selectors = []
        
        # Define available colors for players
        self.available_colors = [
            (220, 20, 20),    # Red
            (20, 180, 20),    # Green
            (220, 220, 20),   # Yellow
            (255, 130, 171),  # Pink
            (160, 32, 240),   # Purple
            (255, 128, 0),    # Orange
            (30, 80, 200),    # Blue
            (0, 150, 150)     # Teal
        ]
        
        # Track which colors are in use (by player index)
        self.color_assignments = {}
        
        # Create scrollable area for player setup
        self.content_height = 500  # Initial estimate
        self.scroll_area = ScrollArea(50, 170, self.width - 100, 350, self.content_height)
        
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
        
        # Color selectors for each player
        self.color_selectors = []
        for i in range(6):  # Support up to 6 players
            y_pos = 40 + i * 60  # Compact spacing
            
            # Color selector
            color_selector = ColorSelector(
                100, y_pos, 
                self.available_colors,
                initial_color_index=min(i, len(self.available_colors)-1)
            )
            self.color_selectors.append(color_selector)
            
            # Update color assignments
            self.color_assignments[i] = color_selector.selected_index
        
        # Start game button
        self.elements["start_game"] = HorrorButton(
            300, 530, 200, 50, "Start Game",
            font_size=24, action=self._start_game,
            disabled=not self.ui.client.is_connected
        )
        
        # Update content height based on player count
        self._update_content_height()
    
    def _update_content_height(self):
        """Update the scrollable content height based on player count."""
        self.content_height = 40 + self.player_count * 60 + 20  # Extra padding
        self.scroll_area.update_content_height(self.content_height)
    
    def _change_player_count(self, change):
        """Change the number of players."""
        new_count = self.player_count + change
        if 2 <= new_count <= 6:
            self.player_count = new_count
            self._update_content_height()
    
    def _start_game(self):
        """Start the game with the current player configuration."""
        # Verify no duplicate colors
        used_colors = set()
        for i in range(self.player_count):
            color_idx = self.color_selectors[i].selected_index
            if color_idx in used_colors:
                self.ui.show_error("Each player must have a unique color")
                return
            used_colors.add(color_idx)
        
        # Get player names (which are just the color names)
        player_names = [selector.get_selected_color_name() for selector in self.color_selectors[:self.player_count]]
        
        # Get player colors
        player_colors = [selector.get_selected_color() for selector in self.color_selectors[:self.player_count]]
        
        # Pass to UI to handle the game start
        self.ui.start_game(player_names, player_colors)
    
    def _check_duplicate_colors(self):
        """Check for and resolve duplicate color selections."""
        used_indices = {}
        
        # Find duplicates
        for player_idx in range(self.player_count):
            color_idx = self.color_selectors[player_idx].selected_index
            
            if color_idx in used_indices:
                # We have a duplicate - find a free color
                for alt_color_idx in range(len(self.available_colors)):
                    if alt_color_idx not in used_indices.values():
                        # Assign this unused color
                        self.color_selectors[player_idx].set_selected_color(alt_color_idx)
                        break
            
            # Record this player's color choice
            used_indices[player_idx] = self.color_selectors[player_idx].selected_index
    
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
            
            # Handle scrolling
            if self.scroll_area.handle_event(event):
                return
            
            # Handle color selectors (only for active players)
            color_changed = False
            
            # Check if click is within the scroll area
            if self.scroll_area.rect.collidepoint(event.pos):
                # Calculate scroll-adjusted mouse position
                scroll_adjusted_pos = (
                    event.pos[0] - self.scroll_area.rect.x,
                    event.pos[1] - self.scroll_area.rect.y + self.scroll_area.scroll_y
                )
                
                # Check each color selector with the adjusted position
                for i in range(self.player_count):
                    # Calculate the correct position for this selector in the scrollable area
                    selector_y = 40 + i * 60
                    
                    # Temporarily adjust the selector to the correct position
                    self.color_selectors[i].set_position(100, selector_y)
                    
                    # Create a temporary event with the adjusted position
                    temp_event = pygame.event.Event(
                        pygame.MOUSEBUTTONDOWN,
                        {'pos': scroll_adjusted_pos, 'button': event.button}
                    )
                    
                    # Check if this selector was clicked
                    if self.color_selectors[i].handle_event(temp_event):
                        color_changed = True
            
            # If a color was changed, check for duplicates
            if color_changed:
                self._check_duplicate_colors()
        
        # Handle scrolling for mouse wheel and dragging
        if event.type in (pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION):
            self.scroll_area.handle_event(event)
        
        # Handle text inputs
        if "server_ip" in self.elements:
            self.elements["server_ip"].handle_event(event)
    
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
        
        # Draw page title - moved down from 20 to 35 pixels from top
        title_font = pygame.font.SysFont("Arial", 32, bold=True)
        title_text = title_font.render("PREPARE THE VICTIMS", True, COLORS["fresh_blood"])
        title_rect = title_text.get_rect(center=(self.width//2, 35))
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
        
        # Create a subsurface for the scrollable area content
        scroll_rect = self.scroll_area.rect
        scroll_surface = surface.subsurface(scroll_rect)
        
        # Clear the scroll surface
        scroll_surface.fill(COLORS["shadow"])
        
        # Draw player color selectors in the scrollable area
        player_font = pygame.font.SysFont("Arial", 18, bold=True)
        
        for i in range(self.player_count):
            y_pos = 40 + i * 60 - int(self.scroll_area.scroll_y)
            
            # Skip if outside visible area
            if y_pos < -60 or y_pos > scroll_rect.height:
                continue
            
            # Player label
            player_text = player_font.render(f"Player {i+1}:", True, COLORS["bone"])
            scroll_surface.blit(player_text, (20, y_pos + 15))
            
            # Update the selector position for drawing
            self.color_selectors[i].set_position(100, y_pos)
            
            # Draw color selector
            self.color_selectors[i].draw(scroll_surface)
        
        # Draw scrollbar if needed
        self.scroll_area.draw(surface)
        
        # Draw start game button
        if "start_game" in self.elements:
            self.elements["start_game"].draw(surface)
        
        # Draw connection status
        conn_status = "Connected" if self.ui.client.is_connected else "Not Connected"
        conn_color = COLORS["toxic_green"] if self.ui.client.is_connected else COLORS["fresh_blood"]
        conn_font = pygame.font.SysFont("Arial", 16)
        conn_text = conn_font.render(f"Status: {conn_status}", True, conn_color)
        surface.blit(conn_text, (10, self.height - 60))
