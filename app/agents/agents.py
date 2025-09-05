from typing import List
from pathlib import Path
import importlib.util

from crewai import Agent

# Load tools via file path to avoid package import collisions
TOOLS_PATH = Path(__file__).resolve().parents[1] / "tools" / "firecrawl_tool.py"
spec_tools = importlib.util.spec_from_file_location("newsletter_app_tools", str(TOOLS_PATH))
if not spec_tools or not spec_tools.loader:
	raise ImportError("Unable to load tools module")
tools_mod = importlib.util.module_from_spec(spec_tools)
spec_tools.loader.exec_module(tools_mod)
FirecrawlTool = getattr(tools_mod, "FirecrawlTool")
FirecrawlBatchTool = getattr(tools_mod, "FirecrawlBatchTool")


def build_agents(openai_model: str | None = None) -> List[Agent]:
	researcher = Agent(
		role="Researcher",
		goal=(
			"Collect latest Nintendo and Pokémon gaming news from Nintendo Life, Pokémon Community, and Polygon."
		),
		backstory=(
			"Experienced web researcher specializing in gaming news aggregation and source validation."
		),
		tools=[FirecrawlTool(), FirecrawlBatchTool()],
		verbose=True,
		allow_delegation=False,
		llm=openai_model,
	)

	analyzer = Agent(
		role="Analyzer",
		goal="Analyze scraped articles to extract key announcements, release info, and summaries.",
		backstory="Senior analyst skilled at identifying relevant news and discarding noise.",
		verbose=True,
		allow_delegation=False,
		llm=openai_model,
	)

	writer = Agent(
		role="Writer",
		goal="Write concise, well-structured newsletter-ready summaries with sources and links.",
		backstory="Seasoned tech writer with a focus on clarity and editorial tone.",
		verbose=True,
		allow_delegation=False,
		llm=openai_model,
	)

	return [researcher, analyzer, writer]


