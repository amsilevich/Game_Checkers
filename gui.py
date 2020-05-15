from itertools import product

import numpy as np

import time
import pygame
from pygame import Surface

from src.ai import AI, PositionEvaluation
from src.boardstate import BoardState
from src.boardstate import update


def draw_board(screen: Surface, pos_x: int, pos_y: int, elem_size: int, board: BoardState):
    dark = (0, 0, 0)
    white = (200, 200, 200)
    for y, x in product(range(8), range(8)):
        color = white if (x + y) % 2 == 0 else dark
        position = pos_x + x * elem_size, pos_y + y * elem_size, elem_size, elem_size
        pygame.draw.rect(screen, color, position)

        figure = board.board[y, x]

        if figure == 0:
            continue

        if figure > 0:
            figure_color = 255, 255, 255
        else:
            figure_color = 100, 100, 100
        r = elem_size // 2 - 10

        pygame.draw.circle(screen, figure_color, (position[0] + elem_size // 2, position[1] + elem_size // 2), r)
        if abs(figure) == 2:
            r = 5
            negative_color = [255 - e for e in figure_color]
            pygame.draw.circle(screen, negative_color, (position[0] + elem_size // 2, position[1] + elem_size // 2), r)


def is_equal(first_board, second_board):
    if first_board.current_player != second_board.current_player:
        return 0
    for x in range(0, 8):
        for y in range(0, 8):
            if first_board.board[x, y] != second_board.board[x, y]:
                return 0
    return 1


def find(board, boards):
    for i in boards:
        if is_equal(board, i):
            return 1
    return 0


def write(moves):
    print("----------------------------")
    print()
    for i in moves:
        print(i.board)
        print()
    print("----------------------------")


def write_pygame(output_text, color):
    fontObj = pygame.font.Font('freesansbold.ttf', 75)
    textSurfaceObj = fontObj.render(output_text, True, color, (170, 170, 170))
    textRectObj = textSurfaceObj.get_rect()
    textRectObj.center = (256, 256)
    screen.blit(textSurfaceObj, textRectObj)
    pygame.display.flip()


def save_in_file(board, s):
    buffer = open(s, 'w')
    for x in range(0, 8):
        for y in range(0, 8):
            buffer.write(str(board.board[x, y]) + '\n')
    buffer.close()


def load_from_file(board, s):
    buffer = open(s, 'r')
    buffer_to_str = buffer.read()
    data = np.array(buffer_to_str.split('\n'))
    for ind in range(0, 64):
        board.board[ind // 8, ind % 8] = data[ind]
    buffer.close()


def upd_arr(first, second):
    for i in range(0, 8):
        for j in range(0, 8):
            first[i, j] = second[i, j]


def lose_case(screen, grid_size, board):
    draw_board(screen, 0, 0, grid_size, board)
    pygame.display.flip()
    time.sleep(0.5)
    write_pygame("You lose!", (128, 0, 0))


def win_case():
    time.sleep(0.5)
    write_pygame("You won!", (255, 255, 0))


def try_move(screen, board, moves,  used, old_y, old_x, new_y, new_x, grid_size):
    new_board, n_used = board.do_move(used, old_y, old_x, new_y, new_x)
    upd_arr(used, n_used)
    if new_board is None:
        return 1
    upd_arr(board.board, new_board.board)
    changed_board = board.copy()
    update(changed_board, used)
    if not find(changed_board, moves):
        return 1
    update(board, used)
    draw_board(screen, 0, 0, grid_size, board)
    pygame.display.flip()
    upd_arr(used, np.zeros((8, 8)))
    board.current_player *= -1
    if ai.next_move(board) is None:
        win_case()
        return 0
    upd_arr(board.board, ai.next_move(board).board)
    board.current_player *= -1
    if len(board.get_possible_moves()) == 0:
        lose_case(screen, grid_size, board)
        return 0
    return 2


def game_loop(screen: Surface, board: BoardState, ai: AI):
    grid_size = screen.get_size()[0] // 8
    used = np.zeros((8, 8))
    moves = board.get_possible_moves()
    god_mode = 0
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_click_position = event.pos

            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                new_x, new_y = [p // grid_size for p in event.pos]
                old_x, old_y = [p // grid_size for p in mouse_click_position]
                try_res = try_move(screen, board, moves, used, old_y, old_x, new_y, new_x, grid_size)
                if try_res == 2:
                    moves = board.get_possible_moves()
                    write(moves)
                elif not try_res:
                    return

            if event.type == pygame.MOUSEBUTTONUP and event.button == 3:
                if not god_mode:
                    continue
                x, y = [p // grid_size for p in event.pos]
                used = np.zeros((8, 8))
                board.current_player = 1
                board.board[y, x] = int((board.board[y, x] + 1 + 2) % 5 - 2)  # change figure
                moves = board.get_possible_moves()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    board = board.inverted()

                if event.key == pygame.K_g:
                    god_mode = 1 - god_mode
                    if god_mode:
                        board.board = np.zeros((8, 8))
                    else:
                        board = board.initial_state()

                if event.key == pygame.K_s:
                    save_in_file(board, "buffer.txt")

                if event.key == pygame.K_l:
                    load_from_file(board, "buffer.txt")
                    moves = board.get_possible_moves()
                    used = np.zeros((8, 8))

            draw_board(screen, 0, 0, grid_size, board)
            pygame.display.flip()
    save_in_file(board.initial_state(), "buffer.txt")


pygame.init()

screen: Surface = pygame.display.set_mode([512, 512])
ai = AI(PositionEvaluation(), search_depth=3)

game_loop(screen, BoardState.initial_state(), ai)

pygame.quit()