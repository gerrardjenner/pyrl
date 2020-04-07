import libtcodpy as libtcod

from enum import Enum

from components.ai import Follower
from game_states import GameStates

from menus import character_screen, inventory_menu, level_up_menu, shop_menu


class RenderOrder(Enum):
    STAIRS = 1
    CORPSE = 2
    ITEM = 3
    ACTOR = 4
    HIDDEN = 5


def get_names_under_mouse(mouse, entities, fov_map):
    (x, y) = (mouse.cx, mouse.cy)

    names = [entity.name for entity in entities
             if entity.x == x and entity.y == y and libtcod.map_is_in_fov(fov_map, entity.x, entity.y)]
    names = ', '.join(names)

    return names.capitalize()


def render_bar(panel, x, y, total_width, name, value, maximum, bar_color, back_color):
    bar_width = int(float(value) / maximum * total_width)

    libtcod.console_set_default_background(panel, back_color)
    libtcod.console_rect(panel, x, y, total_width, 1, False, libtcod.BKGND_SCREEN)

    libtcod.console_set_default_background(panel, bar_color)
    if bar_width > 0:
        libtcod.console_rect(panel, x, y, bar_width, 1, False, libtcod.BKGND_SCREEN)

    libtcod.console_set_default_foreground(panel, libtcod.white)
    libtcod.console_print_ex(panel, int(x + total_width / 2), y, libtcod.BKGND_NONE, libtcod.CENTER,
                             '{0}: {1}/{2}'.format(name, value, maximum))


