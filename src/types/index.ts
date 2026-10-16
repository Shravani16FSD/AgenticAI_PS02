export type TaskStatus = 'not_started' | 'in_progress' | 'completed';

export type SkillProficiency = 'learning' | 'practicing' | 'proficient';

export interface UserProfile {
  name: string;
  studyStatus: string;
  targetCareerId: string;
  interests: string[];
  currentSkills: string[];
  primaryGoal: string;
  weeklyHours: number;
  onboardingCompleted: boolean;
}

export interface CareerPath {
  id: string;
  title: string;
  category: 'Engineering' | 'Design & UX' | 'Data & AI' | 'Systems & Cloud';
  tagline: string;
  matchReason: string;
  description: string;
  responsibilities: string[];
  requiredSkills: {
    name: string;
    importance: 'Essential' | 'Core' | 'Valuable';
    category: string;
  }[];
  learningPhases: {
    phase: string;
    focus: string;
    estimatedMonths: string;
  }[];
  recommendedNextStep: {
    title: string;
    whyItMatters: string;
    duration: string;
    resourceName: string;
    resourceUrl: string;
  };
  entryPoints: string[];
}

export interface RoadmapTask {
  id: string;
  phaseId: number;
  phaseName: string;
  title: string;
  description: string;
  skill: string;
  estimatedTime: string;
  status: TaskStatus;
  resourceName?: string;
  resourceType?: 'Documentation' | 'Course' | 'Interactive' | 'Project Spec';
  resourceUrl?: string;
  notes?: string;
}

export interface SkillProgress {
  id: string;
  name: string;
  category: string;
  status: SkillProficiency;
  hoursSpent: number;
  targetHours: number;
  lastPracticed: string;
}

export interface WeeklyActivityDay {
  day: string;
  shortDay: string;
  hours: number;
  dateStr: string;
}

export interface ChatMessage {
  id: string;
  sender: 'user' | 'assistant';
  text: string;
  timestamp: number;
  status?: 'sending' | 'thinking' | 'delivered' | 'error';
  suggestedActions?: string[];
}

export interface Toast {
  id: string;
  title: string;
  message?: string;
  type: 'success' | 'info' | 'warning' | 'error';
}
