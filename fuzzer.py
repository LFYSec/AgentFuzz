import json
import re
import os
import platform
import sys
import config as _Config
from config.PromptTemplete import *
import Logger as _Logger
import asyncio
import inspect
from langchain_community.chat_models import ChatOpenAI
from langchain.chains.conversation.base import ConversationChain
from langchain.chains.llm import LLMChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
import time
from langchain.callbacks import OpenAICallbackHandler
import copy
from generate_conbyte import infer_variable_types, get_conbyte_result
from trace.compare.compare import fuzzy_search, longest_common_substring
from solve_dsc import solve_dsc
import ast
import math
import threading

LOG = _Logger.get_logger(_Config.__prog__)
Timer = False
connect_with_auth = None
SEED_POOL = []
CALL_CHAIN_SCORE = []
HOOK_FILE_PATH = ""
IF_FILE_PATH = ""
IF_RULE = []
IF_RULE_PATH = ""
ORACLE_FILE_PATH = ""
ORACLE_RULE = []
WIN_HOOK_FILE_PATH = ""
WIN_IF_FILE_PATH = ""
WIN_ORACLE_FILE_PATH = ""
OUTPUT = "tmp"
DSC_RULE = []
IS_DSC_SOLVE = False
LAST_COMMON_SUBSTRING = {}
LAST_CORRECT_PAYLOAD = {}
LAST_PROMPT = ""
DSC_FILE_PATH = ""


class Chromosome:
    input_prompt: str = "" # The prompt to call LLM to get agent_input_prompt
    llm_response: str = "" # The response from LLM(include the agent_input_prompt and the CoT)

    target_call_chain: str = "" # The target call chain of the chromosome

    agent_input_prompt: str = "" # The prompt sent to agent
    call_stack: str = "" # After the agent response, the call_stack agent have.
    is_successful: bool = False # Whether trigered the target component
    fitness_score_response: str = "" # The reason why the fitness score is calculated
    fitness_score: float = 0.0 # The score of the agent_intput_prompt

    similarity_score: float = 0.0 # The similarity score of the prompt with the target component
    similarity_score_reason: str = "" # The reason why the similarity score is calculated
    distance_score: float = 0.0 # The distance score of the prompt with the target component
    select_penalty_score: float = 0.0
    callchain_penalty_score: float = 0.0
    final_score: float = 0.0
    final_match_oracle = []
    match_oracle_rule = {}
    is_semantic_success: bool = False
    match_index = -1
    match_rules = []
    is_dsc_solve = False
    dsc_constraint = []


os.environ["OPENAI_API_BASE"] = _Config.OPENAI_API_BASE
os.environ["OPENAI_API_KEY"] = _Config.OPENAI_API_KEY

# Semantic mutator
openai_callback = OpenAICallbackHandler()

llm = ChatOpenAI(model_name=_Config.__gpt_version__, temperature=_Config.__gpt__temperature__, callbacks=[openai_callback])

system_message = SystemMessagePromptTemplate.from_template(
    MUTATE_SYSTEM_PROMPT
)

chat_prompt = ChatPromptTemplate.from_messages([
    system_message,
    HumanMessagePromptTemplate.from_template("{input} , {history}")
])

memory = ConversationBufferMemory()
conversationchain = ConversationChain(llm=llm, memory=memory, prompt = chat_prompt)
conversationchain.invoke({"input": MUTATE_EXAMPLE})


# Similarity scoring
init_prompt = ChatPromptTemplate.from_messages([
    HumanMessagePromptTemplate.from_template("{input}")
])

llmchain = LLMChain(llm=llm, prompt=init_prompt)



# Mutator scheduling
scheduling_system_message = SystemMessagePromptTemplate.from_template(
    SCHEDULING_SYSTEM_PROMPT
)

scheduling_chat_prompt = ChatPromptTemplate.from_messages([
    scheduling_system_message,
    HumanMessagePromptTemplate.from_template("{input} , {history}")
])

scheduling_memory = ConversationBufferMemory()
scheduling_conversationchain = ConversationChain(llm=llm, memory=scheduling_memory, prompt = scheduling_chat_prompt)



CALL_STACK_FILE_PATH = ""
HOOK_FILE_PATH = ""
WIN_CALL_STACK_FILE_PATH = ""
WIN_HOOK_FILE_PATH = ""
OUTPUT = "tmp"


def gpt_4o_mini_api(query:str):
    res = conversationchain.invoke({"input": query})
    LOG.info(f"mutate token usage: {openai_callback.total_tokens}")
    return res['response']


