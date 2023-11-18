import ast
from textwrap import dedent

import anyio
import inflection
import loguru
import pyperclip
from icontract import require, ensure

from typetemp.template.typed_template import TypedTemplate
from utils.complete import acreate, achat
from utils.create_primatives import create_list
from utils.file_tools import write, extract_code
from utils.models import get_model


async def create_domain_model_from_yaml(
    prompt, max_tokens=2500, model="gpt4", filepath=None
):
    model = get_model(model)

    prompt = dedent(prompt)

    yaml_prompt = dedent(
        f"""
    Objective:
    Craft a robust, Pythonic, non-anemic domain model rooted in YAML formatted input. The model should fuse the Pythonic 
    principles of Luciano Ramalho, the Domain-Driven Design precepts of Vaughn Vernon, and the pragmatic wisdom of 
    Andrew Hunt and David Thomas. Verify that none of the Sample Input is included in your response.

    Key Principles:
    - Fluent Interfaces: Employ fluent interfaces for method chaining and immutability.
    - Design by Contract: Use 'require' and 'ensure' to define contracts for methods.
    - DRY Principle: Avoid repetitive code to improve maintainability.
    - Pythonic: Aim for readability and elegance in the Pythonic sense.

    Sample Input:
    ```yaml
    OnlineContractAdminCapability:
      overview_description: "Welcome to Contract Administration."
      features:
        - "Dashboard with Metrics"
        - "Interactive Query Tool"
    ```

    Template:
    ```python
    from dataclasses import dataclass, field
    from typing import List
    from icontract import require, ensure

    @dataclass
    class Contract:
        contract_id: str
        contract_name: str
        metrics: List[ContractMetric]  # Assume ContractMetric is defined elsewhere
        approval_rates: List[ApprovalRate]  # Assume ApprovalRate is defined elsewhere
        pending_reviews: List[PendingReview]  # Assume PendingReview is defined elsewhere
        health_monitor: HealthMonitor  # Assume HealthMonitor is defined elsewhere
        is_active: bool = field(default=True)
        has_been_approved: bool = field(default=False)

        @ensure(lambda result: result is not None and all(isinstance(x, ContractMetric) for x in result), "Must return a list of ContractMetric objects.")
        def view_metrics(self):
            '''
            Design by Contract Principle: The postcondition ensures that we return metrics that have valid data.
            Pythonic Idiom: Leverage list comprehensions to elegantly filter metrics.

            # Luciano's take on implementation:
            filtered_metrics = [m for m in self.metrics if m.is_relevant()]
            if not filtered_metrics:
                raise ValueError("No relevant metrics found.")
            return filtered_metrics
            '''
            pass

        @require(lambda user_id: isinstance(user_id, str) and user_id.strip() != "", "User ID must be a non-empty string.")
        @ensure(lambda result: isinstance(result, bool), "Must return a boolean value.")
        def user_has_approved(self, user_id: str):
            '''
            Design by Contract Principle: Preconditions validate the user_id.
            Fluent Python: Use any() to express the idea elegantly.

            # Luciano's take on implementation:
            return any(rate.user_id == user_id and rate.is_approved for rate in self.approval_rates)
            '''
            pass

        @ensure(lambda result: not self.is_active, "Must set is_active to False.")
        def close_contract(self):
            '''
            Design by Contract Principle: Postcondition ensures the contract is no longer active.
            Fluent Python: Use simple, yet effective language constructs.

            # Luciano's take on implementation:
            self.is_active = False
            return True
            '''
            pass
    ```
    
    DO NOT REFERENCE OnlineContractAdminCapability in your code. It is only provided as an example.

    User Requirement Input:
    {prompt}
    """
    )
    return await __chat(
        prompt=yaml_prompt,
        md_type="python",
        model=model,
        max_tokens=max_tokens,
        filepath=filepath,
    )


async def create_yaml(prompt, max_tokens=2500, model=None):
    yaml_prompt = dedent(
        f"""
    Objective:
    Transform the given input (whether it's Python code, project documentation, or another form of structured data) into a YAML format.

    GIVEN INPUT:
    {prompt}

    GIVEN OUTPUT:
    """
    )
    return await __create(
        prompt=yaml_prompt, md_type="yaml", model=model, max_tokens=max_tokens
    )


create_jinja_template = """
Objective:
Transform the given input (whether it's template data, text, or another form of structured data) 
into a Jinja2 template that follows best practices and is easy to maintain. Ensure it leverages 
Jinja2's features effectively. Use Jinja2's template syntax and filters appropriately.

You are generating a Jinja2 template for a specific task. The template should be ready to be used 
in a production environment.

```prompt
{{prompt}}
```

"""


