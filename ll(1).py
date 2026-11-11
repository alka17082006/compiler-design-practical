from collections import defaultdict

grammar = {}
FIRST = defaultdict(set)
FOLLOW = defaultdict(set)
table = {}


def is_nt(symbol):
    return symbol in grammar


def calculate_first():
    changed = True

    while changed:
        changed = False

        for A, rules in grammar.items():
            for rule in rules:
                nullable = True

                for symbol in rule:
                    current = FIRST[symbol] if is_nt(symbol) else {symbol}

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


def calculate_follow(start):
    FOLLOW[start].add("$")

    changed = True

    while changed:
        changed = False

        for A, rules in grammar.items():
            for rule in rules:
                for i, B in enumerate(rule):
                    if not is_nt(B):
                        continue

                    remaining = rule[i + 1 :]
                    nullable = True

                    for symbol in remaining:
                        current = FIRST[symbol] if is_nt(symbol) else {symbol}

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


def first_of_string(string):
    result = set()
    nullable = True

    for symbol in string:
        current = FIRST[symbol] if is_nt(symbol) else {symbol}

        result.update(current - {"#"})

        if "#" not in current:
            nullable = False
            break

    if nullable:
        result.add("#")

    return result


def create_table():
    for A, rules in grammar.items():
        for rule in rules:
            first = first_of_string(rule)

            for terminal in first - {"#"}:
                key = (A, terminal)

                if key in table and table[key] != rule:
                    print("Grammar is NOT LL(1): conflict detected.")
                    return False

                table[key] = rule

            if "#" in first:
                for terminal in FOLLOW[A]:
                    key = (A, terminal)

                    if key in table and table[key] != rule:
                        print("Grammar is NOT LL(1): conflict detected.")
                        return False

                    table[key] = rule

    return True


def parse_string(start, string):
    stack = ["$", start]
    string += "$"
    index = 0

    print("\nStack\t\tInput\t\tAction")

    while stack:
        top = stack[-1]
        current = string[index]

        if top == current == "$":
            print("ACCEPTED")
            return

        if not is_nt(top):
            if top == current:
                stack.pop()
                index += 1
                action = f"Match {top}"
            else:
                print("REJECTED")
                return
        else:
            rule = table.get((top, current))

            if rule is None:
                print("REJECTED")
                return

            stack.pop()

            if rule != "#":
                stack.extend(reversed(rule))

            action = f"{top} -> {rule}"

        print("".join(stack[::-1]), "\t\t", string[index:], "\t\t", action)

    print("REJECTED")


def main():
    n = int(input("Enter number of productions: "))

    print("Enter productions (e.g. E -> TQ | #):")

    for _ in range(n):
        line = input().replace(" ", "")
        A, rhs = line.split("->")
        grammar[A] = rhs.split("|")

    start = next(iter(grammar))

    calculate_first()
    calculate_follow(start)

    print("\nFIRST:")
    for A in grammar:
        print(A, "=", FIRST[A])

    print("\nFOLLOW:")
    for A in grammar:
        print(A, "=", FOLLOW[A])

    if not create_table():
        return

    print("\nPREDICTIVE PARSING TABLE:")
    for key, value in sorted(table.items()):
        print(f"M[{key[0]}, {key[1]}] = {key[0]} -> {value}")

    string = input("\nEnter input string: ")
    parse_string(start, string)


if __name__ == "__main__":
    main()
