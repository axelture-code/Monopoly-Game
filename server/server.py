"""
Monopoly game server implementation.
Handles game logic, state management, and client connections.
"""
import json
import socket
import threading
import random
import time
import logging
from typing import Dict, List, Optional, Any

# Import from our other modules
from common.messages import Message, MessageType, GameStateMessage
from server.game_state import GameState, Player

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('monopoly-server')

class MonopolyServer:
    """Main server class for the Monopoly game."""
    
    def __init__(self, host: str = '0.0.0.0', port: int = 5555):
        self.host = host
        self.port = port
        self.game_state = GameState()
        self.clients: Dict[str, socket.socket] = {}
        self.client_addresses: Dict[str, str] = {}
        self.server_socket = None
        self.is_running = False
        self.lock = threading.Lock()  # For thread-safe access to game state
    
    def start(self):
        """Start the server and listen for connections."""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            self.is_running = True
            
            logger.info(f"Server started on {self.host}:{self.port}")
            
            # Start accepting client connections
            accept_thread = threading.Thread(target=self._accept_connections)
            accept_thread.daemon = True
            accept_thread.start()
            
            # Main server loop for game logic
            self._main_loop()
            
        except Exception as e:
            logger.error(f"Server error: {str(e)}")
            self.stop()
    
    def stop(self):
        """Stop the server and close all connections."""
        self.is_running = False
        
        # Close all client connections
        for client_id, client_socket in self.clients.items():
            try:
                client_socket.close()
            except:
                pass
        
        # Close server socket
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
                
        logger.info("Server stopped")
    
    def _accept_connections(self):
        """Accept client connections in a separate thread."""
        while self.is_running:
            try:
                client_socket, client_address = self.server_socket.accept()
                logger.info(f"New connection from {client_address[0]}:{client_address[1]}")
                
                # Start a new thread to handle this client
                client_thread = threading.Thread(
                    target=self._handle_client,
                    args=(client_socket, client_address)
                )
                client_thread.daemon = True
                client_thread.start()
                
            except Exception as e:
                if self.is_running:
                    logger.error(f"Error accepting connection: {str(e)}")
    
    def _handle_client(self, client_socket: socket.socket, address):
        """Handle communication with a connected client."""
        client_id = None
        
        try:
            # First message should be a connection message with player name
            data = client_socket.recv(4096)
            if not data:
                return
                
            message = Message.from_json(data.decode('utf-8'))
            if message.type != MessageType.CONNECT:
                logger.warning(f"First message from {address} was not CONNECT")
                return
                
            player_name = message.data.get("player_name", f"Player_{len(self.clients) + 1}")
            client_id = str(hash(f"{address[0]}:{address[1]}:{time.time()}"))
            
            with self.lock:
                # Add new player to game state
                self.game_state.add_player(client_id, player_name)
                # Store client socket
                self.clients[client_id] = client_socket
                self.client_addresses[client_id] = f"{address[0]}:{address[1]}"
            
            logger.info(f"Player '{player_name}' (ID: {client_id}) connected")
            
            # Send current game state to the new client
            self._broadcast_game_state()
            
            # Main loop for receiving messages from this client
            while self.is_running:
                data = client_socket.recv(4096)
                if not data:
                    break
                    
                message = Message.from_json(data.decode('utf-8'))
                self._process_message(client_id, message)
                
        except Exception as e:
            logger.error(f"Error handling client {client_id}: {str(e)}")
        finally:
            # Clean up when client disconnects
            if client_id and client_id in self.clients:
                with self.lock:
                    self.game_state.remove_player(client_id)
                    del self.clients[client_id]
                    del self.client_addresses[client_id]
                    
                logger.info(f"Client {client_id} disconnected")
                self._broadcast_game_state()
    
    def _process_message(self, client_id: str, message: Message):
        """Process a message received from a client."""
        logger.debug(f"Processing message type {message.type} from {client_id}")
        
        with self.lock:
            if message.type == MessageType.PLAYER_ACTION:
                action = message.data.get("action")
                action_data = message.data.get("action_data", {})
                
                # Process different actions
                if action == "roll_dice":
                    self._handle_dice_roll(client_id)
                elif action == "buy_property":
                    property_id = action_data.get("property_id")
                    self._handle_buy_property(client_id, property_id)
                elif action == "end_turn":
                    self._handle_end_turn(client_id)
                # Add more action handlers here
            
            # After processing, broadcast updated game state
            self._broadcast_game_state()
    
    def _handle_dice_roll(self, player_id: str):
        """Handle a dice roll action."""
        # Check if it's this player's turn
        if self.game_state.current_player_id != player_id:
            logger.warning(f"Player {player_id} tried to roll dice but it's not their turn")
            return
            
        # Roll the dice
        dice1 = random.randint(1, 6)
        dice2 = random.randint(1, 6)
        is_doubles = dice1 == dice2
        steps = dice1 + dice2
        
        # Update game state
        self.game_state.dice_roll = (dice1, dice2)
        
        # Move the player
        new_position = self.game_state.move_player(player_id, steps)
        
        logger.info(f"Player {player_id} rolled {dice1}+{dice2}={steps} and moved to position {new_position}")
        
        # For physical board game, we don't need to handle landing on spaces
        # as that will be done by the players in real life
    
    def _handle_end_turn(self, player_id: str):
        """Handle an end turn action."""
        # Check if it's this player's turn
        if self.game_state.current_player_id != player_id:
            logger.warning(f"Player {player_id} tried to end turn but it's not their turn")
            return
            
        # Move to next player
        player_ids = list(self.game_state.players.keys())
        if not player_ids:
            return
            
        current_idx = player_ids.index(player_id) if player_id in player_ids else -1
        next_idx = (current_idx + 1) % len(player_ids)
        self.game_state.current_player_id = player_ids[next_idx]
        self.game_state.turn_number += 1
        
        # Reset dice roll for next player
        self.game_state.dice_roll = (0, 0)
        
        logger.info(f"Turn ended. Next player: {self.game_state.current_player_id}")
    
    def _broadcast_game_state(self):
        """Send current game state to all connected clients."""
        game_state_dict = self.game_state.to_dict()
        message = GameStateMessage(game_state_dict)
        json_data = message.to_json()
        
        # Send to all clients
        for client_id, client_socket in list(self.clients.items()):
            try:
                client_socket.sendall(json_data.encode('utf-8'))
            except Exception as e:
                logger.error(f"Error sending to client {client_id}: {str(e)}")
    
    def _main_loop(self):
        """Main server loop for game logic."""
        while self.is_running:
            # This loop handles game logic that's not directly tied to client actions
            # For example, timers, automated events, etc.
            
            time.sleep(1)  # Sleep to prevent CPU hogging

if __name__ == "__main__":
    server = MonopolyServer()
    try:
        server.start()
    except KeyboardInterrupt:
        print("Server shutting down...")
    finally:
        server.stop()