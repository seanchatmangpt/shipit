from loguru import logger
from lchop.context.task_context import register_task

import json
import time
from itertools import islice

from duckduckgo_search import DDGS

from utils.create_prompts import create_tailwind_landing
from utils.prompt_tools import batched_prompt_map

DUCKDUCKGO_MAX_ATTEMPTS = 3

import asyncio
import aiohttp

import asyncio
import aiohttp
import bs4


async def extract_text(url):
    # create a session
    async with aiohttp.ClientSession() as session:
        # get response from url
        response = await session.get(url)
        # read response as text
        text = await response.text()
        # return BeautifulSoup object
        return bs4.BeautifulSoup(text, "html.parser")


async def download_and_extract(urls):
    # create a session
    async with aiohttp.ClientSession() as session:
        # create a list of tasks
        tasks = [asyncio.create_task(extract_text(url)) for url in urls]
        # wait for all tasks to be completed
        results = await asyncio.gather(*tasks)
        # return list of extracted texts
        return [result.get_text() for result in results]


import re


def extract_hyperlinks(input_string):
    """
    Extracts hyperlinks from a string and returns them in a list.
    Args:
        input_string(str): String to extract hyperlinks from.
    Returns:
        List(str): List of hyperlinks found in the string.
    """
    return re.findall(r"(https?://\S+)", input_string)


async def web_search(query: str, num_results: int = 5) -> list[str]:
    """Return the results of a Google search

    Args:
        query (str): The search query.
        num_results (int): The number of results to return.

    Returns:
        str: The results of the search.
    """
    search_results = []
    attempts = 0

    while attempts < DUCKDUCKGO_MAX_ATTEMPTS:
        results = DDGS().text(query)
        search_results = list(islice(results, num_results))

        if search_results:
            break

        time.sleep(1)
        attempts += 1

    results = json.dumps(search_results, ensure_ascii=False, indent=4)
    return json.loads(safe_google_results(results))


def safe_google_results(results: str | list) -> str:
    """
        Return the results of a Google search in a safe format.

    Args:
        results (str | list): The search results.

    Returns:
        str: The results of the search.
    """
    if isinstance(results, list):
        safe_message = json.dumps(
            [result.encode("utf-8", "ignore").decode("utf-8") for result in results]
        )
    else:
        safe_message = results.encode("utf-8", "ignore").decode("utf-8")
    return safe_message


@register_task
async def competitive_analysis_ADSC(work_ctx, services, revenue_threshold, **kwargs):
    logger.info(f"Executing task: competitive_analysis_ADSC")

    prompt = """Please do a competitive analysis of Applied Direct Services Corporation, Also Known As ADSC, whose website is located at https://www.applieddirectservicescorp.com/ and also at https://www.adscke.com/index.php/adsc-ethical-competitive-intelligence-services/ and also at https://www.adscke.com/index.php/adsc-sales-marketing-generative-ai-services/ an act as an expert on Enterprise Sales and Marketing, Competitive Intelligence and Generative AI. Please do a comparative analysis via SWOT of this group versus their top 5 competitors only for Competitive Intelligence Services and Generative AI Services and no other services, and please avoid large companies as they are in a different category, the competitors should have no more than $50 Million of gross annual revenue, and after that do a comparative VRIO analysis of these groups as well. Gather this information for further steps of Dataflow. Only look at two core service offerings that ADSC offers as follows and nothing else:
Ethical Competitive Intelligence Services.
Generative AI Services
And do not look at anything else that ADSC does. Learn about them.
"""

    # links = extract_hyperlinks(prompt)

    # adsc_texts = await download_and_extract(links)

    competitors = await web_search(
        "List of Ethical Competitive Intelligence Services", num_results=25
    )

    companies = await batched_prompt_map(
        prompts_iterable=competitors,
        base_prompt="Tell me the name of the "
        "Intelligence Service Company or None:\n",
    )

    return {
        "success": True,
        "results": f"Successfully executed: competitive_analysis_ADSC",
        "companies": companies,
    }


import anyio


@register_task
async def analyze_competitors(work_ctx, number_of_competitors, **kwargs):
    logger.info(f"Executing task: analyze_competitors")

    prompt = """ADSC can be a valuable partner to your Ethical Competitive Intelligence efforts.

We can support your creation of an Ethical Competitive Intelligence program from scratch.

Throughout your Ethical Competitive Intelligence processes, we can both train and/or support your team to better enable:

Data Acquisition.
Secure Online Recording of Such Information.
Analysis Of Information.
Assembling Of The Big Picture Meaning Of Such Information
Attribution
We can train your team to better deal with these five business processes. Alternatively, we can also organize your team on how to orchestrate these kinds of business processes.

In this way we can help you & your team to better know on an ongoing basis, the factors relevant to your business involving:

Customers
Prospects
Competitors
External Forces.
Therefore, we can provide a means for you to either ethically enhance your existing Competitive Intelligence Program or to start such a program from scratch.

Please contact us as shown below:

Applied Direct Services Corporation (ADSC) 
Please do a competitive analysis of the top 5 competitors from the last prompt and do both a 
    comparative chart with SWOT and then VRIO between ADSC and it’s competitors. Please show this and then show a 
    chart showing the positioning against Maslow’s Hierarchy of human needs for these competitors versus ADSC."""

    await create_tailwind_landing(prompt=prompt, filepath="analyze_competitors.html")
    return {"success": True, "results": f"Successfully executed: analyze_competitors"}


