from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task

from festy_crew.models.festival import FestivalList
from festy_crew.tools.firecrawl_tool import FirecrawlScrapeTool, FirecrawlSearchTool


@CrewBase
class ResearchCrew:
    """Crew for discovering and scoring Asian music festivals."""

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def festival_researcher(self) -> Agent:
        return Agent(
            config=self.agents_config["festival_researcher"],
            tools=[FirecrawlSearchTool(), FirecrawlScrapeTool()],
            verbose=True,
        )

    @agent
    def genre_filter_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config["genre_filter_analyst"],
            verbose=True,
        )

    @task
    def discover_festivals_task(self) -> Task:
        return Task(
            config=self.tasks_config["discover_festivals_task"],
        )

    @task
    def score_and_filter_festivals_task(self) -> Task:
        return Task(
            config=self.tasks_config["score_and_filter_festivals_task"],
            output_pydantic=FestivalList,
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
