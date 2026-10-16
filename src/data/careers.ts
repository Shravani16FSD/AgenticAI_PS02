import type { CareerPath, RoadmapTask, SkillProgress } from '../types';

export const INITIAL_CAREER_PATHS: CareerPath[] = [
  {
    id: 'ai-product-engineer',
    title: 'AI Product Engineer',
    category: 'Engineering',
    tagline: 'Bridging modern foundation models with production user interfaces and resilient client-server workflows.',
    matchReason: 'Combines your curiosity about machine learning with practical frontend and backend development skills.',
    description: 'AI Product Engineers build user-facing software powered by Large Language Models and multimodal systems. Rather than training models from scratch, they specialize in prompt architectures, evaluation harnesses, structured streaming, retrieval-augmented generation (RAG), and human-in-the-loop interfaces.',
    responsibilities: [
      'Architect full-stack web applications integrating LLM APIs and vector retrieval layers.',
      'Design graceful fallbacks, structured output validation, and streaming UI states for AI interactions.',
      'Build automated evaluation pipelines to benchmark prompt changes against quality and latency criteria.',
      'Collaborate with designers to create intuitive, transparent AI experiences that build user trust.'
    ],
    requiredSkills: [
      { name: 'TypeScript & React', importance: 'Essential', category: 'Frontend' },
      { name: 'Python Fundamentals', importance: 'Essential', category: 'Backend' },
      { name: 'API Design & Streaming', importance: 'Core', category: 'System Architecture' },
      { name: 'Prompt & Context Engineering', importance: 'Core', category: 'AI Architecture' },
      { name: 'Vector Embeddings & RAG', importance: 'Valuable', category: 'Information Retrieval' },
      { name: 'Evaluation & Testing', importance: 'Valuable', category: 'Reliability' }
    ],
    learningPhases: [
      { phase: '1. Foundations', focus: 'Modern TypeScript, asynchronous programming, and basic Python scripting.', estimatedMonths: '1-2 months' },
      { phase: '2. Core Skills', focus: 'API integrations, streaming protocols (SSE/WebSockets), and vector databases.', estimatedMonths: '2-3 months' },
      { phase: '3. Applied Projects', focus: 'End-to-end RAG application with evaluation suite and fallback UX.', estimatedMonths: '1-2 months' },
      { phase: '4. Portfolio & Systems', focus: 'Open-source contributions, public demo deployment, and latency optimization.', estimatedMonths: '1 month' },
      { phase: '5. Interview Readiness', focus: 'System design for AI applications, behavioral stories, and coding exercises.', estimatedMonths: '1 month' }
    ],
    recommendedNextStep: {
      title: 'Spend 25 minutes practicing Python fundamentals & structured outputs',
      whyItMatters: 'Understanding JSON schema validation and pydantic models is the cornerstone of reliable agentic integrations.',
      duration: '25 mins',
      resourceName: 'Official Python Documentation & Pydantic Guide',
      resourceUrl: 'https://docs.pydantic.dev/latest/'
    },
    entryPoints: [
      'Junior Full-Stack Developer transitioning into AI-powered tools.',
      'Computer Science graduate with personal projects in LLM interfaces.',
      'Frontend developer broadening into backend API orchestration.'
    ]
  },
  {
    id: 'product-designer',
    title: 'Product & Design Systems Specialist',
    category: 'Design & UX',
    tagline: 'Crafting thoughtful digital typography, accessible interaction models, and reusable component architectures.',
    matchReason: 'Aligns with your eye for detail, typographic taste, and passion for inclusive user experiences.',
    description: 'Product Designers design human-centered interfaces from early discovery and wireframing through to high-fidelity design systems. They partner closely with engineers to ensure accessibility (WCAG AA/AAA), consistency, and effortless interactions.',
    responsibilities: [
      'Design accessible, responsive web interfaces grounded in editorial typography and token-driven design systems.',
      'Conduct user interviews, synthesize feedback, and validate prototypes with real users.',
      'Maintain component libraries in Figma and author documentation for engineering handoff.',
      'Audit interfaces for color contrast, keyboard navigation, and cognitive clarity.'
    ],
    requiredSkills: [
      { name: 'Figma & Component Architecture', importance: 'Essential', category: 'Design Tools' },
      { name: 'Design Tokens & CSS', importance: 'Essential', category: 'Frontend' },
      { name: 'WCAG 2.2 Accessibility', importance: 'Core', category: 'UX Standards' },
      { name: 'Information Hierarchy', importance: 'Core', category: 'Visual Design' },
      { name: 'Usability Testing & Research', importance: 'Valuable', category: 'Research' }
    ],
    learningPhases: [
      { phase: '1. Foundations', focus: 'Grid systems, typography scales, optical balance, and WCAG contrast rules.', estimatedMonths: '1-2 months' },
      { phase: '2. Core Skills', focus: 'Token-based design systems, auto-layout, interactive prototyping.', estimatedMonths: '2 months' },
      { phase: '3. Applied Projects', focus: 'Complete case study: redesigning a complex utility into a calm editorial experience.', estimatedMonths: '2 months' },
      { phase: '4. Portfolio & Review', focus: 'Publishing two in-depth case studies with process and accessibility audits.', estimatedMonths: '1 month' },
      { phase: '5. Interview Readiness', focus: 'Whiteboard design challenges, portfolio walkthroughs, and rationale defense.', estimatedMonths: '1 month' }
    ],
    recommendedNextStep: {
      title: 'Audit a component for WCAG 2.2 AA contrast and focus states',
      whyItMatters: 'Editorial aesthetics require rigorous accessible foundation to ensure all readers can participate comfortably.',
      duration: '30 mins',
      resourceName: 'Web Accessibility Initiative (W3C WAI)',
      resourceUrl: 'https://www.w3.org/WAI/fundamentals/accessibility-intro/'
    },
    entryPoints: [
      'Visual designer expanding into digital product ergonomics.',
      'Frontend engineer who enjoys design tokens and UI architecture.',
      'Self-taught designer building a dedicated case-study portfolio.'
    ]
  },
  {
    id: 'data-systems-analyst',
    title: 'Data Systems & Analytics Engineer',
    category: 'Data & AI',
    tagline: 'Transforming messy business events into clean semantic models, trustworthy data pipelines, and clear decisions.',
    matchReason: 'Suited for structured thinkers who enjoy analytical problem solving and data reliability.',
    description: 'Analytics Engineers sit between data engineers and decision-makers. They write performant SQL, build dbt models, manage version-controlled transformation pipelines, and create clear semantic metrics that the entire organization can rely upon.',
    responsibilities: [
      'Model dimension and fact tables in modern cloud data warehouses (BigQuery, Snowflake).',
      'Author automated data tests, documentation, and lineage graphs using dbt or SQLX.',
      'Optimize query performance and partition schemas for cost efficiency.',
      'Build dashboards with transparent data definitions that prevent misinterpretation.'
    ],
    requiredSkills: [
      { name: 'Advanced SQL & Window Functions', importance: 'Essential', category: 'Data Analysis' },
      { name: 'Data Modeling (Kimball/Dimensional)', importance: 'Essential', category: 'Architecture' },
      { name: 'dbt (Data Build Tool)', importance: 'Core', category: 'Engineering' },
      { name: 'Python for Data Automation', importance: 'Core', category: 'Scripting' },
      { name: 'Data Quality & Testing', importance: 'Valuable', category: 'Reliability' }
    ],
    learningPhases: [
      { phase: '1. Foundations', focus: 'SQL mastery, aggregations, window functions, and relational schema principles.', estimatedMonths: '1-2 months' },
      { phase: '2. Core Skills', focus: 'Dimensional modeling, staging vs mart layers, and git-based workflows.', estimatedMonths: '2 months' },
      { phase: '3. Applied Projects', focus: 'Build a production dbt pipeline on a public dataset with 100% test coverage.', estimatedMonths: '1-2 months' },
      { phase: '4. Portfolio', focus: 'Document data model architecture, pipeline cost analysis, and reproducible demo.', estimatedMonths: '1 month' },
      { phase: '5. Interview Prep', focus: 'SQL live coding, scenario-based data modeling, and business logic explanation.', estimatedMonths: '1 month' }
    ],
    recommendedNextStep: {
      title: 'Write three analytical window queries on sample data',
      whyItMatters: 'Window functions like LEAD, LAG, and ROW_NUMBER unlock deep cohort and retention analytics.',
      duration: '35 mins',
      resourceName: 'PostgreSQL Window Function Documentation',
      resourceUrl: 'https://www.postgresql.org/docs/current/tutorial-window.html'
    },
    entryPoints: [
      'Business analyst transitioning into software-engineered data stacks.',
      'Math or economics graduate with quantitative programming interest.',
      'Junior backend engineer interested in data modeling and warehousing.'
    ]
  },
  {
    id: 'frontend-architect',
    title: 'Frontend Architect & Web Platform Engineer',
    category: 'Engineering',
    tagline: 'Engineering fast, resilient, accessible web applications with modern modular architectures.',
    matchReason: 'Ideal for engineers who value software craftsmanship, performance optimization, and delightful developer experience.',
    description: 'Frontend Architects oversee client-side application architecture, state synchronization, bundle optimization, Core Web Vitals (LCP, INP, CLS), and component systems. They build scalable foundations that make team members productive and users happy.',
    responsibilities: [
      'Design clean component interfaces, state machines, and API data-fetching strategies.',
      'Measure and improve Core Web Vitals, runtime rendering performance, and bundle footprints.',
      'Establish testing standards across unit, component, and end-to-end user journeys.',
      'Ensure uncompromising cross-browser compatibility and keyboard accessibility.'
    ],
    requiredSkills: [
      { name: 'TypeScript & Modern React', importance: 'Essential', category: 'Frontend' },
      { name: 'Browser Internals & Performance', importance: 'Essential', category: 'Platform' },
      { name: 'State Management & Caching', importance: 'Core', category: 'Architecture' },
      { name: 'Testing (Vitest, Testing Library)', importance: 'Core', category: 'Quality' },
      { name: 'Accessibility & Semantic HTML', importance: 'Core', category: 'UX Standards' }
    ],
    learningPhases: [
      { phase: '1. Foundations', focus: 'Deep dive into JavaScript event loop, DOM rendering tree, and strict TypeScript.', estimatedMonths: '1-2 months' },
      { phase: '2. Core Skills', focus: 'Component lifecycle, memory leak prevention, server-rendering patterns.', estimatedMonths: '2 months' },
      { phase: '3. Applied Projects', focus: 'Build an offline-capable, responsive application with high performance marks.', estimatedMonths: '2 months' },
      { phase: '4. Portfolio & Systems', focus: 'Open-source component library with comprehensive test suite and docs.', estimatedMonths: '1 month' },
      { phase: '5. Interview Prep', focus: 'Frontend system design (feed, collaborative editor, state architecture).', estimatedMonths: '1 month' }
    ],
    recommendedNextStep: {
      title: 'Analyze network waterfall and bundle composition in DevTools',
      whyItMatters: 'Finding bottlenecks early creates instantaneous, low-friction digital products.',
      duration: '20 mins',
      resourceName: 'Web.dev Core Web Vitals Guide',
      resourceUrl: 'https://web.dev/vitals/'
    },
    entryPoints: [
      'Self-taught web developer seeking deeper architectural rigor.',
      'Full-stack engineer focusing on high-polish client applications.'
    ]
  }
];

