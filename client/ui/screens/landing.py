"""Landing screen for the Monopoly game."""

import pygame
from client.ui.screens.base import Screen
from client.ui.theme import COLORS
from client.ui.components import HorrorButton
from client.ui.effects import BloodTitle, HauntedSkyline

class LandingScreen(Screen):
    """Landing screen with title and start button."""

    def __init__(self, ui):
        super().__init__(ui)
        self._create_elements()

        # Create background elements
        self.skyline = HauntedSkyline(self.width, self.height)

    def _create_elements(self):
        """Create UI elements for the landing screen."""
        # Title with blood dripping effect - with larger font size
        self.elements["title"] = BloodTitle(
            self.width // 2,
            self.height // 3,
            "REAL ESTATE MASSACRE",
            font_size=64,
            multiline=True
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

    def draw(self, surface):
        """Draw the screen on the given surface."""
        # Draw the haunted skyline background
        self.skyline.draw(surface)

        # Draw the title with blood dripping effect
        if "title" in self.elements:
            self.elements["title"].draw(surface)
        
        # Draw the start button
        if "start_button" in self.elements:
            self.elements["start_button"].draw(surface)
    def draw(self, surface):
        """Draw the screen on the given surface."""
        # Draw the haunted skyline background
        self.skyline.draw(surface)

        
        # Draw the title with blood dripping effect
        if "title" in self.elements:
            self.elements["title"].draw(surface)
        
        # Draw the start button
        if "start_button" in self.elements:
            self.elements["start_button"].draw(surface)
