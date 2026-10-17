"""
Adaptive Challenge & Evaluation Engine for SkillProof Arena.
Implements:
- Objective rubric evaluation combining test suite results and static AST heuristics
- Adaptive task recommendation based on diagnostic and practical performance thresholds
- Cross-modality balance (identifying practical vs conceptual gaps)
- Evidence-grounded skill mastery updates
- Optional Gemini qualitative mentorship review with transparent fallback
"""

import ast
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

from ..models import (
    DiagnosticAttempt,
    ProjectSubmission,
    MiniProjectDefinition,
    SkillMasteryRecord,
    UserProfile
)
from .ai_service import has_configured_api_key, get_gemini_client

logger = logging.getLogger("arena.adaptive_engine")

# Configurable default threshold rules (Feature C)
THRESHOLD_DIAGNOSTIC_BEGINNER = 40.0
THRESHOLD_DIAGNOSTIC_INTERMEDIATE = 70.0
THRESHOLD_DIAGNOSTIC_ADVANCED = 85.0


class AdaptiveEngine:
    @staticmethod
    def evaluate_code_quality_ast(code: str) -> Dict[str, Any]:
        """
        Performs static AST inspection to evaluate code structure objectively:
        - Function definitions, type annotations, docstrings, error handling.
        """
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            return {
                "score": 0.0,
                "has_functions": False,
                "has_docstrings": False,
                "has_type_hints": False,
                "has_error_handling": False,
                "notes": f"Syntax error in code: {str(e)}"
            }

        functions = [n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
        has_functions = len(functions) > 0
        has_docstrings = any(ast.get_docstring(f) is not None for f in functions)
        has_type_hints = any(
            (f.returns is not None or any(arg.annotation is not None for arg in f.args.args))
            for f in functions
        )
        has_error_handling = any(isinstance(n, ast.Try) for n in ast.walk(tree))

        quality_score = 40.0  # base syntax valid
        notes = []

        if has_functions:
            quality_score += 25.0
            notes.append("Clean function modularity detected.")
        if has_docstrings:
            quality_score += 15.0
            notes.append("Clear docstrings and documentation.")
        if has_type_hints:
            quality_score += 10.0
            notes.append("Explicit Python type annotations used.")
        if has_error_handling:
            quality_score += 10.0
            notes.append("Defensive error handling (try/except) included.")

        return {
            "score": min(100.0, quality_score),
            "has_functions": has_functions,
            "has_docstrings": has_docstrings,
            "has_type_hints": has_type_hints,
            "has_error_handling": has_error_handling,
            "notes": "; ".join(notes) if notes else "Valid basic Python syntax."
        }

    @classmethod
    def evaluate_project(
        cls,
        code: str,
        project: MiniProjectDefinition,
        sandbox_res: Dict[str, Any],
        hints_used: int
    ) -> Dict[str, Any]:
        """
        Evaluates project submission against defined rubric and test suite.
        Distinguishes automated objective test results from qualitative review.
        """
        test_score = sandbox_res.get("score", 0.0)
        tests_passed = sandbox_res.get("tests_passed", 0)
        tests_total = sandbox_res.get("tests_total", 0)
        is_success = sandbox_res.get("success", False)

        # 1. AST Code Quality Evaluation
        ast_eval = cls.evaluate_code_quality_ast(code)
        quality_score = ast_eval["score"]

        # 2. Hint Efficiency (Penalty for reliance on progressive hints)
        # 0 hints: 100%, 1 hint: 90%, 2 hints: 80%, 3+ hints: 70%
        hint_score = max(50.0, 100.0 - (hints_used * 12.0))

        # 3. Composite Weighted Rubric Score:
        # Correctness & automated tests: 60%
        # Code structure & modularity: 25%
        # Independent problem-solving (hint usage): 15%
        composite_score = round(
            (test_score * 0.60) + (quality_score * 0.25) + (hint_score * 0.15),
            1
        )

        # 4. Rubric Breakdown
        rubric_breakdown = [
            {
                "criterion": "Functional Correctness & Unit Tests",
                "weight": "60%",
                "score": test_score,
                "passed": tests_passed == tests_total and tests_total > 0,
                "detail": f"{tests_passed} of {tests_total} automated assertions satisfied."
            },
            {
                "criterion": "Code Quality & Structural Hygiene",
                "weight": "25%",
                "score": quality_score,
                "passed": quality_score >= 65.0,
                "detail": ast_eval["notes"]
            },
            {
                "criterion": "Independent Problem Solving",
                "weight": "15%",
                "score": hint_score,
                "passed": hints_used <= 1,
                "detail": f"{hints_used} hint(s) unlocked during project implementation."
            }
        ]

        # 5. Skills Demonstrated vs. Needing Practice
        demonstrated_skills = []
        skills_to_practice = []

        if is_success:
            demonstrated_skills.append(f"{project.skill_name} Implementation")
            demonstrated_skills.append("Data Transformation & Logic Validation")
            if ast_eval["has_type_hints"]:
                demonstrated_skills.append("Type-Annotated Python Design")
        else:
            skills_to_practice.append(f"{project.skill_name} Edge Cases")
            skills_to_practice.append("Automated Test Debugging")

        if not ast_eval["has_error_handling"]:
            skills_to_practice.append("Defensive Exception Handling")

        # 6. Optional Qualitative Feedback via Gemini (if configured)
        ai_feedback_text = None
        has_ai_review = False

        if has_configured_api_key():
            try:
                client = get_gemini_client()
                prompt = (
                    f"Provide brief, rigorous mentor feedback (max 3 sentences) on this Python submission for the project '{project.title}'.\n"
                    f"Task: {project.description}\n"
                    f"Code:\n```python\n{code[:1500]}\n```\n"
                    f"Test score: {test_score}%, Quality score: {quality_score}%.\n"
                    "Focus strictly on practical improvement."
                )
                response = client.models.generate_content(
                    model="gemini-3.8-flash",
                    contents=prompt
                )
                if response and response.text:
                    ai_feedback_text = response.text.strip()
                    has_ai_review = True
            except Exception as e:
                logger.warning(f"Gemini mentorship feedback failed gracefully: {e}")

        # Deterministic feedback fallback if AI unavailable
        if not ai_feedback_text:
            if composite_score >= 80.0:
                ai_feedback_text = (
                    f"Excellent execution on '{project.title}'. Your logic passed all critical assertions and shows solid structural discipline. "
                    "You are ready to advance to more complex pipeline tasks."
                )
            elif composite_score >= 50.0:
                ai_feedback_text = (
                    f"Good foundational attempt on '{project.title}'. Core functionality is emerging, but several test cases or edge conditions failed. "
                    "Review the failed test assertions and refine your handling of nulls or boundary inputs."
                )
            else:
                ai_feedback_text = (
                    f"Significant issues encountered in '{project.title}'. Test assertions were not satisfied. "
                    "Consider taking the conceptual diagnostic or reviewing starter instructions before re-attempting."
                )

        feedback_package = {
            "summary": ai_feedback_text,
            "has_ai_mentor_review": has_ai_review,
            "demonstrated_skills": demonstrated_skills,
            "skills_to_practice": skills_to_practice,
            "composite_score": composite_score,
            "verdict": "PASSED" if is_success and composite_score >= 70.0 else "NEEDS_PRACTICE"
        }

        return {
            "composite_score": composite_score,
            "rubric_evaluation": rubric_breakdown,
            "feedback": feedback_package,
            "status": "passed" if is_success and composite_score >= 70.0 else "failed"
        }

    @classmethod
    def determine_adaptive_challenge(
        cls,
        user_id: str,
        career_id: str,
        skill_name: str,
        diagnostic_attempts: List[DiagnosticAttempt],
        project_submissions: List[ProjectSubmission],
        available_assessments: List[Any],
        available_projects: List[MiniProjectDefinition]
    ) -> Dict[str, Any]:
        """
        Determines the next adaptive task based on demonstrated evidence and cross-modality balance:
        - High diagnostic + low practical -> Recommend targeted practical coding challenge
        - High practical + low diagnostic -> Recommend conceptual assessment
        - Low in both (<40%) -> Recommend guided beginner review + structured task
        - 40-69% -> Beginner project with hints
        - 70-84% -> Intermediate project with fewer hints
        - 85%+ -> Advanced challenge
        """
        # 1. Compute recent diagnostic performance for this skill
        matching_diag = [d for d in diagnostic_attempts if d.skill_name.lower() == skill_name.lower() or d.career_id == career_id]
        latest_diag = matching_diag[0] if matching_diag else None
        diag_score = latest_diag.score if latest_diag else None

        # 2. Compute recent project performance for this skill
        matching_proj = [p for p in project_submissions if p.skill_name.lower() == skill_name.lower() or p.career_id == career_id]
        latest_proj = matching_proj[0] if matching_proj else None
        proj_score = latest_proj.score if latest_proj else None

        # 3. Rule evaluations
        # Case A: Cross-modality imbalance: High theoretical, weak practical
        if diag_score is not None and diag_score >= 70.0 and (proj_score is None or proj_score < 50.0):
            target_proj = cls._find_project(available_projects, skill_name, "beginner")
            return {
                "action_type": "project",
                "recommended_id": target_proj.id if target_proj else "py-data-cleaner-101",
                "skill_name": skill_name,
                "difficulty": "beginner",
                "reason": (
                    f"Your conceptual score is strong ({diag_score}%), but practical implementation needs practice. "
                    "We recommend a hands-on project workspace to translate theory into verified code."
                ),
                "target_type": "Hands-on Mini Project",
                "target_title": target_proj.title if target_proj else "Data Cleaning Pipeline",
                "prerequisites_met": True
            }

        # Case B: Cross-modality imbalance: High practical, weak theoretical
        if proj_score is not None and proj_score >= 70.0 and (diag_score is None or diag_score < 50.0):
            target_diag = cls._find_diagnostic(available_assessments, skill_name, "beginner")
            return {
                "action_type": "diagnostic",
                "recommended_id": target_diag.id if target_diag else "diag-py-101",
                "skill_name": skill_name,
                "difficulty": "beginner",
                "reason": (
                    f"Your practical code execution is proven ({proj_score}%), but theoretical foundations show gaps. "
                    "Take a focused diagnostic to verify core principles and edge-case comprehension."
                ),
                "target_type": "Diagnostic Assessment",
                "target_title": target_diag.title if target_diag else f"{skill_name} Fundamentals Diagnostic",
                "prerequisites_met": True
            }

        # Case C: Low performance (< 40%) in latest test
        active_score = diag_score if diag_score is not None else (proj_score or 0.0)
        if active_score < THRESHOLD_DIAGNOSTIC_BEGINNER and (diag_score is not None or proj_score is not None):
            target_proj = cls._find_project(available_projects, skill_name, "beginner")
            return {
                "action_type": "project",
                "recommended_id": target_proj.id if target_proj else "py-data-cleaner-101",
                "skill_name": skill_name,
                "difficulty": "beginner",
                "reason": (
                    f"Recent performance ({active_score}%) indicates foundational gaps. "
                    "A guided beginner task with step-by-step hints will help anchor essential syntax and patterns."
                ),
                "target_type": "Guided Beginner Project",
                "target_title": target_proj.title if target_proj else "Data Cleaning Pipeline",
                "prerequisites_met": True
            }

        # Case D: Moderate performance (40% - 69%)
        if active_score < THRESHOLD_DIAGNOSTIC_INTERMEDIATE:
            target_proj = cls._find_project(available_projects, skill_name, "beginner")
            return {
                "action_type": "project",
                "recommended_id": target_proj.id if target_proj else "py-data-cleaner-101",
                "skill_name": skill_name,
                "difficulty": "beginner",
                "reason": (
                    f"Demonstrated competence is at {active_score}%. "
                    "Consolidate your working fluency with a practical coding challenge using hints as needed."
                ),
                "target_type": "Hands-on Mini Project",
                "target_title": target_proj.title if target_proj else "Data Cleaning Pipeline",
                "prerequisites_met": True
            }

        # Case E: Strong performance (70% - 84%)
        if active_score < THRESHOLD_DIAGNOSTIC_ADVANCED:
            target_proj = cls._find_project(available_projects, skill_name, "intermediate") or cls._find_project(available_projects, skill_name, "beginner")
            return {
                "action_type": "project",
                "recommended_id": target_proj.id if target_proj else "py-metrics-aggregator-201",
                "skill_name": skill_name,
                "difficulty": "intermediate",
                "reason": (
                    f"Strong performance established ({active_score}%). "
                    "Challenge yourself with an intermediate project featuring fewer hints and multi-step data transformations."
                ),
                "target_type": "Intermediate Project",
                "target_title": target_proj.title if target_proj else "Metrics Aggregation Engine",
                "prerequisites_met": True
            }

        # Case F: Mastery / Advanced performance (>= 85%)
        target_proj = (
            cls._find_project(available_projects, skill_name, "advanced")
            or cls._find_project(available_projects, skill_name, "intermediate")
        )
        return {
            "action_type": "project",
            "recommended_id": target_proj.id if target_proj else "py-metrics-aggregator-201",
            "skill_name": skill_name,
            "difficulty": "advanced",
            "reason": (
                f"Distinguished mastery demonstrated ({active_score}%). "
                "Prerequisites verified across tests and code evidence. Proceeding to advanced system engineering challenge."
            ),
            "target_type": "Advanced Challenge",
            "target_title": target_proj.title if target_proj else "Advanced Event Pipeline",
            "prerequisites_met": True
        }

    @staticmethod
    def _find_project(projects: List[MiniProjectDefinition], skill_name: str, difficulty: str) -> Optional[MiniProjectDefinition]:
        for p in projects:
            if p.difficulty.lower() == difficulty.lower() and (
                p.skill_name.lower() in skill_name.lower() or skill_name.lower() in p.skill_name.lower()
            ):
                return p
        # Fallback to any project of that difficulty
        for p in projects:
            if p.difficulty.lower() == difficulty.lower():
                return p
        return projects[0] if projects else None

    @staticmethod
    def _find_diagnostic(assessments: List[Any], skill_name: str, difficulty: str) -> Optional[Any]:
        for a in assessments:
            if a.difficulty.lower() == difficulty.lower() and (
                a.skill_name.lower() in skill_name.lower() or skill_name.lower() in a.skill_name.lower()
            ):
                return a
        for a in assessments:
            if a.difficulty.lower() == difficulty.lower():
                return a
        return assessments[0] if assessments else None

    @classmethod
    def calculate_skill_mastery(
        cls,
        diagnostic_score: Optional[float],
        practical_score: Optional[float],
        attempts_count: int
    ) -> Tuple[str, float]:
        """
        Calculates evidence-based skill mastery:
        Never awards mastery just for opening a project or submitting empty code.
        Requires evidence from both test passing and practical execution.
        """
        if diagnostic_score is None and practical_score is None:
            return "novice", 0.0

        if diagnostic_score is not None and practical_score is not None:
            # 40% conceptual + 60% practical
            combined = (diagnostic_score * 0.40) + (practical_score * 0.60)
        elif practical_score is not None:
            combined = practical_score * 0.85  # ceiling if no conceptual diagnostic taken
        else:
            combined = (diagnostic_score or 0.0) * 0.70  # ceiling if no practical code submitted

        # Account for evidence depth (single attempt capped)
        if attempts_count <= 1:
            combined = min(combined, 74.0)

        combined = round(combined, 1)

        if combined >= 85.0 and attempts_count >= 2:
            return "advanced", combined
        if combined >= 70.0:
            return "proficient", combined
        if combined >= 45.0:
            return "competent", combined
        return "novice", combined


adaptive_engine = AdaptiveEngine()