def render_all(con, panel, mpanel, entities, allies, player, game_map, fov_map, fov_recompute, message_log, screen_width, screen_height,
               bar_width, panel_height, panel_y, mouse, colors, game_state, shops, tilemap, underfoot):
    if fov_recompute:
        libtcod.console_set_default_background(con, libtcod.black)
    # Draw all the tiles in the game map
        for y in range(game_map.height):
            for x in range(game_map.width):
                visible = libtcod.map_is_in_fov(fov_map, x, y)
                wall = game_map.tiles[x][y].block_sight

                if visible:
                    if wall:
                        libtcod.console_put_char_ex(con, x, y, tilemap.get('wall_tile'), libtcod.white, libtcod.black)
                    else:
                        c = int(game_map.tiles[x][y].contaminants)
                        if c > 255:
                            c = 255
                        ccol = (255, 255-c, 255-c)
                        libtcod.console_put_char_ex(con, x, y, tilemap.get('floor_tile'), ccol, libtcod.black)
                        #since it's visible, explore it
                    game_map.tiles[x][y].explored = True

                elif game_map.tiles[x][y].explored:
                    if wall:
                        libtcod.console_put_char_ex(con, x, y, tilemap.get('wall_tile'), libtcod.grey, libtcod.black)
                    else:
                        libtcod.console_put_char_ex(con, x, y, tilemap.get('floor_tile'), libtcod.grey, libtcod.black)


    '''
                if visible:
                    if wall:
                        #libtcod.console_set_char_background(con, x, y, colors.get('light_wall'), libtcod.BKGND_SET)
                        libtcod.console_set_default_foreground(con, colors.get('light_wall'))
                        libtcod.console_put_char(con, x, y, 178, libtcod.BKGND_SET)
                    else:
                        libtcod.console_set_char_background(con, x, y, colors.get('light_ground'), libtcod.BKGND_SET)
                        #libtcod.console_set_default_foreground(con, colors.get('light_ground'))
                        #libtcod.console_put_char(con, x, y, 250, libtcod.BKGND_OVERLAY)

                    game_map.tiles[x][y].explored = True
                elif game_map.tiles[x][y].explored:
                    if wall:
                        #libtcod.console_set_char_background(con, x, y, colors.get('dark_wall'), libtcod.BKGND_SET)
                        libtcod.console_set_default_foreground(con, colors.get('dark_wall'))
                        libtcod.console_put_char(con, x, y, 178, libtcod.BKGND_SET)

                    else:
                        libtcod.console_set_char_background(con, x, y, colors.get('dark_ground'), libtcod.BKGND_SET)
                        #libtcod.console_put_char(con, x, y, ' ', libtcod.BKGND_OVERLAY)
    '''
    entities_in_render_order = sorted(entities, key=lambda x: x.render_order.value)

    # Draw all entities in the list
    for entity in entities_in_render_order:
        if not isinstance(entity.ai, Follower):
            if entity.char == '%' and not libtcod.map_is_in_fov(fov_map, entity.x, entity.y):
                entities.remove(entity)
                pass
            else:
                draw_entity(con, entity, fov_map, game_map, tilemap)
    #draw followers on top?

    for entity in allies:
        draw_entity(con, entity, fov_map, game_map, tilemap)

    #draw player on top
    draw_entity(con, player, fov_map, game_map, tilemap)


    # show info about entity under
    f = entities + allies
    mouseinfo = get_names_under_mouse(mouse, f, fov_map)

    #image = libtcod.image_from_console(con)

    #libtcod.image_put_pixel(image, player.x, player.y + 16, libtcod.light_red)

    #libtcod.image_blit_rect(image, 0, 0, 0, screen_width, screen_height, libtcod.BKGND_SET)
    #libtcod.console_flush()

    libtcod.console_blit(con, 0, 0, screen_width, screen_height, 0, 0, 0)

    if mouseinfo:
        #libtcod.console_clear(mpanel)
        x = len(mouseinfo)
        mpanel = libtcod.console_new(x, 1)
        #libtcod.console_set_key_color(mpanel, libtcod.black)
        libtcod.console_set_default_background(mpanel, libtcod.black)
        libtcod.console_print_ex(mpanel, 0, 0, libtcod.BKGND_ALPHA(0.5), libtcod.LEFT, mouseinfo)
        #print('{0}, {1}'.format(mouse.cx-len(mouseinfo), mouse.cy))
        #libtcod.console_set_key_color(mpanel, libtcod.black)
        if mouse.cx-x < 0:
            libtcod.console_blit(mpanel, 0, 0, 32, 1, 0, mouse.cx+1, mouse.cy, 1, 1)
        else:
            libtcod.console_blit(mpanel, 0, 0, 32, 1, 0, mouse.cx-x, mouse.cy, 1, 1)
    else:
        if libtcod.map_is_in_fov(fov_map, mouse.cx, mouse.cy):
            mpanel = libtcod.console_new(3, 3)
            libtcod.console_set_default_background(mpanel, libtcod.light_cyan)
            libtcod.console_rect(mpanel, 0, 0, 3, 3, False, libtcod.BKGND_SCREEN)
            libtcod.console_blit(mpanel, 0, 0, 3, 3, 0, mouse.cx - 1, mouse.cy -1, 1, .5)
        else:
            libtcod.console_clear(mpanel)

    #libtcod.console_blit(con, 0, 0, screen_width, screen_height, 0, 0, 0)
    #libtcod.console_blit(con, 0, 0, int(screen_width / 2), int(screen_height / 2), 0, 0-player.x+int(screen_width/2), 0-player.y+int(screen_height/2))
    #libtcod.console_blit(con, 0 - player.x + int(screen_width / 2), 0 - player.y + int(screen_height / 2), 0, 0, 0, int(screen_width / 2), int(screen_height / 2))

    #image = libtcod.image_from_console(con)

    #libtcod.image_put_pixel()

    #libtcod.image_blit_2x(image, player.x-int(screen_width/2), player.y-int(screen_height/2), 0)#, libtcod.BKGND_NONE, 1, 1, 0)

    #libtcod.blit(con, 0, 0, libtcod.BKGND_NONE, 2, 2,0)


    #else:
    #    #show mouse
    #    #libtcod.console_set_char_background(mpanel, mouse.cx, mouse.cy, libtcod.desaturated_red, libtcod.BKGND_SET)





    libtcod.console_set_default_background(panel, libtcod.black)
    libtcod.console_clear(panel)

    # Print the game messages, one line at a time
    y = 1
    for message in message_log.messages:
        libtcod.console_set_default_foreground(panel, message.color)
        libtcod.console_print_ex(panel, message_log.x, y, libtcod.BKGND_NONE, libtcod.LEFT, message.text)
        y += 1

    render_bar(panel, 1, 1, bar_width, 'HP', player.fighter.hp, player.fighter.max_hp,
               libtcod.light_red, libtcod.darker_red)
    #render_bar(panel, 1, 2, bar_width, 'Hunger', player.fighter.hunger, 100,
    #           libtcod.light_blue, libtcod.darker_blue)
    render_bar(panel, 1, 3, bar_width, 'Contact', player.fighter.contact, 100,
               libtcod.dark_yellow, libtcod.darker_yellow)

    libtcod.console_print_ex(panel, 1, 4, libtcod.BKGND_NONE, libtcod.LEFT,
                             'Gold: {0}'.format(player.fighter.gold))
    libtcod.console_print_ex(panel, 1, 5, libtcod.BKGND_NONE, libtcod.LEFT,
                             'XP: {0}'.format(player.level.current_xp))
    libtcod.console_print_ex(panel, 1, 6, libtcod.BKGND_NONE, libtcod.LEFT,
                             'Dungeon level: {0}'.format(game_map.dungeon_level))

    libtcod.console_set_default_foreground(panel, libtcod.light_gray)

    #Show what is underfoot
    #if game_map.tiles[player.x][player.y].name

    libtcod.console_print_ex(panel, 1, 0, libtcod.BKGND_NONE, libtcod.LEFT, underfoot)



    libtcod.console_blit(panel, 0, 0, screen_width, panel_height, 0, 0, panel_y)

    #libtcod.console_blit(mpanel, 0, 0, screen_width, screen_height, 0, 0, 0)

    if game_state in (GameStates.SHOW_INVENTORY, GameStates.DROP_INVENTORY):
        if game_state == GameStates.SHOW_INVENTORY:
            inventory_title = 'Press the key next to an item to use it, or Esc to cancel.\n'
        else:
            inventory_title = 'Press the key next to an item to drop it, or Esc to cancel.\n'

        inventory_menu(con, inventory_title, player, 50, screen_width, screen_height)

    elif game_state == GameStates.LEVEL_UP:
        level_up_menu(con, 'Level up! Choose a stat to raise:', player, 40, screen_width, screen_height)

    elif game_state == GameStates.CHARACTER_SCREEN:
        character_screen(player, 30, 10, screen_width, screen_height)

    elif game_state == GameStates.SHOP_SCREEN:
        #print(shops[0])
        shop_menu(con, 'Welcome to my shop!', player, 50, screen_width, screen_height, shops[0])


    libtcod.console_set_default_background(con, (0,0,0))

