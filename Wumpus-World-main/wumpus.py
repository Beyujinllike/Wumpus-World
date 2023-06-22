import random as random
import pygame as pygame
import copy
import easygui

pygame.init()  # start up pygame
clock = pygame.time.Clock()
cave_size, room_margin = 4, 5   # how many rooms in either direction of the cave, # wall size
pit_size = round(0.1 * ((cave_size * cave_size) - 1))  # number of pits
room_dimension = ((pygame.display.Info().current_h - 100) - (
        room_margin * (cave_size - 1)) - 100) / cave_size  # width and height of each room
screen = pygame.display.set_mode([(room_dimension * cave_size) + (cave_size * room_margin), (
        (room_dimension * cave_size) + (cave_size * room_margin)) + 100])  # window creation and size
quit_game, show_rooms = False, False
# game colors 수정
BLACK, WALL, VISITED, WHITE, RED = (0, 0, 0), (97, 49, 0), (0, 255, 0), (255, 255, 255), (255, 0, 0)
# valid keyboard keys (eliminates if, else)
MOVEMENT_KEYBOARD = {pygame.K_UP: "UP", pygame.K_DOWN: "DOWN", pygame.K_LEFT: "LEFT", pygame.K_RIGHT: "RIGHT"}
SHOOT_KEYBOARD = {pygame.K_w: "UP", pygame.K_s: "DOWN", pygame.K_a: "LEFT", pygame.K_d: "RIGHT"}
# initial game values 수정_추후의 문제지만 point싹 필요없잖아 그냥 죽으면 다시 하고만 있으면 됨.
start_level, start_points, move_point, arrow_point, death_points = 1, 100, 1, 10, 1000
# agent, wumpus, and gold image
hero = pygame.transform.smoothscale(pygame.image.load("Wumpus-World-main\\images\\hero.png"), (room_dimension, room_dimension))
wumpus = pygame.transform.smoothscale(pygame.image.load("Wumpus-World-main\\images\\wumpus.png"), (room_dimension, room_dimension))
gold = pygame.transform.smoothscale(pygame.image.load("Wumpus-World-main\\images\\gold.png"), (room_dimension, room_dimension))



