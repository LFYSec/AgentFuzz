import poc.agentzero.poc
import poc.bisheng.poc
import poc.devika.poc
import poc.ragflow.poc
import poc.openagents.poc
import poc.taskingai.poc
import poc.autogpt.poc
import poc.langflow.poc
import poc.TaskWeaver.poc
import poc.langchainchatchat.poc
import poc.chuanhu.poc
import poc.jarvis.poc
import poc.superagi.poc
import poc.dbgpt.poc
import poc.agentscope.poc
import poc.quivr.poc
import poc.vanna.poc


class MetaData:
    def __init__(self, call_chain: str, container_name: str, oracle_json: str, if_json: str, hook_json: str,
                 dsc_json: str,
                 connect_with_auth):
        self.call_chain = call_chain
        self.container_name = container_name
        self.oracle_json = oracle_json
        self.if_json = if_json
        self.dsc_json = dsc_json
        self.hook_json = hook_json
        self.connect_with_auth = connect_with_auth


def get_metadata(app: str):
    factory = {
        "agentzero": MetaData(
            "WebpageContentTool.execute -> get",
            "agentzero-withoutdocker",
            "output/agentzero/oracle.json",
            "output/agentzero/agentzero-if.json",
            "output/agentzero/enter_hook.json",
            "output/agentzero/agentzero-dsc.json",
            poc.agentzero.poc.connect_with_auth
        ),
        "devika": MetaData(
            "Runner.run_code -> run",
            "devika",
            "output/devika/oracle.json",
            "output/devika/devika-if.json",
            "output/devika/enter_hook.json",
            "output/devika/devika-dsc.json",
            poc.devika.poc.connect_with_auth
        ),
        "ragflow": MetaData(
            "ExeSQL._run -> cursor.execute",
            "ragflow-server",
            "output/ragflow/win/oracle.json",
            "output/ragflow/win/ragflow-if.json",
            "output/ragflow/win/enter_hook.json",
            "output/ragflow/win/ragflow-dsc.json",
            poc.ragflow.poc.connect_with_auth
        ),
        "openagents": MetaData(
            "PythonEvaluator.run -> PythonEvaluator.run_program_local -> ip.run_cell",
            "openagents-backend-1",
            "output/openagents/oracle.json",
            "output/openagents/openagents-if.json",
            "output/openagents/enter_hook.json",
            "output/openagents/openagents-dsc.json",
            poc.openagents.poc.connect_with_auth
        ),
        "taskingai": MetaData(
            "ReadWebPage.execute -> session.get",
            "taskingai-backend-plugin-1",
            "output/TaskingAI/oracle.json",
            "output/TaskingAI/taskingai-if.json",
            "output/TaskingAI/enter_hook.json",
            "output/TaskingAI/taskingai-dsc.json",
            poc.taskingai.poc.connect_with_auth
        ),
        "autogpt": MetaData(
            "SendWebRequestBlock.run -> requests.request",
            "autogpt_platform-executor-1",
            "output/autogpt/oracle.json",
            "output/autogpt/autogpt-if.json",
            "output/autogpt/enter_hook.json",
            "output/autogpt/autogpt-dsc.json",
            poc.autogpt.poc.connect_with_auth
        ),
        "langflow": MetaData(
            "PythonREPLToolComponent.build_tool.run_python_code -> python_repl.run",
            "docker_example-langflow-1",
            "output/langflow/win/oracle.json",
            "output/langflow/win/langflow-if.json",
            "output/langflow/win/enter_hook.json",
            "output/langflow/win/langflow-dsc.json",
            poc.langflow.poc.connect_with_auth
        ),
        "Taskweaver": MetaData(
            "CodeExecutor.execute_code -> execute_code",
            "taskweaver",
            "output/TaskWeaver/oracle.json",
            "output/TaskWeaver/TaskWeaver-if.json",
            "output/TaskWeaver/enter_hook.json",
            "output/TaskWeaver/TaskWeaver-dsc.json",
            poc.TaskWeaver.poc.connect_with_auth
        ),
        "chatchat": MetaData(
            "shell -> run",
            "chatchat",
            "output/Langchain-Chatchat/oracle.json",
            "output/Langchain-Chatchat/Langchain-Chatchat-if.json",
            "output/Langchain-Chatchat/enter_hook.json",
            "output/Langchain-Chatchat/Langchain-Chatchat-dsc.json",
            poc.langchainchatchat.poc.connect_with_auth
        ),
        "chuanhu": MetaData(
            "ChuanhuAgent_Client.summary_url -> ChuanhuAgent_Client.fetch_url_content -> requests.get",
            "",
            "output/chuanhu/win/oracle.json",
            "output/chuanhu/win/chuanhu-if.json",
            "output/chuanhu/win/enter_hook.json",
            "output/chuanhu/win/chuanhu-dsc.json",
            poc.chuanhu.poc.connect_with_auth
        ),
        "jarvis": MetaData(
            "This application does not have any vulnerabilities.",
            "jarvis",
            "output/jarvis/oracle.json",
            "output/jarvis/jarvis-if.json",
            "output/jarvis/enter_hook.json",
            "output/jarvis/jarvis-dsc.json",
            poc.jarvis.poc.connect_with_auth
        ),
        "superagi": MetaData(
            "ReplaceTaskOutputHandler.handle -> eval",
            "superagi-celery-1",
            "output/superagi/oracle.json",
            "output/superagi/superagi-if.json",
            "output/superagi/enter_hook.json",
            "output/superagi/superagi-dsc.json",
            poc.superagi.poc.connect_with_auth
        ),
        "dbgpt": MetaData(
            "CodeAction.run -> CodeAction.execute_code_blocks -> execute_code -> submit",
            "dbgpt-allinone",
            "output/DB-GPT/oracle.json",
            "output/DB-GPT/DB-GPT-if.json",
            "output/DB-GPT/enter_hook.json",
            "output/DB-GPT/DB-GPT-dsc.json",
            poc.dbgpt.poc.connect_with_auth
        ),
        "agentscope": MetaData(
            "_sys_execute -> exec",
            "agentscope",
            "output/agentscope/oracle.json",
            "output/agentscope/agentscope-if.json",
            "output/agentscope/enter_hook.json",
            "output/agentscope/agentscope-dsc.json",
            poc.agentscope.poc.connect_with_auth
        ),
        "quivr": MetaData(
            "",
            "",
            "output/quivr/win/oracle.json",
            "output/quivr/win/quivr-if.json",
            "output/quivr/win/enter_hook.json",
            "output/quivr/win/quivr-dsc.json",
            poc.quivr.poc.connect_with_auth
        ),
        "vanna": MetaData(
            "",
            "",
            "output/vanna/win/oracle.json",
            "output/vanna/win/vanna-if.json",
            "output/vanna/win/enter_hook.json",
            "output/vanna/win/vanna-dsc.json",
            poc.vanna.poc.connect_with_auth
        ),
        "bisheng_win": MetaData(
            "calculator -> eval",
            "bisheng-backend",
            "output/bisheng/win/oracle.json",
            "output/bisheng/win/bisheng-if.json",
            "output/bisheng/win/enter_hook.json",
            "output/bisheng/win/bisheng-dsc.json",
            poc.bisheng.poc.connect_with_auth
        )
    }
    if app not in factory.keys():
        print(f"[*] app: {app} not found, please fill in {__file__}")
        exit(0)
    return factory[app]