def get_similarity_score(target_call_chain, agent_input_prompt, call_stack):
    result = llmchain.run(input=SCORE_PROMPT.format(target_call_chain, agent_input_prompt, call_stack))
    # LOG.info("********************************* result prompt **************************************")
    # print(result)
    LOG.info(f"init token usage: {openai_callback.total_tokens}")
    pattern = r"<SCORE>(\s*\d+\s*)<ENDSCORE>"

    # Matching similarity score
    match = re.search(pattern, result)
    if match:
        score = float(match.group(1))
    else:
        score = 0

    # Matching score reasons
    pattern = r"<SCOREREASON>(.*?)<SCOREREASON>"

    match = re.search(pattern, result)

    if match:
        score_reason = str(match.group(1))
    else:
        score_reason = result
    return score, score_reason

def get_distance_score(target_call_chain, call_stack):
    cloest_index = -1
    target_call_chain = target_call_chain.split("->")[:-1]
    for call_index in  range(len(target_call_chain)):
        for call in call_stack:
            if call in target_call_chain[call_index]:
                cloest_index = call_index
                break
    
    if cloest_index == -1:
        return 0
    else:
        return 10 * math.exp(-(len(target_call_chain) -1 - cloest_index))



def output_parser(output_message):
    pattern = r"```.*?\n(.*?)\n.*?```"
    match = re.search(pattern, output_message, re.DOTALL)

    if match:
        extracted_text = match.group(1).strip()
        return extracted_text
    else:
        LOG.info("No match found.")


def mutate_output_parser(output_message):
    pattern = r"<NEWPROMPT>.*?\n(.*?)\n.*?<ENDNEWPROMPT>"
    match = re.search(pattern, output_message, re.DOTALL)

    if match:
        extracted_text = match.group(1).strip()
        return extracted_text
    else:
        LOG.info("No match found.")


def contains_constant_string(expression):
    try:
        tree = ast.parse(expression, mode='eval')

        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                return True
        return False
    except Exception:
        return False

def clean_text(s:str):
    s = s.strip()
    # Remove special characters from the beginning and end of a string
    s = re.sub(r'^[",.:\'\s]+|[",.:\'\s]+$', '', s)
    return s


def solve_and_get_new_prompt(population: Chromosome):
    global IF_RULE, LAST_COMMON_SUBSTRING, LAST_CORRECT_PAYLOAD, LAST_PROMPT, IS_DSC_SOLVE,IF_RULE_PATH
    with open(IF_RULE_PATH,'r')as f:
        content = json.load(f)
    IF_RULE = content.get(population.target_call_chain,[])

    match_index = population.match_index
    match_rules = population.match_rules
    input_prompt = population.agent_input_prompt
    dsc_rule = population.dsc_constraint
    is_dsc_solve = population.is_dsc_solve
    match_results = []
    input_vars_key = []
    input_vars = {}
    LAST_COMMON_SUBSTRING = {}
    LAST_CORRECT_PAYLOAD = {}
    LAST_PROMPT = input_prompt
    if match_index < 0 or len(match_rules) == 0:
        return input_prompt, population.is_dsc_solve 
    if match_index > -1:
        expr = IF_RULE[match_index]["expr"]
        input_vars_key = IF_RULE[match_index].get("input_vars",[])
        function_code = IF_RULE[match_index].get("function_code","")
        if not contains_constant_string(expr):
            LOG.info("************************ MATCH RESULTS **********************")
            LOG.info("not found constant str in constraint expr: {}".format(expr))
            LOG.info("***************************  NEW PROMPT **************************")
            LOG.info(input_prompt)
            return input_prompt, population.is_dsc_solve
        for match_rule in match_rules:
            local_vars = match_rule[2]
            pattern = re.compile(r"'(\w+)':\s*(.*?)(?=,\s*'\w+':|}$)", re.DOTALL)

            matches = pattern.findall(local_vars)

            result_dict = {key: value for key, value in matches}
            match_results.append(result_dict)
        final_result = match_results[-1]
        for key in input_vars_key:
            input_vars[key] = final_result[key]
    else:
        return input_prompt, population.is_dsc_solve 
    LOG.info("************************ MATCH RESULTS **********************")
    LOG.info(match_results)
    print("********************** expr ***************************")
    print(expr)
    print("************************* input vars ************************")
    print(input_vars)
    print("*********************** input_vars_key *****************************")
    print(input_vars_key)
    variable_types = infer_variable_types(expr)
    if variable_types is None:
        return input_prompt, population.is_dsc_solve 
    z3_vars = []
    for var, type_ in variable_types.items():
        if type_ != 'Bool':
            z3_vars.append(var)
    common_substrings = {}
    for key in z3_vars:
        common_substrings[key] = []
    for match_result in match_results:
        for key in z3_vars:
            if len(input_prompt) > len(match_result[key]):
                common_substrings[key].append(fuzzy_search(input_prompt, match_result[key]))
            else:
                common_substrings[key].append(longest_common_substring(input_prompt, match_result[key]))
    for key in common_substrings:
        common_substrings[key].sort(key=len, reverse=True)
            # print(key, ": ", match_result[key])
    corret_payload = get_conbyte_result(input_vars, function_code)
    print(corret_payload)
    if not isinstance(corret_payload, dict):
        LAST_COMMON_SUBSTRING = common_substrings
        LAST_CORRECT_PAYLOAD = corret_payload
        LOG.info("***************************  NEW PROMPT **************************")
        LOG.info(input_prompt)
        return input_prompt, population.is_dsc_solve 
    # last if rule need to solve dsc
    if match_index == len(IF_RULE) - 1 and not is_dsc_solve:
        for key in z3_vars:
            if key not in corret_payload:
                continue
            corret_payload[key] = solve_dsc(dsc_rule, corret_payload[key])
        population.is_dsc_solve = True

    for key in z3_vars:
        if key not in corret_payload:
            continue
        input_prompt = input_prompt.replace(clean_text(common_substrings[key][0]), corret_payload[key])
    LOG.info("***************************  NEW PROMPT **************************")
    LOG.info(input_prompt)

    LAST_COMMON_SUBSTRING = common_substrings
    LAST_CORRECT_PAYLOAD = corret_payload

    return input_prompt, population.is_dsc_solve 


