import json
import re
import sys
import copy
import argparse

data = None

filename = "./sarif/TaskWeaver-location.sarif"
enter_hook_path = "./output/TaskWeaver/enter_hook.json"
oracle_path = "./output/TaskWeaver/oracle.json"

def args_from_cli():
    global filename
    global enter_hook_path
    global oracle_path
    parser = argparse.ArgumentParser(description="Process input and output files.")
    parser.add_argument(
        "--filename",
        type=str,
        required=False,
        default=None,
        help="The path to the input file to process."
    )
    parser.add_argument(
        "--enter_hook_path",
        type=str,
        required=False,
        default=None,
        help="The path to the output file to save enter hook json."
    )
    parser.add_argument(
        "--oracle_path",
        type=str,
        required=False,
        default=None,
        help="The path to the output file to save oracle json."
    )
    args = parser.parse_args()
    if args.filename:
        filename = args.filename
    if args.enter_hook_path:
        enter_hook_path = args.enter_hook_path
    if args.oracle_path:
        oracle_path = args.oracle_path

args_from_cli()

results = None

rules = []

rules_hash = set()
oracles = []

def paser_call_chain(input_str):
    if ']' in input_str:
        pattern = r'\[(.*?)\]'
        match = re.findall(pattern, input_str)[0]
    else:
        match = input_str

    pattern = r'^\d+#\s*(.*)$'
    match = re.match(pattern, match.strip())
    match_str = match.group(1)
    pattern = r'@[\w.]+\.py'
    result = re.sub(pattern, '', match_str)
    pattern = r'@.*'
    result = re.sub(pattern, '', result)
    result = result.replace('->',' -> ')
    return result.strip()

def extract_code_segment(file_path, start_row, start_col, end_row, end_col):
    with open(file_path, "r", encoding="utf-8") as file:
        lines = file.readlines()

    extracted_lines = lines[start_row - 1 : end_row]
    extracted_content = []

    if len(extracted_lines) == 1:
        extracted_content.append(extracted_lines[0][start_col-1:end_col])
    else:
        for i, line in enumerate(extracted_lines):
            if i == 0:
                extracted_content.append(line[start_col - 1 :])
            elif i == len(extracted_lines) - 1:
                extracted_content.append(line[: end_col])
            else:
                extracted_content.append(line)
    return "".join(extracted_content).replace("\n","")

def get_oracle(file_path, output2):
    with open(file_path, encoding="utf-8") as f:
        data = json.load(f)

    results = None
    messages = {}
    try:
        results =  data["runs"][0]["results"]
        for r in results:
            for one_call in r["message"]["text"].split("\n"):
                sink_path = one_call.split("->")[-1].strip()
                caller = one_call.split("->")[-2].strip()
                if "#" in caller:
                    caller = caller.split("#")[1].strip()
                if "@" in caller:
                    caller = caller.split("@")[0].strip()
                if ']' in  sink_path:
                    pattern = r'(.*?)\]'
                    sink_path = re.findall(pattern, sink_path)[0]

                sink = sink_path.split("@")[0]
                file = sink_path.split("@")[1]
                anchor_parts = file.split("$$")
                file_path = anchor_parts[0]
                start = anchor_parts[1].split(":")
                start_row = int(start[0])
                start_col = int(start[1])
                end = anchor_parts[2].split(":")
                end_row = int(end[0])
                end_col = int(end[1])
                try:
                    data = extract_code_segment(
                                file_path, start_row, start_col, end_row, end_col
                            )
                except Exception as e:
                    print("data: {}".format(e))
                    data = ""
                call_chain = paser_call_chain(one_call)
                if call_chain not in messages:
                    messages[call_chain] = []
                messages[call_chain].append({"file_path":file_path, "sink": sink, "line":start_row, "expr":data, "caller":caller})
    except Exception as e:
        print(e)

    with open(output2, "w+") as f:
        f.write(json.dumps(messages))

def get_enter_hook(file_path, output):
    with open(file_path, encoding="utf-8") as f:
        data = json.load(f)
    try:
        results =  data["runs"][0]["results"]
        for r in results:
            text = r["message"]["text"]
            if ']' in text:
                our_text = text[1:len(text)-4]
            else:
                our_text = text
            s1 = our_text.split("#")[1].split("->")[0:-1]
            for k in s1:
                if k not in rules_hash:
                    rules_hash.add(k)
                    s2 = k.split("@")
                    rules.append({"package_name": "*", "module_name": s2[1][0:-3], "func_name": s2[0]})
    except Exception as e:
        print(e)

    with open(output, "w+") as f:
        f.write(json.dumps(rules))


if __name__ == "__main__":
    get_enter_hook(filename, enter_hook_path)
    get_oracle(filename, oracle_path)