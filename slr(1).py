from collections import defaultdict, deque

grammar = {}
productions = []
non_terminals = set()
terminals = set()

FIRST = defaultdict(set)
FOLLOW = defaultdict(set)

states = []
transitions = {}
ACTION = {}
GOTO = {}


def is_nt(c):
    return c in non_terminals


# Calculate FIRST sets
def find_first():
    changed = True

    while changed:
        changed = False

        for A, rules in grammar.items():
            for rule in rules:
                nullable = True

                for c in rule:
                    current = FIRST[c] if is_nt(c) else {c}

                    before = len(FIRST[A])
                    FIRST[A].update(current - {"#"})

                    if len(FIRST[A]) != before:
                        changed = True

                    if "#" not in current:
                        nullable = False
                        break

                if nullable and "#" not in FIRST[A]:
                    FIRST[A].add("#")
                    changed = True


# Calculate FOLLOW sets
def find_follow(start):
    FOLLOW[start].add("$")

    changed = True

    while changed:
        changed = False

        for A, rules in grammar.items():
            for rule in rules:
                for i, B in enumerate(rule):
                    if not is_nt(B):
                        continue

                    nullable = True

                    for c in rule[i + 1 :]:
                        current = FIRST[c] if is_nt(c) else {c}

                        before = len(FOLLOW[B])
                        FOLLOW[B].update(current - {"#"})

                        if len(FOLLOW[B]) != before:
                            changed = True

                        if "#" not in current:
                            nullable = False
                            break

                    if nullable:
                        before = len(FOLLOW[B])
                        FOLLOW[B].update(FOLLOW[A])

                        if len(FOLLOW[B]) != before:
                            changed = True


# CLOSURE operation
def closure(items):
    items = set(items)

    changed = True

    while changed:
        changed = False

        for p, dot in list(items):
            lhs, rhs = productions[p]

            if dot < len(rhs):
                symbol = rhs[dot]

                if is_nt(symbol):
                    for i, (A, beta) in enumerate(productions):
                        if A == symbol and (i, 0) not in items:
                            items.add((i, 0))
                            changed = True

    return frozenset(items)


# GOTO operation
def go_to(items, symbol):
    moved = set()

    for p, dot in items:
        lhs, rhs = productions[p]

        if dot < len(rhs) and rhs[dot] == symbol:
            moved.add((p, dot + 1))

    return closure(moved) if moved else frozenset()


# Build canonical LR(0) states
def build_states():
    initial = closure({(0, 0)})

    states.append(initial)
    state_map = {initial: 0}

    queue = deque([0])

    while queue:
        i = queue.popleft()

        for symbol in sorted(non_terminals | terminals):
            next_state = go_to(states[i], symbol)

            if not next_state:
                continue

            if next_state not in state_map:
                state_map[next_state] = len(states)
                states.append(next_state)
                queue.append(state_map[next_state])

            transitions[(i, symbol)] = state_map[next_state]


# Insert ACTION entry and detect conflicts
def add_action(key, value):
    if key in ACTION and ACTION[key] != value:
        return False

    ACTION[key] = value
    return True


# Construct SLR parsing table
def build_table():
    for i, items in enumerate(states):

        for symbol in terminals:
            if (i, symbol) in transitions:
                j = transitions[(i, symbol)]

                if not add_action((i, symbol), ("s", j)):
                    return False

        for symbol in non_terminals:
            if (i, symbol) in transitions:
                GOTO[(i, symbol)] = transitions[(i, symbol)]

        for p, dot in items:
            lhs, rhs = productions[p]

            if dot == len(rhs):

                if p == 0:
                    if not add_action((i, "$"), ("acc", 0)):
                        return False

                else:
                    for terminal in FOLLOW[lhs]:
                        if not add_action((i, terminal), ("r", p)):
                            return False

    return True


# Display LR(0) item sets
def display_states():
    print("\nCANONICAL COLLECTION:")

    for i, items in enumerate(states):
        print(f"\nI{i}:")

        for p, dot in sorted(items):
            lhs, rhs = productions[p]
            print(f"  {lhs} -> {rhs[:dot]}.{rhs[dot:]}")


# Display parsing tables
def display_table():
    print("\nACTION TABLE:")

    for key, value in sorted(ACTION.items()):
        print(f"ACTION[{key[0]}, {key[1]}] = {value}")

    print("\nGOTO TABLE:")

    for key, value in sorted(GOTO.items()):
        print(f"GOTO[{key[0]}, {key[1]}] = {value}")


# Parse input string
def parse_string(text):
    stack = [0]
    text += "$"
    index = 0

    print("\nSTACK\t\tINPUT\t\tACTION")

    while True:
        state = stack[-1]
        symbol = text[index]

        operation = ACTION.get((state, symbol))

        if operation is None:
            print("REJECTED")
            return

        kind, value = operation

        if kind == "s":
            stack.append(value)
            index += 1
            description = f"SHIFT {value}"

        elif kind == "r":
            lhs, rhs = productions[value]

            for _ in range(len(rhs)):
                stack.pop()

            next_state = GOTO.get((stack[-1], lhs))

            if next_state is None:
                print("REJECTED")
                return

            stack.append(next_state)
            description = f"REDUCE {lhs} -> {rhs or '#'}"

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
            rule = "" if rule == "#" else rule
            grammar.setdefault(lhs, []).append(rule)

    for lhs, rules in grammar.items():
        for rule in rules:
            productions.append((lhs, rule))

    # Augment grammar
    productions.insert(0, ("@", start))
    non_terminals.add("@")

    # Identify terminals
    for lhs, rhs in productions:
        for c in rhs:
            if not is_nt(c):
                terminals.add(c)

    find_first()
    find_follow(start)

    print("\nFIRST SETS:")
    for A in grammar:
        print(f"FIRST({A}) = {FIRST[A]}")

    print("\nFOLLOW SETS:")
    for A in grammar:
        print(f"FOLLOW({A}) = {FOLLOW[A]}")

    build_states()
    display_states()

    if not build_table():
        print("\nGrammar is NOT SLR(1): conflict detected.")
        return

    print("\nGrammar is SLR(1).")
    display_table()

    text = input("\nEnter input string: ")
    parse_string(text)


if __name__ == "__main__":
    main()
