from random import randint, choice

p_empty = '-'  # заполнитель поля
p_ship = "■"
p_kill = 'X'      # метка первого игрока
p_shot = 'O'      # второго игрока


class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f"({self.x}, {self.y})"


class BoardException(Exception):
    pass


class BoardOutException(BoardException):
    def __str__(self):
        return "Вы пытаетесь выстрелить за доску!"


class BoardUsedException(BoardException):
    def __str__(self):
        return "Вы уже стреляли в эту клетку"


class BoardWrongShipException(BoardException):
    pass


class Ship:
    def __init__(self, xy, s, way):
        self.xy = xy
        self.s = s
        self.way = way
        self.lives = s

    @property
    def dots(self):
        ship_dots = []
        for i in range(self.s):
            x = self.xy.x
            y = self.xy.y
            if self.way:
                x += i
            else:
                y += i
            ship_dots.append(Dot(x, y))
        return ship_dots

    def shooten(self, shot):
        return shot in self.dots


class Board:
    def __init__(self, size=6, hid=False ):
        self.hid = hid
        self.size = size

        self.live_ships = 7
        self.field = [[p_empty]*size for _ in range(size)]

        self.ships = []
        self.busy = []

    def add_ship(self, ship):
        for d in ship.dots:
            if d in self.busy or self.out(d):
                raise BoardWrongShipException()
        for d in ship.dots:
            self.field[d.x][d.y] = p_ship
            self.busy.append(d)
        self.ships.append(ship)
        self.round(ship)

    def round(self, ship, hid=False):
        near = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        for d in ship.dots:
            for px, py in near:
                xy = Dot(d.x + px, d.y + py)
                
                if not self.out(xy) and xy not in self.busy:
                    #print(f'{xy} out {not self.out(xy)}  busy {xy not in self.busy}')
                    if hid:
                        self.field[xy.x][xy.y] = p_shot
                    self.busy.append(xy)

    def out(self, d):
        return not (d.x in range(self.size) and d.y in range(self.size))

    def __str__(self):
        text = ''
        text = '  1 2 3 4 5 6'
        for i, f in enumerate(self.field):
            text += f'\n{i+1} '+' '.join(f)
        if self.hid:
            text = text.replace(p_ship, p_empty)
        return text

    def shot(self, xy):
        if self.out(xy):
            raise BoardOutException()

        if xy in self.busy:
            raise BoardUsedException()

        self.busy.append(xy)

        for ship in self.ships:
            if xy in ship.dots:
                ship.lives -= 1
                self.field[xy.x][xy.y] = p_kill
                if ship.lives == 0:
                    self.live_ships -= 1
                    self.round(ship, hid=True)
                    print("Корабль уничтожен!")
                    return True
                else:
                    print("Корабль ранен!")
                    return True

        self.field[xy.x][xy.y] = p_shot
        print("Мимо!")
        return False

    def begin(self):
        self.busy = []


class Player:
    def __init__(self, own, enemy):
        self.own = own
        self.enemy = enemy
        
    def ask(self):
        raise NotImplementedError()    
    
    def move(self):
        while True:
            try:
                target = self.ask()
                res = self.enemy.shot(target)
                return res
            except BoardException as e:
                print(e)

class AI(Player):
    def ask(self):
        xy = Dot(randint(0,5), randint(0,5))
        print(f'Ходит АИ x:{xy.x+1} y:{xy.y+1}')
        return xy
        
class User(Player):
    def ask(self):
        while True:
            xy = input('Ваш ход:').split()
            if len(xy) != 2:
                print('Введите две оординаты')
                continue
            
            x,y = xy
            
            if not(x.isdigit()) or not(y.isdigit()):
                print('Введите цифры')
                continue
            x, y = int(x), int(y)
            return Dot(x-1, y-1)

class Game:
    def __init__(self, size = 6):
        self.size = size
        b1 = self.random_board()
        b2 = self.random_board()
        b2.hid = True
        self.us = User(b1, b2)
        self.ai = AI(b2,b1)
         
    def random_board(self):
        board = None
        while board is None:
            board = self.creat_board()
        return board
            
    def no_busy(self, board):
        free = []
        for x in range(self.size):
            for y in range(self.size):
                xy = Dot(x, y)
                if not xy in board.busy:
                    free.append(xy)
        return free
    
    def creat_board(self):
        lens = [3, 2, 2, 1, 1, 1, 1]
        board = Board(self.size)
        i = 0
        for l in lens:
            while True:
                i += 1
                if i > 1000:
                    return None
                free = self.no_busy(board)
                if free == []:
                    return None
                ship = Ship(choice(free), l, randint(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.begin()
        return board
                    
    def greet(self):
        print("-------------------")
        print("  Приветсвуем вас  ")
        print("      в игре       ")
        print("    морской бой    ")
        print("-------------------")
        print(" формат ввода: x y ")
        print(" x - номер строки  ")
        print(" y - номер столбца ")
        
    def board_rep(self, string, hid):
        ss = ''.join(string)
        if hid:
            ss = ss.replace(p_ship, p_empty)
        return ss
    
    def board_print(self, boards):
        text = ''
        text = "-"*15 + '\t\t' + "-"*15
        text += "\nДоска пользователя:"
        text += "\tДоска компьютера:"
        
        text += '\n  1 2 3 4 5 6\t\t  1 2 3 4 5 6'
        for i in range(self.size):
            own = self.board_rep(boards.own.field[i], boards.own.hid)
            enemy = self.board_rep(boards.enemy.field[i], boards.enemy.hid)
            text += f'\n{i+1} '+' '.join(own) + f'\t\t{i+1} '+' '.join(enemy)
        return text
        
    def loop(self):
        num = 0
        while True:
            print(self.board_print(self.us))
            if num % 2 == 0:
                print("-"*20)
                print("Ходит пользователь!", end = '')
                repeat = self.us.move()
            else:
                print("-"*20)
                print("Ходит компьютер!", end = '')
                repeat = self.ai.move()
            if repeat:
                num -= 1
            
            if self.ai.own.live_ships == 0:
                print("-"*20)
                print("Пользователь выиграл!")
                break
            
            if self.us.own.live_ships == 0:
                print("-"*20)
                print("Компьютер выиграл!")
                break
            num += 1
            
    def start(self):
        self.greet()
        self.loop()
            
g = Game()
g.start()            
  
            
