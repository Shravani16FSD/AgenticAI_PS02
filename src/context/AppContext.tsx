import React, { createContext, useContext, useState, useEffect, useMemo, type ReactNode } from 'react';
import type { UserProfile, CareerPath, RoadmapTask, SkillProgress, ChatMessage, Toast, TaskStatus } from '../types';
import { INITIAL_CAREER_PATHS, INITIAL_ROADMAP_TASKS, INITIAL_SKILLS } from '../data/careers';
import { apiClient } from '../services/apiClient';

interface AppContextType {
  profile: UserProfile;
  updateProfile: (updates: Partial<UserProfile>) => void;
  resetAllData: () => void;
  careerPaths: CareerPath[];
  savedCareerIds: string[];
  toggleSaveCareer: (id: string) => void;
  isCareerSaved: (id: string) => boolean;
  roadmapTasks: RoadmapTask[];
  updateTaskStatus: (taskId: string, status: TaskStatus) => void;
  addTask: (task: Omit<RoadmapTask, 'id'>) => void;
  deleteTask: (taskId: string) => void;
  skills: SkillProgress[];
  updateSkill: (skillId: string, updates: Partial<SkillProgress>) => void;
  addSkill: (skill: Omit<SkillProgress, 'id'>) => void;
  chatMessages: ChatMessage[];
  addChatMessage: (msg: ChatMessage) => void;
  updateChatMessage: (id: string, updates: Partial<ChatMessage>) => void;
  clearChat: () => void;
  toasts: Toast[];
  addToast: (toast: Omit<Toast, 'id'>) => void;
  removeToast: (id: string) => void;
  completedTasksCount: number;
  totalTasksCount: number;
  overallProgressPercent: number;
  activeCareer: CareerPath | undefined;
  activeUserId: string;
  isLoggedIn: boolean;
  availableUsers: AvailableUser[];
  loginUser: (userId: string) => Promise<boolean>;
  logoutUser: () => Promise<void>;
}

export interface AvailableUser {
  id: string;
  name: string;
  target_career_id?: string;
  study_status?: string;
  primary_goal?: string;
  interests?: string[];
  role?: string;
  avatarInitials?: string;
}

export const SEEDED_USERS: AvailableUser[] = [
  {
    id: 'default_user',
    name: 'Alex Morgan',
    target_career_id: 'ai-product-engineer',
    study_status: 'Third-year CS & Machine Learning Honors Student',
    primary_goal: 'Secure a Summer 2027 AI Product & Stream Processing Engineering Internship',
    interests: ['Distributed Systems', 'Data Pipelines', 'PyTorch & MLOps', 'Stream Processing', 'Vector Search'],
    role: 'AI Product & Data Pipeline Engineer',
    avatarInitials: 'AM'
  },
  {
    id: 'user_jordan_chen',
    name: 'Jordan Chen',
    target_career_id: 'product-designer',
    study_status: 'Design Systems Architect & Accessibility Lead',
    primary_goal: 'Scale tokenized cross-platform design systems and achieve 100% WCAG 2.2 AAA audit compliance',
    interests: ['Design Tokens', 'WCAG 2.2 AAA Accessibility', 'Component Systems', 'Micro-interactions', 'Headless UI'],
    role: 'Lead Design Systems & Accessibility Architect',
    avatarInitials: 'JC'
  },
  {
    id: 'user_priya_sharma',
    name: 'Priya Sharma',
    target_career_id: 'data-systems-analyst',
    study_status: 'Analytics Engineering & Financial Marts Specialist',
    primary_goal: 'Architect reliable dimensional models and enterprise dbt transformation pipelines',
    interests: ['dbt Core & Modeling', 'Financial Data Marts', 'Snowflake Observability', 'Dimensional Schemas', 'BI Metrics'],
    role: 'Staff Analytics Engineer & Financial Marts Lead',
    avatarInitials: 'PS'
  },
  {
    id: 'user_marcus_vance',
    name: 'Marcus Vance',
    target_career_id: 'ai-product-engineer',
    study_status: 'High-Performance Graphics & Zero-Trust AppSec Specialist',
    primary_goal: 'Engineer ultra-low-latency WebGL canvas rendering engines and hardened sandbox harnesses',
    interests: ['WebGL & WebGPU', 'Virtualized Canvas Grids', 'Memory Safety & WASM', 'Zero-Trust Security', 'Low-Level Graphics'],
    role: 'Principal Systems & Graphics Engineer',
    avatarInitials: 'MV'
  }
];

