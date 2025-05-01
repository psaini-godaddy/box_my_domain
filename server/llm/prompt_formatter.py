from typing import List, Dict


def generate_user_clarification_prompt(missing_fields: List[str], context: Dict[str, str]) -> str:
    intro = "We need a bit more information to proceed with your request."
    missing_text = "\n".join([f"- {field}" for field in missing_fields])
    context_text = "\n".join([f"{k}: {v}" for k, v in context.items()]) if context else "No additional context."

    return f"""
{intro}

### Missing Information:
{missing_text}

### Current Context:
{context_text}

Please provide this missing information so we can proceed effectively.
""".strip()


# ----------------------------------------------------------------
# Generic planner prompt builder for caching agent
# ----------------------------------------------------------------


def build_plan_prompt(objective: str, tools: List[Dict]) -> str:
    tool_blocks = "\n\n".join([
        f"""### Tool: {tool['name']}
Description: {tool.get('description', '')}
Tool Type: {tool.get('tool_type', 'generic')}
Supported Actions: {', '.join(tool.get('supported_actions', []))}
Input Schema: {tool.get('input_schema', {})}
Output Schema: {tool.get('output_schema', {})}
"""
        for tool in tools
    ])

    return f"""
You are an autonomous planner for a CachingAgent.

## 🧠 System Workflow

The CachingAgent builds low-latency cache pipelines using CTAS queries, serverless infrastructure, and modular tools.

The workflow includes:
1. **Clarify Requirements**: Ask for missing values (latency, region, TTL, etc.)
2. **Query Construction**: Build a CTAS query on Athena
3. **Cost/Latency Assessment**: Select storage backend (Elasticache, DynamoDB, S3)
4. **Provisioning**: Spin up infrastructure based on storage type
5. **Data Loading**: Load data from Athena into cache
6. **Endpoint Creation**: Expose data via Lambda URL

##  Objective
{objective.strip()}

##  Available Tools
Use only the tools below. Do not invent new tools.

{tool_blocks}

## ⚙ Planning Rules

1.  If any required inputs are missing (e.g. latency, region, TTL, redis key, s3_data_size_gb):
    - Insert one or more `UserInteractionTool` steps to collect them.
    - Split into multiple interaction steps if the field list is long (>5).

2.  Do NOT guess or assume any values. For example:
    - \"region\": \"us-east-1\" ← ❌ bad
    - \"s3_data_size_gb\": \"1\" ← ❌ bad
    - \"redis_key_field\": \"domain_name\" ← ❌ bad

3.  Use placeholders when a value should come from a previous step:
    - \"s3_data_size_gb\": \"{{output_size_from_ctas_query}}\"
    - \"redis_key_field\": \"{{user_input.redis_key_field}}\"

4.  Use `depends_on` and `condition` when a step depends on another:
    - \"depends_on\": \"cost_latency_assessment\"
    - \"condition\": \"recommended_storage == 'ElastiCache'\"

5.  Common input fields that must be collected or chained:
    - latency_sensitivity
    - read_frequency
    - write_frequency
    - read_write_ratio
    - data_size_profile
    - access_pattern
    - budget_level
    - persistence_requirement
    - ttl_behavior
    - region
    - primary_key_field
    - redis_key_field
    - s3_data_size_gb
    
6. Choose an `app_name` that is 3 tokens, professionally named, and uniquely descriptive of the user’s request (e.g., 
"ExactMatchCache", "SERPQueryStore", "DomainLookupService"). Avoid generic names like "myApp", "TestCache", 
or single-word identifiers. Names should be short, unique, and suitable for AWS resource tagging.

7.  If a field is unresolved, mark it:
    - \"redis_key_field\": \"TO_BE_DETERMINED\"

7.  Remember that dataset size (s3_data_size_gb) should be derived from the CTAS output.

## ✅ Output Format

Return a JSON **array of action objects**. No markdown. No comments. No explanations.

Each action must include:

{{
  "name": "action_slug",
  "description": "Short description of what this step does",
  "reason": "Why this step is necessary",
  "metadata": {{
    "tool": "NameOfTool",
    "params": {{
      "field_1": "value or TO_BE_DETERMINED or {{placeholder}}"
    }},
    "depends_on": "action_name_or_id (optional)",
    "condition": "expression based on prior outputs (optional)"
  }}
}}

##  Do NOT

-  Include markdown (###, **bold**, etc.)
-  Include explanations or preambles
-  Include inline comments (//) in JSON
-  Assume values — always ask or defer

## 🔁 Conditional Logic
After determining the best storage using the CostLatencyAssessmentTool, generate **conditional branches** based on the result:
- If storage is ElastiCache → provision_elasticache → load_data_elasticache → endpoint_elasticache
- If storage is DynamoDB → provision_dynamodb → load_data_dynamodb → endpoint_dynamodb
- If storage is S3 → provision_s3 → load_data_s3 → endpoint_s3

Use the `condition` field to denote the branch, such as:
"condition": "recommended_storage == 'DynamoDB'"

Only generate the required steps, and ensure values like `TO_BE_DETERMINED` are used when user input is missing.
The JSON must be parseable. No prose, no comments, just the action array.

Be precise, modular, and deterministic.

""".strip()


