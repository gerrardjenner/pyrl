import libtcodpy as libtcod

from death_functions import kill_monster, kill_player
from entity import get_blocking_entities_at_location, get_nonblocking_entities_at_location
from fov_functions import initialize_fov, recompute_fov
from game_messages import Message
from game_states import GameStates
from input_handlers import handle_keys, handle_mouse, handle_main_menu
from loader_functions.initialize_new_game import get_constants, get_game_variables
from loader_functions.data_loaders import load_game, save_game
from menus import main_menu, message_box
from render_functions import clear_all, render_all

from random import randint

from components.ai import Follower


def play_game(player, entities, game_map, message_log, game_state, con, panel, mpanel, constants, allies, shops, cleaner):
    fov_recompute = True

    fov_map = initialize_fov(game_map)

    key = libtcod.Key()
    mouse = libtcod.Mouse()

    game_state = GameStates.PLAYERS_TURN
    previous_game_state = game_state

    targeting_item = None
    underfoot = ' '

    #print(shops)

    while not libtcod.console_is_window_closed():
        libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS | libtcod.EVENT_MOUSE, key, mouse)

        #


        clear_all(con, entities, allies)

        action = handle_keys(key, game_state)
        mouse_action = handle_mouse(mouse)

        move = action.get('move')
        wait = action.get('wait')
        pickup = action.get('pickup')

        show_inventory = action.get('show_inventory')
        drop_inventory = action.get('drop_inventory')
        show_merchant = action.get('show_merchant')
        inventory_index = action.get('inventory_index')
        shop_index = action.get('shop_index')
        take_stairs = action.get('take_stairs')
        level_up = action.get('level_up')
        show_character_screen = action.get('show_character_screen')
        exit = action.get('exit')
        fullscreen = action.get('fullscreen')

        left_click = mouse_action.get('left_click')
        right_click = mouse_action.get('right_click')

        player_turn_results = []
        enemy_turn_results = []
        ally_turn_results = []
        floor_turn_results = []

        if move and game_state == GameStates.PLAYERS_TURN:
            dx, dy = move
            destination_x = player.x + dx
            destination_y = player.y + dy

            if not game_map.is_blocked(destination_x, destination_y):
                target = get_blocking_entities_at_location(entities, destination_x, destination_y)

                if target:
                    if not target.name == 'Follower':
                        attack_results = player.fighter.attack(target)
                        player_turn_results.extend(attack_results)
                    else:
                        #swap positions
                        tempx, tempy = player.x, player.y
                        player.x, player.y = destination_x, destination_y
                        target.x, target.y = tempx, tempy
                else:
                    player.move(dx, dy)
                    #if entity gold then add to gold
                    target = get_nonblocking_entities_at_location(entities, destination_x, destination_y)
                    if target:
                        #print(target.name)
                        if target.name == 'Gold':
                            #print(target.name)
                            #player.inventory.add_item(target)
                            pickup_results = player.inventory.use(target)
                            player_turn_results.extend(pickup_results)
                            entities.remove(target)
                        elif target.name == 'Merchant':
                            message_log.add_message(Message('Hello! Press M to shop', libtcod.green))
                        elif target.stairs:
                            message_log.add_message(Message('Press Enter to take stairs', libtcod.green))
                        #
                        underfoot = target.name
                    else:
                        underfoot = ''
                    fov_recompute = True

                game_state = GameStates.ENEMY_TURN

        elif wait:
            game_state = GameStates.ENEMY_TURN

        elif pickup and game_state == GameStates.PLAYERS_TURN:
            for entity in entities:
                if entity.item and entity.x == player.x and entity.y == player.y:
                    pickup_results = player.inventory.add_item(entity)
                    player_turn_results.extend(pickup_results)
                    break
            else:
                message_log.add_message(Message('There is nothing here to pick up.', libtcod.yellow))

        if show_inventory:
            previous_game_state = game_state
            game_state = GameStates.SHOW_INVENTORY

        if drop_inventory:
            previous_game_state = game_state
            game_state = GameStates.DROP_INVENTORY

        if inventory_index is not None and previous_game_state != GameStates.PLAYER_DEAD and inventory_index < len(
                player.inventory.items):
            item = player.inventory.items[inventory_index]

            if game_state == GameStates.SHOW_INVENTORY:
                player_turn_results.extend(player.inventory.use(item, entities=entities, fov_map=fov_map))
            elif game_state == GameStates.DROP_INVENTORY:
                player_turn_results.extend(player.inventory.drop_item(item))

        if shop_index is not None and previous_game_state != GameStates.PLAYER_DEAD and shop_index < len(shops[0].inventory.items):
            item = shops[0].inventory.items[shop_index]

            if game_state == GameStates.SHOP_SCREEN:
                if player.fighter.gold >= item.cost:
                    player.fighter.gold -= item.cost
                    shops[0].inventory.remove_item(item)
                    entities.append(item)
                    player_turn_results.extend(player.inventory.add_item(item))


        if take_stairs and game_state == GameStates.PLAYERS_TURN:
            for entity in entities:
                if entity.stairs and entity.x == player.x and entity.y == player.y:
                    entities = game_map.next_floor(player, message_log, constants, allies, shops)
                    fov_map = initialize_fov(game_map)
                    fov_recompute = True
                    libtcod.console_clear(con)

                    break
            else:
                message_log.add_message(Message('There are no stairs here.', libtcod.yellow))

        if show_merchant and game_state == GameStates.PLAYERS_TURN:
            for entity in entities:
                if entity.name == 'Merchant' and entity.x == player.x and entity.y == player.y:
                    message_log.add_message(Message('What would you like to buy?', libtcod.yellow))
                    previous_game_state = game_state
                    game_state = GameStates.SHOP_SCREEN
                    break


        if level_up:
            if level_up == 'hp':
                player.fighter.base_max_hp += 20
                player.fighter.hp += 20
            elif level_up == 'str':
                player.fighter.base_power += 1
            elif level_up == 'def':
                player.fighter.base_defense += 1

            game_state = previous_game_state

        if show_character_screen:
            previous_game_state = game_state
            game_state = GameStates.CHARACTER_SCREEN

        if game_state == GameStates.TARGETING:
            if left_click:
                target_x, target_y = left_click

                item_use_results = player.inventory.use(targeting_item, entities=entities, fov_map=fov_map,
                                                        target_x=target_x, target_y=target_y)
                player_turn_results.extend(item_use_results)
            elif right_click:
                player_turn_results.append({'targeting_cancelled': True})
        elif left_click:
            target_x, target_y = left_click
            #print('{0}, {1}'.format(target_x, target_y))

            #player.inventory.add_item(item_component)
            #player_turn_results.extend(player.inventory.use(item, entities=entities, fov_map=fov_map))
            item_use_results = player.inventory.use(cleaner, entities=entities, fov_map=fov_map, game_map=game_map,
                                                    target_x=target_x, target_y=target_y)
            player_turn_results.extend(item_use_results)


        if exit:
            if game_state in (GameStates.SHOW_INVENTORY, GameStates.DROP_INVENTORY, GameStates.CHARACTER_SCREEN, GameStates.SHOP_SCREEN):
                game_state = previous_game_state
            elif game_state == GameStates.TARGETING:
                player_turn_results.append({'targeting_cancelled': True})
            else:
                save_game(player, entities, game_map, message_log, game_state, allies, shops, cleaner)

                return True

        if fullscreen:
            libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())

        for player_turn_result in player_turn_results:
            #print(player_turn_result.keys())
            message = player_turn_result.get('message')
            dead_entity = player_turn_result.get('dead')
            item_added = player_turn_result.get('item_added')
            gold_added = player_turn_result.get('gold_added')
            item_consumed = player_turn_result.get('consumed')
            cleaner_used = player_turn_result.get('clean')
            item_dropped = player_turn_result.get('item_dropped')
            equip = player_turn_result.get('equip')
            targeting = player_turn_result.get('targeting')
            targeting_cancelled = player_turn_result.get('targeting_cancelled')
            xp = player_turn_result.get('xp')

            if message:
                message_log.add_message(message)

            if dead_entity:
                if dead_entity == player:
                    message, game_state = kill_player(dead_entity)
                    if game_state == GameStates.PLAYER_DEAD:
                        break
                else:
                    message = kill_monster(dead_entity)

                message_log.add_message(message)

            if item_added:
                entities.remove(item_added)

                game_state = GameStates.ENEMY_TURN

            if gold_added:
                entities.remove(gold_added)
                game_state = GameStates.ENEMY_TURN

            if item_consumed:
                game_state = GameStates.ENEMY_TURN

            if item_dropped:
                entities.append(item_dropped)

                game_state = GameStates.ENEMY_TURN

            if cleaner_used:
                #print('cleaner used')
                fov_recompute = True
                game_state = GameStates.ENEMY_TURN

            if equip:
                equip_results = player.equipment.toggle_equip(equip)

                for equip_result in equip_results:
                    equipped = equip_result.get('equipped')
                    dequipped = equip_result.get('dequipped')

                    if equipped:
                        message_log.add_message(Message('You equipped the {0}'.format(equipped.name)))

                    if dequipped:
                        message_log.add_message(Message('You dequipped the {0}'.format(dequipped.name)))

                game_state = GameStates.ENEMY_TURN

            if targeting:
                previous_game_state = GameStates.PLAYERS_TURN
                game_state = GameStates.TARGETING

                targeting_item = targeting

                message_log.add_message(targeting_item.item.targeting_message)

            if targeting_cancelled:
                game_state = previous_game_state

                message_log.add_message(Message('Targeting cancelled'))

            if xp:
                leveled_up = player.level.add_xp(xp)
                message_log.add_message(Message('You gain {0} experience points.'.format(xp)))

                if leveled_up:

                    previous_game_state = game_state
                    game_state = GameStates.LEVEL_UP







        if game_state == GameStates.ENEMY_TURN:

            #if game_state == GameStates.ALLIES_TURN:
            # Do Allies turns
            # ally movement - go through each one and get distance to target then a* follow in order or distance
            asort = sorted(allies, key=lambda x: x.distance_to(player))
            # print(asort[0].distance_to(player))
            # ally_turn_results = asort[0].ai.take_turn(player, fov_map, game_map, entities, allies)
            # print(len(ally_turn_results))
            for a in range(0, len(asort)):
                if a == 0:
                    ally_turn_results = asort[0].ai.take_turn(player, fov_map, game_map, entities, allies)
                else:
                    ally_turn_results = asort[a].ai.take_turn(asort[a - 1], fov_map, game_map, entities, allies)

                for ally_turn_result in ally_turn_results:
                    #print("Follower {0}".format(a))
                    message = ally_turn_result.get('message')
                    dead_entity = ally_turn_result.get('dead')
                    xp = ally_turn_result.get('xp')
                    # print(message)
                    # print(dead_entity)

                    if message:
                        message_log.add_message(message)

                    if dead_entity:
                        if dead_entity == player:
                            message, game_state = kill_player(dead_entity)
                        else:
                            message = kill_monster(dead_entity)

                        message_log.add_message(message)
                    if xp:
                        leveled_up = player.level.add_xp(xp)
                        message_log.add_message(Message('You gain {0} experience points.'.format(xp)))

                        if leveled_up:
                            print('Level Up')
                            previous_game_state = game_state
                            game_state = GameStates.LEVEL_UP
                            break

            # have a percent chance to increase hunger
            #if randint(0, 10) < 3:
            #    #player.fighter.hunger += 1
            #    if player.fighter.contact > 1:
            #        player.fighter.contact += 1

            player.fighter.contact += game_map.tiles[player.x][player.y].contaminants


            #if player.fighter.hunger > 99:
            #    player.fighter.hunger = 100
            #    message_log.add_message(Message('Hunger Pain!', libtcod.lighter_red))
            #    # take damage
            #    floor_turn_results = player.fighter.take_damage(1)
            #    # floor_turn_results.append(move_results)

            if player.fighter.contact > 99:
                player.fighter.contact = 100
                message_log.add_message(Message('Infected!', libtcod.lighter_yellow))
                # take damage
                floor_turn_results = player.fighter.take_damage(10)
                # floor_turn_results.append(move_results)

            for floor_turn_result in floor_turn_results:
                message = floor_turn_result.get('message')
                dead_entity = floor_turn_result.get('dead')

                if message:
                    message_log.add_message(message)

                if dead_entity:
                    if dead_entity == player:
                        message, game_state = kill_player(dead_entity)
                    else:
                        message = kill_monster(dead_entity)

                    message_log.add_message(message)

                    if game_state == GameStates.PLAYER_DEAD:
                        break

            ###

            #do enemies - also account for followers in pathing etc



            for entity in entities:
                if entity.ai:
                    if isinstance(entity.ai, Follower):
                        pass
                    else:
                        enemy_turn_results = entity.ai.take_turn(player, fov_map, game_map, entities, allies)

                    for enemy_turn_result in enemy_turn_results:
                        message = enemy_turn_result.get('message')
                        dead_entity = enemy_turn_result.get('dead')

                        if message:
                            message_log.add_message(message)

                        if dead_entity:
                            if dead_entity == player:
                                message, game_state = kill_player(dead_entity)
                            else:
                                message = kill_monster(dead_entity)

                            message_log.add_message(message)

                            if game_state == GameStates.PLAYER_DEAD:
                                break

                    if game_state == GameStates.PLAYER_DEAD:
                        break
            else:
                game_state = GameStates.PLAYERS_TURN

        if fov_recompute:
            recompute_fov(fov_map, player.x, player.y, constants['fov_radius'], constants['fov_light_walls'],
                          constants['fov_algorithm'])

        #
        render_all(con, panel, mpanel, entities, allies, player, game_map, fov_map, fov_recompute, message_log,
                   constants['screen_width'], constants['screen_height'], constants['bar_width'],
                   constants['panel_height'], constants['panel_y'], mouse, constants['colors'], game_state, shops, constants['tilemap'], underfoot)

        fov_recompute = False

        libtcod.console_flush()
        #


