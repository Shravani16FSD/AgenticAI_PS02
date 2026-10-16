import type { UserProfile, CareerPath, RoadmapTask, SkillProgress, ChatMessage, TaskStatus } from '../types';

const API_BASE = '/api';

class ApiClient {
  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T | null> {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 6000); // 6s timeout

      const response = await fetch(`${API_BASE}${endpoint}`, {
        ...options,
        headers: {
          'Content-Type': 'application/json',
          ...(options.headers || {})
        },
        signal: controller.signal
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        return null;
      }

      return await response.json();
    } catch {
      // Return null on connection error, timeout, or offline
      return null;
    }
  }

  // Health
  public async checkHealth(): Promise<boolean> {
    const res = await this.request<{ status: string }>('/health');
    return res?.status === 'healthy';
  }

  // User Profile
  public async getProfile(): Promise<UserProfile | null> {
    const data = await this.request<any>('/profile');
    if (!data) return null;
    return {
      name: data.name,
      studyStatus: data.study_status,
      targetCareerId: data.target_career_id,
      interests: data.interests || [],
      currentSkills: data.current_skills || [],
      primaryGoal: data.primary_goal,
      weeklyHours: data.weekly_hours,
      onboardingCompleted: data.onboarding_completed
    };
  }

  public async updateProfile(profile: Partial<UserProfile>): Promise<UserProfile | null> {
    const payload: any = {};
    if (profile.name !== undefined) payload.name = profile.name;
    if (profile.studyStatus !== undefined) payload.study_status = profile.studyStatus;
    if (profile.targetCareerId !== undefined) payload.target_career_id = profile.targetCareerId;
    if (profile.interests !== undefined) payload.interests = profile.interests;
    if (profile.currentSkills !== undefined) payload.current_skills = profile.currentSkills;
    if (profile.primaryGoal !== undefined) payload.primary_goal = profile.primaryGoal;
    if (profile.weeklyHours !== undefined) payload.weekly_hours = profile.weeklyHours;
    if (profile.onboardingCompleted !== undefined) payload.onboarding_completed = profile.onboardingCompleted;

    const data = await this.request<any>('/profile', {
      method: 'PUT',
      body: JSON.stringify(payload)
    });

    if (!data) return null;
    return {
      name: data.name,
      studyStatus: data.study_status,
      targetCareerId: data.target_career_id,
      interests: data.interests || [],
      currentSkills: data.current_skills || [],
      primaryGoal: data.primary_goal,
      weeklyHours: data.weekly_hours,
      onboardingCompleted: data.onboarding_completed
    };
  }

  // Careers & Bookmarks
  public async getCareers(): Promise<CareerPath[] | null> {
    const data = await this.request<any[]>('/careers');
    if (!data) return null;
    return data.map(c => ({
      id: c.id,
      title: c.title,
      category: c.category,
      tagline: c.tagline,
      matchReason: c.match_reason,
      description: c.description,
      responsibilities: c.responsibilities,
      requiredSkills: c.required_skills,
      learningPhases: c.learning_phases,
      recommendedNextStep: c.recommended_next_step,
      entryPoints: c.entry_points
    }));
  }

  public async getSavedCareerIds(): Promise<string[] | null> {
    return await this.request<string[]>('/careers/saved');
  }

  public async saveCareer(careerId: string): Promise<boolean> {
    const res = await this.request(`/careers/${careerId}/save`, { method: 'POST' });
    return res !== null;
  }

  public async removeSavedCareer(careerId: string): Promise<boolean> {
    const res = await this.request(`/careers/${careerId}/save`, { method: 'DELETE' });
    return res !== null;
  }

  // Roadmap Tasks
  public async getRoadmap(): Promise<RoadmapTask[] | null> {
    const data = await this.request<any[]>('/roadmap');
    if (!data) return null;
    return data.map(t => ({
      id: t.id,
      phaseId: t.phase_id,
      phaseName: t.phase_name,
      title: t.title,
      description: t.description,
      skill: t.skill,
      estimatedTime: t.estimated_time,
      status: t.status as TaskStatus,
      resourceName: t.resource_name,
      resourceType: t.resource_type,
      resourceUrl: t.resource_url,
      notes: t.notes
    }));
  }

  public async createTask(task: Omit<RoadmapTask, 'id'>): Promise<RoadmapTask | null> {
    const payload = {
      phase_id: task.phaseId,
      phase_name: task.phaseName,
      title: task.title,
      description: task.description,
      skill: task.skill,
      estimated_time: task.estimatedTime,
      status: task.status,
      resource_name: task.resourceName,
      resource_type: task.resourceType,
      resource_url: task.resourceUrl,
      notes: task.notes
    };
    const t = await this.request<any>('/roadmap/tasks', {
      method: 'POST',
      body: JSON.stringify(payload)
    });
    if (!t) return null;
    return {
      id: t.id,
      phaseId: t.phase_id,
      phaseName: t.phase_name,
      title: t.title,
      description: t.description,
      skill: t.skill,
      estimatedTime: t.estimated_time,
      status: t.status as TaskStatus,
      resourceName: t.resource_name,
      resourceType: t.resource_type,
      resourceUrl: t.resource_url,
      notes: t.notes
    };
  }

  public async updateTask(taskId: string, updates: Partial<RoadmapTask>): Promise<boolean> {
    const payload: any = {};
    if (updates.status !== undefined) payload.status = updates.status;
    if (updates.title !== undefined) payload.title = updates.title;
    if (updates.description !== undefined) payload.description = updates.description;
    if (updates.notes !== undefined) payload.notes = updates.notes;

    const res = await this.request(`/roadmap/tasks/${taskId}`, {
      method: 'PATCH',
      body: JSON.stringify(payload)
    });
    return res !== null;
  }

  public async deleteTask(taskId: string): Promise<boolean> {
    const res = await this.request(`/roadmap/tasks/${taskId}`, { method: 'DELETE' });
    return res !== null;
  }

  // Skills
  public async getSkills(): Promise<SkillProgress[] | null> {
    const data = await this.request<any[]>('/skills');
    if (!data) return null;
    return data.map(s => ({
      id: s.id,
      name: s.name,
      category: s.category,
      status: s.status,
      hoursSpent: s.hours_spent,
      targetHours: s.target_hours,
      lastPracticed: s.last_practiced
    }));
  }

  public async createSkill(skill: Omit<SkillProgress, 'id'>): Promise<SkillProgress | null> {
    const payload = {
      name: skill.name,
      category: skill.category,
      status: skill.status,
      hours_spent: skill.hoursSpent,
      target_hours: skill.targetHours,
      last_practiced: skill.lastPracticed
    };
    const s = await this.request<any>('/skills', {
      method: 'POST',
      body: JSON.stringify(payload)
    });
    if (!s) return null;
    return {
      id: s.id,
      name: s.name,
      category: s.category,
      status: s.status,
      hoursSpent: s.hours_spent,
      targetHours: s.target_hours,
      lastPracticed: s.last_practiced
    };
  }

  public async logPractice(skillId: string, hours: number): Promise<SkillProgress | null> {
    const s = await this.request<any>(`/skills/${skillId}/log`, {
      method: 'POST',
      body: JSON.stringify({ hours })
    });
    if (!s) return null;
    return {
      id: s.id,
      name: s.name,
      category: s.category,
      status: s.status,
      hoursSpent: s.hours_spent,
      targetHours: s.target_hours,
      lastPracticed: s.last_practiced
    };
  }

  // Chat
  public async getChatHistory(): Promise<ChatMessage[] | null> {
    const data = await this.request<any[]>('/chat/history');
    if (!data) return null;
    return data.map(m => ({
      id: m.id,
      sender: m.sender,
      text: m.text,
      status: m.status,
      suggestedActions: m.suggested_actions || [],
      timestamp: new Date(m.timestamp).getTime()
    }));
  }

  public async clearChatHistory(): Promise<boolean> {
    const res = await this.request('/chat/history', { method: 'DELETE' });
    return res !== null;
  }
}

export const apiClient = new ApiClient();
