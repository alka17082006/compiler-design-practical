
#include <bits/stdc++.h>
using namespace std;

vector<pair<char, string>> productions;
set<char> nonTerminals, terminals;

using Item = pair<int, int>;
using State = set<Item>;

vector<State> states;
map<pair<int, char>, int> transitions;

map<pair<int, char>, pair<char, int>> ACTION;
map<pair<int, char>, int> GOTO_TABLE;


// CLOSURE operation
State closure(State items) {
    bool changed = true;

    while (changed) {
        changed = false;

        State current = items;

        for (auto item : current) {
            int p = item.first;
            int dot = item.second;

            string rhs = productions[p].second;

            if (dot < rhs.size()) {
                char symbol = rhs[dot];

                if (nonTerminals.count(symbol)) {
                    for (int i = 0; i < productions.size(); i++) {
                        if (productions[i].first == symbol) {
                            if (items.insert({i, 0}).second)
                                changed = true;
                        }
                    }
                }
            }
        }
    }

    return items;
}


// GOTO operation
State goTo(State items, char symbol) {
    State moved;

    for (auto item : items) {
        int p = item.first;
        int dot = item.second;

        string rhs = productions[p].second;

        if (dot < rhs.size() && rhs[dot] == symbol)
            moved.insert({p, dot + 1});
    }

    if (!moved.empty())
        return closure(moved);

    return {};
}


// Construct canonical collection
void buildStates() {
    State initial;
    initial.insert({0, 0});
    initial = closure(initial);

    states.push_back(initial);

    map<State, int> stateMap;
    stateMap[initial] = 0;

    queue<int> q;
    q.push(0);

    set<char> symbols = nonTerminals;

    symbols.insert(terminals.begin(), terminals.end());

    while (!q.empty()) {
        int i = q.front();
        q.pop();

        for (char symbol : symbols) {
            State next = goTo(states[i], symbol);

            if (next.empty())
                continue;

            if (!stateMap.count(next)) {
                int id = states.size();

                stateMap[next] = id;
                states.push_back(next);
                q.push(id);
            }

            transitions[{i, symbol}] = stateMap[next];
        }
    }
}


// Add ACTION entry and detect conflicts
bool addAction(pair<int, char> key, pair<char, int> value) {
    if (ACTION.count(key) && ACTION[key] != value)
        return false;

    ACTION[key] = value;
    return true;
}


// Construct ACTION and GOTO tables
bool buildTable() {
    for (int i = 0; i < states.size(); i++) {

        for (char symbol : terminals) {
            if (transitions.count({i, symbol})) {
                int j = transitions[{i, symbol}];

                if (!addAction({i, symbol}, {'s', j}))
                    return false;
            }
        }

        for (char symbol : nonTerminals) {
            if (transitions.count({i, symbol})) {
                GOTO_TABLE[{i, symbol}] =
                    transitions[{i, symbol}];
            }
        }

        for (auto item : states[i]) {
            int p = item.first;
            int dot = item.second;

            char lhs = productions[p].first;
            string rhs = productions[p].second;

            if (dot == rhs.size()) {

                if (p == 0) {
                    if (!addAction({i, '$'}, {'a', 0}))
                        return false;
                }
                else {
                    for (char terminal : terminals) {
                        if (!addAction({i, terminal}, {'r', p}))
                            return false;
                    }

                    if (!addAction({i, '$'}, {'r', p}))
                        return false;
                }
            }
        }
    }

    return true;
}


// Display LR(0) items
void displayStates() {
    cout << "\nCANONICAL COLLECTION:\n";

    for (int i = 0; i < states.size(); i++) {
        cout << "\nI" << i << ":\n";

        for (auto item : states[i]) {
            int p = item.first;
            int dot = item.second;

            string rhs = productions[p].second;
            rhs.insert(dot, ".");

            cout << "  " << productions[p].first
                 << " -> " << rhs << "\n";
        }
    }
}


// Display parsing tables
void displayTable() {
    cout << "\nACTION TABLE:\n";

    for (auto p : ACTION) {
        cout << "ACTION[" << p.first.first
             << ", " << p.first.second << "] = ";

        if (p.second.first == 's')
            cout << "SHIFT " << p.second.second;
        else if (p.second.first == 'r')
            cout << "REDUCE " << p.second.second;
        else
            cout << "ACCEPT";

        cout << "\n";
    }

    cout << "\nGOTO TABLE:\n";

    for (auto p : GOTO_TABLE) {
        cout << "GOTO[" << p.first.first
             << ", " << p.first.second
             << "] = " << p.second << "\n";
    }
}


// Parse input string
void parseString(string input) {
    vector<int> st = {0};

    input += '$';
    int i = 0;

    cout << "\nSTACK\t\tINPUT\t\tACTION\n";

    while (true) {
        int state = st.back();
        char symbol = input[i];

        if (!ACTION.count({state, symbol})) {
            cout << "REJECTED\n";
            return;
        }

        auto operation = ACTION[{state, symbol}];

        char type = operation.first;
        int value = operation.second;

        if (type == 's') {
            st.push_back(value);
            i++;

            cout << "SHIFT " << value << "\n";
        }

        else if (type == 'r') {
            char lhs = productions[value].first;
            string rhs = productions[value].second;

            for (int j = 0; j < rhs.size(); j++)
                st.pop_back();

            if (!GOTO_TABLE.count({st.back(), lhs})) {
                cout << "REJECTED\n";
                return;
            }

            st.push_back(GOTO_TABLE[{st.back(), lhs}]);

            cout << "REDUCE " << lhs
                 << " -> " << (rhs.empty() ? "#" : rhs) << "\n";
        }

        else {
            cout << "ACCEPTED\n";
            return;
        }
    }
}


int main() {
    int n;

    cout << "Enter number of productions: ";
    cin >> n;
    cin.ignore();

    char start;

    cout << "Enter productions (e.g. S -> CC):\n";

    for (int i = 0; i < n; i++) {
        string line;
        getline(cin, line);

        line.erase(remove_if(line.begin(), line.end(),
            ::isspace), line.end());

        char lhs = line[0];

        if (i == 0)
            start = lhs;

        nonTerminals.insert(lhs);

        string rhs = line.substr(line.find("->") + 2);
        stringstream ss(rhs);
        string rule;

        while (getline(ss, rule, '|')) {
            if (rule == "#")
                rule = "";

            productions.push_back({lhs, rule});
        }
    }

    // Augmented grammar
    productions.insert(productions.begin(), {'@', string(1, start)});
    nonTerminals.insert('@');

    // Identify terminals
    for (auto p : productions) {
        for (char c : p.second) {
            if (!nonTerminals.count(c))
                terminals.insert(c);
        }
    }

    buildStates();
    displayStates();

    if (!buildTable()) {
        cout << "\nGrammar is NOT LR(0). "
             << "Parsing conflict detected.\n";
        return 0;
    }

    cout << "\nGrammar is LR(0).\n";

    displayTable();

    string input;
    cout << "\nEnter input string: ";
    cin >> input;

    parseString(input);

    return 0;
}