const STORAGE_KEYS = {
  PROFILE: 'nexora_user_profile',
  SAVED_CAREERS: 'nexora_saved_careers',
  ROADMAP: 'nexora_roadmap_tasks',
  SKILLS: 'nexora_skills',
  CHAT: 'nexora_chat_history',
};

const DEFAULT_PROFILE: UserProfile = {
  name: 'Alex Morgan',
  studyStatus: 'Third-year CS & Machine Learning Honors Student',
  targetCareerId: 'ai-product-engineer',
  interests: ['Distributed Systems', 'Data Pipelines', 'PyTorch & MLOps', 'Stream Processing', 'Vector Search'],
  currentSkills: ['Python', 'Pandas', 'FastAPI', 'PyTorch', 'Kafka Basics'],
  primaryGoal: 'Secure a Summer 2027 AI Product & Stream Processing Engineering Internship',
  weeklyHours: 8,
  onboardingCompleted: true,
};

const INITIAL_GREETING_MESSAGE: ChatMessage = {
  id: 'msg-welcome',
  sender: 'assistant',
  text: `Hello. I am NEXORA, your career mentor.

Your career is a journey, and you do not need to figure everything out today. Whether you want to reflect on what path fits your strengths, structure your weekly learning, or prepare for internship applications, I am here to work through it with you step-by-step.

Where would you like to start today?`,
  timestamp: Date.now() - 3600000,
  status: 'delivered',
  suggestedActions: [
    'Help me choose a career direction.',
    'What should I learn to become an AI engineer?',
    'Can you help me prepare for an internship?',
    'Let\'s make a realistic weekly learning plan.'
  ]
};

let nextIdCounter = 1;
export const generateId = (prefix: string) => `${prefix}-${Date.now().toString(36)}-${++nextIdCounter}`;

export const AppContext = createContext<AppContextType | undefined>(undefined);

