"""
UI implementation for Monopoly game client.
Handles display (LCD screen or mocked window) and user input.
This is for a physical board game with an LCD control panel.
Uses Pygame for a horror-themed game interface.

THIS FILE IS DEPRECATED - See the ui/ directory for the refactored implementation
"""
import pygame
import sys
import threading
import time
import logging
import random
import os
import math
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
    
    # Horror theme colors
    "blood_red": (145, 0, 0),
    "fresh_blood": (190, 0, 0),
    "dark_blood": (85, 0, 0),
    "bone": (225, 215, 190),
    "shadow": (20, 20, 25),
    "midnight": (5, 5, 15),
    "fog": (180, 180, 200, 150),  # With alpha
    "toxic_green": (50, 200, 50),
    "horror_text": (200, 0, 0),
    
    # UI elements
    "button_color": (100, 0, 0),
    "button_hover": (150, 0, 0),
    "button_text": (255, 200, 200),
    "disabled_button": (60, 60, 60),
    "bg_color": (50, 50, 60),  # Added background color
    
    # Player colors (more muted/creepy)
    "player1": (145, 0, 0),      # Blood red
    "player2": (0, 0, 100),      # Dark blue
    "player3": (0, 80, 0),       # Dark green
    "player4": (100, 50, 0),     # Dark orange
    "player5": (80, 0, 80),      # Dark purple
    "player6": (80, 25, 10)      # Dark brown
}

# Player token colors
PLAYER_COLORS = [
    COLORS["player1"], COLORS["player2"], COLORS["player3"],
    COLORS["player4"], COLORS["player5"], COLORS["player6"]
]

class BloodDrop:
    """A blood drop for animation effects."""
    
    def __init__(self, x, y, speed=1, size=5, thickness=2):
        self.x = x
        self.y = y
        self.orig_x = x
        self.speed = speed
        self.size = size
        self.thickness = thickness
        self.dripping = True
        self.drip_length = random.randint(10, 60)
        self.alpha = 255
        self.fade_rate = random.uniform(0.5, 2.0)
        
    def update(self):
        """Update the blood drop position."""
        if self.dripping:
            self.y += self.speed
            
            # Check if we've dripped enough
            if self.y >= self.orig_y + self.drip_length:
                self.dripping = False
        else:
            # Fade out slowly
            self.alpha -= self.fade_rate
    
    def draw(self, surface):
        """Draw the blood drop on the surface."""
        # Create a surface with alpha channel
        drop_surface = pygame.Surface((self.size*2, self.y - self.orig_y + self.size*2), pygame.SRCALPHA)
        
        # Draw the drop
        color = COLORS["fresh_blood"] + (int(self.alpha),)  # Add alpha
        pygame.draw.line(
            drop_surface, 
            color, 
            (self.size, 0), 
            (self.size, self.y - self.orig_y), 
            self.thickness
        )
        
        # Draw the rounded end of the drop
        pygame.draw.circle(
            drop_surface,
            color,
            (self.size, self.y - self.orig_y + self.size),
            self.size,
            0
        )
        
        # Blit to main surface
        surface.blit(drop_surface, (self.x - self.size, self.orig_y - self.size))
        
    def is_finished(self):
        """Check if the animation is finished."""
        return self.alpha <= 0