async def create_jinja(
    prompt, max_tokens=2500, model=None, filepath=None, temperature=0.7
):
    """
    Generate a Jinja2 template based on the given prompt.
    """
    create_prompt = TypedTemplate(source=create_python_template, prompt=prompt)()

    return await __create(
        prompt=create_prompt,
        filepath=filepath,
        md_type="jinja",
        model=model,
        max_tokens=max_tokens,
        temperature=temperature,
    )


create_python_template = """
Objective:
Transform the given input (whether it's Python code, project documentation, or another form of structured data) 
into PYTHON CODE that aligns with the Pythonic practices Luciano Ramalho would advocate for based on his 
teachings in "Fluent Python". Ensure it's idiomatic, concise, and leverages Python's features effectively.
Use the standard library and built-in functions unless the library is specified in the prompt.
Use functional programming without classes. Do not use the keyword pass.

You are generating answer code for a job interview question. The code should be production-ready and
ready to be deployed to a production environment.

```prompt
{{prompt}}
```

# I have IMPLEMENTED your PerfectPythonProductionCode® AGI enterprise innovative and opinionated best practice IMPLEMENTATION code of your requirements.
"""


async def create_python(
    prompt, max_tokens=2500, model=None, filepath=None, temperature=0.7
):
    create_prompt = TypedTemplate(source=create_python_template, prompt=prompt)()

    return await __create(
        prompt=create_prompt,
        filepath=filepath,
        md_type="python",
        model=model,
        max_tokens=max_tokens,
        temperature=temperature,
    )


__create_template = """
{{prompt}}
```{{md_type}}
{{suffix}}
"""


async def __create(
    prompt,
    md_type="text",
    max_tokens=2500,
    model=None,
    filepath=None,
    temperature=0.0,
    stop=None,
    suffix=None,
):
    model = get_model(model)

    create_prompt = TypedTemplate(
        source=__create_template, prompt=prompt, md_type=md_type, suffix=suffix
    )()

    result = await acreate(
        prompt=create_prompt,
        model=model,
        stop=["```"] + (stop or []),
        max_tokens=max_tokens,
        temperature=temperature,
    )
    # loguru.logger.info(f"Prompt: {result}")
    # loguru.logger.info(f"Result: {result}")

    if filepath:
        await write(contents=result, filename=filepath)

    return result


async def __chat(
    prompt,
    md_type="text",
    max_tokens=2500,
    filepath=None,
    temperature=0.0,
    model="gpt4",
    **kwargs,
):
    model = get_model(model)

    prompt = dedent(
        f"""
    {prompt}
    ```{md_type}\n# Here is your PerfectPythonProductionCode® AGI response. Tests have been written to a different file:\n"""
    )
    result = await achat(prompt=prompt, model=model)
    loguru.logger.info(f"Prompt: {result}")
    loguru.logger.info(f"Result: {result}")

    if filepath:
        await write(contents=result, filename=filepath)

    return result


async def spr(
    prompt, encode=True, model="3i", max_tokens=250, temperature=0.0, filepath=None
):
    """
    Create a Sparse Priming Representation (SPR) from the given prompt.
    """

    encode_prompt = dedent(
        f"""
# INSTRUCTIONS: You are tasked with generating a Sparse Priming Representation (SPR) from the provided text. SPRs encapsulate information in a highly compressed format. Your objective is to condense the given content, focusing on its essence, and represent it within a fraction of its original length. Abide by the following principles:

- Extract core ideas, disregarding specific examples or detailed explanations.
- Main# Here is your PerfectPythonProductionCode® AGI response.\n\ntain critical relationships and underlying principles.
- Use succinct, clear language, aiming for maximum compression with minimum loss of essential content.

Do not include any references or content outside of the given input. 
Your output should be a distilled SPR, 5x than the original text. Use emergent properties within the model to generate the SPR.
It is not intended to be human readable. Use these techniques to achieve the desired compression:
Symbolic Representation
Conceptual Abstraction
Referential Indicators
Data Compression Techniques
Nonlinear Structuring
Encoded Semantics
Mathematical and Logical Constructs
Metasymbols and Metaconcepts

    ```input
    {prompt}
    ```


    ```spr output\n
    """
    )

    decode_prompt = dedent(
        f"""

# INSTRUCTIONS: You are presented with a Sparse Priming Representation (SPR). Your task is to decode this SPR, expanding it into a detailed, coherent piece of content. The SPR contains highly compressed information, and your goal is to unpack it, elaborating on the concepts and relationships it alludes to. Follow these guidelines:

- Interpret the concise cues in the SPR to rebuild detailed content.
- Provide examples, explanations, and relevant details that align with the themes in the SPR.
- Ensure the expanded text logically connects and fully represents the original information compressed in the SPR.

Do not reference any external content; rely solely on the SPR for your expansion. Generate a comprehensive, detailed output that faithfully represents the original content behind the SPR.

    ```spr
    {prompt}
    ```

    ```output\n"""
    )

    if encode:
        result = await acreate(
            prompt=encode_prompt,
            model=model,
            stop=["```"],
            max_tokens=max_tokens,
            temperature=temperature,
        )
    else:
        result = await acreate(
            prompt=decode_prompt,
            model=model,
            stop=["```"],
            max_tokens=max_tokens,
            temperature=temperature,
        )

    if filepath:
        await write(contents=result, filename=filepath)

    return result


