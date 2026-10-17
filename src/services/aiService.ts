import type { UserProfile, CareerPath, RoadmapTask, SkillProgress } from '../types';
import { API_BASE } from './apiClient';

export interface AIServiceContext {
  profile: UserProfile;
  activeCareer?: CareerPath;
  currentTasks: RoadmapTask[];
  skills: SkillProgress[];
  conversationHistory: { sender: 'user' | 'assistant'; text: string }[];
  sessionId?: string;
}

export interface StreamCallbacks {
  onStatusChange?: (status: string) => void;
  onChunk: (chunk: string) => void;
  onError: (error: Error) => void;
  onDone: (fullText: string, suggestedFollowUps?: string[]) => void;
}

/**
 * Service layer for AI Career Coach interactions.
 * Connects directly to the backend API (/api/chat) which is powered by Google Gemini.
 * Returns transparent, user-friendly errors when keys or servers are unavailable,
 * and never fabricates mock AI responses.
 */
export class AICoachService {
  private abortController: AbortController | null = null;
  private isProcessing = false;

  public cancelCurrentRequest(): void {
    if (this.abortController) {
      this.abortController.abort();
      this.abortController = null;
      this.isProcessing = false;
    }
  }

  public get isBusy(): boolean {
    return this.isProcessing;
  }

  public async sendMessage(
    userInput: string,
    context: AIServiceContext,
    callbacks: StreamCallbacks
  ): Promise<void> {
    const trimmedInput = userInput.trim();
    if (!trimmedInput) {
      callbacks.onError(new Error('Message cannot be empty or contain only whitespace.'));
      return;
    }

    if (this.isProcessing) {
      callbacks.onError(new Error('A response is currently in progress. Please wait for it to finish.'));
      return;
    }

    this.isProcessing = true;
    this.abortController = new AbortController();
    const signal = this.abortController.signal;

    try {
      callbacks.onStatusChange?.('Connecting with your career mentor…');

      const remoteEndpoint = (import.meta as any).env?.VITE_AI_API_ENDPOINT || `${API_BASE}/chat`;

      const timeoutId = setTimeout(() => {
        this.abortController?.abort();
      }, 45000); // 45s timeout for AI stream

      let response: Response;
      try {
        response = await fetch(remoteEndpoint, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            message: trimmedInput,
            session_id: context.sessionId || 'default_session',
            profile: context.profile,
            activeCareer: context.activeCareer?.title,
            history: context.conversationHistory.slice(-6)
          }),
          signal
        });
      } catch (fetchError: any) {
        clearTimeout(timeoutId);
        this.isProcessing = false;
        if (fetchError.name === 'AbortError') {
          callbacks.onError(new Error('Response generation was cancelled.'));
          return;
        }
        callbacks.onError(
          new Error('Unable to connect to the backend server. Please verify the backend service is running.')
        );
        return;
      }

      clearTimeout(timeoutId);

      if (!response.ok) {
        this.isProcessing = false;
        let errorMessage = `AI mentor service returned an error (${response.status}).`;
        try {
          const errData = await response.json();
          if (errData && errData.detail) {
            errorMessage = errData.detail;
          }
        } catch {
          const textErr = await response.text().catch(() => '');
          if (textErr) errorMessage = textErr;
        }
        callbacks.onError(new Error(errorMessage));
        return;
      }

      if (!response.body) {
        this.isProcessing = false;
        callbacks.onError(new Error('No response stream received from the server.'));
        return;
      }

      callbacks.onStatusChange?.('Putting your mentorship plan together…');
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let accumulated = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        const chunk = decoder.decode(value, { stream: true });
        accumulated += chunk;
        callbacks.onChunk(chunk);
      }

      this.isProcessing = false;
      callbacks.onDone(accumulated);
    } catch (err: any) {
      this.isProcessing = false;
      if (err.name === 'AbortError') {
        callbacks.onError(new Error('Response generation was cancelled.'));
      } else {
        callbacks.onError(
          new Error(err.message || 'An unexpected error occurred while communicating with your mentor.')
        );
      }
    }
  }
}

export const aiService = new AICoachService();
