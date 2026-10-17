export interface DiagnosticQuestion {
  id: string;
  type: 'mcq' | 'short_answer' | 'code_snippet';
  text: string;
  options?: string[];
  skill_tag: string;
}

export interface DiagnosticAssessmentData {
  id: string;
  career_id: string;
  skill_name: string;
  title: string;
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  time_limit_mins: number;
  questions: DiagnosticQuestion[];
}

export interface DiagnosticQuestionResult {
  question_id: string;
  question_text: string;
  user_answer: string;
  correct_answer: string;
  is_correct: boolean;
  explanation: string;
}

export interface DiagnosticSubmitResult {
  attempt_id: string;
  score: number;
  passed: boolean;
  correct_count: number;
  total_questions: number;
  strengths: string[];
  weaknesses: string[];
  confidence_level: 'low' | 'moderate' | 'high';
  question_results: DiagnosticQuestionResult[];
}

export interface TestCaseItem {
  name: string;
  function_name?: string;
  args?: any[];
  expected?: any;
}

export interface RubricItem {
  criterion: string;
  weight: string;
  description: string;
}

export interface MiniProjectData {
  id: string;
  career_id: string;
  skill_name: string;
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  title: string;
  tagline: string;
  description: string;
  starter_code: string;
  sample_data?: string;
  hints: string[];
  rubric: RubricItem[];
  public_test_cases: TestCaseItem[];
}

export interface TestVerdict {
  name: string;
  passed: boolean;
  actual?: string | null;
  expected?: string | null;
  error?: string | null;
  execution_time_ms: number;
  is_hidden?: boolean;
}

export interface ProjectRunResult {
  success: boolean;
  status: string;
  score: number;
  tests_passed: number;
  tests_total: number;
  test_results: TestVerdict[];
  output: string;
  error: string;
  execution_time_ms: number;
}

export interface RubricEvaluationItem {
  criterion: string;
  weight: string;
  score: number;
  passed: boolean;
  detail: string;
}

export interface ProjectSubmitResult {
  submission_id: string;
  status: string;
  score: number;
  tests_passed: number;
  tests_total: number;
  test_results: TestVerdict[];
  rubric_evaluation: RubricEvaluationItem[];
  feedback: {
    summary: string;
    has_ai_mentor_review: boolean;
    demonstrated_skills: string[];
    skills_to_practice: string[];
    composite_score: number;
    verdict: string;
  };
  execution_output: string;
  execution_time_ms: number;
  adaptive_next_challenge: AdaptiveChallengeRec;
}

export interface AdaptiveChallengeRec {
  action_type: 'project' | 'diagnostic';
  recommended_id: string;
  skill_name: string;
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  reason: string;
  target_type: string;
  target_title: string;
  prerequisites_met: boolean;
}

export interface DiagnosticHistoryItem {
  id: string;
  assessment_id: string;
  skill_name: string;
  difficulty: string;
  score: number;
  passed: boolean;
  total_questions: number;
  correct_count: number;
  strengths: string[];
  weaknesses: string[];
  confidence_level: string;
  created_at: string | null;
}

export interface ProjectHistoryItem {
  id: string;
  project_id: string;
  skill_name: string;
  status: string;
  score: number;
  tests_passed: number;
  tests_total: number;
  hints_used: number;
  feedback_summary?: string;
  created_at: string | null;
}

export interface SkillMasteryItem {
  id: string;
  skill_name: string;
  category: string;
  mastery_level: 'novice' | 'competent' | 'proficient' | 'advanced';
  mastery_score: number;
  diagnostic_score?: number | null;
  practical_score?: number | null;
  evidence_count: number;
  last_evidence_at: string | null;
}

export interface ArenaDashboardData {
  user_id: string;
  diagnostic_history: DiagnosticHistoryItem[];
  project_history: ProjectHistoryItem[];
  demonstrated_skills: string[];
  skills_to_practice: string[];
  mastery_records: SkillMasteryItem[];
  adaptive_recommendation: AdaptiveChallengeRec;
  study_time_hours: number;
}

// -------------------------------------------------------------
// Evidence-Based Skill Mapping Engine Types
// -------------------------------------------------------------

export interface EvidenceSkillItem {
  skill_name: string;
  confidence: 'High' | 'Medium' | 'Low';
  evidence_summary: string;
  file_paths: string[];
  observed_indicators: string[];
  missing_evidence: string;
  recommendation: string;
}

export interface SkillGapItem {
  area: string;
  observation: string;
  recommendation: string;
  severity: 'high' | 'medium' | 'low';
}

export interface PrioritizedNextStep {
  priority: number;
  type: 'immediate' | 'mini_project' | 'verification';
  title: string;
  description: string;
  action_label: string;
  target_id?: string | null;
}

export interface EvidenceReportData {
  repository_name: string;
  repo_url: string;
  commit_sha: string;
  scanned_files_count: number;
  is_sample_data: boolean;
  generated_at: string;
  detected_skills: EvidenceSkillItem[];
  skill_gaps: SkillGapItem[];
  prioritized_actions: PrioritizedNextStep[];
  ai_synthesis?: string | null;
  languages_detected: string[];
}