create_evo_template = """
# Task: Automatically generate a YAML configuration for the prompt. 
This configuration must be based on Domain-Driven Design principles, 
outlining Entities, Value Objects, and Business Functions.

# Instructions: 

# Step 1: Define Value Objects
# These are elements without identity, describing characteristics. They are immutable.
value_objects:
  - name: "ValueObjectName"
    definition: "Provide a clear, concise description."
    properties:
      - name: "name_of_property"
        type: "primitive_type"
      # Add more properties as required for the description (6 maximum).

# Step 2: Detail Entities
# These have unique identities and undergo various states and behaviors.
entities:
  - name: "EntityName"
    definition: "Provide a clear, concise description."
    value_objects: 
      - "List associated Value Objects by name"

# Step 3: Describe Business Functions
# These operations are performed on Entities and Value Objects, following Design by Contract principles.
business_functions:
  - entity: "Specify the associated entity"
    name: "name_of_function"
    parameters:
      - parameter: "name_of_parameter"
        type: "primitive_type or value_object"
    definition: "Provide a clear, concise description of function's purpose."
    contract:
      pre:
        - condition: "icontract ensure condition in lambda format"
      post:
        - condition: "icontract require condition in lambda format"

# Step 4: Additional Information
# Provide any extra context or clarification about the domain configuration.
additional_info:
  - key: "Specify the context topic"
    value: "Give detailed information or instructions"

# Reminder: Replace all placeholder text with actual, relevant information. 
Ensure data consistency and accuracy, adhering to the YAML hierarchical 
structure for successful parsing. 

# Step 5: Generate YAML Configuration from Prompt following the schema exactly
that means that the output should be a valid YAML file that follows the schema above.


```domain prompt
{{prompt}}
```

"""


async def create_evo(
    prompt, max_tokens=2500, model=None, filepath=None, temperature=0.0
):
    create_prompt = TypedTemplate(source=create_evo_template, prompt=prompt)()

    result = await __create(
        prompt=create_prompt,
        md_type="domain yaml",
        model=model,
        max_tokens=max_tokens,
        temperature=temperature,
        suffix='# AGI Simulations of Luciano Ramahlo from "Fluent Python" and '
        'David Thomas and Andrew Hunt from "The Pragmatic Programmer" have created this'
        " YAML representation of the domain specified in the prompt.\nvalue_objects:\n",
    )

    result = "value_objects:\n  " + result

    if filepath:
        await write(contents=result, filename=filepath)

    return result


async def main():
    satisfy = """Recent efforts have augmented large language models (LLMs) with external resources (e.g., 
    the Internet) or internal control flows (e.g., prompt chaining) for tasks requiring grounding or reasoning, 
    leading to a new class of language agents. While these agents have achieved substantial empirical success, 
    we lack a systematic framework to organize existing agents and plan future developments. In this paper, 
    we draw on the rich history of cognitive science and symbolic artificial intelligence to propose Cognitive 
    Architectures for Language Agents (CoALA). CoALA describes a language agent with modular memory components, 
    a structured action space to interact with internal memory and external environments, and a generalized 
    decision-making process to choose actions. We use CoALA to retrospectively survey and organize a large body of 
    recent work, and prospectively identify actionable directions towards more capable agents. Taken together, 
    CoALA contextualizes today's language agents within the broader history of AI and outlines a path towards 
    language-based general intelligence."""

    enc = await spr(satisfy)

    print(enc)

    dec = await spr(enc, encode=False)

    print(dec)

    action_space = """ CoALA also includes a structured action space. This refers to the set of 
    actions that an agent can take in response to a given situation. By organizing these actions in a structured 
    manner, CoALA agents are able to make more informed decisions and carry out more complex tasks."""

    # evo = await create_evo(dec, filepath="coala_evo.yaml")
    # evo = await create_evo(, filepath="action_space_evo.yaml")

    # print(evo)


async def gen_evo():
    """ """
    action_space = """ CoALA also includes a structured action space. This refers to the set of 
    actions that an agent can take in response to a given situation. By organizing these actions in a structured 
    manner, CoALA agents are able to make more informed decisions and carry out more complex tasks."""

    # evo = await create_evo(dec, filepath="coala_evo.yaml")
    evo = await create_evo(action_space, filepath="action_space_evo.yaml")


if __name__ == "__main__":
    anyio.run(gen_evo)
