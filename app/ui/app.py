import os
import sys
from pathlib import Path
import importlib.util

import streamlit as st
from dotenv import load_dotenv

# Ensure project root is on sys.path so `app` package can be imported
PROJECT_ROOT = str(Path(__file__).resolve().parents[2])
if PROJECT_ROOT not in sys.path:
	sys.path.insert(0, PROJECT_ROOT)

# Safely import run() from app/main.py even if another top-level 'app' package exists
MAIN_PATH = Path(PROJECT_ROOT) / "app" / "main.py"
spec = importlib.util.spec_from_file_location("newsletter_app_main", str(MAIN_PATH))
if spec and spec.loader:
	newsletter_main = importlib.util.module_from_spec(spec)
	spec.loader.exec_module(newsletter_main)
	run = getattr(newsletter_main, "run")
else:  # pragma: no cover
	raise ImportError("Unable to load app/main.py")


def main() -> None:
	load_dotenv()
	st.set_page_config(page_title="Nintendo & Pokémon News", layout="wide")
	st.markdown(
		"""
		<style>
		:root { --nintendo-red: #E60012; }
		[data-testid="stAppViewContainer"] { background: #ffffff; }
		[data-testid="stSidebar"] { background-color: #fff8f8 !important; border-right: 1px solid #ffd6d6; color: var(--nintendo-red) !important; }
		[data-testid="stSidebar"] * { color: var(--nintendo-red) !important; }
		[data-testid="stSidebar"] ::placeholder { color: rgba(230,0,18,0.7) !important; }
		[data-testid="stSidebar"] label, [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 { color: var(--nintendo-red) !important; }
		.stButton > button { background-color: var(--nintendo-red) !important; color: #fff !important; border: 0px !important; border-radius: 12px !important; padding: 0.6rem 1rem !important; box-shadow: 0 2px 8px rgba(230,0,18,.25); }
		[data-testid="stSidebar"] .stButton > button { color: #ffffff !important; }
		.stButton > button:hover { background-color: #cc0010 !important; }
		.stTextInput input, textarea { border-radius: 10px !important; border: 1px solid #ffc7c7 !important; }
		/* Sidebar text inputs: black background with white text */
		[data-testid="stSidebar"] .stTextInput input,
		[data-testid="stSidebar"] textarea { background-color: #000000 !important; color: #ffffff !important; caret-color: #ffffff !important; border: 1px solid #cc0010 !important; }
		[data-testid="stSidebar"] .stTextInput input::placeholder,
		[data-testid="stSidebar"] textarea::placeholder { color: rgba(255,255,255,0.75) !important; }
		div.stSpinner > div { border-color: var(--nintendo-red) !important; }
		.result-card { border: 1px solid #ffd6d6; border-radius: 12px; padding: 1rem; background: #fff8f8; }
		.top-banner { width: 100%; background: var(--nintendo-red); color: #fff; padding: 18px 20px; border-radius: 12px; margin-bottom: 16px; }
		.top-banner .title { font-size: 1.5rem; font-weight: 700; }
		.top-banner .subtitle { opacity: .9; }
		/* Ensure sidebar primary button text is white, overriding red universal text */
		[data-testid="stSidebar"] .stButton > button, [data-testid="stSidebar"] .stButton > button * { color: #ffffff !important; }
		</style>
		<div class="top-banner">
			<div class="title">Nintendo & Pokémon News Aggregator</div>
			<div class="subtitle">Latest headlines from Nintendo Life, Pokémon Community, and Polygon</div>
		</div>
		""",
		unsafe_allow_html=True,
	)

	with st.sidebar:
		st.header("Settings")
		query = st.text_input("Focus query", value="Nintendo and Pokémon news")
		model = st.text_input("LLM model (optional)", value=os.getenv("OPENAI_MODEL", ""))
		openai_key = st.text_input("OPENAI_API_KEY", type="password", value=os.getenv("OPENAI_API_KEY", ""))
		firecrawl = st.text_input("FIRECRAWL_API_KEY", type="password", value=os.getenv("FIRECRAWL_API_KEY", ""))
		run_button = st.button("Fetch Latest News", use_container_width=True)

	if run_button:
		if not firecrawl:
			st.error("FIRECRAWL_API_KEY is required.")
			return
		if not openai_key:
			st.error("OPENAI_API_KEY is required.")
			return
		os.environ["FIRECRAWL_API_KEY"] = (firecrawl or "").strip()
		os.environ["OPENAI_API_KEY"] = (openai_key or "").strip()
		with st.spinner("Fetching and summarizing news..."):
			result = run(query=query, model=model or None)
		st.success("Done")
		st.markdown("### Results")
		st.markdown('<div class="result-card">', unsafe_allow_html=True)
		st.write(result)
		st.markdown('</div>', unsafe_allow_html=True)


if __name__ == "__main__":
	main()


