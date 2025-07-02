# AgentFuzz

[TOC]

## Description

The source code of *Make Agent Defeat Agent: Automatic Detection of Taint-Style Vulnerabilities in LLM-based Agents*

```
citation
```

## Step 1. Static analysis

### Preparation

Before Static Analysis, you should install [CodeQL-CLI](https://docs.github.com/en/code-security/codeql-cli/getting-started-with-the-codeql-cli/setting-up-the-codeql-cli), and [Miniconda](https://docs.conda.io/en/latest/miniconda.html). 

Then, run the following command to create a Python 3.10.12 environment:
```shell
conda create -n py31012 python=3.10.12
```

Then execute the following command to enter the virtual environment:
```shell
conda activate py31012
```

Execute the following command within the virtual environment
```shell
pip install -r requirements.txt
```

### Execution

`git clone` your analysis target. For example:

```shell
git clone https://github.com/microsoft/TaskWeaver.git
```

`cd` into it.

```shell
cd TaskWeaver
```

Create a CodeQL database:

```shell
codeql database create /path/to/database/TaskWeaver --language=python --source-root=.
```

Modify file `auto_analyze.py`, change `DB_HOME` and `arg_dbname` to your previously created database:

```python
DB_HOME = '/path/to/database'
arg_dbname = "TaskWeaver"
```

Finally, run it:

```shell
python3 auto_analyze.py
```

### Result

Finally, you'll get 4 files under directory `output/TaskWeaver`:

```text
enter_hook.json
oracle.json
TaskWeaver-dsc.json
TaskWeaver-if.json
```

## Step 2. Instrumentation

### Preparation

You should start you target application manually.

### Execution

Move `trace/cetracer.py` , `enter_hook.json`, `oracle.json`, `TaskWeaver-if.json` to where the application is running. 

For example:

```shell
docker cp trace/cetracer.py taskweaver:/app/playground/UI/cetracer.py
docker cp output/TaskWeaver/enter_hook.json taskweaver:/app/enter_hook.json
docker cp output/TaskWeaver/oracle.json taskweaver:/app/oracle.json
docker cp output/TaskWeaver/TaskWeaver-if.json taskweaver:/app/TaskWeaver-if.json
```

Next, add the following code to the agent thread. (For multi-threaded applications, this code should be added to the thread where the agent is running.)

```python
import cetracer 
cetracer.start_ce_trace(conf="/app/if.json", enter_input_conf="/app/enter_hook.json", oracle_rule_conf = "/app/oracle.json", log="/tmp/if.log", match_log = "/tmp/hook.log", call_stack_log = "/tmp/callstack.log", oracle_name = "/tmp/oracle.log")
```

For example, add codes to `/app/playground/UIapp.py`

```python
from taskweaver.app.app import TaskWeaverApp

......

import cetracer 
cetracer.start_ce_trace(conf="/app/if.json", enter_input_conf="/app/enter_hook.json", oracle_rule_conf = "/app/oracle.json", log="/tmp/if.log", match_log = "/tmp/hook.log", call_stack_log = "/tmp/callstack.log", oracle_name = "/tmp/oracle.log")

......

if __name__ == "__main__":
    ......
```

Finally, restart the target application and **wait for 40 seconds**. (Because, to avoid introducing excessive overhead during application startup, our instrumentation remains inactive for the first 40 seconds after the target application starts.)

## Step 3. Fuzzing

### Preparation

#### Prerequisites

- SMT-solver installed ([Z3](https://github.com/Z3Prover/z3)) 


Environment for py-conbyte
1. Exit the current virtual environment.
    ```shell
    conda deactivate
    ```
2. Creating a Python 3.7.3 Virtual Environment with Miniconda:
    ```shell
    conda create -n py373 python=3.7.3
    ```
3. Enter the virtual environment and obtain the Python address:
    ```shell
    conda activate py373
    ```
4. Install pipenv:
    ```shell
    pip install pipenv
    ```
5. Enter the py conbyte directory and install the required virtual environment
    ```shell
    cd py-conbyte
    pipenv shell
    ```
6. Install required packages for this environment.
    ```shell
    conda activate py373
    pipenv install
    ```
7. Leave this virtual environment.
    ```shell
    exit
    conda deactivate
    ```
8. Enter the virtual environment for agentfuzz.
    ```shell
    conda activate py31012
    ```

#### LLM Configuration

Fill in `OPENAI_API_BASE` and `OPENAI_API_KEY` in `./config/__init__.py`.

#### Create a script

Create a script under `./poc` to tell us **how to send message** to target agent.

For example, `./poc/TaskWeaver/poc.py`:

```python
with sync_playwright() as playwright:
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()
    page.route(
        "**/*",
        lambda route: route.abort()
        if route.request.resource_type in ["image", "stylesheet"] else route.continue_()
    )
    page.goto("http://localhost:8000/")
    page.get_by_placeholder("Type your message here...").click()
    page.get_by_placeholder("Type your message here...").fill(payload)
    page.keyboard.press("Enter")
    time.sleep(60)
    context.close()
    browser.close()
```

It just open the browser, type in the message and click button to send to the agent.

#### Fill in configuration

Open `./poc/poc_factory.py` and add an entry to the dict `factory`. 

The application name and agent name can be any name you prefer. For example, `"Taskweaver"` and `"CodeInterpreter"`.

The `call_chain` of `MetaData` is the target call chain in `oracle.json`.

> `call_chain` of `MetaData` can be any content when running `batchmain.py`, because we will traverse all call chains.
> Only if you are running `main.py`, you should fill in `call_chain` of `MetaData`. 

The `container_name` of `MetaData` means which docker the application is running.

For example:

```python
"Taskweaver": MetaData(
    "DEADBEEF",
    "taskweaver",
    "output/TaskWeaver/oracle.json",
    "output/TaskWeaver/TaskWeaver-if.json",
    "output/TaskWeaver/enter_hook.json",
    "output/TaskWeaver/TaskWeaver-dsc.json",
    poc.TaskWeaver.CodeInterpreter.poc.connect_with_auth
)

```

Then, modify the commands and callchain file path in `batchmain.py`. For example:

```python
with open('./output/TaskWeaver/oracle.json') as f:
    
......

subprocess.run([PYTHON_EXECUTABLE, "main.py", "-app", "Taskweaver"], env={"CALLCHAIN": c}, timeout=1200)
```

This enables our tool to traverse all call chains, send the prompt to the target agent via `poc.TaskWeaver.CodeInterpreter.poc.connect_with_auth`, and detect potential vulnerabilities.

### Execution

Just run:

```shell
python3 batchmain.py
```

And results will be shown in command line and `./log`.

### Result

If you see the following output, it means we have triggered the callchain and it may be a vulnerability.

```text
**********exploration successful**********
True
```