def main():
    constants = get_constants()

    #libtcod.console_set_custom_font('arial10x10.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
    #libtcod.console_set_custom_font('terminal16x16_gs_ro.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_ASCII_INROW)
    #libtcod.console_set_custom_font('dejavu_wide16x16_gs_tc.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
    #libtcod.console_set_custom_font('terminal16x16_gs_ro.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_ASCII_INROW)
    #libtcod.console_set_custom_font('TiledFont.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD, 32, 10)

    libtcod.console_set_custom_font('terminal16x16_gs_ro_ext.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_ASCII_INROW, 16, 17)

    load_customfont()

    libtcod.console_init_root(constants['screen_width'], constants['screen_height'], constants['window_title'], False)

    con = libtcod.console_new(constants['screen_width'], constants['screen_height'])
    panel = libtcod.console_new(constants['screen_width'], constants['panel_height'])
    mpanel = libtcod.console_new(32, 1)

    player = None
    shops = []
    allies = []
    entities = []
    game_map = None
    message_log = None
    game_state = None

    show_main_menu = True
    show_load_error_message = False

    main_menu_background_image = libtcod.image_load('menu_background.png')

    key = libtcod.Key()
    mouse = libtcod.Mouse()

    while not libtcod.console_is_window_closed():
        libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS | libtcod.EVENT_MOUSE, key, mouse)

        if show_main_menu:
            main_menu(con, main_menu_background_image, constants['screen_width'],
                      constants['screen_height'])

            if show_load_error_message:
                message_box(con, 'No save game to load', 50, constants['screen_width'], constants['screen_height'])

            libtcod.console_flush()

            action = handle_main_menu(key)

            new_game = action.get('new_game')
            load_saved_game = action.get('load_game')
            exit_game = action.get('exit')

            if show_load_error_message and (new_game or load_saved_game or exit_game):
                show_load_error_message = False
            elif new_game:
                player, entities, game_map, message_log, game_state, allies, shops, cleaner = get_game_variables(constants)
                game_state = GameStates.PLAYERS_TURN

                show_main_menu = False
            elif load_saved_game:
                try:
                    player, entities, game_map, message_log, game_state, allies, shops, cleaner = load_game()
                    show_main_menu = False
                except FileNotFoundError:
                    show_load_error_message = True
            elif exit_game:
                break

        else:
            libtcod.console_clear(con)
            play_game(player, entities, game_map, message_log, game_state, con, panel, mpanel, constants, allies, shops, cleaner)

            show_main_menu = True


def load_customfont():
    # The index of the first custom tile in the file
    a = 256

    # The "y" is the row index, here we load the sixth row in the font file. Increase the "6" to load any new rows from the file
    for y in range(16, 17):
        libtcod.console_map_ascii_codes_to_font(a, 16, 0, y)
        a += 16



if __name__ == '__main__':
    main()
