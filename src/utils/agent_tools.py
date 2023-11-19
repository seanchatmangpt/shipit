import ast
import inspect
from typing import List, Callable

from utils.complete import create, acreate
from utils.create_primatives import create_dict


def interpret_with_openai(prompt: str) -> str:
    # print(prompt)
    response = create(
        prompt=prompt
    )  # Assuming 'create' is a wrapper for OpenAI API call
    # print(response)
    return response.strip()


async def create_kwargs(prompt: str, required_args: List[str]) -> dict:
    instructions = f"Based on the prompt: '{prompt}', create a dictionary of keyword arguments for the function called " \
                   f"kwargs_dict\n```python\nkwargs_dict = "
    # print(instructions)
    kwargs_dict = ast.literal_eval(create(prompt=instructions, stop=["```"]))
    # print(kwargs_dict)
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


async def choose_function(user_input: str, function_list: list):
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

    selected_function_name = await acreate(prompt=combined_prompt)

    for function in function_list:
        if function.__name__ in selected_function_name:
            print(f"Selected function: {function.__name__}")
            return function

    raise ValueError("No suitable function found.")


async def select_and_execute_function(user_input: str, function_list: List[Callable]):
    selected_function = choose_function(user_input, function_list)
    function_signature = inspect.signature(selected_function)
    required_args = [
        param.name
        for param in function_signature.parameters.values()
        if param.default is param.empty
    ]

    source = inspect.getsource(selected_function)

    prompt_for_kwargs = f"The user has input {user_input}.\n\nCreate the kwargs dictionary for the function based on the user input\n\nFunction:\n{source}"

    kwargs = await create_kwargs(prompt_for_kwargs, required_args)
    try:
        selected_function(**kwargs)
    except TypeError as e:
        print(f"Error when calling the function: {e}")


async def execute_function(user_input: str, function: Callable):
    function_signature = inspect.signature(function)
    required_args = [
        param.name
        for param in function_signature.parameters.values()
        if param.default is param.empty
    ]

    source = inspect.getsource(function)

    prompt_for_kwargs = f"The user has input {user_input}.\n\nCreate the kwargs dictionary for the function based on the user input\n\nFunction:\n{source}"

    kwargs = await create_kwargs(prompt_for_kwargs, required_args)
    try:
        return function(**kwargs)
    except TypeError as e:
        print(f"Error when calling the function: {e}")