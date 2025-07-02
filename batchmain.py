import json
import subprocess
import os
import time


def extract_token_usage(log_file):
    with open(log_file, 'r') as f:
        lines = f.readlines()

    for line in reversed(lines):
        if 'token usage:' in line:
            parts = line.split('token usage:')
            if len(parts) > 1:
                token_str = parts[1].strip()
                try:
                    return int(token_str)
                except ValueError:
                    return None
    return None


with open('./output/TaskWeaver/oracle.json') as f:
    data = json.load(f)
    call_chains = []
    for key, value in data.items():
        call_chains.append(key)

os.system("mkdir log")


PYTHON_EXECUTABLE = "python3"
if os.name == "nt":  # Windows
    PYTHON_EXECUTABLE = "python"

with open("log/succ.log", "a+") as f:
    f.write(f"================={time.strftime('%Y-%m-%d %H:%M:%S')}=================\n")

for chain in call_chains:
    c = chain.strip()
    try:
        start_time = time.time()
        subprocess.run([PYTHON_EXECUTABLE, "main.py", "-app", "Taskweaver"], env={"CALLCHAIN": c}, timeout=1200)
        end_time = time.time()
        elapsed_time = end_time - start_time
        newlog = f"log/{c.replace(' ', '').replace('>', '-')}.log"
        if os.name == "nt":  # Windows
            os.system(f"move test.log {newlog}")
        else:
            os.system(f"mv test.log {newlog}")
        try:
            n = extract_token_usage(newlog)
            with open("log/succ.log", "a+") as f:
                f.write(f"{c}:{str(elapsed_time)}s:{str(n)}\n")
        except Exception as ee:
            print(ee)
    except Exception as e:
        try:
            end_time = time.time()
            elapsed_time = end_time - start_time
            with open("log/error.log", "a+") as f:
                f.write(f"{c}:{str(elapsed_time)}s:{str(e)}\n")
        except Exception as ee:
            print(ee)
        newlog = f"log/error-{c.replace(' ', '').replace('>', '-')}.log"
        os.system(f"mv test.log {newlog}")
