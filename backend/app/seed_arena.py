"""
Seed inventory for SkillProof Arena:
- Diagnostic assessments with verified questions and rubrics
- Practical in-browser Python mini-projects with starter code, sample data, progressive hints, and hidden test cases.
"""

from typing import List, Dict, Any
from sqlalchemy.orm import Session
from .models import DiagnosticAssessment, MiniProjectDefinition

SEED_DIAGNOSTICS: List[Dict[str, Any]] = [
    {
        "id": "diag-py-101",
        "career_id": "ai-product-engineer",
        "skill_name": "Python Fundamentals",
        "title": "Python Architecture & Fundamentals Diagnostic",
        "difficulty": "beginner",
        "time_limit_mins": 15,
        "questions": [
            {
                "id": "q1",
                "type": "mcq",
                "text": "In Python 3.10+, what is the time complexity of checking membership `x in collection` if `collection` is a `set` vs a `list`?",
                "options": [
                    "O(1) average for set, O(n) for list",
                    "O(n) for both set and list",
                    "O(log n) for set, O(1) for list",
                    "O(1) for list, O(n) for set"
                ],
                "correct_answer": "O(1) average for set, O(n) for list",
                "explanation": "Hash sets compute a hash for O(1) average lookup, whereas lists perform a linear O(n) traversal across elements.",
                "skill_tag": "Data Structures & Complexity"
            },
            {
                "id": "q2",
                "type": "mcq",
                "text": "What happens if a function specifies a default mutable argument like `def add_item(item, target_list=[])`?",
                "options": [
                    "A new empty list is instantiated on every function call.",
                    "The same list instance is reused across invocations, retaining state across calls.",
                    "Python raises a `TypeError` at compile time.",
                    "The list is automatically cloned inside the function frame."
                ],
                "correct_answer": "The same list instance is reused across invocations, retaining state across calls.",
                "explanation": "Default arguments are evaluated once at function definition time, binding mutable objects across all subsequent calls.",
                "skill_tag": "Function Semantics & Memory"
            },
            {
                "id": "q3",
                "type": "short_answer",
                "text": "Which built-in Python module provides decorators like `@lru_cache` and `@cached_property`?",
                "correct_answer": "functools",
                "explanation": "The `functools` module contains higher-order functions and operations on callable objects, including caching decorators.",
                "skill_tag": "Standard Library & Optimization"
            },
            {
                "id": "q4",
                "type": "mcq",
                "text": "Given `data = [1, 2, 3, 4, 5]`, which expression cleanly produces a list of squares of even numbers?",
                "options": [
                    "[x**2 for x in data if x % 2 == 0]",
                    "[x**2 if x % 2 == 0 for x in data]",
                    "filter(lambda x: x**2, data)",
                    "data.map(x => x**2).filter(x % 2 == 0)"
                ],
                "correct_answer": "[x**2 for x in data if x % 2 == 0]",
                "explanation": "List comprehensions filter elements using trailing `if condition` before mapping the target expression.",
                "skill_tag": "Comprehensions & Functional Style"
            },
            {
                "id": "q5",
                "type": "code_snippet",
                "text": "What does the following snippet print?\n```python\na = [1, 2, 3]\nb = a\nb.append(4)\nprint(len(a))\n```",
                "options": ["3", "4", "Error", "None"],
                "correct_answer": "4",
                "explanation": "Variables `a` and `b` reference the identical underlying list in memory; mutating via `b` reflects immediately on `a`.",
                "skill_tag": "References & Memory Management"
            }
        ]
    },
    {
        "id": "diag-data-101",
        "career_id": "data-systems-analyst",
        "skill_name": "Data Analysis & SQL",
        "title": "Data Engineering & Pipeline Diagnostic",
        "difficulty": "beginner",
        "time_limit_mins": 15,
        "questions": [
            {
                "id": "q1",
                "type": "mcq",
                "text": "In SQL, what is the key behavioral difference between `WHERE` and `HAVING`?",
                "options": [
                    "`WHERE` filters rows before grouping; `HAVING` filters aggregated groups after `GROUP BY`.",
                    "`WHERE` is only for numeric columns, `HAVING` is for string columns.",
                    "`HAVING` executes before `WHERE`.",
                    "There is no difference; they are interchangeable aliases."
                ],
                "correct_answer": "`WHERE` filters rows before grouping; `HAVING` filters aggregated groups after `GROUP BY`.",
                "explanation": "Row-level filtering happens first via `WHERE`. After rows are aggregated via `GROUP BY`, `HAVING` evaluates expressions on aggregate functions.",
                "skill_tag": "SQL Query Execution Order"
            },
            {
                "id": "q2",
                "type": "mcq",
                "text": "What is the primary objective of an idempotency property in an automated ETL pipeline?",
                "options": [
                    "Guaranteeing that executing the pipeline multiple times on the same input produces the exact same outcome without duplicate rows.",
                    "Ensuring data is encrypted at rest using TLS.",
                    "Restricting data types to 64-bit floating point.",
                    "Allowing only one user to view reporting dashboards at a time."
                ],
                "correct_answer": "Guaranteeing that executing the pipeline multiple times on the same input produces the exact same outcome without duplicate rows.",
                "explanation": "Idempotent pipelines allow resilient retries without generating duplicate rows or partial state corruption.",
                "skill_tag": "Pipeline Reliability & Idempotency"
            },
            {
                "id": "q3",
                "type": "short_answer",
                "text": "In dimensional data modeling (Kimball), what kind of table stores quantitative metrics, timestamps, and foreign keys to dimension tables?",
                "correct_answer": "fact table",
                "explanation": "Fact tables record measurements, metrics, and transaction events, linked to surrounding descriptive dimension tables.",
                "skill_tag": "Dimensional Modeling"
            },
            {
                "id": "q4",
                "type": "mcq",
                "text": "Which SQL window function computes a running partition rank without leaving gaps between ties?",
                "options": [
                    "DENSE_RANK()",
                    "RANK()",
                    "ROW_NUMBER()",
                    "NTILE()"
                ],
                "correct_answer": "DENSE_RANK()",
                "explanation": "`DENSE_RANK()` assigns contiguous sequential integers when values tie, unlike `RANK()` which skips ranks.",
                "skill_tag": "Advanced SQL & Window Functions"
            }
        ]
    }
]

