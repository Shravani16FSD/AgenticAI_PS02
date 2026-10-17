import type { UserProfile, CareerPath, RoadmapTask, SkillProgress, ChatMessage, TaskStatus } from '../types';

const API_BASE = '/api';

class ApiClient {
  private token: string | null = null;
  private currentUserId: string | null = null;

  constructor() {
    try {
      this.token = localStorage.getItem('chapter_auth_token');
      this.currentUserId = localStorage.getItem('chapter_session_user');
    } catch {
      // ignore
    }
  }

  public setSession(token: string | null, userId: string | null) {
    this.token = token;
    this.currentUserId = userId;
    try {
      if (token) localStorage.setItem('chapter_auth_token', token);
      else localStorage.removeItem('chapter_auth_token');

      if (userId) localStorage.setItem('chapter_session_user', userId);
      else localStorage.removeItem('chapter_session_user');
    } catch {
      // ignore
    }
  }

  public getActiveUserId(): string | null {
    return this.currentUserId;
  }

  public getActiveToken(): string | null {
    return this.token;
  }

  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T | null> {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 6000); // 6s timeout

      const headers: Record<string, string> = {
        'Content-Type': 'application/json',
        ...(options.headers as Record<string, string> || {})
      };

      if (this.token) {
        headers['Authorization'] = `Bearer ${this.token}`;
      }
      if (this.currentUserId) {
        headers['X-User-ID'] = this.currentUserId;
      }

      let url = `${API_BASE}${endpoint}`;
      if (this.currentUserId && !url.includes('user_id=') && !endpoint.startsWith('/auth/')) {
        const delimiter = url.includes('?') ? '&' : '?';
        url = `${url}${delimiter}user_id=${encodeURIComponent(this.currentUserId)}`;
      }

      const response = await fetch(url, {
        ...options,
        credentials: 'include',
        headers,
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

  // Career Explorer & ML Matching
  public async getNaukriJobs(keywords: string, location: string, experience: string, isInternship: boolean): Promise<any | null> {
    const params = new URLSearchParams();
    if (keywords) params.set('keywords', keywords);
    if (location && location !== 'All') params.set('location', location);
    if (experience && experience !== 'Any Experience') params.set('experience', experience);
    if (isInternship) params.set('is_internship', 'true');
    return await this.request(`/careers/naukri?${params.toString()}`);
  }

  public async matchJobsWithML(payload: {
    target_role: string;
    summary: string;
    current_skills: string[];
    experience_years: number;
    preferred_work_modes: string[];
    preferred_locations: string[];
    candidate_evidence?: any[];
    sort_by?: string;
  }): Promise<any | null> {
    return await this.request('/careers/match', {
      method: 'POST',
      body: JSON.stringify(payload)
    });
  }

  public async getJobSkillGap(payload: {
    job_id: string;
    candidate_skills: string[];
    candidate_evidence?: any[];
  }): Promise<any | null> {
    return await this.request('/careers/skill-gap', {
      method: 'POST',
      body: JSON.stringify(payload)
    });
  }

  public async createJobRoadmap(payload: {
    job_id: string;
    candidate_skills: string[];
    candidate_evidence?: any[];
  }): Promise<any | null> {
    return await this.request('/careers/roadmap', {
      method: 'POST',
      body: JSON.stringify(payload)
    });
  }

  public async submitJobApplication(payload: {
    job_id: string;
    applicant_name: string;
    applicant_email: string;
    applicant_github: string;
    applicant_pitch?: string;
  }): Promise<any | null> {
    return await this.request('/careers/apply', {
      method: 'POST',
      body: JSON.stringify(payload)
    });
  }

  public async getJobApplications(): Promise<any[] | null> {
    return await this.request('/careers/applications');
  }

  // Repository Skill Profile & Continuous Reassessment
  public async getRepositorySkillProfile(userId?: string): Promise<any | null> {
    const uid = userId || this.currentUserId;
    const url = uid ? `/skills/repository-profile?user_id=${encodeURIComponent(uid)}` : '/skills/repository-profile';
    return await this.request(url);
  }

  public async reanalyseRepository(userId?: string): Promise<any | null> {
    const uid = userId || this.currentUserId;
    const url = uid ? `/skills/reanalyse?user_id=${encodeURIComponent(uid)}` : '/skills/reanalyse';
    return await this.request(url, { method: 'POST' });
  }

  // Authentication & Session Management
  public async getAvailableUsers(): Promise<Array<{ id: string; name: string; target_career_id: string; study_status: string; primary_goal: string }> | null> {
    return await this.request('/auth/users');
  }

  public async login(userId: string): Promise<{ token: string; user: any; message: string } | null> {
    const data = await this.request<{ token: string; user: any; message: string }>('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ user_id: userId })
    });
    if (data && data.token && data.user) {
      this.setSession(data.token, data.user.id);
    }
    return data;
  }

  public async logout(): Promise<boolean> {
    await this.request('/auth/logout', { method: 'POST' });
    this.setSession(null, null);
    return true;
  }

  public async getMe(): Promise<any | null> {
    return await this.request('/auth/me');
  }
}

export const apiClient = new ApiClient();

// Expose safe helper on window for developer testing
if (typeof window !== 'undefined') {
  (window as any).auth = {
    login: (userId: string) => apiClient.login(userId),
    logout: () => apiClient.logout(),
    getUsers: () => apiClient.getAvailableUsers(),
    getMe: () => apiClient.getMe(),
    getActiveUserId: () => apiClient.getActiveUserId()
  };
}
