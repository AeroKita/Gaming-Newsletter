from __future__ import annotations

from typing import List, Optional

from crewai import Task
from pydantic import BaseModel


NINTENDO_LIFE = "https://www.nintendolife.com/news"
POLYGON_NINTENDO = "https://www.polygon.com/nintendo"
POKEMON_COMMUNITY_BASE = "https://community.pokemon.com/en-us/"


def pokemon_news_sections() -> List[str]:
	# Focus on News & Announcements for major game categories
	return [
		"news-and-announcements",
		"pokemon-scarlet-violet/news-and-announcements",
		"pokemon-go/news-and-announcements",
		"pokemon-unite/news-and-announcements",
		"pokemon-masters-ex/news-and-announcements",
		"pokemon-sleep/news-and-announcements",
	]


class Article(BaseModel):
	title: str
	date: Optional[str] = None
	source: str
	url: str
	snippet: Optional[str] = None


class ArticlesOutput(BaseModel):
	items: List[Article]

# Ensure forward refs are resolved for Pydantic schema parsing
ArticlesOutput.model_rebuild()


def build_tasks(agents: List, query: str | None = None) -> List[Task]:
	researcher, analyzer, writer = agents

	sections = [POKEMON_COMMUNITY_BASE + s for s in pokemon_news_sections()]
	seed_urls = [NINTENDO_LIFE, POLYGON_NINTENDO, *sections]

	research_task = Task(
		description=(
			"Use Firecrawl to crawl/scrape the following sources for the latest Nintendo and Pokémon news. "
			f"Prioritize 'News & Announcements' sections. Seed URLs: {seed_urls}. "
			"Return a structured list of articles with title, date, source, url, and brief snippet."
		),
		expected_output="A JSON object with 'items': list of articles (title, date, source, url, snippet).",
		agent=researcher,
		output_json=ArticlesOutput,
	)

	analyze_task = Task(
		description=(
			"Analyze the scraped articles to extract the most important announcements, releases, updates, "
			"and notable rumors. Deduplicate items across sources and cluster by game/title."
		),
		expected_output="A concise analysis highlighting key headlines, grouped by game/title, deduplicated.",
		context=[research_task],
		agent=analyzer,
	)

	write_task = Task(
		description=(
			"Write a concise newsletter-ready summary with sections: Headlines, Releases/Updates, Other News. "
			"Include bullet points with 1-2 lines each and cite source links."
		),
		expected_output="Markdown-formatted newsletter summary with sections and bullet points including links.",
		context=[analyze_task],
		agent=writer,
	)

	return [research_task, analyze_task, write_task]