SEED_PROJECTS: List[Dict[str, Any]] = [
    {
        "id": "py-data-cleaner-101",
        "career_id": "ai-product-engineer",
        "skill_name": "Python Fundamentals",
        "difficulty": "beginner",
        "title": "Trading Log Ingestion & Data Cleaner",
        "tagline": "Build a resilient data ingestion function to sanitize messy financial transaction records.",
        "description": """### Project Overview
Financial transaction streams often arrive with noisy formatting, invalid currencies, missing values, and negative anomalies.

### Requirements
Implement the function:
```python
def clean_transactions(records: list) -> dict:
```

#### Task Rules:
1. **Filter Invalid Records**: Discard any record where `amount` is `<= 0`, `status` is `'FAILED'`, or `trade_id` is missing or null.
2. **Normalize Strings**:
   - `symbol`: strip whitespace and convert to uppercase (e.g. `' aapl '` $\to$ `'AAPL'`).
   - `currency`: standard 3-letter code uppercase (e.g. `'usd'` $\to$ `'USD'`).
3. **Calculate Aggregate Stats**: Return a dictionary containing:
   - `'valid_count'`: total count of valid processed records (int).
   - `'total_volume'`: sum of `amount` across valid records rounded to 2 decimal places (float).
   - `'unique_symbols'`: sorted list of distinct uppercase symbols (list of str).
   - `'cleaned_records'`: list of sanitized record dicts, sorted by `'trade_id'`.

If the input is empty or contains no valid records, return:
```python
{
    'valid_count': 0,
    'total_volume': 0.0,
    'unique_symbols': [],
    'cleaned_records': []
}
```
""",
        "starter_code": """# Trading Log Ingestion & Data Cleaner
# Implement clean_transactions according to the specifications

def clean_transactions(records: list) -> dict:
    valid_records = []
    total_volume = 0.0
    symbols = set()

    for item in records:
        # TODO: Validate trade_id, amount > 0, and status != 'FAILED'
        # TODO: Normalize symbol and currency
        # TODO: Aggregate totals
        pass

    return {
        "valid_count": 0,
        "total_volume": 0.0,
        "unique_symbols": [],
        "cleaned_records": []
    }
""",
        "sample_data": """trade_id,symbol,amount,currency,status
T-101, aapl ,150.50,usd,COMPLETED
T-102,msft,-45.00,usd,COMPLETED
T-103,  googl,320.00,usd,FAILED
T-104,aapl,80.25,usd,COMPLETED
T-105,,50.00,usd,COMPLETED
""",
        "hints": [
            "Start by checking if `not isinstance(records, list) or len(records) == 0` at the very top.",
            "Remember to verify `item.get('trade_id')` is truthy and `item.get('status', '').upper() != 'FAILED'`.",
            "Use `round(total_volume, 2)` to eliminate floating-point precision discrepancies.",
            "Sort `unique_symbols` with `sorted(list(symbols))` and `cleaned_records` with `sorted(valid_records, key=lambda x: x['trade_id'])`."
        ],
        "rubric": [
            {"criterion": "Functional Correctness", "weight": "60%", "description": "All test assertions pass cleanly with expected values."},
            {"criterion": "Defensive Validation", "weight": "25%", "description": "Handles nulls, missing keys, and invalid formats safely."},
            {"criterion": "Independent Problem Solving", "weight": "15%", "description": "Minimal reliance on hints during execution."}
        ],
        "public_test_cases": [
            {
                "name": "Standard Ingestion & Sanitization",
                "function_name": "clean_transactions",
                "args": [
                    [
                        {"trade_id": "T-1", "symbol": " aapl ", "amount": 100.5, "currency": "usd", "status": "COMPLETED"},
                        {"trade_id": "T-2", "symbol": "msft", "amount": 200.25, "currency": "usd", "status": "COMPLETED"},
                        {"trade_id": "T-3", "symbol": "googl", "amount": -50.0, "currency": "usd", "status": "COMPLETED"},
                        {"trade_id": "T-4", "symbol": "aapl", "amount": 50.0, "currency": "usd", "status": "FAILED"}
                    ]
                ],
                "expected": {
                    "valid_count": 2,
                    "total_volume": 300.75,
                    "unique_symbols": ["AAPL", "MSFT"],
                    "cleaned_records": [
                        {"trade_id": "T-1", "symbol": "AAPL", "amount": 100.5, "currency": "USD", "status": "COMPLETED"},
                        {"trade_id": "T-2", "symbol": "MSFT", "amount": 200.25, "currency": "USD", "status": "COMPLETED"}
                    ]
                }
            },
            {
                "name": "Empty Input Handling",
                "function_name": "clean_transactions",
                "args": [[]],
                "expected": {
                    "valid_count": 0,
                    "total_volume": 0.0,
                    "unique_symbols": [],
                    "cleaned_records": []
                }
            }
        ],
        "hidden_test_cases": [
            {
                "name": "Hidden: Corrupted Keys and Mixed Cases",
                "function_name": "clean_transactions",
                "args": [
                    [
                        {"trade_id": "T-99", "symbol": " nvda ", "amount": 500.0, "currency": "eur", "status": "completed"},
                        {"symbol": "tsla", "amount": 120.0, "currency": "usd", "status": "COMPLETED"},
                        {"trade_id": "T-98", "symbol": "nvda", "amount": 250.5, "currency": "EUR", "status": "COMPLETED"},
                        {"trade_id": "T-97", "symbol": "amzn", "amount": 0, "currency": "usd", "status": "COMPLETED"}
                    ]
                ],
                "expected": {
                    "valid_count": 2,
                    "total_volume": 750.5,
                    "unique_symbols": ["NVDA"],
                    "cleaned_records": [
                        {"trade_id": "T-98", "symbol": "NVDA", "amount": 250.5, "currency": "EUR", "status": "COMPLETED"},
                        {"trade_id": "T-99", "symbol": "NVDA", "amount": 500.0, "currency": "EUR", "status": "COMPLETED"}
                    ]
                }
            },
            {
                "name": "Hidden: All Invalid Rows",
                "function_name": "clean_transactions",
                "args": [
                    [
                        {"trade_id": "T-0", "symbol": "x", "amount": -10, "status": "COMPLETED"},
                        {"trade_id": "T-1", "symbol": "y", "amount": 10, "status": "FAILED"}
                    ]
                ],
                "expected": {
                    "valid_count": 0,
                    "total_volume": 0.0,
                    "unique_symbols": [],
                    "cleaned_records": []
                }
            }
        ]
    },
    {
        "id": "py-metrics-aggregator-201",
        "career_id": "data-systems-analyst",
        "skill_name": "Data Analysis & SQL",
        "difficulty": "intermediate",
        "title": "Event Stream Metrics & Cohort Aggregator",
        "tagline": "Build an analytical rollup engine to calculate conversion rates and active user counts.",
        "description": """### Project Overview
Product platforms record thousands of granular event pings. Analytics engineers translate these chronological event logs into cohort summaries.

### Requirements
Implement the function:
```python
def aggregate_user_funnel(events: list) -> dict:
```

#### Task Rules:
1. Each event is a dict: `{"user_id": str, "event": str, "timestamp": int}`.
2. Supported funnel stages in order: `'view'`, `'click'`, `'purchase'`.
3. Compute:
   - `'total_unique_users'`: total distinct user IDs (int).
   - `'stage_counts'`: count of unique users who performed each stage: `{"view": int, "click": int, "purchase": int}`.
   - `'click_through_rate'`: `(users who clicked / users who viewed)` rounded to 3 decimal places (float, 0.0 if views == 0).
   - `'conversion_rate'`: `(users who purchased / users who viewed)` rounded to 3 decimal places (float, 0.0 if views == 0).
   - `'top_purchasers'`: list of user IDs who had 2 or more purchase events, sorted alphabetically.
""",
        "starter_code": """# Event Stream Metrics & Cohort Aggregator
# Implement aggregate_user_funnel according to the specifications

def aggregate_user_funnel(events: list) -> dict:
    # TODO: Track unique users, events per user, and purchase counts
    return {
        "total_unique_users": 0,
        "stage_counts": {"view": 0, "click": 0, "purchase": 0},
        "click_through_rate": 0.0,
        "conversion_rate": 0.0,
        "top_purchasers": []
    }
""",
        "sample_data": """[
  {"user_id": "u1", "event": "view", "timestamp": 1600000001},
  {"user_id": "u1", "event": "click", "timestamp": 1600000005},
  {"user_id": "u1", "event": "purchase", "timestamp": 1600000010},
  {"user_id": "u2", "event": "view", "timestamp": 1600000020}
]""",
        "hints": [
            "Use sets to collect distinct `user_id` values per event type.",
            "Use a dictionary or `collections.Counter` to track how many purchase events each user triggered.",
            "Guard against division by zero when calculating rates if view count is 0."
        ],
        "rubric": [
            {"criterion": "Aggregation Accuracy", "weight": "60%", "description": "All stage metrics and conversion ratios computed accurately."},
            {"criterion": "Edge Case Safety", "weight": "25%", "description": "Safely handles missing stages and zero-division scenarios."},
            {"criterion": "Code Quality", "weight": "15%", "description": "Clean modular structures and type awareness."}
        ],
        "public_test_cases": [
            {
                "name": "Standard Funnel Event Stream",
                "function_name": "aggregate_user_funnel",
                "args": [
                    [
                        {"user_id": "u1", "event": "view", "timestamp": 10},
                        {"user_id": "u1", "event": "click", "timestamp": 12},
                        {"user_id": "u1", "event": "purchase", "timestamp": 15},
                        {"user_id": "u1", "event": "purchase", "timestamp": 20},
                        {"user_id": "u2", "event": "view", "timestamp": 30},
                        {"user_id": "u2", "event": "click", "timestamp": 35},
                        {"user_id": "u3", "event": "view", "timestamp": 40}
                    ]
                ],
                "expected": {
                    "total_unique_users": 3,
                    "stage_counts": {"view": 3, "click": 2, "purchase": 1},
                    "click_through_rate": 0.667,
                    "conversion_rate": 0.333,
                    "top_purchasers": ["u1"]
                }
            }
        ],
        "hidden_test_cases": [
            {
                "name": "Hidden: Zero Views Stream",
                "function_name": "aggregate_user_funnel",
                "args": [[]],
                "expected": {
                    "total_unique_users": 0,
                    "stage_counts": {"view": 0, "click": 0, "purchase": 0},
                    "click_through_rate": 0.0,
                    "conversion_rate": 0.0,
                    "top_purchasers": []
                }
            }
        ]
    }
]


