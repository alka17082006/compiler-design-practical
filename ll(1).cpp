
#include <bits/stdc++.h>
using namespace std;

map<char, vector<string>> grammar;
map<char, set<char>> FIRST, FOLLOW;
map<pair<char, char>, string> table;

bool isNT(char c) {
    return grammar.count(c);
}

// Calculate FIRST sets
void findFirst() {
    bool change = true;

    while (change) {
        change = false;

        for (auto p : grammar) {
            char A = p.first;

            for (string rule : p.second) {
                bool nullable = true;

                for (char c : rule) {
                    set<char> current;

                    if (isNT(c))
                        current = FIRST[c];
                    else
                        current.insert(c);

                    for (char x : current) {
                        if (x != '#' && FIRST[A].insert(x).second)
                            change = true;
                    }

                    if (!current.count('#')) {
                        nullable = false;
                        break;
                    }
                }

                if (nullable && FIRST[A].insert('#').second)
                    change = true;
            }
        }
    }
}

// Calculate FOLLOW sets
void findFollow(char start) {
    FOLLOW[start].insert('$');

    bool change = true;

    while (change) {
        change = false;

        for (auto p : grammar) {
            char A = p.first;

            for (string rule : p.second) {
                for (int i = 0; i < rule.size(); i++) {
                    char B = rule[i];

                    if (!isNT(B))
                        continue;

                    bool nullable = true;

                    for (int j = i + 1; j < rule.size(); j++) {
                        char c = rule[j];
                        set<char> current;

                        if (isNT(c))
                            current = FIRST[c];
                        else
                            current.insert(c);

                        for (char x : current) {
                            if (x != '#' && FOLLOW[B].insert(x).second)
                                change = true;
                        }

                        if (!current.count('#')) {
                            nullable = false;
                            break;
                        }
                    }

                    if (nullable) {
                        for (char x : FOLLOW[A]) {
                            if (FOLLOW[B].insert(x).second)
                                change = true;
                        }
                    }
                }
            }
        }
    }
}

// FIRST of a complete production RHS
set<char> firstOfString(string s) {
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

// Construct LL(1) parsing table
bool createTable() {
    for (auto p : grammar) {
        char A = p.first;

        for (string rule : p.second) {
            set<char> first = firstOfString(rule);

            for (char c : first) {
                if (c == '#')
                    continue;

                auto key = make_pair(A, c);

                if (table.count(key) && table[key] != rule)
                    return false;

                table[key] = rule;
            }

            if (first.count('#')) {
                for (char c : FOLLOW[A]) {
                    auto key = make_pair(A, c);

                    if (table.count(key) && table[key] != rule)
                        return false;

                    table[key] = rule;
                }
            }
        }
    }

    return true;
}

// Parse input string
void parseString(char start, string input) {
    stack<char> st;
    st.push('$');
    st.push(start);

    input += '$';
    int i = 0;

    cout << "\nStack\t\tInput\t\tAction\n";

    while (!st.empty()) {
        char top = st.top();
        char current = input[i];

        if (top == '$' && current == '$') {
            cout << "ACCEPTED\n";
            return;
        }

        if (!isNT(top)) {
            if (top == current) {
                st.pop();
                i++;
                cout << "Match " << top << "\n";
            }
            else {
                cout << "REJECTED\n";
                return;
            }
        }
        else {
            auto key = make_pair(top, current);

            if (!table.count(key)) {
                cout << "REJECTED\n";
                return;
            }

            string rule = table[key];
            st.pop();

            if (rule != "#") {
                for (int j = rule.size() - 1; j >= 0; j--)
                    st.push(rule[j]);
            }

            cout << top << " -> " << rule << "\n";
        }
    }

    cout << "REJECTED\n";
}

int main() {
    int n;

    cout << "Enter number of productions: ";
    cin >> n;
    cin.ignore();

    char start;

    cout << "Enter productions (e.g. E -> TQ | #):\n";

    for (int i = 0; i < n; i++) {
        string line;
        getline(cin, line);

        line.erase(remove_if(line.begin(), line.end(),
            ::isspace), line.end());

        char A = line[0];

        if (i == 0)
            start = A;

        string rhs = line.substr(line.find("->") + 2);
        stringstream ss(rhs);
        string rule;

        while (getline(ss, rule, '|'))
            grammar[A].push_back(rule);
    }

    findFirst();
    findFollow(start);

    cout << "\nFIRST SETS:\n";
    for (auto p : grammar) {
        cout << "FIRST(" << p.first << ") = { ";
        for (char c : FIRST[p.first])
            cout << c << " ";
        cout << "}\n";
    }

    cout << "\nFOLLOW SETS:\n";
    for (auto p : grammar) {
        cout << "FOLLOW(" << p.first << ") = { ";
        for (char c : FOLLOW[p.first])
            cout << c << " ";
        cout << "}\n";
    }

    if (!createTable()) {
        cout << "\nGrammar is NOT LL(1). Conflict detected.\n";
        return 0;
    }

    cout << "\nPREDICTIVE PARSING TABLE:\n";

    for (auto p : table) {
        cout << "M[" << p.first.first << ", "
             << p.first.second << "] = "
             << p.first.first << " -> "
             << p.second << "\n";
    }

    string input;
    cout << "\nEnter input string: ";
    cin >> input;

    parseString(start, input);

    return 0;
}