def solve_dsc_in_sink(prompt: str):
    LOG.info("solve_dsc_in_sink")
    match_oracle_rules = []
    final_match_oracle = []
    match_rule = {}
    if is_windows():
        with open(WIN_ORACLE_FILE_PATH,'r',encoding="utf8") as f:
            try:
                contents = f.read().split("<=======================>\n")[1:]
            except Exception as e:
                contents = []
    else:
        with open(ORACLE_FILE_PATH,'r') as f:
            try:
                contents = f.read().split("<=======================>\n")[1:]
            except Exception as e:
                contents = []

    for match in contents:
        match_oracle_rules.append(match.split('\n'))

    for index in range(len(ORACLE_RULE)):
        rule = ORACLE_RULE[index]
        for match_oracle in match_oracle_rules:
            if len(match_oracle) > 1:
                if match_oracle[-2] == f'{rule["sink"]}@{rule["file_path"]}:{rule["line"]}':
                    final_match_oracle = match_oracle
                    match_rule = rule
                    break

    var = ("\n".join(final_match_oracle[0:-2]))

    if match_rule["sink"] in ["eval", "exec"]:
        var = var[2:-1]
        if len(prompt) > len(var):
                common_prompt = fuzzy_search(prompt, var)
        else:
                common_prompt = longest_common_substring(var, prompt)

        correct_payload = solve_dsc(DSC_RULE, clean_text(common_prompt))
        return prompt.replace(clean_text(common_prompt), correct_payload)


    else:
        if "expr" in match_rule:
            variable_types = infer_variable_types(match_rule["expr"])
            if variable_types is None:
                return
            sink_vars = []
            for var_, type_ in variable_types.items():
                if type_ != 'Bool':
                    sink_vars.append(var_)
            pattern = re.compile(r"'(\w+)':\s*(.*?)(?=,\s*'\w+':|}$)", re.DOTALL)
            matches = pattern.findall(var)
            local_var_dict = {key: value for key, value in matches}
            common_prompts = []
            for sink in sink_vars:
                if sink in local_var_dict:
                    match_var = local_var_dict[sink]
                    match_var = match_var.strip()
                    if match_var.startswith("<") and match_var.endswith(">"):
                        continue
                if len(prompt) > len(match_var):
                    common_prompts.append(fuzzy_search(prompt, match_var))
                else:
                    common_prompts.append(longest_common_substring(match_var, prompt))
            if len(common_prompts) < 1:
                LOG.error("There is no common substring in prompt")
                return prompt
            common_prompts.sort(key=len, reverse=True)
            common_prompt = common_prompts[0]
            if clean_text(common_prompt) in prompt:
                correct_payload = solve_dsc(DSC_RULE, clean_text(common_prompt))
                return prompt.replace(clean_text(common_prompt), correct_payload)

    return prompt


