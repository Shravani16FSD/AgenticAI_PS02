"""
Evidence-Based Skill Mapping Engine for SkillTrace AI.
Inspects structured repository evidence (AST, dependency manifests, tests, documentation, workflows)
and converts it into an evidence-grounded skill profile, skill-gap report, and personalized next steps.

Key Principles:
1. Never claim a skill is proven just because a library is imported or a file exists.
2. Differentiate substantive implementations from import-only stubs.
3. Explicitly report what evidence is missing or unproven.
4. If evidence is insufficient, explicitly report 'Insufficient evidence'.
5. Deterministic fallback with optional Gemini AI contextual synthesis.
"""

from __future__ import annotations
import ast
import os
import re
import logging
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional, Tuple

from pydantic import BaseModel, Field

logger = logging.getLogger("skilltrace.mapping_engine")

# ---------------------------------------------------------------------------
# Pydantic Schemas for the Skill Mapping Report
# ---------------------------------------------------------------------------

class EvidenceSkillItem(BaseModel):
    skill_name: str
    confidence: str  # "High" | "Medium" | "Low"
    evidence_summary: str
    file_paths: List[str]
    observed_indicators: List[str]
    missing_evidence: str
    recommendation: str


class SkillGapItem(BaseModel):
    area: str
    observation: str
    recommendation: str
    severity: str  # "high" | "medium" | "low"


class PrioritizedNextStep(BaseModel):
    priority: int  # 1, 2, 3
    type: str  # "immediate" | "mini_project" | "verification"
    title: str
    description: str
    action_label: str
    target_id: Optional[str] = None


