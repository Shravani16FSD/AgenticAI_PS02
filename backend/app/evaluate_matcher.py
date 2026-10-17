"""
SkillTrace AI — Reproducible ML Model Evaluation Script.
Computes:
- Precision@1, Precision@3, Precision@5
- Recall@3, Recall@5
- NDCG@3, NDCG@5 (Normalized Discounted Cumulative Gain)
- Mean Reciprocal Rank (MRR)
Compares Baseline (TF-IDF Cosine Similarity) vs SkillTrace Multi-Signal Hybrid Matcher.
Persists results to SQLite model_evaluations table.
"""

import os
import json
import math
import sqlite3
from datetime import datetime, timezone
from typing import List, Dict, Any

from ml_matcher import JobMatchingModel, CandidateProfile


def compute_dcg(relevance_scores: List[int], k: int) -> float:
    dcg = 0.0
    for i, rel in enumerate(relevance_scores[:k]):
        # 2^rel - 1 / log2(i + 2)
        gain = (2 ** rel) - 1
        discount = math.log2(i + 2)
        dcg += gain / discount
    return dcg


def compute_ndcg(retrieved_relevances: List[int], ideal_relevances: List[int], k: int) -> float:
    dcg = compute_dcg(retrieved_relevances, k)
    idcg = compute_dcg(sorted(ideal_relevances, reverse=True), k)
    if idcg == 0:
        return 0.0
    return min(dcg / idcg, 1.0)


def evaluate_ranking(ranked_job_ids: List[str], ground_truth: Dict[str, int]) -> Dict[str, float]:
    """
    Computes P@K, R@K, NDCG@K, MRR for a single ranking against ground truth relevance.
    Relevance >= 2 is considered positive (relevant).
    """
    total_relevant = sum(1 for rel in ground_truth.values() if rel >= 2)
    retrieved_rels = [ground_truth.get(jid, 0) for jid in ranked_job_ids]
    all_ideal_rels = list(ground_truth.values())

    # Precision@1, 3, 5
    p_at_1 = sum(1 for r in retrieved_rels[:1] if r >= 2) / 1.0
    p_at_3 = sum(1 for r in retrieved_rels[:3] if r >= 2) / 3.0
    p_at_5 = sum(1 for r in retrieved_rels[:5] if r >= 2) / 5.0

    # Recall@3, 5
    r_at_3 = (sum(1 for r in retrieved_rels[:3] if r >= 2) / total_relevant) if total_relevant > 0 else 0.0
    r_at_5 = (sum(1 for r in retrieved_rels[:5] if r >= 2) / total_relevant) if total_relevant > 0 else 0.0

    # NDCG@3, 5
    ndcg_at_3 = compute_ndcg(retrieved_rels, all_ideal_rels, 3)
    ndcg_at_5 = compute_ndcg(retrieved_rels, all_ideal_rels, 5)

    # MRR (rank of first item with rel >= 2)
    mrr = 0.0
    for idx, r in enumerate(retrieved_rels):
        if r >= 2:
            mrr = 1.0 / (idx + 1)
            break

    return {
        "p_at_1": p_at_1,
        "p_at_3": p_at_3,
        "p_at_5": p_at_5,
        "r_at_3": r_at_3,
        "r_at_5": r_at_5,
        "ndcg_at_3": ndcg_at_3,
        "ndcg_at_5": ndcg_at_5,
        "mrr": mrr
    }


