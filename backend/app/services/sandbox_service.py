"""
Isolated Sandbox Execution Engine for SkillProof Arena.
Executes Python user submissions in an isolated subprocess with resource limits.
Never runs code inside the FastAPI process.
Keeps hidden tests and trusted evaluation logic strictly on the server side.
"""

import sys
import os
import json
import subprocess
import tempfile
import time
import re
from typing import Dict, Any, List, Optional

EXECUTION_TIMEOUT_SECS = 4.0
MAX_OUTPUT_CHARS = 50_000

# Strict list of disallowed dangerous token imports in novice/intermediate arena projects
DISALLOWED_PATTERNS = [
    r"\bimport\s+os\b",
    r"\bfrom\s+os\s+import\b",
    r"\bimport\s+subprocess\b",
    r"\bfrom\s+subprocess\s+import\b",
    r"\bimport\s+shutil\b",
    r"\bfrom\s+shutil\s+import\b",
    r"\bimport\s+socket\b",
    r"\bfrom\s+socket\s+import\b",
    r"\bimport\s+urllib\b",
    r"\bfrom\s+urllib\s+import\b",
    r"\bimport\s+requests\b",
    r"\bfrom\s+requests\s+import\b",
    r"\bimport\s+ctypes\b",
    r"\b__import__\b",
    r"\beval\s*\(",
    r"\bexec\s*\(",
    r"\bopen\s*\([^)]*['\"][wa\+]",  # writing files
]


