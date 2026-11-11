from collections import defaultdict, deque

grammar = {}
productions = []

non_terminals = set()
terminals = set()

FIRST = defaultdict(set)

states = []
transitions = {}

lalr_states = []
lalr_transitions = {}

ACTION = {}
GOTO = {}


def is_nt(c):
    return c in non_terminals


# FIRST of a sequence
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
# Item = (production number, dot position, lookahead)
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


# Construct canonical CLR(1) states
def build_clr_states():
    initial = closure({(0, 0, "$")})

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


# Find the LR(0) core of a CLR state
def get_core(state):
    return frozenset((p, dot) for p, dot, a in state)


# Merge CLR states with identical cores
def merge_states():
    core_map = {}
    state_group = {}

    for i, state in enumerate(states):
        core = get_core(state)

        if core not in core_map:
            core_map[core] = len(core_map)

        state_group[i] = core_map[core]

    lalr_states.extend([set() for _ in range(len(core_map))])

    for i, state in enumerate(states):
        group = state_group[i]

        for p, dot, lookahead in state:
            lalr_states[group].add((p, dot, lookahead))

    # Merge transitions
    for (i, symbol), j in transitions.items():
        source = state_group[i]
        destination = state_group[j]

        key = (source, symbol)

        if key in lalr_transitions:
            if lalr_transitions[key] != destination:
                raise ValueError("Inconsistent merged transitions")

        lalr_transitions[key] = destination

    # Convert merged states into immutable sets
    for i in range(len(lalr_states)):
        lalr_states[i] = frozenset(lalr_states[i])


# Add ACTION entry and detect conflicts
def add_action(key, value):
    if key in ACTION and ACTION[key] != value:
        return False

    ACTION[key] = value
    return True


# Construct LALR parsing table
def build_table():
    for i, items in enumerate(lalr_states):

        # SHIFT entries
        for symbol in terminals:
            if (i, symbol) in lalr_transitions:
                j = lalr_transitions[(i, symbol)]

                if not add_action((i, symbol), ("s", j)):
                    return False

        # GOTO entries
        for symbol in non_terminals:
            if (i, symbol) in lalr_transitions:
                GOTO[(i, symbol)] = lalr_transitions[(i, symbol)]

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


# Display merged LALR states
def display_states():
    print("\nLALR(1) ITEM COLLECTION")

    for i, items in enumerate(lalr_states):
        print(f"\nI{i}:")

        for p, dot, lookahead in sorted(items):
            lhs, rhs = productions[p]

            rule = rhs[:dot] + "." + rhs[dot:]

            print(f"  [{lhs} -> {rule}, {lookahead}]")


# Display parsing tables
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

    # Build CLR states and merge them
    build_clr_states()

    print("\nNumber of CLR(1) states:", len(states))

    merge_states()

    print("Number of LALR(1) states:", len(lalr_states))

    display_states()

    if not build_table():
        print("\nGrammar is NOT LALR(1): conflict detected.")
        return

    print("\nGrammar is LALR(1).")

    display_table()

    text = input("\nEnter input string: ")
    parse_string(text)


if __name__ == "__main__":
    main()
