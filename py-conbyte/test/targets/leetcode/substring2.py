def substring2(s: str) -> int:
    if len(s) == 0:
        return 0
    max_len = 1
    cur_len = 1
    n = len(s)
    str_start = 0
    str_end = 0
    i = 1
    while i < len(s):
        if s[i] in s[str_start:str_end + 1]:
            occuried = s.find(s[i], str_start, str_end + 1)
            new_len = i - occuried
            if new_len > max_len:
                max_len = new_len
            str_start = i
            cur_len = 1
        else:
            cur_len += 1
        str_end = i
        i += 1
    
    if cur_len > max_len:
        return cur_len
    else:
        return max_len

print(substring2('quiaaaaaaaaaac')) # pragma: no cover