export const AppProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  // 1. Profile State
  const [profile, setProfile] = useState<UserProfile>(() => {
    try {
      const saved = localStorage.getItem(STORAGE_KEYS.PROFILE);
      return saved ? JSON.parse(saved) : DEFAULT_PROFILE;
    } catch {
      return DEFAULT_PROFILE;
    }
  });

  // 2. Saved Careers
  const [savedCareerIds, setSavedCareerIds] = useState<string[]>(() => {
    try {
      const saved = localStorage.getItem(STORAGE_KEYS.SAVED_CAREERS);
      return saved ? JSON.parse(saved) : ['ai-product-engineer', 'product-designer'];
    } catch {
      return ['ai-product-engineer', 'product-designer'];
    }
  });

  // 3. Roadmap Tasks
  const [roadmapTasks, setRoadmapTasks] = useState<RoadmapTask[]>(() => {
    try {
      const saved = localStorage.getItem(STORAGE_KEYS.ROADMAP);
      return saved ? JSON.parse(saved) : INITIAL_ROADMAP_TASKS;
    } catch {
      return INITIAL_ROADMAP_TASKS;
    }
  });

  // 4. Skills
  const [skills, setSkills] = useState<SkillProgress[]>(() => {
    try {
      const saved = localStorage.getItem(STORAGE_KEYS.SKILLS);
      return saved ? JSON.parse(saved) : INITIAL_SKILLS;
    } catch {
      return INITIAL_SKILLS;
    }
  });

  // 5. Chat Messages
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>(() => {
    try {
      const saved = localStorage.getItem(STORAGE_KEYS.CHAT);
      return saved ? JSON.parse(saved) : [INITIAL_GREETING_MESSAGE];
    } catch {
      return [INITIAL_GREETING_MESSAGE];
    }
  });

  // 6. Toasts (in-memory)
  const [toasts, setToasts] = useState<Toast[]>([]);

  // 7. Active User & Multi-User Support
  const [activeUserId, setActiveUserId] = useState<string>(() => {
    return apiClient.getActiveUserId() || 'default_user';
  });
  const [isLoggedIn, setIsLoggedIn] = useState<boolean>(() => {
    return Boolean(apiClient.getActiveUserId() || localStorage.getItem('chapter_session_user') || localStorage.getItem('nexora_session_user'));
  });
  const [availableUsers, setAvailableUsers] = useState<AvailableUser[]>(SEEDED_USERS);

  const loadUserDataForSession = async () => {
    const isLive = await apiClient.checkHealth();
    if (!isLive) return;

    try {
      const [usersList, remoteProfile, remoteSaved, remoteRoadmap, remoteSkills, remoteChat] = await Promise.all([
        apiClient.getAvailableUsers(),
        apiClient.getProfile(),
        apiClient.getSavedCareerIds(),
        apiClient.getRoadmap(),
        apiClient.getSkills(),
        apiClient.getChatHistory()
      ]);

      if (usersList && usersList.length > 0) {
        setAvailableUsers(
          usersList.map(u => {
            const seed = SEEDED_USERS.find(s => s.id === u.id);
            return {
              ...u,
              interests: seed?.interests || ['Technology', 'Software Engineering'],
              role: seed?.role || u.study_status,
              avatarInitials: seed?.avatarInitials || u.name.slice(0, 2).toUpperCase()
            };
          })
        );
      }
      if (remoteProfile) {
        setProfile(remoteProfile);
      }
      if (remoteSaved) {
        setSavedCareerIds(remoteSaved);
      }
      if (remoteRoadmap && remoteRoadmap.length > 0) {
        setRoadmapTasks(remoteRoadmap);
      }
      if (remoteSkills && remoteSkills.length > 0) {
        setSkills(remoteSkills);
      }
      if (remoteChat && remoteChat.length > 0) {
        setChatMessages(remoteChat);
      }
    } catch (e) {
      console.warn('Error loading remote user session data', e);
    }
  };

  const loginUser = async (userId: string): Promise<boolean> => {
    const normalizedId = userId.toLowerCase() === 'jordan' || userId.toLowerCase() === 'jordan_chen' ? 'user_jordan_chen'
      : userId.toLowerCase() === 'priya' || userId.toLowerCase() === 'priya_sharma' ? 'user_priya_sharma'
      : userId.toLowerCase() === 'marcus' || userId.toLowerCase() === 'marcus_vance' ? 'user_marcus_vance'
      : userId.toLowerCase() === 'alex' || userId.toLowerCase() === 'alex_morgan' ? 'default_user'
      : userId;

    const isLive = await apiClient.checkHealth();
    if (isLive) {
      await apiClient.login(normalizedId);
    } else {
      apiClient.setSession(`token_${normalizedId}`, normalizedId);
    }

    setActiveUserId(normalizedId);
    setIsLoggedIn(true);

    const seed = SEEDED_USERS.find(s => s.id === normalizedId);
    if (seed) {
      setProfile(prev => ({
        ...prev,
        name: seed.name,
        studyStatus: seed.study_status || prev.studyStatus,
        targetCareerId: seed.target_career_id || prev.targetCareerId,
        primaryGoal: seed.primary_goal || prev.primaryGoal,
        interests: seed.interests || prev.interests,
        currentSkills: seed.id === 'user_jordan_chen' ? ['Design Tokens', 'WCAG 2.2 AAA', 'TypeScript', 'Component Systems']
          : seed.id === 'user_priya_sharma' ? ['dbt Core', 'Snowflake', 'SQL Transformations', 'Dimensional Modeling']
          : seed.id === 'user_marcus_vance' ? ['WebGL', 'WebGPU', 'Canvas Virtualization', 'AppSec Sandboxing']
          : ['Python', 'Pandas', 'FastAPI', 'PyTorch']
      }));
    }

    if (isLive) {
      await loadUserDataForSession();
    }

    addToast({
      type: 'success',
      title: 'Welcome to NEXORA',
      message: `Signed in as ${seed?.name || normalizedId}. Dashboard personalized.`
    });
    return true;
  };

  const logoutUser = async (): Promise<void> => {
    try {
      const isLive = await apiClient.checkHealth();
      if (isLive) {
        await apiClient.logout();
      } else {
        apiClient.setSession(null, null);
      }
    } catch {
      apiClient.setSession(null, null);
    }

    setIsLoggedIn(false);
    setActiveUserId('');
    try {
      localStorage.removeItem(STORAGE_KEYS.PROFILE);
    } catch {}

    addToast({
      type: 'info',
      title: 'Logged Out',
      message: 'You have been signed out of your NEXORA account.'
    });
  };

  // Load remote database state on startup if available
  useEffect(() => {
    loadUserDataForSession();
  }, []);

  // Persistent storage synchronizations
  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEYS.PROFILE, JSON.stringify(profile));
    } catch (e) {
      console.warn('Could not persist profile to localStorage', e);
    }
  }, [profile]);

  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEYS.SAVED_CAREERS, JSON.stringify(savedCareerIds));
    } catch (e) {
      console.warn('Could not persist saved careers', e);
    }
  }, [savedCareerIds]);

  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEYS.ROADMAP, JSON.stringify(roadmapTasks));
    } catch (e) {
      console.warn('Could not persist roadmap', e);
    }
  }, [roadmapTasks]);

  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEYS.SKILLS, JSON.stringify(skills));
    } catch (e) {
      console.warn('Could not persist skills', e);
    }
  }, [skills]);

  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEYS.CHAT, JSON.stringify(chatMessages));
    } catch (e) {
      console.warn('Could not persist chat', e);
    }
  }, [chatMessages]);

  // Actions
  const updateProfile = (updates: Partial<UserProfile>) => {
    setProfile(prev => {
      const updated = { ...prev, ...updates };
      apiClient.updateProfile(updated);
      return updated;
    });
    addToast({
      title: 'Profile updated',
      message: 'Your preferences have been saved.',
      type: 'success'
    });
  };

  const toggleSaveCareer = (id: string) => {
    setSavedCareerIds(prev => {
      const exists = prev.includes(id);
      const updated = exists ? prev.filter(c => c !== id) : [...prev, id];
      if (exists) {
        apiClient.removeSavedCareer(id);
      } else {
        apiClient.saveCareer(id);
      }
      addToast({
        title: exists ? 'Career removed' : 'Career saved',
        message: exists ? 'Removed from your saved list.' : 'Saved to your career paths.',
        type: 'info'
      });
      return updated;
    });
  };

  const isCareerSaved = (id: string) => savedCareerIds.includes(id);

  const updateTaskStatus = (taskId: string, status: TaskStatus) => {
    setRoadmapTasks(prev =>
      prev.map(t => (t.id === taskId ? { ...t, status } : t))
    );
    apiClient.updateTask(taskId, { status });
    if (status === 'completed') {
      addToast({
        title: 'Milestone completed',
        message: 'Great progress. Small steps count.',
        type: 'success'
      });
    }
  };

  const addTask = (task: Omit<RoadmapTask, 'id'>) => {
    const tempId = generateId('task');
    const newTask: RoadmapTask = {
      ...task,
      id: tempId
    };
    setRoadmapTasks(prev => [...prev, newTask]);
    apiClient.createTask(task).then(created => {
      if (created) {
        setRoadmapTasks(prev => prev.map(t => t.id === tempId ? created : t));
      }
    });
    addToast({
      title: 'Task added',
      message: 'Added to your personalized roadmap.',
      type: 'success'
    });
  };

  const deleteTask = (taskId: string) => {
    setRoadmapTasks(prev => prev.filter(t => t.id !== taskId));
    apiClient.deleteTask(taskId);
    addToast({
      title: 'Task removed',
      message: 'The item has been deleted from your roadmap.',
      type: 'info'
    });
  };

  const updateSkill = (skillId: string, updates: Partial<SkillProgress>) => {
    setSkills(prev =>
      prev.map(s => (s.id === skillId ? { ...s, ...updates } : s))
    );
    addToast({
      title: 'Skill progress updated',
      message: 'Updated practice time.',
      type: 'success'
    });
  };

  const addSkill = (skill: Omit<SkillProgress, 'id'>) => {
    const tempId = generateId('skill');
    const newSkill: SkillProgress = {
      ...skill,
      id: tempId
    };
    setSkills(prev => [...prev, newSkill]);
    apiClient.createSkill(skill).then(created => {
      if (created) {
        setSkills(prev => prev.map(s => s.id === tempId ? created : s));
      }
    });
    addToast({
      title: 'Skill added',
      message: 'Now tracking your learning progress.',
      type: 'success'
    });
  };

  const addChatMessage = (msg: ChatMessage) => {
    setChatMessages(prev => [...prev, msg]);
  };

  const updateChatMessage = (id: string, updates: Partial<ChatMessage>) => {
    setChatMessages(prev =>
      prev.map(m => (m.id === id ? { ...m, ...updates } : m))
    );
  };

  const clearChat = () => {
    setChatMessages([INITIAL_GREETING_MESSAGE]);
    apiClient.clearChatHistory();
    addToast({
      title: 'Conversation refreshed',
      message: 'Started a fresh coaching session.',
      type: 'info'
    });
  };

  const resetAllData = () => {
    localStorage.clear();
    setProfile(DEFAULT_PROFILE);
    setSavedCareerIds(['ai-product-engineer', 'product-designer']);
    setRoadmapTasks(INITIAL_ROADMAP_TASKS);
    setSkills(INITIAL_SKILLS);
    setChatMessages([INITIAL_GREETING_MESSAGE]);
    addToast({
      title: 'Data reset',
      message: 'Default sample data restored.',
      type: 'info'
    });
  };

  const addToast = (toast: Omit<Toast, 'id'>) => {
    const id = generateId('toast');
    const newToast: Toast = { ...toast, id };
    setToasts(prev => [...prev, newToast]);
    setTimeout(() => {
      removeToast(id);
    }, 4500);
  };

  const removeToast = (id: string) => {
    setToasts(prev => prev.filter(t => t.id !== id));
  };

  // Computations
  const completedTasksCount = useMemo(
    () => roadmapTasks.filter(t => t.status === 'completed').length,
    [roadmapTasks]
  );

  const totalTasksCount = roadmapTasks.length;

  const overallProgressPercent = useMemo(
    () => (totalTasksCount > 0 ? Math.round((completedTasksCount / totalTasksCount) * 100) : 0),
    [completedTasksCount, totalTasksCount]
  );

  const activeCareer = useMemo(
    () => INITIAL_CAREER_PATHS.find(c => c.id === profile.targetCareerId) || INITIAL_CAREER_PATHS[0],
    [profile.targetCareerId]
  );

  return (
    <AppContext.Provider
      value={{
        profile,
        updateProfile,
        resetAllData,
        careerPaths: INITIAL_CAREER_PATHS,
        savedCareerIds,
        toggleSaveCareer,
        isCareerSaved,
        roadmapTasks,
        updateTaskStatus,
        addTask,
        deleteTask,
        skills,
        updateSkill,
        addSkill,
        chatMessages,
        addChatMessage,
        updateChatMessage,
        clearChat,
        toasts,
        addToast,
        removeToast,
        completedTasksCount,
        totalTasksCount,
        overallProgressPercent,
        activeCareer,
        activeUserId,
        isLoggedIn,
        availableUsers,
        loginUser,
        logoutUser
      }}
    >
      {children}
    </AppContext.Provider>
  );
};

export const useApp = () => {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useApp must be used within an AppProvider');
  }
  return context;
};
