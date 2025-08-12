import random
import time
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class Direction(Enum):
    NORTH = "north"
    SOUTH = "south"
    EAST = "east"
    WEST = "west"

class ItemType(Enum):
    WEAPON = "weapon"
    ARMOR = "armor"
    POTION = "potion"
    KEY = "key"
    TREASURE = "treasure"

@dataclass
class Item:
    name: str
    description: str
    item_type: ItemType
    damage: int = 0
    defense: int = 0
    healing: int = 0

@dataclass
class Room:
    name: str
    description: str
    exits: Dict[Direction, str]
    items: List[Item]
    enemies: List[Dict]
    visited: bool = False

@dataclass
class Player:
    name: str
    health: int = 100
    max_health: int = 100
    inventory: List[Item] = None
    current_room: str = "entrance"
    gold: int = 0
    level: int = 1
    experience: int = 0
    
    def __post_init__(self):
        if self.inventory is None:
            self.inventory = []

class ASCIIGame:
    def __init__(self):
        self.player = None
        self.game_started = False
        self.game_over = False
        self.rooms = self._create_world()
        self.current_enemy = None
        
    def _create_world(self) -> Dict[str, Room]:
        """Create the game world with rooms, items, and enemies"""
        rooms = {}
        
        # Entrance
        rooms["entrance"] = Room(
            name="Cave Entrance",
            description="""
╔══════════════════════════════════════════════════════════════╗
║                        CAVE ENTRANCE                         ║
╠══════════════════════════════════════════════════════════════╣
║  You stand at the entrance of a mysterious cave. The air    ║
║  is cool and damp. Sunlight filters in from behind you,     ║
║  but ahead lies darkness. You can hear the sound of         ║
║  dripping water echoing from within.                        ║
║                                                              ║
║  Items: A rusty sword lies on the ground                    ║
║  Exits: north                                                ║
╚══════════════════════════════════════════════════════════════╝
            """,
            exits={Direction.NORTH: "main_cavern"},
            items=[Item("Rusty Sword", "A basic sword with some rust", ItemType.WEAPON, damage=5)],
            enemies=[]
        )
        
        # Main Cavern
        rooms["main_cavern"] = Room(
            name="Main Cavern",
            description="""
╔══════════════════════════════════════════════════════════════╗
║                        MAIN CAVERN                           ║
╠══════════════════════════════════════════════════════════════╣
║  A large cavern stretches before you. Stalactites hang      ║
║  from the ceiling like stone icicles, and the floor is      ║
║  uneven with scattered rocks. The air is thick with         ║
║  mystery and danger.                                         ║
║                                                              ║
║  Items: Health potion                                        ║
║  Exits: north, south, east, west                            ║
╚══════════════════════════════════════════════════════════════╝
            """,
            exits={
                Direction.NORTH: "treasure_room",
                Direction.SOUTH: "entrance",
                Direction.EAST: "goblin_camp",
                Direction.WEST: "armory"
            },
            items=[Item("Health Potion", "Restores 30 health", ItemType.POTION, healing=30)],
            enemies=[{"name": "Cave Bat", "health": 20, "damage": 8, "exp": 15}]
        )
        
        # Goblin Camp
        rooms["goblin_camp"] = Room(
            name="Goblin Camp",
            description="""
╔══════════════════════════════════════════════════════════════╗
║                       GOBLIN CAMP                            ║
╠══════════════════════════════════════════════════════════════╣
║  A small camp with scattered bones and crude weapons.       ║
║  The remains of a campfire smolder in the center. This      ║
║  place reeks of goblin activity.                            ║
║                                                              ║
║  Items: Leather armor, Gold coins                           ║
║  Exits: west                                                 ║
╚══════════════════════════════════════════════════════════════╝
            """,
            exits={Direction.WEST: "main_cavern"},
            items=[
                Item("Leather Armor", "Basic leather protection", ItemType.ARMOR, defense=10),
                Item("Gold Coins", "Shiny gold coins", ItemType.TREASURE)
            ],
            enemies=[{"name": "Goblin Warrior", "health": 35, "damage": 12, "exp": 25}]
        )
        
        # Armory
        rooms["armory"] = Room(
            name="Ancient Armory",
            description="""
╔══════════════════════════════════════════════════════════════╗
║                     ANCIENT ARMORY                           ║
╠══════════════════════════════════════════════════════════════╣
║  An old armory with rusted weapon racks and armor stands.   ║
║  Most equipment has decayed, but a few items remain         ║
║  in usable condition.                                        ║
║                                                              ║
║  Items: Steel sword, Iron helmet                            ║
║  Exits: east                                                 ║
╚══════════════════════════════════════════════════════════════╝
            """,
            exits={Direction.EAST: "main_cavern"},
            items=[
                Item("Steel Sword", "A well-crafted steel blade", ItemType.WEAPON, damage=15),
                Item("Iron Helmet", "Protective headgear", ItemType.ARMOR, defense=8)
            ],
            enemies=[]
        )
        
        # Treasure Room
        rooms["treasure_room"] = Room(
            name="Treasure Chamber",
            description="""
╔══════════════════════════════════════════════════════════════╗
║                    TREASURE CHAMBER                          ║
╠══════════════════════════════════════════════════════════════╣
║  A magnificent chamber filled with gold, jewels, and        ║
║  ancient artifacts. The walls sparkle with precious         ║
║  metals. This is the legendary treasure room!               ║
║                                                              ║
║  Items: Diamond sword, Golden armor, Treasure chest         ║
║  Exits: south                                               ║
╚══════════════════════════════════════════════════════════════╝
            """,
            exits={Direction.SOUTH: "main_cavern"},
            items=[
                Item("Diamond Sword", "A legendary blade", ItemType.WEAPON, damage=25),
                Item("Golden Armor", "Magnificent golden protection", ItemType.ARMOR, defense=20),
                Item("Treasure Chest", "Filled with gold and jewels", ItemType.TREASURE)
            ],
            enemies=[{"name": "Dragon Guardian", "health": 100, "damage": 20, "exp": 100}]
        )
        
        return rooms
    
    def start_game(self, player_name: str) -> str:
        """Start a new game with the given player name"""
        self.player = Player(name=player_name)
        self.game_started = True
        self.game_over = False
        self.current_enemy = None
        
        return f"""
╔══════════════════════════════════════════════════════════════╗
║                    WELCOME TO THE CAVE!                      ║
╠══════════════════════════════════════════════════════════════╣
║  Greetings, {player_name}! You have entered a mysterious     ║
║  cave filled with danger and treasure. Your quest is to     ║
║  explore the depths and find the legendary treasure!        ║
║                                                              ║
║  Commands:                                                   ║
║  - look: Examine your surroundings                          ║
║  - move [direction]: Move north/south/east/west             ║
║  - take [item]: Pick up an item                             ║
║  - inventory: Check your inventory                          ║
║  - status: Check your health and stats                      ║
║  - attack: Fight enemies                                    ║
║  - use [item]: Use an item                                  ║
║  - help: Show this help message                             ║
╚══════════════════════════════════════════════════════════════╝

{self._get_room_description()}
        """
    
    def _get_room_description(self) -> str:
        """Get the current room description"""
        if not self.game_started:
            return "Game not started. Use 'start_game' to begin."
        
        room = self.rooms[self.player.current_room]
        room.visited = True
        
        # Check for enemies
        if room.enemies and not self.current_enemy:
            self.current_enemy = random.choice(room.enemies).copy()
            return f"{room.description}\n\n⚠️  A {self.current_enemy['name']} appears! (Health: {self.current_enemy['health']})"
        
        return room.description
    
    def look(self) -> str:
        """Look around the current room"""
        if not self.game_started:
            return "Game not started. Use 'start_game' to begin."
        
        room = self.rooms[self.player.current_room]
        items_list = ", ".join([item.name for item in room.items]) if room.items else "None"
        exits_list = ", ".join([exit.value for exit in room.exits.keys()])
        
        return f"""
{self._get_room_description()}

Items in room: {items_list}
Available exits: {exits_list}
        """
    
    def move(self, direction: str) -> str:
        """Move in the specified direction"""
        if not self.game_started:
            return "Game not started. Use 'start_game' to begin."
        
        if self.current_enemy:
            return "You cannot move while in combat! Attack or flee first."
        
        try:
            dir_enum = Direction(direction.lower())
        except ValueError:
            return f"Invalid direction: {direction}. Use north, south, east, or west."
        
        current_room = self.rooms[self.player.current_room]
        if dir_enum not in current_room.exits:
            return f"You cannot go {direction} from here."
        
        self.player.current_room = current_room.exits[dir_enum]
        return f"You move {direction}.\n\n{self._get_room_description()}"
    
    def take(self, item_name: str) -> str:
        """Take an item from the current room"""
        if not self.game_started:
            return "Game not started. Use 'start_game' to begin."
        
        room = self.rooms[self.player.current_room]
        
        for item in room.items:
            if item.name.lower() == item_name.lower():
                self.player.inventory.append(item)
                room.items.remove(item)
                
                if item.item_type == ItemType.TREASURE:
                    if item.name == "Gold Coins":
                        self.player.gold += 50
                        return f"You picked up {item.name} and gained 50 gold!"
                    elif item.name == "Treasure Chest":
                        self.player.gold += 200
                        return f"You found a treasure chest! You gained 200 gold!"
                
                return f"You picked up {item.name}."
        
        return f"Item '{item_name}' not found in this room."
    
    def inventory(self) -> str:
        """Show player inventory"""
        if not self.game_started:
            return "Game not started. Use 'start_game' to begin."
        
        if not self.player.inventory:
            return "Your inventory is empty."
        
        items_list = "\n".join([f"- {item.name}: {item.description}" for item in self.player.inventory])
        return f"""
╔══════════════════════════════════════════════════════════════╗
║                        INVENTORY                             ║
╠══════════════════════════════════════════════════════════════╣
{items_list}
╚══════════════════════════════════════════════════════════════╝
        """
    
    def status(self) -> str:
        """Show player status"""
        if not self.game_started:
            return "Game not started. Use 'start_game' to begin."
        
        # Calculate total stats from equipped items
        total_damage = sum(item.damage for item in self.player.inventory if item.item_type == ItemType.WEAPON)
        total_defense = sum(item.defense for item in self.player.inventory if item.item_type == ItemType.ARMOR)
        
        return f"""
╔══════════════════════════════════════════════════════════════╗
║                         STATUS                               ║
╠══════════════════════════════════════════════════════════════╣
║  Name: {self.player.name}                                    ║
║  Health: {self.player.health}/{self.player.max_health}       ║
║  Level: {self.player.level}                                  ║
║  Experience: {self.player.experience}                        ║
║  Gold: {self.player.gold}                                    ║
║  Attack: {total_damage}                                      ║
║  Defense: {total_defense}                                    ║
║  Current Room: {self.rooms[self.player.current_room].name}   ║
╚══════════════════════════════════════════════════════════════╝
        """
    
    def attack(self) -> str:
        """Attack the current enemy"""
        if not self.game_started:
            return "Game not started. Use 'start_game' to begin."
        
        if not self.current_enemy:
            return "There are no enemies to attack."
        
        # Calculate player damage
        weapon_damage = sum(item.damage for item in self.player.inventory if item.item_type == ItemType.WEAPON)
        base_damage = 5
        total_damage = base_damage + weapon_damage
        
        # Player attacks enemy
        self.current_enemy['health'] -= total_damage
        result = f"You attack the {self.current_enemy['name']} for {total_damage} damage!"
        
        # Check if enemy is defeated
        if self.current_enemy['health'] <= 0:
            exp_gained = self.current_enemy['exp']
            self.player.experience += exp_gained
            result += f"\nYou defeated the {self.current_enemy['name']}! Gained {exp_gained} experience."
            self.current_enemy = None
            
            # Level up check
            if self.player.experience >= self.player.level * 50:
                self.player.level += 1
                self.player.max_health += 20
                self.player.health = self.player.max_health
                result += f"\n🎉 LEVEL UP! You are now level {self.player.level}!"
            
            return result
        
        # Enemy attacks back
        enemy_damage = self.current_enemy['damage']
        defense = sum(item.defense for item in self.player.inventory if item.item_type == ItemType.ARMOR)
        actual_damage = max(1, enemy_damage - defense)
        self.player.health -= actual_damage
        
        result += f"\nThe {self.current_enemy['name']} attacks you for {actual_damage} damage!"
        result += f"\nEnemy health: {self.current_enemy['health']}"
        result += f"\nYour health: {self.player.health}"
        
        # Check if player is defeated
        if self.player.health <= 0:
            self.game_over = True
            result += "\n💀 You have been defeated! Game over."
        
        return result
    
    def use(self, item_name: str) -> str:
        """Use an item from inventory"""
        if not self.game_started:
            return "Game not started. Use 'start_game' to begin."
        
        for item in self.player.inventory:
            if item.name.lower() == item_name.lower():
                if item.item_type == ItemType.POTION:
                    if "health" in item.name.lower():
                        self.player.health = min(self.player.max_health, self.player.health + item.healing)
                        self.player.inventory.remove(item)
                        return f"You used {item.name} and restored {item.healing} health!"
                
                return f"You cannot use {item.name} right now."
        
        return f"Item '{item_name}' not found in your inventory."
    
    def help(self) -> str:
        """Show help information"""
        return """
╔══════════════════════════════════════════════════════════════╗
║                           HELP                               ║
╠══════════════════════════════════════════════════════════════╣
║  Commands:                                                   ║
║  - start_game [name]: Start a new game                      ║
║  - look: Examine your surroundings                          ║
║  - move [direction]: Move north/south/east/west             ║
║  - take [item]: Pick up an item                             ║
║  - inventory: Check your inventory                          ║
║  - status: Check your health and stats                      ║
║  - attack: Fight enemies                                    ║
║  - use [item]: Use an item                                  ║
║  - help: Show this help message                             ║
║                                                              ║
║  Game Tips:                                                 ║
║  - Explore all rooms to find better equipment              ║
║  - Defeat enemies to gain experience and level up          ║
║  - Use health potions when your health is low              ║
║  - Find the treasure room for the best loot!               ║
╚══════════════════════════════════════════════════════════════╝
        """
    
    def get_game_state(self) -> str:
        """Get current game state summary"""
        if not self.game_started:
            return "Game not started. Use 'start_game' to begin."
        
        if self.game_over:
            return "Game Over! You have been defeated."
        
        room = self.rooms[self.player.current_room]
        enemy_info = f"\nEnemy: {self.current_enemy['name']} (Health: {self.current_enemy['health']})" if self.current_enemy else ""
        
        return f"""
Location: {room.name}
Health: {self.player.health}/{self.player.max_health}
Level: {self.player.level}
Gold: {self.player.gold}{enemy_info}
        """

# Global game instance
game = ASCIIGame()
