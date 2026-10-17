# SkillTrace AI — Technical Design Document: Evidence-Based Repository Skill Assessment & Job-Matching Model

## 1. System Overview & Purpose

SkillTrace AI provides an authentic, verifiable bridge between software engineering/data analytics job requirements and concrete source code evidence in authorized public and private GitHub repositories.

Rather than relying on self-reported resume bullet points, unverified keywords, or black-box LLM hallucinations, SkillTrace AI inspects the actual Abstract Syntax Tree (AST), imports, function calls, class definitions, test suites, SQL queries, and configuration files. It produces traceable evidence citations pinned to commit SHAs, file paths, and exact line ranges.

---

## 2. Separation of the Three Core Measurements

The system strictly enforces the conceptual and mathematical separation of three distinct measurements:

| Measurement | Definition | Output Domain | Interpretation |
| :--- | :--- | :--- | :--- |
| **1. Skill Evidence Strength** ($E_s$) | How strongly the analysed repository code proves practical competence in skill $s$. | Categorical (`Strong`, `Moderate`, `Limited`, `No evidence found`, `Unable to assess`) + Continuous $[0, 100]$ | Reflects implementation depth, testing, and multi-file integration within the repository. |
| **2. Job Requirement Coverage** ($C_{\text{req}}$) | Proportion of a job's explicitly required and preferred skills that have verified repository evidence. | Percentage $[0, 100\%]$ | Explicitly split into $C_{\text{required}}$ and $C_{\text{preferred}}$. Measures breadth of matching skills. |
| **3. Overall Job Match** ($M_{\text{job}}$) | Explainable weighted compatibility between the candidate's repository evidence profile and the target job specification. | Continuous $[0, 100]$ or `"Insufficient evidence"` | Transparent ensemble formula displaying numerator, denominator, and explicit breakdown. **Never indicates probability of hire.** |

---

## 3. Mathematical Scoring Formulas

### 3.1 Skill Evidence Strength Score ($E_s \in [0, 100]$)

For a canonical skill $s$ assessed across repository files $\mathcal{F}$:

$$E_s = \min\left(100, \; w_{\text{impl}} \cdot N_{\text{impl}} + w_{\text{ast}} \cdot S_{\text{ast}} + w_{\text{test}} \cdot S_{\text{test}} + w_{\text{rec}} \cdot S_{\text{rec}} - P_{\text{import\_only}}\right)$$

Where:
- $N_{\text{impl}}$: Number of verified AST implementations (function defs, class defs, framework decorators, complex query joins). Weight: $25$ pts per substantial implementation (capped at 50).
- $S_{\text{ast}}$: AST depth score (call hierarchy, parameter usage, error handling). Max: $25$ pts.
- $S_{\text{test}}$: Test verification bonus (presence of asserts, pytest fixtures, or unit tests executing the module). Max: $15$ pts.
- $S_{\text{rec}}$: Recency and repository integration (file committed in active project structure). Max: $10$ pts.
- $P_{\text{import\_only}}$: Penalty (-20 pts) if a library is imported or listed in `requirements.txt` but never invoked in AST Call or Attribute nodes.

#### Evidence Categorization Rules:
- **Strong evidence** ($E_s \ge 70$): At least 2 substantial implementations OR coherent module with unit tests and class structures.
- **Moderate evidence** ($40 \le E_s < 70$): At least 1 meaningful implementation with verified AST calls and parameter configuration.
- **Limited evidence** ($15 \le E_s < 40$): Superficial code, basic tutorial syntax, or imports with minimal calls.
- **No evidence found** ($E_s = 0$): Analysed scope contained no occurrences of skill $s$.
- **Unable to assess**: Files in unsupported binary formats or repository access restricted.

### 3.2 Job Requirement Coverage ($C_{\text{req}}$ & $C_{\text{pref}}$)

Let $\mathcal{R}_{\text{req}}$ be the set of mandatory skills, and $\mathcal{R}_{\text{pref}}$ be the set of preferred skills:

$$C_{\text{required}} = \frac{|\{s \in \mathcal{R}_{\text{req}} : \text{status}(s) \in \{\text{Demonstrated}, \text{Partially demonstrated}\}\}|}{|\mathcal{R}_{\text{req}}|}$$

$$C_{\text{preferred}} = \frac{|\{p \in \mathcal{R}_{\text{pref}} : \text{status}(p) \in \{\text{Demonstrated}, \text{Partially demonstrated}\}\}|}{|\mathcal{R}_{\text{pref}}|}$$

If $|\mathcal{R}_{\text{req}}| = 0$, $C_{\text{required}}$ is marked as unconstrained (1.0).

### 3.3 Overall Job Match Score ($M_{\text{job}}$)

To ensure full transparency and avoid arbitrary black-box outputs, the overall score is computed with an explicit numerator and denominator:

$$\text{Numerator} = \sum_{s \in \mathcal{R}_{\text{req}}} w_{\text{req}} \cdot \alpha(s) \cdot E_s + \sum_{p \in \mathcal{R}_{\text{pref}}} w_{\text{pref}} \cdot \alpha(p) \cdot E_p + w_{\text{text}} \cdot S_{\text{text}} + w_{\text{exp}} \cdot S_{\text{exp}}$$

$$\text{Denominator} = w_{\text{req}} \cdot |\mathcal{R}_{\text{req}}| \cdot 100 + w_{\text{pref}} \cdot |\mathcal{R}_{\text{pref}}| \cdot 100 + w_{\text{text}} \cdot 100 + w_{\text{exp}} \cdot 100$$

