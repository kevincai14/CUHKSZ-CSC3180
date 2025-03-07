//
// Created by Quan on 2025/3/7.
//
#include <iostream>
#include <vector>
#include <cctype>
#include <string>
#include <queue>
#include <unordered_set>
#include <cmath>
#include <sstream>
using namespace std;

vector<vector<int>> get_board(string input) {
    vector<vector<int>> board(2, vector<int>());
    int count = 0;
    int row = 0;

    for (char i: input) {
        if (isdigit(i)) {
            if (count == 3) {
                row++;
            }
            board[row].push_back(i - '0');
            count++;
        }
    }
    return board;
}

int manhattan(vector<vector<int>> board) {
    int dist = 0;

    int goal_row[6] = {0, 0, 0, 1, 1, 1};
    int goal_col[6] = {0, 1, 2, 0, 1, 2};

    for (int i = 0; i < 2; i++) {
        for (int j = 0; j < 3; j++) {
            int num = board[i][j];
            if (num != 0) {
                int target_row = goal_row[num - 1];
                int target_col = goal_col[num - 1];

                dist += ((i - target_row) > 0 ? (i - target_row) : (target_row - i))
                        + ((j - target_col) > 0 ? (j - target_col) : (target_col - j));
            }
        }
    }
    return dist;
}



struct State {
    vector<vector<int>> board;
    int zero_row, zero_col;
    int g;
    int h;
    string path;

    bool operator>(State other) const {
        return (g + h) > (other.g + other.h);
    }
};

vector<State> get_neighbors(State s) {
    vector<State> neighbors;
    vector<pair<int, int>> dirs = {{0, -1}, {0, 1}, {-1, 0}, {1, 0}};
    vector<char> dir_names = {'l', 'r', 'u', 'd'};

    for (int i = 0; i < 4; ++i) {
        int new_row = s.zero_row + dirs[i].first;
        int new_col = s.zero_col + dirs[i].second;

        if (new_row >= 0 && new_row < 2 && new_col >= 0 && new_col < 3) {
            State new_state = s;
            swap(new_state.board[s.zero_row][s.zero_col],
                 new_state.board[new_row][new_col]);
            new_state.zero_row = new_row;
            new_state.zero_col = new_col;
            new_state.g += 1;
            new_state.h = manhattan(new_state.board);
            new_state.path += dir_names[i];
            neighbors.push_back(new_state);
        }
    }
    return neighbors;
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
                start.zero_row = i;
                start.zero_col = j;
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

        for (auto neighbor : get_neighbors(current)) {
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
    vector<string> source_v;
    string input;

    while (cin) {
        getline(cin, input);
        source_v.push_back(input);
    }

    vector<vector<int>> board = get_board(source_v[0]);
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
    system("pause");
}