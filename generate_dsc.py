import json
import re
import os
import traceback
import argparse
data = None

filename = "./sarif/TaskWeaver-dsc.sarif"
output = "./output/TaskWeaver/TaskWeaver-dsc.json"

def args_from_cli():
    global filename
    global output
    parser = argparse.ArgumentParser(description="Process input and output files.")
    parser.add_argument(
        "--filename",
        type=str,
        required=True,
        help="The path to the input file to process."
    )
    parser.add_argument(
        "--output",
        type=str,
        required=True,
        help="The path to the output file to save results."
    )
    args = parser.parse_args()
    if args.filename:
        filename = args.filename
    if args.output:
        output = args.output

args_from_cli()

with open(filename, encoding="utf-8") as f:
    data = json.load(f)


results = None

def extract_code_segment(file_path, start_row, start_col, end_row, end_col):
    with open(file_path, "r", encoding="utf-8") as file:
        lines = file.readlines()

    extracted_lines = lines[start_row - 1 : end_row]
    extracted_content = []

    for i, line in enumerate(extracted_lines):
        if i == 0:
            extracted_content.append(line[start_col - 1 :])
        elif i == len(extracted_lines) - 1:
            extracted_content.append(line[: end_col + 1])
        else:
            extracted_content.append(line)

    return "".join(extracted_content)

def extract_content(text):
    if "]" in text:
        match = re.search(r"\[(.*?)\]", text)
        return match.group(1) if match else None
    else:
        return text

def paser_call_chain(input_str):
    pattern = r'^\d+#\s*(.*)$'
    match = re.match(pattern, input_str.strip())
    match_str = match.group(1)
    pattern = r'@[\w.]+\.py'
    result = re.sub(pattern, '', match_str)
    pattern = r'@.*'
    result = re.sub(pattern, '', result)
    result = result.replace('->',' -> ')
    return result.strip()

try:
    results = data["runs"][0]["results"]
    constraints = {}
    constraints_set = {}
    for r in results:
        texts = r["message"]["text"].split("\n")
        for text in texts:
            our_text = extract_content(text)
            if len(our_text) == 0:
                continue
            ccsc = our_text.split("@@")
            cc = ccsc[0] # Source.getPathStr()
            cc = paser_call_chain(cc)
            sc = ccsc[1].split("~")
            for c in sc:
                p = c.split("#")
                abstract = p[0]
                file_path = p[1]
                start = p[2].split(":")
                start_row = int(start[0])
                start_col = int(start[1])
                end = p[3].split(":")
                end_row = int(end[0])
                end_col = int(end[1])
                try:
                    data = extract_code_segment(
                        file_path, start_row, start_col, end_row, end_col
                    )
                except Exception as e:
                    print("data: {}".format(e))
                    data = ""
                if cc in constraints and not data.strip() in constraints_set[cc]:
                    constraints[cc].append(data.strip())
                    constraints_set[cc].add(data.strip())
                else:
                    constraints[cc] = [data.strip()]
                    constraints_set[cc] = {data.strip()}
            
except Exception as e:
    print(e)

with open(output, "w+") as f:
    json.dump(constraints, f)