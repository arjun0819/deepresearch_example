# -*- coding: utf-8 -*-
"""The output format of deep research agent"""
from pydantic import BaseModel, Field

class SubtasksDecomposition(BaseModel):
    """
    深度研究中结构化子任务分解输出的模型。
    """
    knowledge_gaps: str = Field(
        description=(
            "必要知识缺口的 markdown 清单，以及可选的视角拓展缺口（用(EXPANSION)标记），"
            "每个缺口单独占一行。"
            "例如：'- [ ] 对京东的详细分析"
            "...\\n- [ ] (EXPANSION) X...'。"
        ),
    )
    working_plan: str = Field(
        description=(
        "按逻辑排序的分步工作计划（3-5 步），每步以序号开头（1.、2.等），包括核心步骤和拓展步骤。"
        "拓展步骤需用(EXPANSION)明确标记，并提供上下文或分析深度。"
        ),
    )

class WebExtraction(BaseModel):
    """
    深度研究中结构化后续网络提取输出的模型。
    """
    reasoning: str = Field(
       description="决策的推理过程，包括关于是否需要更多信息的证据总结和逻辑分析。",
    )
    need_more_information: bool = Field(
        description="是否需要更多信息。",
    )

    title: str = Field(
        description="需要进一步提取的已识别搜索结果片段的标题，如不适用则为空字符串。",
    )
    url: str = Field(
        description="需要进一步提取的原始搜索结果的直接 URL，如不适用则为空字符串。",
    )
    subtask: str = Field(
        description="获取所需信息的后续任务的可执行描述，如不适用则为空字符串。",
    )

class FollowupJudge(BaseModel):
    """
    深度研究中结构化后续分解判断输出的模型。
    """
    reasoning: str = Field(
        description="决策的推理过程，包括关于信息内容是否足够的证据总结和逻辑分析。",
    )
    is_sufficient: bool = Field(
        description="信息内容是否足够。",
    )

class ReflectFailure(BaseModel):
    """
    深度研究中结构化失败反思输出的模型。
    """
    rephrase_subtask: dict = Field(
        description=(
            "关于有问题的子任务是否因设计缺陷或理解偏差需要重新表述的信息。"
            "如果需要重新表述，提供仅将不合适的子任务替换为改进版本的修改后工作计划。"
        ),
        json_schema_extra={
            "additionalProperties": {
                "type": "object",
                "properties": {
                    "need_rephrase": {
                        "type": "boolean",
                        "description": "如果失败的子任务因设计缺陷或理解偏差需要重新表述，则设为'true'；否则设为'false'。",
                    },
                    "rephrased_plan": {
                        "type": "string",
                        "description": "仅将不合适的子任务替换为改进版本的修改后工作计划。如果不需要重新表述，则提供空字符串。",
                    },
                },
            },
        },
    )
    ompose_subtask: dict = Field(
        description=(
            "关于有问题的子任务是否应进一步分解的信息。如果需要分解，提供失败的子任务及其分解原因。"
        ),
        json_schema_extra={
            "additionalProperties": {
                "type": "object",
                "properties": {
                    "need_decompose": {
                        "type": "boolean",
                        "description": "如果失败的子任务应进一步分解，则设为'true'；否则设为'false'。",
                    },
                    "rephrased_plan": {
                        "type": "string",
                        "description": "关于失败的子任务是否需要分解的信息，必要时包括失败的子任务本身。",
                    },
                },
            },
        },
    )
