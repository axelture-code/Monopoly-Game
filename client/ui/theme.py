"""
Theme settings for the Monopoly game UI.
Defines colors, fonts, and other visual styling.
"""

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

# Player token colors list for easy access
PLAYER_COLORS = [
    COLORS["player1"], COLORS["player2"], COLORS["player3"],
    COLORS["player4"], COLORS["player5"], COLORS["player6"]
]

# Font settings
FONTS = {
    "title": {"name": "Arial Black", "size": 54, "bold": True},  # Reduced size
    "subtitle": {"name": "Arial", "size": 24, "italic": True},
    "button": {"name": "Arial", "size": 24, "bold": True},
    "text": {"name": "Arial", "size": 18, "bold": False},
    "small": {"name": "Arial", "size": 14, "bold": False}
}

__all__ = ['COLORS', 'PLAYER_COLORS', 'FONTS']
