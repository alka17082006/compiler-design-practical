
def first(symbol, productions, first_sets):
    if symbol not in productions:
        return {symbol}

    result = first_sets[symbol]
    return result


def calculate_first(productions):
    first_sets = {nt: set() for nt in productions}

    changed = True

    while changed:
        changed = False

        for nt, rules in productions.items():
            for rule in rules:
                nullable = True

                for symbol in rule:
                    if symbol in productions:
                        symbols_first = first_sets[symbol]
                    else:
                        symbols_first = {symbol}

                    before = len(first_sets[nt])
                    first_sets[nt].update(symbols_first - {'#'})

                    if len(first_sets[nt]) != before:
                        changed = True

                    if '#' not in symbols_first:
                        nullable = False
                        break

                if nullable and '#' not in first_sets[nt]:
                    first_sets[nt].add('#')
                    changed = True

    return first_sets


def calculate_follow(productions, first_sets, start_symbol):
    follow_sets = {nt: set() for nt in productions}
    follow_sets[start_symbol].add('$')

    changed = True

    while changed:
        changed = False

        for nt, rules in productions.items():
            for rule in rules:
                for i, symbol in enumerate(rule):

                    if symbol not in productions:
                        continue

                    remaining = rule[i + 1:]
                    first_remaining = set()

                    nullable = True

                    for s in remaining:
                        if s in productions:
                            s_first = first_sets[s]
                        else:
                            s_first = {s}

                        first_remaining.update(s_first - {'#'})

                        if '#' not in s_first:
                            nullable = False
                            break

                    before = len(follow_sets[symbol])

                    follow_sets[symbol].update(first_remaining)

                    if nullable:
                        follow_sets[symbol].update(follow_sets[nt])

                    if len(follow_sets[symbol]) != before:
                        changed = True

    return follow_sets


def main():
    productions = {}

    n = int(input("Enter number of productions: "))

    print("Enter productions (example: E -> TQ | #)")

    for _ in range(n):
        line = input().replace(" ", "")
        nt, rhs = line.split("->")

        productions[nt] = rhs.split("|")

    start_symbol = next(iter(productions))

    first_sets = calculate_first(productions)
    follow_sets = calculate_follow(
        productions, first_sets, start_symbol
    )

    print("\nFIRST SETS")
    for nt in productions:
        print(f"FIRST({nt}) = {{ {', '.join(sorted(first_sets[nt]))} }}")

    print("\nFOLLOW SETS")
    for nt in productions:
        print(f"FOLLOW({nt}) = {{ {', '.join(sorted(follow_sets[nt]))} }}")


if __name__ == "__main__":
    main()
