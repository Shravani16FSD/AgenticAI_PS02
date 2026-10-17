"""
SkillTrace AI — Machine Learning Job Matching & Recommendation Pipeline.
Implements:
1. TF-IDF Text Representation & Cosine Similarity baseline
2. Skill Compatibility Evaluator with AST repository evidence linking
3. Multi-Signal Ensemble Scoring (Text, Skills, Experience, Location, Work Mode)
4. Explainable Match Reasoning generation
5. Safe fallback and reproducible evaluation metrics
"""

from __future__ import annotations
import re
import math
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    import numpy as np
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    import numpy as np


@dataclass
class CandidateProfile:
    """Represents a candidate's profile for ML career matching."""
    name: str = "Candidate"
    target_role: str = "Data Analyst"
    summary: str = ""
    current_skills: List[str] = field(default_factory=list)
    experience_years: float = 0.5
    preferred_work_modes: List[str] = field(default_factory=lambda: ["Remote", "Hybrid"])
    preferred_locations: List[str] = field(default_factory=lambda: ["Mumbai", "Remote", "Bengaluru", "Pune"])
    target_career_id: str = "data-analyst"


@dataclass
class MatchSignalBreakdown:
    """Detailed explainable signals produced by the hybrid matching model."""
    final_score: float
    match_percentage: int
    text_similarity: float
    skill_score: float
    experience_score: float
    work_mode_score: float
    location_score: float
    evidence_boost: float
    reasons: List[str]
    skill_evaluations: List[Dict[str, Any]]
    model_version: str = "SkillTrace-ML-v1.2-Hybrid"
    disclaimer: str = "This score reflects profile and repository code alignment, not an employment guarantee."


class PurePythonTfidf:
    """Fast, zero-dependency TF-IDF fallback when scikit-learn is not available."""

    def __init__(self):
        self.vocabulary: Dict[str, int] = {}
        self.idf: Dict[str, float] = {}
        self.doc_count: int = 0

    @staticmethod
    def tokenize(text: str) -> List[str]:
        clean = re.sub(r"[^a-zA-Z0-9\s]", " ", text.lower())
        tokens = [t for t in clean.split() if len(t) > 2]
        stopwords = {
            "and", "the", "for", "with", "from", "you", "will", "this", "that",
            "are", "have", "been", "work", "role", "our", "job", "years", "join"
        }
        return [t for t in tokens if t not in stopwords]

    def fit(self, documents: List[str]):
        self.doc_count = len(documents)
        df: Dict[str, int] = {}
        all_words = set()

        for doc in documents:
            tokens = set(self.tokenize(doc))
            for t in tokens:
                df[t] = df.get(t, 0) + 1
                all_words.add(t)

        self.vocabulary = {word: idx for idx, word in enumerate(sorted(all_words))}
        self.idf = {
            word: math.log((1 + self.doc_count) / (1 + df.get(word, 0))) + 1.0
            for word in self.vocabulary
        }

    def transform_vector(self, text: str) -> Dict[str, float]:
        tokens = self.tokenize(text)
        if not tokens:
            return {}
        tf: Dict[str, float] = {}
        for t in tokens:
            if t in self.vocabulary:
                tf[t] = tf.get(t, 0.0) + 1.0

        length = len(tokens)
        vec: Dict[str, float] = {}
        norm_sq = 0.0
        for t, count in tf.items():
            val = (count / length) * self.idf.get(t, 1.0)
            vec[t] = val
            norm_sq += val * val

        norm = math.sqrt(norm_sq)
        if norm > 0:
            return {k: v / norm for k, v in vec.items()}
        return vec

    def cosine_sim(self, vec1: Dict[str, float], vec2: Dict[str, float]) -> float:
        dot = sum(vec1[k] * vec2[k] for k in vec1 if k in vec2)
        return min(max(dot, 0.0), 1.0)