$$M_{\text{job}} = \text{round}\left(100 \times \frac{\text{Numerator}}{\text{Denominator}}\right)$$

#### Weight Parameters:
- $w_{\text{req}} = 3.0$ (Mandatory job requirements carry 3x weight).
- $w_{\text{pref}} = 1.0$ (Preferred requirements carry 1x weight).
- $w_{\text{text}} = 0.5$ (TF-IDF domain semantic alignment between candidate summary & job responsibilities).
- $w_{\text{exp}} = 0.5$ (Seniority/experience level compatibility).
- $\alpha(s)$: Status multiplier ($1.0$ for `Demonstrated`, $0.6$ for `Partially demonstrated`, $0.0$ for `Not demonstrated`).

#### Insufficient Evidence Safeguard:
If $|\mathcal{F}| = 0$ (no authorized repositories analysed) or $\sum E_s = 0$ across all skills:
$$\text{Output} \leftarrow \text{"Insufficient evidence to compute a meaningful match score"}$$
The system never manufactures a default number or penalty score when evidence is missing.

---

## 4. Input Data & Output Labels

### 4.1 Input Data Specification
1. **Repository Source Files**:
   - Source code: `.py`, `.sql`, `.js`, `.ts`, `.java`, `.cpp`, `.ipynb`.
   - Configurations & Dependencies: `requirements.txt`, `pyproject.toml`, `package.json`, `Dockerfile`, `.github/workflows/*.yml`.
   - Documentation: `README.md`, `docs/*.md`.
2. **Provenance Metadata**:
   - Repository full name (e.g. `octocat/data-pipeline`).
   - Commit SHA (e.g. `7f8a3c4b...`).
   - File path, start line, end line, raw snippet.
3. **Target Job Specification**:
   - Title, employer, location, experience range.
   - Raw description text.
   - Structured skill requirements (required vs. preferred).

### 4.2 Output Labels & Taxonomies
1. **Skill Evidence Category**:
   - `Strong evidence`
   - `Moderate evidence`
   - `Limited evidence`
   - `No evidence found`
   - `Unable to assess`
2. **Requirement Match Status**:
   - `Demonstrated` (evidence strength $\ge 60$)
   - `Partially demonstrated` ($25 \le \text{strength} < 60$)
   - `Not demonstrated in analysed scope` (evidence not found; does NOT imply candidate lacks skill)
   - `Unable to assess` (unsupported format or ambiguous requirement)

---

## 5. Machine Learning Architecture & Training Pipeline

### 5.1 Supervised Evidence Classification Model
To distinguish authentic implementation depth from superficial keyword hits, we implement a supervised machine learning pipeline:

1. **Feature Extraction Pipeline**:
   - **Text Representation**: `TfidfVectorizer` (character n-grams $(3, 5)$ and word n-grams $(1, 2)$) on code snippet and docstrings.
   - **AST Structural Signals**: Vector of dense engineered metrics:
     - `call_count`: Number of distinct function calls.
     - `func_def_count`: Number of function definitions.
     - `class_def_count`: Number of class structures.
     - `test_assert_count`: Number of assertion statements.
     - `is_import_only`: Binary indicator if module is only imported without usage.
     - `is_tutorial_syntax`: Binary indicator for beginner patterns (`print("hello")`, `a = 1 + 2`).
     - `line_span`: Total physical lines in code block.
   - **Feature Combiner**: `FeatureUnion` combining TF-IDF representations with AST structural feature matrix.
2. **Model Choice**:
   - `CalibratedClassifierCV(LinearSVC)` / `RandomForestClassifier` with probability calibration via isotonic/sigmoid regression to output true posterior probabilities for evidence tiers.

### 5.2 Leakage Prevention Strategy (Repository Grouping)
- **Problem**: In software codebases, snippets from the same repository often share naming conventions, author styles, and helper functions. Standard random train/test splits cause high data leakage and falsely inflated accuracy.
- **Solution**: We implement **Group-K-Fold** cross-validation grouped strictly by `repository_id`. All snippets from a given repository reside exclusively in either the training split, validation split, or test split.

### 5.3 Evaluation Strategy & Metrics
- **Evidence Classifier**:
  - Precision, Recall, and Macro-F1 across all evidence categories (`Strong`, `Moderate`, `Limited`).
  - Expected Calibration Error (ECE) and Brier Score for confidence estimates.
- **Job Ranking & Matcher**:
  - Precision@1, Precision@3, Recall@3, NDCG@3, and Mean Reciprocal Rank (MRR) measured against human-validated job-candidate relevance pairs.
  - Comparative benchmark against rule-based and pure TF-IDF baselines.

---

## 6. Evidence Verification Layer

Every skill claim rendered in the UI must pass the Verification Layer:
1. **Path Existence**: File path must match an inspected file in the repository tree.
2. **Line Range Validation**: Specified start and end lines must correspond to valid line numbers in the file at the analyzed commit SHA.
3. **AST Node Tracing**: The snippet must contain the AST node (Call, FunctionDef, ClassDef) referenced by the extractor.
4. **Permanent Commit Pinning**: Links are generated in the form:
   `https://github.com/{repo}/blob/{commit_sha}/{filepath}#L{start}-L{end}`
5. **Transparency Disclaimer**: When a skill is marked `Not demonstrated in analysed scope`, the UI explicitly informs the recruiter/user:
   *"No code evidence found in analysed repository scope. This does not indicate a lack of proficiency."*
