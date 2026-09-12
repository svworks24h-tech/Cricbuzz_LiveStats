from __future__ import annotations

from typing import Any

import requests

from config import API_TIMEOUT, RAPIDAPI_BASE_URL, RAPIDAPI_HOST, RAPIDAPI_KEY


class CricbuzzAPI:
    """Small REST client for a RapidAPI Cricbuzz-compatible service."""

    def __init__(self) -> None:
        self.enabled = bool(RAPIDAPI_KEY)
        self.headers = {
            "X-RapidAPI-Key": RAPIDAPI_KEY,
            "X-RapidAPI-Host": RAPIDAPI_HOST,
        }

    def get(self, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        if not self.enabled:
            raise RuntimeError("RAPIDAPI_KEY is not configured")
        url = f"{RAPIDAPI_BASE_URL.rstrip('/')}/{path.lstrip('/')}"
        response = requests.get(url, headers=self.headers, params=params or {}, timeout=API_TIMEOUT)
        response.raise_for_status()
        return response.json()

    def live_matches(self) -> dict[str, Any]:
        return self.get("matches/v1/live")

    def recent_matches(self) -> dict[str, Any]:
        return self.get("matches/v1/recent")

    def upcoming_matches(self) -> dict[str, Any]:
        return self.get("matches/v1/upcoming")

    def top_batting(self) -> dict[str, Any]:
        return self.get("stats/v1/topstats/0", {"statsType": "mostRuns"})

    def top_bowling(self) -> dict[str, Any]:
        return self.get("stats/v1/topstats/0", {"statsType": "mostWickets"})


def flatten_matches(payload: dict[str, Any]) -> list[dict[str, Any]]:
    """Best-effort extraction from common Cricbuzz JSON response shapes."""
    out: list[dict[str, Any]] = []

    def walk(obj: Any) -> None:
        if isinstance(obj, dict):
            if "matchInfo" in obj:
                info = obj.get("matchInfo") or {}
                score = obj.get("matchScore") or {}
                teams = info.get("team1", {}), info.get("team2", {})
                out.append({
                    "id": info.get("matchId"),
                    "description": info.get("matchDesc") or info.get("seriesName") or "Live Match",
                    "status": info.get("status") or "",
                    "venue": (info.get("venueInfo") or {}).get("ground") or "",
                    "city": (info.get("venueInfo") or {}).get("city") or "",
                    "team1": teams[0].get("teamName", ""),
                    "team2": teams[1].get("teamName", ""),
                    "score": score,
                })
            for value in obj.values():
                walk(value)
        elif isinstance(obj, list):
            for value in obj:
                walk(value)

    walk(payload)
    seen = set()
    unique = []
    for row in out:
        key = row.get("id") or (row.get("team1"), row.get("team2"), row.get("description"))
        if key not in seen:
            seen.add(key)
            unique.append(row)
    return unique
