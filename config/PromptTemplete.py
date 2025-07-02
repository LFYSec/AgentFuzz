INIT_PROMPT_TEMPLETE = """
You are a person who is very familiar with prompt design and can generate a prompt to help LLM perform specific tasks.
Now you need to design a prompt that conforms to the Component semantics based on the call chain of a Component, which can guide LLM to call this Component, and give the reason for your design of this prompt.
Here are something you have to think about. You must think about them step-by-step carefuly and don't skip any step!
- First, you need to infer the function of this component based on the content of the call chain.
- Secondly, you need to generate a prompt with similar semantics to the component.
- Finally, you need to check whether the generated prompt is similar to the component semantics. If not, modify it.
ATTENTION! When you are editing, you need to fill in all the content instead of leaving space for me to fill in!!



The output format needs to meet:
- CoT: ...  # the reason why you generated the prompt.
- Prompt: 
        ```text
            ... # the prompt you generated.
        ```

Now here is a example you can follow:
@EXAMPLE
    INPUT:
        - Call Chain: <begin>  calculator -> eval  <end>
    
    OUTPUT:
        - CoT:
            1. Identify the function of the component based on the call chain. The call chain "<begin> calculator -> eval <end>" suggests that the component is designed to evaluate mathematical expressions.
            2. The prompt should instruct the LLM to use the calculator component to perform an evaluation, which aligns with the function inferred from the call chain.
            3. The prompt should clearly specify a mathematical expression for evaluation to ensure it is directly related to the component's purpose.

        - Prompt:
            ```text
            Please use the calculator to evaluate the following mathematical expression: 3 * (4 + 5).
            ```
@END EXAMPLE


Here is the call chain of the Component:
    - Call Chain: <begin> {} <end>

"""