def get_poc_prompt(prompt: str, final_match_oracle, match_rule):
    LOG.info("get_poc_prompt")

    var = ("\n".join(final_match_oracle[0:-2]))

    if match_rule["sink"] in ["eval", "exec"]:
        var = var[2:-1]
        if len(prompt) > len(var):
            common_prompt = fuzzy_search(prompt, var)
        else:
            common_prompt = longest_common_substring(prompt, var)
        return prompt.replace(clean_text(common_prompt), " print(1) # " + clean_text(common_prompt))


    else:
        if "expr" in match_rule:
            variable_types = infer_variable_types(match_rule["expr"])
            if variable_types is None:
                return
            sink_vars = []
            for var_, type_ in variable_types.items():
                if type_ != 'Bool':
                    sink_vars.append(var_)
            pattern = re.compile(r"'(\w+)':\s*(.*?)(?=,\s*'\w+':|}$)", re.DOTALL)
            matches = pattern.findall(var)
            local_var_dict = {key: value for key, value in matches}
            common_prompts = []
            for sink in local_var_dict:
                # If the sink is not subprocess.run, submit, or os.system,
                # then the input parameters of the function must contain payload,
                # so filtering out cases where local variables are not inputted into the function.
                if not sink in sink_vars and not any(keyword in match_rule["sink"] for keyword in ["submit", "run", "system", "load", "GitLoader", "request", "connection"]):
                    continue

                match_var = local_var_dict[sink]
                match_var = match_var.strip()
                if match_var.startswith("<") and match_var.endswith(">"):
                    continue
                if len(prompt) > len(match_var):
                    common_prompts.append(fuzzy_search(prompt, match_var))
                else:
                    common_prompts.append(longest_common_substring(match_var, prompt))

            if len(common_prompts) < 1:
                LOG.error("There is no common substring in prompt")
                return prompt
            common_prompts.sort(key=len, reverse=True)
            common_prompt = common_prompts[0]
            if clean_text(common_prompt) in prompt:
                if any(keyword in match_rule["sink"] for keyword in ["submit", "run", "system"]) and not "crawler" in match_rule["sink"] and not "python" in match_rule["sink"] and not "run_cell" in match_rule["sink"]:
                    return prompt.replace(clean_text(common_prompt), " echo 1 # " + clean_text(common_prompt))
                elif any(keyword in match_rule["sink"] for keyword in ["post", "get", "request"]) or "crawler" in match_rule["sink"] or "GitLoader" in match_rule["sink"] or "loader.load" in match_rule["sink"]:
                    return prompt.replace(clean_text(common_prompt), " 127.0.0.1:1234 ")
                elif "jinja" in match_rule["sink"]:
                    return prompt.replace(clean_text(common_prompt), " {{ print(1) }} ")
                elif any(keyword in match_rule["sink"] for keyword in ["invoke"]) or "connection.execute" == match_rule["sink"]:
                    return prompt.replace(clean_text(common_prompt), " select 1 -- " + clean_text(common_prompt))
                else:
                    return prompt.replace(clean_text(common_prompt), " print(1) # " + clean_text(common_prompt))
            LOG.info("********************* local_var_dict ***************************")
            LOG.info(local_var_dict)
            LOG.info("********************* common_prompt ****************************")
            LOG.info(common_prompt)
            LOG.info(clean_text(common_prompt))
    return prompt


def get_initial_chromosome(target_chain):
    chromosome = Chromosome()

    result = llmchain.run(input=INIT_PROMPT_TEMPLETE.format(target_chain))
    # LOG.info("********************************* result prompt **************************************")
    # print(result)
    LOG.info(f"init token usage: {openai_callback.total_tokens}")
    agent_input_prompt = output_parser(result)
    chromosome.input_prompt = INIT_PROMPT_TEMPLETE.format(target_chain)
    chromosome.llm_response = result
    chromosome.agent_input_prompt = agent_input_prompt
    chromosome.target_call_chain = target_chain
    return chromosome


def get_chromosome(prompt,target_call_chain):
    chromosome = Chromosome()
    # LOG.info("********************************* seed prompt **************************************")
    # LOG.info(prompt)
    result = gpt_4o_mini_api(prompt)
    # LOG.info("********************************* result prompt **************************************")
    # print(result)
    agent_input_prompt = mutate_output_parser(result)
    chromosome.input_prompt = prompt
    chromosome.llm_response = result
    chromosome.agent_input_prompt = agent_input_prompt
    chromosome.target_call_chain = target_call_chain
    return chromosome


def send(content: str):
    # Remove curly braces to avoid template parsing errors in f-string format.
    if content:
        content = content.replace("{", "").replace("}", "")
    try:
        if inspect.iscoroutinefunction(connect_with_auth):
            asyncio.get_event_loop().run_until_complete(connect_with_auth(content))
        else:
            connect_with_auth(content)
    except Exception as e:
        print(e)

