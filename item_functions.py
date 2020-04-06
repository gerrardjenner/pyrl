import libtcodpy as libtcod

from components.ai import ConfusedMonster

from game_messages import Message


def acquire_gold(*args, **kwargs):
    entity = args[0]
    amount = kwargs.get('amount')

    results = []
    entity.fighter.addgold(amount)
    results.append({'gold_added': False, 'message': Message('You picked up {0} gold!'.format(amount), libtcod.gold)})

    return results


def heal(*args, **kwargs):
    entity = args[0]
    amount = kwargs.get('amount')

    results = []

    if entity.fighter.hp == entity.fighter.max_hp:
        results.append({'consumed': False, 'message': Message('You are already at full health', libtcod.yellow)})
    else:
        entity.fighter.heal(amount)
        results.append({'consumed': True, 'message': Message('Your wounds start to feel better!', libtcod.green)})

    return results


def eat(*args, **kwargs):
    entity = args[0]
    amount = kwargs.get('amount')

    results = []

    if entity.fighter.hunger == 0:
        results.append({'consumed': False, 'message': Message('You are already full!', libtcod.yellow)})
    else:
        entity.fighter.eat(amount)
        results.append({'consumed': True, 'message': Message('You eat the apple ... mmm!', libtcod.green)})

    return results


def clean(*args, **kwargs):
    entity = args[0]
    amount = kwargs.get('amount')

    results = []

    if entity.fighter.contact == 0:
        results.append({'consumed': False, 'message': Message('You are already clean', libtcod.light_blue)})
    else:
        entity.fighter.clean(amount)
        results.append({'consumed': True, 'message': Message('Happy Birthday to you Happy Birthday to you ...', libtcod.light_blue)})

    return results


def cast_lightning(*args, **kwargs):
    caster = args[0]
    entities = kwargs.get('entities')
    fov_map = kwargs.get('fov_map')
    damage = kwargs.get('damage')
    maximum_range = kwargs.get('maximum_range')

    results = []

    target = None
    closest_distance = maximum_range + 1

    for entity in entities:
        if entity.fighter and entity != caster and libtcod.map_is_in_fov(fov_map, entity.x, entity.y):
            distance = caster.distance_to(entity)

            if distance < closest_distance:
                target = entity
                closest_distance = distance

    if target:
        results.append({'consumed': True, 'target': target, 'message': Message(
            'A lighting bolt strikes the {0} with a loud thunder! The damage is {1}'.format(target.name, damage))})
        results.extend(target.fighter.take_damage(damage))
    else:
        results.append(
            {'consumed': False, 'target': None, 'message': Message('No enemy is close enough to strike.', libtcod.red)})

    return results


def throw_cleaner(*args, **kwargs):
    entities = kwargs.get('entities')
    fov_map = kwargs.get('fov_map')
    game_map = kwargs.get('game_map')
    damage = kwargs.get('damage')
    radius = kwargs.get('radius')
    target_x = kwargs.get('target_x')
    target_y = kwargs.get('target_y')

    results = []
    print('throw_cleaner')

    if not libtcod.map_is_in_fov(fov_map, target_x, target_y):
        results.append({'consumed': False,
                        'message': Message('You cannot target a tile outside your field of view.', libtcod.yellow)})
        return results

    for x in range(target_x-1, target_x+2):
        for y in range(target_y - 1, target_y + 2):
            game_map.tiles[x][y].contaminants = 0

    #game_map.tiles[target_x][target_y].contaminants = 0
    results.append({'clean': True,
                    'message': Message('Everything within {0} tiles is clean!'.format(radius),
                                       libtcod.orange)})

    for entity in entities:
        if entity.distance(target_x, target_y) <= radius and entity.fighter:
            results.append({'message': Message('The {0} gets {1}% cleaner.'.format(entity.name, damage),
                                               libtcod.orange)})
            entity.fighter.clean(damage)
            #results.extend(entity.fighter.clean(damage))
            #results.extend()

    #update the map state of every tile in radius

    return results


def cast_fireball(*args, **kwargs):
    entities = kwargs.get('entities')
    fov_map = kwargs.get('fov_map')
    damage = kwargs.get('damage')
    radius = kwargs.get('radius')
    target_x = kwargs.get('target_x')
    target_y = kwargs.get('target_y')

    results = []

    if not libtcod.map_is_in_fov(fov_map, target_x, target_y):
        results.append({'consumed': False,
                        'message': Message('You cannot target a tile outside your field of view.', libtcod.yellow)})
        return results

    results.append({'consumed': True,
                    'message': Message('The fireball explodes, burning everything within {0} tiles!'.format(radius),
                                       libtcod.orange)})

    for entity in entities:
        if entity.distance(target_x, target_y) <= radius and entity.fighter:
            results.append({'message': Message('The {0} gets burned for {1} hit points.'.format(entity.name, damage),
                                               libtcod.orange)})
            results.extend(entity.fighter.take_damage(damage))

    return results


def cast_confuse(*args, **kwargs):
    entities = kwargs.get('entities')
    fov_map = kwargs.get('fov_map')
    target_x = kwargs.get('target_x')
    target_y = kwargs.get('target_y')

    results = []

    if not libtcod.map_is_in_fov(fov_map, target_x, target_y):
        results.append({'consumed': False,
                        'message': Message('You cannot target a tile outside your field of view.', libtcod.yellow)})
        return results

    for entity in entities:
        if entity.x == target_x and entity.y == target_y and entity.ai:
            confused_ai = ConfusedMonster(entity.ai, 10)

            confused_ai.owner = entity
            entity.ai = confused_ai

            results.append({'consumed': True, 'message': Message(
                'The eyes of the {0} look vacant, as he starts to stumble around!'.format(entity.name),
                libtcod.light_green)})

            break
    else:
        results.append(
            {'consumed': False, 'message': Message('There is no targetable enemy at that location.', libtcod.yellow)})

    return results



def locate_ally(*args, **kwargs):
    results = []

    allies = kwargs.get('alist')
    #print(allies[-1].ai.found)
    allies[-1].ai.found = True

    results.append({'consumed': True, 'message': Message('You reach out with your mind and sense an ally nearby!', libtcod.light_green)})

    return results