def clear_all(con, entities, allies):
    for entity in entities:
        clear_entity(con, entity)
    for entity in allies:
        clear_entity(con, entity)


def draw_entity(con, entity, fov_map, game_map, tilemap):
    if game_map.tiles[entity.x][entity.y].explored:
        if libtcod.map_is_in_fov(fov_map, entity.x, entity.y):
            libtcod.console_set_default_background(con, (86, 114, 143))
            libtcod.console_set_default_foreground(con, entity.color)
            libtcod.console_put_char(con, entity.x, entity.y, entity.char, libtcod.BKGND_ALPHA(1.0))
        else:  # shaded discovered item not in fov
            # libtcod.console_set_default_background(con, (86, 114, 143))
            libtcod.console_set_default_background(con, (43, 57, 71))
            libtcod.console_set_default_foreground(con, libtcod.grey)  # entity.color)
            libtcod.console_put_char(con, entity.x, entity.y, entity.char, libtcod.BKGND_ALPHA(1.0))
    else:
        if entity.item:
            libtcod.console_set_default_foreground(con, libtcod.white)
            libtcod.console_put_char(con, entity.x, entity.y, '+', libtcod.BKGND_NONE)
        elif isinstance(entity.ai, Follower) and entity.ai.found:
            # libtcod.console_set_default_background(con, (86, 114, 143))
            libtcod.console_set_default_background(con, (43, 57, 71))
            libtcod.console_set_default_foreground(con, libtcod.grey)  # entity.color)
            libtcod.console_put_char(con, entity.x, entity.y, entity.char, libtcod.BKGND_ALPHA(1.0))

    '''
    #if (entity.stairs and game_map.tiles[entity.x][entity.y].explored) or entity.item or libtcod.map_is_in_fov(fov_map, entity.x, entity.y):
    if  (entity.stairs and game_map.tiles[entity.x][entity.y].explored) or entity.item or isinstance(entity.ai, Follower) or libtcod.map_is_in_fov(fov_map, entity.x, entity.y):

        if entity.item and not game_map.tiles[entity.x][entity.y].explored:
            libtcod.console_set_default_foreground(con, libtcod.white)
            libtcod.console_put_char(con, entity.x, entity.y, '+', libtcod.BKGND_NONE)
        elif isinstance(entity.ai, Follower) and not entity.ai.found:
            libtcod.console_set_default_foreground(con, entity.color)
            libtcod.console_put_char(con, entity.x, entity.y, ' ', libtcod.BKGND_NONE)
        else:
            if game_map.tiles[entity.x][entity.y].explored: #entity.stairs and
                if libtcod.map_is_in_fov(fov_map, entity.x, entity.y):
                    libtcod.console_set_default_background(con, (86, 114, 143))
                    libtcod.console_set_default_foreground(con, entity.color)
                    libtcod.console_put_char(con, entity.x, entity.y, entity.char, libtcod.BKGND_ALPHA(1.0))
                else:   #shaded discovered item not in fov
                    #libtcod.console_set_default_background(con, (86, 114, 143))
                    libtcod.console_set_default_background(con, (43, 57, 71))
                    libtcod.console_set_default_foreground(con, libtcod.grey)#entity.color)
                    libtcod.console_put_char(con, entity.x, entity.y, entity.char, libtcod.BKGND_ALPHA(1.0))
            else:
                libtcod.console_set_default_background(con, (86,114,143))
                libtcod.console_set_default_foreground(con, entity.color)
                libtcod.console_put_char(con, entity.x, entity.y, entity.char, libtcod.BKGND_ALPHA(1.0))
    '''

def clear_entity(con, entity):
    # erase the character that represents this object
    libtcod.console_put_char(con, entity.x, entity.y, ' ', libtcod.BKGND_NONE)
