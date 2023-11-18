import typer
from typing import Callable, List

import inspect
import asyncio
import ast

from utils.complete import create  # Assuming this is your OpenAI API wrapper


import icontract

from utils.create_primatives import create_dict

app = typer.Typer()


# Function definitions with icontract decorators


@icontract.require(
    lambda dataset_path: dataset_path.endswith(".csv"),
    "Dataset path must point to a CSV file.",
)
@icontract.require(
    lambda analysis_type: analysis_type in ["regression", "classification"],
    "Analysis type must be 'regression' or 'classification'.",
)
@icontract.require(
    lambda output_format: output_format in ["csv", "json"],
    "Output format must be 'csv' or 'json'.",
)
def perform_data_analysis(dataset_path: str, analysis_type: str, output_format: str):
    """
    Performs data analysis on the specified dataset.
    Args:
    dataset_path (str): Path to the dataset file. Must be a CSV file.
    analysis_type (str): Type of analysis to perform ('regression', 'classification').
    output_format (str): Format for the analysis output ('csv', 'json').
    """
    print(f"Analyzing {dataset_path} using {analysis_type} analysis.")
    print(f"Output will be provided in {output_format} format.")


@icontract.require(
    lambda action: action in ["create", "update", "delete"],
    "Action must be 'create', 'update', or 'delete'.",
)
@icontract.require(lambda user_id: user_id.isalnum(), "User ID must be alphanumeric.")
@icontract.require(
    lambda details: isinstance(details, dict), "Details must be a dictionary."
)
def manage_user_account(action: str, user_id: str, details: dict):
    """
    Manages user accounts based on the given action.
    Args:
    action (str): Action to perform on the user account ('create', 'update', 'delete').
    user_id (str): Unique identifier of the user account. Must be alphanumeric.
    details (dict): Additional details for the account action. Must be a dictionary.
    """
    print(f"Action '{action}' will be performed on user account with ID: {user_id}.")
    print(f"Additional details provided: {details}")


def interpret_with_openai(prompt: str) -> str:
    print(prompt)
    response = create(
        prompt=prompt
    )  # Assuming 'create' is a wrapper for OpenAI API call
    print(response)
    return response.strip()


async def create_kwargs(prompt: str, required_args: List[str]) -> dict:
    instructions = f"Based on the prompt: '{prompt}', create a dictionary of keyword arguments for the function."
    kwargs_dict = await create_dict(prompt=instructions)
    try:
        if isinstance(kwargs_dict, dict):
            # Check if all required arguments are present
            missing_args = [arg for arg in required_args if arg not in kwargs_dict]
            if missing_args:
                raise ValueError(f"Missing required arguments: {missing_args}")
            return kwargs_dict
        else:
            raise ValueError("Response is not a valid dictionary.")
    except (ValueError, SyntaxError) as e:
        print(f"Error in create_kwargs: {e}")
        raise


def select_and_call_function(user_input: str, function_list: list):
    prompts = []
    for function in function_list:
        source = inspect.getsource(function)
        docstring = function.__doc__ if function.__doc__ else "No docstring provided."
        prompts.append(
            f"Function: {function.__name__}\nDocstring: {docstring.strip()}\nSource:\n{source}"
        )

    combined_prompt = (
        "\n\n".join(prompts)
        + f"\n\nUser input: {user_input}\nWhich function should be called?"
    )
    selected_function_name = interpret_with_openai(combined_prompt)

    for function in function_list:
        if function.__name__ in selected_function_name:
            return function

    raise ValueError("No suitable function found.")


@app.command()
def chatbot():
    user_input = typer.prompt("How can I assist you today?")
    function_list = [perform_data_analysis, manage_user_account]
    asyncio.run(select_and_execute_function(user_input, function_list))


async def select_and_execute_function(user_input: str, function_list: List[Callable]):
    selected_function = select_and_call_function(user_input, function_list)
    function_signature = inspect.signature(selected_function)
    required_args = [
        param.name
        for param in function_signature.parameters.values()
        if param.default is param.empty
    ]

    source = inspect.getsource(selected_function)

    prompt_for_kwargs = f"The user has input {user_input}.\n\nCreate the kwargs dictionary for the function based on the user input\n\nFunction:\n{source}\n\nUser input: {user_input}"

    kwargs = await create_kwargs(prompt_for_kwargs, required_args)
    try:
        selected_function(**kwargs)
    except TypeError as e:
        print(f"Error when calling the function: {e}")


# Test function with predefined arguments (for testing purposes)
# def test_perform_data_analysis():
#     test_args = {
#         "dataset_path": "path/to/dataset.csv",
#         "analysis_type": "regression",
#         "output_format": "json",
#     }
#     perform_data_analysis(**test_args)


if __name__ == "__main__":
    app()