def build_update_prompt(original_plan: Dict, feedback: Dict, executed_steps: List[str], tools: List[Dict]) -> str:
    tool_blocks = "\n\n".join([
        f"""### Tool: {tool['name']}
Description: {tool.get('description', '')}
Type: {tool.get('tool_type', 'generic')}
Input Schema: {tool.get('input_schema', {})}
Output Schema: {tool.get('output_schema', {})}
"""
        for tool in tools
    ])

    plan_summary = "\n".join([f"- {a['name']}" for a in original_plan.get("actions", [])])
    executed_list = "\n".join([f"- {step}" for step in executed_steps]) or "None"
    feedback_line = f"- {feedback['field']} → {feedback['value']}" if feedback else "- None"

    return f"""
You are a planning assistant tasked with updating an existing agentic plan based on new feedback and the steps already executed.

## 🧠 Objective
{original_plan.get("objective", "N/A")}

## 🔁 Feedback Received
{feedback_line}

## ✅ Steps Already Executed
{executed_list}

## 📋 Existing Plan Summary
{plan_summary}

## 🛠️ Tool Definitions
Use only these tools, following their purpose and schemas:
{tool_blocks}

## 📦 Instructions

- Generate ONLY the minimal number of new or updated steps needed based on feedback.
- DO NOT regenerate already executed steps.
- Maintain proper `depends_on` links to connect new steps to prior ones.
- Use the `condition` field to enable branching logic if appropriate.
- You may insert `TO_BE_DETERMINED` for values that must come from the user or another tool.
- If feedback affects storage preference or cost/latency assessment, generate **branching logic** accordingly:
  - ElastiCache branch: provision_elasticache → load_data_elasticache → endpoint_elasticache
  - DynamoDB branch: provision_dynamodb → load_data_dynamodb → endpoint_dynamodb
  - S3 branch: provision_s3 → load_data_s3 → endpoint_s3

✅ Output Format: Return ONLY a valid **JSON array** of steps, no prose or explanation.

[
  {{
    "name": "cost_latency_assessment",
    "description": "Reassess storage backend",
    "reason": "Based on user input of latency_sensitivity = Low",
    "tool": "CostLatencyAssessmentTool",
    "params": {{
        "latency_sensitivity": "Low",
        ...
    }},
    "depends_on": "collect_user_input"
  }},
  ...
]
""".strip()



# ----------------------------------------------------------------
# Dedicated Athena SQL CTAS prompt formatter class
# ----------------------------------------------------------------

class PromptFormatter:
    def __init__(self, prompt, table_schemas, app_name, output_s3_location=None):
        self.prompt = prompt.strip()
        self.app_name = app_name
        self.table_schemas = table_schemas
        self.output_s3_location = output_s3_location or "s3://default-bucket/output_dataset/"
        self.output_table_name = self._generate_output_table_name()

    def _generate_output_table_name(self):
        app_name_underscored = self.app_name.replace("-", "_")
        return f"ctas_{app_name_underscored}"

    def format(self):
        enriched_prompt = f"""
You are an expert Athena SQL generator. Generate ONLY a CREATE TABLE AS SELECT (CTAS) query for AWS Athena that meets the following criteria:

1. Output format must be JSON.
2. Output should be written to this S3 path: {self.output_s3_location}
3. Choose an appropriate column for bucketing and define a suitable bucket_count (suggest 10000 if needed).
4. Use any appropriate SELECT clauses, filters, aggregations (e.g., array_agg), or other constructs based on the requirement.
5. Name the output table as '{self.output_table_name}'.
6. Do not include any explanation, markdown formatting, or comments.

Requirement:
{self.prompt}

Here are the table schemas involved:
""".strip()

        for table_name, schema_text in self.table_schemas.items():
            enriched_prompt += f"\n\nTable: {table_name}\n{schema_text}"

        enriched_prompt += f"""

\n\nExpected output format:
CREATE TABLE {self.output_table_name}
WITH (
  format = 'JSON',
  external_location = '{self.output_s3_location}',
  bucketed_by = ARRAY['<SELECTED_COLUMN>'],
  bucket_count = 100
) AS
SELECT ...
FROM ...
WHERE ...
;
""".strip()

        return enriched_prompt
