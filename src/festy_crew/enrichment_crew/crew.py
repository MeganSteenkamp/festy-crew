from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import SerperDevTool

from festy_crew.models.festival import EnrichedContact
from festy_crew.tools.firecrawl_tool import FirecrawlScrapeTool, WebsiteContactFinderTool
from festy_crew.tools.hunter_tool import HunterDomainSearchTool, HunterEmailVerifierTool


@CrewBase
class EnrichmentCrew:
    """Crew for finding and verifying festival organizer contact information."""

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def contact_finder(self) -> Agent:
        return Agent(
            config=self.agents_config["contact_finder"],
            tools=[WebsiteContactFinderTool(), FirecrawlScrapeTool(), SerperDevTool()],
            verbose=True,
        )

    @agent
    def email_enricher(self) -> Agent:
        return Agent(
            config=self.agents_config["email_enricher"],
            tools=[HunterDomainSearchTool(), HunterEmailVerifierTool()],
            verbose=True,
        )

    @task
    def find_contacts_task(self) -> Task:
        return Task(
            config=self.tasks_config["find_contacts_task"],
        )

    @task
    def enrich_emails_task(self) -> Task:
        return Task(
            config=self.tasks_config["enrich_emails_task"],
            output_pydantic=EnrichedContact,
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
