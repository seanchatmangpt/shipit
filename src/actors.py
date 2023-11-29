from pydantic import BaseModel
from typing import List
from rx import just


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
    epic: SAFeEpic


class SAFeUserStory(BaseModel):
    name: str
    description: str
    feature: SAFeFeature


class SAFeTeam(BaseModel):
    name: str
    members: List[str]


class SAFeIteration(BaseModel):
    name: str
    start_date: str
    end_date: str
    team: SAFeTeam
    user_stories: List[SAFeUserStory]


class Agent:
    def __init__(self, name, persona):
        self.name = name
        self.persona = persona

    def speak(self, message):
        return just(f"[{self.name}] {message}")


class ProductOwner(Agent):
    def suggest_stories(self, stories: List[SAFeUserStory]):
        message = "Here are my top stories for this sprint:\n"
        for story in stories:
            message += f"- {story.name}: {story.description}\n"
        return self.speak(message)


class ScrumMaster(Agent):
    def facilitate(self, iteration: SAFeIteration):
        message = f"Let's plan our sprint goals and scope for {iteration.name}.\n"
        message += f"Start Date: {iteration.start_date}, End Date: {iteration.end_date}\n"
        message += f"Team: {iteration.team.name}\n"
        return self.speak(message)


class Developer(Agent):
    def estimate(self, stories: List[SAFeUserStory]):
        message = "Based on these stories, my initial estimates are:\n"
        for story in stories:
            message += f"- {story.name}: {story.description}\n"
        return self.speak(message)





import anyio

async def main():
    agents = [
        ProductOwner("Sarah", "Product Owner"),
        ScrumMaster("John", "Scrum Master"),
        Developer("Mark", "Developer")
    ]

    # Define some SAFe objects
    epic = SAFeEpic(name="Epic 1", description="A big epic")
    feature = SAFeFeature(name="Feature 1", description="A feature under Epic 1", epic=epic)
    stories = [
        SAFeUserStory(name="Story 1", description="User story 1", feature=feature),
        SAFeUserStory(name="Story 2", description="User story 2", feature=feature)
    ]
    team = SAFeTeam(name="Development Team", members=["Alice", "Bob"])
    iteration = SAFeIteration(
        name="Sprint 1",
        start_date="2023-01-01",
        end_date="2023-01-15",
        team=team,
        user_stories=stories
    )

    for agent in agents:
        agent.speak(f"{agent.persona} joining sprint planning").subscribe(print)

    agents[0].suggest_stories(stories).subscribe(print)
    agents[1].facilitate(iteration).subscribe(print)
    agents[2].estimate(stories).subscribe(print)


if __name__ == '__main__':
    anyio.run(main)