class SandboxExecutionService:
    @staticmethod
    def inspect_static_safety(code: str) -> Optional[str]:
        """Pre-execution static check to reject obviously unsafe or malicious constructs."""
        for pattern in DISALLOWED_PATTERNS:
            if re.search(pattern, code):
                return f"Disallowed security pattern detected: '{pattern}'. System network/filesystem/subprocess calls are forbidden in Arena tasks."
        return None

    @classmethod
    def run_tests(
        cls,
        code: str,
        test_cases: List[Dict[str, Any]],
        sample_data: Optional[str] = None,
        is_dry_run: bool = False
    ) -> Dict[str, Any]:
        """
        Executes code against test cases in an isolated subprocess.
        Returns detailed results including per-test verdicts and stdout.
        """
        # 1. Static security validation
        security_error = cls.inspect_static_safety(code)
        if security_error:
            return {
                "success": False,
                "status": "security_violation",
                "score": 0.0,
                "tests_passed": 0,
                "tests_total": len(test_cases),
                "test_results": [],
                "output": "",
                "error": security_error,
                "execution_time_ms": 0.0
            }

        start_time = time.perf_counter()

        with tempfile.TemporaryDirectory(prefix="arena_sandbox_") as tmp_dir:
            solution_file = os.path.join(tmp_dir, "solution.py")
            with open(solution_file, "w", encoding="utf-8") as f:
                f.write(code)

            if sample_data:
                sample_file = os.path.join(tmp_dir, "sample_data.csv")
                with open(sample_file, "w", encoding="utf-8") as f:
                    f.write(sample_data)

            # Build harness script
            harness_file = os.path.join(tmp_dir, "harness.py")
            harness_content = cls._build_harness_code(test_cases)
            with open(harness_file, "w", encoding="utf-8") as f:
                f.write(harness_content)

            # Run isolated subprocess:
            # -I: Run in isolated mode (ignore environment variables, no user site packages)
            # -B: Don't write .pyc bytecode
            # -s: Don't add user site directory to sys.path
            cmd = [
                sys.executable,
                "-I",
                "-B",
                "-s",
                "harness.py"
            ]

            try:
                proc = subprocess.run(
                    cmd,
                    cwd=tmp_dir,
                    capture_output=True,
                    text=True,
                    timeout=EXECUTION_TIMEOUT_SECS,
                    env={
                        "PYTHONPATH": tmp_dir,
                        "PYTHONIOENCODING": "utf-8",
                        "PYTHONDONTWRITEBYTECODE": "1"
                    }
                )
                duration_ms = round((time.perf_counter() - start_time) * 1000, 2)

                stdout = proc.stdout or ""
                stderr = proc.stderr or ""

                # Sanitize temporary directory paths in error outputs
                stdout = stdout.replace(tmp_dir, ".")
                stderr = stderr.replace(tmp_dir, ".")

                # Truncate if massive
                if len(stdout) > MAX_OUTPUT_CHARS:
                    stdout = stdout[:MAX_OUTPUT_CHARS] + "\n...[Output truncated due to length]"
                if len(stderr) > MAX_OUTPUT_CHARS:
                    stderr = stderr[:MAX_OUTPUT_CHARS] + "\n...[Error output truncated]"

                # Parse JSON test results from harness output
                results_match = re.search(r"__ARENA_RESULTS_START__(.*?)__ARENA_RESULTS_END__", stdout, re.DOTALL)
                clean_stdout = re.sub(r"__ARENA_RESULTS_START__.*?__ARENA_RESULTS_END__", "", stdout, flags=re.DOTALL).strip()

                if results_match:
                    try:
                        raw_data = json.loads(results_match.group(1).strip())
                        test_verdicts = raw_data.get("results", [])
                        passed_count = sum(1 for t in test_verdicts if t.get("passed"))
                        total_count = len(test_verdicts)
                        score = round((passed_count / total_count * 100), 1) if total_count > 0 else 0.0

                        return {
                            "success": passed_count == total_count and total_count > 0,
                            "status": "passed" if passed_count == total_count else "failed",
                            "score": score,
                            "tests_passed": passed_count,
                            "tests_total": total_count,
                            "test_results": test_verdicts,
                            "output": clean_stdout,
                            "error": stderr.strip() if proc.returncode != 0 and not test_verdicts else "",
                            "execution_time_ms": duration_ms
                        }
                    except json.JSONDecodeError:
                        pass

                # If harness crashed before emitting JSON
                return {
                    "success": False,
                    "status": "error",
                    "score": 0.0,
                    "tests_passed": 0,
                    "tests_total": len(test_cases),
                    "test_results": [
                        {
                            "name": t.get("name", "Test"),
                            "passed": False,
                            "error": "Syntax or Runtime Error preventing test execution"
                        }
                        for t in test_cases
                    ],
                    "output": clean_stdout,
                    "error": stderr.strip() or "Process terminated without completing test suite.",
                    "execution_time_ms": duration_ms
                }

            except subprocess.TimeoutExpired:
                duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
                return {
                    "success": False,
                    "status": "timeout",
                    "score": 0.0,
                    "tests_passed": 0,
                    "tests_total": len(test_cases),
                    "test_results": [],
                    "output": "",
                    "error": f"Execution timed out after {EXECUTION_TIMEOUT_SECS} seconds. Check for infinite loops or heavy operations.",
                    "execution_time_ms": duration_ms
                }
            except Exception as ex:
                return {
                    "success": False,
                    "status": "error",
                    "score": 0.0,
                    "tests_passed": 0,
                    "tests_total": len(test_cases),
                    "test_results": [],
                    "output": "",
                    "error": f"Sandbox runner error: {str(ex)}",
                    "execution_time_ms": 0.0
                }

    @classmethod
    def _build_harness_code(cls, test_cases: List[Dict[str, Any]]) -> str:
        """
        Builds a Python test harness that executes user solution functions and returns structured JSON verdicts.
        """
        escaped_tests = json.dumps(test_cases)
        return f'''
import sys
import json
import time
import traceback

def run_all():
    import sys
    import os
    # Ensure local directory is at top of path so solution can be imported in isolated mode
    local_dir = os.path.dirname(os.path.abspath(__file__))
    if local_dir not in sys.path:
        sys.path.insert(0, local_dir)

    results = []
    test_specs = {escaped_tests}

    try:
        import solution
    except Exception as e:
        tb = traceback.format_exc()
        # Clean traceback
        err_msg = f"{{type(e).__name__}}: {{str(e)}}"
        for spec in test_specs:
            results.append({{
                "name": spec.get("name", "Test"),
                "passed": False,
                "error": f"Import Error: {{err_msg}}",
                "execution_time_ms": 0.0
            }})
        print("__ARENA_RESULTS_START__" + json.dumps({{"results": results}}) + "__ARENA_RESULTS_END__")
        return

    for spec in test_specs:
        t_name = spec.get("name", "Test")
        entry_func = spec.get("function_name", "solve")
        args = spec.get("args", [])
        kwargs = spec.get("kwargs", {{}})
        expected = spec.get("expected")
        custom_assert = spec.get("assert_code")

        t_start = time.perf_counter()
        try:
            if not hasattr(solution, entry_func):
                results.append({{
                    "name": t_name,
                    "passed": False,
                    "error": f"Expected function '{{entry_func}}' not found in solution.py",
                    "execution_time_ms": 0.0
                }})
                continue

            fn = getattr(solution, entry_func)
            actual = fn(*args, **kwargs)
            duration = round((time.perf_counter() - t_start) * 1000, 2)

            passed = False
            error_detail = None

            if custom_assert:
                # Custom trusted verification hook
                locs = {{"actual": actual, "expected": expected, "passed": True, "error": None}}
                exec(custom_assert, {{"__builtins__": __builtins__}}, locs)
                passed = locs.get("passed", False)
                error_detail = locs.get("error")
            elif expected is not None:
                passed = (actual == expected)
                if not passed:
                    error_detail = f"Expected {{repr(expected)}}, but got {{repr(actual)}}"
            else:
                passed = True

            results.append({{
                "name": t_name,
                "passed": bool(passed),
                "actual": str(actual)[:200] if actual is not None else None,
                "expected": str(expected)[:200] if expected is not None else None,
                "error": error_detail,
                "execution_time_ms": duration
            }})

        except Exception as e:
            duration = round((time.perf_counter() - t_start) * 1000, 2)
            results.append({{
                "name": t_name,
                "passed": False,
                "error": f"{{type(e).__name__}}: {{str(e)}}",
                "execution_time_ms": duration
            }})

    print("__ARENA_RESULTS_START__" + json.dumps({{"results": results}}) + "__ARENA_RESULTS_END__")

if __name__ == "__main__":
    run_all()
'''

sandbox_service = SandboxExecutionService()
