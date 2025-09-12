"""Base screen class for all UI screens."""

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