def run_benchmark_evaluation(dataset_path: str = None) -> Dict[str, Any]:
    if dataset_path is None:
        dataset_path = os.path.join(os.path.dirname(__file__), "data", "benchmark_dataset.json")

    with open(dataset_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    jobs = data["jobs"]
    candidates = data["test_candidates"]
    ground_truth = data["ground_truth_judgements"]

    model = JobMatchingModel(jobs)

    baseline_metrics_list = []
    hybrid_metrics_list = []

    for cand_data in candidates:
        cand_id = cand_data["id"]
        cand_obj = CandidateProfile(
            name=cand_data["name"],
            target_role=cand_data["target_role"],
            summary=cand_data["summary"],
            current_skills=cand_data["current_skills"],
            experience_years=cand_data["experience_years"],
            preferred_work_modes=cand_data.get("preferred_work_modes", ["Hybrid", "Remote"]),
            preferred_locations=cand_data.get("preferred_locations", [])
        )
        cand_evidence = cand_data.get("evidence", [])
        gt = ground_truth.get(cand_id, {})

        # 1. Baseline: Pure TF-IDF Text Cosine Similarity
        baseline_scored = []
        for j in jobs:
            text_sim = model.compute_text_similarity(
                f"{cand_obj.target_role} {cand_obj.summary}",
                f"{j.get('title', '')} {j.get('description', '')}"
            )
            baseline_scored.append((j["id"], text_sim))
        baseline_scored.sort(key=lambda x: x[1], reverse=True)
        baseline_ranked_ids = [x[0] for x in baseline_scored]
        baseline_metrics_list.append(evaluate_ranking(baseline_ranked_ids, gt))

        # 2. Hybrid Multi-Signal Model
        hybrid_ranked_jobs = model.rank_jobs(jobs, cand_obj, cand_evidence, sort_by="best_match")
        hybrid_ranked_ids = [j["id"] for j in hybrid_ranked_jobs]
        hybrid_metrics_list.append(evaluate_ranking(hybrid_ranked_ids, gt))

    # Aggregate averages
    def average_metrics(m_list):
        keys = m_list[0].keys()
        return {k: round(sum(m[k] for m in m_list) / len(m_list), 4) for k in keys}

    avg_baseline = average_metrics(baseline_metrics_list)
    avg_hybrid = average_metrics(hybrid_metrics_list)

    # Persist evaluation to database
    db_path = os.path.join(os.path.dirname(__file__), "skilltrace.db")
    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS model_evaluations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                model_name TEXT NOT NULL,
                evaluated_at TEXT NOT NULL,
                p_at_1 REAL,
                p_at_3 REAL,
                p_at_5 REAL,
                r_at_3 REAL,
                ndcg_at_3 REAL,
                ndcg_at_5 REAL,
                mrr REAL,
                sample_count INTEGER,
                dataset_name TEXT
            )
        """)

        now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        cur.execute("""
            INSERT INTO model_evaluations (
                model_name, evaluated_at, p_at_1, p_at_3, p_at_5, r_at_3, ndcg_at_3, ndcg_at_5, mrr, sample_count, dataset_name
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            "SkillTrace-Hybrid-ML-v1.2",
            now_str,
            avg_hybrid["p_at_1"],
            avg_hybrid["p_at_3"],
            avg_hybrid["p_at_5"],
            avg_hybrid["r_at_3"],
            avg_hybrid["ndcg_at_3"],
            avg_hybrid["ndcg_at_5"],
            avg_hybrid["mrr"],
            len(candidates),
            data["metadata"]["dataset_name"]
        ))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Database logging warning: {e}")

    results = {
        "dataset_name": data["metadata"]["dataset_name"],
        "dataset_version": data["metadata"]["version"],
        "candidates_evaluated": len(candidates),
        "jobs_evaluated": len(jobs),
        "baseline_tfidf": avg_baseline,
        "skilltrace_hybrid_ml": avg_hybrid,
        "delta_improvement": {
            "p_at_3_lift": f"{round((avg_hybrid['p_at_3'] - avg_baseline['p_at_3']) * 100, 1)}%",
            "ndcg_at_3_lift": f"{round((avg_hybrid['ndcg_at_3'] - avg_baseline['ndcg_at_3']) * 100, 1)}%",
            "mrr_lift": f"{round((avg_hybrid['mrr'] - avg_baseline['mrr']) * 100, 1)}%"
        }
    }
    return results


if __name__ == "__main__":
    res = run_benchmark_evaluation()
    print("=" * 60)
    print("SKILLTRACE AI — REPRODUCIBLE ML MODEL EVALUATION RESULTS")
    print("=" * 60)
    print(f"Dataset: {res['dataset_name']} (v{res['dataset_version']})")
    print(f"Candidates Tested: {res['candidates_evaluated']} | Job Pool: {res['jobs_evaluated']}")
    print("-" * 60)
    print("METRIC          | BASELINE (TF-IDF) | SKILLTRACE HYBRID ML")
    print("-" * 60)
    print(f"Precision@1     | {res['baseline_tfidf']['p_at_1']:<17} | {res['skilltrace_hybrid_ml']['p_at_1']}")
    print(f"Precision@3     | {res['baseline_tfidf']['p_at_3']:<17} | {res['skilltrace_hybrid_ml']['p_at_3']}")
    print(f"Precision@5     | {res['baseline_tfidf']['p_at_5']:<17} | {res['skilltrace_hybrid_ml']['p_at_5']}")
    print(f"Recall@3        | {res['baseline_tfidf']['r_at_3']:<17} | {res['skilltrace_hybrid_ml']['r_at_3']}")
    print(f"Recall@5        | {res['baseline_tfidf']['r_at_5']:<17} | {res['skilltrace_hybrid_ml']['r_at_5']}")
    print(f"NDCG@3          | {res['baseline_tfidf']['ndcg_at_3']:<17} | {res['skilltrace_hybrid_ml']['ndcg_at_3']}")
    print(f"NDCG@5          | {res['baseline_tfidf']['ndcg_at_5']:<17} | {res['skilltrace_hybrid_ml']['ndcg_at_5']}")
    print(f"MRR             | {res['baseline_tfidf']['mrr']:<17} | {res['skilltrace_hybrid_ml']['mrr']}")
    print("=" * 60)
    print("Lift Summary:", res["delta_improvement"])
