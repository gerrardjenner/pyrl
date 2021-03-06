import libtcodpy as libtcod

from components.equipment import Equipment
from components.equippable import Equippable
from components.fighter import Fighter
from components.ai import Follower
from components.inventory import Inventory
from components.level import Level

from entity import Entity

from equipment_slots import EquipmentSlots
from components.item import Item
from item_functions import locate_ally, throw_cleaner

from game_messages import MessageLog

from game_states import GameStates

from map_objects.game_map import GameMap

from render_functions import RenderOrder


def get_constants():
    window_title = 'pyrl'

    screen_width = 80
    screen_height = 50

    bar_width = 20
    panel_height = 7
    panel_y = screen_height - panel_height

    message_x = bar_width + 2
    message_width = screen_width - bar_width - 2
    message_height = panel_height - 1

    map_width = 80
    map_height = 43

    room_max_size = 10
    room_min_size = 6
    max_rooms = 30

    fov_algorithm = 0
    fov_light_walls = True
    fov_radius = 10

    max_monsters_per_room = 3
    max_items_per_room = 2

    tilemap = {
        'wall_tile': 256,
        'floor_tile': 257,
        'player_tile': 258,
        'orc_tile': 259,
        'troll_tile': 260,
        'boss_tile': 261,
        'healingpotion_tile': 262,
        'cleaner_tile': 263,
        'shield_tile': 264,
        'stairsdown_tile': 265,
        'dagger_tile': 266,
        'ally_tile': 267,
        'gold_tile': 268,
        'shop_tile': 269
    }

    colors = {
        'dark_wall': libtcod.Color(0, 0, 100),
        'dark_ground': libtcod.Color(50, 50, 150),
        'light_wall': libtcod.Color(130, 110, 50),
        'light_ground': libtcod.Color(200, 180, 50)
    }

    constants = {
        'window_title': window_title,
        'screen_width': screen_width,
        'screen_height': screen_height,
        'bar_width': bar_width,
        'panel_height': panel_height,
        'panel_y': panel_y,
        'message_x': message_x,
        'message_width': message_width,
        'message_height': message_height,
        'map_width': map_width,
        'map_height': map_height,
        'room_max_size': room_max_size,
        'room_min_size': room_min_size,
        'max_rooms': max_rooms,
        'fov_algorithm': fov_algorithm,
        'fov_light_walls': fov_light_walls,
        'fov_radius': fov_radius,
        'max_monsters_per_room': max_monsters_per_room,
        'max_items_per_room': max_items_per_room,
        'colors': colors,
        'tilemap': tilemap
    }

    return constants


def get_game_variables(constants):
    fighter_component = Fighter(hp=100, defense=1, power=2, xp=0, gold=100)
    inventory_component = Inventory(26)
    level_component = Level()
    equipment_component = Equipment()
    #player = Entity(0, 0, 2, libtcod.white, 'Player', blocks=True, render_order=RenderOrder.ACTOR,
    #                fighter=fighter_component, inventory=inventory_component, level=level_component,
    #                equipment=equipment_component)
    player = Entity(0, 0, 258, libtcod.white, 'Player', blocks=True, render_order=RenderOrder.ACTOR,
                    fighter=fighter_component, inventory=inventory_component, level=level_component,
                    equipment=equipment_component)

    entities = [player]

    # add Follower
    fighter_component = Fighter(hp=20, defense=0, power=4, xp=35)
    ai_component = Follower()
    # blocks true - pushable true?
    follower = Entity(1, 1, constants['tilemap'].get('ally_tile'), libtcod.white, 'Follower', blocks=True,
                      render_order=RenderOrder.ACTOR, fighter=fighter_component, ai=ai_component)
    allies = [follower]
    #allies = []
    shops = []

    #equippable_component = Equippable(EquipmentSlots.MAIN_HAND, power_bonus=2)
    #dagger = Entity(0, 0, '-', libtcod.sky, 'Dagger', equippable=equippable_component)
    #player.inventory.add_item(dagger)
    #player.equipment.toggle_equip(dagger)

    #equippable_component = Equippable(EquipmentSlots.MAIN_HAND, power_bonus=2)
    #cleaner = Entity(0, 0, 'j', libtcod.red, 'Throw Cleaner', equippable=equippable_component, render_order=RenderOrder.ITEM, item=item_component)
    #player.inventory.add_item(dagger)
    #player.equipment.toggle_equip(dagger)


    item_component = Item(use_function=throw_cleaner, damage=25, radius=3)
    cleaner = Entity(0, 0, 'j', libtcod.red, 'Throw Cleaner', render_order=RenderOrder.HIDDEN, item=item_component)
    player.inventory.add_item(cleaner)

    item_component = Item(use_function=locate_ally, alist=allies)
    item = Entity(0, 0, 'j', libtcod.red, 'Locate Ally', render_order=RenderOrder.ITEM, item=item_component, cost=40)
    player.inventory.add_item(item)

    game_map = GameMap(constants['map_width'], constants['map_height'])
    game_map.make_map(constants['max_rooms'], constants['room_min_size'], constants['room_max_size'],
                      constants['map_width'], constants['map_height'], player, entities, allies, shops, constants['tilemap'])

    message_log = MessageLog(constants['message_x'], constants['message_width'], constants['message_height'])

    game_state = GameStates.PLAYERS_TURN

    return player, entities, game_map, message_log, game_state, allies, shops, cleaner
