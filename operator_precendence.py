def is_terminal(symbol, non_terminals):
    return symbol not in non_terminals


def calculate_firstvt(productions, non_terminals):
    firstvt = {nt: set() for nt in non_terminals}

    changed = True
    while changed:
        changed = False

        for lhs, rhs in productions:
            if not rhs:
                continue

            first = rhs[0]

            if is_terminal(first, non_terminals):
                if first not in firstvt[lhs]:
                    firstvt[lhs].add(first)
                    changed = True
            else:
                if len(rhs) > 1 and is_terminal(rhs[1], non_terminals):
                    if rhs[1] not in firstvt[lhs]:
                        firstvt[lhs].add(rhs[1])
                        changed = True

                for symbol in firstvt[first]:
                    if symbol not in firstvt[lhs]:
                        firstvt[lhs].add(symbol)
                        changed = True

    return firstvt


def calculate_lastvt(productions, non_terminals):
    lastvt = {nt: set() for nt in non_terminals}

    changed = True
    while changed:
        changed = False

        for lhs, rhs in productions:
            if not rhs:
                continue

            last = rhs[-1]

            if is_terminal(last, non_terminals):
                if last not in lastvt[lhs]:
                    lastvt[lhs].add(last)
                    changed = True
            else:
                if len(rhs) > 1 and is_terminal(rhs[-2], non_terminals):
                    if rhs[-2] not in lastvt[lhs]:
                        lastvt[lhs].add(rhs[-2])
                        changed = True

                for symbol in lastvt[last]:
                    if symbol not in lastvt[lhs]:
                        lastvt[lhs].add(symbol)
                        changed = True

    return lastvt


def build_precedence_table(productions, non_terminals, start):
    firstvt = calculate_firstvt(productions, non_terminals)
    lastvt = calculate_lastvt(productions, non_terminals)

    table = {}
    conflict = False

    def add_relation(a, b, relation):
        nonlocal conflict
        key = (a, b)

        if key in table and table[key] != relation:
            conflict = True
        else:
            table[key] = relation

    for lhs, rhs in productions:
        for i in range(len(rhs) - 1):
            a, b = rhs[i], rhs[i + 1]

            if is_terminal(a, non_terminals) and is_terminal(b, non_terminals):
                add_relation(a, b, "=")

            if is_terminal(a, non_terminals) and b in non_terminals:
                for t in firstvt[b]:
                    add_relation(a, t, "<")

            if a in non_terminals and is_terminal(b, non_terminals):
                for t in lastvt[a]:
                    add_relation(t, b, ">")

            if (
                i + 2 < len(rhs)
                and is_terminal(a, non_terminals)
                and b in non_terminals
                and is_terminal(rhs[i + 2], non_terminals)
            ):
                add_relation(a, rhs[i + 2], "=")

    for t in firstvt[start]:
        add_relation("$", t, "<")

    for t in lastvt[start]:
        add_relation(t, "$", ">")

    return firstvt, lastvt, table, conflict


def parse_string(text, productions, non_terminals, start, table):
    stack = "$"
    text += "$"
    pos = 0

    print("\nSTACK\t\tINPUT\t\tACTION")

    for _ in range(500):
        remaining = text[pos:]

        if stack == "$" + start and remaining == "$":
            print(f"{stack}\t\t{remaining}\t\tACCEPT")
            return True

        # Find the rightmost terminal in the stack.
        top_index = -1
        for i in range(len(stack) - 1, -1, -1):
            if stack[i] == "$" or stack[i] not in non_terminals:
                top_index = i
                break

        if top_index == -1 or pos >= len(text):
            break

        top_terminal = stack[top_index]
        next_symbol = text[pos]
        relation = table.get((top_terminal, next_symbol))

        if relation in ("<", "="):
            print(f"{stack}\t\t{remaining}\t\tSHIFT")
            stack += next_symbol
            pos += 1

        elif relation == ">":
            # Find the nearest '<' boundary between terminals.
            current = top_index
            boundary = -1

            while current > 0:
                previous = -1

                for i in range(current - 1, -1, -1):
                    if stack[i] == "$" or stack[i] not in non_terminals:
                        previous = i
                        break

                if previous == -1:
                    break

                rel = table.get((stack[previous], stack[current]))

                if rel == "<":
                    boundary = previous
                    break

                if rel not in ("=", ">"):
                    break

                current = previous

            if boundary == -1:
                break

            handle = stack[boundary + 1 :]

            matching_lhs = None
            for lhs, rhs in productions:
                if rhs == handle:
                    matching_lhs = lhs
                    break

            if matching_lhs is None:
                break

            print(f"{stack}\t\t{remaining}\t\tREDUCE {handle} -> {matching_lhs}")
            stack = stack[: boundary + 1] + matching_lhs

        else:
            break

    print(f"{stack}\t\t{text[pos:]}\t\tREJECT")
    return False


# Main program
print("OPERATOR PRECEDENCE PARSER")

n = int(input("Enter number of grammar productions: "))

productions = []
non_terminals = set()

print("Enter productions in the format E=E+T|T")

for _ in range(n):
    line = input().replace(" ", "")
    lhs, rhs_part = line.split("=")

    non_terminals.add(lhs)

    for rhs in rhs_part.split("|"):
        productions.append((lhs, rhs))

start = productions[0][0]

# Validate grammar restrictions.
valid = True

for lhs, rhs in productions:
    if "#" in rhs or any(
        rhs[i] in non_terminals and rhs[i + 1] in non_terminals
        for i in range(len(rhs) - 1)
    ):
        valid = False

if not valid:
    print("Invalid operator grammar.")
else:
    firstvt, lastvt, table, conflict = build_precedence_table(
        productions, non_terminals, start
    )

    print("\nFIRSTVT:")
    for nt in sorted(non_terminals):
        print(nt, ":", sorted(firstvt[nt]))

    print("\nLASTVT:")
    for nt in sorted(non_terminals):
        print(nt, ":", sorted(lastvt[nt]))

    if conflict:
        print("\nGrammar has precedence conflicts.")
    else:
        print("\nPrecedence Relations:")
        for (a, b), relation in sorted(table.items()):
            print(f"{a} {relation} {b}")

        expression = input("\nEnter input string: ")
        parse_string(expression, productions, non_terminals, start, table)
