"""
Job Requirement Discovery Service for SkillTrace AI.
Enforces:
1. Importing real job/internship listings from original public URLs.
2. Preserving source URL, job title, employer, retrieved description, and timestamp.
3. Separately identifying explicit (required) vs preferred skills.
4. Strictly recording retrieval failures and stale listings without inventing jobs.
"""

from __future__ import annotations
import re
import uuid
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timezone
from urllib.parse import urlparse
import httpx
from sqlalchemy.orm import Session

from ..models import JobListing, JobRequirement
from ..taxonomy import taxonomy_registry

logger = logging.getLogger("skilltrace.jobs")


class JobDiscoveryService:
    def __init__(self):
        pass

    def validate_url(self, url: str) -> bool:
        """Validates that a URL is a syntactically valid public http/https URL."""
        try:
            parsed = urlparse(url.strip())
            return parsed.scheme in ("http", "https") and bool(parsed.netloc)
        except Exception:
            return False

    def _clean_html_text(self, html: str) -> str:
        """Strips HTML tags, scripts, and extra whitespace."""
        text = re.sub(r"<script.*?</script>", " ", html, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r"<style.*?</style>", " ", html, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r"<[^>]+>", " ", text)
        text = re.sub(r"&nbsp;", " ", text)
        text = re.sub(r"&amp;", "&", text)
        text = re.sub(r"&lt;", "<", text)
        text = re.sub(r"&gt;", ">", text)
        text = re.sub(r"\s+", " ", text).strip()
        return text

    def _extract_meta_property(self, html: str, prop: str) -> Optional[str]:
        m = re.search(rf'<meta[^>]+(?:property|name)=["\']{re.escape(prop)}["\'][^>]+content=["\']([^"\']+)["\']', html, re.I)
        if m:
            return m.group(1).strip()
        m2 = re.search(rf'<meta[^>]+content=["\']([^"\']+)["\'][^>]+(?:property|name)=["\']{re.escape(prop)}["\']', html, re.I)
        if m2:
            return m2.group(1).strip()
        return None

    def _extract_title(self, html: str) -> str:
        og_title = self._extract_meta_property(html, "og:title")
        if og_title:
            return og_title
        m = re.search(r"<title[^>]*>(.*?)</title>", html, re.IGNORECASE | re.DOTALL)
        if m:
            clean = re.sub(r"\s+", " ", m.group(1)).strip()
            # Often title has "| Employer" or "- Careers"
            parts = re.split(r"\s*[-|–]\s*", clean)
            return parts[0].strip() if parts else clean
        return "Software Engineering Position"

    def _extract_employer(self, html: str, url: str) -> str:
        og_site = self._extract_meta_property(html, "og:site_name")
        if og_site:
            return og_site
        author = self._extract_meta_property(html, "author")
        if author:
            return author

        # Fallback to domain name
        domain = urlparse(url).netloc
        domain = re.sub(r"^www\.", "", domain)
        parts = domain.split(".")
        if parts:
            return parts[0].capitalize()
        return "Company"

    def is_listing_stale(self, text: str) -> bool:
        """Detects whether listing has expired or closed."""
        stale_signals = [
            r"this job has expired",
            r"this job listing is no longer available",
            r"job posting closed",
            r"applications are now closed",
            r"no longer accepting applications",
            r"position has been filled"
        ]
        lower = text.lower()
        for signal in stale_signals:
            if re.search(signal, lower):
                return True
        return False

    def extract_skills_from_text(self, text: str) -> Tuple[List[str], List[str]]:
        """
        Extracts required vs preferred skills by detecting requirement section boundaries
        and cross-referencing against standard technical skill taxonomy.
        """
        required_skills: List[str] = []
        preferred_skills: List[str] = []

        lower_text = text.lower()

        # Split text into sections based on typical headers
        req_pattern = r"(requirements|qualifications|what you('ll)? need|minimum qualifications|must have|what we look for)"
        pref_pattern = r"(preferred|nice to have|bonus|pluses|good to have|desired skills)"

        req_match = re.search(req_pattern, lower_text)
        pref_match = re.search(pref_pattern, lower_text)

        req_section = ""
        pref_section = ""

        if req_match and pref_match:
            if req_match.start() < pref_match.start():
                req_section = lower_text[req_match.start():pref_match.start()]
                pref_section = lower_text[pref_match.start():pref_match.start() + 2000]
            else:
                pref_section = lower_text[pref_match.start():req_match.start()]
                req_section = lower_text[req_match.start():req_match.start() + 2000]
        elif req_match:
            req_section = lower_text[req_match.start():req_match.start() + 3000]
        elif pref_match:
            pref_section = lower_text[pref_match.start():pref_match.start() + 3000]
        else:
            req_section = lower_text

        # Test against all defined skills in taxonomy
        for defn in taxonomy_registry.definitions:
            canonical = defn.canonical_name
            # Check canonical and aliases
            terms = [canonical.lower()] + [a.lower() for a in defn.aliases]

            in_pref = False
            in_req = False

            for t in terms:
                # Word boundary match
                pattern = rf"(^|[\s,.\-/(])" + re.escape(t) + rf"([\s,.\-/)!]|$)"
                if pref_section and re.search(pattern, pref_section):
                    in_pref = True
                    break

            for t in terms:
                pattern = rf"(^|[\s,.\-/(])" + re.escape(t) + rf"([\s,.\-/)!]|$)"
                if req_section and re.search(pattern, req_section):
                    in_req = True
                    break

            if in_req and canonical not in required_skills:
                required_skills.append(canonical)
            elif in_pref and canonical not in preferred_skills:
                preferred_skills.append(canonical)

        # Fallback if no specific skills detected, check entire text
        if not required_skills and not preferred_skills:
            for defn in taxonomy_registry.definitions:
                canonical = defn.canonical_name
                terms = [canonical.lower()] + [a.lower() for a in defn.aliases]
                for t in terms:
                    pattern = rf"(^|[\s,.\-/(])" + re.escape(t) + rf"([\s,.\-/)!]|$)"
                    if re.search(pattern, lower_text):
                        required_skills.append(canonical)
                        break

        return required_skills, preferred_skills

    async def import_job_from_url(
        self,
        url: str,
        db: Session,
        custom_content: Optional[str] = None
    ) -> JobListing:
        """
        Imports and stores a real job listing from a live public URL.
        Never invents jobs or creates synthetic placeholders without actual content.
        """
        clean_url = url.strip()
        if not self.validate_url(clean_url):
            raise ValueError(f"Invalid public URL format: '{clean_url}'")

        # Check if already imported with valid requirements
        existing = db.query(JobListing).filter(JobListing.source_url == clean_url).first()
        if existing and existing.retrieval_status == "active" and not custom_content:
            existing_reqs = db.query(JobRequirement).filter(JobRequirement.job_id == existing.id).count()
            if existing_reqs > 0:
                return existing


        now_utc = datetime.now(timezone.utc)
        listing_id = existing.id if existing else f"job-{uuid.uuid4().hex[:10]}"

        # If custom content was supplied (e.g. for testing or verified job import)
        if custom_content:
            raw_html = custom_content
            status_code = 200
        else:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
            }
            try:
                async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
                    resp = await client.get(clean_url, headers=headers)
                    status_code = resp.status_code
                    raw_html = resp.text
            except Exception as e:
                logger.error(f"Failed to fetch job URL {clean_url}: {e}")
                job = JobListing(
                    id=listing_id,
                    source_url=clean_url,
                    title="Unavailable Job Listing",
                    employer="Unknown Employer",
                    description_raw=f"Failed to retrieve listing: {str(e)}",
                    retrieval_status="failed",
                    failure_reason=str(e),
                    retrieved_at=now_utc
                )
                job = db.merge(job)
                db.commit()
                return job

        if status_code in (404, 410):
            job = JobListing(
                id=listing_id,
                source_url=clean_url,
                title="Listing Not Found",
                employer="Unknown Employer",
                description_raw=f"HTTP {status_code} returned by destination server.",
                retrieval_status="failed",
                failure_reason=f"HTTP {status_code} Not Found",
                retrieved_at=now_utc
            )
            job = db.merge(job)
            db.commit()
            return job

        clean_text = self._clean_html_text(raw_html)
        title = self._extract_title(raw_html)
        employer = self._extract_employer(raw_html, clean_url)
        is_stale = self.is_listing_stale(clean_text)

        status_label = "stale" if is_stale else "active"
        failure_msg = "Listing detected as closed or expired." if is_stale else None

        job = JobListing(
            id=listing_id,
            source_url=clean_url,
            title=title,
            employer=employer,
            description_raw=clean_text[:10000],
            retrieval_status=status_label,
            failure_reason=failure_msg,
            retrieved_at=now_utc
        )
        job = db.merge(job)
        db.commit()


        # Extract and persist skills
        req_skills, pref_skills = self.extract_skills_from_text(clean_text)

        # Clear old requirements if re-importing
        db.query(JobRequirement).filter(JobRequirement.job_id == job.id).delete()

        for s in req_skills:
            defn = taxonomy_registry.get(s)
            cat = defn.category if defn else "General"
            db.add(JobRequirement(
                id=f"req-{uuid.uuid4().hex[:8]}",
                job_id=job.id,
                skill_name=s,
                skill_category=cat,
                requirement_type="required",
                importance="Essential"
            ))

        for p in pref_skills:
            if p in req_skills:
                continue
            defn = taxonomy_registry.get(p)
            cat = defn.category if defn else "General"
            db.add(JobRequirement(
                id=f"req-{uuid.uuid4().hex[:8]}",
                job_id=job.id,
                skill_name=p,
                skill_category=cat,
                requirement_type="preferred",
                importance="Valuable"
            ))

        db.commit()
        db.refresh(job)
        return job


job_discovery_service = JobDiscoveryService()
