# 408_Valid_Word_Abbreviation.py

# Given a non-empty string s and an abbreviation abbr, 
# return whether the string matches with the given abbreviation.

# A string such as "word" contains only the following valid abbreviations:

# ["word", "1ord", "w1rd", "wo1d", "wor1", "2rd", "w2d", "wo2", "1o1d", "1or1", "w1r1", "1o2", "2r1", "3d", "w3", "4"]

# Notice that only the above abbreviations are valid abbreviations 
# of the string "word". Any other string is not a valid abbreviation of "word".

def validWordAbbreviation( word, abbr):
    pos = curr = 0
    for i in range(len(abbr)):
        if abbr[i].isdigit():
            num = int(abbr[i])
            if num == 0 and curr == 0:
                return False
            # curr = curr * 10 + num
            curr = int(str(curr) + str(num))
        else:
            pos += curr
            curr = 0
            if pos >= len(word):
                return False
            if word[pos] != abbr[i]:
                return False
            pos += 1
    pos += curr
    if pos == len(word):
        return True
    return False
    

print(validWordAbbreviation("internationalization", "i12iz4n"))   # pragma: no cover
