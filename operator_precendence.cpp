
#include <iostream>
#include <vector>
#include <map>
#include <set>
#include <string>
#include <algorithm>
using namespace std;

struct Production {
    char lhs;
    string rhs;
};

bool isTerminal(char c, set<char>& nonTerminals) {
    return nonTerminals.find(c) == nonTerminals.end();
}

map<char, set<char> > calculateFIRSTVT(
    vector<Production>& productions,
    set<char>& nonTerminals
) {
    map<char, set<char> > firstvt;
    bool changed = true;

    while (changed) {
        changed = false;

        for (int i = 0; i < (int)productions.size(); i++) {
            char lhs = productions[i].lhs;
            string rhs = productions[i].rhs;

            if (rhs.empty()) continue;

            char first = rhs[0];

            if (isTerminal(first, nonTerminals)) {
                if (firstvt[lhs].insert(first).second)
                    changed = true;
            } else {
                if (rhs.size() > 1 &&
                    isTerminal(rhs[1], nonTerminals)) {
                    if (firstvt[lhs].insert(rhs[1]).second)
                        changed = true;
                }

                for (set<char>::iterator it = firstvt[first].begin();
                     it != firstvt[first].end(); ++it) {
                    if (firstvt[lhs].insert(*it).second)
                        changed = true;
                }
            }
        }
    }

    return firstvt;
}

map<char, set<char> > calculateLASTVT(
    vector<Production>& productions,
    set<char>& nonTerminals
) {
    map<char, set<char> > lastvt;
    bool changed = true;

    while (changed) {
        changed = false;

        for (int i = 0; i < (int)productions.size(); i++) {
            char lhs = productions[i].lhs;
            string rhs = productions[i].rhs;

            if (rhs.empty()) continue;

            char last = rhs[rhs.size() - 1];

            if (isTerminal(last, nonTerminals)) {
                if (lastvt[lhs].insert(last).second)
                    changed = true;
            } else {
                if (rhs.size() > 1 &&
                    isTerminal(rhs[rhs.size() - 2], nonTerminals)) {
                    if (lastvt[lhs].insert(rhs[rhs.size() - 2]).second)
                        changed = true;
                }

                for (set<char>::iterator it = lastvt[last].begin();
                     it != lastvt[last].end(); ++it) {
                    if (lastvt[lhs].insert(*it).second)
                        changed = true;
                }
            }
        }
    }

    return lastvt;
}