@register_task
async def create_landing_page_CI_AI_services(
    work_ctx, emphasize_CI, target_audience, call_to_action, **kwargs
):
    logger.info(f"Executing task: create_landing_page_CI_AI_services")

    # Task-specific code here...

    return {
        "success": True,
        "results": f"Successfully executed: create_landing_page_CI_AI_services",
    }


@register_task
async def generate_follow_up_forms(
    work_ctx, question_types, response_based_branching, **kwargs
):
    logger.info(f"Executing task: generate_follow_up_forms")

    # Task-specific code here...

    return {
        "success": True,
        "results": f"Successfully executed: generate_follow_up_forms",
    }


@register_task
async def create_synthetic_data_landing_page(
    work_ctx, focus_on_synthetic_data, saas_potential_explanation, **kwargs
):
    logger.info(f"Executing task: create_synthetic_data_landing_page")

    prompt = """Please continue to act as an expert in SEO & eCommerce and Competitive Intelligence but also an expert on 
    Generative AI. ADSC created a small page on Generative AI on their website at 
    https://www.adscke.com/index.php/adsc-sales-marketing-generative-ai-services/ please review this. And then 
    knowing that ADSC is one of the few companies in the world that can use competitive intelligence and resulting 
    competitive insight from Generative AI together with human subject matter experts please generate at least a 
    five-page sub-website that explains the power of generative AI and how ADSC can help with it’s partners to create 
    custom Generative AI Agents. ADSC uses synthetic data for anything external. Please explain why that’s important. 
    And how this is about compliance from a privacy perspective. And talk both about internal Custom Agents to better 
    support sales and marketing and other complex business processes to save budget and increase sales. And then talk 
    about how there is the potential for SAAS sales of subscriptions for insights wrapped as custom Agents with 
    Synthetic Data. Synthetic Data needs to have it’s own page and should be linked into both the internal and 
    external pages talking about custom Agents. And please make sure that there is an appropriate styling to fit 
    WordPress and the current other pages in the ADSC website. And then output the HTML so that we can implement what 
    you’ve generated."""

    await create_tailwind_landing(prompt=prompt, filepath="synthetic_data_landing.html")

    return {
        "success": True,
        "results": f"Successfully executed: create_synthetic_data_landing_page",
    }


@register_task
async def confirm_interest_in_consultation(
    work_ctx, response_type, reasons_count, **kwargs
):
    logger.info(f"Executing task: confirm_interest_in_consultation")

    # Task-specific code here...

    return {
        "success": True,
        "results": f"Successfully executed: confirm_interest_in_consultation",
    }


@register_task
async def rewrite_ethical_CI_webpage(
    work_ctx, source_url, target_format, audience_focus, **kwargs
):
    logger.info(f"Executing task: rewrite_ethical_CI_webpage")

    # Task-specific code here...

    return {
        "success": True,
        "results": f"Successfully executed: rewrite_ethical_CI_webpage",
    }


@register_task
async def develop_generative_AI_mini_website(
    work_ctx, pages_count, focus_areas, wordpress_compatibility, **kwargs
):
    logger.info(f"Executing task: develop_generative_AI_mini_website")

    # Task-specific code here...

    return {
        "success": True,
        "results": f"Successfully executed: develop_generative_AI_mini_website",
    }


"""
# Importing libraries
import anyio
import httpx
import trio

# Function to call duck duck go search n times using anyio task group
async def duck_duck_go_search_n_times(n):
    # Creating a task group
    async with anyio.create_task_group() as task_group:
        # Running the task group n times
        for i in range(n):
            # Calling the search function in a new task
            await task_group.spawn(search, i)

# Function to perform the search
async def search(i):
    # Creating a client
    async with httpx.AsyncClient() as client:
        # Performing a GET request to duck duck go
        response = await client.get("https://duckduckgo.com/")
        # Printing the response
        print(f"Response {i}: {response}")

# Calling the function to search 10 times
trio.run(duck_duck_go_search_n_times, 10)
"""


async def main():
    # await competitive_analysis_ADSC(work_ctx=None, services=None, revenue_threshold=None)
    await analyze_competitors(None, None)


if __name__ == "__main__":
    anyio.run(main)
