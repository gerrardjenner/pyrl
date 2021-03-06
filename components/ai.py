import libtcodpy as libtcod

from random import randint

from game_messages import Message


class BasicMonster:
    def take_turn(self, target, fov_map, game_map, entities, allies):
        results = []

        monster = self.owner

        game_map.tiles[monster.x][monster.y].contaminants += 10

        if monster.distance_to(target) < 4:
            if(target.fighter.contact < 100):
                target.fighter.contact += 1
                #attack_results = monster.fighter.attack(target)
                #results.extend(attack_results)

        if libtcod.map_is_in_fov(fov_map, monster.x, monster.y):

            if monster.distance_to(target) >= 2:
                e = allies + entities
                monster.move_astar(target, e, game_map)

            elif target.fighter.hp > 0:
                attack_results = monster.fighter.attack(target)
                results.extend(attack_results)

        #if game_map.tiles[monster.x][monster.y].contaminants < 100:
        #    game_map.tiles[monster.x][monster.y].contaminants += 10
        #else:
            for x in range(monster.x - 1, monster.x + 2):
                for y in range(monster.y - 1, monster.y + 2):
                    game_map.tiles[x][y].contaminants += 25
            #game_map.tiles[monster.x][monster.y].contaminants = 100

        return results


class ConfusedMonster:
    def __init__(self, previous_ai, number_of_turns=10):
        self.previous_ai = previous_ai
        self.number_of_turns = number_of_turns

    def take_turn(self, target, fov_map, game_map, entities, allies):
        results = []

        if self.number_of_turns > 0:
            random_x = self.owner.x + randint(0, 2) - 1
            random_y = self.owner.y + randint(0, 2) - 1

            if random_x != self.owner.x and random_y != self.owner.y:
                e = entities + allies
                self.owner.move_towards(random_x, random_y, game_map, e)

            self.number_of_turns -= 1
        else:
            self.owner.ai = self.previous_ai
            results.append({'message': Message('The {0} is no longer confused!'.format(self.owner.name), libtcod.red)})

        return results


class Follower:
    def __init__(self, found=False):
        self.found = found

    def take_turn(self, target, fov_map, game_map, entities, allies):
        results = []
        e = entities + allies

        follower = self.owner
        #print('{0}, {1}'.format(follower.x, follower.y))
        if self.found or libtcod.map_is_in_fov(fov_map, follower.x, follower.y):
            self.found = True
            if follower.distance_to(target) >= 2:
                follower.move_astar(target, e, game_map)
                #if follower.distance_to(target) > 1:
                #    follower.move_astar(target, entities, game_map)
            #elif follower.x == target.x and follower.y == target.y:
            #    #on top of target - move away
            #    f = target.x, target.y
            #    f.x += randint(0,2)-1
            #    f.y += randint(0,2)-1
            #    follower.move_astar(f, e, game_map)

            #elif target.fighter.hp > 0:
            #    attack_results = follower.fighter.attack(target)
            #    results.extend(attack_results)

            for f in e:
                if isinstance(f.ai, BasicMonster) and not f.char == '%':
                    if libtcod.map_is_in_fov(fov_map, f.x, f.y):
                        if follower.distance_to(f) < 2:
                            if target.fighter.hp > 0:
                                # print('Attack')
                                attack_results = follower.fighter.attack(f)
                                results.extend(attack_results)
                                # only do one attack
                                break
                        else:
                            follower.move_astar(f, entities, game_map)#ignore allies in a* but then check if on top of another

                        #if follower.distance_to(f) >= 2:
                        #    follower.move_astar(f, entities, game_map)#ignore allies in a* but then check if on top of another
                        #elif target.fighter.hp > 0:
                        #    #print('Attack')
                        #    attack_results = follower.fighter.attack(f)
                        #    results.extend(attack_results)
                        #    #only do one attack
                        #    break


        return results

class BossMonster:
    def take_turn(self, target, fov_map, game_map, entities, allies):
        results = []

        monster = self.owner

        game_map.tiles[monster.x][monster.y].contaminants += 10

        if monster.distance_to(target) < 4:
            if(target.fighter.contact < 100):
                target.fighter.contact += 1
                #attack_results = monster.fighter.attack(target)
                #results.extend(attack_results)

        if libtcod.map_is_in_fov(fov_map, monster.x, monster.y):

            if monster.distance_to(target) >= 2:
                e = allies + entities
                monster.move_astar(target, e, game_map)

            elif target.fighter.hp > 0:
                attack_results = monster.fighter.attack(target)
                results.extend(attack_results)

        #if game_map.tiles[monster.x][monster.y].contaminants < 100:
        #    game_map.tiles[monster.x][monster.y].contaminants += 10
        #else:
            for x in range(monster.x - 1, monster.x + 2):
                for y in range(monster.y - 1, monster.y + 2):
                    game_map.tiles[x][y].contaminants += 25
            #game_map.tiles[monster.x][monster.y].contaminants = 100

        return results