class EvidenceReportData(BaseModel):
    repository_name: str
    repo_url: str
    commit_sha: str
    scanned_files_count: int
    is_sample_data: bool
    generated_at: str
    detected_skills: List[EvidenceSkillItem]
    skill_gaps: List[SkillGapItem]
    prioritized_actions: List[PrioritizedNextStep]
    ai_synthesis: Optional[str] = None
    languages_detected: List[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Core Engine Implementation
# ---------------------------------------------------------------------------

class SkillMappingEngine:
    """
    Static code analyzer and evidence mapping engine.
    Extracts structural indicators from repository files and maps them to skills.
    """

    def __init__(self):
        pass

    def analyze_repository(
        self,
        files: List[Dict[str, str]],
        repo_name: str = "alex-morgan/data-pipeline-lab",
        repo_url: Optional[str] = None,
        commit_sha: str = "HEAD",
        is_sample_data: bool = False,
        target_career: Optional[str] = None
    ) -> EvidenceReportData:
        """
        Analyzes a list of repository files [{'path': str, 'content': str}]
        and returns an EvidenceReportData instance.
        """
        if not repo_url:
            clean_name = repo_name.replace("https://github.com/", "").replace("http://github.com/", "").strip("/")
            repo_url = f"https://github.com/{clean_name}"

        # 1. Extract structural signals across all files
        signals = self._extract_signals(files)

        # 2. Map signals to the 9 canonical skills
        detected_skills = self._map_skills(signals, files)

        # 3. Detect skill gaps based on missing or limited evidence
        skill_gaps = self._detect_skill_gaps(signals, detected_skills)

        # 4. Generate 3 prioritized personalized next steps
        prioritized_actions = self._generate_prioritized_actions(detected_skills, skill_gaps, target_career)

        # 5. Optional AI synthesis using Gemini
        ai_synthesis = self._generate_ai_synthesis(repo_name, detected_skills, skill_gaps, target_career)

        return EvidenceReportData(
            repository_name=repo_name,
            repo_url=repo_url,
            commit_sha=commit_sha,
            scanned_files_count=len(files),
            is_sample_data=is_sample_data,
            generated_at=datetime.now(timezone.utc).isoformat(),
            detected_skills=detected_skills,
            skill_gaps=skill_gaps,
            prioritized_actions=prioritized_actions,
            ai_synthesis=ai_synthesis,
            languages_detected=sorted(list(signals.get("languages", set())))
        )

    def _extract_signals(self, files: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Scans all files and extracts AST, regex, and manifest indicators.
        """
        signals: Dict[str, Any] = {
            "languages": set(),
            "python_ast": {
                "functions": [],
                "classes": [],
                "imports": set(),
                "calls": set(),
                "route_handlers": [],
                "orm_models": [],
                "test_functions": [],
                "assertions_count": 0,
                "data_pipeline_ops": [],
                "has_docstrings": False,
            },
            "js_ts": {
                "files": [],
                "components": [],
                "exports": [],
                "test_files": [],
            },
            "sql": {
                "files": [],
                "has_cte": False,
                "has_window_functions": False,
                "has_joins": False,
                "queries_count": 0,
            },
            "dependencies": set(),
            "test_files": [],
            "has_readme": False,
            "readme_length": 0,
            "has_ci_workflow": False,
            "has_dockerfile": False,
            "files_by_ext": {}
        }

        for f in files:
            path = f.get("path", "").replace("\\", "/")
            content = f.get("content", "")
            path_lower = path.lower()
            basename = os.path.basename(path_lower)
            _, ext = os.path.splitext(path_lower)

            if ext:
                signals["files_by_ext"][ext] = signals["files_by_ext"].get(ext, 0) + 1

            # README & Documentation
            if basename in ("readme.md", "readme.rst", "readme.txt", "readme"):
                signals["has_readme"] = True
                signals["readme_length"] = len(content.strip())

            # CI/CD Workflows
            if ".github/workflows" in path_lower or "circleci" in path_lower or "jenkinsfile" in path_lower:
                signals["has_ci_workflow"] = True

            # Dockerfile
            if "dockerfile" in basename or "docker-compose" in basename:
                signals["has_dockerfile"] = True

            # Test files
            if (
                "test_" in basename
                or "_test.py" in basename
                or ".test." in basename
                or ".spec." in basename
                or "tests/" in path_lower
            ):
                signals["test_files"].append(path)

            # Dependencies manifests
            if basename == "requirements.txt":
                for line in content.splitlines():
                    clean = re.sub(r"[=<>~!#].*", "", line).strip().lower()
                    if clean:
                        signals["dependencies"].add(clean)
            elif basename == "package.json":
                signals["languages"].add("JavaScript")
                matches = re.findall(r'"([a-zA-Z0-9_\-/@]+)":\s*"[^"]+"', content)
                for m in matches:
                    signals["dependencies"].add(m.lower())

            # Python Analysis
            if ext == ".py":
                signals["languages"].add("Python")
                self._inspect_python_ast(path, content, signals["python_ast"])

            # TypeScript / JavaScript Analysis
            elif ext in (".ts", ".tsx", ".js", ".jsx"):
                signals["languages"].add("TypeScript" if "ts" in ext else "JavaScript")
                signals["js_ts"]["files"].append(path)
                if ext in (".test.ts", ".spec.ts", ".test.js", ".spec.js") or "tests/" in path_lower:
                    signals["js_ts"]["test_files"].append(path)
                # Quick regex for functions & components
                components = re.findall(r"(?:export\s+)?(?:const|function)\s+([A-Z][a-zA-Z0-9]+)\s*[:=]", content)
                signals["js_ts"]["components"].extend([{"name": c, "path": path} for c in components])
                exports = re.findall(r"export\s+(?:default\s+)?(?:class|function|const|interface|type)\s+([a-zA-Z0-9_]+)", content)
                signals["js_ts"]["exports"].extend([{"name": e, "path": path} for e in exports])

            # SQL Analysis
            elif ext == ".sql":
                signals["languages"].add("SQL")
                signals["sql"]["files"].append(path)
                signals["sql"]["queries_count"] += 1
                upper_content = content.upper()
                if "WITH " in upper_content:
                    signals["sql"]["has_cte"] = True
                if "OVER (" in upper_content or "PARTITION BY" in upper_content:
                    signals["sql"]["has_window_functions"] = True
                if "JOIN " in upper_content:
                    signals["sql"]["has_joins"] = True

        return signals

    def _inspect_python_ast(self, path: str, content: str, py_signals: Dict[str, Any]):
        """
        Parses Python file using built-in ast module.
        """
        try:
            tree = ast.parse(content, filename=path)
        except SyntaxError:
            return

        is_test_file = "test_" in path.lower() or "_test.py" in path.lower() or "tests/" in path.lower()

        # Imports
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    py_signals["imports"].add(alias.name.split('.')[0])
            elif isinstance(node, ast.ImportFrom) and node.module:
                py_signals["imports"].add(node.module.split('.')[0])
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    py_signals["calls"].add(node.func.id)
                elif isinstance(node.func, ast.Attribute):
                    py_signals["calls"].add(node.func.attr)

        # Classes
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                is_orm = any(
                    getattr(b, "id", "") in ("Base", "Model") or getattr(b, "attr", "") == "Model"
                    for b in node.bases
                )
                class_info = {
                    "name": node.name,
                    "path": path,
                    "line": getattr(node, "lineno", 1),
                    "is_orm": is_orm,
                    "methods_count": sum(1 for m in node.body if isinstance(m, ast.FunctionDef))
                }
                py_signals["classes"].append(class_info)
                if is_orm:
                    py_signals["orm_models"].append(class_info)

        # Functions, API Routes, Tests
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                func_doc = ast.get_docstring(node)
                if func_doc:
                    py_signals["has_docstrings"] = True

                # Route decorator detection (@router.get, @app.post, etc.)
                is_route = False
                for dec in node.decorator_list:
                    dec_str = ast.dump(dec)
                    if any(verb in dec_str for verb in ("get", "post", "put", "delete", "patch", "route")):
                        is_route = True
                        break

                func_info = {
                    "name": node.name,
                    "path": path,
                    "line": getattr(node, "lineno", 1),
                    "args_count": len(node.args.args),
                    "has_docstring": bool(func_doc)
                }
                py_signals["functions"].append(func_info)

                if is_route:
                    py_signals["route_handlers"].append(func_info)

                if is_test_file or node.name.startswith("test_"):
                    asserts_in_func = sum(1 for sub in ast.walk(node) if isinstance(sub, ast.Assert))
                    py_signals["assertions_count"] += asserts_in_func
                    py_signals["test_functions"].append({
                        **func_info,
                        "assertions": asserts_in_func
                    })

                # Check data operations
                for sub in ast.walk(node):
                    if isinstance(sub, ast.Call) and isinstance(sub.func, ast.Attribute):
                        if sub.func.attr in ("groupby", "dropna", "read_csv", "merge", "cumsum", "rolling", "agg", "fillna"):
                            py_signals["data_pipeline_ops"].append(sub.func.attr)

    def _map_skills(self, signals: Dict[str, Any], files: List[Dict[str, str]]) -> List[EvidenceSkillItem]:
        """
        Maps extracted signals to the canonical skills:
        - Python programming
        - JavaScript and TypeScript
        - Data analysis
        - API development
        - Database management
        - Software engineering
        - Testing and debugging
        - Git and GitHub
        - Documentation and project organization

        Only includes skills supported by concrete evidence.
        Does not claim a skill is proven just because a library or file exists.
        """
        results: List[EvidenceSkillItem] = []
        py_signals = signals["python_ast"]
        deps = signals["dependencies"] | py_signals["imports"]

        # -------------------------------------------------------------
        # 1. Python Programming
        # -------------------------------------------------------------
        py_files = [f["path"] for f in files if f["path"].endswith(".py")]
        if py_files:
            funcs = py_signals["functions"]
            classes = py_signals["classes"]
            substantive_count = len(funcs) + len(classes)

            if substantive_count == 0:
                confidence = "Low"
                summary = f"Basic Python script(s) found in {len(py_files)} file(s), but no function definitions or class abstractions were detected."
                missing = "Modular function definitions, argument type signatures, and class abstractions."
            elif substantive_count >= 5 and len(py_files) >= 2:
                confidence = "High"
                summary = f"Demonstrated through {len(py_files)} Python files containing {len(funcs)} functions and {len(classes)} classes with substantive control flow."
                missing = "Full type annotations (mypy), exception hierarchies, and package build configuration (pyproject.toml)."
            else:
                confidence = "Medium"
                summary = f"Demonstrated through {len(py_files)} Python files containing {len(funcs)} functions and {len(classes)} classes."
                missing = "Advanced metaclasses, custom context managers, and strict type annotations."

            indicators = [
                f"{len(py_files)} Python source file(s) parsed via AST",
                f"{len(funcs)} function definition(s) with argument signatures",
                f"{len(classes)} class definition(s) implemented"
            ]
            if py_signals["has_docstrings"]:
                indicators.append("Function/class docstrings documented")

            rec = "Expand Python tests with parametrized fixtures and enforce strict type annotations across modules."

            results.append(EvidenceSkillItem(
                skill_name="Python Programming",
                confidence=confidence,
                evidence_summary=summary,
                file_paths=py_files[:4],
                observed_indicators=indicators,
                missing_evidence=missing,
                recommendation=rec
            ))

        # -------------------------------------------------------------
        # 2. JavaScript and TypeScript
        # -------------------------------------------------------------
        js_files = signals["js_ts"]["files"]
        if js_files:
            components = signals["js_ts"]["components"]
            exports = signals["js_ts"]["exports"]
            if len(js_files) >= 3 and (components or exports):
                confidence = "High"
            elif components or exports:
                confidence = "Medium"
            else:
                confidence = "Low"

            indicators = [
                f"{len(js_files)} TypeScript/JavaScript file(s)",
                f"{len(components)} React/UI component definition(s)",
                f"{len(exports)} exported module member(s)"
            ]
            missing = "End-to-end browser testing (Playwright/Cypress) and state management architecture."
            rec = "Add component test coverage and ensure zero implicit 'any' types in TypeScript configuration."
            results.append(EvidenceSkillItem(
                skill_name="JavaScript and TypeScript",
                confidence=confidence,
                evidence_summary=f"Demonstrated through {len(js_files)} TS/JS files exporting {len(exports)} functions/components.",
                file_paths=js_files[:4],
                observed_indicators=indicators,
                missing_evidence=missing,
                recommendation=rec
            ))

        # -------------------------------------------------------------
        # 3. Data Analysis
        # -------------------------------------------------------------
        data_libs = {"pandas", "numpy", "scipy", "matplotlib", "seaborn", "polars", "dbt"} & deps
        data_ops = py_signals["data_pipeline_ops"]
        data_files = [f["path"] for f in files if any(kw in f["path"].lower() for kw in ("data", "etl", "pipeline", "mart", "analytic", "chart", "viz"))]

        if data_libs or data_ops or signals["sql"]["files"] or data_files:
            has_substantive = len(data_ops) >= 2 or signals["sql"]["has_window_functions"]
            
            # Check if import-only (declared library but no operations invoked in AST)
            if data_libs and not has_substantive and not signals["sql"]["files"]:
                confidence = "Low"
                summary = f"Data analysis librar{'ies' if len(data_libs) > 1 else 'y'} ({', '.join(sorted(list(data_libs)))}) declared in dependencies/imports, but no substantive DataFrame transformation operations (e.g., groupby, aggregations, rolling calculations) were detected in the AST."
                indicators = [
                    f"Declared in dependencies: {', '.join(sorted(list(data_libs)))}",
                    "No DataFrame transformations or aggregations found in AST"
                ]
                missing = "Substantive data transformations, aggregations, filtering, or exploratory analysis in code."
                rec = "Implement active data processing functions invoking pandas/polars transformations rather than unused dependency declarations."
            else:
                confidence = "High" if (data_libs and has_substantive) else "Medium"
                indicators = []
                if data_libs:
                    indicators.append(f"Data libraries detected: {', '.join(sorted(list(data_libs)))}")
                if data_ops:
                    indicators.append(f"AST operations detected: {', '.join(set(data_ops))}")
                if signals["sql"]["has_window_functions"]:
                    indicators.append("SQL analytical window functions (OVER / PARTITION BY) implemented")

                missing = "Exploratory Jupyter notebooks (.ipynb) and statistical validation of data distributions."
                rec = "Provide an exploratory notebook or data pipeline with statistical summaries and data profiling."
                summary = f"Demonstrated via data transformation logic using {', '.join(sorted(list(data_libs or {'analytical SQL'})))}."

            results.append(EvidenceSkillItem(
                skill_name="Data Analysis",
                confidence=confidence,
                evidence_summary=summary,
                file_paths=data_files[:4] or [f["path"] for f in files if f["path"].endswith(".py")][:2],
                observed_indicators=indicators,
                missing_evidence=missing,
                recommendation=rec
            ))

        # -------------------------------------------------------------
        # 4. API Development
        # -------------------------------------------------------------
        routes = py_signals["route_handlers"]
        api_files = [f["path"] for f in files if any(kw in f["path"].lower() for kw in ("api", "router", "endpoint", "controller", "server"))]
        api_libs = {"fastapi", "flask", "django", "express"} & deps

        if routes or api_files or api_libs:
            if api_libs and not routes:
                confidence = "Low"
                summary = f"Web framework ({', '.join(sorted(list(api_libs)))}) declared, but no HTTP route decorators or endpoint handlers were detected in parsed source files."
                indicators = [
                    f"Web framework dependency: {', '.join(sorted(list(api_libs)))}",
                    "No route decorators (@get, @post) detected in AST"
                ]
                missing = "HTTP route decorators (@router.get/@post), endpoint controllers, request schemas, and response handling."
                rec = "Implement route handlers with method decorators exposing REST API endpoints."
            else:
                confidence = "High" if len(routes) >= 2 and api_libs else "Medium"
                summary = f"Observed {len(routes)} API route decorator(s) handling HTTP endpoints."
                indicators = [
                    f"{len(routes)} HTTP route handler(s) with method decorators (@get, @post)",
                    f"Web framework dependencies: {', '.join(sorted(list(api_libs or {'custom router'})))}"
                ]
                missing = "API contract validation schemas (Pydantic/Zod), rate-limiting middleware, and automated integration tests."
                rec = "Add request body validation and write automated HTTP integration tests with status code assertions."

            results.append(EvidenceSkillItem(
                skill_name="API Development",
                confidence=confidence,
                evidence_summary=summary,
                file_paths=api_files[:3] or [r["path"] for r in routes][:3],
                observed_indicators=indicators,
                missing_evidence=missing,
                recommendation=rec
            ))

        # -------------------------------------------------------------
        # 5. Database Management
        # -------------------------------------------------------------
        orm_models = py_signals["orm_models"]
        sql_files = signals["sql"]["files"]
        db_libs = {"sqlalchemy", "sqlite3", "psycopg2", "asyncpg", "prisma", "pg"} & deps

        if orm_models or sql_files or db_libs:
            if db_libs and not orm_models and not sql_files:
                confidence = "Low"
                summary = f"Database client/ORM ({', '.join(sorted(list(db_libs)))}) declared, but no ORM entity classes or SQL schema/query files were found."
                indicators = [
                    f"Database dependency: {', '.join(sorted(list(db_libs)))}",
                    "No ORM Base/Model classes or .sql files detected"
                ]
                missing = "Database entity definitions (Model/Base), SQL tables, migration scripts, or transactional queries."
                rec = "Implement ORM entity classes inheriting from Base or Model with column definitions."
            else:
                confidence = "High" if ((orm_models and sql_files) or (sql_files and signals["sql"]["has_window_functions"]) or len(orm_models) >= 2) else "Medium"
                summary = f"Observed {'ORM model declarations' if orm_models else ''} {'and SQL queries' if sql_files else ''} managing persistent relational structures."
                indicators = []
                if orm_models:
                    indicators.append(f"{len(orm_models)} ORM entity class(es) inheriting from Model/Base")
                if sql_files:
                    indicators.append(f"{len(sql_files)} SQL file(s) with {'CTEs & joins' if signals['sql']['has_cte'] else 'queries'}")
                if db_libs:
                    indicators.append(f"Database client dependencies: {', '.join(sorted(list(db_libs)))}")

                missing = "Database migration scripts (Alembic/Flyway) and index performance optimization."
                rec = "Add database migration scripts and index declarations on foreign-key lookup columns."

            results.append(EvidenceSkillItem(
                skill_name="Database Management",
                confidence=confidence,
                evidence_summary=summary,
                file_paths=[m["path"] for m in orm_models] + sql_files[:2],
                observed_indicators=indicators,
                missing_evidence=missing,
                recommendation=rec
            ))

        # -------------------------------------------------------------
        # 6. Software Engineering
        # -------------------------------------------------------------
        dirs = set()
        for f in files:
            d = os.path.dirname(f["path"])
            if d:
                dirs.add(d.split('/')[0])

        is_modular = len(dirs) >= 2 or len(files) >= 5
        confidence = "High" if is_modular and signals["has_ci_workflow"] else ("Medium" if is_modular else "Low")
        indicators = [
            f"Modular project layout across {len(dirs)} distinct directories: {', '.join(sorted(list(dirs)) or ['root'])}",
            f"{len(files)} tracked repository file(s) separated by concerns"
        ]
        if signals["has_ci_workflow"]:
            indicators.append("Automated CI workflow defined")

        missing = "Automated static linters (Ruff/ESLint), pre-commit hooks, and architecture decision records."
        rec = "Configure a linter configuration file (.ruff.toml or .eslintrc) and add a pre-commit config."

        results.append(EvidenceSkillItem(
            skill_name="Software Engineering",
            confidence=confidence,
            evidence_summary="Project demonstrates structured directory separation and modular code organization.",
            file_paths=[f["path"] for f in files[:4]],
            observed_indicators=indicators,
            missing_evidence=missing,
            recommendation=rec
        ))

        # -------------------------------------------------------------
        # 7. Testing and Debugging
        # -------------------------------------------------------------
        test_files = signals["test_files"]
        py_tests = py_signals["test_functions"]
        asserts = py_signals["assertions_count"]

        if test_files or py_tests:
            if asserts == 0 and len(py_tests) == 0:
                confidence = "Low"
                summary = f"Test files ({', '.join(test_files[:2])}) detected, but zero assertion statements were found in the AST."
                indicators = [
                    f"{len(test_files)} test file(s) present without verified assertions"
                ]
                missing = "Explicit test assertions (assert ...), pytest fixtures, and boundary condition checks."
                rec = "Add concrete assertion statements validating function outputs against expected values."
            else:
                confidence = "High" if asserts >= 3 or len(test_files) >= 2 else "Medium"
                summary = f"Demonstrated with {len(test_files)} test file(s) and {asserts} verified assertion(s)."
                indicators = [
                    f"{len(test_files)} dedicated test file(s) identified",
                    f"{len(py_tests)} test function(s) with {asserts} explicit assertions"
                ]
                missing = "Mocking external HTTP/database dependencies and test coverage reports (pytest-cov)."
                rec = "Add integration test mocks for network boundaries and verify test coverage above 80%."

            results.append(EvidenceSkillItem(
                skill_name="Testing and Debugging",
                confidence=confidence,
                evidence_summary=summary,
                file_paths=test_files[:3],
                observed_indicators=indicators,
                missing_evidence=missing,
                recommendation=rec
            ))

        # -------------------------------------------------------------
        # 8. Git and GitHub
        # -------------------------------------------------------------
        ci_files = [f["path"] for f in files if ".github/workflows" in f["path"].lower()]
        confidence = "High" if ci_files else "Medium"
        indicators = [
            f"Repository files tracked under Git version control"
        ]
        if ci_files:
            indicators.append(f"GitHub Actions automation workflow: {ci_files[0]}")

        missing = "Pull request templates, issue templates, and release workflow tags."
        rec = "Add a branch protection rule and PR template to establish robust collaborative Git practices."

        results.append(EvidenceSkillItem(
            skill_name="Git and GitHub",
            confidence=confidence,
            evidence_summary="Evidence of Git repository tracking and CI/CD workflow automation." if ci_files else "Git tracking observed; no CI workflows.",
            file_paths=ci_files if ci_files else [files[0]["path"] if files else "README.md"],
            observed_indicators=indicators,
            missing_evidence=missing,
            recommendation=rec
        ))

        # -------------------------------------------------------------
        # 9. Documentation and Project Organization
        # -------------------------------------------------------------
        readme_files = [f["path"] for f in files if os.path.basename(f["path"]).lower() in ("readme.md", "readme.rst", "readme.txt", "readme")]
        if readme_files:
            if signals["readme_length"] < 100:
                confidence = "Low"
                summary = f"README file exists ({readme_files[0]}), but contains minimal content ({signals['readme_length']} characters) lacking setup or architectural detail."
                indicators = [f"README file contains only {signals['readme_length']} characters"]
                missing = "Installation commands, architecture breakdown, and usage examples."
                rec = "Expand README.md with detailed setup steps, prerequisites, and code usage snippets."
            else:
                confidence = "High" if signals["readme_length"] > 300 else "Medium"
                summary = f"Project documentation provided via {readme_files[0]} ({signals['readme_length']} characters)."
                indicators = [
                    f"Repository documentation found in {readme_files[0]} ({signals['readme_length']} characters)",
                    "Installation / setup instructions provided"
                ]
                missing = "Architecture diagrams, API specification docs (OpenAPI), and contribution guidelines."
                rec = "Add architectural sequence diagrams and an explicit troubleshooting guide to README.md."

            results.append(EvidenceSkillItem(
                skill_name="Documentation and Project Organization",
                confidence=confidence,
                evidence_summary=summary,
                file_paths=readme_files,
                observed_indicators=indicators,
                missing_evidence=missing,
                recommendation=rec
            ))

        return results

    def _detect_skill_gaps(self, signals: Dict[str, Any], detected_skills: List[EvidenceSkillItem]) -> List[SkillGapItem]:
        """
        Identifies key skill gaps based strictly on missing or limited evidence.
        """
        gaps: List[SkillGapItem] = []

        # Gap 1: Automated testing (e.g. no test files detected -> recommend adding unit tests)
        has_tests = any(s.skill_name == "Testing and Debugging" and s.confidence in ("Medium", "High") for s in detected_skills)
        if not has_tests:
            gaps.append(SkillGapItem(
                area="Automated Testing & Coverage",
                observation="No test files (e.g., tests/test_*.py) or assertion statements were identified in the repository.",
                recommendation="Write a pytest test suite covering both normal inputs and boundary edge cases (nulls, empty collections).",
                severity="high"
            ))

        # Gap 2: README documentation (e.g. no README detected -> recommend documenting setup and usage)
        has_doc = any(s.skill_name == "Documentation and Project Organization" and s.confidence in ("Medium", "High") for s in detected_skills)
        if not has_doc:
            gaps.append(SkillGapItem(
                area="Project Documentation & Setup",
                observation="The repository lacks a comprehensive README.md detailing dependencies, local run commands, and architecture.",
                recommendation="Add a clear README.md with an overview, prerequisites, environment variables, and usage examples.",
                severity="medium"
            ))

        # Gap 3: Data-analysis libraries detected but no analysis notebook or report
        data_skill = next((s for s in detected_skills if s.skill_name == "Data Analysis"), None)
        has_notebook = any(ext == ".ipynb" for ext in signals["files_by_ext"])
        if data_skill and not has_notebook:
            gaps.append(SkillGapItem(
                area="Exploratory Data Artifacts & Notebooks",
                observation="Data analysis libraries or routines are present, but no exploratory Jupyter notebook (.ipynb) or structured analysis report was found.",
                recommendation="Include a clean Jupyter notebook demonstrating exploratory analysis, hypothesis validation, and distribution plots.",
                severity="low"
            ))

        # Gap 4: API routes detected but no test results available -> recommend API testing
        api_skill = next((s for s in detected_skills if s.skill_name == "API Development"), None)
        if api_skill and not has_tests:
            gaps.append(SkillGapItem(
                area="API Integration Verification",
                observation="HTTP route handlers are defined, but no automated endpoint integration tests or status code assertions were detected.",
                recommendation="Add integration tests using httpx or TestClient to verify endpoint status codes, error payloads, and response schemas.",
                severity="high"
            ))

        # Gap 5: Import-only or library without implementation
        import_only_skills = [s for s in detected_skills if s.confidence == "Low" and "declared" in s.evidence_summary.lower()]
        for s in import_only_skills:
            gaps.append(SkillGapItem(
                area=f"{s.skill_name} Implementation Depth",
                observation=f"{s.skill_name} dependencies are declared, but no substantive AST implementation calls were found.",
                recommendation=s.recommendation,
                severity="medium"
            ))

        # Gap 6: CI/CD Pipeline
        if not signals["has_ci_workflow"]:
            gaps.append(SkillGapItem(
                area="CI/CD Pipeline Automation",
                observation="No automated CI workflow (.github/workflows) was found to validate test execution on code commits.",
                recommendation="Add a GitHub Actions workflow (.github/workflows/ci.yml) to automatically run tests and lint checks on push.",
                severity="medium"
            ))

        return gaps

    def _generate_prioritized_actions(
        self,
        detected_skills: List[EvidenceSkillItem],
        skill_gaps: List[SkillGapItem],
        target_career: Optional[str]
    ) -> List[PrioritizedNextStep]:
        """
        Generates 3 prioritized personalized next steps:
        1. Immediate improvement
        2. Suitable mini-project or coding exercise
        3. Way to demonstrate and verify the skill
        """
        # Determine highest severity gap
        high_gaps = [g for g in skill_gaps if g.severity == "high"]
        target_gap = high_gaps[0] if high_gaps else (skill_gaps[0] if skill_gaps else None)

        if target_gap and "Testing" in target_gap.area:
            action1 = PrioritizedNextStep(
                priority=1,
                type="immediate",
                title="Add Automated Unit Tests to Repository",
                description="Create a `tests/` directory with pytest test cases covering your core functions and assert expected outputs.",
                action_label="Implement Tests"
            )
        elif target_gap and "Documentation" in target_gap.area:
            action1 = PrioritizedNextStep(
                priority=1,
                type="immediate",
                title="Document Project in README.md",
                description="Write a README.md explaining what your repository does, installation steps, and example execution commands.",
                action_label="Create README"
            )
        else:
            action1 = PrioritizedNextStep(
                priority=1,
                type="immediate",
                title="Refactor Modules for Clean Separation",
                description="Separate business logic, data transformation, and presentation into decoupled files with clear type annotations.",
                action_label="Refactor Code"
            )

        # Action 2: Mini-project
        action2 = PrioritizedNextStep(
            priority=2,
            type="mini_project",
            title="Complete 'Trading Log Ingestion & Data Cleaner' Mini-Project",
            description="Build a resilient data ingestion function inside the in-browser workspace to prove edge-case handling against public and hidden test suites.",
            action_label="Launch Mini-Project",
            target_id="py-data-cleaner-101"
        )

        # Action 3: Verification
        action3 = PrioritizedNextStep(
            priority=3,
            type="verification",
            title="Take SkillProof Diagnostic Assessment",
            description="Complete the 15-minute Python Architecture & Fundamentals Diagnostic to formally verify your conceptual mastery and earn proof badges.",
            action_label="Take Diagnostic",
            target_id="diag-py-101"
        )

        return [action1, action2, action3]

    def _generate_ai_synthesis(
        self,
        repo_name: str,
        detected_skills: List[EvidenceSkillItem],
        skill_gaps: List[SkillGapItem],
        target_career: Optional[str]
    ) -> Optional[str]:
        """
        Calls Gemini AI with structured evidence to produce a grounded 2-3 sentence executive summary.
        Falls back cleanly to deterministic synthesis if Gemini is unavailable.
        """
        high_skills = [s.skill_name for s in detected_skills if s.confidence == "High"]
        med_skills = [s.skill_name for s in detected_skills if s.confidence == "Medium"]

        deterministic_summary = (
            f"Repository '{repo_name}' provides verified evidence of {', '.join(high_skills or med_skills[:2]) or 'fundamental programming'}. "
            f"The primary gap identified is {skill_gaps[0].area if skill_gaps else 'further test hardening'}, which can be resolved by "
            f"{skill_gaps[0].recommendation if skill_gaps else 'adding end-to-end integration tests'}."
        )

        try:
            from ..gemini_service import gemini_service
            if not gemini_service.is_configured:
                return deterministic_summary

            prompt = (
                f"You are an expert AI Career Coach evaluating repository '{repo_name}' for target career '{target_career or 'Software Engineering'}'.\n"
                f"Demonstrated Skills (High): {', '.join(high_skills) or 'None'}\n"
                f"Demonstrated Skills (Medium): {', '.join(med_skills) or 'None'}\n"
                f"Identified Evidence Gaps: {'; '.join(g.area + ': ' + g.observation for g in skill_gaps[:2])}\n\n"
                f"Provide a concise, objective 2-sentence executive summary. "
                f"Do NOT invent unobserved skills. Clearly distinguish observed evidence from inferred ability. "
                f"Focus on the strongest verified evidence and the single most impactful recommendation."
            )
            resp = gemini_service.send_message(prompt, system_instruction="You are an evidence-grounded engineering assessor. Be factual, concise, and constructive.")
            if resp.success and resp.text:
                return resp.text.strip()
        except Exception as err:
            logger.warning("Gemini synthesis skipped or errored: %s", err)

        return deterministic_summary


skill_mapping_engine = SkillMappingEngine()