SCORE_PROMPT = """

You are tasked with evaluating whether the prompt semantics can correctly trigger the target component for the agent. Follow these steps carefully:
Infer Component Function: Based on the content of the call chain, determine the function of the target component.
Infer Prompt Semantics: Analyze the seed prompt and execution trace to infer the current prompt semantics.
Rate Prompt Semantics: Once you have a clear understanding of the target component and the corresponding call chain, rate the current prompt semantics.

Scoring Criteria:
Rate the prompt semantics on a scale of 0 to 10, using the following guidelines:
10 (Fully Aligned): The prompt perfectly triggers components in the call chain, meaning the execution trace contains components that are present in the call chain.
8-9 (High Semantic Match): The prompt does not directly trigger any component in the call chain, but the triggered execution trace is semantically close to the target component, and the prompt is also semantically close to the target component.
6-7 (Moderate Semantic Match): The prompt does not trigger any components in the call chain, but the semantics of the triggered execution trace and the prompt show some similarity to the target component.
4-5 (Low Semantic Match): The prompt does not trigger any components in the call chain, and there is a low degree of semantic similarity between the triggered execution trace and the target component.
1-3 (Minimal Semantic Match): The prompt does not trigger any components in the call chain, and the semantics of the triggered execution trace and prompt have very little similarity to the target component.
0 (Completely Unrelated): The prompt does not trigger any components in the call chain, and the semantics of the triggered execution trace and prompt are entirely unrelated to the target component.

The output format needs to meet:
<SCORE> ... <ENDSCORE>
<SCOREREASON> ... <ENDSCOREREASON>

The input format is:
<TARGETCALLCHAIN> ... <ENDTARGETCALLCHAIN>
<PROMPT> ... <ENDPROMPT>
<EXECUTIONTRACE> ... <ENDEXECUTIONTRACE>

Now here are some examples you can follow:
@EXAMPLE
- Example 1
    INPUT:
        <TARGETCALLCHAIN>  ElasticKeywordsSearch.similarity_search -> ElasticKeywordsSearch.similarity_search_with_score -> eval  <ENDTARGETCALLCHAIN>
        <PROMPT> Please perform a similarity search using the ElasticKeywordsSearch component for the keywords "machine learning" and return the results along with their scores. After retrieving the results, evaluate their relevance. <ENDPROMPT>
        <EXECUTIONTRACE>   ElasticKeywordsSearch.__init__,  ElasticKeywordsSearch.add_texts,  _default_text_mapping,  VectorStoreVertex._update_built_object_and_artifacts,  VectorStoreVertex._validate_built_object,  VectorStoreVertex._built_object_repr,  ChainVertex.build,  ChainVertex._build,  ChainVertex._build_each_node_in_params_dict,  ChainVertex._is_node,  ChainVertex._build_node_and_update_params,  ChainVertex._handle_func,  ChainVertex._is_dict_of_nodes,  ChainVertex._get_and_instantiate_class,  initialize,  load_qa_chain,  _load_stuff_chain,  ChainVertex._update_built_object_and_artifacts,  ChainVertex._validate_built_object,  ChainVertex._built_object_repr,  ChainVertex.__eq__,  ChainVertex.get_result,  VectorStoreVertex.__eq__,  VectorStoreVertex.get_result,  import_chain,  instantiate_chains,  Graph.abuild,  get_root_vertex,  AssistantAgent.init_agent,  ConfigurableAssistant.__init__,  LiberalFunctionMessage,  LiberalToolMessage,  get_react_agent_executor,  create_agent_executor,  _get_agent_state,  AgentState,  AssistantAgent.run,  AssistantAgent.fake_callback, AssistantAgent.react_run,  arun_agent,  BishengLLM._llm_type,  BishengLLM.bisheng_model_limit_check,  BishengLLM._agenerate,  BishengLLM._update_model_status,  update_model_status,  should_continue,  aexecute_tools,  ElasticKeywordsSearch.similarity_search,  ElasticKeywordsSearch.similarity_search_with_score,  BishengLLM._generate,  ElasticKeywordsSearch.client_search,  StuffDocumentsChain.acombine_docs,  AssistantAgent.record_chat_history,  _event_stream   <ENDEXECUTIONTRACE>
    
    OUTPUT:
        <SCORE> 10 <ENDSCORE>
        <SCOREREASON> The EXECUTIONTRACE contains the  ElasticKeywordsSearch.__init__ which is the same call with the target call chain and also trigger ElasticKeywordsSearch.similarity_search and  ElasticKeywordsSearch.similarity_search_with_score which is the same as traget call chain. The prompt perfectly triggers components in the call chain, meaning the execution trace contains components that are present in the call chain. So, the semantic score is 10<ENDSCOREREASON>

        

Here is the input:
<TARGETCALLCHAIN> {} <ENDTARGETCALLCHAIN>
<PROMPT> {} <ENDPROMPT>
<EXECUTIONTRACE> {} <ENDEXECUTIONTRACE>

"""

SCHEDULING_SYSTEM_PROMPT = """

You are a scheduling system responsible for determining the appropriate mutator to transform a seed so that it successfully triggers the sink. Your decision should be based on the contextual and execution details provided below.  

### Information Provided  

1. **Dominant Conditional Statement**  
   During execution, this is the last significant conditional statement encountered by the agent. If this statement is not satisfied, the execution path will not reach the sink. Analyzing this condition is essential to understanding what constraints the seed must fulfill to achieve its goal.  

2. **Key Variables**  
   These include the critical parameter values during the execution process. Examples include parameters in the dominant conditional statement and data that flows into the sink. These variables play a pivotal role in determining how the seed interacts with the agent's logic and components.  

3. **Feedback**
Feedback encompasses the evaluation of the seed's previous performance and provides key insights to guide the mutator's selection and adjustments. This evaluation typically includes two crucial metrics:
    - Semantic Score: This metric assesses how closely the seed aligns with the intended purpose or function of the sink. A high semantic score indicates a strong alignment with the sink's requirements, suggesting that the seed effectively addresses the contextual or logical nuances needed for the execution to progress. Conversely, a low score may highlight a need for the Semantic Mutator to refine the seed's relevance or clarity.
    - Distance Score: This metric quantifies how far the seed is from satisfying the dominant conditional statement or achieving the execution path leading to the sink. A lower distance score signifies that the seed is closer to fulfilling the necessary conditions, whereas a higher score suggests that adjustments are required to meet these constraints. This score often serves as a primary indicator for deploying the Variable Mutat


### Information About Mutators  

1. **Semantic Mutator**  
   The Semantic Mutator is designed to bridge the semantic gap between the seed prompt and the target component. It adjusts the seed prompt to better align with the functional requirements and intent of the target component, ensuring the prompt is meaningful and relevant within the given context.  

2. **Variable Mutator**  
   The Variable Mutator is crafted to modify the seed prompt or its output to meet specific constraints. It ensures that the LLM's response adheres to conditions necessary for successful execution, such as satisfying the dominant conditional statement or meeting parameter requirements for the sink.  

### Task  
Using the provided information, you must analyze the context and determine whether the **Semantic Mutator** or the **Variable Mutator** (or potentially both) is required to transform the seed effectively and achieve the desired outcome.


the input is:
    <DOMINATANTCONDITINALSTATEMENT> ... <ENDDOMINATANTCONDITINALSTATEMENT>
    <KEYVARIABLES> ... <ENDKEYVARIABLES>
    <FEEDBACK> ... <ENDFEEDBACK>



The output format needs to meet:
    <SEMANTIC MUTATOR> or <VARIABLE MUTATOR>
"""


