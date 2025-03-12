import heapq


def get_board():
    s = input().strip()
    digits = [int(ch) for ch in s if ch.isdigit()]
    return [digits[:3], digits[3:6]]


def manhattan(board):
    dist = 0
    goal_board = [(0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (1, 2)]
    for i in range(2):
        for j in range(3):
            if board[i][j] != 0:
                tile = board[i][j]
                goal_y, goal_x = goal_board[tile - 1]
                dist += abs(i - goal_y) + abs(j - goal_x)
    return dist


class State:
    def __init__(self, board, g, h, path):
        self.board = board
        self.g = g
        self.h = h
        self.path = path


def get_priority(move):
    mapping = {'l': 'a', 'u': 'b', 'r': 'c', 'd': 'd'}
    return mapping[move]


def get_next_state(current_state):
    next_states = []
    directions = ['l', 'u', 'r', 'd']
    direction_xy = [(0, -1), (-1, 0), (0, 1), (1, 0)]

    empty_x = empty_y = None
    for i in range(2):
        for j in range(3):
            if current_state.board[i][j] == 0:
                empty_x, empty_y = j, i
                break
        if empty_x is not None:
            break

    for d, (dy, dx) in zip(directions, direction_xy):
        new_x = empty_x + dx
        new_y = empty_y + dy
        if 0 <= new_y < 2 and 0 <= new_x < 3:
            new_board = [row[:] for row in current_state.board]
            new_board[empty_y][empty_x] = new_board[new_y][new_x]
            new_board[new_y][new_x] = 0
            new_g = current_state.g + 1
            new_h = manhattan(new_board)
            new_path = current_state.path + d
            next_states.append(State(new_board, new_g, new_h, new_path))
    return next_states


def board_to_str(board):
    return ''.join(str(num) for row in board for num in row)


def solve_puzzle(board):
    goal = [[1, 2, 3], [4, 5, 0]]
    pq = []
    visited = {}

    start = State(board, 0, manhattan(board), "")
    start_priority = (start.g + start.h, ''.join(get_priority(m) for m in start.path))
    heapq.heappush(pq, (start_priority, start))
    visited[board_to_str(start.board)] = start.g + start.h

    while pq:
        current_priority, current = heapq.heappop(pq)
        if current.board == goal:
            return current.path
        for neighbor in get_next_state(current):
            state_str = board_to_str(neighbor.board)
            f = neighbor.g + neighbor.h
            if state_str not in visited or visited[state_str] > f:
                visited[state_str] = f
                neighbor_priority = (f, ''.join(get_priority(m) for m in neighbor.path))
                heapq.heappush(pq, (neighbor_priority, neighbor))
    return "None"


def main():
    board = get_board()
    moving = solve_puzzle(board)
    steps = -1 if moving == "None" else len(moving)
    print(steps)
    print(moving)


if __name__ == '__main__':
    main()
