
#include <iostream>
#include <vector>
#include <map>
#include <set>
#include <string>
#include <sstream>
#include <algorithm>
using namespace std;

map<char, vector<string>> productions;
map<char, set<char>> firstSet, followSet;

bool isNonTerminal(char symbol) {
    return productions.find(symbol) != productions.end();
}

// Calculate FIRST sets
void calculateFirst() {
    bool changed = true;

    while (changed) {
        changed = false;

        for (auto &entry : productions) {
            char nt = entry.first;

            for (string rule : entry.second) {
                bool nullable = true;

                for (char symbol : rule) {
                    set<char> currentFirst;

                    if (isNonTerminal(symbol))
                        currentFirst = firstSet[symbol];
                    else
                        currentFirst.insert(symbol);

                    int before = firstSet[nt].size();

                    for (char c : currentFirst) {
                        if (c != '#')
                            firstSet[nt].insert(c);
                    }

                    if (firstSet[nt].size() != before)
                        changed = true;

                    if (currentFirst.find('#') == currentFirst.end()) {
                        nullable = false;
                        break;
                    }
                }

                if (nullable && firstSet[nt].insert('#').second)
                    changed = true;
            }
        }
    }
}

// Calculate FOLLOW sets
void calculateFollow(char startSymbol) {
    followSet[startSymbol].insert('$');

    bool changed = true;

    while (changed) {
        changed = false;

        for (auto &entry : productions) {
            char nt = entry.first;

            for (string rule : entry.second) {
                for (int i = 0; i < (int)rule.size(); i++) {
                    char symbol = rule[i];

                    if (!isNonTerminal(symbol))
                        continue;

                    set<char> firstRemaining;
                    bool nullable = true;

                    for (int j = i + 1; j < (int)rule.size(); j++) {
                        char next = rule[j];

                        set<char> currentFirst;

                        if (isNonTerminal(next))
                            currentFirst = firstSet[next];
                        else
                            currentFirst.insert(next);

                        for (char c : currentFirst) {
                            if (c != '#')
                                firstRemaining.insert(c);
                        }

                        if (currentFirst.find('#') == currentFirst.end()) {
                            nullable = false;
                            break;
                        }
                    }

                    int before = followSet[symbol].size();

                    followSet[symbol].insert(
                        firstRemaining.begin(),
                        firstRemaining.end()
                    );

                    if (nullable) {
                        followSet[symbol].insert(
                            followSet[nt].begin(),
                            followSet[nt].end()
                        );
                    }

                    if (followSet[symbol].size() != before)
                        changed = true;
                }
            }
        }
    }
}

int main() {
    int n;
    cout << "Enter number of productions: ";
    cin >> n;

    cout << "Enter productions (example: E -> TQ | #)\n";

    cin.ignore();

    for (int i = 0; i < n; i++) {
        string line;
        getline(cin, line);

        line.erase(
            remove_if(line.begin(), line.end(), ::isspace),
            line.end()
        );

        char nt = line[0];
        string rhs = line.substr(line.find("->") + 2);

        stringstream ss(rhs);
        string rule;

        while (getline(ss, rule, '|')) {
            productions[nt].push_back(rule);
        }
    }

    char startSymbol = productions.begin()->first;

    calculateFirst();
    calculateFollow(startSymbol);

    cout << "\nFIRST SETS\n";

    for (auto &entry : productions) {
        cout << "FIRST(" << entry.first << ") = { ";

        for (char c : firstSet[entry.first])
            cout << c << " ";

        cout << "}\n";
    }

    cout << "\nFOLLOW SETS\n";

    for (auto &entry : productions) {
        cout << "FOLLOW(" << entry.first << ") = { ";

        for (char c : followSet[entry.first])
            cout << c << " ";

        cout << "}\n";
    }

    return 0;
}