SCHEDULING_PROMPT = """
Here is the current input:
    <DOMINATANTCONDITINALSTATEMENT> {} <ENDDOMINATANTCONDITINALSTATEMENT>
    <KEYVARIABLES> {} <ENDKEYVARIABLES>
    <FEEDBACK> {} <ENDFEEDBACK>
"""

MUTATE_SYSTEM_PROMPT = """
You are familiar with evaluating whether prompt semantics can trigger the target component for the agent. Here are two task you need to do. You need to do them step-by-step.
First, you need to rate the current prompt semantics based on the call chain that reaches the target component and the call trace that the current agent executes the current prompt. you need to Make sure you understand the semantics about the target component with the target call chain clearly before scoring.
Second, you need to design a prompt that conforms to the Component semantics based on the call chain of a Component, which can guide LLM to call this Component, and give the reason for your design of this prompt. You can refer to the original prompt its rating and the call trace and than make modifications based on it to make the semantics of the prompt more similar to the target call chain, allowing the agent to call components on the call chain.
Attention! If there is past history, you need to refer to it for mutation!
You need to make modifications based on the original prompt, rather than overturning it as a whole and starting over!!


The input is:
    - Target Call Chain: <BEGIN> ... <END>  # The target call chain the original prompt wants to trigger.
    - Current Call Trace: <BEGIN>
        ...
        <END> # The call trace the agent executes the original prompt. Each component is separated by commas.
    - Original Prompt: <BEGIN> ... <END>  # The original prompt.



The output format needs to meet:
<NEWPROMPT>
 ... 
<ENDNEWPROMPT>
<PROMPTREASON>
 ... 
<ENDPROMPTREASON>


"""

