"""
Supervised Machine Learning Training & Evaluation Pipeline for SkillTrace AI.
Trains a calibrated classifier to predict repository evidence categories:
- 'Strong evidence'
- 'Moderate evidence'
- 'Limited evidence'

Uses GroupKFold grouped strictly by `repository_id` to prevent data leakage between repositories.
Compares the trained supervised ML model against a heuristic rule-based baseline.
Saves model artifacts and generates an evaluation report.
"""

from __future__ import annotations
import os
import json
import numpy as np
from typing import Dict, Any, List, Tuple
from sklearn.model_selection import GroupKFold
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import FeatureUnion, Pipeline
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, f1_score, precision_score, recall_score, accuracy_score
import joblib


class ASTFeatureExtractor(BaseEstimator, TransformerMixin):
    """Transforms raw AST signal dictionaries into dense numerical feature matrix."""

    def fit(self, X, y=None):
        self.is_fitted_ = True
        return self

    def transform(self, X):
        features = []
        for sample in X:
            signals = sample.get("ast_signals", {})
            feat = [
                float(signals.get("call_count", 0)),
                float(signals.get("func_def_count", 0)),
                float(signals.get("class_def_count", 0)),
                float(signals.get("test_assert_count", 0)),
                1.0 if signals.get("is_import_only", False) else 0.0,
                1.0 if signals.get("is_tutorial_syntax", False) else 0.0,
                float(signals.get("line_span", 1)),
            ]
            features.append(feat)
        return np.array(features)


class CodeTextExtractor(BaseEstimator, TransformerMixin):
    """Extracts raw code string from sample objects."""

    def fit(self, X, y=None):
        self.is_fitted_ = True
        return self

    def transform(self, X):
        return [sample.get("code_snippet", "") for sample in X]


def rule_based_baseline_predict(samples: List[Dict[str, Any]]) -> List[str]:
    """
    Deterministic rule-based heuristic baseline for comparison.
    Uses AST call counts and import indicators.
    """
    preds = []
    for s in samples:
        sig = s.get("ast_signals", {})
        calls = sig.get("call_count", 0)
        is_import = sig.get("is_import_only", False)
        is_tut = sig.get("is_tutorial_syntax", False)
        asserts = sig.get("test_assert_count", 0)
        classes = sig.get("class_def_count", 0)

        if is_import or is_tut:
            preds.append("Limited evidence")
        elif (calls >= 4 or asserts >= 2 or classes >= 1):
            preds.append("Strong evidence")
        elif calls >= 1:
            preds.append("Moderate evidence")
        else:
            preds.append("Limited evidence")
    return preds