int main() {
    int n;
    vector<Production> productions;
    set<char> nonTerminals;

    cout << "OPERATOR PRECEDENCE PARSER\n";
    cout << "Enter number of grammar productions: ";
    cin >> n;

    cout << "Enter productions like E=E+T|T\n";

    for (int i = 0; i < n; i++) {
        string line;
        cin >> line;

        line.erase(remove(line.begin(), line.end(), ' '), line.end());

        char lhs = line[0];
        nonTerminals.insert(lhs);

        size_t pos = line.find('=');
        string right = line.substr(pos + 1);

        size_t start = 0;

        while (true) {
            size_t separator = right.find('|', start);

            string rhs = right.substr(start, separator - start);

            Production p;
            p.lhs = lhs;
            p.rhs = rhs;
            productions.push_back(p);

            if (separator == string::npos)
                break;

            start = separator + 1;
        }
    }

    char startSymbol = productions[0].lhs;

    // Check operator grammar restrictions.
    bool valid = true;

    for (int i = 0; i < (int)productions.size(); i++) {
        string rhs = productions[i].rhs;

        if (rhs.find('#') != string::npos)
            valid = false;

        for (int j = 0; j + 1 < (int)rhs.size(); j++) {
            if (nonTerminals.count(rhs[j]) &&
                nonTerminals.count(rhs[j + 1])) {
                valid = false;
            }
        }
    }

    if (!valid) {
        cout << "Invalid operator grammar.\n";
        return 0;
    }

    map<char, set<char> > firstvt =
        calculateFIRSTVT(productions, nonTerminals);

    map<char, set<char> > lastvt =
        calculateLASTVT(productions, nonTerminals);

    cout << "\nFIRSTVT:\n";
    for (set<char>::iterator nt = nonTerminals.begin();
         nt != nonTerminals.end(); ++nt) {
        cout << *nt << " : ";
        for (set<char>::iterator t = firstvt[*nt].begin();
             t != firstvt[*nt].end(); ++t)
            cout << *t << " ";
        cout << "\n";
    }

    cout << "\nLASTVT:\n";
    for (set<char>::iterator nt = nonTerminals.begin();
         nt != nonTerminals.end(); ++nt) {
        cout << *nt << " : ";
        for (set<char>::iterator t = lastvt[*nt].begin();
             t != lastvt[*nt].end(); ++t)
            cout << *t << " ";
        cout << "\n";
    }

    // Construct precedence table.
    map<pair<char, char>, char> table;
    bool conflict = false;

    auto addRelation = [&](char a, char b, char relation) {
        pair<char, char> key = make_pair(a, b);

        if (table.count(key) && table[key] != relation)
            conflict = true;
        else
            table[key] = relation;
    };

    for (int p = 0; p < (int)productions.size(); p++) {
        string rhs = productions[p].rhs;

        for (int i = 0; i + 1 < (int)rhs.size(); i++) {
            char a = rhs[i];
            char b = rhs[i + 1];

            if (isTerminal(a, nonTerminals) &&
                isTerminal(b, nonTerminals)) {
                addRelation(a, b, '=');
            }

            if (isTerminal(a, nonTerminals) &&
                nonTerminals.count(b)) {
                for (set<char>::iterator t = firstvt[b].begin();
                     t != firstvt[b].end(); ++t)
                    addRelation(a, *t, '<');
            }

            if (nonTerminals.count(a) &&
                isTerminal(b, nonTerminals)) {
                for (set<char>::iterator t = lastvt[a].begin();
                     t != lastvt[a].end(); ++t)
                    addRelation(*t, b, '>');
            }

            if (i + 2 < (int)rhs.size() &&
                isTerminal(a, nonTerminals) &&
                nonTerminals.count(b) &&
                isTerminal(rhs[i + 2], nonTerminals)) {
                addRelation(a, rhs[i + 2], '=');
            }
        }
    }

    for (set<char>::iterator t = firstvt[startSymbol].begin();
         t != firstvt[startSymbol].end(); ++t)
        addRelation('$', *t, '<');

    for (set<char>::iterator t = lastvt[startSymbol].begin();
         t != lastvt[startSymbol].end(); ++t)
        addRelation(*t, '$', '>');

    if (conflict) {
        cout << "\nGrammar has precedence conflicts.\n";
        return 0;
    }

    cout << "\nPrecedence Relations:\n";
    for (map<pair<char, char>, char>::iterator it = table.begin();
         it != table.end(); ++it) {
        cout << it->first.first << " "
             << it->second << " "
             << it->first.second << "\n";
    }

    string input;
    cout << "\nEnter input string: ";
    cin >> input;
    input += '$';

    string stack = "$";
    int pos = 0;
    bool accepted = false;

    cout << "\nSTACK\t\tINPUT\t\tACTION\n";

    for (int step = 0; step < 500; step++) {
        string remaining = input.substr(pos);

        if (stack == string("$") + startSymbol &&
            remaining == "$") {
            cout << stack << "\t\t" << remaining
                 << "\t\tACCEPT\n";
            accepted = true;
            break;
        }

        // Find rightmost terminal in stack.
        int topIndex = -1;

        for (int i = (int)stack.size() - 1; i >= 0; i--) {
            if (stack[i] == '$' ||
                !nonTerminals.count(stack[i])) {
                topIndex = i;
                break;
            }
        }

        if (topIndex == -1 || pos >= (int)input.size())
            break;

        char topTerminal = stack[topIndex];
        char nextSymbol = input[pos];

        pair<char, char> key =
            make_pair(topTerminal, nextSymbol);

        if (!table.count(key))
            break;

        char relation = table[key];

        if (relation == '<' || relation == '=') {
            cout << stack << "\t\t" << remaining << "\t\tSHIFT\n";
            stack += nextSymbol;
            pos++;
        }
        else if (relation == '>') {
            // Find the left boundary of the handle.
            int current = topIndex;
            int boundary = -1;

            while (current > 0) {
                int previous = -1;

                for (int i = current - 1; i >= 0; i--) {
                    if (stack[i] == '$' ||
                        !nonTerminals.count(stack[i])) {
                        previous = i;
                        break;
                    }
                }

                if (previous == -1)
                    break;

                pair<char, char> boundaryKey =
                    make_pair(stack[previous], stack[current]);

                if (!table.count(boundaryKey))
                    break;

                char rel = table[boundaryKey];

                if (rel == '<') {
                    boundary = previous;
                    break;
                }

                if (rel != '=' && rel != '>')
                    break;

                current = previous;
            }

            if (boundary == -1)
                break;

            string handle = stack.substr(boundary + 1);
            char matchingLHS = '\0';

            for (int i = 0; i < (int)productions.size(); i++) {
                if (productions[i].rhs == handle) {
                    matchingLHS = productions[i].lhs;
                    break;
                }
            }

            if (matchingLHS == '\0')
                break;

            cout << stack << "\t\t" << remaining
                 << "\t\tREDUCE " << handle
                 << " -> " << matchingLHS << "\n";

            stack = stack.substr(0, boundary + 1) + matchingLHS;
        }
        else {
            break;
        }
    }

    if (!accepted) {
        cout << stack << "\t\t" << input.substr(pos)
             << "\t\tREJECT\n";
        cout << "\nString is REJECTED.\n";
    } else {
        cout << "\nString is ACCEPTED.\n";
    }

    return 0;
}
