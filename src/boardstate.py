import numpy as np
from typing import Optional, List
from itertools import product

def check(x, y):
    return 0 <= x < 8 and 0 <= y < 8


def update(board, used):
    for x in range(0, 8):
        for y in range(0, 8):
            if used[x, y]:
                board.board[x, y] = 0


class BoardState:
    def __init__(self, board: np.ndarray, current_player: int = 1):
        self.board: np.ndarray = board
        self.current_player: int = current_player

    def inverted(self) -> 'BoardState':
        return BoardState(board=self.board[::-1, ::-1] * -1, current_player=self.current_player * -1)

    def copy(self) -> 'BoardState':
        return BoardState(self.board.copy(), self.current_player)

    def do_move(self, used, from_x, from_y, to_x, to_y) -> Optional['BoardState']:
        figure = self.board[from_x, from_y]
        can = self.check_can()
        new_used = used.copy()
        if self.current_player * figure <= 0:
            return None, used
        
        if self.board[to_x, to_y] != 0:
            return None, used

        if abs(to_x - from_x) != abs(to_y - from_y):
            return None, used
        
        if abs(figure) == 1:
            if abs(to_x - from_x) > 2:
                return None, used
            elif abs(to_x - from_x) == 1:
                if not can:
                    return None, used
                if to_x - from_x * figure > 0:
                    return None, used
            else:
                center_x = (from_x + to_x) // 2
                center_y = (from_y + to_y) // 2
                if self.board[center_x, center_y] * figure >= 0:
                    return None, used
                elif used[center_x, center_y]:
                    return None, used
                else:
                    new_used[center_x, center_y] = 1
        else:
            count_opposite_color = 0
            cur_x, cur_y = from_x, from_y
            while cur_x != to_x and cur_y != to_y:
                if cur_x > to_x:
                    cur_x -= 1
                else: 
                    cur_x += 1
                    
                if cur_y > to_y:
                    cur_y -= 1
                else: 
                    cur_y += 1
                    
                if cur_x == to_x and cur_y == to_y: break
                
                if self.board[cur_x, cur_y] * figure > 0:
                    return None, used

                if self.board[cur_x, cur_y] * figure < 0:
                    if used[cur_x, cur_y]:
                        return None, used
                    new_used[cur_x, cur_y] = 1
                    count_opposite_color += 1   
              
            if count_opposite_color > 1:
                return None, used
            
            if count_opposite_color == 0 and not can:
                return None, used
        
        used = new_used.copy()
        result = self.copy()
        result.board[to_x, to_y] = result.board[from_x, from_y]
        result.board[from_x, from_y] = 0
        if figure == 1 and to_x == 0 or figure == -1 and to_x == 7:
            result.board[to_x, to_y] *= 2
        return result, used
      
    def try_go_king(self, x, y, current_board, figure, used, dest_x, dest_y, can):
        result = []
        flag = 0
        for i in range(1, 8):
            dx = x + dest_x * i
            dy = y + dest_y * i
            
            if check(dx, dy):
                if figure * current_board.board[dx, dy] == 0:
                    now = current_board.copy()
                    now.board[x, y] = 0
                    now.board[dx, dy] = figure
                    
                    if flag == 0 and can:
                        result += [now]
                        
                    if flag == 1:
                        result += self.move_king(dx, dy, now, figure, used, 0)
                        if len(self.move_king(dx, dy, now, figure, used, 0)) == 0:
                            update(now, used)
                            result += [now]
                elif figure * current_board.board[dx, dy] < 0:
                    if flag == 1 or used[dx, dy]: break
                    flag += 1
                    used[dx, dy] = 1  
                else: break 
        return result
    
    def check_can_king(self, x, y, dest_x, dest_y):
        figure = self.board[x, y]
        flag = 0
        for i in range(1, 8):
            dx = x + dest_x * i
            dy = y + dest_y * i
            if not check(dx, dy):
                return 1
            
            if self.board[dx, dy] == 0:
                if flag != 0:
                    return 0
            elif self.board[dx, dy] * figure < 0:
                if flag == 1:
                    return 1
                flag = 1
            else:
                return 1
        return 1

    def move_king(self, x, y, current_board, figure, used, can):
        result = []
        for i, j in product((-1, 1), (-1, 1)):
            result += self.try_go_king(x, y, current_board, figure, used.copy(), i, j, can)
        return result
        
    def try_go_checker(self, x, y, current_board, figure, used, dest_x, dest_y, can):
        result = []
        flag = 0
        
        for i in range(1, 3):
            dx = x + dest_x * i
            dy = y + dest_y * i
            
            if check(dx, dy):
                if figure * current_board.board[dx, dy] == 0:
                    if (dx - x) * figure > 0 and i == 1: break
                    if flag == 0 and i == 2: break
                    
                    now = current_board.copy()
                    now.board[x, y] = 0
                    now.board[dx, dy] = figure
                    
                    if flag == 0 and can:
                        if (figure < 0 and dx == 7) or (figure > 0 and dx == 0): 
                            now.board[x, y] = 0
                            now.board[dx, dy] = figure * 2
                        result += [now]
                        
                    if flag == 1:
                        if (figure < 0 and dx == 7) or (figure > 0 and dx == 0):
                            now.board[x, y] = 0 
                            now.board[dx, dy] = figure * 2
                            
                            result += self.move_king(dx, dy, now, figure * 2, used, 0)
                            if len(self.move_king(dx, dy, now, figure * 2, used, 0)) == 0:
                                update(now, used)
                                result += [now]
                        else:
                            result += self.move_checker(dx, dy, now, figure, used, 0)
                            if len(self.move_checker(dx, dy, now, figure, used, 0)) == 0:
                                update(now, used)
                                result += [now]                            
                            
                elif figure * current_board.board[dx, dy] < 0:
                    if used[dx, dy] or i == 2: break

                    flag += 1
                    used[dx, dy] = 1  
                else: break
        return result

    def check_can_checker(self, x, y, dest_x, dest_y):
        dx = x + dest_x
        dy = y + dest_y
        figure = self.board[x, y]
        if check(dx + dest_x, dy + dest_y):
            if self.board[dx, dy] * figure < 0 and self.board[dx + dest_x, dy + dest_y] == 0:
                return 0
        return 1
    
    def move_checker(self, x, y, current_board, figure, used, can):
        result = []
        for i, j in product((-1, 1), (-1, 1)):
            result += self.try_go_checker(x, y, current_board, figure, used.copy(), i, j, can)
        return result        
    
    def move(self, x, y, can):
        figure = self.board[x, y]
        if abs(figure) == 2:
            return self.move_king(x, y, self.copy(), self.board[x, y], np.zeros((8, 8)), can)
        else:
            return self.move_checker(x, y, self.copy(), self.board[x, y], np.zeros((8, 8)), can)
    
    def check_can(self):
        can = 1
        
        for x in range(0, 8):
            for y in range(0, 8):
                figure = self.board[x, y]
                if figure * self.current_player > 0:
                    if abs(figure) == 1:
                        for i, j in product((-1, 1), (-1, 1)):
                            can = min(can, self.check_can_checker(x, y, i, j))
                    else:
                        for i, j in product((-1, 1), (-1, 1)):
                            can = min(can, self.check_can_king(x, y, i, j))
        return can

    def get_possible_moves(self) -> List['BoardState']:
        moves = []
        can = self.check_can()
        
        for x in range(0, 8):
            for y in range(0, 8):
                figure = self.board[x, y]                   
                if self.board[x, y] * self.current_player > 0:
                    if abs(figure) == 1:
                        moves += self.move(x, y, can)
                    else:
                        moves += self.move(x, y, can)
                        
        return moves

    @property
    def is_game_finished(self) -> bool:
        return len(self.get_possible_moves()) == 0

    @property
    def get_winner(self) -> Optional[int]:
        ...

    @staticmethod
    def initial_state() -> 'BoardState':
        board = np.zeros(shape=(8, 8), dtype=np.int8)
        for x in range(0, 8):
            for y in range(0, 8):
                if (x + y) % 2 == 1:
                    if x < 3:
                        board[x, y] = -1
                    elif x > 4:
                        board[x, y] = 1
        
        return BoardState(board, 1)
"""
b = np.zeros((8, 8))
b[5, 2] = -1
b[6, 1] = -1
b[3, 4] = 2
a = BoardState(b, 1)
for i in a.get_possible_moves():
    print(i.board)
"""