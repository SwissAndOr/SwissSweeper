import random
import time


class Game:
    def __init__(self, width, height, mines):
        if mines > width * height - 9:
            raise ValueError("more mines than field spaces")

        self._field = [[0 for _ in range(width)] for _ in range(height)]
        self._cleared = [[False for _ in range(width)] for _ in range(height)]
        self._flagged = [[False for _ in range(width)] for _ in range(height)]
        self._width = width
        self._height = height
        self._mines = mines
        self._mines_left = mines
        self._generated = False
        self._start_time = 0

    def _generate(self, start_x=None, start_y=None):
        mines_remaining = self._mines
        while mines_remaining > 0:
            x = random.randrange(self._width)
            y = random.randrange(self._height)
            if self._field[y][x] == -1:
                continue
            if start_x is not None and start_y is not None:
                if abs(x - start_x) <= 1 and abs(y - start_y) <= 1:
                    continue

            self._field[y][x] = -1
            for neighbor_y in range(max(0, y - 1), min(self._height, y + 2)):
                for neighbor_x in range(max(0, x - 1), min(self._width, x + 2)):
                    if self._field[neighbor_y][neighbor_x] >= 0:
                        self._field[neighbor_y][neighbor_x] += 1
            mines_remaining -= 1
        self._start_time = time.time()

    def clear(self, x, y, ignore_flags=False):
        if not (0 <= x < self._width and 0 <= y < self._height):
            raise IndexError("field coordinates out of range")

        if self._cleared[y][x] or (self._flagged[y][x] and not ignore_flags):
            return

        if not self._generated:
            self._generate(x, y)
            self._generated = True

        if self._field[y][x] != -1:
            self.flag(x, y, False)
            self._cleared[y][x] = True
            if self._field[y][x] == 0:
                for neighbor_y in range(max(0, y - 1), min(self._height, y + 2)):
                    for neighbor_x in range(max(0, x - 1), min(self._width, x + 2)):
                        if not self._cleared[neighbor_y][neighbor_x]:
                            self.clear(neighbor_x, neighbor_y, True)
            if self._check_win():  # Win game
                return True
            return
        else:
            self._cleared[y][x] = True  # Lose game
            return False

    def flag(self, x, y, state=None):
        if state is not None and self._flagged[y][x] == state:
            return
        if not self._cleared[y][x]:
            self._mines_left += 1 if self._flagged[y][x] else -1
            self._flagged[y][x] = not self._flagged[y][x]

    def clear_around(self, x, y):
        if self._field[y][x] < 1:
            return
        neighbor_flags = 0
        for neighbor_y in range(max(0, y - 1), min(self._height, y + 2)):
            for neighbor_x in range(max(0, x - 1), min(self._width, x + 2)):
                if self._flagged[neighbor_y][neighbor_x]:
                    neighbor_flags += 1
        if neighbor_flags == self._field[y][x]:
            for neighbor_y in range(max(0, y - 1), min(self._height, y + 2)):
                for neighbor_x in range(max(0, x - 1), min(self._width, x + 2)):
                    result = self.clear(neighbor_x, neighbor_y)
                    if result is not None:
                        return result

    def _check_win(self):
        for y in range(self._height):
            for x in range(self._width):
                if (self._field[y][x] >= 0) != self._cleared[y][x]:
                    return False
        return True

    def get_state(self, x, y):
        if self._cleared[y][x] is None:
            return None
        else:
            return self._field[y][x]

    def get_time(self):
        return int(time.time() - self._start_time) if self._generated else 0

    def display_game(self, axis=True):
        if axis:
            print('   ' + ' '.join(str(i)[-1] for i in range(self._width)))
            print(' +' + '-' * (self._width * 2))
        for y in range(self._height):
            row = str(y)[-1] + '| ' if axis else ""
            for x in range(self._width):
                if self._cleared[y][x]:
                    state = self._field[y][x]
                    row += 'X' if state == -1 else (' ' if state == 0 else str(state))
                else:
                    row += 'F' if self._flagged[y][x] else '-'
                row += ' '
            print(row)

    def play_text(self):
        commands = (
            ({'c', 'clear'}, "(c)lear x y", lambda params: self.clear(int(params[0]), int(params[1])), True),
            ({'f', 'flag'},  "(f)lag x y", lambda params: self.flag(int(params[0]), int(params[1])), True),
            ({'ca', 'clear-around'}, "(c)lear-(a)round x y",
                lambda params: self.clear_around(int(params[0]), int(params[1])), True),
            ({'help'}, "help", lambda params: print("Commands:\n" + '\n'.join(i[1] for i in commands)), False),
            ({'about'}, "about", lambda params: print("Created by SwissAndOr, January 31, 2019."), False),
            ({'exit'}, "exit", lambda params: False, False)
        )

        result = None
        show_field = True
        while True:
            if show_field:
                print("Time: %i | Mines Left: %i" % (self.get_time(), self._mines_left))
                self.display_game()
            com_name, *args = input("Enter command: ").split()
            com_name = com_name.lower()
            for command in commands:
                if com_name in command[0]:
                    result = command[2](args)
                    show_field = command[3]
                    break
            else:
                print("Unknown command '%s'. Try entering 'help'." % com_name)
                show_field = False
            if result is not None:
                break
            print()
        if show_field:
            self.display_game()
        print(("Victory!" if result else "Defeat!") + " Time: " + str(self.get_time()))


if __name__ == '__main__':
    print("SwissSweeper 0.5\n")
    print("Presets         w   h   m")
    print("Beginner     -  9,  9, 10")
    print("Intermediate - 16, 16, 40")
    print("Expert       - 30, 16, 99\n")
    w = input("Width:  ")
    h = input("Height: ")
    m = input("Mines:  ")
    game = Game(int(w), int(h), int(m))
    print()
    game.play_text()
    input("Press ENTER to exit")
