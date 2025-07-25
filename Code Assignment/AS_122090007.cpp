//
// Created by Quan on 2025/3/7.
//
#include <iostream>
#include <vector>
#include <queue>
#include <unordered_map>
using namespace std;

vector<vector<int>> get_board() {
    string input;
    getline(cin, input);

    vector<vector<int>> board(2, vector<int>());
    int column = 0;
    int row = 0;

    for (char i: input) {
        if (isdigit(i)) {
            if (column == 3) {
                row++;
            }
            board[row].push_back(i - '0');
            column++;
        }
    }
    return board;
}

int manhattan(vector<vector<int>> board) {
    int dist = 0;
    vector<pair<int, int>> goal_board = {{0, 0}, {0, 1}, {0, 2}, {1, 0}, {1, 1}, {1, 2}};

    for (int i = 0; i < 2; i++) {
        for (int j = 0; j < 3; j++) {
            if (board[i][j] != 0) {
                dist += abs(i - goal_board[board[i][j] - 1].first) + abs(j - goal_board[board[i][j] - 1].second);
            }
        }
    }

    return dist;
}

struct State {
    vector<vector<int>> board;
    double g;
    double h;
    vector<char> path;
    int timestamp;

    char get_priority(char i) const {
        if (!path.empty()) {
            switch (i) {
                case 'l':
                    return 'a';
                case 'u':
                    return 'b';
                case 'r':
                    return 'c';
                case 'd':
                    return 'd';
            }
        }
    }

    bool operator<(const State& other_state) const {
        if (g + h == other_state.g + other_state.h) {
            if (timestamp == other_state.timestamp) {
                string path1, path2;
                for (auto i: path) {
                    path1 += get_priority(i);
                }
                for (auto i: other_state.path) {
                    path2 += get_priority(i);
                }
                return path1 > path2;
            } else {
                return timestamp > other_state.timestamp;
            }
        } else {
            return (g + h) > (other_state.g + other_state.h);
        }
    }
};

vector<State> get_next_state(State current_state) {
    vector<State> next_state;
    vector<char> direction = {'l', 'u', 'r', 'd'};
    vector<pair<int, int>> direction_xy = {{0, -1}, {-1, 0}, {0, 1}, {1, 0}};

    int empty_x, empty_y;

    for (int i = 0; i < 2; i++) {
        for (int j = 0; j < 3; j++) {
            if (current_state.board[i][j] == 0) {
                empty_x = j;
                empty_y = i;
                break;
            }
        }
    }

    for (int i = 0; i < 4; i++) {
        int new_x = empty_x + direction_xy[i].second;
        int new_y = empty_y + direction_xy[i].first;

        if (new_y >= 0 and new_y <= 1 and new_x >= 0 and new_x <= 2) {
            State new_state = current_state;
            new_state.board[empty_y][empty_x] = new_state.board[new_y][new_x];
            new_state.board[new_y][new_x] = 0;
            new_state.g += 1;
            new_state.h = manhattan(new_state.board);
            new_state.path.push_back(direction[i]);
            next_state.push_back(new_state);
        }
    }
    return next_state;
}

string board_to_str(vector<vector<int>> board) {
    string s;
    for (auto row : board) {
        for (int num : row) {
            s += to_string(num);
        }
    }
    return s;
}

string solve_puzzle(vector<vector<int>> board) {
    vector<vector<int>> goal = { {1, 2, 3}, {4, 5, 0} };

    priority_queue<State> pq;
    unordered_map<string, double> visited;
    int timestamp_counter = 0;

    State start;
    start.board = board;
    start.g = 0;
    start.h = manhattan(board);
    start.path = vector<char>();
    start.timestamp = timestamp_counter++;
    pq.push(start);
    visited[board_to_str(start.board)] = start.g;

    while (!pq.empty()) {
        State current = pq.top();
        pq.pop();

        if (current.board == goal) {
            return string(current.path.begin(), current.path.end());
        }

        vector<State> neighbors = get_next_state(current);
        for (State& neighbor : neighbors) {
            string state_str = board_to_str(neighbor.board);
            if (visited.find(state_str) == visited.end() || neighbor.g < visited[state_str]) {
                visited[state_str] = neighbor.g;
                neighbor.timestamp = timestamp_counter++;
                pq.push(neighbor);
            }
        }
    }

    return "None";
}

int main() {
    vector<vector<int>> board = get_board();
    string moving = solve_puzzle(board);
    int steps;

    if (moving == "None")
        steps = -1;
    else {
        steps = moving.length();
    }

    cout << steps << endl;
    cout << moving << endl;
}