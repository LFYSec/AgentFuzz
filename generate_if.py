import json
import re
import os
import traceback
import argparse
data = None

filename = "./sarif/TaskWeaver-if.sarif"
output = "./output/TaskWeaver/TaskWeaver-if.json"

def args_from_cli():
    global filename
    global output
    parser = argparse.ArgumentParser(description="Process input and output files.")
    parser.add_argument(
        "--filename",
        type=str,
        required=False,
        default=None,
        help="The path to the input file to process."
    )
    parser.add_argument(
        "--output",
        type=str,
        required=False,
        default=None,
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


def extract_content(text:str):
    if "]" in text:
        match = re.search(r"\[(.*?)\]", text)
        return match.group(1) if match else None
    else:
        return text


def paser_call_chain(input_str:str):
    try:
        sink_line = int(input_str.split("@")[-1].split("$$")[1].split(":")[0])
    except Exception as e:
        sink_line = 1000
    pattern = r'^\d+#\s*(.*)$'
    match = re.match(pattern, input_str.strip())
    match_str = match.group(1)
    pattern = r'@[\w.]+\.py'
    result = re.sub(pattern, '', match_str)
    pattern = r'@.*'
    result = re.sub(pattern, '', result)
    result = result.replace('->',' -> ')
    return result.strip(), sink_line

constraints = {}

try:
    results = data["runs"][0]["results"]
    for r in results:
        texts = r["message"]["text"].split("\n")
        for text in texts:
            our_text = extract_content(text)
            if len(our_text) == 0:
                continue
            call_chain = ""
            call_chain = our_text.split("@@")[0]
            call_chain, sink_line= paser_call_chain(call_chain)
            our_text = our_text.split("@@")[1]
            if len(our_text) == 0:
                continue
            priority_order = {}
            if "->"  in call_chain:
                call_functions = call_chain.split("->")
            else:
                call_functions =call_chain
            for index in range(len(call_functions)):
                priority_order[call_functions[index].strip()] = index
            our_ifs = []
            files = our_text.split("->")
            for file in files:
                try:
                    anchor_parts = file.split("#")
                    function_name = anchor_parts[0]
                    file_path = anchor_parts[1]
                    start = anchor_parts[2].split(":")
                    start_row = int(start[0])
                    start_col = int(start[1])
                    end = anchor_parts[3].split(":")
                    end_row = int(end[0])
                    end_col = int(end[1])
                    try:
                        data = extract_code_segment(
                            file_path, start_row, start_col, end_row, end_col
                        )
                    except Exception as e:
                        print("data: {}".format(e))
                        data = ""
                    try:
                        # Filter out if statements after the sink point
                        if function_name == call_functions[-2].strip() and start_row > sink_line:
                            continue
                    except Exception as e:
                        print(traceback.print_exc())
                        print(e)
                    our_ifs.append(
                        {
                            "file_path": file_path,
                            "module_name": os.path.basename(file_path)[:-3],
                            "func_name": function_name,
                            "expr": data.rstrip(":\n"),
                            "start_line": start_row,
                        }
                    )
                    if function_name not in priority_order:
                        priority_order[function_name] = 1
                        for k in priority_order:
                            priority_order[k] += 1

                except Exception as e:
                    print(traceback.print_exc())
                    print(e)
                    print(text)
                    print(files)
                    exit(0)
            our_ifs = sorted(our_ifs, key=lambda x: (priority_order[x['func_name']], x['start_line']))
            constraints[call_chain] = our_ifs
except Exception as e:
    print(traceback.print_exc())
    print(e)
with open(output, "w+") as f:
    json.dump(constraints, f)
