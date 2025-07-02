
# 003_Longest_Substring_Without_Repeating_Characters

def substring(s: str) -> int:
    if len(s) == 0:
        return 0
    max_len = 1
    n = len(s)
    str_start = 0
    str_end = 0
    i = 1
    cur_str = s[str_start:str_end + 1]
    cur_len = len(cur_str)
    while i < len(s):
        if s[i] in cur_str:
            occuried = s.find(s[i], str_start, str_end + 1)
            str_start = occuried + 1
        str_end = i
        cur_str = s[str_start:str_end + 1]
        cur_len = len(cur_str)
        if cur_len >= max_len:  
            max_len = cur_len
        i += 1
    
    return max_len


print(substring("oi"))  # pragma: no cover
