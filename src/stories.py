import asyncio
from typing import Optional

from pydantic import BaseModel

from utils.create_prompts import create_data


class SAFeProgramIncrement(BaseModel):
    name: str
    start_date: str
    end_date: str


class SAFeReleaseTrain(BaseModel):
    name: str
    program_increment: SAFeProgramIncrement


class SAFeRelease(BaseModel):
    name: str
    release_date: str


class SAFeEpic(BaseModel):
    name: str
    description: str


class SAFeFeature(BaseModel):
    name: str
    description: str
    epic: Optional[SAFeEpic]


class SAFeUserStory(BaseModel):
    name: str
    description: str
    feature: SAFeFeature


class SAFeTeam(BaseModel):
    name: str
    members: list[str]


class SAFeIteration(BaseModel):
    name: str
    start_date: str
    end_date: str
    team: SAFeTeam
    user_stories: list[SAFeUserStory]



async def main():
    epic_prompt = "Epic with name Epic 1 and description A big epic"
    epic_data = await create_data(epic_prompt, SAFeEpic)
    epic = SAFeEpic(**epic_data)

    feature_prompt = f"Feature with name Feature 1, description A feature under {epic.name} and epic {epic}"
    feature_data = await create_data(feature_prompt, SAFeFeature)
    feature = SAFeFeature(**feature_data)

    story_prompts = [
        f"Streamlit AI Calendar {feature.name}",
        f"Todo list AGI {feature.name}"
    ]
    story_data = [
        await create_data(prompt, SAFeUserStory) for prompt in story_prompts
    ]
    stories = [SAFeUserStory(**data) for data in story_data]

    print(f"Stories: {stories}")

    # Rest of main logic...

loop = asyncio.get_event_loop()
loop.run_until_complete(main())