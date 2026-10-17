"""
Standard Skill Taxonomy for SkillTrace AI.
Defines canonical technical skills across:
- Programming
- Data Analysis
- Machine Learning
- Software Engineering
- Analytics Engineering

Each skill has canonical names, aliases, relevant roles, AST and static evidence criteria,
and specific anti-patterns (such as unused imports or superficial stubs).
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set, Any


@dataclass
class SkillDefinition:
    canonical_name: str
    category: str
    aliases: List[str]
    relevant_roles: List[str]
    evidence_criteria: str
    file_patterns: List[str]
    ast_call_patterns: List[str] = field(default_factory=list)
    import_modules: List[str] = field(default_factory=list)
    anti_patterns: List[str] = field(default_factory=list)

    def matches_alias(self, query: str) -> bool:
        """Case-insensitive matching of query against canonical name or aliases."""
        clean_q = query.strip().lower()
        if clean_q == self.canonical_name.lower():
            return True
        for a in self.aliases:
            if clean_q == a.lower():
                return True
        return False


SKILL_TAXONOMY: List[SkillDefinition] = [
    # ------------------ Programming ------------------
    SkillDefinition(
        canonical_name="Python",
        category="Programming",
        aliases=["py", "python3", "python 3", "python programming"],
        relevant_roles=["Software Engineer", "Data Analyst", "Data Scientist", "ML Engineer", "Backend Developer"],
        evidence_criteria="Python source files (.py, .ipynb) with function defs, classes, list comprehensions, context managers, and type annotations.",
        file_patterns=[r"\.py$", r"\.ipynb$"],
        ast_call_patterns=["def ", "class ", "with ", "try:"],
        import_modules=["sys", "os", "typing", "collections", "functools"],
        anti_patterns=["Single line print('hello')", "empty script", "only imports without execution"]
    ),
    SkillDefinition(
        canonical_name="Java",
        category="Programming",
        aliases=["java 8", "java 11", "java 17", "java 21", "jvm", "core java"],
        relevant_roles=["Software Engineer", "Backend Developer", "Enterprise Developer"],
        evidence_criteria="Java source files (.java) with class definitions, interface implementations, Spring annotations, or JUnit tests.",
        file_patterns=[r"\.java$"],
        ast_call_patterns=["public class ", "public interface ", "@Autowired", "@Service"],
        import_modules=["java.util", "java.io", "org.springframework"],
        anti_patterns=["Empty main method without logic"]
    ),
    SkillDefinition(
        canonical_name="JavaScript",
        category="Programming",
        aliases=["js", "es6", "esnext", "ecmascript", "vanilla js", "modern javascript"],
        relevant_roles=["Frontend Developer", "Full Stack Developer", "Software Engineer"],
        evidence_criteria="JavaScript files (.js, .jsx, .mjs) containing async/await, DOM operations, export/import statements, closures, or Promise handling.",
        file_patterns=[r"\.js$", r"\.jsx$", r"\.mjs$"],
        ast_call_patterns=["async function", "addEventListener", "Promise", "fetch("],
        import_modules=["react", "express", "lodash"],
        anti_patterns=["Minified bundle files (dist/bundle.js)", "vendor scripts"]
    ),
    SkillDefinition(
        canonical_name="TypeScript",
        category="Programming",
        aliases=["ts", "typescript 4", "typescript 5"],
        relevant_roles=["Frontend Developer", "Full Stack Developer", "Software Engineer"],
        evidence_criteria="TypeScript files (.ts, .tsx) with interface definitions, type aliases, generic types, and strict null checks.",
        file_patterns=[r"\.ts$", r"\.tsx$"],
        ast_call_patterns=["interface ", "type ", "export const ", "<T>"],
        import_modules=["react", "@types/node"],
        anti_patterns=["`any` type everywhere, no custom interfaces"]
    ),
    SkillDefinition(
        canonical_name="C++",
        category="Programming",
        aliases=["cpp", "c/c++", "modern c++", "c++17", "c++20"],
        relevant_roles=["Systems Engineer", "Embedded Engineer", "Performance Engineer"],
        evidence_criteria="C++ source files (.cpp, .hpp, .cc) with class declarations, templates, smart pointers (std::unique_ptr), or STL algorithms.",
        file_patterns=[r"\.cpp$", r"\.hpp$", r"\.cc$", r"\.h$"],
        ast_call_patterns=["#include <", "std::", "template<", "class "],
        import_modules=["vector", "memory", "algorithm", "iostream"],
        anti_patterns=["Pure C syntax without STL or object orientation"]
    ),
    SkillDefinition(
        canonical_name="SQL",
        category="Programming",
        aliases=["structured query language", "postgresql", "mysql", "sqlite", "tsql", "plsql"],
        relevant_roles=["Data Analyst", "Analytics Engineer", "Backend Developer", "Database Administrator"],
        evidence_criteria="SQL files or embedded queries with JOINs, aggregations (GROUP BY, HAVING), CTEs (WITH), or window functions (OVER PARTITION BY).",
        file_patterns=[r"\.sql$", r"\.py$"],
        ast_call_patterns=["SELECT ", "JOIN ", "GROUP BY ", "WITH ", "OVER (PARTITION BY"],
        import_modules=["sqlite3", "psycopg2", "sqlalchemy"],
        anti_patterns=["Trivial single-table `SELECT * FROM table LIMIT 1`"]
    ),

    # ------------------ Data Analysis ------------------
    SkillDefinition(
        canonical_name="Data Cleaning",
        category="Data Analysis",
        aliases=["data cleansing", "data wrangling", "data preprocessing", "handling missing data", "outlier removal"],
        relevant_roles=["Data Analyst", "Data Scientist", "Analytics Engineer"],
        evidence_criteria="Imputation routines, dropna/fillna transformations, string normalization, type conversions, and deduplication logic.",
        file_patterns=[r"\.py$", r"\.ipynb$"],
        ast_call_patterns=["dropna(", "fillna(", "drop_duplicates(", "astype(", "apply(", "replace("],
        import_modules=["pandas", "numpy"],
        anti_patterns=["Calling dropna() once without inspection or parameters"]
    ),
    SkillDefinition(
        canonical_name="Pandas",
        category="Data Analysis",
        aliases=["pd", "pandas dataframe", "python pandas"],
        relevant_roles=["Data Analyst", "Data Scientist", "Analytics Engineer", "ML Engineer"],
        evidence_criteria="DataFrame and Series operations including groupby, merge, pivot_table, concat, datetime accessor, and aggregation functions.",
        file_patterns=[r"\.py$", r"\.ipynb$"],
        ast_call_patterns=["read_csv", "read_sql", "groupby", "merge", "pivot_table", "apply", "agg"],
        import_modules=["pandas"],
        anti_patterns=["`import pandas as pd` with zero calls in the file"]
    ),
    SkillDefinition(
        canonical_name="NumPy",
        category="Data Analysis",
        aliases=["np", "numpy arrays", "numerical python"],
        relevant_roles=["Data Scientist", "ML Engineer", "Data Analyst"],
        evidence_criteria="Vectorized array operations, linear algebra (np.linalg), broadcasting, indexing, or statistical aggregations (mean, std).",
        file_patterns=[r"\.py$", r"\.ipynb$"],
        ast_call_patterns=["np.array", "np.zeros", "np.dot", "np.mean", "np.where", "np.linalg"],
        import_modules=["numpy"],
        anti_patterns=["Importing numpy only for np.nan in a dictionary"]
    ),
    SkillDefinition(
        canonical_name="Data Visualization",
        category="Data Analysis",
        aliases=["data viz", "matplotlib", "seaborn", "plotly", "charting", "plotting"],
        relevant_roles=["Data Analyst", "Data Storyteller", "Data Scientist", "BI Developer"],
        evidence_criteria="Generating labeled visual plots (scatter, line, bar, heatmap, boxplot) with titles, axis labels, legends, or interactive layouts.",
        file_patterns=[r"\.py$", r"\.ipynb$"],
        ast_call_patterns=["plt.subplots", "sns.barplot", "sns.heatmap", "px.scatter", "plt.title", "plt.xlabel"],
        import_modules=["matplotlib.pyplot", "seaborn", "plotly.express"],
        anti_patterns=["Calling plt.show() without adding axes, titles, or formatting"]
    ),
    SkillDefinition(
        canonical_name="Exploratory Data Analysis",
        category="Data Analysis",
        aliases=["eda", "exploratory analysis", "data profiling", "statistical exploration"],
        relevant_roles=["Data Analyst", "Data Scientist"],
        evidence_criteria="Distributions inspection, correlation matrices (df.corr()), summary statistics (describe()), and hypothesis-driven data exploration.",
        file_patterns=[r"\.py$", r"\.ipynb$"],
        ast_call_patterns=["describe()", "info()", "corr()", "value_counts()", "nunique()"],
        import_modules=["pandas", "seaborn"],
        anti_patterns=["Only df.head() without subsequent statistical inspection"]
    ),
    SkillDefinition(
        canonical_name="Statistical Analysis",
        category="Data Analysis",
        aliases=["statistics", "hypothesis testing", "ab testing", "scipy.stats", "p-value", "anova"],
        relevant_roles=["Data Scientist", "Statistician", "Quantitative Analyst"],
        evidence_criteria="Significance tests (ttest_ind, chisquare), confidence intervals, regression p-values, or distribution fitting.",
        file_patterns=[r"\.py$", r"\.ipynb$"],
        ast_call_patterns=["ttest_ind", "stats.chi2_contingency", "stats.f_oneway", "ols("],
        import_modules=["scipy.stats", "statsmodels.api"],
        anti_patterns=["Just computing mean without statistical inferences"]
    ),
    SkillDefinition(
        canonical_name="Data Storytelling",
        category="Data Analysis",
        aliases=["business insights", "executive reporting", "narrative reporting", "markdown reports"],
        relevant_roles=["Lead Data Analyst", "Product Analyst", "Analytics Consultant"],
        evidence_criteria="Structured README or notebook markdown blocks articulating problem statement, methodology, key findings, and business recommendations.",
        file_patterns=[r"README\.md$", r"\.ipynb$", r"REPORT\.md$"],
        ast_call_patterns=["# Key Findings", "## Recommendations", "Executive Summary"],
        import_modules=[],
        anti_patterns=["Generic default README template"]
    ),

    # ------------------ Machine Learning ------------------
    SkillDefinition(
        canonical_name="Feature Engineering",
        category="Machine Learning",
        aliases=["feature extraction", "feature selection", "one-hot encoding", "scaling", "polynomial features"],
        relevant_roles=["Machine Learning Engineer", "Data Scientist"],
        evidence_criteria="Transforming raw variables into feature matrices via StandardScaler, OneHotEncoder, ColumnTransformer, PCA, or domain-specific aggregations.",
        file_patterns=[r"\.py$", r"\.ipynb$"],
        ast_call_patterns=["StandardScaler", "OneHotEncoder", "ColumnTransformer", "fit_transform", "SelectKBest"],
        import_modules=["sklearn.preprocessing", "sklearn.feature_selection"],
        anti_patterns=["Feeding raw unstructured text directly into a model"]
    ),
    SkillDefinition(
        canonical_name="Model Training",
        category="Machine Learning",
        aliases=["model fit", "supervised learning", "estimator training", "hyperparameter tuning"],
        relevant_roles=["Machine Learning Engineer", "Data Scientist"],
        evidence_criteria="Invoking estimator.fit() with training data, GridSearch/RandomizedSearchCV, cross-validation, or training loops.",
        file_patterns=[r"\.py$", r"\.ipynb$"],
        ast_call_patterns=[".fit(", "GridSearchCV", "RandomizedSearchCV", "cross_val_score"],
        import_modules=["sklearn", "xgboost", "lightgbm"],
        anti_patterns=["Calling fit() on test data directly (data leakage)"]
    ),
    SkillDefinition(
        canonical_name="Model Evaluation",
        category="Machine Learning",
        aliases=["model validation", "metrics", "confusion matrix", "roc auc", "classification report", "rmse"],
        relevant_roles=["Machine Learning Engineer", "Data Scientist"],
        evidence_criteria="Computing held-out test metrics: classification_report, roc_auc_score, confusion_matrix, mean_squared_error, or r2_score.",
        file_patterns=[r"\.py$", r"\.ipynb$"],
        ast_call_patterns=["classification_report", "roc_auc_score", "confusion_matrix", "mean_squared_error", "r2_score"],
        import_modules=["sklearn.metrics"],
        anti_patterns=["Evaluating accuracy only on training split"]
    ),
    SkillDefinition(
        canonical_name="Scikit-learn",
        category="Machine Learning",
        aliases=["sklearn", "scikit learn", "scikit-learn"],
        relevant_roles=["Machine Learning Engineer", "Data Scientist", "Data Analyst"],
        evidence_criteria="Using scikit-learn Pipeline, BaseEstimator, transformers, and classifiers.",
        file_patterns=[r"\.py$", r"\.ipynb$"],
        ast_call_patterns=["Pipeline(", "RandomForest", "LogisticRegression", "train_test_split"],
        import_modules=["sklearn"],
        anti_patterns=["`import sklearn` without any instantiated estimator or function"]
    ),
    SkillDefinition(
        canonical_name="Deep Learning",
        category="Machine Learning",
        aliases=["pytorch", "tensorflow", "keras", "neural networks", "torch", "transformers", "huggingface"],
        relevant_roles=["Machine Learning Engineer", "Deep Learning Researcher", "AI Engineer"],
        evidence_criteria="PyTorch nn.Module or TensorFlow Keras models, loss functions, backward passes (loss.backward()), optimizers, and DataLoader.",
        file_patterns=[r"\.py$", r"\.ipynb$"],
        ast_call_patterns=["nn.Module", "torch.optim", "tf.keras.Sequential", "loss.backward()", "DataLoader("],
        import_modules=["torch", "tensorflow", "transformers"],
        anti_patterns=["Importing torch without defining or running a tensor graph"]
    ),

    # ------------------ Software Engineering ------------------
    SkillDefinition(
        canonical_name="APIs",
        category="Software Engineering",
        aliases=["rest api", "fastapi", "flask", "api design", "endpoints", "express api", "http routes"],
        relevant_roles=["Backend Developer", "Full Stack Developer", "Software Engineer"],
        evidence_criteria="Routing decorators (@app.get, @router.post, app.use), request validation (Pydantic, schemas), HTTP response status codes.",
        file_patterns=[r"\.py$", r"\.js$", r"\.ts$"],
        ast_call_patterns=["@app.get", "@router.post", "@app.route", "HTTPException", "status_code"],
        import_modules=["fastapi", "flask", "express"],
        anti_patterns=["Stub route returning static string with no parameter handling"]
    ),
    SkillDefinition(
        canonical_name="Database Design",
        category="Software Engineering",
        aliases=["rdbms", "sqlalchemy", "prisma", "schemas", "orm", "foreign keys", "migrations", "entity relationship"],
        relevant_roles=["Backend Developer", "Database Architect", "Software Engineer"],
        evidence_criteria="Relational ORM models with Column, ForeignKey, relationship definitions, Alembic migration files, or DDL schemas.",
        file_patterns=[r"\.py$", r"\.sql$", r"\.prisma$"],
        ast_call_patterns=["Column(", "ForeignKey(", "relationship(", "primary_key=True", "CREATE TABLE"],
        import_modules=["sqlalchemy", "alembic", "prisma"],
        anti_patterns=["Raw unindexed single-column table"]
    ),
    SkillDefinition(
        canonical_name="Testing",
        category="Software Engineering",
        aliases=["unit testing", "pytest", "unittest", "integration tests", "test suite", "assertions", "jest"],
        relevant_roles=["Software Engineer", "QA Engineer", "Backend Developer"],
        evidence_criteria="Test files (test_*.py, *.test.ts) containing assert statements, pytest fixtures (@pytest.fixture), TestCase classes, or mocks.",
        file_patterns=[r"test_.*\.py$", r".*_test\.py$", r"\.test\.(ts|js)$"],
        ast_call_patterns=["assert ", "@pytest.fixture", "unittest.TestCase", "mock.", "expect("],
        import_modules=["pytest", "unittest", "unittest.mock"],
        anti_patterns=["Empty test function with pass"]
    ),
    SkillDefinition(
        canonical_name="Authentication",
        category="Software Engineering",
        aliases=["auth", "jwt", "oauth", "password hashing", "bcrypt", "session management", "rbac"],
        relevant_roles=["Backend Developer", "Security Engineer", "Full Stack Developer"],
        evidence_criteria="Password hashing (bcrypt.hashpw), JWT token encoding/decoding, OAuth authorization flows, or middleware role checks.",
        file_patterns=[r"\.py$", r"\.ts$", r"\.js$"],
        ast_call_patterns=["jwt.encode", "jwt.decode", "bcrypt.hashpw", "OAuth2PasswordBearer", "check_password_hash"],
        import_modules=["jwt", "jose", "passlib", "bcrypt"],
        anti_patterns=["Storing plain text passwords"]
    ),
    SkillDefinition(
        canonical_name="Error Handling",
        category="Software Engineering",
        aliases=["exceptions", "exception handling", "try catch", "custom exceptions", "defensive programming"],
        relevant_roles=["Software Engineer", "Backend Developer"],
        evidence_criteria="Try/except blocks with specific exception classes, custom Exception subclasses, logging error context, or HTTP error mappings.",
        file_patterns=[r"\.py$", r"\.java$", r"\.ts$"],
        ast_call_patterns=["try:", "except Exception", "except (", "raise HTTPException", "logger.error"],
        import_modules=["logging"],
        anti_patterns=["Bare except: pass (swallowing exceptions silently)"]
    ),
    SkillDefinition(
        canonical_name="Git",
        category="Software Engineering",
        aliases=["version control", "git workflows", "branching", "commits", "pull requests"],
        relevant_roles=["All Technical Roles"],
        evidence_criteria="Meaningful commit history, .gitignore configuration, git tags, or structured pull request workflows.",
        file_patterns=[r"\.gitignore$", r"\.git/"],
        ast_call_patterns=["git commit", "git push"],
        import_modules=[],
        anti_patterns=["Single initial commit containing all code at once"]
    ),
    SkillDefinition(
        canonical_name="CI/CD",
        category="Software Engineering",
        aliases=["continuous integration", "github actions", "gitlab ci", "jenkins", "docker build", "automation"],
        relevant_roles=["DevOps Engineer", "Software Engineer", "MLOps Engineer"],
        evidence_criteria="Workflow configuration files (.github/workflows/*.yml) running test suites, linting, build steps, or container packaging.",
        file_patterns=[r"\.github/workflows/.*\.ya?ml$", r"Dockerfile$", r"docker-compose\.ya?ml$"],
        ast_call_patterns=["runs-on:", "steps:", "actions/checkout", "pip install", "pytest"],
        import_modules=[],
        anti_patterns=["Empty workflow with placeholder echo command"]
    ),

    # ------------------ Analytics Engineering ------------------
    SkillDefinition(
        canonical_name="SQL Transformations",
        category="Analytics Engineering",
        aliases=["dbt", "data transformations", "dbt models", "sql modeling", "jinja sql"],
        relevant_roles=["Analytics Engineer", "Data Engineer"],
        evidence_criteria="Multi-stage staging/marts data models, ref() macros in dbt, incremental models, and surrogate keys.",
        file_patterns=[r"models/.*\.sql$", r"\.sql$"],
        ast_call_patterns=["{{ config(", "{{ ref(", "surrogate_key", "WITH source AS"],
        import_modules=["dbt"],
        anti_patterns=["Single temporary query without reusable model structure"]
    ),
    SkillDefinition(
        canonical_name="Data Modeling",
        category="Analytics Engineering",
        aliases=["dimensional modeling", "star schema", "snowflake schema", "fact tables", "dimension tables"],
        relevant_roles=["Analytics Engineer", "Data Architect", "BI Developer"],
        evidence_criteria="Dimensional schemas defining dim_* and fct_* tables with surrogate keys, grain declarations, and relationships.",
        file_patterns=[r"\.sql$", r"schema\.ya?ml$"],
        ast_call_patterns=["dim_", "fct_", "surrogate_key", "foreign key"],
        import_modules=[],
        anti_patterns=["Denormalized mega-table with no primary keys"]
    ),
    SkillDefinition(
        canonical_name="Data Pipelines",
        category="Analytics Engineering",
        aliases=["etl", "elt", "data ingestion", "pipeline orchestration", "airflow dag", "prefect", "dagster"],
        relevant_roles=["Data Engineer", "Analytics Engineer"],
        evidence_criteria="Directed Acyclic Graphs (Airflow DAG, Prefect flow) orchestrating scheduled tasks, dependency chaining (>>), and retries.",
        file_patterns=[r"dags/.*\.py$", r"pipelines/.*\.py$", r"\.py$"],
        ast_call_patterns=["@dag", "DAG(", "@flow", "@task", ">>"],
        import_modules=["airflow", "prefect", "dagster"],
        anti_patterns=["Cron script with no logging or error handling"]
    ),
    SkillDefinition(
        canonical_name="Data Quality Testing",
        category="Analytics Engineering",
        aliases=["dbt test", "great expectations", "data validation", "schema testing", "asserting data quality"],
        relevant_roles=["Analytics Engineer", "Data Engineer"],
        evidence_criteria="Automated data contract checks: unique tests, not_null tests, relationships tests, Great Expectations suites.",
        file_patterns=[r"schema\.ya?ml$", r"tests/.*\.sql$", r"expectations/.*\.json$"],
        ast_call_patterns=["unique:", "not_null:", "expect_column_values_to_not_be_null", "relationships:"],
        import_modules=["great_expectations"],
        anti_patterns=["Manual visual check of data in CSV"]
    ),
    SkillDefinition(
        canonical_name="Workflow Orchestration",
        category="Analytics Engineering",
        aliases=["orchestration", "airflow", "dag schedule", "task scheduling"],
        relevant_roles=["Data Engineer", "Analytics Engineer"],
        evidence_criteria="Managing task dependencies, sensors, retry intervals, execution timeouts, and failure callbacks.",
        file_patterns=[r"\.py$", r"airflow.*\.py$"],
        ast_call_patterns=["schedule_interval=", "retries=", "on_failure_callback=", "PythonOperator("],
        import_modules=["airflow.operators"],
        anti_patterns=["Running sequential scripts in an infinite while loop"]
    ),
    SkillDefinition(
        canonical_name="Docker",
        category="Software Engineering",
        aliases=["dockerfile", "containerization", "docker compose", "containers", "docker-compose"],
        relevant_roles=["Software Engineer", "Backend Developer", "DevOps Engineer", "ML Engineer"],
        evidence_criteria="Dockerfile or docker-compose.yml files with multi-stage builds and environment configurations.",
        file_patterns=[r"dockerfile", r"docker-compose\.ya?ml$"],
        ast_call_patterns=["FROM ", "RUN ", "COPY ", "ENTRYPOINT ", "CMD "],
        anti_patterns=["Empty placeholder Dockerfile"]
    ),
    SkillDefinition(
        canonical_name="Kubernetes",
        category="Software Engineering",
        aliases=["k8s", "kubectl", "helm", "container orchestration"],
        relevant_roles=["DevOps Engineer", "Cloud Engineer", "Backend Developer"],
        evidence_criteria="Kubernetes manifests (.yaml) defining Deployments, Services, ConfigMaps, or Ingress.",
        file_patterns=[r"k8s/.*\.ya?ml$", r"deployment\.ya?ml$"],
        ast_call_patterns=["apiVersion:", "kind: Deployment", "kind: Service"],
        anti_patterns=["Unconfigured template yaml"]
    ),
]



class SkillTaxonomyRegistry:
    """Central lookup and canonical normalization registry for skills."""

    def __init__(self, definitions: List[SkillDefinition] = SKILL_TAXONOMY):
        self.definitions = definitions
        self._canonical_map: Dict[str, SkillDefinition] = {}
        self._alias_map: Dict[str, SkillDefinition] = {}
        self._build_index()

    def _build_index(self):
        for item in self.definitions:
            canon_lower = item.canonical_name.lower()
            self._canonical_map[canon_lower] = item
            self._alias_map[canon_lower] = item
            for alias in item.aliases:
                self._alias_map[alias.lower()] = item

    def normalize(self, skill_query: str) -> Optional[SkillDefinition]:
        """Resolves an arbitrary skill name to its canonical definition."""
        clean = skill_query.strip().lower()
        return self._alias_map.get(clean)

    def get(self, skill_query: str) -> Optional[SkillDefinition]:
        """Alias for normalize, providing standard dict-style retrieval."""
        return self.normalize(skill_query)

    def get_canonical_name(self, skill_query: str) -> str:

        """Returns the canonical name if found in taxonomy, else returns formatted query."""
        match = self.normalize(skill_query)
        if match:
            return match.canonical_name
        return skill_query.strip()

    def get_skills_by_category(self, category: str) -> List[SkillDefinition]:
        return [s for s in self.definitions if s.category.lower() == category.lower()]

    def all_canonical_names(self) -> List[str]:
        return [s.canonical_name for s in self.definitions]

    def all_categories(self) -> List[str]:
        seen = []
        for s in self.definitions:
            if s.category not in seen:
                seen.append(s.category)
        return seen


# Global singleton instance
taxonomy_registry = SkillTaxonomyRegistry()
