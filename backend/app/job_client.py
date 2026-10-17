"""
Job Data Retrieval Client for SkillTrace AI.
Integrates:
1. Adzuna API (Preferred primary live job source via ADZUNA_APP_ID and ADZUNA_APP_KEY)
2. RemoteOK API (Public secondary remote tech jobs feed)
3. Verified Authentic Jobs Pool (Reliable fallback with transparent source provenance)

Includes canonical skill normalization against the SkillTrace AI taxonomy.
"""

from __future__ import annotations
import os
import re
import time
import json
import logging
from typing import List, Dict, Optional, Any, Tuple
from datetime import datetime, timezone
import httpx
from dotenv import load_dotenv

from .taxonomy import taxonomy_registry

load_dotenv()

logger = logging.getLogger(__name__)

# Cache configuration to respect provider terms and rate limits
_CACHE: Dict[str, Tuple[float, List[Dict[str, Any]]]] = {}
CACHE_TTL_SECONDS = 3600  # 1 hour cache per query


class JobDataClient:
    """Manages multi-source live job retrieval with attribution and skill normalization."""

    def __init__(self):
        self.adzuna_app_id = os.getenv("ADZUNA_APP_ID", "").strip()
        self.adzuna_app_key = os.getenv("ADZUNA_APP_KEY", "").strip()
        self.adzuna_country = os.getenv("ADZUNA_COUNTRY", "in").lower()  # default India ('in') or 'us', 'gb'

    def has_adzuna_credentials(self) -> bool:
        return bool(self.adzuna_app_id and self.adzuna_app_key)

    def search_jobs(
        self,
        keyword: str = "",
        location: str = "",
        work_mode: str = "All",
        source_preference: str = "auto",  # 'adzuna', 'remoteok', 'verified', or 'auto'
        page: int = 1,
        results_per_page: int = 15
    ) -> Dict[str, Any]:
        """
        Unified search querying Adzuna (primary), RemoteOK (secondary),
        or the verified authentic pool (fallback).
        """
        cache_key = f"{keyword.lower()}_{location.lower()}_{work_mode}_{source_preference}_{page}"
        now = time.time()
        if cache_key in _CACHE:
            cached_time, cached_data = _CACHE[cache_key]
            if now - cached_time < CACHE_TTL_SECONDS:
                return {
                    "source": "cache",
                    "total": len(cached_data),
                    "jobs": cached_data,
                    "last_updated": datetime.fromtimestamp(cached_time, timezone.utc).isoformat()
                }

        # 1. Try Adzuna if credentials exist
        if (source_preference in ("auto", "adzuna")) and self.has_adzuna_credentials():
            try:
                adzuna_res = self._fetch_from_adzuna(keyword, location, page, results_per_page)
                if adzuna_res:
                    _CACHE[cache_key] = (now, adzuna_res)
                    return {
                        "source": "Adzuna API",
                        "total": len(adzuna_res),
                        "jobs": adzuna_res,
                        "last_updated": datetime.now(timezone.utc).isoformat(),
                        "is_live": True
                    }
            except Exception as e:
                logger.warning(f"Adzuna API query failed: {e}. Falling back to secondary sources.")

        # 2. Try RemoteOK if remote preference or secondary
        if source_preference in ("auto", "remoteok") or work_mode == "Remote":
            try:
                remoteok_res = self._fetch_from_remoteok(keyword, limit=results_per_page)
                if remoteok_res:
                    _CACHE[cache_key] = (now, remoteok_res)
                    return {
                        "source": "RemoteOK API",
                        "total": len(remoteok_res),
                        "jobs": remoteok_res,
                        "last_updated": datetime.now(timezone.utc).isoformat(),
                        "is_live": True
                    }
            except Exception as e:
                logger.warning(f"RemoteOK API query failed: {e}. Falling back to verified pool.")

        # 3. Fallback to Verified Authentic Jobs Pool
        fallback_res = self._get_verified_pool(keyword, location, work_mode)
        _CACHE[cache_key] = (now, fallback_res)
        return {
            "source": "SkillTrace Verified Feed",
            "total": len(fallback_res),
            "jobs": fallback_res,
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "is_live": False,
            "setup_note": None if self.has_adzuna_credentials() else (
                "Adzuna API credentials not configured. Using verified authentic opportunities pool. "
                "Set ADZUNA_APP_ID and ADZUNA_APP_KEY in .env to enable direct live Adzuna queries."
            )
        }

    def _fetch_from_adzuna(
        self,
        keyword: str,
        location: str,
        page: int,
        results_per_page: int
    ) -> List[Dict[str, Any]]:
        """Queries the official Adzuna REST API."""
        url = f"https://api.adzuna.com/v1/api/jobs/{self.adzuna_country}/search/{page}"
        params = {
            "app_id": self.adzuna_app_id,
            "app_key": self.adzuna_app_key,
            "results_per_page": results_per_page,
            "content-type": "application/json"
        }
        if keyword.strip():
            params["what"] = keyword.strip()
        if location.strip() and location != "All":
            params["where"] = location.strip()

        resp = httpx.get(url, params=params, timeout=8.0, follow_redirects=True)
        if resp.status_code != 200:
            raise RuntimeError(f"Adzuna API returned status {resp.status_code}: {resp.text[:200]}")

        data = resp.json()
        raw_results = data.get("results", [])
        normalized = []

        for item in raw_results:
            desc = item.get("description", "")
            title = item.get("title", "")
            req_skills, pref_skills = self._extract_and_normalize_skills(f"{title} {desc}")
            salary_min = item.get("salary_min")
            salary_max = item.get("salary_max")
            salary_str = (
                f"₹{salary_min:,.0f} - ₹{salary_max:,.0f} P.A."
                if (salary_min and salary_max)
                else "Disclosed upon interview"
            )

            normalized.append({
                "id": f"adzuna-{item.get('id')}",
                "title": re.sub(r"<[^>]+>", "", title),
                "company": item.get("company", {}).get("display_name", "Confidential"),
                "location": item.get("location", {}).get("display_name", "Remote / Hybrid"),
                "work_mode": "Remote" if "remote" in desc.lower() else "Hybrid",
                "experience": "1 - 3 years",
                "employment_type": "Full-time",
                "salary": salary_str,
                "posting_date": item.get("created", datetime.now(timezone.utc).isoformat())[:10],
                "source_name": "Adzuna.com",
                "source_url": item.get("redirect_url", ""),
                "skills": req_skills,
                "required_skills": req_skills,
                "preferred_skills": pref_skills,
                "description": re.sub(r"<[^>]+>", "", desc),
                "application_mode": "external_required"
            })

        return normalized

    def _fetch_from_remoteok(self, keyword: str, limit: int = 15) -> List[Dict[str, Any]]:
        """Queries RemoteOK public feed."""
        headers = {"User-Agent": "SkillTraceAI-CareerMatcher/1.0"}
        resp = httpx.get("https://remoteok.com/api", headers=headers, timeout=8.0, follow_redirects=True)
        if resp.status_code != 200:
            raise RuntimeError(f"RemoteOK API returned status {resp.status_code}")

        data = resp.json()
        jobs_raw = [j for j in data if isinstance(j, dict) and "position" in j]

        normalized = []
        kw_lower = keyword.strip().lower()

        for item in jobs_raw:
            title = item.get("position", "")
            desc = item.get("description", "")
            tags = item.get("tags", [])

            if kw_lower and not (kw_lower in title.lower() or kw_lower in desc.lower() or any(kw_lower in t.lower() for t in tags)):
                continue

            req_skills, pref_skills = self._extract_and_normalize_skills(f"{title} {' '.join(tags)} {desc}")
            salary_min = item.get("salary_min")
            salary_max = item.get("salary_max")
            salary_str = (
                f"${salary_min:,.0f} - ${salary_max:,.0f} / year"
                if (salary_min and salary_max)
                else "Competitive compensation"
            )

            normalized.append({
                "id": f"remoteok-{item.get('id')}",
                "title": title,
                "company": item.get("company", "Remote Enterprise"),
                "location": "Worldwide / Remote",
                "work_mode": "Remote",
                "experience": "2+ years",
                "employment_type": "Full-time",
                "salary": salary_str,
                "posting_date": item.get("date", datetime.now(timezone.utc).isoformat())[:10],
                "source_name": "RemoteOK",
                "source_url": item.get("url", f"https://remoteok.com/l/{item.get('id')}"),
                "skills": req_skills,
                "required_skills": req_skills,
                "preferred_skills": pref_skills,
                "description": re.sub(r"<[^>]+>", "", desc)[:1500],
                "application_mode": "external_required"
            })

            if len(normalized) >= limit:
                break

        return normalized

    def _get_verified_pool(self, keyword: str, location: str, work_mode: str) -> List[Dict[str, Any]]:
        """Returns verified authentic opportunities."""
        from .routers.careers import VERIFIED_JOBS
        results = []
        kw = keyword.lower().strip()
        loc = location.lower().strip()

        for j in VERIFIED_JOBS:
            if kw and not (kw in j["title"].lower() or any(kw in s.lower() for s in j.get("skills", [])) or kw in j["company"].lower()):
                continue
            if loc and loc != "all" and not (loc in j["location"].lower() or "remote" in j["location"].lower()):
                continue
            results.append(j)

        if not results:
            return list(VERIFIED_JOBS)

        return results

    def _extract_and_normalize_skills(self, text: str) -> Tuple[List[str], List[str]]:
        """Extracts and normalizes required and preferred skills using the standard taxonomy."""
        found_skills = set()
        text_lower = text.lower()

        for skill_def in taxonomy_registry.definitions:
            if skill_def.canonical_name.lower() in text_lower:
                found_skills.add(skill_def.canonical_name)
            else:
                for alias in skill_def.aliases:
                    if re.search(r"\b" + re.escape(alias.lower()) + r"\b", text_lower):
                        found_skills.add(skill_def.canonical_name)
                        break

        all_skills = sorted(list(found_skills))
        if len(all_skills) >= 4:
            return all_skills[:4], all_skills[4:7]
        elif len(all_skills) >= 2:
            return all_skills[:2], all_skills[2:]
        else:
            return all_skills, ["Testing"]


# Global singleton
job_client = JobDataClient()
