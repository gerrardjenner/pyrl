import libtcodpy as libtcod
from random import randint

from components.ai import BasicMonster, Follower
from components.equipment import EquipmentSlots
from components.equippable import Equippable
from components.fighter import Fighter
from components.item import Item
from components.stairs import Stairs
from components.shop import Shop


from entity import Entity

from game_messages import Message

from item_functions import cast_confuse, cast_fireball, cast_lightning, heal, acquire_gold, eat, clean, locate_ally

from map_objects.rectangle import Rect
from map_objects.tile import Tile

from random_utils import from_dungeon_level, random_choice_from_dict

from render_functions import RenderOrder


class GameMap:
    def __init__(self, width, height, dungeon_level=1):
        self.width = width
        self.height = height
        self.tiles = self.initialize_tiles()

        self.dungeon_level = dungeon_level

    def initialize_tiles(self):
        tiles = [[Tile(True) for y in range(self.height)] for x in range(self.width)]

        return tiles

    def make_boss_map(self, max_rooms, room_min_size, room_max_size, map_width, map_height, player, entities, allies, shops, tilemap):
        rooms = []
        num_rooms = 0
        #2 rooms - small room to enter in connected to larger room

        for i in range (0,2):

            # random width and height
            w = randint(room_min_size+(i*10), room_max_size+(1*10))
            h = randint(room_min_size+(i*10), room_max_size+(1*10))
            # random position without going out of the boundaries of the map
            x = randint(0, map_width - w - 1)
            y = randint(0, map_height - h - 1)

            # "Rect" class makes rectangles easier to work with
            new_room = Rect(x, y, w, h)

            # "paint" it to the map's tiles
            self.create_room(new_room)

            # center coordinates of new room, will be useful later
            (new_x, new_y) = new_room.center()

            center_of_last_room_x = new_x
            center_of_last_room_y = new_y

            if i == 0:
                # this is the first room, where the player starts at
                player.x = new_x
                player.y = new_y

                self.place_allies(player, allies)
            else:
                # all rooms after the first:
                # connect it to the previous room with a tunnel

                # center coordinates of previous room
                (prev_x, prev_y) = rooms[num_rooms - 1].center()

                # flip a coin (random number that is either 0 or 1)
                if randint(0, 1) == 1:
                    # first move horizontally, then vertically
                    self.create_h_tunnel(prev_x, new_x, prev_y)
                    self.create_v_tunnel(prev_y, new_y, new_x)
                else:
                    # first move vertically, then horizontally
                    self.create_v_tunnel(prev_y, new_y, prev_x)
                    self.create_h_tunnel(prev_x, new_x, new_y)

                # boss room

                fighter_component = Fighter(hp=60, defense=2, power=8, xp=300)
                ai_component = BasicMonster()

                monster = Entity(new_x, new_y, tilemap['boss_tile'], libtcod.white, 'Haggard Infested', blocks=True, fighter=fighter_component,
                                 render_order=RenderOrder.ACTOR, ai=ai_component)

                entities.append(monster)

                stairs_component = Stairs(self.dungeon_level + 1)
                down_stairs = Entity(center_of_last_room_x, center_of_last_room_y, '>', libtcod.white, 'Stairs',
                                     render_order=RenderOrder.STAIRS, stairs=stairs_component)
                entities.append(down_stairs)

            rooms.append(new_room)
            num_rooms += 1







    def make_map(self, max_rooms, room_min_size, room_max_size, map_width, map_height, player, entities, allies, shops, tilemap):
        rooms = []
        num_rooms = 0

        center_of_last_room_x = None
        center_of_last_room_y = None
        #center_of_first_room_x = None
        #center_of_first_room_y = None


        for r in range(max_rooms):
            # random width and height
            w = randint(room_min_size, room_max_size)
            h = randint(room_min_size, room_max_size)
            # random position without going out of the boundaries of the map
            x = randint(0, map_width - w - 1)
            y = randint(0, map_height - h - 1)

            # "Rect" class makes rectangles easier to work with
            new_room = Rect(x, y, w, h)

            # run through the other rooms and see if they intersect with this one
            for other_room in rooms:
                if new_room.intersect(other_room):
                    break
            else:
                # this means there are no intersections, so this room is valid

                # "paint" it to the map's tiles
                self.create_room(new_room)

                # center coordinates of new room, will be useful later
                (new_x, new_y) = new_room.center()

                center_of_last_room_x = new_x
                center_of_last_room_y = new_y

                if num_rooms == 0:
                    # this is the first room, where the player starts at
                    player.x = new_x
                    player.y = new_y

                    self.place_allies(player, allies)

                    #add Merchant in first room
                    shop_component = Shop(5)

                    item_component = Item(use_function=heal, amount=40)
                    item = Entity(-1, -1, tilemap.get('healingpotion_tile'), libtcod.violet, 'Healing Potion', render_order=RenderOrder.ITEM, item=item_component, cost=20)
                    shop_component.add_item(item)

                    item_component = Item(use_function=eat, amount=40)
                    item = Entity(-1, -1, 'a', libtcod.red, 'Apple', render_order=RenderOrder.ITEM, item=item_component, cost=30)
                    shop_component.add_item(item)

                    item_component = Item(use_function=clean, amount=100)
                    item = Entity(-1, -1, 'b', libtcod.red, 'Hand Sanitiser', render_order=RenderOrder.ITEM, item=item_component, cost=40)
                    shop_component.add_item(item)

                    item_component = Item(use_function=locate_ally, alist=allies)
                    item = Entity(-1, -1, 'j', libtcod.red, 'Locate Ally', render_order=RenderOrder.ITEM, item=item_component, cost=40)
                    shop_component.add_item(item)

                    shop = Entity(new_room.x1+1, new_room.y1+1, tilemap['shop_tile'], libtcod.white, 'Medi-vend', blocks=False,
                                         render_order=RenderOrder.STAIRS, inventory = shop_component)
                    #print(shop)
                    entities.append(shop)
                    shops.append(shop)
                    #print(shops[0].inventory.items)

                else:
                    # all rooms after the first:
                    # connect it to the previous room with a tunnel

                    # center coordinates of previous room
                    (prev_x, prev_y) = rooms[num_rooms - 1].center()

                    # flip a coin (random number that is either 0 or 1)
                    if randint(0, 1) == 1:
                        # first move horizontally, then vertically
                        self.create_h_tunnel(prev_x, new_x, prev_y)
                        self.create_v_tunnel(prev_y, new_y, new_x)
                    else:
                        # first move vertically, then horizontally
                        self.create_v_tunnel(prev_y, new_y, prev_x)
                        self.create_h_tunnel(prev_x, new_x, new_y)

                self.place_entities(new_room, entities, tilemap)

                # finally, append the new room to the list
                rooms.append(new_room)
                num_rooms += 1

        stairs_component = Stairs(self.dungeon_level + 1)
        down_stairs = Entity(center_of_last_room_x, center_of_last_room_y, tilemap['stairsdown_tile'], libtcod.white, 'Stairs',
                             render_order=RenderOrder.STAIRS, stairs=stairs_component)
        entities.append(down_stairs)

        # add Follower
        fighter_component = Fighter(hp=20, defense=0, power=4, xp=35)
        ai_component = Follower()
        # blocks true - pushable true?
        follower = Entity(center_of_last_room_x + 1, center_of_last_room_y + 1, tilemap.get('ally_tile'), libtcod.white,
                          'Follower', blocks=True,
                          render_order=RenderOrder.ACTOR, fighter=fighter_component, ai=ai_component)
        #print(follower.ai.found)

        #entities.append(follower)
        allies.append(follower)



    def create_room(self, room):
        # go through the tiles in the rectangle and make them passable
        for x in range(room.x1 + 1, room.x2):
            for y in range(room.y1 + 1, room.y2):
                self.tiles[x][y].blocked = False
                self.tiles[x][y].block_sight = False

    def create_h_tunnel(self, x1, x2, y):
        for x in range(min(x1, x2), max(x1, x2) + 1):
            self.tiles[x][y].blocked = False
            self.tiles[x][y].block_sight = False

    def create_v_tunnel(self, y1, y2, x):
        for y in range(min(y1, y2), max(y1, y2) + 1):
            self.tiles[x][y].blocked = False
            self.tiles[x][y].block_sight = False

    def place_allies(self, target, allies):
        j = 1
        new_x = target.x
        new_y = target.y

        for i in allies:
            # need to place around player
            if j == 1:
                i.x = new_x + 1
                i.y = new_y + 1
            elif j == 2:
                i.x = new_x
                i.y = new_y + 1
            elif j == 3:
                i.x = new_x - 1
                i.y = new_y + 1
            elif j == 4:
                i.x = new_x - 1
                i.y = new_y
            elif j == 5:
                i.x = new_x - 1
                i.y = new_y - 1
            elif j == 6:
                i.x = new_x
                i.y = new_y - 1
            elif j == 7:
                i.x = new_x + 1
                i.y = new_y - 1
            elif j == 8:
                i.x = new_x + 1
                i.y = new_y
            j += 1

    def place_entities(self, room, entities, tilemap):
        max_monsters_per_room = from_dungeon_level([[2, 1], [3, 4], [5, 6]], self.dungeon_level)
        max_items_per_room = from_dungeon_level([[2, 1], [3, 4]], self.dungeon_level)

        # Get a random number of monsters
        number_of_monsters = randint(0, max_monsters_per_room)

        # Get a random number of items
        number_of_items = randint(0, max_items_per_room)

        monster_chances = {
            'orc': 80,
            'troll': from_dungeon_level([[15, 3], [30, 5], [60, 7]], self.dungeon_level)
        }

        item_chances = {
            'healing_potion': 35,
            'gold': 40,
            #'apple': 40,
            'sanitiser': 50,
            'sword': from_dungeon_level([[5, 4]], self.dungeon_level),
            'shield': from_dungeon_level([[15, 8]], self.dungeon_level),
            'lightning_scroll': from_dungeon_level([[25, 4]], self.dungeon_level),
            'fireball_scroll': from_dungeon_level([[25, 6]], self.dungeon_level),
            'confusion_scroll': from_dungeon_level([[10, 2]], self.dungeon_level)
        }

        for i in range(number_of_monsters):
            # Choose a random location in the room
            x = randint(room.x1 + 1, room.x2 - 1)
            y = randint(room.y1 + 1, room.y2 - 1)

            # Check if an entity is already in that location
            if not any([entity for entity in entities if entity.x == x and entity.y == y]):
                monster_choice = random_choice_from_dict(monster_chances)

                if monster_choice == 'orc':
                    fighter_component = Fighter(hp=20, defense=0, power=4, xp=35)
                    ai_component = BasicMonster()

                    monster = Entity(x, y, tilemap.get('orc_tile'), libtcod.white, 'Infected', blocks=True,
                                     render_order=RenderOrder.ACTOR, fighter=fighter_component, ai=ai_component)
                else:
                    fighter_component = Fighter(hp=30, defense=2, power=8, xp=100)
                    ai_component = BasicMonster()

                    monster = Entity(x, y, tilemap.get('troll_tile'), libtcod.darker_green, 'Infested', blocks=True, fighter=fighter_component,
                                     render_order=RenderOrder.ACTOR, ai=ai_component)

                entities.append(monster)

        for i in range(number_of_items):
            x = randint(room.x1 + 1, room.x2 - 1)
            y = randint(room.y1 + 1, room.y2 - 1)

            if not any([entity for entity in entities if entity.x == x and entity.y == y]):
                item_choice = random_choice_from_dict(item_chances)
                if item_choice == 'gold':
                    item_component = Item(use_function=acquire_gold, amount=randint(10, 40))
                    item = Entity(x, y, tilemap.get('gold_tile'), libtcod.white, 'Gold', render_order=RenderOrder.ITEM, item=item_component)
                elif item_choice == 'healing_potion':
                    item_component = Item(use_function=heal, amount=40)
                    item = Entity(x, y, tilemap.get('healingpotion_tile'), libtcod.white, 'Healing Potion', render_order=RenderOrder.ITEM,
                                  item=item_component)
                #elif item_choice == 'apple':
                #    item_component = Item(use_function=eat, amount=40)
                #    item = Entity(x, y, tilemap.get('healingpotion_tile'), libtcod.red, 'Apple', render_order=RenderOrder.ITEM,
                #                  item=item_component)
                elif item_choice == 'sanitiser':
                    item_component = Item(use_function=clean, amount=100)
                    item = Entity(x, y, tilemap.get('cleaner_tile'), libtcod.white, 'Hand Sanitiser', render_order=RenderOrder.ITEM,
                                  item=item_component)
                elif item_choice == 'sword':
                    equippable_component = Equippable(EquipmentSlots.MAIN_HAND, power_bonus=3)
                    item = Entity(x, y, '/', libtcod.sky, 'Sword', equippable=equippable_component)
                elif item_choice == 'shield':
                    equippable_component = Equippable(EquipmentSlots.OFF_HAND, defense_bonus=1)
                    item = Entity(x, y, '[', libtcod.darker_orange, 'Shield', equippable=equippable_component)
                elif item_choice == 'fireball_scroll':
                    item_component = Item(use_function=cast_fireball, targeting=True, targeting_message=Message(
                        'Left-click a target tile for the fireball, or right-click to cancel.', libtcod.light_cyan),
                                          damage=25, radius=3)
                    item = Entity(x, y, '#', libtcod.red, 'Fireball Scroll', render_order=RenderOrder.ITEM,
                                  item=item_component)
                elif item_choice == 'confusion_scroll':
                    item_component = Item(use_function=cast_confuse, targeting=True, targeting_message=Message(
                        'Left-click an enemy to confuse it, or right-click to cancel.', libtcod.light_cyan))
                    item = Entity(x, y, '#', libtcod.light_pink, 'Confusion Scroll', render_order=RenderOrder.ITEM,
                                  item=item_component)
                else:
                    item_component = Item(use_function=cast_lightning, damage=40, maximum_range=5)
                    item = Entity(x, y, '#', libtcod.yellow, 'Lightning Scroll', render_order=RenderOrder.ITEM,
                                  item=item_component)

                entities.append(item)

    def is_blocked(self, x, y):
        if self.tiles[x][y].blocked:
            return True

        return False

    def next_floor(self, player, message_log, constants, allies, shops):
        self.dungeon_level += 1

        entities = [player]
        #entities += allies
        shops.clear()

        self.tiles = self.initialize_tiles()
        if self.dungeon_level % 2 == 0:
            self.make_boss_map(constants['max_rooms'], constants['room_min_size'], constants['room_max_size'],
                               constants['map_width'], constants['map_height'], player, entities, allies, shops, constants['tilemap'])
        else:
            self.make_map(constants['max_rooms'], constants['room_min_size'], constants['room_max_size'], constants['map_width'], constants['map_height'], player, entities, allies, shops, constants['tilemap'])



        player.fighter.heal(player.fighter.max_hp // 2)
        player.fighter.eat(100)
        player.fighter.clean(100)

        message_log.add_message(Message('You take a moment to rest, and recover your strength.', libtcod.light_violet))

        return entities