def clean_call_stack(container_name):
    global CALL_STACK_FILE_PATH, HOOK_FILE_PATH
    global IF_FILE_PATH, ORACLE_FILE_PATH
    global WIN_HOOK_FILE_PATH, WIN_IF_FILE_PATH, WIN_ORACLE_FILE_PATH
    global OUTPUT
    WIN_HOOK_FILE_PATH = os.path.join(OUTPUT, os.path.basename(HOOK_FILE_PATH))
    WIN_IF_FILE_PATH = os.path.join(OUTPUT, os.path.basename(WIN_HOOK_FILE_PATH))
    WIN_ORACLE_FILE_PATH = os.path.join(OUTPUT, os.path.basename(ORACLE_FILE_PATH))

    if len(container_name) > 0:
        os.system(f"docker exec {container_name} rm {HOOK_FILE_PATH}")
        time.sleep(0.5)
        os.system(f"docker exec {container_name} rm {CALL_STACK_FILE_PATH}")
        time.sleep(0.5)
        os.system(f"docker exec {container_name} rm {IF_FILE_PATH}")
        time.sleep(0.5)
        os.system(f"docker exec {container_name} rm {ORACLE_FILE_PATH}")
        time.sleep(0.5)

        os.system(f"docker exec {container_name} touch {IF_FILE_PATH}")
        time.sleep(0.5)
        os.system(f"docker exec {container_name} touch {HOOK_FILE_PATH}")
        time.sleep(0.5)
        os.system(f"docker exec {container_name} touch {ORACLE_FILE_PATH}")
    else:
        os.system(f"rm {HOOK_FILE_PATH}")
        os.system(f"rm {CALL_STACK_FILE_PATH}")
        os.system(f"rm {IF_FILE_PATH}")
        os.system(f"rm {ORACLE_FILE_PATH}")
        os.system(f"touch {IF_FILE_PATH}")
        os.system(f"touch {HOOK_FILE_PATH}")
        os.system(f"touch {ORACLE_FILE_PATH}")

def get_result(container_name):
    global CALL_STACK_FILE_PATH, HOOK_FILE_PATH
    global WIN_CALL_STACK_FILE_PATH, WIN_HOOK_FILE_PATH
    global IF_FILE_PATH, IF_RULE, ORACLE_FILE_PATH, ORACLE_RULE
    global WIN_IF_FILE_PATH, WIN_ORACLE_FILE_PATH
    global OUTPUT
    WIN_HOOK_FILE_PATH = os.path.join(OUTPUT, os.path.basename(HOOK_FILE_PATH))
    WIN_IF_FILE_PATH = os.path.join(OUTPUT, os.path.basename(IF_FILE_PATH))
    WIN_ORACLE_FILE_PATH = os.path.join(OUTPUT, os.path.basename(ORACLE_FILE_PATH))

    WIN_CALL_STACK_FILE_PATH = os.path.join(OUTPUT, os.path.basename(CALL_STACK_FILE_PATH))
    WIN_HOOK_FILE_PATH = os.path.join(OUTPUT, os.path.basename(HOOK_FILE_PATH))

    if len(container_name) > 0:
        if is_windows():
            os.system(f"type nul > {WIN_CALL_STACK_FILE_PATH}")
            os.system(f"type nul > {WIN_HOOK_FILE_PATH}")
            os.system(f"docker cp {container_name}:{CALL_STACK_FILE_PATH} {WIN_CALL_STACK_FILE_PATH}")
            os.system(f"docker cp {container_name}:{HOOK_FILE_PATH} {WIN_HOOK_FILE_PATH}")
            os.system(f"docker cp {container_name}:{IF_FILE_PATH} {WIN_IF_FILE_PATH}")
            os.system(f"docker cp {container_name}:{ORACLE_FILE_PATH} {WIN_ORACLE_FILE_PATH}")
        else:
            os.system(f"docker exec {container_name} cat {CALL_STACK_FILE_PATH} > {CALL_STACK_FILE_PATH} && chmod a+rw {CALL_STACK_FILE_PATH}")
            os.system(f"docker exec {container_name} cat {HOOK_FILE_PATH} > {HOOK_FILE_PATH} && chmod a+rw {HOOK_FILE_PATH}")
            os.system(f"docker exec {container_name} cat {IF_FILE_PATH} > {IF_FILE_PATH} && chmod a+rw {IF_FILE_PATH}")
            os.system(f"docker exec {container_name} cat {ORACLE_FILE_PATH} > {ORACLE_FILE_PATH} && chmod a+rw {ORACLE_FILE_PATH}")



def is_windows():
    return platform.system() == "Windows"

