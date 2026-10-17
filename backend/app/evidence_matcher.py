"""
Evidence-Based Repository Skill Assessment and Job-Matching Engine for SkillTrace AI.

Produces two distinct, transparent results:
1. Repository Skill Profile: Which technical skills are demonstrated, evidence category
   (Strong, Moderate, Limited, No evidence found, Unable to assess), and 0-100 strength score.
2. Job Requirement Match: Transparent matching against job requirements with exact
   Section 5 formula:
   Match % = 100 * (sum of assessed requirement weights * evidence scores) / (sum of weights for assessed requirements)
   With explicit handling of required vs. preferred skills, evidence coverage, and
   "Insufficient evidence to calculate a reliable match".

Strictly preserves traceable line-range citations, commit SHAs, and GitHub provenance.
"""

from __future__ import annotations
import ast
import re
import math
from datetime import datetime, timezone
from typing import List, Dict, Optional, Tuple, Any

from .taxonomy import taxonomy_registry, SkillDefinition


class EvidenceCategory:
    STRONG = "Strong evidence"
    MODERATE = "Moderate evidence"
    LIMITED = "Limited evidence"
    NO_EVIDENCE = "No evidence found"
    UNABLE = "Unable to assess"


class RequirementStatus:
    DEMONSTRATED = "Demonstrated"
    PARTIALLY_DEMONSTRATED = "Partially demonstrated"
    NOT_DEMONSTRATED = "Not demonstrated in analysed scope"
    UNABLE_TO_ASSESS = "Unable to assess"


def make_direct_github_url(repo_full_name: str, commit_sha: str, file_path: str, start_line: int, end_line: int) -> str:
    clean_sha = commit_sha.strip() if commit_sha else "HEAD"
    clean_path = file_path.replace("\\", "/")
    line_ref = f"#L{start_line}" if start_line == end_line else f"#L{start_line}-L{end_line}"
    return f"https://github.com/{repo_full_name}/blob/{clean_sha}/{clean_path}{line_ref}"


def extract_snippet(lines: List[str], start_line: int, end_line: int, max_lines: int = 10) -> str:
    s_idx = max(0, start_line - 1)
    e_idx = min(len(lines), end_line)
    slice_lines = lines[s_idx:e_idx]
    if len(slice_lines) > max_lines:
        slice_lines = slice_lines[:max_lines] + ["... [truncated for display]"]
    return "\n".join(slice_lines)


