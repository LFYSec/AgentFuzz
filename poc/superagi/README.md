before run this poc, you need to change the source code of superagi, because of the [issue](https://github.com/TransformerOptimus/SuperAGI/issues/1438)

in docker `superagi-backend-1` /app/superagi/agent/output_handler.py and get_output_handler function. After modifying, you need to restart  both `superagi-backend-1` and `superagi-celery-1`

Origin:

<<<
```python
def get_output_handler(output_type: str, agent_execution_id: int, agent_config: dict, agent_tools: list = [],memory=None):
    if output_type == "tools":
        return ToolOutputHandler(agent_execution_id, agent_config, agent_tools,memory=memory)
    elif output_type == "replace_tasks":
        return ReplaceTaskOutputHandler(agent_execution_id, agent_config)
    elif output_type == "tasks":
        return TaskOutputHandler(agent_execution_id, agent_config)
    return ToolOutputHandler(agent_execution_id, agent_config, agent_tools,memory=memory)
```
---
New:
>>>

```python
def get_output_handler(output_type: str, agent_execution_id: int, agent_config: dict, agent_tools: list = [],memory=None):

    return ReplaceTaskOutputHandler(agent_execution_id, agent_config)
    return ToolOutputHandler(agent_execution_id, agent_config, agent_tools,memory=memory)
```

