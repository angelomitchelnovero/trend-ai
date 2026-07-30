"""FastAPI entrypoint. Phase 3."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import articles, ask, digest, news_analyzer, presence, search, trending

app = FastAPI(title="Trend.ai by Aloe", version="0.1.0")

# Loosen this to the actual frontend origin(s) before deploying.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(articles.router)
app.include_router(trending.router)
app.include_router(ask.router)
app.include_router(digest.router)
app.include_router(news_analyzer.router)
app.include_router(search.router)
app.include_router(presence.router)


@app.get("/health")
def health():
    return {"status": "ok"}