def get_call_stack_and_oracle(container_name, target_call_chain):
    global CALL_STACK_FILE_PATH, HOOK_FILE_PATH
    global WIN_CALL_STACK_FILE_PATH, WIN_HOOK_FILE_PATH
    global OUTPUT

    WIN_CALL_STACK_FILE_PATH = os.path.join(OUTPUT, os.path.basename(CALL_STACK_FILE_PATH))
    WIN_HOOK_FILE_PATH = os.path.join(OUTPUT, os.path.basename(HOOK_FILE_PATH))

    if is_windows():
        with open(WIN_CALL_STACK_FILE_PATH, 'r', encoding="utf8") as f:
            content = f.readlines()
    else:
        with open(CALL_STACK_FILE_PATH,'r') as f:
            content = f.readlines()
    call_stack = [oneline.replace('\n',"").strip() for oneline in content]
    call_stack = ",  ".join(call_stack)
    if is_windows():
        with open(WIN_HOOK_FILE_PATH, 'r', encoding="utf8") as f:
            content = f.readlines()
    else:
        with open(HOOK_FILE_PATH,'r') as f:
            content = f.readlines()
    content = [oneline.replace("\n","") for oneline in content]
    # LOG.info("********************************* match function **************************************")
    # LOG.info(content)
    # LOG.info("********************************** function call ********************************")
    functions_call = [function_call.strip() for function_call in target_call_chain.split('->')[:-1]]
    # LOG.info(functions_call)
    for function in functions_call:
        for oneline in content:
            if oneline.endswith(function):
                return call_stack, True
    return call_stack, False


def get_if_and_oracle(container_name, target_call_chain):
    global HOOK_FILE_PATH, IF_FILE_PATH, IF_RULE, ORACLE_FILE_PATH, ORACLE_RULE
    global WIN_HOOK_FILE_PATH, WIN_IF_FILE_PATH, WIN_ORACLE_FILE_PATH,IF_RULE_PATH
    global OUTPUT
    WIN_HOOK_FILE_PATH = os.path.join(OUTPUT, os.path.basename(HOOK_FILE_PATH))
    WIN_IF_FILE_PATH = os.path.join(OUTPUT, os.path.basename(IF_FILE_PATH))
    WIN_ORACLE_FILE_PATH = os.path.join(OUTPUT, os.path.basename(ORACLE_FILE_PATH))

    with open(IF_RULE_PATH,'r')as f:
        content = json.load(f)
    IF_RULE = content.get(target_call_chain,[])

    if len(container_name) > 0:
        if is_windows():
            os.system(f"docker cp {container_name}:{HOOK_FILE_PATH} {WIN_HOOK_FILE_PATH}")
            os.system(f"docker cp {container_name}:{IF_FILE_PATH} {WIN_IF_FILE_PATH}")
            os.system(f"docker cp {container_name}:{ORACLE_FILE_PATH} {WIN_ORACLE_FILE_PATH}")
        else:
            os.system(f"docker exec {container_name} cat {HOOK_FILE_PATH} > {HOOK_FILE_PATH} && chmod a+rw {HOOK_FILE_PATH}")
            os.system(f"docker exec {container_name} cat {IF_FILE_PATH} > {IF_FILE_PATH} && chmod a+rw {IF_FILE_PATH}")
            os.system(f"docker exec {container_name} cat {ORACLE_FILE_PATH} > {ORACLE_FILE_PATH} && chmod a+rw {ORACLE_FILE_PATH}")
    match_oracle_rules = []
    if is_windows():
        with open(WIN_ORACLE_FILE_PATH,'r', encoding="utf-8") as f:
            try:
                contents = f.read().split("<=======================>\n")[1:]
            except Exception as e:
                contents = []
    else:
        with open(ORACLE_FILE_PATH,'r') as f:
            try:
                contents = f.read().split("<=======================>\n")[1:]
            except Exception as e:
                contents = []

    for match in contents:
        match_oracle_rules.append(match.split('\n'))

    for index in range(len(ORACLE_RULE)):
        rule = ORACLE_RULE[index]
        for match_oracle in match_oracle_rules:
            if len(match_oracle) > 1:
                if match_oracle[-2] == f'{rule["sink"]}@{rule["file_path"]}:{rule["line"]}':
                    final_match_oracle = match_oracle
                    match_oracle_rule = rule
                    return -1, [], True, final_match_oracle, match_oracle_rule

    if is_windows():
        with open(WIN_HOOK_FILE_PATH,'r', encoding="utf8") as f:
            content = f.readlines()
    else:
        with open(HOOK_FILE_PATH,'r') as f:
            content = f.readlines()
    content = [oneline.replace("\n","") for oneline in content]

    if is_windows():
        with open(WIN_IF_FILE_PATH,'r', encoding="utf8") as f:
            try:
                if_content = f.read().split("match: ")
            except Exception as e:
                if_content = []
    else:
        with open(IF_FILE_PATH,'r') as f:
            try:
                if_content = f.read().split("match: ")
            except Exception as e:
                if_content = []
    match_if_rules = []
    for match_if_rule in if_content:
        match_if_rules.append(match_if_rule.split("\n"))
    match_index = -1
    match_rule = []
    for index in range(len(IF_RULE)):
        rule = IF_RULE[index]
        for match_if_rule in match_if_rules:
            if match_if_rule[0] == f'{rule["file_path"]}:L{rule["start_line"]}, {rule["func_name"]}':
                if match_index < index:
                    match_index = index
                    match_rule = []
                match_rule.append(match_if_rule)

    return match_index, match_rule, False,[],{}


