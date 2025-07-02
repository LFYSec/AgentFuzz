import re
import math

def solve_dsc(rules:[], payload:str):

    for rule in rules:
        if ".split(" in rule and not "re.split(" in rule:
            payload = solve_split(rule, payload)
        if ".index(" in rule or ".rindex(" in rule:
            payload = solve_index(rule, payload)
    return payload


def solve_split(expr:str, payload:str):
    pattern1 = r"\.split\((.*?)\)\[(.*?)\]"
    pattern2 = r"\.split\((.*?)\)"
    match = re.search(pattern1, expr)

    split_str = ""
    split_index = -1
    list_index = -math.inf


    if match:
        # .split(xxx)[xxx]
        split_args = match.group(1)
        list_index = int(match.group(2))

        if "," in split_args:
            split_str = split_args.split(",")[0].strip()[1:-1]
            split_index = int(split_args.split(",")[1].strip())
        else:
            split_str = split_args.strip()[1:-1]
    else:
        # .split(xxx)
        match = re.search(pattern2, expr)
        split_args = match.group(1)
        if "," in split_args:
            split_str = split_args.split(",")[0].strip()[1:-1]
            split_index = int(split_args.split(",")[1].strip())
        else:
            split_str = split_args.strip()[1:-1]

    print("split_str:", split_str)
    print("split_index:", split_index)
    print("list_index:", list_index)
    if list_index == -math.inf or list_index == 0:
        payload = payload + split_str
    elif list_index > 0 or list_index == -1:
        payload = abs(list_index) * split_str + payload
    else:
        payload = payload + (abs(list_index)-1) * split_str
    return payload

def solve_index(expr, payload):
    pattern1 = r"\.index\((.*?)\)"
    pattern2 = r"\.rindex\((.*?)\)"
    match = re.search(pattern1, expr)
    if match:
        # index
        index_str = match.group(1)[1:-1]
        return index_str + payload
    else:
        # rindex
        match = re.search(pattern2, expr)
        index_str = match.group(1)[1:-1]
        return payload + index_str