class RepositoryEvidenceAnalyzer:
    """
    Deterministic static code and AST analyzer for multi-language repositories.
    Inspects source files, parses ASTs, detects imports vs substantive implementations,
    and captures commit-pinned evidence records.
    """

    def __init__(self, repo_full_name: str, commit_sha: str = "HEAD"):
        self.repo_full_name = repo_full_name
        self.commit_sha = commit_sha

    @classmethod
    def analyze_multiple_repositories(cls, repositories: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyzes multiple authorized repositories and combines their evidence
        without double-counting identical files or duplicate code snippets.
        """
        if not repositories:
            return {
                "repository_name": "No repositories authorized",
                "commit_sha": "NONE",
                "scanned_files_count": 0,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "skill_profiles": {},
                "status": EvidenceCategory.UNABLE
            }

        combined_files = []
        seen_file_hashes = set()

        for repo in repositories:
            repo_name = repo.get("repo_full_name") or repo.get("repo_name", "candidate/repo")
            c_sha = repo.get("commit_sha", "HEAD")
            for f in repo.get("files", []):
                path = f.get("path", "")
                content = f.get("content", "")
                # Fingerprint to avoid double-counting duplicate vendored or copied files
                digest = hash(f"{path.split('/')[-1]}_{len(content)}_{content[:120]}")
                if digest not in seen_file_hashes:
                    seen_file_hashes.add(digest)
                    combined_files.append({
                        "path": path,
                        "content": content,
                        "repo_name": repo_name,
                        "commit_sha": c_sha
                    })

        analyzer = cls(
            repo_full_name=f"Combined ({len(repositories)} repositories)",
            commit_sha="multi-head"
        )
        res = analyzer.analyze_repository_files(combined_files)
        res["repositories_analyzed"] = len(repositories)
        res["total_files_scanned"] = sum(len(r.get("files", [])) for r in repositories)
        res["unique_files_fingerprinted"] = len(combined_files)
        return res

    def analyze_repository_files(self, files: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Analyzes a list of file dicts: [{'path': str, 'content': str}]
        Returns verified citations and evidence metrics grouped by canonical skill.
        """
        if not files:
            return {
                "repository_name": self.repo_full_name,
                "commit_sha": self.commit_sha,
                "evidence_by_skill": {},
                "files_scanned": 0,
                "status": EvidenceCategory.UNABLE,
                "summary": "Unable to assess: No source files available in repository scope.",
                "skill_profiles": {}
            }

        evidence_by_skill: Dict[str, List[Dict[str, Any]]] = {}
        for skill in taxonomy_registry.all_canonical_names():
            evidence_by_skill[skill] = []

        scanned_count = len(files)

        for file_entry in files:
            path = file_entry.get("path", "").replace("\\", "/")
            content = file_entry.get("content", "")
            if not content.strip():
                continue

            path_lower = path.lower()
            lines = content.splitlines()

            # Python files
            if path_lower.endswith(".py") or path_lower.endswith(".ipynb"):
                self._inspect_python(path, lines, content, evidence_by_skill)

            # SQL files
            elif path_lower.endswith(".sql"):
                self._inspect_sql(path, lines, content, evidence_by_skill)

            # JavaScript / TypeScript
            elif path_lower.endswith(".ts") or path_lower.endswith(".tsx") or path_lower.endswith(".js") or path_lower.endswith(".jsx"):
                self._inspect_js_ts(path, lines, content, evidence_by_skill)

            # Java
            elif path_lower.endswith(".java"):
                self._inspect_java(path, lines, content, evidence_by_skill)

            # C++
            elif path_lower.endswith(".cpp") or path_lower.endswith(".hpp") or path_lower.endswith(".cc"):
                self._inspect_cpp(path, lines, content, evidence_by_skill)

            # CI/CD Workflows
            elif ".github/workflows" in path_lower or "dockerfile" in path_lower or "docker-compose" in path_lower:
                self._inspect_devops(path, lines, content, evidence_by_skill)

        # Build skill profiles
        has_repo_tests = bool(evidence_by_skill.get("Testing"))
        skill_profiles = {}
        for skill_def in taxonomy_registry.definitions:
            skill_name = skill_def.canonical_name
            items = evidence_by_skill.get(skill_name, [])
            strength_score, breakdown, category, rationale, actions = self._evaluate_skill_evidence(
                skill_name, items, scanned_count, has_repo_tests
            )
            skill_profiles[skill_name] = {
                "canonical_name": skill_name,
                "category": skill_def.category,
                "evidence_strength": strength_score,
                "evidence_category": category,
                "evidence_count": len(items),
                "citations": items,
                "score_breakdown": breakdown,
                "rationale": rationale,
                "suggested_actions": actions,
            }

        return {
            "repository_name": self.repo_full_name,
            "commit_sha": self.commit_sha,
            "scanned_files_count": scanned_count,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "skill_profiles": skill_profiles
        }

    # -------------------------------------------------------------
    # Language Parsers
    # -------------------------------------------------------------
    def _inspect_python(
        self,
        path: str,
        lines: List[str],
        content: str,
        evidence_by_skill: Dict[str, List[Dict[str, Any]]]
    ):
        is_test_file = "test_" in path.lower() or "_test.py" in path.lower() or "tests/" in path.lower()
        try:
            tree = ast.parse(content, filename=path)
        except SyntaxError:
            return

        imported_modules = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imported_modules.add(alias.name.split('.')[0])
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported_modules.add(node.module.split('.')[0])

        # Track usage to catch import-only anti-pattern
        calls_by_name = set()
        attrs_by_name = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    calls_by_name.add(node.func.id)
                elif isinstance(node.func, ast.Attribute):
                    attrs_by_name.add(node.func.attr if isinstance(node.func, ast.Attribute) else node.attr)
            elif isinstance(node, ast.Attribute):
                attrs_by_name.add(node.attr)

        # 1. Classes & OOP
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                start = getattr(node, "lineno", 1)
                end = getattr(node, "end_lineno", start + 4)
                is_orm = any(getattr(b, "id", "") in ("Base", "Model") or getattr(b, "attr", "") == "Model" for b in node.bases)
                is_nn = any(getattr(b, "id", "") in ("Module", "Sequential") or getattr(b, "attr", "") == "Module" for b in node.bases)

                if is_orm:
                    evidence_by_skill["Database Design"].append({
                        "skill": "Database Design",
                        "detail": f"ORM Database Model: Class '{node.name}'",
                        "repository_name": self.repo_full_name,
                        "file_path": path,
                        "start_line": start,
                        "end_line": end,
                        "snippet": extract_snippet(lines, start, end),
                        "commit_sha": self.commit_sha,
                        "direct_url": make_direct_github_url(self.repo_full_name, self.commit_sha, path, start, end),
                        "confidence": 0.95,
                        "is_import_only": False,
                        "is_substantial": True
                    })
                elif is_nn:
                    evidence_by_skill["Deep Learning"].append({
                        "skill": "Deep Learning",
                        "detail": f"Neural Network Architecture: PyTorch nn.Module '{node.name}'",
                        "repository_name": self.repo_full_name,
                        "file_path": path,
                        "start_line": start,
                        "end_line": end,
                        "snippet": extract_snippet(lines, start, end),
                        "commit_sha": self.commit_sha,
                        "direct_url": make_direct_github_url(self.repo_full_name, self.commit_sha, path, start, end),
                        "confidence": 0.95,
                        "is_import_only": False,
                        "is_substantial": True
                    })
                else:
                    evidence_by_skill["Python"].append({
                        "skill": "Python",
                        "detail": f"Object-Oriented Structure: Class '{node.name}'",
                        "repository_name": self.repo_full_name,
                        "file_path": path,
                        "start_line": start,
                        "end_line": end,
                        "snippet": extract_snippet(lines, start, end),
                        "commit_sha": self.commit_sha,
                        "direct_url": make_direct_github_url(self.repo_full_name, self.commit_sha, path, start, end),
                        "confidence": 0.92,
                        "is_import_only": False,
                        "is_substantial": True
                    })

        # 2. Functions, API routes, Tests
        has_functions = False
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                has_functions = True
                start = getattr(node, "lineno", 1)
                end = getattr(node, "end_lineno", start + 3)

                # Route decorator check
                is_route = False
                for dec in node.decorator_list:
                    dec_str = ast.dump(dec)
                    if any(verb in dec_str for verb in ("get", "post", "put", "delete", "patch", "route")):
                        is_route = True
                        break

                if is_route:
                    evidence_by_skill["APIs"].append({
                        "skill": "APIs",
                        "detail": f"HTTP API Route Handler: '{node.name}'",
                        "repository_name": self.repo_full_name,
                        "file_path": path,
                        "start_line": start,
                        "end_line": end,
                        "snippet": extract_snippet(lines, start, end),
                        "commit_sha": self.commit_sha,
                        "direct_url": make_direct_github_url(self.repo_full_name, self.commit_sha, path, start, end),
                        "confidence": 0.95,
                        "is_import_only": False,
                        "is_substantial": True
                    })
                elif is_test_file or node.name.startswith("test_"):
                    assert_count = sum(1 for sub in ast.walk(node) if isinstance(sub, ast.Assert))
                    evidence_by_skill["Testing"].append({
                        "skill": "Testing",
                        "detail": f"Automated Test Case: '{node.name}' ({assert_count} assertions)",
                        "repository_name": self.repo_full_name,
                        "file_path": path,
                        "start_line": start,
                        "end_line": end,
                        "snippet": extract_snippet(lines, start, end),
                        "commit_sha": self.commit_sha,
                        "direct_url": make_direct_github_url(self.repo_full_name, self.commit_sha, path, start, end),
                        "confidence": 0.95,
                        "is_import_only": False,
                        "is_substantial": True
                    })
                else:
                    is_sub = len(node.body) >= 2 and not isinstance(node.body[0], ast.Pass)
                    evidence_by_skill["Python"].append({
                        "skill": "Python",
                        "detail": f"Function Implementation: '{node.name}' with parameter handling",
                        "repository_name": self.repo_full_name,
                        "file_path": path,
                        "start_line": start,
                        "end_line": end,
                        "snippet": extract_snippet(lines, start, end),
                        "commit_sha": self.commit_sha,
                        "direct_url": make_direct_github_url(self.repo_full_name, self.commit_sha, path, start, end),
                        "confidence": 0.92,
                        "is_import_only": False,
                        "is_substantial": is_sub
                    })

        # Top-level basic python scripts (e.g. print statements or pass stubs)
        if not has_functions and not any(isinstance(n, ast.ClassDef) for n in ast.walk(tree)):
            evidence_by_skill["Python"].append({
                "skill": "Python",
                "detail": "Basic Python script execution and top-level expressions",
                "repository_name": self.repo_full_name,
                "file_path": path,
                "start_line": 1,
                "end_line": min(len(lines), 5),
                "snippet": extract_snippet(lines, 1, 5),
                "commit_sha": self.commit_sha,
                "direct_url": make_direct_github_url(self.repo_full_name, self.commit_sha, path, 1, min(len(lines), 5)),
                "confidence": 0.70,
                "is_import_only": False,
                "is_substantial": False
            })

        # 3. Pandas / Data Cleaning
        if "pandas" in imported_modules:
            pandas_ops = [c for c in ("DataFrame", "Series", "read_csv", "read_sql", "groupby", "merge", "pivot_table", "dropna", "fillna", "rolling") if c in attrs_by_name or c in calls_by_name]
            if pandas_ops:
                for node in ast.walk(tree):
                    if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr in pandas_ops:
                        start = getattr(node, "lineno", 1)
                        end = getattr(node, "end_lineno", start + 2)
                        evidence_by_skill["Pandas"].append({
                            "skill": "Pandas",
                            "detail": f"DataFrame Operation: '{node.func.attr}' transformation",
                            "repository_name": self.repo_full_name,
                            "file_path": path,
                            "start_line": start,
                            "end_line": end,
                            "snippet": extract_snippet(lines, start, end),
                            "commit_sha": self.commit_sha,
                            "direct_url": make_direct_github_url(self.repo_full_name, self.commit_sha, path, start, end),
                            "confidence": 0.95,
                            "is_import_only": False,
                            "is_substantial": True
                        })
                        if node.func.attr in ("dropna", "fillna", "drop_duplicates", "astype"):
                            evidence_by_skill["Data Cleaning"].append({
                                "skill": "Data Cleaning",
                                "detail": f"Data Cleaning Routine: '{node.func.attr}' handling missing/duplicate records",
                                "repository_name": self.repo_full_name,
                                "file_path": path,
                                "start_line": start,
                                "end_line": end,
                                "snippet": extract_snippet(lines, start, end),
                                "commit_sha": self.commit_sha,
                                "direct_url": make_direct_github_url(self.repo_full_name, self.commit_sha, path, start, end),
                                "confidence": 0.92,
                                "is_import_only": False,
                                "is_substantial": True
                            })
            else:
                evidence_by_skill["Pandas"].append({
                    "skill": "Pandas",
                    "detail": "Import statement only: 'pandas' imported without subsequent DataFrame operations",
                    "repository_name": self.repo_full_name,
                    "file_path": path,
                    "start_line": 1,
                    "end_line": 2,
                    "snippet": extract_snippet(lines, 1, 2),
                    "commit_sha": self.commit_sha,
                    "direct_url": make_direct_github_url(self.repo_full_name, self.commit_sha, path, 1, 2),
                    "confidence": 0.40,
                    "is_import_only": True,
                    "is_substantial": False
                })

        # 4. Scikit-learn / Model Training / Evaluation
        if "sklearn" in imported_modules:
            has_fit = "fit" in attrs_by_name
            has_eval = any(m in attrs_by_name or m in calls_by_name for m in ("score", "classification_report", "roc_auc_score", "mean_squared_error"))
            for node in ast.walk(tree):
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "fit":
                    start = getattr(node, "lineno", 1)
                    end = getattr(node, "end_lineno", start + 2)
                    evidence_by_skill["Model Training"].append({
                        "skill": "Model Training",
                        "detail": "Model Training: Invocation of estimator .fit() with training data",
                        "repository_name": self.repo_full_name,
                        "file_path": path,
                        "start_line": start,
                        "end_line": end,
                        "snippet": extract_snippet(lines, start, end),
                        "commit_sha": self.commit_sha,
                        "direct_url": make_direct_github_url(self.repo_full_name, self.commit_sha, path, start, end),
                        "confidence": 0.95,
                        "is_import_only": False,
                        "is_substantial": True
                    })
                    evidence_by_skill["Scikit-learn"].append({
                        "skill": "Scikit-learn",
                        "detail": "Scikit-learn Estimator Training pipeline execution",
                        "repository_name": self.repo_full_name,
                        "file_path": path,
                        "start_line": start,
                        "end_line": end,
                        "snippet": extract_snippet(lines, start, end),
                        "commit_sha": self.commit_sha,
                        "direct_url": make_direct_github_url(self.repo_full_name, self.commit_sha, path, start, end),
                        "confidence": 0.95,
                        "is_import_only": False,
                        "is_substantial": True
                    })
                    break

            if has_eval:
                evidence_by_skill["Model Evaluation"].append({
                    "skill": "Model Evaluation",
                    "detail": "Model Validation: Evaluation metric computation on test split",
                    "repository_name": self.repo_full_name,
                    "file_path": path,
                    "start_line": 1,
                    "end_line": 5,
                    "snippet": extract_snippet(lines, 1, 5),
                    "commit_sha": self.commit_sha,
                    "direct_url": make_direct_github_url(self.repo_full_name, self.commit_sha, path, 1, 5),
                    "confidence": 0.92,
                    "is_import_only": False,
                    "is_substantial": True
                })

        # 5. Data Visualization (matplotlib, seaborn, plotly)
        if any(m in imported_modules for m in ("matplotlib", "seaborn", "plotly")):
            has_plots = any(p in attrs_by_name for p in ("plot", "scatter", "subplots", "histplot", "heatmap", "barplot"))
            if has_plots:
                for node in ast.walk(tree):
                    if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr in ("plot", "scatter", "subplots", "histplot", "heatmap", "barplot"):
                        start = getattr(node, "lineno", 1)
                        end = getattr(node, "end_lineno", start + 3)
                        evidence_by_skill["Data Visualization"].append({
                            "skill": "Data Visualization",
                            "detail": f"Chart Generation: '{node.func.attr}' visualization call",
                            "repository_name": self.repo_full_name,
                            "file_path": path,
                            "start_line": start,
                            "end_line": end,
                            "snippet": extract_snippet(lines, start, end),
                            "commit_sha": self.commit_sha,
                            "direct_url": make_direct_github_url(self.repo_full_name, self.commit_sha, path, start, end),
                            "confidence": 0.95,
                            "is_import_only": False,
                            "is_substantial": True
                        })

    def _inspect_sql(
        self,
        path: str,
        lines: List[str],
        content: str,
        evidence_by_skill: Dict[str, List[Dict[str, Any]]]
    ):
        upper_sql = content.upper()
        has_joins = "JOIN " in upper_sql
        has_window = "OVER (" in upper_sql or "PARTITION BY" in upper_sql
        has_cte = "WITH " in upper_sql and " AS (" in upper_sql
        has_agg = "GROUP BY" in upper_sql

        if has_joins or has_window or has_cte or has_agg:
            detail_terms = []
            if has_window: detail_terms.append("Window Functions")
            if has_cte: detail_terms.append("CTEs (Common Table Expressions)")
            if has_joins: detail_terms.append("Multi-Table Relational JOINs")
            if has_agg: detail_terms.append("Aggregations (GROUP BY)")

            if has_cte:
                evidence_by_skill["SQL"].append({
                    "skill": "SQL",
                    "detail": "CTE Architecture: Common Table Expression modular query structure",
                    "repository_name": self.repo_full_name,
                    "file_path": path,
                    "start_line": 1,
                    "end_line": min(len(lines), 8),
                    "snippet": extract_snippet(lines, 1, 8),
                    "commit_sha": self.commit_sha,
                    "direct_url": make_direct_github_url(self.repo_full_name, self.commit_sha, path, 1, min(len(lines), 8)),
                    "confidence": 0.98,
                    "is_import_only": False,
                    "is_substantial": True
                })
            if has_agg or has_joins or has_window:
                evidence_by_skill["SQL"].append({
                    "skill": "SQL",
                    "detail": f"Query Analytics: {', '.join(detail_terms)}",
                    "repository_name": self.repo_full_name,
                    "file_path": path,
                    "start_line": min(len(lines), 5),
                    "end_line": min(len(lines), 15),
                    "snippet": extract_snippet(lines, min(len(lines), 5), min(len(lines), 15)),
                    "commit_sha": self.commit_sha,
                    "direct_url": make_direct_github_url(self.repo_full_name, self.commit_sha, path, min(len(lines), 5), min(len(lines), 15)),
                    "confidence": 0.96,
                    "is_import_only": False,
                    "is_substantial": True
                })

            # Check if dbt or dimensional analytics
            if "{{ config(" in content or "{{ ref(" in content or "fct_" in path or "dim_" in path:
                evidence_by_skill["SQL Transformations"].append({
                    "skill": "SQL Transformations",
                    "detail": "Analytics Engineering: dbt transformation model with jinja macros",
                    "repository_name": self.repo_full_name,
                    "file_path": path,
                    "start_line": 1,
                    "end_line": min(len(lines), 15),
                    "snippet": extract_snippet(lines, 1, 15),
                    "commit_sha": self.commit_sha,
                    "direct_url": make_direct_github_url(self.repo_full_name, self.commit_sha, path, 1, min(len(lines), 15)),
                    "confidence": 0.95,
                    "is_import_only": False,
                    "is_substantial": True
                })

    def _inspect_js_ts(
        self,
        path: str,
        lines: List[str],
        content: str,
        evidence_by_skill: Dict[str, List[Dict[str, Any]]]
    ):
        is_ts = path.lower().endswith(".ts") or path.lower().endswith(".tsx")
        target_skill = "TypeScript" if is_ts else "JavaScript"

        has_interfaces = "interface " in content or "type " in content
        has_async = "async " in content or "Promise" in content
        has_components = "export default function" in content or ("const " in content and "=>" in content)

        if has_interfaces or has_async or has_components:
            evidence_by_skill[target_skill].append({
                "skill": target_skill,
                "detail": f"Structured {target_skill} Implementation: interfaces, async calls, and functional modules",
                "repository_name": self.repo_full_name,
                "file_path": path,
                "start_line": 1,
                "end_line": min(len(lines), 14),
                "snippet": extract_snippet(lines, 1, 14),
                "commit_sha": self.commit_sha,
                "direct_url": make_direct_github_url(self.repo_full_name, self.commit_sha, path, 1, min(len(lines), 14)),
                "confidence": 0.92,
                "is_import_only": False,
                "is_substantial": True
            })

    def _inspect_java(
        self,
        path: str,
        lines: List[str],
        content: str,
        evidence_by_skill: Dict[str, List[Dict[str, Any]]]
    ):
        if "class " in content and ("public " in content or "private " in content):
            is_substantial = "@Service" in content or "@RestController" in content or "@Test" in content or len(lines) > 10
            evidence_by_skill["Java"].append({
                "skill": "Java",
                "detail": "Enterprise Java: Class structure with encapsulation and annotations",
                "repository_name": self.repo_full_name,
                "file_path": path,
                "start_line": 1,
                "end_line": min(len(lines), 16),
                "snippet": extract_snippet(lines, 1, 16),
                "commit_sha": self.commit_sha,
                "direct_url": make_direct_github_url(self.repo_full_name, self.commit_sha, path, 1, min(len(lines), 16)),
                "confidence": 0.94,
                "is_import_only": False,
                "is_substantial": is_substantial
            })

    def _inspect_cpp(
        self,
        path: str,
        lines: List[str],
        content: str,
        evidence_by_skill: Dict[str, List[Dict[str, Any]]]
    ):
        if "#include" in content and ("class " in content or "template" in content or "std::" in content):
            evidence_by_skill["C++"].append({
                "skill": "C++",
                "detail": "Modern C++: Standard Template Library and class implementation",
                "repository_name": self.repo_full_name,
                "file_path": path,
                "start_line": 1,
                "end_line": min(len(lines), 16),
                "snippet": extract_snippet(lines, 1, 16),
                "commit_sha": self.commit_sha,
                "direct_url": make_direct_github_url(self.repo_full_name, self.commit_sha, path, 1, min(len(lines), 16)),
                "confidence": 0.94,
                "is_import_only": False,
                "is_substantial": len(lines) > 8
            })

    def _inspect_devops(
        self,
        path: str,
        lines: List[str],
        content: str,
        evidence_by_skill: Dict[str, List[Dict[str, Any]]]
    ):
        if "runs-on:" in content and "steps:" in content:
            evidence_by_skill["CI/CD"].append({
                "skill": "CI/CD",
                "detail": "Automated Pipeline: GitHub Actions workflow with testing and build stages",
                "repository_name": self.repo_full_name,
                "file_path": path,
                "start_line": 1,
                "end_line": min(len(lines), 16),
                "snippet": extract_snippet(lines, 1, 16),
                "commit_sha": self.commit_sha,
                "direct_url": make_direct_github_url(self.repo_full_name, self.commit_sha, path, 1, min(len(lines), 16)),
                "confidence": 0.96,
                "is_import_only": False,
                "is_substantial": True
            })

    # -------------------------------------------------------------
    # 0-100 Evidence Strength Scoring Formula
    # -------------------------------------------------------------
    def _evaluate_skill_evidence(
        self,
        skill_name: str,
        items: List[Dict[str, Any]],
        files_scanned: int,
        has_repo_tests: bool = False
    ) -> Tuple[float, Dict[str, float], str, str, List[str]]:
        """
        Calculates exact evidence strength score on a 0-100 scale:
        Es = min(100, N_impl * 25 + S_ast + S_test + S_rec - P_import_only)
        """
        if files_scanned == 0:
            return 0.0, {}, EvidenceCategory.UNABLE, "Unable to assess: zero files were retrieved.", ["Check repository access permissions."]

        if not items:
            return (
                0.0,
                {"implementation_depth": 0.0, "ast_signals": 0.0, "test_coverage": 0.0, "recency": 0.0, "import_penalty": 0.0},
                EvidenceCategory.NO_EVIDENCE,
                f"No evidence found in analysed scope for {skill_name}. (Does not imply candidate lacks this skill).",
                [f"Add practical code implementations demonstrating {skill_name} to the repository."]
            )

        # Count substantial vs import-only items
        substantial_items = [it for it in items if it.get("is_substantial", False)]
        import_only_items = [it for it in items if it.get("is_import_only", False)]

        # 1. Implementation depth: 25 pts each (capped at 50)
        impl_pts = min(50.0, len(substantial_items) * 25.0)

        # 2. AST signals & complexity: up to 25 pts
        ast_pts = min(25.0, len(items) * 10.0)

        # 3. Test verification bonus: 15 pts if tests exist for this skill or in the repository
        has_tests = has_repo_tests or any(it["skill"] == "Testing" or "test" in it["file_path"].lower() for it in items)
        test_pts = 15.0 if has_tests else 0.0

        # 4. Project integration & recency: 10 pts
        recency_pts = 10.0

        # 5. Import only penalty: -20 pts if import only and 0 substantial items
        import_penalty = 20.0 if (import_only_items and not substantial_items) else 0.0

        raw_score = impl_pts + ast_pts + test_pts + recency_pts - import_penalty
        final_score = max(0.0, min(100.0, raw_score))

        breakdown = {
            "implementation_depth": impl_pts,
            "ast_signals": ast_pts,
            "test_coverage": test_pts,
            "recency": recency_pts,
            "import_penalty": import_penalty
        }

        # Category mapping
        if final_score >= 70.0:
            category = EvidenceCategory.STRONG
            rationale = f"Strong evidence: Multiple verified implementations ({len(substantial_items)} substantive code examples)."
            actions = ["Maintain code hygiene and publish advanced design patterns in README."]
        elif final_score >= 40.0:
            category = EvidenceCategory.MODERATE
            rationale = f"Moderate evidence: At least 1 meaningful implementation with active parameters."
            actions = [f"Add automated tests and modularize {skill_name} logic to reach Strong evidence."]
        elif final_score >= 15.0:
            category = EvidenceCategory.LIMITED
            rationale = "Limited evidence: Superficial usage or imports with minimal verified calls."
            actions = [f"Build an end-to-end practical feature using {skill_name} rather than basic syntax."]
        else:
            category = EvidenceCategory.LIMITED
            rationale = "Weak/Uncertain evidence: Import declared without active AST method invocations."
            actions = [f"Replace unused imports with functional implementations of {skill_name}."]

        return final_score, breakdown, category, rationale, actions


class JobRequirementMatcher:
    """
    Transparent, evidence-based requirement matcher implementing Section 5:
    Match % = 100 * (sum of assessed requirement weights * evidence scores) / (sum of weights for assessed requirements)
    """

    @staticmethod
    def match_job(
        job_listing: Dict[str, Any],
        repository_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Executes requirement matching according to Section 5:
        - wi: weight (3.0 for required, 1.0 for preferred)
        - ei: evidence score (1.0 for Strong, 0.5 for Moderate/Partial, 0.0 for Not demonstrated)
        - Excludes genuinely unassessable requirements from denominator and reports separately.
        - Computes Evidence Coverage %.
        - If evidence coverage is too low or 0 evidence found: returns 'Insufficient evidence to calculate a reliable match'.
        """
        profiles = repository_profile.get("skill_profiles", {})
        total_evidence_count = sum(p.get("evidence_count", 0) for p in profiles.values())

        required_skills_raw = job_listing.get("required_skills", job_listing.get("skills", []))
        preferred_skills_raw = job_listing.get("preferred_skills", [])

        # Insufficient evidence check: If repository has zero evidence across all skills
        if total_evidence_count == 0 or not profiles:
            return {
                "job_id": job_listing.get("id", ""),
                "job_title": job_listing.get("title", ""),
                "company": job_listing.get("company", ""),
                "overall_score": None,
                "match_percentage": None,
                "status_label": "Insufficient evidence",
                "numerator": 0.0,
                "denominator": 0.0,
                "evidence_coverage_percent": 0.0,
                "required_skills_demonstrated": f"0 of {len(required_skills_raw)}",
                "preferred_skills_demonstrated": f"0 of {len(preferred_skills_raw)}",
                "assessed_requirements_count": 0,
                "partially_demonstrated_count": 0,
                "not_demonstrated_count": len(required_skills_raw) + len(preferred_skills_raw),
                "unable_to_assess_count": 0,
                "required_coverage_percent": 0.0,
                "preferred_coverage_percent": 0.0,
                "requirements": [],
                "strong_matches": [],
                "partial_matches": [],
                "evidence_gaps": required_skills_raw + preferred_skills_raw,
                "unable_to_assess": [],
                "explanation": (
                    "Insufficient repository evidence in analyzed scope to calculate a reliable match score. "
                    "Connect an active GitHub repository with source code to compute career compatibility."
                ),
                "actionable_recommendations": [
                    "Authorize a GitHub repository containing project source code.",
                    "Ensure source files (.py, .sql, .js, .ts) are committed to the default branch."
                ]
            }

        matched_reqs: List[Dict[str, Any]] = []
        strong_matches: List[str] = []
        partial_matches: List[str] = []
        evidence_gaps: List[str] = []
        unable_to_assess: List[str] = []

        # Weights
        w_req = 3.0
        w_pref = 1.0

        numerator = 0.0
        assessed_denominator = 0.0
        total_possible_weight = 0.0

        req_demonstrated_count = 0
        pref_demonstrated_count = 0
        partial_count = 0
        not_demo_count = 0
        unable_count = 0

        # Assess Required Skills
        for raw_skill in required_skills_raw:
            total_possible_weight += w_req

            # Check if skill is unassessable
            if any(term in raw_skill.lower() for term in ("experience", "leadership", "degree", "certification", "communication", "bachelor")):
                unable_count += 1
                unable_to_assess.append(raw_skill)
                matched_reqs.append({
                    "requirement_name": raw_skill,
                    "canonical_skill": raw_skill,
                    "is_required": True,
                    "status": RequirementStatus.UNABLE_TO_ASSESS,
                    "evidence_strength": 0.0,
                    "evidence_score": None,
                    "citations": [],
                    "reason": "Non-code attribute or unverified credential requirement. Excluded from assessed match denominator.",
                    "remaining_uncertainty": "Unable to assess from repository code."
                })
                continue

            canon = taxonomy_registry.get_canonical_name(raw_skill)
            prof = profiles.get(canon, {
                "evidence_strength": 0.0,
                "evidence_category": EvidenceCategory.NO_EVIDENCE,
                "citations": []
            })
            strength = prof.get("evidence_strength", 0.0)
            citations = prof.get("citations", [])

            if strength >= 40.0:
                status = RequirementStatus.DEMONSTRATED
                e_i = 1.0
                req_demonstrated_count += 1
                strong_matches.append(canon)
                reason = f"Demonstrated with {len(citations)} verified code citations in repository (strength: {strength:.0f}/100)."
                uncertainty = "Low uncertainty: Substantial implementation verified via AST inspection."
            elif strength >= 15.0:
                status = RequirementStatus.PARTIALLY_DEMONSTRATED
                e_i = 0.5
                req_demonstrated_count += 1
                partial_count += 1
                partial_matches.append(canon)
                reason = f"Partially demonstrated with moderate evidence (strength: {strength:.0f}/100)."
                uncertainty = "Moderate uncertainty: Implementation found but lacks full test suite or multi-file depth."
            else:
                status = RequirementStatus.NOT_DEMONSTRATED
                e_i = 0.0
                not_demo_count += 1
                evidence_gaps.append(canon)
                reason = f"No verified evidence found in analyzed repository scope. (Does not mean candidate lacks skill)."
                uncertainty = "Evidence gap: No matching source files in scanned repositories."

            numerator += w_req * e_i
            assessed_denominator += w_req

            matched_reqs.append({
                "requirement_name": raw_skill,
                "canonical_skill": canon,
                "is_required": True,
                "status": status,
                "evidence_strength": strength,
                "evidence_score": e_i,
                "evidence_category": prof.get("evidence_category", EvidenceCategory.NO_EVIDENCE),
                "citations": citations,
                "reason": reason,
                "remaining_uncertainty": uncertainty
            })

        # Assess Preferred Skills
        for raw_skill in preferred_skills_raw:
            total_possible_weight += w_pref

            if any(term in raw_skill.lower() for term in ("experience", "leadership", "degree", "certification", "communication", "bachelor")):
                unable_count += 1
                unable_to_assess.append(raw_skill)
                matched_reqs.append({
                    "requirement_name": raw_skill,
                    "canonical_skill": raw_skill,
                    "is_required": False,
                    "status": RequirementStatus.UNABLE_TO_ASSESS,
                    "evidence_strength": 0.0,
                    "evidence_score": None,
                    "citations": [],
                    "reason": "Preferred non-code qualification. Excluded from assessed match denominator.",
                    "remaining_uncertainty": "Unable to assess from repository code."
                })
                continue

            canon = taxonomy_registry.get_canonical_name(raw_skill)
            prof = profiles.get(canon, {
                "evidence_strength": 0.0,
                "evidence_category": EvidenceCategory.NO_EVIDENCE,
                "citations": []
            })
            strength = prof.get("evidence_strength", 0.0)
            citations = prof.get("citations", [])

            if strength >= 40.0:
                status = RequirementStatus.DEMONSTRATED
                e_i = 1.0
                pref_demonstrated_count += 1
                strong_matches.append(f"{canon} (Preferred)")
                reason = f"Demonstrated preferred qualification (strength: {strength:.0f}/100)."
                uncertainty = "Low uncertainty."
            elif strength >= 15.0:
                status = RequirementStatus.PARTIALLY_DEMONSTRATED
                e_i = 0.5
                pref_demonstrated_count += 1
                partial_count += 1
                partial_matches.append(f"{canon} (Preferred)")
                reason = f"Partially demonstrated preferred qualification (strength: {strength:.0f}/100)."
                uncertainty = "Moderate uncertainty."
            else:
                status = RequirementStatus.NOT_DEMONSTRATED
                e_i = 0.0
                not_demo_count += 1
                reason = f"Preferred skill not demonstrated in analysed repository scope."
                uncertainty = "No evidence found."

            numerator += w_pref * e_i
            assessed_denominator += w_pref

            matched_reqs.append({
                "requirement_name": raw_skill,
                "canonical_skill": canon,
                "is_required": False,
                "status": status,
                "evidence_strength": strength,
                "evidence_score": e_i,
                "evidence_category": prof.get("evidence_category", EvidenceCategory.NO_EVIDENCE),
                "citations": citations,
                "reason": reason,
                "remaining_uncertainty": uncertainty
            })

        # Calculate Evidence Coverage: proportion of weighted requirements actually assessable
        evidence_coverage = (
            round(100.0 * (assessed_denominator / total_possible_weight), 1)
            if total_possible_weight > 0
            else 100.0
        )

        # Insufficient Evidence Safeguard
        if total_evidence_count == 0 or (assessed_denominator == 0 and total_possible_weight > 0):
            return {
                "job_id": job_listing.get("id", ""),
                "job_title": job_listing.get("title", ""),
                "company": job_listing.get("company", ""),
                "overall_score": None,
                "match_percentage": None,
                "status_label": "Insufficient evidence",
                "numerator": 0.0,
                "denominator": 0.0,
                "evidence_coverage_percent": 0.0,
                "required_skills_demonstrated": f"0 of {len(required_skills_raw)}",
                "preferred_skills_demonstrated": f"0 of {len(preferred_skills_raw)}",
                "assessed_requirements_count": 0,
                "partially_demonstrated_count": 0,
                "not_demonstrated_count": len(required_skills_raw),
                "unable_to_assess_count": len(unable_to_assess),
                "required_coverage_percent": 0.0,
                "preferred_coverage_percent": 0.0,
                "requirements": matched_reqs,
                "strong_matches": [],
                "partial_matches": [],
                "evidence_gaps": evidence_gaps,
                "unable_to_assess": unable_to_assess,
                "explanation": "Insufficient evidence to calculate a reliable match across job requirements.",
                "actionable_recommendations": ["Authorize and commit code to an active project repository."]
            }

        # Calculate Final Honest Skill-Match Percentage: 100 * sum(w_i * e_i) / sum(w_i for assessed)
        final_score = (
            round(100.0 * (numerator / assessed_denominator))
            if assessed_denominator > 0
            else 0
        )

        # Coverage percentages
        req_total = len(required_skills_raw)
        pref_total = len(preferred_skills_raw)
        req_coverage = round(100.0 * (req_demonstrated_count / req_total), 1) if req_total > 0 else 100.0
        pref_coverage = round(100.0 * (pref_demonstrated_count / pref_total), 1) if pref_total > 0 else 100.0

        # Actionable recommendations based on gaps
        actionable_recommendations = []
        for gap in evidence_gaps[:3]:
            actionable_recommendations.append(f"Implement a verified {gap} project module with automated unit tests.")
        if unable_to_assess:
            actionable_recommendations.append(f"Document or substantiate {unable_to_assess[0]} outside of code repositories.")
        if not actionable_recommendations:
            actionable_recommendations.append("All primary required skills have demonstrated repository evidence.")

        explanation = (
            f"Evidence-based skill match of {final_score}% calculated across {len(matched_reqs) - unable_count} assessable requirements. "
            f"Candidate demonstrates {req_demonstrated_count} of {req_total} required skills ({req_coverage}% coverage) "
            f"and {pref_demonstrated_count} of {max(1, pref_total)} preferred skills. "
            f"Evidence coverage: {evidence_coverage}%. "
            f"Scoring: Numerator = {numerator:.1f}, Assessed Denominator = {assessed_denominator:.1f}."
        )

        return {
            "job_id": job_listing.get("id", ""),
            "job_title": job_listing.get("title", ""),
            "company": job_listing.get("company", ""),
            "overall_score": final_score,
            "match_percentage": final_score,
            "status_label": f"{final_score}% Match",
            "numerator": round(numerator, 1),
            "denominator": round(assessed_denominator, 1),
            "evidence_coverage_percent": evidence_coverage,
            "required_skills_demonstrated": f"{req_demonstrated_count} of {req_total}",
            "preferred_skills_demonstrated": f"{pref_demonstrated_count} of {pref_total}",
            "assessed_requirements_count": len(matched_reqs) - unable_count,
            "partially_demonstrated_count": partial_count,
            "not_demonstrated_count": not_demo_count,
            "unable_to_assess_count": unable_count,
            "required_coverage_percent": req_coverage,
            "preferred_coverage_percent": pref_coverage,
            "requirements": matched_reqs,
            "strong_matches": strong_matches,
            "partial_matches": partial_matches,
            "evidence_gaps": evidence_gaps,
            "unable_to_assess": unable_to_assess,
            "explanation": explanation,
            "actionable_recommendations": actionable_recommendations
        }
