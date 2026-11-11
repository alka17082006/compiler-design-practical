from collections import defaultdict, deque

grammar = {}
productions = []

non_terminals = set()
terminals = set()

FIRST = defaultdict(set)

states = []
transitions = {}

ACTION = {}
GOTO = {}


def is_nt(c):
    return c in non_terminals


# FIRST of a sequence of symbols
def first_sequence(sequence):
    result = set()
    nullable = True

    for c in sequence:
        current = FIRST[c] if is_nt(c) else {c}

        result.update(current - {"#"})

        if "#" not in current:
            nullable = False
            break

    if nullable:
        result.add("#")

    return result


# Calculate FIRST sets
def find_first():
    changed = True

    while changed:
        changed = False

        for A, rules in grammar.items():
            for rhs in rules:
                current = first_sequence(rhs)

                before = len(FIRST[A])
                FIRST[A].update(current)

                if len(FIRST[A]) != before:
                    changed = True


# CLR(1) CLOSURE
# Item = (production_number, dot_position, lookahead)
def closure(items):
    items = set(items)

    changed = True

    while changed:
        changed = False

        for p, dot, lookahead in list(items):
            lhs, rhs = productions[p]

            if dot < len(rhs):
                B = rhs[dot]

                if is_nt(B):
                    beta = rhs[dot + 1 :] + lookahead

                    lookaheads = first_sequence(beta) - {"#"}

                    for i, (A, rule) in enumerate(productions):
                        if A == B:
                            for a in lookaheads:
                                item = (i, 0, a)

                                if item not in items:
                                    items.add(item)
                                    changed = True

    return frozenset(items)


# GOTO operation
def go_to(items, symbol):
    moved = set()

    for p, dot, lookahead in items:
        lhs, rhs = productions[p]

        if dot < len(rhs) and rhs[dot] == symbol:
            moved.add((p, dot + 1, lookahead))

    return closure(moved) if moved else frozenset()


# Build canonical LR(1) collection
def build_states():
    initial = closure({(0, 0, "$")})

    states.append(initial)
    state_map = {initial: 0}

    queue = deque([0])

    symbols = sorted(non_terminals | terminals)

    while queue:
        i = queue.popleft()

        for symbol in symbols:
            next_state = go_to(states[i], symbol)

            if not next_state:
                continue

            if next_state not in state_map:
                state_map[next_state] = len(states)
                states.append(next_state)
                queue.append(state_map[next_state])

            transitions[(i, symbol)] = state_map[next_state]


# Add ACTION entry
def add_action(key, value):
    if key in ACTION and ACTION[key] != value:
        return False

    ACTION[key] = value
    return True


# Construct CLR(1) parsing table
def build_table():
    for i, items in enumerate(states):

        # SHIFT entries
        for symbol in terminals:
            if (i, symbol) in transitions:
                j = transitions[(i, symbol)]

                if not add_action((i, symbol), ("s", j)):
                    return False

        # GOTO entries
        for symbol in non_terminals:
            if (i, symbol) in transitions:
                GOTO[(i, symbol)] = transitions[(i, symbol)]

        # REDUCE and ACCEPT entries
        for p, dot, lookahead in items:
            lhs, rhs = productions[p]

            if dot == len(rhs):

                if p == 0:
                    if not add_action((i, "$"), ("acc", 0)):
                        return False

                else:
                    if not add_action((i, lookahead), ("r", p)):
                        return False

    return True


# Display canonical LR(1) items
def display_states():
    print("\nCANONICAL LR(1) ITEM COLLECTION")

    for i, items in enumerate(states):
        print(f"\nI{i}:")

        for p, dot, lookahead in sorted(items):
            lhs, rhs = productions[p]

            rule = rhs[:dot] + "." + rhs[dot:]

            print(f"  [{lhs} -> {rule}, {lookahead}]")


# Display parsing table
def display_table():
    print("\nACTION TABLE")

    for key, value in sorted(ACTION.items()):
        print(f"ACTION[{key[0]}, {key[1]}] = {value}")

    print("\nGOTO TABLE")

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
        for rhs in rules:
            productions.append((lhs, rhs))

    # Augmented grammar
    productions.insert(0, ("@", start))
    non_terminals.add("@")

    # Identify terminals
    for lhs, rhs in productions:
        for c in rhs:
            if not is_nt(c):
                terminals.add(c)

    find_first()

    print("\nFIRST SETS:")
    for A in grammar:
        print(f"FIRST({A}) = {FIRST[A]}")

    build_states()
    display_states()

    if not build_table():
        print("\nGrammar is NOT CLR(1): conflict detected.")
        return

    print("\nGrammar is CLR(1).")
    display_table()

    text = input("\nEnter input string: ")
    parse_string(text)


if __name__ == "__main__":
    main()
