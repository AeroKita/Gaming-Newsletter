from __future__ import annotations

from typing import Optional
import importlib.util
from pathlib import Path

from crewai import Crew


def build_crew(openai_model: Optional[str] = None, query: Optional[str] = None) -> Crew:
	base_dir = Path(__file__).resolve().parent

	# Load agents
	agents_path = base_dir / "agents" / "agents.py"
	spec_agents = importlib.util.spec_from_file_location("newsletter_app_agents", str(agents_path))
	if not spec_agents or not spec_agents.loader:
		raise ImportError("Unable to load agents module")
	agents_mod = importlib.util.module_from_spec(spec_agents)
	spec_agents.loader.exec_module(agents_mod)
	build_agents = getattr(agents_mod, "build_agents")

	# Load tasks
	tasks_path = base_dir / "tasks" / "tasks.py"
	spec_tasks = importlib.util.spec_from_file_location("newsletter_app_tasks", str(tasks_path))
	if not spec_tasks or not spec_tasks.loader:
		raise ImportError("Unable to load tasks module")
	tasks_mod = importlib.util.module_from_spec(spec_tasks)
	spec_tasks.loader.exec_module(tasks_mod)
	build_tasks = getattr(tasks_mod, "build_tasks")

	agents = build_agents(openai_model=openai_model)
	tasks = build_tasks(agents=agents, query=query)
	return Crew(agents=agents, tasks=tasks, verbose=True)


