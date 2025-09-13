"""
Visual effects for the Monopoly game UI.
Provides animations and special effects.
"""
import pygame
import random
import math
import os
from client.ui.theme import COLORS

class BloodDrop:
    """A blood drop for animation effects."""
    
    def __init__(self, x, y, speed=1, size=5, thickness=2):
        self.x = x
        self.y = y
        self.orig_x = x
        self.orig_y = y
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


class HauntedHouse:
    """A haunted house silhouette for the background."""
    
    def __init__(self, x, y, width, height, color=COLORS["shadow"]):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.window_color = COLORS["fresh_blood"]
        self.window_alpha = 100
        self.window_alpha_change = 0.2
        self.window_alpha_direction = 1
        self.time = 0
        
    def update(self):
        """Update the house animation."""
        # Slowly pulse the windows
        self.time += 0.01
        self.window_alpha += self.window_alpha_direction * self.window_alpha_change
        
        if self.window_alpha > 180:
            self.window_alpha = 180
            self.window_alpha_direction = -1
        elif self.window_alpha < 40:
            self.window_alpha = 40
            self.window_alpha_direction = 1
    
    def draw(self, surface):
        """Draw the haunted house silhouette."""
        # Main house body
        house_rect = pygame.Rect(self.x, self.y - self.height, self.width, self.height)
        pygame.draw.rect(surface, self.color, house_rect)
        
        # Roof (triangle)
        roof_points = [
            (self.x, self.y - self.height),
            (self.x + self.width // 2, self.y - self.height - self.height // 2),
            (self.x + self.width, self.y - self.height)
        ]
        pygame.draw.polygon(surface, self.color, roof_points)
        
        # Chimney
        chimney_width = self.width // 8
        chimney_height = self.height // 3
        chimney_x = self.x + self.width - self.width // 4
        chimney_y = self.y - self.height - self.height // 4
        pygame.draw.rect(surface, self.color, (chimney_x, chimney_y - chimney_height, chimney_width, chimney_height))
        
        # Door
        door_width = self.width // 4
        door_height = self.height // 2
        door_x = self.x + (self.width - door_width) // 2
        door_y = self.y - door_height
        pygame.draw.rect(surface, COLORS["dark_blood"], (door_x, door_y, door_width, door_height))
        
        # Door knob
        knob_x = door_x + door_width - door_width // 4
        knob_y = door_y + door_height // 2
        pygame.draw.circle(surface, COLORS["bone"], (knob_x, knob_y), 3)
        
        # Windows (with glowing effect)
        window_size = self.width // 6
        window_padding = window_size // 2
        
        # Create a surface with alpha for the glow
        window_surface = pygame.Surface((window_size, window_size), pygame.SRCALPHA)
        
        # Draw the window with current alpha
        window_color_with_alpha = (*self.window_color, int(self.window_alpha))
        pygame.draw.rect(window_surface, window_color_with_alpha, (0, 0, window_size, window_size))
        
        # Add window crossbars
        pygame.draw.line(window_surface, COLORS["black"], (window_size//2, 0), (window_size//2, window_size), 2)
        pygame.draw.line(window_surface, COLORS["black"], (0, window_size//2), (window_size, window_size//2), 2)
        
        # Left window
        window_left_x = self.x + window_padding
        window_y = self.y - self.height + window_padding
        surface.blit(window_surface, (window_left_x, window_y))
        
        # Right window
        window_right_x = self.x + self.width - window_padding - window_size
        surface.blit(window_surface, (window_right_x, window_y))
        
        # Attic window (in the roof)
        attic_window_size = window_size // 2
        attic_window_x = self.x + (self.width - attic_window_size) // 2
        attic_window_y = self.y - self.height - self.height // 4
        
        # Create a circular window for the attic
        attic_surface = pygame.Surface((attic_window_size, attic_window_size), pygame.SRCALPHA)
        pygame.draw.circle(attic_surface, window_color_with_alpha, 
                          (attic_window_size//2, attic_window_size//2), 
                          attic_window_size//2)
        surface.blit(attic_surface, (attic_window_x, attic_window_y))


class HauntedSkyline:
    """A background skyline of haunted buildings."""
    
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.buildings = []
        self.fog_particles = []
        self.moon_x = screen_width * 0.8
        self.moon_y = screen_height * 0.2
        self.moon_size = 60
        self.moon_glow_size = 80
        self.moon_alpha = 180
        self.stars = []
        self.clouds = []
        self.time = 0
        
        # Load moon texture if available
        self.moon_texture = self._load_moon_texture()
        
        # Generate buildings
        self._generate_buildings()
        
        # Generate stars
        self._generate_stars()
        
        # Generate clouds
        self._generate_clouds(5)
        
        # Generate initial fog
        self._generate_fog(20)
    
    def _load_moon_texture(self):
        """Load moon texture image or create a fallback texture."""
        try:
            # Try to load moon image from assets folder
            moon_path = os.path.join('assets', 'images', 'moon.png')
            if os.path.exists(moon_path):
                return pygame.image.load(moon_path).convert_alpha()
            
            # If file doesn't exist, create a procedural moon texture
            size = 128
            texture = pygame.Surface((size, size), pygame.SRCALPHA)
            
            # Base moon circle
            pygame.draw.circle(texture, (230, 230, 210), (size//2, size//2), size//2)
            
            # Add craters and details to make it look like a moon
            for _ in range(15):
                crater_x = random.randint(size//4, 3*size//4)
                crater_y = random.randint(size//4, 3*size//4)
                crater_size = random.randint(5, 15)
                crater_color = (200, 200, 190, 150)
                pygame.draw.circle(texture, crater_color, (crater_x, crater_y), crater_size)
            
            # Add some shadow gradients
            shadow_surf = pygame.Surface((size, size), pygame.SRCALPHA)
            for i in range(size//2):
                alpha = 100 - (i * 2)
                if alpha > 0:
                    pygame.draw.circle(shadow_surf, (20, 20, 30, alpha), (size//4, size//2), size//2 - i)
            
            texture.blit(shadow_surf, (0, 0))
            return texture
        except Exception as e:
            print(f"Error loading moon texture: {e}")
            return None
    
    def _generate_clouds(self, count):
        """Generate atmospheric clouds."""
        for _ in range(count):
            x = random.randint(-100, self.screen_width)
            y = random.randint(50, self.screen_height // 3)
            width = random.randint(100, 300)
            height = random.randint(30, 80)
            speed = random.uniform(0.1, 0.3)
            alpha = random.randint(20, 60)
            
            self.clouds.append({
                "x": x,
                "y": y,
                "width": width,
                "height": height,
                "speed": speed,
                "alpha": alpha,
                "bumps": random.randint(3, 6)
            })
    
    def _generate_stars(self):
        """Generate stars in the night sky."""
        self.stars = []
        
        # Create a bunch of stars with more variety
        for _ in range(150):
            x = random.randint(0, self.screen_width)
            y = random.randint(0, self.screen_height // 2)  # Only in top half
            size = random.uniform(0.5, 2.5)
            twinkle_speed = random.uniform(0.01, 0.05)
            brightness = random.uniform(0.7, 1.0)
            color_shift = random.randint(0, 30)
            color = (
                min(255, 255 - color_shift), 
                min(255, 255 - color_shift // 2), 
                min(255, 255 - color_shift // 3)
            )
            
            self.stars.append({
                "x": x,
                "y": y,
                "size": size,
                "twinkle_speed": twinkle_speed,
                "phase": random.uniform(0, 2 * math.pi),  # Random starting phase
                "brightness": brightness,
                "color": color
            })
        
        # Add a few shooting stars that appear occasionally
        self.shooting_star_timer = 0
        self.shooting_star = None
    
    def _generate_fog(self, count):
        """Generate fog particles."""
        for _ in range(count):
            x = random.randint(0, self.screen_width)
            y = random.randint(self.screen_height - 100, self.screen_height)
            size = random.randint(50, 150)
            speed = random.uniform(0.1, 0.3)
            
            self.fog_particles.append({
                "x": x,
                "y": y,
                "size": size,
                "speed": speed,
                "alpha": random.randint(20, 60)
            })
    
    def _generate_buildings(self):
        """Generate a skyline of buildings."""
        self.buildings = []
        
        # Start from the left edge of the screen
        current_x = 0
        
        # Continue adding buildings until we fill the screen width
        while current_x < self.screen_width:
            # Vary the height
            height = random.randint(100, 250)
            width = random.randint(60, 120)
            
            # Ensure the building doesn't extend too far off screen
            if current_x + width > self.screen_width + 50:
                # Adjust width to fit within screen with some overlap allowed
                width = max(60, self.screen_width + 50 - current_x)
            
            # Decide if this should be a house or a building
            if random.random() < 0.3:  # 30% chance for a house
                self.buildings.append(HauntedHouse(
                    current_x, self.screen_height, width, height
                ))
            else:
                # For buildings, just add a rectangle
                building = {
                    "x": current_x,
                    "y": self.screen_height,
                    "width": width,
                    "height": height,
                    "windows": []
                }
                
                # Add windows to the building
                window_size = 10
                window_spacing = 20
                num_floors = height // window_spacing
                num_columns = width // window_spacing
                
                for floor in range(num_floors):
                    for col in range(num_columns):
                        # Not every window position should have a window
                        if random.random() < 0.7:  # 70% chance
                            window_x = current_x + col * window_spacing + (window_spacing - window_size) // 2
                            window_y = self.screen_height - height + floor * window_spacing + (window_spacing - window_size) // 2
                            
                            # Randomize the glow of the window
                            glow = random.randint(0, 180)
                            glow_speed = random.uniform(0.1, 0.5)
                            glow_direction = 1 if random.random() < 0.5 else -1
                            
                            building["windows"].append({
                                "x": window_x,
                                "y": window_y,
                                "size": window_size,
                                "glow": glow,
                                "glow_speed": glow_speed,
                                "glow_direction": glow_direction
                            })
                
                self.buildings.append(building)
            
            # Move to the position for the next building with a small gap
            gap = random.randint(5, 15)  # Small random gap between buildings
            current_x += width + gap
    
    def update(self):
        """Update the skyline animation."""
        self.time += 0.01
        
        # Update building windows
        for building in self.buildings:
            if isinstance(building, HauntedHouse):
                building.update()
            elif "windows" in building:
                for window in building["windows"]:
                    window["glow"] += window["glow_direction"] * window["glow_speed"]
                    
                    if window["glow"] > 180:
                        window["glow"] = 180
                        window["glow_direction"] = -1
                    elif window["glow"] < 20:
                        window["glow"] = 20
                        window["glow_direction"] = 1
        
        # Update clouds
        for cloud in self.clouds:
            cloud["x"] += cloud["speed"]
            if cloud["x"] > self.screen_width + 100:
                cloud["x"] = -cloud["width"]
                cloud["y"] = random.randint(50, self.screen_height // 3)
        
        # Update fog particles
        for particle in self.fog_particles[:]:
            particle["x"] -= particle["speed"]
            
            # Remove particles that go off screen
            if particle["x"] + particle["size"] < 0:
                self.fog_particles.remove(particle)
        
        # Add new fog particles occasionally
        if random.random() < 0.02:  # 2% chance per frame
            self._generate_fog(1)
        
        # Occasionally add a shooting star
        self.shooting_star_timer -= 1
        if self.shooting_star_timer <= 0 and random.random() < 0.02:
            self.shooting_star = {
                "x": random.randint(0, self.screen_width),
                "y": random.randint(0, self.screen_height // 3),
                "angle": random.uniform(math.pi/4, math.pi/2),
                "speed": random.uniform(5, 15),
                "length": random.randint(30, 80),
                "life": random.randint(20, 40)
            }
            self.shooting_star_timer = random.randint(100, 300)
            
        # Update existing shooting star
        if self.shooting_star:
            self.shooting_star["life"] -= 1
            if self.shooting_star["life"] <= 0:
                self.shooting_star = None
    
    def draw(self, surface):
        """Draw the haunted skyline."""
        # Draw the night sky gradient
        sky_rect = pygame.Rect(0, 0, self.screen_width, self.screen_height)
        pygame.draw.rect(surface, COLORS["midnight"], sky_rect)
        
        # Add a subtle gradient from dark blue at top to darker at bottom
        gradient_surf = pygame.Surface((self.screen_width, self.screen_height // 2), pygame.SRCALPHA)
        for y in range(self.screen_height // 2):
            alpha = 50 - int(y / (self.screen_height // 2) * 50)
            pygame.draw.line(gradient_surf, (0, 20, 50, alpha), (0, y), (self.screen_width, y))
        surface.blit(gradient_surf, (0, 0))
        
        # Draw stars
        for star in self.stars:
            # Calculate twinkle effect
            twinkle = star["brightness"] * (0.5 + 0.5 * math.sin(self.time * star["twinkle_speed"] + star["phase"]))
            size = star["size"] * twinkle
            
            # Calculate color with twinkle
            color = tuple(min(255, int(c * twinkle)) for c in star["color"])
            
            # Draw the star as a small circle
            pygame.draw.circle(
                surface, 
                color, 
                (int(star["x"]), int(star["y"])), 
                size
            )
            
            # Add a subtle glow for brighter stars
            if star["size"] > 1.5:
                glow_size = size * 2
                glow_surf = pygame.Surface((int(glow_size*2), int(glow_size*2)), pygame.SRCALPHA)
                glow_color = (*color[:3], 50)  # Semi-transparent
                pygame.draw.circle(glow_surf, glow_color, (int(glow_size), int(glow_size)), int(glow_size))
                surface.blit(glow_surf, (int(star["x"] - glow_size), int(star["y"] - glow_size)))
        
        # Draw shooting star if active
        if self.shooting_star:
            ss = self.shooting_star
            # Calculate end point based on angle and length
            end_x = ss["x"] - math.cos(ss["angle"]) * ss["length"]
            end_y = ss["y"] + math.sin(ss["angle"]) * ss["length"]
            
            # Move the shooting star
            ss["x"] += math.cos(ss["angle"]) * ss["speed"]
            ss["y"] -= math.sin(ss["angle"]) * ss["speed"]
            
            # Draw the shooting star trail
            fade_factor = min(1.0, ss["life"] / 20.0)
            for i in range(10):
                segment_start_x = ss["x"] - (i/10) * math.cos(ss["angle"]) * ss["length"]
                segment_start_y = ss["y"] + (i/10) * math.sin(ss["angle"]) * ss["length"]
                segment_end_x = ss["x"] - ((i+1)/10) * math.cos(ss["angle"]) * ss["length"]
                segment_end_y = ss["y"] + ((i+1)/10) * math.sin(ss["angle"]) * ss["length"]
                
                alpha = int(255 * (1 - i/10) * fade_factor)
                color = (255, 255, 255, alpha)
                
                pygame.draw.line(
                    surface, 
                    color, 
                    (segment_start_x, segment_start_y), 
                    (segment_end_x, segment_end_y), 
                    2
                )
        
        # Draw clouds behind the moon
        for cloud in self.clouds:
            cloud_surf = pygame.Surface((cloud["width"], cloud["height"]), pygame.SRCALPHA)
            
            # Draw cloud as a series of overlapping circles
            base_y = cloud["height"] // 2
            bump_width = cloud["width"] // cloud["bumps"]
            
            for i in range(cloud["bumps"]):
                bump_x = i * bump_width + bump_width // 2
                bump_radius = random.randint(cloud["height"] // 2, cloud["height"] - 10)
                cloud_color = (30, 30, 40, cloud["alpha"])
                pygame.draw.circle(cloud_surf, cloud_color, (bump_x, base_y), bump_radius)
            
            surface.blit(cloud_surf, (cloud["x"], cloud["y"]))
        
        # Draw the moon with texture or procedural effect
        if self.moon_texture:
            # Draw moon glow
            glow_surf = pygame.Surface((self.moon_glow_size*2, self.moon_glow_size*2), pygame.SRCALPHA)
            for radius in range(self.moon_glow_size, self.moon_size, -1):
                alpha = int(50 * (radius - self.moon_size) / (self.moon_glow_size - self.moon_size))
                pygame.draw.circle(glow_surf, (255, 255, 220, alpha), 
                                  (self.moon_glow_size, self.moon_glow_size), radius)
            
            surface.blit(glow_surf, (int(self.moon_x - self.moon_glow_size), 
                                     int(self.moon_y - self.moon_glow_size)))
            
            # Draw the textured moon
            scaled_moon = pygame.transform.scale(self.moon_texture, 
                                                (self.moon_size*2, self.moon_size*2))
            surface.blit(scaled_moon, (int(self.moon_x - self.moon_size), 
                                      int(self.moon_y - self.moon_size)))
        else:
            # Fallback to a circle if texture loading failed
            # Draw moon glow
            glow_surf = pygame.Surface((self.moon_glow_size*2, self.moon_glow_size*2), pygame.SRCALPHA)
            for radius in range(self.moon_glow_size, self.moon_size, -1):
                alpha = int(30 * (radius - self.moon_size) / (self.moon_glow_size - self.moon_size))
                pygame.draw.circle(glow_surf, (255, 255, 220, alpha), 
                                  (self.moon_glow_size, self.moon_glow_size), radius)
            
            surface.blit(glow_surf, (int(self.moon_x - self.moon_glow_size), 
                                     int(self.moon_y - self.moon_glow_size)))
            
            # Draw the moon circle
            pygame.draw.circle(surface, COLORS["bone"], 
                              (int(self.moon_x), int(self.moon_y)), self.moon_size)
        
        # Draw buildings
        for building in self.buildings:
            if isinstance(building, HauntedHouse):
                building.draw(surface)
            else:
                # Draw the building rectangle
                pygame.draw.rect(
                    surface,
                    COLORS["shadow"],
                    (building["x"], building["y"] - building["height"], building["width"], building["height"])
                )
                
                # Draw windows
                for window in building["windows"]:
                    window_color = (*COLORS["fresh_blood"], int(window["glow"]))
                    window_surface = pygame.Surface((window["size"], window["size"]), pygame.SRCALPHA)
                    pygame.draw.rect(window_surface, window_color, (0, 0, window["size"], window["size"]))
                    surface.blit(window_surface, (window["x"], window["y"]))
        
        # Draw clouds that might be in front of buildings
        for cloud in self.clouds:
            if cloud["y"] > self.screen_height // 4:
                cloud_surf = pygame.Surface((cloud["width"], cloud["height"]), pygame.SRCALPHA)
                
                # Draw cloud as a series of overlapping circles
                base_y = cloud["height"] // 2
                bump_width = cloud["width"] // cloud["bumps"]
                
                for i in range(cloud["bumps"]):
                    bump_x = i * bump_width + bump_width // 2
                    bump_radius = random.randint(cloud["height"] // 2, cloud["height"] - 10)
                    cloud_color = (30, 30, 40, cloud["alpha"])
                    pygame.draw.circle(cloud_surf, cloud_color, (bump_x, base_y), bump_radius)
                
                surface.blit(cloud_surf, (cloud["x"], cloud["y"]))
        
        # Draw fog particles
        for particle in self.fog_particles:
            fog_surface = pygame.Surface((particle["size"], particle["size"]), pygame.SRCALPHA)
            fog_color = (*COLORS["fog"][:3], particle["alpha"])  # Use RGB from fog color but our own alpha
            pygame.draw.circle(fog_surface, fog_color, (particle["size"]//2, particle["size"]//2), particle["size"]//2)
            surface.blit(fog_surface, (particle["x"], particle["y"]))


__all__ = ['BloodDrop', 'BloodTitle', 'HauntedSkyline']
  