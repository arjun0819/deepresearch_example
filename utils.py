# -*- coding: utf-8 -*-
"""The utilities for deep research agent"""
import os
import json
import re
from typing import Union, Sequence, Any, Type

from pydantic import BaseModel
from agentscope.tool import Toolkit, ToolResponse
TOOL_RESULTS_MAX_WORDS = 5000


def get_prompt_from_file(
    file_path: str,
    return_json: bool,
) -> Union[str, dict]:
    """Get prompt from file"""
    with open(os.path.join(file_path), "r", encoding="utf-8") as f:
        if return_json:
            prompt = json.load(f)
        else:
            prompt = f.read()
    return prompt

def truncate_by_words(sentence: str) -> str:
    """Truncate too long sentences by words number"""
    words = re.findall(
        r"\w+|[^\w\s]",
        sentence,
        re.UNICODE,
    )
    word_count = 0
    result = []
    for word in words:
        if re.match(r"\w+", word):
            word_count += 1
        if word_count > TOOL_RESULTS_MAX_WORDS:
            break
        result.append(word)
        
    truncated_sentence = ""
    for i, word in enumerate(result):
        if i == 0:
            truncated_sentence += word
        elif re.match(r"\w+", word):
            truncated_sentence += " " + word
        else:
            truncated_sentence += word

    return truncated_sentence

def truncate_search_result(
    res: list,
    search_func: str = "tavily-search",
    extract_function: str = "tavily-extract",
) -> list:
    """Truncate search result in deep research agent"""
    if search_func != "tavily-search" or extract_function != "tavily-extract":
        raise NotImplementedError(
        "Specific implementation of truncation should be provided.",
        )
    for i, val in enumerate(res):
        res[i]["text"] = truncate_by_words(val["text"])
    return res

def generate_structure_output(**kwargs: Any) -> ToolResponse:
    """Generate a structured output tool response.

    This function is designed to be used as a tool function for generating
    structured outputs. It takes arbitrary keyword arguments and wraps them
    in a ToolResponse with metadata.

    Args:
        **kwargs: Arbitrary keyword arguments that should match the format
            of the expected structured output specification.

    Returns:
        ToolResponse: A tool response object with empty content and the
            provided kwargs as metadata.
    Note:
        The input parameters should be in the same format as the specification
        and include as much detail as requested by the calling context.
    """
    return ToolResponse(content=[], metadata=kwargs)

def get_dynamic_tool_call_json(data_model_type: Type[BaseModel]) -> list[dict]:
    """Generate JSON schema for dynamic tool calling with a given data model.

    Creates a temporary toolkit, registers the structure output function,
    and configures it with the specified data model to generate appropriate
    JSON schemas for tool calling.
     Args:
        data_model_type: A Pydantic BaseModel class that defines the expected
            structure of the tool output.

    Returns:
        A list of dictionary that contains the JSON schemas for
        the configured tool, suitable for use in API calls that
        support structured outputs.


    Example:
        class MyModel(BaseModel):
            name: str
            value: int
        
        schema = get_dynamic_tool_call_json(MyModel)
    """
    tmp_toolkit = Toolkit()
    tmp_toolkit.register_tool_function(generate_structure_output)
    tmp_toolkit.set_extended_model(
        "generate_structure_output",
        data_model_type,
    )
    return tmp_toolkit.get_json_schemas()

def get_structure_output(blocks: list | Sequence) -> dict:
    """Extract structured output from a sequence of blocks.

    Processes a list or sequence of blocks to extract tool use outputs
    and combine them into a single dictionary. This is typically used
    to parse responses from language models that include tool calls.

    Args:
        blocks: A list or sequence of blocks that may contain tool use
            information. Each block should be a dictionary with 'type'
            and 'input' keys for tool use blocks.

    Returns:
        A dictionary containing the combined input data from all tool
        use blocks found in the input sequence.
        
    Example:
        blocks = [
            {"type": "tool_use", "input": {"name": "test"}},
            {"type": "text", "content": "Some text"},
            {"type": "tool_use", "input": {"value": 42}}
        ]
        result = PromptBase.get_structure_output(blocks)
        # result: {"name": "test", "value": 42}
    """
    dict_output = {}
    for block in blocks:
        if isinstance(block, dict) and block.get("type") == "tool_use":
            dict_output.update(block.get("input", {}))
    return dict_output