def seed_arena_data(db: Session):
    """Seeds diagnostic assessments and mini project definitions if not present."""
    for diag in SEED_DIAGNOSTICS:
        existing = db.query(DiagnosticAssessment).filter(DiagnosticAssessment.id == diag["id"]).first()
        if not existing:
            db.add(DiagnosticAssessment(
                id=diag["id"],
                career_id=diag["career_id"],
                skill_name=diag["skill_name"],
                title=diag["title"],
                difficulty=diag["difficulty"],
                time_limit_mins=diag["time_limit_mins"],
                questions=diag["questions"]
            ))

    for proj in SEED_PROJECTS:
        existing = db.query(MiniProjectDefinition).filter(MiniProjectDefinition.id == proj["id"]).first()
        if not existing:
            db.add(MiniProjectDefinition(
                id=proj["id"],
                career_id=proj["career_id"],
                skill_name=proj["skill_name"],
                difficulty=proj["difficulty"],
                title=proj["title"],
                tagline=proj["tagline"],
                description=proj["description"],
                starter_code=proj["starter_code"],
                sample_data=proj.get("sample_data"),
                hints=proj["hints"],
                rubric=proj["rubric"],
                public_test_cases=proj["public_test_cases"],
                hidden_test_cases=proj["hidden_test_cases"]
            ))

    db.commit()
