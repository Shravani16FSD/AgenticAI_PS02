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
}

const STORAGE_KEYS = {
  PROFILE: 'chapter_user_profile',
  SAVED_CAREERS: 'chapter_saved_careers',
  ROADMAP: 'chapter_roadmap_tasks',
  SKILLS: 'chapter_skills',
  CHAT: 'chapter_chat_history',
};

const DEFAULT_PROFILE: UserProfile = {
  name: 'Alex Morgan',
  studyStatus: 'Third-year CS & HCI Student',
  targetCareerId: 'ai-product-engineer',
  interests: ['Human-Centered AI', 'Web Architecture', 'Design Systems', 'Interface Ergonomics'],
  currentSkills: ['TypeScript', 'React', 'Basic Python', 'Semantic HTML'],
  primaryGoal: 'Secure a Summer 2027 AI Product Engineering Internship',
  weeklyHours: 8,
  onboardingCompleted: true,
};

const INITIAL_GREETING_MESSAGE: ChatMessage = {
  id: 'msg-welcome',
  sender: 'assistant',
  text: `Hello Alex. I am your career mentor.

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

  // Load remote database state on startup if available
  useEffect(() => {
    let isMounted = true;
    const fetchRemoteData = async () => {
      const isLive = await apiClient.checkHealth();
      if (!isLive || !isMounted) return;

      const [remoteProfile, remoteSaved, remoteRoadmap, remoteSkills, remoteChat] = await Promise.all([
        apiClient.getProfile(),
        apiClient.getSavedCareerIds(),
        apiClient.getRoadmap(),
        apiClient.getSkills(),
        apiClient.getChatHistory()
      ]);

      if (!isMounted) return;
      if (remoteProfile) setProfile(remoteProfile);
      if (remoteSaved) setSavedCareerIds(remoteSaved);
      if (remoteRoadmap && remoteRoadmap.length > 0) setRoadmapTasks(remoteRoadmap);
      if (remoteSkills && remoteSkills.length > 0) setSkills(remoteSkills);
      if (remoteChat && remoteChat.length > 0) setChatMessages(remoteChat);
    };

    fetchRemoteData();
    return () => {
      isMounted = false;
    };
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
        activeCareer
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
