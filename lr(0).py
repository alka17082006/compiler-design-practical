from collections import defaultdict, deque

grammar = {}
productions = []
non_terminals = set()
terminals = set()

states = []
transitions = {}
action = {}
goto_table = {}


def closure(items):
    items = set(items)

    changed = True
    while changed:
        changed = False

        for p, dot in list(items):
            lhs, rhs = productions[p]

            if dot < len(rhs):
                symbol = rhs[dot]

                if symbol in non_terminals:
                    for i, (A, beta) in enumerate(productions):
                        if A == symbol and (i, 0) not in items:
                            items.add((i, 0))
                            changed = True

    return frozenset(items)


def goto(items, symbol):
    moved = set()

    for p, dot in items:
        lhs, rhs = productions[p]

        if dot < len(rhs) and rhs[dot] == symbol:
            moved.add((p, dot + 1))

    if moved:
        return closure(moved)

    return frozenset()


def build_states():
    initial = closure({(0, 0)})

    states.append(initial)
    state_map = {initial: 0}

    queue = deque([0])

    symbols = sorted(non_terminals | terminals)

    while queue:
        i = queue.popleft()

        for symbol in symbols:
            next_state = goto(states[i], symbol)

            if not next_state:
                continue

            if next_state not in state_map:
                state_map[next_state] = len(states)
                states.append(next_state)
                queue.append(state_map[next_state])

            transitions[(i, symbol)] = state_map[next_state]


def add_action(key, value):
    if key in action and action[key] != value:
        return False

    action[key] = value
    return True


def build_table():
    for i, items in enumerate(states):

        # SHIFT and GOTO entries
        for symbol in non_terminals | terminals:
            if (i, symbol) in transitions:
                j = transitions[(i, symbol)]

                if symbol in terminals:
                    if not add_action((i, symbol), ("s", j)):
                        return False
                else:
                    goto_table[(i, symbol)] = j

        # REDUCE and ACCEPT entries
        for p, dot in items:
            lhs, rhs = productions[p]

            if dot == len(rhs):

                if p == 0:
                    if not add_action((i, "$"), ("acc", 0)):
                        return False

                else:
                    for terminal in terminals | {"$"}:
                        if not add_action((i, terminal), ("r", p)):
                            return False

    return True


def display_states():
    print("\nCANONICAL COLLECTION OF LR(0) ITEMS")

    for i, items in enumerate(states):
        print(f"\nI{i}:")

        for p, dot in sorted(items):
            lhs, rhs = productions[p]
            rule = rhs[:dot] + "." + rhs[dot:]
            print(f"  {lhs} -> {rule}")


def display_table():
    print("\nACTION TABLE")

    for (state, symbol), value in sorted(action.items()):
        print(f"ACTION[{state}, {symbol}] = {value}")

    print("\nGOTO TABLE")

    for (state, symbol), value in sorted(goto_table.items()):
        print(f"GOTO[{state}, {symbol}] = {value}")


def parse_string(text):
    stack = [0]
    text += "$"
    index = 0

    print("\nSTACK\t\tINPUT\t\tACTION")

    while True:
        state = stack[-1]
        symbol = text[index]

        operation = action.get((state, symbol))

        if operation is None:
            print("REJECTED")
            return

        kind, value = operation

        if kind == "s":
            stack.extend([symbol, value])
            index += 1
            description = f"SHIFT {value}"

        elif kind == "r":
            lhs, rhs = productions[value]

            if rhs:
                for _ in range(2 * len(rhs)):
                    stack.pop()

            next_state = goto_table.get((stack[-1], lhs))

            if next_state is None:
                print("REJECTED")
                return

            stack.extend([lhs, next_state])
            description = f"REDUCE {lhs} -> {rhs}"

        else:
            print("ACCEPTED")
            return

        print(stack, "\t", text[index:], "\t", description)


def main():
    n = int(input("Enter number of productions: "))

    print("Enter productions (example: S -> CC):")

    start = None

    for _ in range(n):
        line = input().replace(" ", "")
        lhs, rhs = line.split("->")

        if start is None:
            start = lhs

        non_terminals.add(lhs)

        for rule in rhs.split("|"):
            grammar.setdefault(lhs, []).append("" if rule == "#" else rule)

    for lhs, rules in grammar.items():
        for rhs in rules:
            productions.append((lhs, rhs))

    # Add augmented production
    productions.insert(0, ("@", start))
    non_terminals.add("@")

    for lhs, rhs in productions:
        for symbol in rhs:
            if symbol not in non_terminals:
                terminals.add(symbol)

    build_states()

    display_states()

    if not build_table():
        print("\nGrammar is NOT LR(0): parsing conflict detected.")
        return

    print("\nGrammar is LR(0).")
    display_table()

    text = input("\nEnter input string: ")
    parse_string(text)


if __name__ == "__main__":
    main()