def load_prompt_dict() -> dict:
    """Load prompt into dict"""
    prompt_dict = {}
    cur_dir = os.path.dirname(os.path.abspath(__file__))
    prompt_dict["add_note"] = get_prompt_from_file(
        file_path=os.path.join(
            cur_dir,
            "built_in_prompt/prompt_worker_additional_sys_prompt_zh.md",
        ),
        return_json=False,
    )

    prompt_dict["tool_use_rule"] = get_prompt_from_file(
        file_path=os.path.join(
            cur_dir,
            "built_in_prompt/prompt_tool_usage_rules_zh.md",
        ),
        return_json=False,
    )

    prompt_dict["decompose_sys_prompt"] = get_prompt_from_file(
        file_path=os.path.join(
            cur_dir,
            "built_in_prompt/prompt_decompose_subtask_zh.md",
        ),
        return_json=False,
    )

    prompt_dict["expansion_sys_prompt"] = get_prompt_from_file(
        file_path=os.path.join(
            cur_dir,
            "built_in_prompt/prompt_deeper_expansion_zh.md",
        ),
        return_json=False,
    )

    prompt_dict["summarize_sys_prompt"] = get_prompt_from_file(
        file_path=os.path.join(
            cur_dir,
            "built_in_prompt/prompt_inprocess_report_zh.md",
        ),
        return_json=False,
    )

    prompt_dict["reporting_sys_prompt"] = get_prompt_from_file(
        file_path=os.path.join(
            cur_dir,
            "built_in_prompt/prompt_deepresearch_summary_report_zh.md",
        ),
        return_json=False,
    )

    prompt_dict["reflect_sys_prompt"] = get_prompt_from_file(
        file_path=os.path.join(
            cur_dir,
            "built_in_prompt/prompt_reflect_failure_zh.md",
        ),
        return_json=False,
    )

    prompt_dict["reasoning_prompt"] = (
        "## 当前子任务：\n{objective}\n"
        "## 工作计划：\n{plan}\n"
        "{knowledge_gap}\n"
        "## 研究深度：\n{depth}"
    )

    prompt_dict["previous_plan_inst"] = (
        "## 历史计划：\n{previous_plan}\n"
        "## 当前子任务：\n{objective}\n"
    )

    prompt_dict["max_depth_hint"] = (
        "搜索深度已达到最大限制。因此当前子任务无法再进一步分解和扩展。"
        "无论如何，我需要找到其他方法来完成它。"
    )

    prompt_dict["expansion_inst"] = (
         "回顾网页搜索结果，识别是否存在任何可能有助于解决任务清单项或填补任务知识空白的信息，"
        "但这些信息的内容有限或仅被简要提及。\n"
        "**任务描述：**\n{objective}\n"
        "**检查清单：**\n{checklist}\n"
        "**知识空白：**\n{knowledge_gaps}\n"
        "**搜索结果：**\n{search_results}\n"
        "**输出：**\n"
    )

    prompt_dict["follow_up_judge_sys_prompt"] = (
        "为了给用户的查询提供足够的外部信息，你已进行网页搜索以获取额外数据。"
        "但你发现部分信息虽然重要，却不够充分。因此，你从其中一个 URL 中提取了全部内容，"
        "以收集更全面的信息。现在，你必须严格且仔细地评估，在完成网页搜索和内容提取后，"
        "所获取的信息是否足以完成给定任务。请注意，任何随意的决策都可能导致不必要且不可接受的时间成本。\n"
    )

    prompt_dict[
        "retry_hint"
    ] = "在{state}过程中出现错误。我需要重试。"
    
    prompt_dict["need_deeper_hint"] = (
        "现有信息不足，我需要进行更深入的研究来填补知识空白。"
    )
    
    prompt_dict[
        "sufficient_hint"
    ] = "网页搜索和内容提取后的信息已经足够充分！"

    prompt_dict["no_result_hint"] = (
        "我错误地调用了`summarize_intermediate_results`工具，因为目前不存在可总结的里程碑成果。"
    )

    prompt_dict["summarize_hint"] = (
        "基于上述工作历史，检查以下工作计划中的哪一步已完成。在已完成步骤的行末尾标注[已完成]（例如：k.步骤 k [已完成]），"
        "未完成的步骤保持不变。你必须仅返回更新后的计划，严格保留与原始计划完全相同的格式。"
        "不要包含任何解释、推理或诸如'## 工作计划：'之类的章节标题，只需输出更新后的计划本身。"
        "\n\n## 工作计划：\n{plan}"
    )

    prompt_dict["summarize_inst"] = (
        "**任务描述：**\n{objective}\n"
        "**检查清单：**\n{knowledge_gaps}\n"
        "**知识空白：**\n{working_plan}\n"
        "**搜索结果：**\n{tool_result}"
    )

    prompt_dict["update_report_hint"] = (
        "由于信息量过大，我已将研究阶段原始的批量搜索结果替换为以下这份整合并总结核心发现的报告：\n{intermediate_report}\n\n"
        "该报告已保存至{report_path}路径下。我现在将**继续执行工作计划中的下一项**。"
    )

    prompt_dict["save_report_hint"] = (
        "工作计划中当前项的里程碑成果已总结为以下报告：\n{intermediate_report}"
    )

    prompt_dict["reflect_instruction"] = (
        "## 工作历史：\n{conversation_history}\n"
        "## 工作计划：\n{plan}\n"
    )
    prompt_dict["subtask_complete_hint"] = (
        "子任务‘{cur_obj}’已完成。现在当前子任务切换为'{next_obj}'"
    )
    return prompt_dict