def run_training_and_evaluation(
    dataset_path: str = "backend/app/skill_evidence_dataset.json",
    artifacts_dir: str = "backend/app/model_artifacts"
) -> Dict[str, Any]:
    """
    Executes reproducible ML training, GroupKFold evaluation, baseline comparison,
    and model serialization.
    """
    os.makedirs(artifacts_dir, exist_ok=True)

    if not os.path.exists(dataset_path):
        raise FileNotFoundError(f"Dataset not found at {dataset_path}")

    with open(dataset_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    samples = data["samples"]
    groups = [s["repository_id"] for s in samples]
    y_true = [s["evidence_category"] for s in samples]
    classes = sorted(list(set(y_true)))

    print(f"Loaded {len(samples)} samples across {len(set(groups))} distinct repositories.")
    print(f"Class distribution: { {c: y_true.count(c) for c in classes} }")

    # Evaluate Rule-Based Baseline
    baseline_preds = rule_based_baseline_predict(samples)
    baseline_acc = accuracy_score(y_true, baseline_preds)
    baseline_f1 = f1_score(y_true, baseline_preds, average="macro", zero_division=0)
    baseline_prec = precision_score(y_true, baseline_preds, average="macro", zero_division=0)
    baseline_rec = recall_score(y_true, baseline_preds, average="macro", zero_division=0)

    print("\n--- Baseline Heuristic Performance ---")
    print(f"Accuracy:  {baseline_acc:.4f}")
    print(f"Macro F1:  {baseline_f1:.4f}")
    print(f"Precision: {baseline_prec:.4f}")
    print(f"Recall:    {baseline_rec:.4f}")

    def build_pipeline():
        text_vectorizer = Pipeline([
            ("extract_text", CodeTextExtractor()),
            ("tfidf", TfidfVectorizer(ngram_range=(1, 2), max_features=100, lowercase=True))
        ])

        ast_pipeline = Pipeline([
            ("extract_ast", ASTFeatureExtractor())
        ])

        feature_union = FeatureUnion([
            ("text_features", text_vectorizer),
            ("ast_features", ast_pipeline)
        ])

        clf = LogisticRegression(C=1.5, max_iter=500, class_weight="balanced", random_state=42)

        return Pipeline([
            ("features", feature_union),
            ("classifier", clf)
        ])

    # GroupKFold Cross-Validation (Repository Grouping prevents data leakage)
    n_splits = min(5, len(set(groups)))
    gkf = GroupKFold(n_splits=n_splits)

    cv_preds = [None] * len(samples)

    for train_idx, test_idx in gkf.split(samples, y_true, groups=groups):
        train_samples = [samples[i] for i in train_idx]
        train_y = [y_true[i] for i in train_idx]
        test_samples = [samples[i] for i in test_idx]

        fold_pipeline = build_pipeline()
        fold_pipeline.fit(train_samples, train_y)
        fold_preds = fold_pipeline.predict(test_samples)

        for idx, pred in zip(test_idx, fold_preds):
            cv_preds[idx] = pred

    # ML Metrics
    ml_acc = accuracy_score(y_true, cv_preds)
    ml_f1 = f1_score(y_true, cv_preds, average="macro", zero_division=0)
    ml_prec = precision_score(y_true, cv_preds, average="macro", zero_division=0)
    ml_rec = recall_score(y_true, cv_preds, average="macro", zero_division=0)

    detailed_report = classification_report(y_true, cv_preds, output_dict=True, zero_division=0)

    print("\n--- Supervised ML Model Performance (GroupKFold by Repository) ---")
    print(f"Accuracy:  {ml_acc:.4f} (+{(ml_acc - baseline_acc)*100:.1f}%)")
    print(f"Macro F1:  {ml_f1:.4f} (+{(ml_f1 - baseline_f1)*100:.1f}%)")
    print(f"Precision: {ml_prec:.4f}")
    print(f"Recall:    {ml_rec:.4f}")

    # Train final model on all data and save
    ml_pipeline = build_pipeline()
    ml_pipeline.fit(samples, y_true)

    model_file = os.path.join(artifacts_dir, "skill_evidence_classifier.joblib")
    joblib.dump(ml_pipeline, model_file)

    report = {
        "model_version": "1.0.0",
        "algorithm": "LogisticRegression + FeatureUnion(Tfidf, ASTSignals)",
        "split_method": f"GroupKFold (n_splits={n_splits}) grouped by repository_id",
        "classes": classes,
        "sample_count": len(samples),
        "repository_count": len(set(groups)),
        "baseline_metrics": {
            "accuracy": round(baseline_acc, 4),
            "macro_f1": round(baseline_f1, 4),
            "precision": round(baseline_prec, 4),
            "recall": round(baseline_rec, 4)
        },
        "ml_metrics": {
            "accuracy": round(ml_acc, 4),
            "macro_f1": round(ml_f1, 4),
            "precision": round(ml_prec, 4),
            "recall": round(ml_rec, 4),
            "f1_improvement_pct": round((ml_f1 - baseline_f1) * 100, 2)
        },
        "class_breakdown": detailed_report,
        "artifacts": {
            "model_path": model_file
        }
    }

    report_file = os.path.join(artifacts_dir, "evaluation_report.json")
    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print(f"\nModel artifacts saved to {model_file}")
    print(f"Evaluation report saved to {report_file}")
    return report


if __name__ == "__main__":
    run_training_and_evaluation()