def send_and_get_result(agent_input_prompt:str, target_call_chain: str, container_name: str):

    # Clean the hook match result and call stac
    LOG.info("clean call stack")
    clean_call_stack(container_name)
    LOG.info("send request")
    # Send prompt to agent
    LOG.info("*************************** Agent Input *****************************")
    time.sleep(5)
    LOG.info(agent_input_prompt)

    response = send(agent_input_prompt)
    get_result(container_name)
    LOG.info("get response")
    
    # Read file from container
    call_stack, is_semantic_success = get_call_stack_and_oracle(container_name, target_call_chain)
    match_index, match_rule, is_successful,final_match_oracle, match_oracle_rule = get_if_and_oracle(container_name, target_call_chain)
    return call_stack, is_semantic_success, is_successful, match_index, match_rule, final_match_oracle, match_oracle_rule


def attack(chromosome: Chromosome, target_call_chain: str, container_name: str) -> Chromosome:
    call_stack, is_semantic_success, is_success, match_index, match_rules, final_match_oracle, match_oracle_rule = send_and_get_result(chromosome.agent_input_prompt, target_call_chain, container_name)
    chromosome.call_stack = call_stack
    chromosome.is_successful = is_success
    chromosome.is_semantic_success = is_semantic_success
    chromosome.match_index = match_index
    chromosome.match_rules = match_rules
    chromosome.final_match_oracle = final_match_oracle
    chromosome.match_oracle_rule = match_oracle_rule
    LOG.info("************************************   is_semantic_success   ******************************************")
    LOG.info(is_semantic_success)
    LOG.info("************************************   match_rules   ******************************************")
    LOG.info(match_rules)
    LOG.info("**********************************    is success    ****************************************")
    LOG.info(is_success)
    chromosome.similarity_score, chromosome.similarity_score_reason = get_similarity_score(target_call_chain, chromosome.agent_input_prompt, call_stack)
    chromosome.distance_score = get_distance_score(target_call_chain, call_stack)
    return chromosome



def mutate(chromosome: Chromosome, target_call_chain: str) -> Chromosome:
    LOG.info("********************************** BEGIN TO MUTATE ************************************")
    new_chromosome = get_chromosome(MUTATE_TEMPLATE.format(target_call_chain, chromosome.agent_input_prompt, chromosome.fitness_score),target_call_chain)
    LOG.info("******************************** NEW PROMPT ***************************************")
    LOG.info(new_chromosome.agent_input_prompt)
    return new_chromosome



def seed_generation(target_call_chain, container_name, hook_file_name, call_stack_file_name,
                     injected_connect_with_auth, oracle_config_path):
    global connect_with_auth, DSC_FILE_PATH,Timer
    connect_with_auth = injected_connect_with_auth
    global HOOK_FILE_PATH, CALL_STACK_FILE_PATH
    HOOK_FILE_PATH = hook_file_name
    CALL_STACK_FILE_PATH = call_stack_file_name
    population = []
    all_population = []


    with open(oracle_config_path,'r')as f:
        oracle_content = json.load(f)
    sink_configs = oracle_content.get(target_call_chain,[])
    all_call_chain = set()

    # Get all the call chain related to the target call chain's sink.
    for call_chain in oracle_content:
        tmp_sink_configs = oracle_content[call_chain]
        for sink_config in sink_configs:
            for tmp_sink_config in tmp_sink_configs:
                if tmp_sink_config == sink_config:
                    all_call_chain.add(call_chain)
                    break
    not_final_call_chain = []
    for call_chain in all_call_chain:
        for call_chain2 in all_call_chain:
            if call_chain2 == call_chain:
                continue
            if call_chain in call_chain2:
                not_final_call_chain.append(call_chain)
                break
    final_call_chain = set()
    for call_chain in all_call_chain:
        if call_chain not in not_final_call_chain:
            final_call_chain.add(call_chain)

    # Initial seed
    LOG.info("begin to init")
    for new_target_call_chain in final_call_chain:
        with open(DSC_FILE_PATH,'r') as f:
            content = json.load(f)
        dsc_rule = content.get(new_target_call_chain,[])
        LOG.info("begin to init")
        for _ in range(1):
            population = get_initial_chromosome(new_target_call_chain)
            population.dsc_constraint = dsc_rule
            LOG.info("get prompt")
            seed = attack(population, new_target_call_chain, container_name)
            if Timer:
                return None, None
            all_population.append(seed)

    LOG.info("get prompt")
    for seed in all_population:
        SEED_POOL.append(seed)

    return None, False