MUTATE_EXAMPLE = """
Now here are some examples you can follow:
@EXAMPLE
- Example 1
    INPUT:
        - Target Call Chain: <BEGIN> ElasticKeywordsSearch.similarity_search -> ElasticKeywordsSearch.similarity_search_with_score -> eval <END>
        - Current Call Trace: <BEGIN> 
            CustomMiddleware.dispatch,  assistant_chat_completions,  get_request_ip,  get_default_operator,  Settings.get_from_db,  Settings.get_all_config,  RedisClient.get,  RedisClient.cluster_nodes,  RedisClient.close,  session_getter,  get_user,  UserPayload.__init__,  get_user_roles,  get_assistant_info,  get_one_assistant,  wrapper,  UserPayload.is_admin,  get_assistant_link,  get_link_info,  get_list_by_ids,  get_flow_by_ids,  get_logo_share_link,  validate_json,  resp_200,  AssistantAgent.__init__,  AssistantAgent.init_assistant,  AssistantAgent.init_llm,  get_assistant_llm,  get_config,  get_bisheng_llm,  import_by_type,  import_llm,  LLMCreator.type_to_loader_dict,  instantiate_llm,  BishengLLM.__init__,  get_model_by_id,  get_server_by_id,  BishengLLM._get_llm_class,  import_chat_llm,  BishengLLM._get_llm_params,  InterceptHandler.emit,  AssistantAgent.init_tools,  AssistantAgent.init_preset_tools,  AssistantAgent.parse_tool_params,  Settings.get_knowledge,  load_tools,  _handle_callbacks,  _get_native_code_interpreter,  CodeInterpreterTool.__init__,  CodeInterpreterTool.as_tool,  CodeInterpreterTool.description,  CodeInterpreterTool.file_description,  build_flow_no_yield,  from_payload,  Graph.__init__,  process_flow,  raw_topological_sort,  dfs,  process_node,  Graph._build_graph,  Graph._build_vertices,  Graph._get_vertex_class,  VertexTypesDict.VERTEX_TYPE_MAP,  VertexTypesDict.all_types_dict,  VertexTypesDict._build_dict,  VertexTypesDict.get_type_dict,  PromptCreator.to_list,  get_custom_nodes,  PromptCreator.type_to_loader_dict,  AgentCreator.to_list,  AgentCreator.type_to_loader_dict,  function_name,  ChainCreator.to_list,  ChainCreator.type_to_loader_dict,  ToolCreator.to_list,  ToolCreator.type_to_loader_dict,  ToolkitCreator.to_list,  ToolkitCreator.type_to_loader_dict,  WrapperCreator.to_list,  WrapperCreator.type_to_loader_dict,  LLMCreator.to_list,  MemoryCreator.to_list,  MemoryCreator.type_to_loader_dict, EmbeddingCreator.to_list,  EmbeddingCreator.type_to_loader_dict,  VectorstoreCreator.to_list,  VectorstoreCreator.type_to_loader_dict,  DocumentLoaderCreator.to_list,  DocumentLoaderCreator.type_to_loader_dict,  TextSplitterCreator.to_list,  TextSplitterCreator.type_to_loader_dict,  OutputParserCreator.to_list,  OutputParserCreator.type_to_loader_dict,  RetrieverCreator.to_list,  RetrieverCreator.type_to_loader_dict,  LLMVertex.__init__,  LLMVertex._parse_data,  LLMVertex.set_top_level,  PromptVertex.__init__,  PromptVertex._parse_data,  PromptVertex.set_top_level,  ChainVertex.__init__,  ChainVertex._parse_data,  ChainVertex.set_top_level,  EmbeddingVertex.__init__,  EmbeddingVertex._parse_data,  EmbeddingVertex.set_top_level,  VectorStoreVertex.__init__,  VectorStoreVertex._parse_data,  VectorStoreVertex.set_top_level,  Graph._build_edges,  Graph.get_vertex,  Edge.__init__,  Edge.validate_edge,  Graph._build_vertex_params,  LLMVertex._build_params,  LLMVertex.edges,  Graph.get_vertex_edges,  PromptVertex._build_params,  PromptVertex.edges,  ChainVertex._build_params,  ChainVertex.edges,  VectorStoreVertex.edges,  EmbeddingVertex._build_params,  EmbeddingVertex.edges,  VectorStoreVertex._build_params,  Graph._validate_vertices,  Graph._validate_vertex,  Graph.topological_sort,  LLMVertex.__hash__,  PromptVertex.__hash__,  ChainVertex.__hash__,  EmbeddingVertex.__hash__,  VectorStoreVertex.__hash__,  Graph.dfs,  EmbeddingVertex.build,  EmbeddingVertex._build,  EmbeddingVertex._build_each_node_in_params_dict,  EmbeddingVertex._is_node,  EmbeddingVertex._is_dict_of_nodes,  EmbeddingVertex._get_and_instantiate_class,  instantiate_class,  convert_params_to_sets,  convert_kwargs,  BishengEmbedding.__init__,  BishengEmbedding._get_embedding_class,  import_embedding,  BishengEmbedding._get_embedding_params,  instantiate_embedding,  EmbeddingVertex._update_built_object_and_artifacts,  EmbeddingVertex._validate_built_object,  EmbeddingVertex._built_object_repr,  PromptVertex.build,  extract_input_variables_from_prompt,  PromptVertex._build,  PromptVertex._build_each_node_in_params_dict,  PromptVertex._is_node,  PromptVertex._is_list_of_nodes,  PromptVertex._is_dict_of_nodes,  PromptVertex._get_and_instantiate_class,  import_prompt,  import_class,  import_module,  instantiate_based_on_type,  instantiate_prompt,  handle_node_type,  handle_format_kwargs,  handle_variable,  needs_handle_keys,  is_instance_of_list_or_document,  handle_partial_variables,  PromptVertex._update_built_object_and_artifacts,  PromptVertex._validate_built_object,  PromptVertex._built_object_repr,  LLMVertex.build,  LLMVertex._build,  LLMVertex._build_each_node_in_params_dict,  LLMVertex._is_node,  LLMVertex._is_dict_of_nodes,  LLMVertex._get_and_instantiate_class,  LLMVertex._update_built_object_and_artifacts,  LLMVertex._validate_built_object,  LLMVertex._built_object_repr,  VectorStoreVertex.build,  VectorStoreVertex._build,  VectorStoreVertex._build_each_node_in_params_dict,  VectorStoreVertex._is_node,  EmbeddingVertex.__eq__,  VectorStoreVertex._build_node_and_update_params,  EmbeddingVertex.get_result,  VectorStoreVertex._handle_func,  LLMVertex.__eq__,  LLMVertex.get_result,  PromptVertex.__eq__,  PromptVertex.get_result,  VectorStoreVertex._is_dict_of_nodes,  VectorStoreVertex._get_and_instantiate_class,  import_vectorstore,  instantiate_vectorstore,  initial_elastic,  from_texts,  ElasticKeywordsSearch.__init__,  ElasticKeywordsSearch.add_texts,  _default_text_mapping,  VectorStoreVertex._update_built_object_and_artifacts,  VectorStoreVertex._validate_built_object,  VectorStoreVertex._built_object_repr,  ChainVertex.build,  ChainVertex._build,  ChainVertex._build_each_node_in_params_dict,  ChainVertex._is_node,  ChainVertex._build_node_and_update_params,  ChainVertex._handle_func,  ChainVertex._is_dict_of_nodes,  ChainVertex._get_and_instantiate_class,  initialize,  load_qa_chain,  _load_stuff_chain,  ChainVertex._update_built_object_and_artifacts,  ChainVertex._validate_built_object,  ChainVertex._built_object_repr,  ChainVertex.__eq__,  ChainVertex.get_result,  VectorStoreVertex.__eq__,  VectorStoreVertex.get_result,  import_chain,  instantiate_chains,  Graph.abuild,  get_root_vertex,  AssistantAgent.init_agent,  ConfigurableAssistant.__init__,  LiberalFunctionMessage,  LiberalToolMessage,  get_react_agent_executor,  create_agent_executor,  _get_agent_state,  AgentState,  AssistantAgent.run,  AssistantAgent.fake_callback, AssistantAgent.react_run,  arun_agent,  BishengLLM._llm_type,  BishengLLM.bisheng_model_limit_check,  BishengLLM._agenerate,  BishengLLM._update_model_status,  update_model_status,  should_continue,  aexecute_tools,  ElasticKeywordsSearch.similarity_search,  ElasticKeywordsSearch.similarity_search_with_score,  BishengLLM._generate,  ElasticKeywordsSearch.client_search,  StuffDocumentsChain.acombine_docs,  AssistantAgent.record_chat_history,  _event_stream
            <END>
        - Original Prompt: <BEGIN> Please perform a similarity search using the ElasticKeywordsSearch component for the keywords "machine learning" and return the results along with their scores. After retrieving the results, evaluate their relevance. <END>

    OUTPUT:
        <NEWPROMPT> 
        Please perform a similarity search using the ElasticKeywordsSearch component for the keywords "machine learning" and return the results along with their scores. After retrieving the results, evaluate their relevance. 
        <ENDNEWPROMPT>
        <PROMPTREASON>
            The prompt is already aligned with the target component's functionality, and the score is 10. There is no need for modification. Therefore, the prompt remains unchanged.
        <ENDPROMPTREASON>


 """

MUTATE_TEMPLATE = """
If there is any history, you need to refer to the error situation in history for modification to make the prompt better.

Here is the input:
    - Target Call Chain: <BEGIN> {} <END>
    - Current Call Trace: <BEGIN>
        {}
        <END>
    - Original Prompt: <BEGIN> {} <END>
"""