class HorrorButton:
    """A horror-themed button for pygame UI."""
    
    def __init__(self, x, y, width, height, text, color=COLORS["button_color"], 
                 hover_color=COLORS["button_hover"], text_color=COLORS["button_text"],
                 font_size=24, action=None, disabled=False, horror_style=True):
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
        self.horror_style = horror_style
        
        # For horror effect
        self.pulse_value = 0
        self.pulse_direction = 1
        self.pulse_speed = 0.03
        self.pulse_max = 0.5
        
        # Blood drops for hover effect
        self.blood_drops = []
    
    def update(self):
        """Update animation effects."""
        # Update pulsing effect
        self.pulse_value += self.pulse_direction * self.pulse_speed
        if self.pulse_value >= self.pulse_max or self.pulse_value <= 0:
            self.pulse_direction *= -1
        
        # Update existing blood drops
        for drop in self.blood_drops[:]:
            drop.update()
            if drop.is_finished():
                self.blood_drops.remove(drop)
    
    def draw(self, surface):
        """Draw the button on the given surface."""
        # Choose the right color based on state
        if self.disabled:
            color = COLORS["disabled_button"]
        elif self.hovered:
            color = self.hover_color
            
            # Add blood drip effect when hovered
            if self.horror_style and random.random() < 0.05:
                drop_x = random.randint(self.rect.left, self.rect.right)
                self.blood_drops.append(BloodDrop(
                    drop_x, self.rect.bottom, 
                    speed=random.uniform(0.5, 2.0),
                    size=random.randint(2, 4),
                    thickness=random.randint(1, 3)
                ))
        else:
            color = self.color
            
        # Draw button with a glow effect
        if self.horror_style and not self.disabled:
            # Outer glow (pulsing)
            glow_size = int(10 * self.pulse_value)
            if glow_size > 0:
                glow_rect = self.rect.inflate(glow_size*2, glow_size*2)
                pygame.draw.rect(surface, COLORS["fresh_blood"], glow_rect, border_radius=3)
            
            # Inner button with a beveled look
            pygame.draw.rect(surface, COLORS["dark_blood"], self.rect.inflate(4, 4), border_radius=3)
        
        # Main button rectangle
        pygame.draw.rect(surface, color, self.rect, border_radius=3)
        
        # Border effect
        border_color = COLORS["bone"] if self.horror_style else COLORS["black"]
        pygame.draw.rect(surface, border_color, self.rect, 1, border_radius=3)
        
        # Draw text with a slight shadow effect
        font = pygame.font.SysFont("Arial", self.font_size, bold=True)
        
        if self.horror_style:
            # Shadow text for horror effect
            shadow_surf = font.render(self.text, True, COLORS["black"])
            shadow_rect = shadow_surf.get_rect(center=(self.rect.centerx+2, self.rect.centery+2))
            surface.blit(shadow_surf, shadow_rect)
        
        text_surf = font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
        
        # Draw blood drops
        for drop in self.blood_drops:
            drop.draw(surface)
    
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
                 font_size=20, max_length=20, horror_style=True):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.placeholder = placeholder
        self.font_size = font_size
        self.max_length = max_length
        self.active = False
        self.font = pygame.font.SysFont("Arial", font_size)
        self.horror_style = horror_style
        self.blink_timer = 0
        self.show_cursor = True
    
    def draw(self, surface):
        """Draw the text input on the given surface."""
        # Draw background
        if self.horror_style:
            # Darker theme for horror
            bg_color = COLORS["shadow"] if self.active else COLORS["midnight"]
            border_color = COLORS["blood_red"] if self.active else COLORS["dark_blood"]
            text_color = COLORS["bone"]
            placeholder_color = COLORS["dark_gray"]
        else:
            # Original style
            bg_color = COLORS["light_gray"] if self.active else COLORS["white"]
            border_color = COLORS["black"]
            text_color = COLORS["black"]
            placeholder_color = COLORS["dark_gray"]
            
        pygame.draw.rect(surface, bg_color, self.rect, border_radius=3)
        pygame.draw.rect(surface, border_color, self.rect, 2, border_radius=3)
        
        # Draw text or placeholder
        if self.text:
            text_surf = self.font.render(self.text, True, text_color)
        else:
            text_surf = self.font.render(self.placeholder, True, placeholder_color)
            
        # Position text with some padding
        text_rect = text_surf.get_rect(midleft=(self.rect.left + 10, self.rect.centery))
        surface.blit(text_surf, text_rect)
        
        # Draw cursor if active
        if self.active:
            # Update blink timer
            self.blink_timer += 1
            if self.blink_timer >= 30:
                self.blink_timer = 0
                self.show_cursor = not self.show_cursor
                
            if self.show_cursor:
                if self.text:
                    cursor_x = text_rect.right + 2
                else:
                    cursor_x = self.rect.left + 10
                
                cursor_color = COLORS["fresh_blood"] if self.horror_style else COLORS["black"]
                pygame.draw.line(
                    surface,
                    cursor_color,
                    (cursor_x, self.rect.top + 5),
                    (cursor_x, self.rect.bottom - 5),
                    2
                )
    
    def handle_event(self, event):
        """Handle events for the text input."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Toggle active state based on click
            if self.rect.collidepoint(event.pos):
                self.active = True
                self.show_cursor = True
                self.blink_timer = 0
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


class BloodTitle:
    """Animated blood title with dripping effect."""
    
    def __init__(self, x, y, text, font_size=60, color=COLORS["fresh_blood"], multiline=False):
        self.x = x
        self.y = y
        self.text = text
        self.font_size = font_size
        self.color = color
        self.font = pygame.font.SysFont("Arial Black", font_size, bold=True)
        self.drips = []
        self.last_drip_time = 0
        self.letter_positions = []
        self.multiline = multiline
        self.lines = []
        
        if multiline:
            # Split text into multiple lines
            words = self.text.split()
            line = ""
            for word in words:
                test_line = line + word + " "
                test_width = self.font.size(test_line)[0]
                if test_width < 700:  # Maximum width for the title
                    line = test_line
                else:
                    self.lines.append(line)
                    line = word + " "
            if line:
                self.lines.append(line)
        else:
            self.lines = [self.text]
            
        self.generate_letter_positions()
    
    def generate_letter_positions(self):
        """Calculate positions for each letter in the title."""
        self.letter_positions = []
        
        line_height = self.font_size + 10
        start_y = self.y - ((len(self.lines) - 1) * line_height) / 2
        
        for i, line in enumerate(self.lines):
            line_y = start_y + i * line_height
            text_surf = self.font.render(line, True, self.color)
            text_rect = text_surf.get_rect(center=(self.x, line_y))
            
            # Estimate letter widths (approximate)
            total_width = text_rect.width
            letter_width = total_width / len(line)
            
            # Store bottom center of each letter
            for j in range(len(line)):
                letter_x = text_rect.left + letter_width * j + letter_width / 2
                letter_y = text_rect.bottom
                self.letter_positions.append((letter_x, letter_y))
    
    def update(self):
        """Update the animation."""
        current_time = pygame.time.get_ticks()
        
        # Add new blood drips occasionally
        if current_time - self.last_drip_time > 300:  # Every 300ms
            self.last_drip_time = current_time
            if random.random() < 0.3:  # 30% chance
                # Choose a random letter to drip from
                letter_idx = random.randint(0, len(self.text) - 1)
                pos = self.letter_positions[letter_idx]
                
                # Add some randomness to the drip position
                x_offset = random.randint(-10, 10)
                
                self.drips.append(BloodDrop(
                    pos[0] + x_offset, pos[1], 
                    speed=random.uniform(0.5, 2.0),
                    size=random.randint(3, 7),
                    thickness=random.randint(2, 4)
                ))
        
        # Update existing blood drops
        for drip in self.drips[:]:
            drip.update()
            if drip.is_finished():
                self.drips.remove(drip)
    
    def draw(self, surface):
        """Draw the blood title on the surface."""
        line_height = self.font_size + 10
        start_y = self.y - ((len(self.lines) - 1) * line_height) / 2
        
        # Draw each line of the title
        for i, line in enumerate(self.lines):
            line_y = start_y + i * line_height
            
            # Draw the shadow
            shadow_surf = self.font.render(line, True, COLORS["dark_blood"])
            shadow_rect = shadow_surf.get_rect(center=(self.x + 3, line_y + 3))
            surface.blit(shadow_surf, shadow_rect)
            
            # Draw the main text
            text_surf = self.font.render(line, True, self.color)
            text_rect = text_surf.get_rect(center=(self.x, line_y))
            surface.blit(text_surf, text_rect)
        
        # Draw all blood drips
        for drip in self.drips:
            drip.draw(surface)


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
        self.horror_style = True
        
        # For horror animation
        self.blood_drips = []
        self.pulse_value = 0
        self.pulse_direction = 1
    
    def update(self):
        """Update horror animations."""
        # Update pulsing effect for current player
        if self.is_current:
            self.pulse_value += self.pulse_direction * 0.02
            if self.pulse_value >= 0.5 or self.pulse_value <= 0:
                self.pulse_direction *= -1
                
            # Occasionally add blood drips
            if random.random() < 0.01:
                drip_x = random.randint(self.rect.left, self.rect.right)
                self.blood_drips.append(BloodDrop(
                    drip_x, self.rect.top, 
                    speed=random.uniform(0.5, 1.5)
                ))
        
        # Update existing blood drips
        for drip in self.blood_drips[:]:
            drip.update()
            if drip.is_finished():
                self.blood_drips.remove(drip)
    
    def draw(self, surface):
        """Draw the player card on the given surface."""
        if self.horror_style:
            # Horror-themed card
            
            # Glow effect for current player
            if self.is_current:
                glow_size = int(10 * self.pulse_value)
                if glow_size > 0:
                    glow_rect = self.rect.inflate(glow_size*2, glow_size*2)
                    pygame.draw.rect(surface, self.color, glow_rect, border_radius=5)
            
            # Draw card background
            pygame.draw.rect(surface, COLORS["midnight"], self.rect, border_radius=5)
            
            # Draw colored header
            header_rect = pygame.Rect(self.rect.x, self.rect.y, self.rect.width, 30)
            pygame.draw.rect(surface, self.color, header_rect, border_top_left_radius=5, 
                            border_top_right_radius=5)
            
            # Add border (thicker if current player)
            border_color = COLORS["bone"] if self.is_current else COLORS["dark_gray"]
            border_width = 2 if self.is_current else 1
            pygame.draw.rect(surface, border_color, self.rect, border_width, border_radius=5)
            
            # Draw player name
            font = pygame.font.SysFont("Arial", 18, bold=True)
            name_surf = font.render(self.name, True, COLORS["bone"])
            name_rect = name_surf.get_rect(center=(header_rect.centerx, header_rect.centery))
            surface.blit(name_surf, name_rect)
            
            # Draw money amount
            money_font = pygame.font.SysFont("Arial", 24, bold=True)
            money_text = f"${self.money}"
            money_surf = money_font.render(money_text, True, COLORS["bone"])
            money_rect = money_surf.get_rect(center=(self.rect.centerx, self.rect.centery))
            surface.blit(money_surf, money_rect)
            
            # Draw position
            pos_font = pygame.font.SysFont("Arial", 16)
            pos_text = f"Position: {self.position}"
            pos_surf = pos_font.render(pos_text, True, COLORS["bone"])
            pos_rect = pos_surf.get_rect(center=(self.rect.centerx, self.rect.centery + 30))
            surface.blit(pos_surf, pos_rect)
            
            # Draw "Current Player" indicator if applicable
            if self.is_current:
                current_font = pygame.font.SysFont("Arial", 14, bold=True)
                current_surf = current_font.render("CURRENT VICTIM", True, COLORS["fresh_blood"])
                current_rect = current_surf.get_rect(center=(self.rect.centerx, self.rect.bottom - 15))
                surface.blit(current_surf, current_rect)
                
            # Draw blood drips
            for drip in self.blood_drips:
                drip.draw(surface)
        else:
            # Original style card
            pygame.draw.rect(surface, COLORS["white"], self.rect, border_radius=10)
            
            # Draw colored header
            header_rect = pygame.Rect(self.rect.x, self.rect.y, self.rect.width, 40)
            pygame.draw.rect(surface, self.color, header_rect, border_top_left_radius=10, 
                            border_top_right_radius=10)
            
            # Add border
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
                current_surf = current_font.render("CURRENT PLAYER", True, COLORS["red"])
                current_rect = current_surf.get_rect(center=(self.rect.centerx, self.rect.bottom - 15))
                surface.blit(current_surf, current_rect)
    
    def update_player_info(self, money, position, is_current=False):
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
        self.current_page = "landing"  # "landing", "setup" or "game"
        self.player_count = 2
        self.player_names = ["Player 1", "Player 2", "Player 3", "Player 4", "Player 5", "Player 6"]
        self.server_ip = "localhost"
        
        # UI elements
        self.buttons = {}
        self.text_inputs = {}
        self.player_cards = {}
        self.dice_display = None
        self.status_message = ""
        
        # Horror theme elements
        self.blood_title = None
        self.background_image = None
        self.spooky_sounds = []
        
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
        
        # Load or create spooky background elements
        self._load_horror_assets()
        
        clock = pygame.time.Clock()
        self._create_ui_elements()
        
        # Play spooky sound if available
        self._play_background_sound()
        
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
        
    def _load_horror_assets(self):
        """Load or create horror theme assets."""
        # This would normally load image assets
        # For now, we'll create placeholders
        
        # Try to load sound if pygame.mixer is available
        try:
            pygame.mixer.init()
            # In a real implementation, you would load actual sound files
            # self.spooky_sounds.append(pygame.mixer.Sound("path/to/sound.wav"))
        except:
            logger.warning("Pygame mixer not available, sounds disabled")
    
    def _play_background_sound(self):
        """Play background spooky ambient sound."""
        # In a real implementation with actual sound files:
        # if self.spooky_sounds and pygame.mixer.get_init():
        #     sound = random.choice(self.spooky_sounds)
        #     sound.play(loops=-1)  # Loop indefinitely
        pass
    
    def _create_ui_elements(self):
        """Create all UI elements."""
        # Landing page elements
        self._create_landing_elements()
        
        # Setup page elements
        self._create_setup_elements()
        
        # Game page elements
        self._create_game_elements()
    
    def _create_landing_elements(self):
        """Create UI elements for the landing page."""
        # Title with blood dripping effect - now with smaller font and multiline support
        self.blood_title = BloodTitle(
            self.width // 2, 
            self.height // 3,
            "REAL ESTATE MASSACRE",
            font_size=54,  # Reduced from 64
            multiline=True  # Enable multiline
        )
        
        # Start button to go to setup page
        self.buttons["start_setup"] = HorrorButton(
            self.width // 2 - 100,
            self.height * 2 // 3,
            200, 60, 
            "START",
            font_size=36,
            action=lambda: self._change_page("setup")
        )
    
    def _create_setup_elements(self):
        """Create UI elements for the setup page."""
        # Server connection
        self.text_inputs["server_ip"] = TextInput(
            250, 50, 300, 40, 
            placeholder="Server IP (e.g. 192.168.1.100)",
            text=self.server_ip
        )
        
        self.buttons["connect"] = HorrorButton(
            560, 50, 140, 40, "Connect", 
            action=self._connect_to_server
        )
        
        # Player count selector
        self.buttons["player_minus"] = HorrorButton(
            250, 120, 40, 40, "-", 
            action=lambda: self._change_player_count(-1)
        )
        
        self.buttons["player_plus"] = HorrorButton(
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
        self.buttons["start_game"] = HorrorButton(
            300, 500, 200, 50, "Start Game",
            font_size=24, action=self._start_game,
            disabled=not self.client.is_connected
        )
    
    def _create_game_elements(self):
        """Create UI elements for the game page."""
        # Dice display
        self.dice_display = DiceDisplay(350, 50)
        
        # Game control buttons
        self.buttons["roll_dice"] = HorrorButton(
            250, 150, 150, 50, "Roll Dice",
            action=self._roll_dice
        )
        
        self.buttons["end_turn"] = HorrorButton(
            420, 150, 150, 50, "End Turn",
            action=self._end_turn
        )
        
        # Back to setup button
        self.buttons["back"] = HorrorButton(
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
        if self.current_page == "landing":
            # Handle landing page events
            if event.type == pygame.MOUSEBUTTONDOWN:
                for name, button in self.buttons.items():
                    if name in ["start_setup"]:
                        button.handle_event(event)
        
        elif self.current_page == "setup":
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
        # Update blood title animation on landing page
        if self.current_page == "landing" and self.blood_title:
            self.blood_title.update()
        
        # Update dice animation if rolling
        if self.dice_display and self.dice_display.rolling:
            self.dice_display.update()
            
        # Update player cards
        if self.current_page == "game":
            for card in self.player_cards.values():
                card.update()
    
    def _draw(self):
        """Draw the current UI page."""
        # Clear screen with background color
        if self.current_page == "landing":
            # Darker background for landing page
            self.screen.fill(COLORS["midnight"])
        else:
            self.screen.fill(COLORS["bg_color"])
        
        # Draw current page
        if self.current_page == "landing":
            self._draw_landing_page()
        elif self.current_page == "setup":
            self._draw_setup_page()
        elif self.current_page == "game":
            self._draw_game_page()
        
        # Draw status message at bottom
        if self.status_message:
            if self.current_page == "landing":
                status_font = pygame.font.SysFont("Arial", 16)
                status_text = status_font.render(self.status_message, True, COLORS["bone"])
            else:
                status_font = pygame.font.SysFont("Arial", 16)
                status_text = status_font.render(self.status_message, True, COLORS["black"])
            self.screen.blit(status_text, (10, self.height - 30))
            
    def _draw_landing_page(self):
        """Draw the landing page with horror theme."""
        # Clear with dark background
        self.screen.fill(COLORS["midnight"])
        
        # Create a haunted skyline
        self._draw_haunted_skyline()
        
        # Draw slow cobwebs in corners
        self._draw_cobwebs()
        
        # Draw the title with blood dripping effect
        self.blood_title.draw(self.screen)
        
        # Draw a spooky subtitle
        subtitle_font = pygame.font.SysFont("Arial", 24, italic=True)
        subtitle_text = subtitle_font.render("Where property deals are deadly...", True, COLORS["bone"])
        subtitle_rect = subtitle_text.get_rect(center=(self.width//2, self.height//3 + 100))
        self.screen.blit(subtitle_text, subtitle_rect)
        
        # Draw the start button
        self.buttons["start_setup"].draw(self.screen)

    def _draw_haunted_skyline(self):
        """Draw a haunted city skyline in the background."""
        # Draw the night sky
        sky_rect = pygame.Rect(0, 0, self.width, self.height)
        pygame.draw.rect(self.screen, COLORS["midnight"], sky_rect)
        
        # Draw moon
        moon_x = self.width * 0.8
        moon_y = self.height * 0.2
        pygame.draw.circle(self.screen, COLORS["bone"], (int(moon_x), int(moon_y)), 30)
        
        # Draw stars (with slow twinkle)
        for i in range(100):
            x = (i * 13) % self.width
            y = ((i * 17) % (self.height // 2))
            size = 0.5 + (math.sin(pygame.time.get_ticks() * 0.001 + i * 0.1) + 1) * 0.75
            pygame.draw.circle(self.screen, COLORS["white"], (int(x), int(y)), size)
        
        # Draw buildings silhouette
        num_buildings = self.width // 100 + 5
        for i in range(num_buildings):
            x = i * (self.width / num_buildings)
            height = random.randint(100, 250)
            width = random.randint(60, 120)
            
            # Draw building
            pygame.draw.rect(
                self.screen,
                COLORS["shadow"],
                (x, self.height - height, width, height)
            )
            
            # Add some windows
            window_size = 10
            window_spacing = 20
            num_floors = height // window_spacing
            num_columns = width // window_spacing
            
            for floor in range(num_floors):
                for col in range(num_columns):
                    if random.random() < 0.7:  # 70% chance for a window
                        window_x = x + col * window_spacing + (window_spacing - window_size) // 2
                        window_y = self.height - height + floor * window_spacing + (window_spacing - window_size) // 2
                        
                        # Make windows glow with slow-changing intensity
                        glow = (math.sin(pygame.time.get_ticks() * 0.0005 + floor * 0.2 + col * 0.3) + 1) * 90 + 20
                        window_color = (*COLORS["fresh_blood"], int(glow))
                        window_surface = pygame.Surface((window_size, window_size), pygame.SRCALPHA)
                        pygame.draw.rect(window_surface, window_color, (0, 0, window_size, window_size))
                        self.screen.blit(window_surface, (window_x, window_y))
        
        # Draw some fog
        for i in range(10):
            x = (pygame.time.get_ticks() * 0.02 + i * 200) % (self.width + 300) - 150
            y = self.height - 50 - i * 5
            size = 100 + i * 10
            
            fog_surface = pygame.Surface((size, size), pygame.SRCALPHA)
            fog_color = (*COLORS["fog"][:3], 40)  # Use RGB from fog color but set alpha to 40
            pygame.draw.circle(fog_surface, fog_color, (size//2, size//2), size//2)
            self.screen.blit(fog_surface, (int(x), int(y)))

    def _draw_cobwebs(self):
        """Draw subtle cobwebs in the corners."""
        # Draw in each corner
        corners = [
            (0, 0),                          # Top left
            (self.width, 0),                 # Top right
            (0, self.height),                # Bottom left
            (self.width, self.height)        # Bottom right
        ]
        
        for corner in corners:
            # Determine the angle range based on which corner
            if corner[0] == 0 and corner[1] == 0:  # Top left
                angle_start, angle_end = 0, 90
            elif corner[0] == self.width and corner[1] == 0:  # Top right
                angle_start, angle_end = 90, 180
            elif corner[0] == 0 and corner[1] == self.height:  # Bottom left
                angle_start, angle_end = 270, 360
            else:  # Bottom right
                angle_start, angle_end = 180, 270
            
            # Draw subtle web strands
            for i in range(5):
                angle = math.radians(angle_start + (angle_end - angle_start) * (i / 4))
                length = 100
                end_x = corner[0] + math.cos(angle) * length
                end_y = corner[1] + math.sin(angle) * length
                
                # Add subtle slow movement
                wave = math.sin(pygame.time.get_ticks() * 0.0005 + i) * 2
                end_x += wave
                end_y += wave
                
                pygame.draw.line(self.screen, COLORS["bone"], corner, (end_x, end_y), 1)
                
                # Add connecting strands
                for j in range(2):
                    # Position along the strand
                    t = (j + 1) / 3
                    x1 = corner[0] + (end_x - corner[0]) * t
                    y1 = corner[1] + (end_y - corner[1]) * t
                    
                    # Calculate perpendicular line
                    perp_angle = angle + math.pi/2
                    perp_length = 20 * (1 - t)  # Shorter near the edges
                    x2 = x1 + math.cos(perp_angle) * perp_length
                    y2 = y1 + math.sin(perp_angle) * perp_length
                    
                    pygame.draw.line(self.screen, COLORS["bone"], (x1, y1), (x2, y2), 1)

# ...existing code...