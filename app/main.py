import os
from typing import Optional
import importlib.util
from pathlib import Path

from dotenv import load_dotenv

# Robustly import build_crew from app/crew.py by file path to avoid 'app' name conflicts
CREW_PATH = Path(__file__).resolve().parent / "crew.py"
spec = importlib.util.spec_from_file_location("newsletter_app_crew", str(CREW_PATH))
if spec and spec.loader:
	newsletter_crew = importlib.util.module_from_spec(spec)
	spec.loader.exec_module(newsletter_crew)
	build_crew = getattr(newsletter_crew, "build_crew")
else:  # pragma: no cover
	raise ImportError("Unable to load app/crew.py")


def run(query: Optional[str] = None, model: Optional[str] = None) -> str:
	load_dotenv()
	crew = build_crew(openai_model=model, query=query)
	result = crew.kickoff()
	return str(result)


if __name__ == "__main__":
	q = os.environ.get("NEWS_QUERY", "Nintendo and Pokémon news")
	print(run(query=q))