export const INITIAL_ROADMAP_TASKS: RoadmapTask[] = [
  {
    id: 'task-1',
    phaseId: 1,
    phaseName: 'Phase 1: Foundations',
    title: 'Master modern TypeScript fundamentals & strict type safety',
    description: 'Understand union types, generics, type narrowing, and interface composition to prevent runtime bugs.',
    skill: 'TypeScript',
    estimatedTime: '4 hours',
    status: 'completed',
    resourceName: 'TypeScript Handbook',
    resourceType: 'Documentation',
    resourceUrl: 'https://www.typescriptlang.org/docs/handbook/intro.html',
    notes: 'Completed basic generics and discriminated unions exercises.'
  },
  {
    id: 'task-2',
    phaseId: 1,
    phaseName: 'Phase 1: Foundations',
    title: 'Study asynchronous JavaScript & Server-Sent Events (SSE)',
    description: 'Learn how streaming responses work from server to client with ReadableStream and fetch abort controllers.',
    skill: 'Asynchronous Programming',
    estimatedTime: '3 hours',
    status: 'completed',
    resourceName: 'MDN Web Docs: Streams API',
    resourceType: 'Documentation',
    resourceUrl: 'https://developer.mozilla.org/en-US/docs/Web/API/Streams_API',
    notes: 'Built a small reader prototype that handles chunked text streams.'
  },
  {
    id: 'task-3',
    phaseId: 2,
    phaseName: 'Phase 2: Core Skills',
    title: 'Implement structured schema validation with Pydantic & Zod',
    description: 'Enforce deterministic schemas on model outputs to guarantee reliable UI rendering without runtime parsing errors.',
    skill: 'Schema Validation',
    estimatedTime: '25 mins',
    status: 'in_progress',
    resourceName: 'Zod TypeScript First Schema Validation',
    resourceType: 'Documentation',
    resourceUrl: 'https://zod.dev',
    notes: 'Currently working through parsing JSON response chunks into strongly typed objects.'
  },
  {
    id: 'task-4',
    phaseId: 2,
    phaseName: 'Phase 2: Core Skills',
    title: 'Build graceful UI fallback states for AI rate limits & network timeouts',
    description: 'Design human-friendly error banners, retry mechanisms, and non-blocking background task indicators.',
    skill: 'Resilient UX',
    estimatedTime: '2 hours',
    status: 'not_started',
    resourceName: 'Designing for System Recovery & Error States',
    resourceType: 'Interactive',
    resourceUrl: 'https://www.nngroup.com/articles/error-message-guidelines/'
  },
  {
    id: 'task-5',
    phaseId: 3,
    phaseName: 'Phase 3: Applied Projects',
    title: 'Develop an end-to-end Career Research Companion with vector search',
    description: 'Combine a clean editorial frontend with a semantic embedding index of job roles, skills, and open-access courses.',
    skill: 'Full-Stack AI Application',
    estimatedTime: '12 hours',
    status: 'not_started',
    resourceName: 'Project Specification & Architecture Guide',
    resourceType: 'Project Spec',
    resourceUrl: 'https://github.com'
  },
  {
    id: 'task-6',
    phaseId: 4,
    phaseName: 'Phase 4: Portfolio & Practical Experience',
    title: 'Write a technical reflection case study documenting trade-offs',
    description: 'Articulate why you chose specific data structures, streaming protocols, and accessibility considerations in a public write-up.',
    skill: 'Technical Writing & Communication',
    estimatedTime: '4 hours',
    status: 'not_started',
    resourceName: 'StaffEng: Writing Clear Engineering Design Docs',
    resourceType: 'Course',
    resourceUrl: 'https://staffeng.com/guides/engineering-strategy'
  },
  {
    id: 'task-7',
    phaseId: 5,
    phaseName: 'Phase 5: Internship & Job Preparation',
    title: 'Mock interview: explain system architecture & prompt evaluation criteria',
    description: 'Practice walking through system boundaries, latency trade-offs, and how you evaluate AI reliability before shipping.',
    skill: 'System Design & Communication',
    estimatedTime: '3 hours',
    status: 'not_started',
    resourceName: 'System Design Primer',
    resourceType: 'Documentation',
    resourceUrl: 'https://github.com/donnemartin/system-design-primer'
  }
];

export const INITIAL_SKILLS: SkillProgress[] = [
  {
    id: 'skill-ts',
    name: 'TypeScript & React',
    category: 'Frontend Engineering',
    status: 'practicing',
    hoursSpent: 28,
    targetHours: 50,
    lastPracticed: 'Today'
  },
  {
    id: 'skill-py',
    name: 'Python Fundamentals',
    category: 'Backend & Scripting',
    status: 'practicing',
    hoursSpent: 16,
    targetHours: 40,
    lastPracticed: 'Yesterday'
  },
  {
    id: 'skill-api',
    name: 'API Design & Streaming',
    category: 'System Architecture',
    status: 'learning',
    hoursSpent: 8,
    targetHours: 30,
    lastPracticed: '3 days ago'
  },
  {
    id: 'skill-a11y',
    name: 'WCAG 2.2 Accessibility',
    category: 'Design & UX Standards',
    status: 'proficient',
    hoursSpent: 22,
    targetHours: 25,
    lastPracticed: '4 days ago'
  },
  {
    id: 'skill-prompt',
    name: 'Context & Prompt Architecture',
    category: 'AI Systems',
    status: 'learning',
    hoursSpent: 10,
    targetHours: 35,
    lastPracticed: '1 week ago'
  }
];
