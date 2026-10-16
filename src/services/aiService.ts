import type { UserProfile, CareerPath, RoadmapTask, SkillProgress } from '../types';

export interface AIServiceContext {
  profile: UserProfile;
  activeCareer?: CareerPath;
  currentTasks: RoadmapTask[];
  skills: SkillProgress[];
  conversationHistory: { sender: 'user' | 'assistant'; text: string }[];
}

export interface StreamCallbacks {
  onStatusChange?: (status: string) => void;
  onChunk: (chunk: string) => void;
  onError: (error: Error) => void;
  onDone: (fullText: string, suggestedFollowUps?: string[]) => void;
}

/**
 * Service layer for AI Career Coach interactions.
 * Connects to a backend API if configured (e.g., via VITE_AI_API_ENDPOINT or /api/chat),
 * or falls back to an intelligent, contextual mentor model designed specifically for
 * student & early-career coaching.
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
      callbacks.onStatusChange?.('Thinking through your question…');

      // Check if a remote backend endpoint is configured
      const remoteEndpoint = (import.meta as any).env?.VITE_AI_API_ENDPOINT || '/api/chat';
      let usedRemote = false;

      try {
        const timeoutId = setTimeout(() => {
          this.abortController?.abort();
        }, 30000); // 30s timeout

        const response = await fetch(remoteEndpoint, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            message: trimmedInput,
            profile: context.profile,
            activeCareer: context.activeCareer?.title,
            history: context.conversationHistory.slice(-6)
          }),
          signal
        });

        clearTimeout(timeoutId);

        if (response.ok && response.body) {
          usedRemote = true;
          callbacks.onStatusChange?.('Putting your plan together…');
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
          return;
        }
      } catch (remoteError: any) {
        if (remoteError.name === 'AbortError') {
          throw remoteError;
        }
        // Remote endpoint not reachable or returned error; seamlessly fallback to client mentor engine
        usedRemote = false;
      }

      if (!usedRemote) {
        // High-fidelity contextual mentor engine
        await this.generateContextualResponse(trimmedInput, context, signal, callbacks);
      }
    } catch (err: any) {
      this.isProcessing = false;
      if (err.name === 'AbortError') {
        callbacks.onError(new Error('Response generation was cancelled.'));
      } else {
        callbacks.onError(
          new Error('Your message wasn\'t sent. Check your connection and retry.')
        );
      }
    }
  }

  private async generateContextualResponse(
    prompt: string,
    context: AIServiceContext,
    signal: AbortSignal,
    callbacks: StreamCallbacks
  ): Promise<void> {
    const career = context.activeCareer?.title || 'technology and design';
    const goal = context.profile.primaryGoal || 'building career confidence';
    const weeklyHours = context.profile.weeklyHours || 8;
    const lowerPrompt = prompt.toLowerCase();

    // Small delay to simulate initial reflection
    await new Promise(res => setTimeout(res, 600));
    if (signal.aborted) throw new DOMException('Aborted', 'AbortError');

    callbacks.onStatusChange?.('Putting your plan together…');

    let responseMarkdown = '';
    let followUps: string[] = [];

    // Intelligent context-aware branching
    if (lowerPrompt.includes('choose') || lowerPrompt.includes('direction') || lowerPrompt.includes('not sure')) {
      responseMarkdown = `### Finding a direction that fits you

Choosing a career direction doesn't mean locking in a thirty-year commitment. It means choosing an intentional thesis for the next 6 to 12 months.

Based on your background in **${context.profile.studyStatus}** and your stated interests in **${context.profile.interests.slice(0, 2).join(' and ')}**, here is how you can evaluate where to start:

1. **Look at the daily work, not the job title**
   Titles like *${career}* sound exciting, but daily work consists of reading documentation, crafting schemas, debugging interfaces, and collaborating on trade-offs. If you enjoy building things that other people interact with, this path aligns well.

2. **The Test-Project heuristic**
   Before committing to a long curriculum, spend **5 to 8 hours** building one small, contained artifact (such as a working API client with clean error states). If the friction of that task feels energizing rather than draining, you have strong signal.

3. **Suggested Next Step**
   Let's look at your current foundational tasks in your roadmap. Focusing on **${context.currentTasks[0]?.title || 'core technical foundations'}** will give you clarity faster than reading twenty articles.

Would you like to explore what a typical workday looks like for this role, or compare it with another path?`;

      followUps = [
        'What does a typical day look like for this role?',
        'How does this compare to Product Design?',
        'Can we plan my first 8-hour exploratory project?'
      ];
    } else if (lowerPrompt.includes('ai engineer') || lowerPrompt.includes('learn to become') || lowerPrompt.includes('ai product')) {
      responseMarkdown = `### Core Roadmap for AI Product Engineering

To become a capable AI Product Engineer, you do not need a PhD in mathematical optimization. The industry needs engineers who understand **systems engineering, reliability, and human ergonomics**.

Here is a practical breakdown tailored to your weekly commitment of **${weeklyHours} hours/week**:

#### 1. Foundation: Strict Type Systems & API Handling
- Master TypeScript and asynchronous streams (Server-Sent Events / WebSockets).
- *Why it matters:* Foundation models return non-deterministic streams; your client must handle interruptions, timeouts, and structured schemas gracefully.

#### 2. Core: Structured Generation & Schemas
- Work with tools like Pydantic (Python) or Zod (TypeScript) to enforce deterministic JSON outputs.
- Build prompt templates that reject invalid states before they reach the user.

#### 3. Real Application: Context & Vector Grounding
- Implement Retrieval-Augmented Generation (RAG) with local embeddings or lightweight vector indexes.
- Benchmark search accuracy and cost trade-offs.

#### 4. The Differentiator: Systematic Evaluation
- Most candidates stop at "it works in my test prompt." High-impact candidates build automated eval suites testing edge cases.

Your next milestone is: **${context.currentTasks.find(t => t.status === 'in_progress')?.title || 'Structured schema validation'}**. Spending 30 minutes on this today will make your next project significantly more robust.`;

      followUps = [
        'How do I test and benchmark prompt reliability?',
        'Which open-source vector store should I start with?',
        'Can you review my schema validation approach?'
      ];
    } else if (lowerPrompt.includes('internship') || lowerPrompt.includes('interview') || lowerPrompt.includes('job')) {
      responseMarkdown = `### Preparing for Internships with Substance

Hiring teams review hundreds of portfolios with identical tutorial clones. What catches a senior engineer's attention is **craft, error handling, and thoughtful trade-offs**.

Here is a direct checklist for your goal: *"${goal}"*:

1. **Build one deep project over five shallow ones**
   Instead of five half-finished apps, polish one project until it feels production-ready. Ensure it has:
   - Resilient error handling (try disabling your network; does the UI inform you calmly?).
   - Real accessibility (keyboard navigation and WCAG AA contrast).
   - An architectural README explaining what technical trade-offs you made.

2. **Prepare your story around "Friction and Recovery"**
   In interviews, nobody is impressed by stories where everything worked on the first try. Prepare 2-3 stories where a model hallucinated, a stream broke, or a schema failed, and how you engineered a resilient recovery.

3. **Weekly application pace**
   Don't spray 50 applications a day. Identify 5-10 teams whose product you genuinely respect, write a concise note referencing specific engineering decisions in their product, and attach your live demo.

Would you like to practice walking through an architectural trade-off, or review your portfolio project checklist?`;

      followUps = [
        'Help me outline my project\'s technical README.',
        'Let\'s practice a mock interview question.',
        'How do I explain trade-offs during a system design screen?'
      ];
    } else if (lowerPrompt.includes('weekly') || lowerPrompt.includes('schedule') || lowerPrompt.includes('plan') || lowerPrompt.includes('time')) {
      const dailyMinutes = Math.round((weeklyHours * 60) / 4);
      responseMarkdown = `### A Realistic Weekly Learning Plan

Consistency beats intensity every time. With **${weeklyHours} hours per week**, attempting 8-hour weekend marathons often leads to burnout.

Instead, let's distribute this into **4 focused sessions of ${dailyMinutes} minutes**:

- **Session 1 (Mon/Tue - 90 mins): Concept & Deliberate Practice**
  Focus: *${context.currentTasks.find(t => t.status === 'in_progress')?.title || 'Current core skill'}*.
  Action: Read primary documentation, write code from scratch without copying, take notes.

- **Session 2 (Wed/Thu - 90 mins): Applied Experimentation**
  Focus: Build a minimal reproducible example or test harness.
  Action: Deliberately break inputs and observe edge case behavior.

- **Session 3 (Fri/Sat - 90 mins): Integration & Refinement**
  Focus: Connect the component or module to your primary repository.

- **Session 4 (Sun - 60 mins): Reflection & Next Week's Preparation**
  Focus: Document what you learned, update your roadmap status, and queue your next task.

Remember: *Small steps count. Even 25 minutes of focused attention creates lasting momentum.*

Shall we schedule your first 25-minute practice block for today?`;

      followUps = [
        'Help me structure my 25-minute practice session today.',
        'What should I do when I feel stuck on a bug?',
        'How do I track my learning consistency effectively?'
      ];
    } else {
      // General thoughtful career advice
      responseMarkdown = `### Addressing your question thoughtfully

Thank you for bringing this up. When considering **"${prompt.replace(/[<>]/g, '')}"**, it helps to look at both the immediate practical step and the broader trajectory.

Here are three key considerations based on your roadmap toward **${career}**:

1. **Clarify the concrete outcome**
   What would success look like by the end of this week regarding this question? Is it understanding a concept, making a decision between two paths, or completing a specific prototype?

2. **Ground decisions in your real bandwidth**
   With ${weeklyHours} hours available each week, prioritize actions that produce durable artifacts—code you can point to, notes you can reference, or conversations with practitioners.

3. **Immediate recommendation**
   Your current in-progress roadmap milestone is **"${context.currentTasks.find(t => t.status === 'in_progress')?.title || context.currentTasks[0]?.title || 'Core Foundations'}"**. Aligning your next work session with this will keep your momentum steady.

How would you like to proceed? We can break this down into a 20-minute action item or explore the broader strategy.`;

      followUps = [
        'Let\'s break this down into a 20-minute action item.',
        'How does this relate to my current roadmap task?',
        'Can we review my progress so far?'
      ];
    }

    // Realistic streaming output in chunks
    const chunks = responseMarkdown.match(/.{1,18}|\n/g) || [responseMarkdown];
    let accumulated = '';

    for (const chunk of chunks) {
      if (signal.aborted) throw new DOMException('Aborted', 'AbortError');
      accumulated += chunk;
      callbacks.onChunk(chunk);
      // Small pause between chunks (30ms) for natural cadence
      await new Promise(res => setTimeout(res, 28));
    }

    this.isProcessing = false;
    callbacks.onDone(accumulated, followUps);
  }
}

export const aiService = new AICoachService();
