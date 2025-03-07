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
using namespace std;

vector<vector<int>> get_board(const string& input) {
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

int main() {
    string input;
    cin >> input;

    vector<vector<int>> board = get_board(input);
    int result = 2;
    cout << result;





//    for (const vector<int>& row: board) {
//        for (int a: row) {
//            cout << a;
//        }
//        cout << endl;
//    }

}