class JobMatchingModel:
    """
    SkillTrace AI Multi-Signal ML Matching Model.
    Ensembles:
    1. TF-IDF Text Cosine Similarity (Text Fit)
    2. Skill Requirements Coverage (Verified & Profile Skills)
    3. Experience Fit
    4. Location & Work Mode Fit
    5. Verifiable AST Code Evidence Weight
    """

    MODEL_VERSION = "SkillTrace-ML-v1.2-Hybrid"

    def __init__(self, job_corpus: Optional[List[Dict[str, Any]]] = None):
        self.job_corpus = job_corpus or []
        self.sklearn_vectorizer = None
        self.python_tfidf = PurePythonTfidf()
        self._fitted = False

        if self.job_corpus:
            self.fit(self.job_corpus)

    def fit(self, job_corpus: List[Dict[str, Any]]):
        """Fits the TF-IDF vectorizer on the job corpus."""
        self.job_corpus = job_corpus
        docs = [
            f"{j.get('title', '')} {j.get('description', '')} {' '.join(j.get('required_skills', j.get('skills', [])))}"
            for j in job_corpus
        ]
        if not docs:
            docs = ["general software engineering data analysis python sql"]

        if SKLEARN_AVAILABLE:
            try:
                self.sklearn_vectorizer = TfidfVectorizer(
                    ngram_range=(1, 2),
                    stop_words="english",
                    max_features=2500
                )
                self.sklearn_vectorizer.fit(docs)
            except Exception:
                self.sklearn_vectorizer = None

        self.python_tfidf.fit(docs)
        self._fitted = True

    def compute_text_similarity(self, text_a: str, text_b: str) -> float:
        """Computes cosine similarity between two texts using TF-IDF."""
        if not self._fitted:
            self.fit([text_a, text_b])

        if SKLEARN_AVAILABLE and self.sklearn_vectorizer:
            try:
                tfidf_mat = self.sklearn_vectorizer.transform([text_a, text_b])
                sim = float(cosine_similarity(tfidf_mat[0:1], tfidf_mat[1:2])[0][0])
                return min(max(sim, 0.0), 1.0)
            except Exception:
                pass

        vec_a = self.python_tfidf.transform_vector(text_a)
        vec_b = self.python_tfidf.transform_vector(text_b)
        return self.python_tfidf.cosine_sim(vec_a, vec_b)

    @staticmethod
    def parse_job_experience_range(exp_str: str) -> Tuple[float, float]:
        """Parses experience string (e.g. '0 - 1 years', '1 - 3 years') into numeric bounds."""
        if not exp_str or "fresher" in exp_str.lower() or "intern" in exp_str.lower():
            return 0.0, 1.0
        numbers = re.findall(r"\d+", exp_str)
        if len(numbers) >= 2:
            return float(numbers[0]), float(numbers[1])
        elif len(numbers) == 1:
            return float(numbers[0]), float(numbers[0]) + 2.0
        return 0.0, 3.0

    def evaluate_skills(
        self,
        job_skills: List[str],
        candidate_skills: List[str],
        candidate_evidence: Optional[List[Dict[str, Any]]] = None
    ) -> Tuple[float, List[Dict[str, Any]], float]:
        """
        Evaluates job skills against candidate skills and repository AST evidence.
        Returns:
            - skill_score: float [0, 1]
            - detailed_evals: list of per-skill statuses
            - evidence_boost: float [0, 0.15]
        """
        if not job_skills:
            return 1.0, [], 0.0

        evidence_by_skill: Dict[str, List[Dict[str, Any]]] = {}
        for ev in (candidate_evidence or []):
            cat = ev.get("skill_category") if isinstance(ev, dict) else getattr(ev, "skill_category", None)
            if cat:
                evidence_by_skill.setdefault(cat.lower(), []).append(ev)

        candidate_skills_lower = {s.lower() for s in candidate_skills}

        detailed = []
        demonstrated_points = 0.0
        total_possible = len(job_skills)
        verified_citations_count = 0

        for skill in job_skills:
            s_lower = skill.lower()
            citations = evidence_by_skill.get(s_lower, [])

            if len(citations) >= 2:
                status = "Demonstrated"
                note = f"Verified with {len(citations)} code citations in repository scope."
                demonstrated_points += 1.0
                verified_citations_count += len(citations)
            elif len(citations) == 1:
                status = "Partially demonstrated"
                note = "1 verifiable citation found in repository scope."
                demonstrated_points += 0.75
                verified_citations_count += 1
            elif s_lower in candidate_skills_lower or any(s_lower in cs or cs in s_lower for cs in candidate_skills_lower):
                status = "Demonstrated"
                note = "Demonstrated in candidate profile skills."
                demonstrated_points += 0.85
            else:
                status = "Not demonstrated in analysed scope"
                note = "Not demonstrated in analysed scope (does not imply lack of skill)."

            detailed.append({
                "skill": skill,
                "status": status,
                "note": note,
                "citations_count": len(citations)
            })

        skill_score = min(max(demonstrated_points / total_possible, 0.0), 1.0)
        # Evidence boost for having genuine code repository proof
        evidence_boost = min(verified_citations_count * 0.03, 0.15)
        return skill_score, detailed, evidence_boost

    def compute_match(
        self,
        job: Dict[str, Any],
        candidate: CandidateProfile,
        candidate_evidence: Optional[List[Dict[str, Any]]] = None
    ) -> MatchSignalBreakdown:
        """
        Computes the complete multi-signal ML match between a candidate and a job.
        """
        # 1. Text Similarity (Job vs Candidate summary & target role)
        candidate_text = f"{candidate.target_role} {candidate.summary} {' '.join(candidate.current_skills)}"
        job_text = f"{job.get('title', '')} {job.get('description', '')} {' '.join(job.get('required_skills', job.get('skills', [])))}"
        text_sim = self.compute_text_similarity(candidate_text, job_text)

        # 2. Skill Requirements Match
        required_skills = job.get("required_skills", job.get("skills", []))
        skill_score, skill_evals, evidence_boost = self.evaluate_skills(
            required_skills, candidate.current_skills, candidate_evidence
        )

        # 3. Experience Fit
        min_exp, max_exp = self.parse_job_experience_range(job.get("experience", ""))
        c_exp = candidate.experience_years
        if min_exp <= c_exp <= max_exp + 0.5:
            exp_score = 1.0
        elif c_exp < min_exp:
            gap = min_exp - c_exp
            exp_score = max(1.0 - (gap * 0.35), 0.3)
        else:
            exp_score = 0.9

        # 4. Work Mode Fit
        job_work_mode = job.get("work_mode", "Hybrid")
        if not candidate.preferred_work_modes or job_work_mode in candidate.preferred_work_modes or job_work_mode == "Remote":
            work_mode_score = 1.0
        else:
            work_mode_score = 0.6

        # 5. Location Fit
        job_loc = job.get("location", "")
        if job_work_mode == "Remote" or any(loc.lower() in job_loc.lower() for loc in candidate.preferred_locations):
            location_score = 1.0
        else:
            location_score = 0.5

        # Weighted Ensemble
        base_score = (
            (skill_score * 0.40) +
            (text_sim * 0.25) +
            (exp_score * 0.15) +
            (location_score * 0.10) +
            (work_mode_score * 0.10)
        )

        final_score = min(max(base_score + evidence_boost, 0.05), 0.98)
        match_percentage = int(round(final_score * 100))

        # Generate Explainable Reasons
        reasons = []
        matched_skills = [e["skill"] for e in skill_evals if e["status"] in ("Demonstrated", "Partially demonstrated")]
        if matched_skills:
            reasons.append(f"Demonstrated core skills: {', '.join(matched_skills[:3])}")
        if evidence_boost > 0:
            reasons.append("Verifiable code repository evidence detected in GitHub analysis")
        if exp_score >= 0.9:
            reasons.append(f"Experience aligned ({candidate.experience_years} yrs vs required {job.get('experience', 'Entry-level')})")
        if work_mode_score == 1.0:
            reasons.append(f"Matches your work mode preference ({job_work_mode})")

        return MatchSignalBreakdown(
            final_score=round(final_score, 4),
            match_percentage=match_percentage,
            text_similarity=round(text_sim, 4),
            skill_score=round(skill_score, 4),
            experience_score=round(exp_score, 4),
            work_mode_score=round(work_mode_score, 4),
            location_score=round(location_score, 4),
            evidence_boost=round(evidence_boost, 4),
            reasons=reasons,
            skill_evaluations=skill_evals
        )

    def rank_jobs(
        self,
        jobs: List[Dict[str, Any]],
        candidate: CandidateProfile,
        candidate_evidence: Optional[List[Dict[str, Any]]] = None,
        sort_by: str = "best_match"
    ) -> List[Dict[str, Any]]:
        """
        Ranks job listings with explainable ML match metadata attached.
        """
        scored_jobs = []
        for job in jobs:
            breakdown = self.compute_match(job, candidate, candidate_evidence)
            job_copy = dict(job)
            job_copy["ml_match_score"] = breakdown.final_score
            job_copy["ml_match_percentage"] = breakdown.match_percentage
            job_copy["ml_reasons"] = breakdown.reasons
            job_copy["ml_signal_breakdown"] = {
                "text_similarity": breakdown.text_similarity,
                "skill_score": breakdown.skill_score,
                "experience_score": breakdown.experience_score,
                "work_mode_score": breakdown.work_mode_score,
                "location_score": breakdown.location_score,
                "evidence_boost": breakdown.evidence_boost,
                "model_version": breakdown.model_version
            }
            job_copy["skill_evaluations"] = breakdown.skill_evaluations
            scored_jobs.append(job_copy)

        if sort_by == "best_match":
            scored_jobs.sort(key=lambda j: j["ml_match_score"], reverse=True)
        elif sort_by == "experience":
            scored_jobs.sort(key=lambda j: j.get("experience", ""), reverse=False)

        return scored_jobs
