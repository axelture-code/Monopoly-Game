"""
UI components for the Monopoly game.
Provides buttons, text inputs, and other interactive elements.
"""
import pygame
import random
from typing import Callable, Optional, List, Tuple

from client.ui.theme import COLORS
from client.ui.effects import BloodDrop

class HorrorButton:
    """A horror-themed button for pygame UI."""
    
    def __init__(self, x, y, width, height, text, color=COLORS["button_color"], 
                 hover_color=COLORS["button_hover"], text_color=COLORS["button_text"],
                 font_size=24, action: Optional[Callable] = None, disabled=False, horror_style=True):
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
        self.blood_drops: List[BloodDrop] = []
    
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
        self.blood_drips: List[BloodDrop] = []
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
    
    def set_values(self, values: Tuple[int, int]):
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


__all__ = ['HorrorButton', 'TextInput', 'PlayerCard', 'DiceDisplay']
