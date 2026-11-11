
#include <bits/stdc++.h>
using namespace std;

vector<pair<char, string>> productions;
map<char, vector<string>> grammar;

set<char> nonTerminals, terminals;
map<char, set<char>> FIRST;

using Item = tuple<int, int, char>;
using State = set<Item>;

vector<State> states;

map<pair<int, char>, int> transitions;
map<pair<int, char>, pair<char, int>> ACTION;
map<pair<int, char>, int> GOTO_TABLE;


bool isNT(char c) {
    return nonTerminals.count(c);
}


// FIRST of a sequence
set<char> firstSequence(string s) {
    set<char> result;
    bool nullable = true;

    for (char c : s) {
        set<char> current;

        if (isNT(c))
            current = FIRST[c];
        else
            current.insert(c);

        for (char x : current)
            if (x != '#')
                result.insert(x);

        if (!current.count('#')) {
            nullable = false;
            break;
        }
    }

    if (nullable)
        result.insert('#');

    return result;
}


// Calculate FIRST sets
void findFirst() {
    bool change = true;

    while (change) {
        change = false;

        for (auto p : grammar) {
            char A = p.first;

            for (string rhs : p.second) {
                set<char> current = firstSequence(rhs);

                for (char c : current) {
                    if (FIRST[A].insert(c).second)
                        change = true;
                }
            }
        }
    }
}


// CLR(1) CLOSURE
State closure(State items) {
    bool change = true;

    while (change) {
        change = false;

        State current = items;

        for (auto item : current) {
            int p, dot;
            char lookahead;

            tie(p, dot, lookahead) = item;

            string rhs = productions[p].second;

            if (dot < rhs.size()) {
                char B = rhs[dot];

                if (isNT(B)) {

                    // beta followed by lookahead
                    string beta = rhs.substr(dot + 1);
                    beta += lookahead;

                    set<char> lookaheads = firstSequence(beta);

                    lookaheads.erase('#');

                    for (int i = 0; i < productions.size(); i++) {
                        if (productions[i].first == B) {

                            for (char a : lookaheads) {
                                Item newItem = {i, 0, a};

                                if (items.insert(newItem).second)
                                    change = true;
                            }
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
        int p, dot;
        char lookahead;

        tie(p, dot, lookahead) = item;

        string rhs = productions[p].second;

        if (dot < rhs.size() && rhs[dot] == symbol) {
            moved.insert({p, dot + 1, lookahead});
        }
    }

    if (!moved.empty())
        return closure(moved);

    return {};
}


// Build canonical LR(1) states
void buildStates() {
    State initial;
    initial.insert({0, 0, '$'});

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


// Construct CLR(1) parsing table
bool buildTable() {
    for (int i = 0; i < states.size(); i++) {

        // SHIFT entries
        for (char c : terminals) {
            if (transitions.count({i, c})) {
                int j = transitions[{i, c}];

                if (!addAction({i, c}, {'s', j}))
                    return false;
            }
        }

        // GOTO entries
        for (char c : nonTerminals) {
            if (transitions.count({i, c})) {
                GOTO_TABLE[{i, c}] = transitions[{i, c}];
            }
        }

        // REDUCE and ACCEPT entries
        for (auto item : states[i]) {
            int p, dot;
            char lookahead;

            tie(p, dot, lookahead) = item;

            char lhs = productions[p].first;
            string rhs = productions[p].second;

            if (dot == rhs.size()) {

                if (p == 0) {
                    if (!addAction({i, '$'}, {'a', 0}))
                        return false;
                }
                else {
                    if (!addAction({i, lookahead}, {'r', p}))
                        return false;
                }
            }
        }
    }

    return true;
}


// Display CLR(1) item sets
void displayStates() {
    cout << "\nCANONICAL LR(1) ITEM COLLECTION:\n";

    for (int i = 0; i < states.size(); i++) {
        cout << "\nI" << i << ":\n";

        for (auto item : states[i]) {
            int p, dot;
            char lookahead;

            tie(p, dot, lookahead) = item;

            string rhs = productions[p].second;
            rhs.insert(dot, ".");

            cout << "  [" << productions[p].first
                 << " -> " << rhs
                 << ", " << lookahead << "]\n";
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

        auto op = ACTION[{state, symbol}];

        char type = op.first;
        int value = op.second;

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

            cout << "REDUCE " << lhs << " -> "
                 << (rhs.empty() ? "#" : rhs) << "\n";
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

    cout << "Enter productions (example: S -> CC):\n";

    for (int i = 0; i < n; i++) {
        string line;
        getline(cin, line);

        line.erase(remove_if(line.begin(), line.end(),
            [](unsigned char c) { return isspace(c); }),
            line.end());

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

            grammar[lhs].push_back(rule);
            productions.push_back({lhs, rule});
        }
    }

    // Augmented grammar
    productions.insert(
        productions.begin(), {'@', string(1, start)}
    );

    nonTerminals.insert('@');

    // Identify terminals
    for (auto p : productions) {
        for (char c : p.second) {
            if (!isNT(c))
                terminals.insert(c);
        }
    }

    findFirst();

    cout << "\nFIRST SETS:\n";

    for (auto p : grammar) {
        cout << "FIRST(" << p.first << ") = { ";

        for (char c : FIRST[p.first])
            cout << c << " ";

        cout << "}\n";
    }

    buildStates();
    displayStates();

    if (!buildTable()) {
        cout << "\nGrammar is NOT CLR(1): conflict detected.\n";
        return 0;
    }

    cout << "\nGrammar is CLR(1).\n";

    displayTable();

    string input;
    cout << "\nEnter input string: ";
    cin >> input;

    parseString(input);

    return 0;
}