#수정?_그대로일듯
def draw_text(surface, text, size, x, y, color):    # for displaying texts
    font = pygame.font.Font(pygame.font.match_font('arial'), size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surface.blit(text_surface, text_rect)


class CaveRoom(object):  # class for wumpus, and room (stationary)
    def __init__(self, name, col, rw):
        self.name = name
        self.column = col
        self.row = rw

#이걸 통으로 수정 가능한가 - 사실 사후조치는 삭제할 필요가 없는데..
class Agent(object):  # Agents can move around
    def __init__(self, name, col, rw, points, level):
        self.name, self.column, self.row, self.next_column, self.next_row = name, col, rw, col, rw
        self.points, self.level, self.playing = points, level, True

    def in_pit(self):  # when agent falls into a pit #pit에 빠지면 그만한다
        global start_points
        self.playing, start_points = False, self.points - death_points
        if not easygui.ynbox('You fell into a pit', 'Game Over !!!', ['Restart', 'Quit']):
            global quit_game
            quit_game = True

    def in_gold(self):  # agent in gold room
        Cave.room[self.next_column][self.next_row][0].name = "Glitter"
        self.playing = False
        if easygui.ynbox('You got the gold', 'You Won !!!', ('Continue', 'Quit')): #수정
            global start_points
            global start_level
            start_points, start_level = self.points,  self.level + 1
        else:
            global quit_game
            quit_game = True

    def in_wumpus(self):  # agent eaten by wumpus
        start_points, self.playing = self.points - death_points, False
        if not easygui.ynbox('You were killed by Wumpus', 'Game Over !!!', ['Restart', 'Quit']):
            global quit_game
            quit_game = True

    def in_stench(self):  # agent in room adjacent to wumpus's room
        Cave.stench[self.next_column][self.next_row] = 2

    def in_breeze(self):  # agent in room adjacent to pit's room
        Cave.breeze[self.next_column][self.next_row] = 2

    def check_room(self):  # check what's in the room the agent is about to enter  이용
        Cave.visited[self.column][self.row] = 1  # add agent's previous room to safe rooms
        if len(Cave.room[self.next_column][self.next_row]) > 1:
            if Cave.room[self.next_column][self.next_row][1].name == "Wumpus":
                self.in_wumpus()
        elif Cave.room[self.next_column][self.next_row][0].name == "Gold":
            Cave.room[self.next_column][self.next_row][0].name = "Room"
            self.in_gold()
        elif Cave.room[self.next_column][self.next_row][0].name == "Pit":
            self.in_pit()
        if Cave.stench[self.next_column][self.next_row] > 0:
            self.in_stench()
        if Cave.breeze[self.next_column][self.next_row] > 0:
            self.in_breeze()
        return False

    def shoot_action(self):
        self.check_wumpus_shot()

    def move_action(self): #이용
        self.check_room()  # check what's in the new room
        self.row, self.column = self.next_row, self. next_column  # Go ahead and move

    def action(self, direction, action): #이용을 통해 move하도록 random(방향)?
        if action == 'move':
            self.points -= move_point
        else:
            self.points -= arrow_point
        if direction == "UP":
            if self.row > 0:  # If within boundaries of cave
                self.next_column, self.next_row = self.column, self.row - 1
                if action == 'move':
                    self.move_action()
                else:
                    self.shoot_action()
            
        elif direction == "LEFT":
            if self.column > 0:
                self.next_column, self.next_row = self.column - 1, self.row
                if action == 'move':
                    self.move_action()
                else:
                    self.shoot_action()
        elif direction == "RIGHT":
            if self.column < cave_size - 1:
                self.next_column, self.next_row = self.column + 1, self.row
                if action == 'move':
                    self.move_action()
                else:
                    self.shoot_action()
        elif direction == "DOWN":
            if self.row < cave_size - 1:
                self.next_column, self.next_row = self.column, self.row + 1
                if action == 'move':
                    self.move_action()
                else:
                    self.shoot_action()


    def check_wumpus_shot(self):  # when agent shoots arrow, check if it hits the wumpus
        if len(Cave.room[self.next_column][self.next_row]) > 1:
            if Cave.room[self.next_column][self.next_row][1].name == "Wumpus":
                Cave.room[self.next_column][self.next_row].pop(1)  # remove wumpus from cave
                Cave.visited[self.next_column][self.next_row] = 1
                for rw in range(cave_size):
                    for col in range(cave_size):
                        Cave.stench[rw][col] = 0  # delete stench sensors
                easygui.msgbox('You killed the Wumpus', 'Good Job !!!', 'Continue')


class Cave(object):  # main class #각 sensor에 대한 상태..이용
    global cave_size

    def __init__(self):
        self.room, self.breeze, self.stench, self.visited, self.Hero = None, None, None, None, None

    def reset(self):  # new game/restart
        self.room = []
        for rw in range(cave_size):  # creating cave and initializing sensors
            self.room.append([])
            for col in range(cave_size):
                self.room[rw].append([])
        self.visited, self.stench, self.breeze = copy.deepcopy(self.room), copy.deepcopy(self.room), copy.deepcopy(self.room)
        for rw in range(cave_size):  # filling cave with rooms
            for col in range(cave_size):
                temp_room = CaveRoom("Room", col, rw)
                self.room[col][rw].append(temp_room)
                self.visited[col][rw], self.stench[col][rw], self.breeze[col][rw] = 0, 0, 0
        self.visited[0][0] = 1 #처음에 0,0에서 시작하니까?
        count = 0
        while count < pit_size+2:  # adding Pits, gold, and wumpus
            random_row = random.randint(1, cave_size - 1)  # random from 1 (since agent starts in room 0,0)
            random_column = random.randint(1, cave_size - 1)
            if self.room[random_column][random_row][0].name != 'Pit':
                if count < pit_size:
                    self.room[random_column][random_row][0].name = 'Pit'
                    self.place_sensor("breeze", random_column, random_row)
                elif count < pit_size + 1:      # add gold
                    self.room[random_column][random_row][0].name = 'Gold'
                else:       # add wumpus
                    temp_room = CaveRoom("Wumpus", random_column, random_row)
                    self.room[random_column][random_row].append(temp_room)
                    self.place_sensor("stench", random_column, random_row)
                count += 1
        self.Hero = Agent("Hero", 0, 0, start_points, start_level)  # hero with 0,0 as starting room

    def place_the_sensor(self, sensor, col, rw):
        if sensor == 'stench':
            self.stench[col][rw] = 1
        else:
            self.breeze[col][rw] = 1

    def place_sensor(self, sensor, random_column, random_row):
        if random_row < cave_size - 1 and self.room[random_column][random_row + 1][0].name != 'Pit':
            self.place_the_sensor(sensor, random_column, random_row+1)
        if random_row > 0 and self.room[random_column][random_row - 1][0].name != 'Pit':
            self.place_the_sensor(sensor, random_column, random_row - 1)
        if random_column < cave_size - 1 and self.room[random_column + 1][random_row][0].name != 'Pit':
            self.place_the_sensor(sensor, random_column + 1, random_row)
        if random_column > 0 and self.room[random_column - 1][random_row][0].name != 'Pit':
            self.place_the_sensor(sensor, random_column - 1, random_row)

    def update(self):  # update function
        for col in range(cave_size):        # remove agent from previous rooms
            for rw in range(cave_size):
                for count in range(len(self.room[col][rw])):
                    if self.room[col][rw][count].name == "Hero":
                        self.room[col][rw].remove(self.room[col][rw][count])
        self.room[int(self.Hero.column)][int(self.Hero.row)].append(self.Hero)  # update agent room


Cave = Cave()
while not quit_game:
    Cave.reset()
    while Cave.Hero.playing:
        for event in pygame.event.get():  # catching events
            if event.type == pygame.WINDOWCLOSE:
                quit_game = True
                Cave.Hero.playing = False
            elif event.type == pygame.KEYDOWN:  # for keyboard
                if event.key in MOVEMENT_KEYBOARD:
                    Cave.Hero.action(MOVEMENT_KEYBOARD[event.key], 'move')
                elif event.key in SHOOT_KEYBOARD:
                    Cave.Hero.action(SHOOT_KEYBOARD[event.key], 'shoot')
            break   # stop listening for events when pop up shows
        screen.fill(BLACK)
        for row in range(cave_size):  # drawing room
            for column in range(cave_size):
                for i in range(0, len(Cave.room[column][row])):
                    if Cave.room[column][row][i].name == "Pit" and show_rooms:
                        Color = BLACK
                    else:
                        Color = WALL
                    screen_rect = [(room_margin + room_dimension) * column + room_margin,
                                   (room_margin + room_dimension) * row + room_margin,
                                   room_dimension,
                                   room_dimension]
                    if Cave.room[column][row][i].name == "Hero":
                        screen.blit(hero, screen_rect)
                    if Cave.room[column][row][i].name == "Wumpus":
                        screen.blit(wumpus, screen_rect)
                    if Cave.visited[column][row] == 1:
                        Color = VISITED
                    # to show hero, gold, pit, and wumpus
                    sensor_text_x = (room_margin + room_dimension) * column + room_margin + (room_dimension / 2)
                    sensor_text_y = (room_margin + room_dimension) * row + room_margin + (room_dimension / 2)
                    if show_rooms:
                        if Cave.room[column][row][i].name == "Gold":
                            screen.blit(gold, screen_rect)
                        if Cave.room[column][row][i].name != "Hero" and Cave.room[column][row][i].name != "Gold" \
                                and Cave.room[column][row][i].name != "Wumpus":
                            pygame.draw.rect(screen, Color, [(room_margin + room_dimension) * column + room_margin,
                                                             (room_margin + room_dimension) * row + room_margin,
                                                             room_dimension,
                                                             room_dimension])
                        if Cave.stench[column][row] > 0:
                            draw_text(screen, 'stench', 15, sensor_text_x, sensor_text_y - 15, RED)
                        if Cave.breeze[column][row] > 0:
                            draw_text(screen, 'breeze', 15, sensor_text_x, sensor_text_y, WHITE)
                    else:
                        # to hide gold and wumpus
                        if Cave.room[column][row][i].name != "Hero":
                            pygame.draw.rect(screen, Color, [(room_margin + room_dimension) * column + room_margin,
                                                             (room_margin + room_dimension) * row + room_margin,
                                                             room_dimension,
                                                             room_dimension])
                    if Cave.room[column][row][i].name == "Glitter":
                        screen.blit(gold, screen_rect)
            # if a hero enters or has entered a room adjacent to wumpus or pits, display appropriate sensor in room
                    if Cave.stench[column][row] == 2:
                        draw_text(screen, 'stench', 15, sensor_text_x, sensor_text_y - 15, RED)
                    if Cave.breeze[column][row] == 2:
                        draw_text(screen, 'breeze', 15, sensor_text_x, sensor_text_y, WHITE)
        # display level, points, and controls
        bottom_text = (cave_size * (room_dimension + room_margin))
        draw_text(screen, "Level: " + str(Cave.Hero.level), 20, bottom_text / 2, bottom_text + 20, WHITE)
        draw_text(screen, "Points: " + str(Cave.Hero.points), 20, bottom_text / 2, bottom_text + 40, WHITE)
        clock.tick(60)  # 60 FPS
        pygame.display.flip()  # update contents of display
        Cave.update()
pygame.quit()  # quit game
