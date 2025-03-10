//
// Created by Quan on 2025/3/7.
//
#include <iostream>
#include <vector>
#include <queue>
#include <unordered_set>
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
                dist += abs(i - goal_board[board[i][j]].first) + abs(j - goal_board[board[i][j]].second);
            }
        }
    }

    return dist;
}

struct State {
    vector<vector<int>> board;
    int empty_x, empty_y;
    int g;
    int h;
    string path;

    bool operator>(State other) const {
        return (g + h) > (other.g + other.h);
    }
};

vector<State> get_next_state(State current_state) {
    vector<State> next_state;
    vector<char> direction = {'l', 'r', 'u', 'd'};
    vector<pair<int, int>> direction_xy = {{0, -1}, {0, 1}, {-1, 0}, {1, 0}};

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
        int new_row = current_state.empty_y + direction_xy[i].first;
        int new_col = current_state.empty_x + direction_xy[i].second;

        if (new_row >= 0 && new_row < 2 && new_col >= 0 && new_col < 3) {
            State new_state = current_state;
            swap(new_state.board[current_state.empty_y][current_state.empty_x],
                 new_state.board[new_row][new_col]);
            new_state.empty_y = new_row;
            new_state.empty_x = new_col;
            new_state.g += 1;
            new_state.h = manhattan(new_state.board);
            new_state.path += direction[i];
            next_state.push_back(new_state);
        }
    }
    return next_state;
}

string solve_puzzle(vector<vector<int>> board) {
    vector<vector<int>> goal = {{1, 2, 3}, {4, 5, 0}};

    priority_queue<State, vector<State>, greater<State>> pq;
    unordered_set<string> visited;

    State start;
    start.board = board;
    start.g = 0;
    start.h = manhattan(board);
    start.path = "";

    for (int i = 0; i < 2; ++i) {
        for (int j = 0; j < 3; ++j) {
            if (board[i][j] == 0) {
                start.empty_y = i;
                start.empty_x = j;
            }
        }
    }

    auto state_to_str = [](vector<vector<int>> board) {
        string s;
        for (auto row : board)
            for (int num : row)
                s += to_string(num);
        return s;
    };

    pq.push(start);
    visited.insert(state_to_str(start.board));

    while (!pq.empty()) {
        State current = pq.top();
        pq.pop();

        if (current.board == goal) {
            return current.path;
        }

        for (auto neighbor : get_next_state(current)) {
            string state_str = state_to_str(neighbor.board);
            if (visited.find(state_str) == visited.end()) {
                visited.insert(state_str);
                pq.push(neighbor);
            }
        }
    }

    return "None";


}

int main() {

    vector<vector<int>> board = get_board();
    string result = solve_puzzle(board);

    if (result == "None")
        cout << -1 << endl;
    else {
        cout << result.length() << endl;
    }
    cout << result;

//    cout << manhattan(board);



//    for (const vector<int>& row: board) {
//        for (int a: row) {
//            cout << a;
//        }
//        cout << endl;
//    }
}