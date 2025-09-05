import os
from typing import Any, Dict, List, Optional, Type

from pydantic import BaseModel, Field, PrivateAttr
from crewai.tools.base_tool import BaseTool

try:
	from firecrawl.firecrawl import FirecrawlApp
except Exception as e:  # pragma: no cover
	FirecrawlApp = None  # type: ignore


class CrawlInput(BaseModel):
	url: str = Field(..., description="URL to crawl, e.g. https://www.nintendolife.com/")
	mode: str = Field("crawl", description="Mode: crawl|scrape|map|search")
	params: Optional[Dict[str, Any]] = Field(None, description="Firecrawl params/filtering options")
	watch: bool = Field(False, description="If True, wait and stream results when supported")


class FirecrawlTool(BaseTool):
	name: str = "Firecrawl Web Scraper"
	description: str = (
		"Crawl/scrape websites using Firecrawl. Supports crawl_url, scrape_url, map_url, search."
	)
	args_schema: Type[BaseModel] = CrawlInput

	# Pydantic model fields
	api_key: Optional[str] = None
	api_url: Optional[str] = None

	# Private attribute for SDK client
	_client: Any = PrivateAttr(default=None)

	def model_post_init(self, __context: Any) -> None:  # type: ignore[override]
		# Resolve credentials and init SDK
		api_key = self.api_key or os.getenv("FIRECRAWL_API_KEY")
		api_url = self.api_url or os.getenv("FIRECRAWL_API_URL")
		if not api_key:
			raise RuntimeError("FIRECRAWL_API_KEY not set")
		if FirecrawlApp is None:
			raise RuntimeError("firecrawl SDK not available. Install firecrawl-py.")
		self._client = FirecrawlApp(api_key=api_key, api_url=api_url)
		return super().model_post_init(__context)

	def _run(
		self,
		url: str,
		mode: str = "crawl",
		params: Optional[Dict[str, Any]] = None,
		watch: bool = False,
	) -> Any:
		mode = (mode or "crawl").lower()
		if mode == "crawl":
			if watch:
				return self._client.crawl_url_and_watch(url=url, params=params)
			return self._client.crawl_url(url=url, params=params)
		if mode == "scrape":
			return self._client.scrape_url(url=url, params=params)
		if mode == "map":
			return self._client.map_url(url=url, params=params)
		if mode == "search":
			# here url is treated as query when mode==search
			return self._client.search(query=url, params=params)
		raise ValueError(f"Unsupported mode: {mode}")


class BatchCrawlInput(BaseModel):
	urls: List[str] = Field(..., description="List of URLs to batch scrape")
	params: Optional[Dict[str, Any]] = Field(None, description="Firecrawl params")
	watch: bool = Field(True, description="Poll and wait for completion")


class FirecrawlBatchTool(BaseTool):
	name: str = "Firecrawl Batch Scraper"
	description: str = "Batch scrape URLs using Firecrawl batch_scrape_urls API"
	args_schema: Type[BaseModel] = BatchCrawlInput

	api_key: Optional[str] = None
	api_url: Optional[str] = None
	_client: Any = PrivateAttr(default=None)

	def model_post_init(self, __context: Any) -> None:  # type: ignore[override]
		api_key = self.api_key or os.getenv("FIRECRAWL_API_KEY")
		api_url = self.api_url or os.getenv("FIRECRAWL_API_URL")
		if not api_key:
			raise RuntimeError("FIRECRAWL_API_KEY not set")
		if FirecrawlApp is None:
			raise RuntimeError("firecrawl SDK not available. Install firecrawl-py.")
		self._client = FirecrawlApp(api_key=api_key, api_url=api_url)
		return super().model_post_init(__context)

	def _run(self, urls: List[str], params: Optional[Dict[str, Any]] = None, watch: bool = True) -> Any:
		if watch:
			return self._client.batch_scrape_urls(urls=urls, params=params)
		# non-watching path returns job id typically; reuse same call for simplicity
		return self._client.batch_scrape_urls(urls=urls, params=params)


