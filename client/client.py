"""
Client implementation for the Monopoly game.
Handles connecting to server and sending/receiving game messages.
"""
import socket
import threading
import time
import logging
from typing import Dict, List, Optional, Callable, Any

# Import from our other modules
from common.messages import Message, MessageType, ConnectMessage, PlayerActionMessage
from client.ui import MonopolyUI

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('monopoly-client')

class MonopolyClient:
    """Client for the Monopoly game."""
    
    def __init__(self, server_host: str = 'localhost', server_port: int = 5555):
        self.server_host = server_host
        self.server_port = server_port
        self.client_socket = None
        self.is_connected = False
        self.player_name = None
        self.player_id = None
        self.game_state = {}
        self.ui = MonopolyUI(self)
        
        # Callbacks for different message types
        self.message_handlers = {
            MessageType.GAME_STATE: self._handle_game_state,
            MessageType.ERROR: self._handle_error,
            # Add more handlers as needed
        }
    
    def connect(self, player_name: str) -> bool:
        """Connect to the Monopoly server."""
        self.player_name = player_name
        
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((self.server_host, self.server_port))
            self.is_connected = True
            
            # Send connect message
            connect_msg = ConnectMessage(player_name)
            self._send_message(connect_msg)
            
            # Start listening for server messages
            receive_thread = threading.Thread(target=self._receive_messages)
            receive_thread.daemon = True
            receive_thread.start()
            
            logger.info(f"Connected to server at {self.server_host}:{self.server_port}")
            return True
            
        except Exception as e:
            logger.error(f"Connection error: {str(e)}")
            self.disconnect()
            return False
    
    def register_player(self, player_name: str) -> bool:
        """Register a player in the game."""
        if not self.is_connected:
            logger.error("Cannot register player: not connected to server")
            return False
            
        # Send registration message
        connect_msg = ConnectMessage(player_name)
        return self._send_message(connect_msg)
    
    def disconnect(self):
        """Disconnect from the server."""
        self.is_connected = False
        
        if self.client_socket:
            try:
                self.client_socket.close()
            except:
                pass
            self.client_socket = None
            
        logger.info("Disconnected from server")
    
    def _send_message(self, message: Message) -> bool:
        """Send a message to the server."""
        if not self.is_connected or not self.client_socket:
            logger.error("Cannot send message: not connected")
            return False
            
        try:
            json_data = message.to_json()
            self.client_socket.sendall(json_data.encode('utf-8'))
            return True
        except Exception as e:
            logger.error(f"Error sending message: {str(e)}")
            self.disconnect()
            return False
    
    def _receive_messages(self):
        """Continuously receive messages from the server."""
        while self.is_connected:
            try:
                data = self.client_socket.recv(4096)
                if not data:
                    logger.warning("Server closed connection")
                    break
                    
                message = Message.from_json(data.decode('utf-8'))
                self._process_message(message)
                
            except Exception as e:
                if self.is_connected:
                    logger.error(f"Error receiving message: {str(e)}")
                    break
        
        # If we exit the loop, ensure we're disconnected
        self.disconnect()
    
    def _process_message(self, message: Message):
        """Process a message received from the server."""
        logger.debug(f"Received message type: {message.type}")
        
        # Call the appropriate handler for this message type
        if message.type in self.message_handlers:
            self.message_handlers[message.type](message)
        else:
            logger.warning(f"No handler for message type: {message.type}")
    
    def _handle_game_state(self, message: Message):
        """Handle a game state update message."""
        self.game_state = message.data
        
        # Extract player ID if we don't have it yet
        if not self.player_id and self.player_name:
            for player_id, player_data in self.game_state.get("players", {}).items():
                if player_data.get("name") == self.player_name:
                    self.player_id = player_id
                    logger.info(f"Received player ID: {self.player_id}")
                    break
        
        # Update UI with new game state
        self.ui.update_game_state(self.game_state)
    
    def _handle_error(self, message: Message):
        """Handle error messages from the server."""
        error_msg = message.data.get("error", "Unknown error")
        logger.error(f"Server error: {error_msg}")
        self.ui.show_error(error_msg)
    
    # Game action methods that can be called from UI
    
    def roll_dice(self):
        """Send a request to roll the dice."""
        action_msg = PlayerActionMessage(
            player_id=self.player_id,
            action="roll_dice"
        )
        return self._send_message(action_msg)
    
    def buy_property(self, property_id: int):
        """Send a request to buy a property."""
        action_msg = PlayerActionMessage(
            player_id=self.player_id,
            action="buy_property",
            action_data={"property_id": property_id}
        )
        return self._send_message(action_msg)
    
    def end_turn(self):
        """Send a request to end the current turn."""
        action_msg = PlayerActionMessage(
            player_id=self.player_id,
            action="end_turn"
        )
        return self._send_message(action_msg)
    
    def start(self):
        """Start the client application."""
        self.ui.run()

if __name__ == "__main__":
    client = MonopolyClient()
    try:
        client.start()
    except KeyboardInterrupt:
        print("Client shutting down...")
    finally:
        client.disconnect()