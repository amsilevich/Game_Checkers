from typing import Optional

from .boardstate import BoardState


def sign(x):
    if (x == 0):
        return 0
    return 1 if (x > 0) else -1

class PositionEvaluation:
    def __call__(self, board: BoardState) -> float:
        cnt = 0
        for x in range(0, 8):
            for y in range(0, 8):
                figure = board.board[x, y]
                delta = 0
                if figure * board.current_player > 0:
                    delta = (abs(figure) if (abs(figure) == 2) else x * 0.05 + 0.7)
                elif figure * board.current_player < 0:
                    delta = (abs(figure) if (abs(figure) == 2) else (0.3 - x * 0.05) + 0.7)
                cnt += delta * sign(figure * board.current_player)
        #todo
        if figure < 0:
            cnt *= -1
        return cnt

class AI:
    def __init__(self, position_evaluation: PositionEvaluation, search_depth: int):
        self.position_evaluation: PositionEvaluation = position_evaluation
        self.depth: int = search_depth

    def base(self, board: BoardState):
        if board.is_game_finished == 1:
            return None
        moves = board.get_possible_moves()
        best_move = moves[0]
        for move in moves:
            if self.position_evaluation(move) * board.current_player > self.position_evaluation(move) * board.current_player:
                best_move = move
        return best_move

    def get_opponent_move(self, board: BoardState, depth):
        new_board = board.copy()
        new_board.current_player *= -1
        if depth == 1:
            return self.base(new_board)
        return self.choose_move(new_board, depth - 1)

    def choose_move(self, board: BoardState, depth):
        if depth == 1:
            return self.base(board)
        moves = board.get_possible_moves()
        if len(moves) == 0:
            return None
        best_move = moves[0]
        if self.get_opponent_move(moves[0], depth - 1) is None:
            return best_move
        best_future_eval = self.position_evaluation(self.get_opponent_move(moves[0], depth - 1)) * board.current_player

        for move in moves:
            if self.get_opponent_move(move, depth - 1) is None:
                return move
            future_eval = self.position_evaluation(self.get_opponent_move(move, depth - 1)) * board.current_player
            if future_eval > best_future_eval:
                best_future_eval = future_eval
                best_move = move

        return best_move


    def next_move(self, board: BoardState) -> Optional[BoardState]:
        moves = board.get_possible_moves()
        if len(moves) == 0:
            return None

        # todo better implementation
        move = self.choose_move(board, self.depth)
        print(self.position_evaluation(move))
        return move