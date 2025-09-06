# Newsletter Crew: Nintendo & Pokémon News

## Setup 

1. Create venv (already created by assistant as `jobhunt`):

```bash
python3 -m venv "/Users/aerokita/Code Projects/Newsletter/jobhunt"
source "/Users/aerokita/Code Projects/Newsletter/jobhunt/bin/activate"
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Environment variables:

- `FIRECRAWL_API_KEY` (required)
- `OPENAI_MODEL` (optional)

Create a `.env` file in the project root if desired.

## Run CLI

```bash
export FIRECRAWL_API_KEY=your_key
python -m app.main
```

## Streamlit UI

```bash
export FIRECRAWL_API_KEY=your_key
streamlit run app/ui/app.py
```

## Notes

- Sources targeted: Nintendo Life, Pokémon Community News & Announcements sections, Polygon (Nintendo).
- Firecrawl SDK calls used: `crawl_url`, `scrape_url`, `batch_scrape_urls` with params support.

# Gaming-Newsletter
# Gaming-Newsletter
