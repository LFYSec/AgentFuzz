

def isLongPressedName(name, typed):
    j = 0
    for c in name:
        if j == len(typed):
            return False

        # If mismatch...
        if typed[j] != c:
            # If it's the first char of the block, ans is False.
            if (j == 0) or (typed[j-1] != typed[j]):
                return False

            # Discard all similar chars.
            cur = typed[j]
            while j < len(typed) and typed[j] == cur:
                j += 1

            # If next isn't a match, ans is False.
            if j == len(typed) or typed[j] != c:
                return False

        j += 1

    return True

print(isLongPressedName('Foolyou', 'FFoolyouu'))