def seed_scheduling() -> Chromosome:
    global SEED_POOL

    for seed in SEED_POOL:
        seed.final_score = seed.similarity_score + seed.distance_score -seed.select_penalty_score - seed.callchain_penalty_score
    SEED_POOL = sorted(SEED_POOL, key=lambda x: x.final_score, reverse=True)
    selected_seed = SEED_POOL[0]
    selected_seed.select_penalty_score += 0.5
    for seed in SEED_POOL:
        if seed.target_call_chain == selected_seed:
            seed.callchain_penalty_score += 0.5
    new_seed = copy.deepcopy(selected_seed)
    new_seed.select_penalty_score = 0
    return new_seed


def mutator(container_name, iteration_limit):
    iteration = 0
    global SEED_POOL, Timer

    while iteration < iteration_limit:
        iteration += 1

        population = seed_scheduling()
        if Timer:
            return "", False
        # Add poc
        if population.is_successful:
            new_prompt = get_poc_prompt(population.agent_input_prompt, population.final_match_oracle, population.match_oracle_rule)
            population.agent_input_prompt = new_prompt
            new_population = attack(population, population.target_call_chain, container_name)
            if new_population.is_successful:
                return new_population.agent_input_prompt, new_population.is_successful
            else:
                SEED_POOL.append(new_population)
                continue


        if Timer:
            return "", False
        mutator = mutator_scheduling(population)
        print(mutator)
        if "variable" in mutator.lower():
            # Variable mutator
            population.agent_input_prompt, population.is_dsc_solve = solve_and_get_new_prompt(population)
            new_population = attack(population, population.target_call_chain, container_name)
            SEED_POOL.append(new_population)

            continue
        
        else: 
            # Semantic mutator
            new_population, is_semantic_success, is_success= prompt_mutate(population, container_name)
            SEED_POOL.append(new_population)
            continue


    return "", False

def mutator_scheduling(population: Chromosome):
    dominatif = "DOMINANT CONDITION STATEMENT: + \n"
    for rule in population.match_rules:
        dominatif += str(rule[0]) + "\n"
    dominatif += "DATAFLOW CONSTRAINT: + \n"
    dominatif += str(population.dsc_constraint) + '\n'
    feedback = "Semantic Score: {}\n Distance Score: {} \n".format(population.similarity_score, population.distance_score)
    feedback += "Semantic Score Reason: {}\n".format(population.similarity_score_reason)
    res = scheduling_conversationchain.invoke({"input": SCHEDULING_PROMPT.format(dominatif, population.match_rules, feedback)})
    LOG.info(f"mutate token usage: {openai_callback.total_tokens}")
    return res['response']

def prompt_mutate(final_population: Chromosome, container_name):

    target_call_chain = final_population.target_call_chain


    final_population = mutate(final_population, target_call_chain)

    final_population = attack(final_population, target_call_chain, container_name)

    if final_population.is_semantic_success:
        return final_population, True, final_population.is_successful

    return final_population, False, final_population.is_successful


def timmer():
    global Timer
    time.sleep(300)  
    Timer = True

def fuzzing(target_call_chain, container_name, iteration, hook_file_name, call_stack_file_name,
                     injected_connect_with_auth, oracle_config_path, if_file_name, if_rule_path, oracle_file_path,dsc_config_path):
    global Timer
    thread = threading.Thread(target=timmer)
    thread.start()
    global connect_with_auth
    connect_with_auth = injected_connect_with_auth
    global HOOK_FILE_PATH, CALL_STACK_FILE_PATH
    HOOK_FILE_PATH = hook_file_name
    CALL_STACK_FILE_PATH = call_stack_file_name
    global IF_FILE_PATH, IF_RULE, ORACLE_FILE_PATH, ORACLE_RULE, DSC_RULE, DSC_FILE_PATH, IF_RULE_PATH
    IF_RULE_PATH = if_rule_path
    IF_FILE_PATH = if_file_name
    ORACLE_FILE_PATH = oracle_file_path
    DSC_FILE_PATH = dsc_config_path
    with open(IF_RULE_PATH,'r')as f:
        content = json.load(f)
    IF_RULE = content.get(target_call_chain,[])

    with open(oracle_config_path,'r')as f:
        content = json.load(f)
    ORACLE_RULE = content.get(target_call_chain,[])


    LOG.info("begin to get prompt template")

    # Initialization
    population, is_success = seed_generation(target_call_chain, container_name, hook_file_name, call_stack_file_name,
                                             injected_connect_with_auth, oracle_config_path)
    if is_success is not None:
        if is_success:
            new_prompt = get_poc_prompt(population.agent_input_prompt,population.final_match_oracle, population.match_oracle_rule)
            population.agent_input_prompt = new_prompt
            new_population = attack(population, population.target_call_chain, container_name)
            return population.agent_input_prompt, new_population.is_successful

        if not Timer:
            mutator_result = mutator(container_name, iteration)
    return mutator_result




if __name__ == '__main__':
    fuzzing(sys.argv[1:])
