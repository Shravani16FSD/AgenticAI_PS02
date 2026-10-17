from sqlalchemy.orm import Session
from datetime import datetime
from .database import engine, Base, SessionLocal, migrate_database
from .models import (
    UserProfile, CareerPath, SavedCareer, RoadmapTask, UserSkill,
    ChatMessage, GitHubAccount, GitHubRepository, SkillAssessment,
    AssessmentSkillResult, RepositoryEvidence
)

def seed_database(db: Session):
    # Ensure tables and migrations exist safely
    migrate_database()

    # -------------------------------------------------------------
    # 1. Seed Career Paths (Idempotent)
    # -------------------------------------------------------------
    careers = [
        CareerPath(
            id="ai-product-engineer",
            title="AI Product Engineer",
            category="Engineering",
            tagline="Bridging modern foundation models with production user interfaces and resilient client-server workflows.",
            match_reason="Combines your curiosity about machine learning with practical frontend and backend development skills.",
            description="AI Product Engineers build user-facing software powered by Large Language Models and multimodal systems. Rather than training models from scratch, they specialize in prompt architectures, evaluation harnesses, structured streaming, retrieval-augmented generation (RAG), and human-in-the-loop interfaces.",
            responsibilities=[
                "Architect full-stack web applications integrating LLM APIs and vector retrieval layers.",
                "Design graceful fallbacks, structured output validation, and streaming UI states for AI interactions.",
                "Build automated evaluation pipelines to benchmark prompt changes against quality and latency criteria.",
                "Collaborate with designers to create intuitive, transparent AI experiences that build user trust."
            ],
            required_skills=[
                {"name": "TypeScript & React", "importance": "Essential", "category": "Frontend"},
                {"name": "Python Fundamentals", "importance": "Essential", "category": "Backend"},
                {"name": "API Design & Streaming", "importance": "Core", "category": "System Architecture"},
                {"name": "Prompt & Context Engineering", "importance": "Core", "category": "AI Architecture"},
                {"name": "Vector Embeddings & RAG", "importance": "Valuable", "category": "Information Retrieval"},
                {"name": "Evaluation & Testing", "importance": "Valuable", "category": "Reliability"}
            ],
            learning_phases=[
                {"phase": "1. Foundations", "focus": "Modern TypeScript, asynchronous programming, and basic Python scripting.", "estimatedMonths": "1-2 months"},
                {"phase": "2. Core Skills", "focus": "API integrations, streaming protocols (SSE/WebSockets), and vector databases.", "estimatedMonths": "2-3 months"},
                {"phase": "3. Applied Projects", "focus": "End-to-end RAG application with evaluation suite and fallback UX.", "estimatedMonths": "1-2 months"},
                {"phase": "4. Portfolio & Systems", "focus": "Open-source contributions, public demo deployment, and latency optimization.", "estimatedMonths": "1 month"},
                {"phase": "5. Interview Readiness", "focus": "System design for AI applications, behavioral stories, and coding exercises.", "estimatedMonths": "1 month"}
            ],
            recommended_next_step={
                "title": "Spend 25 minutes practicing Python fundamentals & structured outputs",
                "whyItMatters": "Understanding JSON schema validation and pydantic models is the cornerstone of reliable agentic integrations.",
                "duration": "25 mins",
                "resourceName": "Official Python Documentation & Pydantic Guide",
                "resourceUrl": "https://docs.pydantic.dev/latest/"
            },
            entry_points=[
                "Junior Full-Stack Developer transitioning into AI-powered tools.",
                "Computer Science graduate with personal projects in LLM interfaces.",
                "Frontend developer broadening into backend API orchestration."
            ]
        ),
        CareerPath(
            id="product-designer",
            title="Product & Design Systems Specialist",
            category="Design & UX",
            tagline="Crafting thoughtful digital typography, accessible interaction models, and reusable component architectures.",
            match_reason="Aligns with your eye for detail, typographic taste, and passion for inclusive user experiences.",
            description="Product Designers design human-centered interfaces from early discovery and wireframing through to high-fidelity design systems. They partner closely with engineers to ensure accessibility (WCAG AA/AAA), consistency, and effortless interactions.",
            responsibilities=[
                "Design accessible, responsive web interfaces grounded in editorial typography and token-driven design systems.",
                "Conduct user interviews, synthesize feedback, and validate prototypes with real users.",
                "Maintain component libraries in Figma and author documentation for engineering handoff.",
                "Audit interfaces for color contrast, keyboard navigation, and cognitive clarity."
            ],
            required_skills=[
                {"name": "Figma & Component Architecture", "importance": "Essential", "category": "Design Tools"},
                {"name": "Design Tokens & CSS", "importance": "Essential", "category": "Frontend"},
                {"name": "WCAG 2.2 Accessibility", "importance": "Core", "category": "UX Standards"},
                {"name": "Information Hierarchy", "importance": "Core", "category": "Visual Design"},
                {"name": "Usability Testing & Research", "importance": "Valuable", "category": "Research"}
            ],
            learning_phases=[
                {"phase": "1. Foundations", "focus": "Grid systems, typography scales, optical balance, and WCAG contrast rules.", "estimatedMonths": "1-2 months"},
                {"phase": "2. Core Skills", "focus": "Token-based design systems, auto-layout, interactive prototyping.", "estimatedMonths": "2 months"},
                {"phase": "3. Applied Projects", "focus": "Complete case study: redesigning a complex utility into a calm editorial experience.", "estimatedMonths": "2 months"},
                {"phase": "4. Portfolio & Review", "focus": "Publishing two in-depth case studies with process and accessibility audits.", "estimatedMonths": "1 month"},
                {"phase": "5. Interview Readiness", "focus": "Whiteboard design challenges, portfolio walkthroughs, and rationale defense.", "estimatedMonths": "1 month"}
            ],
            recommended_next_step={
                "title": "Audit a component for WCAG 2.2 AA contrast and focus states",
                "whyItMatters": "Editorial aesthetics require rigorous accessible foundation to ensure all readers can participate comfortably.",
                "duration": "30 mins",
                "resourceName": "Web Accessibility Initiative (W3C WAI)",
                "resourceUrl": "https://www.w3.org/WAI/fundamentals/accessibility-intro/"
            },
            entry_points=[
                "Visual designer expanding into digital product ergonomics.",
                "Frontend engineer who enjoys design tokens and UI architecture.",
                "Self-taught designer building a dedicated case-study portfolio."
            ]
        ),
        CareerPath(
            id="data-systems-analyst",
            title="Data Systems & Analytics Engineer",
            category="Data & AI",
            tagline="Transforming messy business events into clean semantic models, trustworthy data pipelines, and clear decisions.",
            match_reason="Suited for structured thinkers who enjoy analytical problem solving and data reliability.",
            description="Analytics Engineers sit between data engineers and decision-makers. They write performant SQL, build dbt models, manage version-controlled transformation pipelines, and create clear semantic metrics that the entire organization can rely upon.",
            responsibilities=[
                "Model dimension and fact tables in modern cloud data warehouses (BigQuery, Snowflake).",
                "Author automated data tests, documentation, and lineage graphs using dbt or SQLX.",
                "Optimize query performance and partition schemas for cost efficiency.",
                "Build dashboards with transparent data definitions that prevent misinterpretation."
            ],
            required_skills=[
                {"name": "Advanced SQL & Window Functions", "importance": "Essential", "category": "Data Analysis"},
                {"name": "Data Modeling (Kimball/Dimensional)", "importance": "Essential", "category": "Architecture"},
                {"name": "dbt (Data Build Tool)", "importance": "Core", "category": "Engineering"},
                {"name": "Python for Data Automation", "importance": "Core", "category": "Scripting"},
                {"name": "Data Quality & Testing", "importance": "Valuable", "category": "Reliability"}
            ],
            learning_phases=[
                {"phase": "1. Foundations", "focus": "SQL mastery, aggregations, window functions, and relational schema principles.", "estimatedMonths": "1-2 months"},
                {"phase": "2. Core Skills", "focus": "Dimensional modeling, staging vs mart layers, and git-based workflows.", "estimatedMonths": "2 months"},
                {"phase": "3. Applied Projects", "focus": "Build a production dbt pipeline on a public dataset with 100% test coverage.", "estimatedMonths": "1-2 months"},
                {"phase": "4. Portfolio", "focus": "Document data model architecture, pipeline cost analysis, and reproducible demo.", "estimatedMonths": "1 month"},
                {"phase": "5. Interview Prep", "focus": "SQL live coding, scenario-based data modeling, and business logic explanation.", "estimatedMonths": "1 month"}
            ],
            recommended_next_step={
                "title": "Write three analytical window queries on sample data",
                "whyItMatters": "Window functions like LEAD, LAG, and ROW_NUMBER unlock deep cohort and retention analytics.",
                "duration": "35 mins",
                "resourceName": "PostgreSQL Window Function Documentation",
                "resourceUrl": "https://www.postgresql.org/docs/current/tutorial-window.html"
            },
            entry_points=[
                "Business analyst transitioning into software-engineered data stacks.",
                "Math or economics graduate with quantitative programming interest.",
                "Junior backend engineer interested in data modeling and warehousing."
            ]
        ),
        CareerPath(
            id="frontend-architect",
            title="Frontend Architect & Web Platform Engineer",
            category="Engineering",
            tagline="Engineering fast, resilient, accessible web applications with modern modular architectures.",
            match_reason="Ideal for engineers who value software craftsmanship, performance optimization, and delightful developer experience.",
            description="Frontend Architects oversee client-side application architecture, state synchronization, bundle optimization, Core Web Vitals (LCP, INP, CLS), and component systems. They build scalable foundations that make team members productive and users happy.",
            responsibilities=[
                "Design clean component interfaces, state machines, and API data-fetching strategies.",
                "Measure and improve Core Web Vitals, runtime rendering performance, and bundle footprints.",
                "Establish testing standards across unit, component, and end-to-end user journeys.",
                "Ensure uncompromising cross-browser compatibility and keyboard accessibility."
            ],
            required_skills=[
                {"name": "TypeScript & Modern React", "importance": "Essential", "category": "Frontend"},
                {"name": "Browser Internals & Performance", "importance": "Essential", "category": "Platform"},
                {"name": "State Management & Caching", "importance": "Core", "category": "Architecture"},
                {"name": "Testing (Vitest, Testing Library)", "importance": "Core", "category": "Quality"},
                {"name": "Accessibility & Semantic HTML", "importance": "Core", "category": "UX Standards"}
            ],
            learning_phases=[
                {"phase": "1. Foundations", "focus": "Deep dive into JavaScript event loop, DOM rendering tree, and strict TypeScript.", "estimatedMonths": "1-2 months"},
                {"phase": "2. Core Skills", "focus": "Component lifecycle, memory leak prevention, server-rendering patterns.", "estimatedMonths": "2 months"},
                {"phase": "3. Applied Projects", "focus": "Build an offline-capable, responsive application with high performance marks.", "estimatedMonths": "2 months"},
                {"phase": "4. Portfolio & Systems", "focus": "Open-source component library with comprehensive test suite and docs.", "estimatedMonths": "1 month"},
                {"phase": "5. Interview Prep", "focus": "Frontend system design (feed, collaborative editor, state architecture).", "estimatedMonths": "1 month"}
            ],
            recommended_next_step={
                "title": "Analyze network waterfall and bundle composition in DevTools",
                "whyItMatters": "Finding bottlenecks early creates instantaneous, low-friction digital products.",
                "duration": "20 mins",
                "resourceName": "Web.dev Core Web Vitals Guide",
                "resourceUrl": "https://web.dev/vitals/"
            },
            entry_points=[
                "Self-taught web developer seeking deeper architectural rigor.",
                "Full-stack engineer focusing on high-polish client applications."
            ]
        )
    ]
=======
    # 1. Seed Career Paths
    careers = [
        CareerPath(
            id="ai-product-engineer",
                title="AI Product Engineer",
                category="Engineering",
                tagline="Bridging modern foundation models with production user interfaces and resilient client-server workflows.",
                match_reason="Combines your curiosity about machine learning with practical frontend and backend development skills.",
                description="AI Product Engineers build user-facing software powered by Large Language Models and multimodal systems. Rather than training models from scratch, they specialize in prompt architectures, evaluation harnesses, structured streaming, retrieval-augmented generation (RAG), and human-in-the-loop interfaces.",
                responsibilities=[
                    "Architect full-stack web applications integrating LLM APIs and vector retrieval layers.",
                    "Design graceful fallbacks, structured output validation, and streaming UI states for AI interactions.",
                    "Build automated evaluation pipelines to benchmark prompt changes against quality and latency criteria.",
                    "Collaborate with designers to create intuitive, transparent AI experiences that build user trust."
                ],
                required_skills=[
                    {"name": "TypeScript & React", "importance": "Essential", "category": "Frontend"},
                    {"name": "Python Fundamentals", "importance": "Essential", "category": "Backend"},
                    {"name": "API Design & Streaming", "importance": "Core", "category": "System Architecture"},
                    {"name": "Prompt & Context Engineering", "importance": "Core", "category": "AI Architecture"},
                    {"name": "Vector Embeddings & RAG", "importance": "Valuable", "category": "Information Retrieval"},
                    {"name": "Evaluation & Testing", "importance": "Valuable", "category": "Reliability"}
                ],
                learning_phases=[
                    {"phase": "1. Foundations", "focus": "Modern TypeScript, asynchronous programming, and basic Python scripting.", "estimatedMonths": "1-2 months"},
                    {"phase": "2. Core Skills", "focus": "API integrations, streaming protocols (SSE/WebSockets), and vector databases.", "estimatedMonths": "2-3 months"},
                    {"phase": "3. Applied Projects", "focus": "End-to-end RAG application with evaluation suite and fallback UX.", "estimatedMonths": "1-2 months"},
                    {"phase": "4. Portfolio & Systems", "focus": "Open-source contributions, public demo deployment, and latency optimization.", "estimatedMonths": "1 month"},
                    {"phase": "5. Interview Readiness", "focus": "System design for AI applications, behavioral stories, and coding exercises.", "estimatedMonths": "1 month"}
                ],
                recommended_next_step={
                    "title": "Spend 25 minutes practicing Python fundamentals & structured outputs",
                    "whyItMatters": "Understanding JSON schema validation and pydantic models is the cornerstone of reliable agentic integrations.",
                    "duration": "25 mins",
                    "resourceName": "Official Python Documentation & Pydantic Guide",
                    "resourceUrl": "https://docs.pydantic.dev/latest/"
                },
                entry_points=[
                    "Junior Full-Stack Developer transitioning into AI-powered tools.",
                    "Computer Science graduate with personal projects in LLM interfaces.",
                    "Frontend developer broadening into backend API orchestration."
                ]
            ),
            CareerPath(
                id="product-designer",
                title="Product & Design Systems Specialist",
                category="Design & UX",
                tagline="Crafting thoughtful digital typography, accessible interaction models, and reusable component architectures.",
                match_reason="Aligns with your eye for detail, typographic taste, and passion for inclusive user experiences.",
                description="Product Designers design human-centered interfaces from early discovery and wireframing through to high-fidelity design systems. They partner closely with engineers to ensure accessibility (WCAG AA/AAA), consistency, and effortless interactions.",
                responsibilities=[
                    "Design accessible, responsive web interfaces grounded in editorial typography and token-driven design systems.",
                    "Conduct user interviews, synthesize feedback, and validate prototypes with real users.",
                    "Maintain component libraries in Figma and author documentation for engineering handoff.",
                    "Audit interfaces for color contrast, keyboard navigation, and cognitive clarity."
                ],
                required_skills=[
                    {"name": "Figma & Component Architecture", "importance": "Essential", "category": "Design Tools"},
                    {"name": "Design Tokens & CSS", "importance": "Essential", "category": "Frontend"},
                    {"name": "WCAG 2.2 Accessibility", "importance": "Core", "category": "UX Standards"},
                    {"name": "Information Hierarchy", "importance": "Core", "category": "Visual Design"},
                    {"name": "Usability Testing & Research", "importance": "Valuable", "category": "Research"}
                ],
                learning_phases=[
                    {"phase": "1. Foundations", "focus": "Grid systems, typography scales, optical balance, and WCAG contrast rules.", "estimatedMonths": "1-2 months"},
                    {"phase": "2. Core Skills", "focus": "Token-based design systems, auto-layout, interactive prototyping.", "estimatedMonths": "2 months"},
                    {"phase": "3. Applied Projects", "focus": "Complete case study: redesigning a complex utility into a calm editorial experience.", "estimatedMonths": "2 months"},
                    {"phase": "4. Portfolio & Review", "focus": "Publishing two in-depth case studies with process and accessibility audits.", "estimatedMonths": "1 month"},
                    {"phase": "5. Interview Readiness", "focus": "Whiteboard design challenges, portfolio walkthroughs, and rationale defense.", "estimatedMonths": "1 month"}
                ],
                recommended_next_step={
                    "title": "Audit a component for WCAG 2.2 AA contrast and focus states",
                    "whyItMatters": "Editorial aesthetics require rigorous accessible foundation to ensure all readers can participate comfortably.",
                    "duration": "30 mins",
                    "resourceName": "Web Accessibility Initiative (W3C WAI)",
                    "resourceUrl": "https://www.w3.org/WAI/fundamentals/accessibility-intro/"
                },
                entry_points=[
                    "Visual designer expanding into digital product ergonomics.",
                    "Frontend engineer who enjoys design tokens and UI architecture.",
                    "Self-taught designer building a dedicated case-study portfolio."
                ]
            ),
            CareerPath(
                id="data-systems-analyst",
                title="Data Systems & Analytics Engineer",
                category="Data & AI",
                tagline="Transforming messy business events into clean semantic models, trustworthy data pipelines, and clear decisions.",
                match_reason="Suited for structured thinkers who enjoy analytical problem solving and data reliability.",
                description="Analytics Engineers sit between data engineers and decision-makers. They write performant SQL, build dbt models, manage version-controlled transformation pipelines, and create clear semantic metrics that the entire organization can rely upon.",
                responsibilities=[
                    "Model dimension and fact tables in modern cloud data warehouses (BigQuery, Snowflake).",
                    "Author automated data tests, documentation, and lineage graphs using dbt or SQLX.",
                    "Optimize query performance and partition schemas for cost efficiency.",
                    "Build dashboards with transparent data definitions that prevent misinterpretation."
                ],
                required_skills=[
                    {"name": "Advanced SQL & Window Functions", "importance": "Essential", "category": "Data Analysis"},
                    {"name": "Data Modeling (Kimball/Dimensional)", "importance": "Essential", "category": "Architecture"},
                    {"name": "dbt (Data Build Tool)", "importance": "Core", "category": "Engineering"},
                    {"name": "Python for Data Automation", "importance": "Core", "category": "Scripting"},
                    {"name": "Data Quality & Testing", "importance": "Valuable", "category": "Reliability"}
                ],
                learning_phases=[
                    {"phase": "1. Foundations", "focus": "SQL mastery, aggregations, window functions, and relational schema principles.", "estimatedMonths": "1-2 months"},
                    {"phase": "2. Core Skills", "focus": "Dimensional modeling, staging vs mart layers, and git-based workflows.", "estimatedMonths": "2 months"},
                    {"phase": "3. Applied Projects", "focus": "Build a production dbt pipeline on a public dataset with 100% test coverage.", "estimatedMonths": "1-2 months"},
                    {"phase": "4. Portfolio", "focus": "Document data model architecture, pipeline cost analysis, and reproducible demo.", "estimatedMonths": "1 month"},
                    {"phase": "5. Interview Prep", "focus": "SQL live coding, scenario-based data modeling, and business logic explanation.", "estimatedMonths": "1 month"}
                ],
                recommended_next_step={
                    "title": "Write three analytical window queries on sample data",
                    "whyItMatters": "Window functions like LEAD, LAG, and ROW_NUMBER unlock deep cohort and retention analytics.",
                    "duration": "35 mins",
                    "resourceName": "PostgreSQL Window Function Documentation",
                    "resourceUrl": "https://www.postgresql.org/docs/current/tutorial-window.html"
                },
                entry_points=[
                    "Business analyst transitioning into software-engineered data stacks.",
                    "Math or economics graduate with quantitative programming interest.",
                    "Junior backend engineer interested in data modeling and warehousing."
                ]
            ),
            CareerPath(
                id="frontend-architect",
                title="Frontend Architect & Web Platform Engineer",
                category="Engineering",
                tagline="Engineering fast, resilient, accessible web applications with modern modular architectures.",
                match_reason="Ideal for engineers who value software craftsmanship, performance optimization, and delightful developer experience.",
                description="Frontend Architects oversee client-side application architecture, state synchronization, bundle optimization, Core Web Vitals (LCP, INP, CLS), and component systems. They build scalable foundations that make team members productive and users happy.",
                responsibilities=[
                    "Design clean component interfaces, state machines, and API data-fetching strategies.",
                    "Measure and improve Core Web Vitals, runtime rendering performance, and bundle footprints.",
                    "Establish testing standards across unit, component, and end-to-end user journeys.",
                    "Ensure uncompromising cross-browser compatibility and keyboard accessibility."
                ],
                required_skills=[
                    {"name": "TypeScript & Modern React", "importance": "Essential", "category": "Frontend"},
                    {"name": "Browser Internals & Performance", "importance": "Essential", "category": "Platform"},
                    {"name": "State Management & Caching", "importance": "Core", "category": "Architecture"},
                    {"name": "Testing (Vitest, Testing Library)", "importance": "Core", "category": "Quality"},
                    {"name": "Accessibility & Semantic HTML", "importance": "Core", "category": "UX Standards"}
                ],
                learning_phases=[
                    {"phase": "1. Foundations", "focus": "Deep dive into JavaScript event loop, DOM rendering tree, and strict TypeScript.", "estimatedMonths": "1-2 months"},
                    {"phase": "2. Core Skills", "focus": "Component lifecycle, memory leak prevention, server-rendering patterns.", "estimatedMonths": "2 months"},
                    {"phase": "3. Applied Projects", "focus": "Build an offline-capable, responsive application with high performance marks.", "estimatedMonths": "2 months"},
                    {"phase": "4. Portfolio & Systems", "focus": "Open-source component library with comprehensive test suite and docs.", "estimatedMonths": "1 month"},
                    {"phase": "5. Interview Prep", "focus": "Frontend system design (feed, collaborative editor, state architecture).", "estimatedMonths": "1 month"}
                ],
                recommended_next_step={
                    "title": "Analyze network waterfall and bundle composition in DevTools",
                    "whyItMatters": "Finding bottlenecks early creates instantaneous, low-friction digital products.",
                    "duration": "20 mins",
                    "resourceName": "Web.dev Core Web Vitals Guide",
                    "resourceUrl": "https://web.dev/vitals/"
                },
                entry_points=[
                    "Self-taught web developer seeking deeper architectural rigor.",
                    "Full-stack engineer focusing on high-polish client applications."
                ]
            )
        ]
>>>>>>> origin/main
    for c in careers:
        if not db.query(CareerPath).filter(CareerPath.id == c.id).first():
            db.add(c)
    db.commit()

    # -------------------------------------------------------------
    # 2. Seed All 4 User Profiles (Idempotent)
    # -------------------------------------------------------------
    users_data = [
        UserProfile(
            id="default_user",
            name="Alex Morgan",
            study_status="Third-year CS & HCI Student",
            target_career_id="ai-product-engineer",
            interests=["Human-Centered AI", "Web Architecture", "Design Systems", "Interface Ergonomics"],
            current_skills=["TypeScript", "React", "Basic Python", "Semantic HTML"],
            primary_goal="Secure a Summer 2027 AI Product Engineering Internship",
            weekly_hours=8,
            onboarding_completed=True
        ),
        UserProfile(
            id="user_jordan_chen",
            name="Jordan Chen",
            study_status="Senior Interaction & Visual Design Major",
            target_career_id="product-designer",
            interests=["Design Systems", "Typography & Layout", "Digital Accessibility", "Design Ergonomics", "Cognitive Walkthroughs"],
            current_skills=["Figma & Auto-Layout", "Design Tokens", "CSS Architecture", "WCAG 2.2 Standards"],
            primary_goal="Join a high-craft product design studio as an Associate Design Systems Specialist",
            weekly_hours=10,
            onboarding_completed=True
        ),
        UserProfile(
            id="user_priya_sharma",
            name="Priya Sharma",
            study_status="Graduate Student in Applied Data Science",
            target_career_id="data-systems-analyst",
            interests=["Data Warehousing", "Semantic Modeling", "Analytical SQL", "Data Observability", "Pipeline Reliability"],
            current_skills=["Advanced SQL", "Python Data Automation", "dbt Core", "Relational Schema Design"],
            primary_goal="Secure an Analytics Engineer or Data Systems Role at a data-first technology enterprise",
            weekly_hours=12,
            onboarding_completed=True
        ),
        UserProfile(
            id="user_marcus_vance",
            name="Marcus Vance",
            study_status="Final-year Computer Science & Systems Engineering Student",
            target_career_id="frontend-architect",
            interests=["Web Performance & Core Web Vitals", "Browser Runtime Architecture", "Reactive State Trees", "Modern TypeScript", "Accessible Component Primitives"],
            current_skills=["Modern React & Hooks", "TypeScript Strict Mode", "Browser Rendering Pipelines", "State Synchronization"],
            primary_goal="Land a Frontend Infrastructure / Platform Engineer role focusing on sub-second web experiences",
            weekly_hours=14,
            onboarding_completed=True
        )
    ]
    for u in users_data:
        existing = db.query(UserProfile).filter(UserProfile.id == u.id).first()
        if not existing:
            db.add(u)
    db.commit()

<<<<<<< HEAD
    # -------------------------------------------------------------
    # 3. Seed Saved Careers (Idempotent)
    # -------------------------------------------------------------
    saved_careers = [
        # Alex Morgan
        SavedCareer(id="sc-alex-1", user_id="default_user", career_id="ai-product-engineer"),
        SavedCareer(id="sc-alex-2", user_id="default_user", career_id="product-designer"),
        # Jordan Chen
        SavedCareer(id="sc-jordan-1", user_id="user_jordan_chen", career_id="product-designer"),
        SavedCareer(id="sc-jordan-2", user_id="user_jordan_chen", career_id="frontend-architect"),
        # Priya Sharma
        SavedCareer(id="sc-priya-1", user_id="user_priya_sharma", career_id="data-systems-analyst"),
        SavedCareer(id="sc-priya-2", user_id="user_priya_sharma", career_id="ai-product-engineer"),
        # Marcus Vance
        SavedCareer(id="sc-marcus-1", user_id="user_marcus_vance", career_id="frontend-architect"),
        SavedCareer(id="sc-marcus-2", user_id="user_marcus_vance", career_id="ai-product-engineer"),
    ]
    for sc in saved_careers:
=======
    # 3. Seed Saved Careers (Idempotent)
    starter_saved = [
        SavedCareer(id="sc-1", user_id="default_user", career_id="ai-product-engineer"),
        SavedCareer(id="sc-2", user_id="default_user", career_id="product-designer")
    ]
    for sc in starter_saved:
>>>>>>> origin/main
        if not db.query(SavedCareer).filter(SavedCareer.user_id == sc.user_id, SavedCareer.career_id == sc.career_id).first():
            db.add(sc)
    db.commit()

<<<<<<< HEAD
    # -------------------------------------------------------------
    # 4. Seed Roadmap Tasks (Idempotent)
    # -------------------------------------------------------------
    all_tasks = [
        # --- Alex Morgan (ai-product-engineer) ---
        RoadmapTask(
            id="task-alex-1",
=======
    # 4. Seed Roadmap Tasks (Idempotent with career_id and deadline)
    starter_tasks = [
        RoadmapTask(
            id="task-1",
>>>>>>> origin/main
            user_id="default_user",
            career_id="ai-product-engineer",
            phase_id=1,
            phase_name="Phase 1: Foundations",
            title="Master modern TypeScript fundamentals & strict type safety",
            description="Understand union types, generics, type narrowing, and interface composition to prevent runtime bugs.",
            skill="TypeScript",
            estimated_time="4 hours",
            deadline="Completed",
            status="completed",
            resource_name="TypeScript Handbook",
            resource_type="Documentation",
            resource_url="https://www.typescriptlang.org/docs/handbook/intro.html",
            completed_at=datetime.utcnow()
        ),
        RoadmapTask(
<<<<<<< HEAD
            id="task-alex-2",
=======
            id="task-2",
>>>>>>> origin/main
            user_id="default_user",
            career_id="ai-product-engineer",
            phase_id=1,
            phase_name="Phase 1: Foundations",
            title="Study asynchronous JavaScript & Server-Sent Events (SSE)",
            description="Learn how streaming responses work from server to client with ReadableStream and fetch abort controllers.",
            skill="Asynchronous Programming",
            estimated_time="3 hours",
            deadline="Completed",
            status="completed",
            resource_name="MDN Web Docs: Streams API",
            resource_type="Documentation",
            resource_url="https://developer.mozilla.org/en-US/docs/Web/API/Streams_API",
            completed_at=datetime.utcnow()
        ),
        RoadmapTask(
<<<<<<< HEAD
            id="task-alex-3",
=======
            id="task-3",
>>>>>>> origin/main
            user_id="default_user",
            career_id="ai-product-engineer",
            phase_id=2,
            phase_name="Phase 2: Core Skills",
            title="Implement structured schema validation with Pydantic & Zod",
            description="Enforce deterministic schemas on model outputs to guarantee reliable UI rendering without runtime parsing errors.",
            skill="Schema Validation",
            estimated_time="25 mins",
            deadline="In 3 days",
            status="in_progress",
            resource_name="Zod TypeScript First Schema Validation",
            resource_type="Documentation",
            resource_url="https://zod.dev"
        ),
        RoadmapTask(
<<<<<<< HEAD
            id="task-alex-4",
=======
            id="task-4",
>>>>>>> origin/main
            user_id="default_user",
            career_id="ai-product-engineer",
            phase_id=2,
            phase_name="Phase 2: Core Skills",
            title="Build graceful UI fallback states for AI rate limits & network timeouts",
            description="Design human-friendly error banners, retry mechanisms, and non-blocking background task indicators.",
            skill="Resilient UX",
            estimated_time="2 hours",
            deadline="Next week",
            status="not_started",
            resource_name="Designing for System Recovery & Error States",
            resource_type="Interactive",
            resource_url="https://www.nngroup.com/articles/error-message-guidelines/"
        ),
        RoadmapTask(
<<<<<<< HEAD
            id="task-alex-5",
=======
            id="task-5",
>>>>>>> origin/main
            user_id="default_user",
            career_id="ai-product-engineer",
            phase_id=3,
            phase_name="Phase 3: Applied Projects",
            title="Develop an end-to-end Career Research Companion with vector search",
            description="Combine a clean editorial frontend with a semantic embedding index of job roles, skills, and open-access courses.",
            skill="Full-Stack AI Application",
            estimated_time="12 hours",
            deadline="End of month",
            status="not_started",
            resource_name="Project Specification & Architecture Guide",
            resource_type="Project Spec",
            resource_url="https://github.com"
<<<<<<< HEAD
        ),

        # --- Jordan Chen (product-designer) ---
        RoadmapTask(
            id="task-jordan-1",
            user_id="user_jordan_chen",
            career_id="product-designer",
            phase_id=1,
            phase_name="Phase 1: Foundations",
            title="Establish strict 4px/8px spatial grid and typographic scale in Figma",
            description="Build modular rem-based typographic hierarchy and spacing variables to streamline design token generation.",
            skill="Figma & Component Architecture",
            estimated_time="3 hours",
            deadline="Completed",
            status="completed",
            resource_name="Figma Design Systems Handbook",
            resource_type="Tutorial",
            resource_url="https://help.figma.com/hc/en-us/articles/360040451373",
            completed_at=datetime.utcnow()
        ),
        RoadmapTask(
            id="task-jordan-2",
            user_id="user_jordan_chen",
            career_id="product-designer",
            phase_id=1,
            phase_name="Phase 1: Foundations",
            title="Audit baseline color palette for WCAG 2.2 AA & AAA contrast compliance",
            description="Test text-to-background luminance ratios across light and dark themes using automated accessibility linters.",
            skill="WCAG 2.2 Accessibility",
            estimated_time="2.5 hours",
            deadline="Completed",
            status="completed",
            resource_name="W3C Contrast & Color Guidelines",
            resource_type="Documentation",
            resource_url="https://www.w3.org/WAI/WCAG22/quickref/",
            completed_at=datetime.utcnow()
        ),
        RoadmapTask(
            id="task-jordan-3",
            user_id="user_jordan_chen",
            career_id="product-designer",
            phase_id=2,
            phase_name="Phase 2: Core Skills",
            title="Build a multi-brand token system exporting to CSS custom properties",
            description="Synchronize Figma Variables with Style Dictionary and compile tokens into theme-specific CSS variables.",
            skill="Design Tokens & CSS",
            estimated_time="4 hours",
            deadline="In 2 days",
            status="in_progress",
            resource_name="Style Dictionary Documentation",
            resource_type="Documentation",
            resource_url="https://amzn.github.io/style-dictionary/"
        ),
        RoadmapTask(
            id="task-jordan-4",
            user_id="user_jordan_chen",
            career_id="product-designer",
            phase_id=2,
            phase_name="Phase 2: Core Skills",
            title="Construct complex modal & drawer dialog primitives with focus trapping",
            description="Prototype keyboard accessible modals with ARIA roles, inert backgrounds, and escape key dismissals.",
            skill="WCAG 2.2 Accessibility",
            estimated_time="3.5 hours",
            deadline="Next week",
            status="not_started",
            resource_name="WAI-ARIA Dialog (Modal) Pattern",
            resource_type="Documentation",
            resource_url="https://www.w3.org/WAI/ARIA/apg/patterns/dialog-modal/"
        ),
        RoadmapTask(
            id="task-jordan-5",
            user_id="user_jordan_chen",
            career_id="product-designer",
            phase_id=3,
            phase_name="Phase 3: Applied Projects",
            title="Publish open-source accessible component system case study",
            description="Document the complete component lifecycle, design rationales, contrast benchmarks, and developer handoff specs.",
            skill="Information Hierarchy",
            estimated_time="10 hours",
            deadline="End of month",
            status="not_started",
            resource_name="Design Systems Field Guide",
            resource_type="Guide",
            resource_url="https://www.designsystems.com/"
        ),

        # --- Priya Sharma (data-systems-analyst) ---
        RoadmapTask(
            id="task-priya-1",
            user_id="user_priya_sharma",
            career_id="data-systems-analyst",
            phase_id=1,
            phase_name="Phase 1: Foundations",
            title="Master analytical window functions and recursive CTEs in PostgreSQL",
            description="Compute running totals, rolling moving averages, LAG/LEAD deltas, and hierarchical graph queries efficiently.",
            skill="Advanced SQL & Window Functions",
            estimated_time="4 hours",
            deadline="Completed",
            status="completed",
            resource_name="PostgreSQL Analytical Queries Guide",
            resource_type="Tutorial",
            resource_url="https://www.postgresql.org/docs/current/tutorial-window.html",
            completed_at=datetime.utcnow()
        ),
        RoadmapTask(
            id="task-priya-2",
            user_id="user_priya_sharma",
            career_id="data-systems-analyst",
            phase_id=1,
            phase_name="Phase 1: Foundations",
            title="Design dimensional fact and dimension schemas using Kimball methodology",
            description="Create star schemas with conformed dimensions, surrogate keys, and slowly changing dimensions (SCD Type 2).",
            skill="Data Modeling (Kimball/Dimensional)",
            estimated_time="3 hours",
            deadline="Completed",
            status="completed",
            resource_name="The Data Warehouse Toolkit (Kimball)",
            resource_type="Reference",
            resource_url="https://www.kimballgroup.com/data-warehouse-business-intelligence-resources/",
            completed_at=datetime.utcnow()
        ),
        RoadmapTask(
            id="task-priya-3",
            user_id="user_priya_sharma",
            career_id="data-systems-analyst",
            phase_id=2,
            phase_name="Phase 2: Core Skills",
            title="Implement dbt staging, intermediate, and mart layers with automated schema tests",
            description="Build modular transformations with ephemeral staging CTEs, custom tests, and dbt documentation generators.",
            skill="dbt (Data Build Tool)",
            estimated_time="5 hours",
            deadline="In 3 days",
            status="in_progress",
            resource_name="dbt Best Practices & Structure Guide",
            resource_type="Documentation",
            resource_url="https://docs.getdbt.com/best-practices/how-we-structure/1-guide-overview"
        ),
        RoadmapTask(
            id="task-priya-4",
            user_id="user_priya_sharma",
            career_id="data-systems-analyst",
            phase_id=2,
            phase_name="Phase 2: Core Skills",
            title="Establish data freshness alerts and anomaly detection checks",
            description="Configure automated data assertions to monitor row count anomalies, missing categorical values, and SLA delays.",
            skill="Data Quality & Testing",
            estimated_time="3.5 hours",
            deadline="Next week",
            status="not_started",
            resource_name="Great Expectations Quickstart",
            resource_type="Documentation",
            resource_url="https://greatexpectations.io/"
        ),
        RoadmapTask(
            id="task-priya-5",
            user_id="user_priya_sharma",
            career_id="data-systems-analyst",
            phase_id=3,
            phase_name="Phase 3: Applied Projects",
            title="Deploy end-to-end event analytics pipeline with documentation and lineage DAG",
            description="Transform multi-gigabyte synthetic transaction streams into dimensional business intelligence marts.",
            skill="Python for Data Automation",
            estimated_time="12 hours",
            deadline="End of month",
            status="not_started",
            resource_name="Modern Data Stack Pipeline Architecture",
            resource_type="Project Spec",
            resource_url="https://github.com"
        ),

        # --- Marcus Vance (frontend-architect) ---
        RoadmapTask(
            id="task-marcus-1",
            user_id="user_marcus_vance",
            career_id="frontend-architect",
            phase_id=1,
            phase_name="Phase 1: Foundations",
            title="Analyze browser layout, paint, and composite stages using Chrome DevTools",
            description="Profile long main-thread execution tasks, forced synchronous reflows, and GPU layer compositing memory footprints.",
            skill="Browser Internals & Performance",
            estimated_time="3.5 hours",
            deadline="Completed",
            status="completed",
            resource_name="Rendering Performance in Chrome DevTools",
            resource_type="Documentation",
            resource_url="https://developer.chrome.com/docs/devtools/performance/",
            completed_at=datetime.utcnow()
        ),
        RoadmapTask(
            id="task-marcus-2",
            user_id="user_marcus_vance",
            career_id="frontend-architect",
            phase_id=1,
            phase_name="Phase 1: Foundations",
            title="Implement strict TypeScript utility types and compile-time invariant checks",
            description="Build robust conditional types, template literal keys, branded types, and exhaustive switch-statement analyzers.",
            skill="TypeScript & Modern React",
            estimated_time="4 hours",
            deadline="Completed",
            status="completed",
            resource_name="Advanced TypeScript Type Programming",
            resource_type="Reference",
            resource_url="https://www.typescriptlang.org/docs/handbook/2/types-from-types.html",
            completed_at=datetime.utcnow()
        ),
        RoadmapTask(
            id="task-marcus-3",
            user_id="user_marcus_vance",
            career_id="frontend-architect",
            phase_id=2,
            phase_name="Phase 2: Core Skills",
            title="Build a high-throughput virtualized data table rendering 100k rows at 60 FPS",
            description="Utilize custom windowing math, dynamic row height measurement, and intersection observers for butter-smooth scrolling.",
            skill="Browser Internals & Performance",
            estimated_time="6 hours",
            deadline="In 4 days",
            status="in_progress",
            resource_name="TanStack Virtual Core Concepts",
            resource_type="Documentation",
            resource_url="https://tanstack.com/virtual/latest"
        ),
        RoadmapTask(
            id="task-marcus-4",
            user_id="user_marcus_vance",
            career_id="frontend-architect",
            phase_id=2,
            phase_name="Phase 2: Core Skills",
            title="Optimize Core Web Vitals (LCP, INP, CLS) to achieve a 98+ Lighthouse score",
            description="Eliminate script-blocking resources, prefetch key assets, and isolate layout shifts using CSS aspect-ratio placeholders.",
            skill="Browser Internals & Performance",
            estimated_time="4 hours",
            deadline="Next week",
            status="not_started",
            resource_name="Web.dev INP Optimization Guide",
            resource_type="Guide",
            resource_url="https://web.dev/optimize-inp/"
        ),
        RoadmapTask(
            id="task-marcus-5",
            user_id="user_marcus_vance",
            career_id="frontend-architect",
            phase_id=3,
            phase_name="Phase 3: Applied Projects",
            title="Architect a modular micro-frontend shell with shared state isolation",
            description="Implement an event-driven pub-sub bus, sandboxed style encapsulation, and resilient sub-app failover mechanisms.",
            skill="State Management & Caching",
            estimated_time="14 hours",
            deadline="End of month",
            status="not_started",
            resource_name="Micro Frontend Architecture Patterns",
            resource_type="Project Spec",
            resource_url="https://martinfowler.com/articles/micro-frontends.html"
        )
    ]
    for task in all_tasks:
        if not db.query(RoadmapTask).filter(RoadmapTask.id == task.id).first():
            db.add(task)
    db.commit()

    # -------------------------------------------------------------
    # 5. Seed Skills (Idempotent)
    # -------------------------------------------------------------
    all_skills = [
        # --- Alex Morgan ---
        UserSkill(id="skill-alex-ts", user_id="default_user", name="TypeScript & React", category="Frontend Engineering", status="practicing", hours_spent=28.0, target_hours=50.0, is_gap=False, last_practiced="Today"),
        UserSkill(id="skill-alex-py", user_id="default_user", name="Python Fundamentals", category="Backend & Scripting", status="practicing", hours_spent=16.0, target_hours=40.0, is_gap=False, last_practiced="Yesterday"),
        UserSkill(id="skill-alex-api", user_id="default_user", name="API Design & Streaming", category="System Architecture", status="learning", hours_spent=8.0, target_hours=30.0, is_gap=False, last_practiced="3 days ago"),
        UserSkill(id="skill-alex-a11y", user_id="default_user", name="WCAG 2.2 Accessibility", category="Design & UX Standards", status="proficient", hours_spent=22.0, target_hours=25.0, is_gap=False, last_practiced="4 days ago"),
        UserSkill(id="skill-alex-prompt", user_id="default_user", name="Context & Prompt Architecture", category="AI Systems", status="learning", hours_spent=10.0, target_hours=35.0, is_gap=False, last_practiced="1 week ago"),
        UserSkill(id="skill-alex-eval", user_id="default_user", name="Vector Embeddings & RAG", category="AI Systems", status="learning", hours_spent=0.0, target_hours=20.0, is_gap=True, last_practiced="Identified gap"),

        # --- Jordan Chen (Product & Design Systems) ---
        UserSkill(id="skill-jordan-figma", user_id="user_jordan_chen", name="Figma & Component Architecture", category="Design Tools", status="proficient", hours_spent=34.0, target_hours=40.0, is_gap=False, last_practiced="Yesterday"),
        UserSkill(id="skill-jordan-tokens", user_id="user_jordan_chen", name="Design Tokens & CSS", category="Frontend", status="practicing", hours_spent=22.0, target_hours=30.0, is_gap=False, last_practiced="2 days ago"),
        UserSkill(id="skill-jordan-a11y", user_id="user_jordan_chen", name="WCAG 2.2 Accessibility", category="UX Standards", status="practicing", hours_spent=19.0, target_hours=25.0, is_gap=False, last_practiced="3 days ago"),
        UserSkill(id="skill-jordan-hierarchy", user_id="user_jordan_chen", name="Information Hierarchy", category="Visual Design", status="proficient", hours_spent=28.0, target_hours=30.0, is_gap=False, last_practiced="1 week ago"),
        UserSkill(id="skill-jordan-research", user_id="user_jordan_chen", name="Usability Testing & Research", category="Research", status="learning", hours_spent=0.0, target_hours=20.0, is_gap=True, last_practiced="Identified gap"),

        # --- Priya Sharma (Data Systems & Analytics) ---
        UserSkill(id="skill-priya-sql", user_id="user_priya_sharma", name="Advanced SQL & Window Functions", category="Data Analysis", status="proficient", hours_spent=38.0, target_hours=40.0, is_gap=False, last_practiced="Today"),
        UserSkill(id="skill-priya-kimball", user_id="user_priya_sharma", name="Data Modeling (Kimball/Dimensional)", category="Architecture", status="practicing", hours_spent=24.0, target_hours=35.0, is_gap=False, last_practiced="Yesterday"),
        UserSkill(id="skill-priya-dbt", user_id="user_priya_sharma", name="dbt (Data Build Tool)", category="Engineering", status="practicing", hours_spent=18.0, target_hours=30.0, is_gap=False, last_practiced="3 days ago"),
        UserSkill(id="skill-priya-python", user_id="user_priya_sharma", name="Python for Data Automation", category="Scripting", status="proficient", hours_spent=29.0, target_hours=30.0, is_gap=False, last_practiced="4 days ago"),
        UserSkill(id="skill-priya-quality", user_id="user_priya_sharma", name="Data Quality & Testing", category="Reliability", status="learning", hours_spent=0.0, target_hours=25.0, is_gap=True, last_practiced="Identified gap"),

        # --- Marcus Vance (Frontend Architect) ---
        UserSkill(id="skill-marcus-ts", user_id="user_marcus_vance", name="TypeScript & Modern React", category="Frontend", status="proficient", hours_spent=46.0, target_hours=50.0, is_gap=False, last_practiced="Today"),
        UserSkill(id="skill-marcus-perf", user_id="user_marcus_vance", name="Browser Internals & Performance", category="Platform", status="practicing", hours_spent=26.0, target_hours=40.0, is_gap=False, last_practiced="Yesterday"),
        UserSkill(id="skill-marcus-state", user_id="user_marcus_vance", name="State Management & Caching", category="Architecture", status="practicing", hours_spent=20.0, target_hours=30.0, is_gap=False, last_practiced="2 days ago"),
        UserSkill(id="skill-marcus-test", user_id="user_marcus_vance", name="Testing (Vitest, Testing Library)", category="Quality", status="practicing", hours_spent=15.0, target_hours=25.0, is_gap=False, last_practiced="5 days ago"),
        UserSkill(id="skill-marcus-a11y", user_id="user_marcus_vance", name="Accessibility & Semantic HTML", category="UX Standards", status="proficient", hours_spent=24.0, target_hours=25.0, is_gap=False, last_practiced="1 week ago"),
        UserSkill(id="skill-marcus-wasm", user_id="user_marcus_vance", name="WebAssembly & Canvas", category="Platform", status="learning", hours_spent=0.0, target_hours=30.0, is_gap=True, last_practiced="Identified gap"),
    ]
    for skill in all_skills:
        if not db.query(UserSkill).filter(UserSkill.id == skill.id).first():
            db.add(skill)
    db.commit()

    # -------------------------------------------------------------
    # 6. Seed Initial Chat Messages (Idempotent)
    # -------------------------------------------------------------
    messages = [
        ChatMessage(
            id="msg-welcome-alex",
            user_id="default_user",
            session_id="session-alex-default",
            sender="assistant",
            text="Hello Alex. I am your career mentor.\n\nYour career is a journey, and you do not need to figure everything out today. Whether you want to reflect on what path fits your strengths, structure your weekly learning, or prepare for internship applications, I am here to work through it with you step-by-step.\n\nWhere would you like to start today?",
            suggested_actions=[
                "Help me choose a career direction.",
                "What should I learn to become an AI engineer?",
                "Can you help me prepare for an internship?",
                "Let's make a realistic weekly learning plan."
            ]
        ),
        ChatMessage(
            id="msg-welcome-jordan",
            user_id="user_jordan_chen",
            session_id="session-jordan-default",
            sender="assistant",
            text="Hello Jordan. I am your design career mentor.\n\nCrafting high-quality interfaces requires both typographic discernment and structured component architectures. Whether you are fine-tuning your token taxonomy, preparing design audit case studies, or exploring design engineering roles, I am here to assist you.\n\nWhere would you like to start today?",
            suggested_actions=[
                "Review my design system token structure",
                "How do I explain accessibility trade-offs in interviews?",
                "Plan a structured usability test protocol",
                "Explore design engineering career transitions"
            ]
        ),
        ChatMessage(
            id="msg-welcome-priya",
            user_id="user_priya_sharma",
            session_id="session-priya-default",
            sender="assistant",
            text="Hello Priya. I am your data systems mentor.\n\nTransforming raw analytical events into reliable business intelligence demands disciplined modeling, rigorous testing, and clear semantic layers. Whether you want to review Kimball modeling principles, structure dbt staging pipelines, or practice SQL whiteboard queries, we can tackle it together.\n\nWhat would you like to work on first?",
            suggested_actions=[
                "Walk through a dimensional modeling scenario",
                "Best practices for dbt model testing and CI",
                "How to prepare for an Analytics Engineer technical screen",
                "Plan weekly SQL practice tasks"
            ]
        ),
        ChatMessage(
            id="msg-welcome-marcus",
            user_id="user_marcus_vance",
            session_id="session-marcus-default",
            sender="assistant",
            text="Hello Marcus. I am your web platform mentor.\n\nBuilding high-performance client applications requires deep mastery over runtime performance, browser rendering threads, and maintainable state boundaries. Let's work together to optimize your portfolio projects, study INP bottlenecks, and craft compelling architectural case studies.\n\nWhere shall we dive in today?",
            suggested_actions=[
                "Analyze Interaction to Next Paint (INP) strategies",
                "Review my virtualized list implementation",
                "System design interview prep for frontend platforms",
                "Map out my next week of performance experiments"
            ]
        )
    ]
    for msg in messages:
        if not db.query(ChatMessage).filter(ChatMessage.id == msg.id).first():
            db.add(msg)
    db.commit()

    # -------------------------------------------------------------
    # 7. Seed GitHub Accounts & Repositories (Idempotent)
    # -------------------------------------------------------------
    gh_accounts = [
        GitHubAccount(
            id="gh-alex",
            user_id="default_user",
            github_username="alex-morgan-dev",
            avatar_url="https://avatars.githubusercontent.com/u/98765432?v=4",
            html_url="https://github.com/alex-morgan-dev",
            scope="repo,read:user"
        ),
        GitHubAccount(
            id="gh-jordan",
            user_id="user_jordan_chen",
            github_username="jordan-chen",
            avatar_url="https://avatars.githubusercontent.com/u/10293847?v=4",
            html_url="https://github.com/jordan-chen",
            scope="repo,read:user"
        ),
        GitHubAccount(
            id="gh-priya",
            user_id="user_priya_sharma",
            github_username="priya-sharma",
            avatar_url="https://avatars.githubusercontent.com/u/20394857?v=4",
            html_url="https://github.com/priya-sharma",
            scope="repo,read:user"
        ),
        GitHubAccount(
            id="gh-marcus",
            user_id="user_marcus_vance",
            github_username="marcus-vance",
            avatar_url="https://avatars.githubusercontent.com/u/30495867?v=4",
            html_url="https://github.com/marcus-vance",
            scope="repo,read:user"
        )
    ]
    for acc in gh_accounts:
        if not db.query(GitHubAccount).filter(GitHubAccount.id == acc.id).first():
            db.add(acc)
    db.commit()

    gh_repos = [
        # Alex Morgan
        GitHubRepository(
            id="repo-alex-1",
            user_id="default_user",
            account_id="gh-alex",
            repo_full_name="alex-morgan-dev/ai-career-companion",
            default_branch="main",
            html_url="https://github.com/alex-morgan-dev/ai-career-companion",
            is_authorized=True,
            last_commit_sha="1a2b3c4d5e6f7a8b",
            last_synced_at=datetime.utcnow()
        ),
        GitHubRepository(
            id="repo-alex-2",
            user_id="default_user",
            account_id="gh-alex",
            repo_full_name="alex-morgan-dev/prompt-eval-harness",
            default_branch="main",
            html_url="https://github.com/alex-morgan-dev/prompt-eval-harness",
            is_authorized=True,
            last_commit_sha="8b7a6f5e4d3c2b1a",
            last_synced_at=datetime.utcnow()
        ),

        # Jordan Chen
        GitHubRepository(
            id="repo-jordan-1",
            user_id="user_jordan_chen",
            account_id="gh-jordan",
            repo_full_name="jordan-chen/accessible-tokens-core",
            default_branch="main",
            html_url="https://github.com/jordan-chen/accessible-tokens-core",
            is_authorized=True,
            last_commit_sha="7a8b9c0d1e2f3a4b",
            last_synced_at=datetime.utcnow()
        ),
        GitHubRepository(
            id="repo-jordan-2",
            user_id="user_jordan_chen",
            account_id="gh-jordan",
            repo_full_name="jordan-chen/design-audit-suite",
            default_branch="main",
            html_url="https://github.com/jordan-chen/design-audit-suite",
            is_authorized=True,
            last_commit_sha="2f3a4b5c6d7e8f9a",
            last_synced_at=datetime.utcnow()
        ),

        # Priya Sharma
        GitHubRepository(
            id="repo-priya-1",
            user_id="user_priya_sharma",
            account_id="gh-priya",
            repo_full_name="priya-sharma/financial-analytics-marts",
            default_branch="main",
            html_url="https://github.com/priya-sharma/financial-analytics-marts",
            is_authorized=True,
            last_commit_sha="4c5d6e7f8a9b0c1d",
            last_synced_at=datetime.utcnow()
        ),
        GitHubRepository(
            id="repo-priya-2",
            user_id="user_priya_sharma",
            account_id="gh-priya",
            repo_full_name="priya-sharma/credit-risk-pipeline",
            default_branch="main",
            html_url="https://github.com/priya-sharma/credit-risk-pipeline",
            is_authorized=True,
            last_commit_sha="9b0c1d2e3f4a5b6c",
            last_synced_at=datetime.utcnow()
        ),

        # Marcus Vance
        GitHubRepository(
            id="repo-marcus-1",
            user_id="user_marcus_vance",
            account_id="gh-marcus",
            repo_full_name="marcus-vance/virtualized-canvas-grid",
            default_branch="main",
            html_url="https://github.com/marcus-vance/virtualized-canvas-grid",
            is_authorized=True,
            last_commit_sha="9e8d7c6b5a4f3e2d",
            last_synced_at=datetime.utcnow()
        ),
        GitHubRepository(
            id="repo-marcus-2",
            user_id="user_marcus_vance",
            account_id="gh-marcus",
            repo_full_name="marcus-vance/reactive-state-store",
            default_branch="main",
            html_url="https://github.com/marcus-vance/reactive-state-store",
            is_authorized=True,
            last_commit_sha="3e2d1c0b9a8f7e6d",
            last_synced_at=datetime.utcnow()
        )
    ]
    for repo in gh_repos:
        if not db.query(GitHubRepository).filter(GitHubRepository.id == repo.id).first():
            db.add(repo)
    db.commit()

    # -------------------------------------------------------------
    # 8. Seed Skill Assessments & Evidence (Idempotent)
    # -------------------------------------------------------------
    assessments_data = [
        # Alex Morgan
        {
            "assessment": SkillAssessment(
                id="asmt-alex-01",
                user_id="default_user",
                repo_full_name="alex-morgan-dev/ai-career-companion",
                commit_sha="1a2b3c4d5e6f7a8b",
                version=1,
                overall_score=85.0,
                match_percentage=82.0,
                status="completed",
                summary="Solid TypeScript client components, server streaming SSE logic, and robust schema validations.",
                total_skills_assessed=4,
                skills_demonstrated=3,
                skills_partially_demonstrated=1,
                skills_not_demonstrated=0
            ),
            "results": [
                AssessmentSkillResult(
                    id="res-alex-1",
                    assessment_id="asmt-alex-01",
                    skill_name="TypeScript & React",
                    requirement_type="required",
                    status="Demonstrated",
                    score=90.0,
                    rationale="Strict interface definitions and functional React hooks in companion layout.",
                    evidence_count=2,
                    direct_evidence_count=2
                ),
                AssessmentSkillResult(
                    id="res-alex-2",
                    assessment_id="asmt-alex-01",
                    skill_name="API Design & Streaming",
                    requirement_type="required",
                    status="Demonstrated",
                    score=85.0,
                    rationale="Direct use of ReadableStream and fetch abort controllers for streaming LLM text.",
                    evidence_count=1,
                    direct_evidence_count=1
                )
            ],
            "evidence": [
                RepositoryEvidence(
                    id="evi-alex-1",
                    assessment_id="asmt-alex-01",
                    skill_name="TypeScript & React",
                    repo_full_name="alex-morgan-dev/ai-career-companion",
                    commit_sha="1a2b3c4d5e6f7a8b",
                    file_path="src/components/CompanionView.tsx",
                    start_line=12,
                    end_line=28,
                    code_snippet="export const CompanionView: React.FC<CompanionProps> = ({ session, onStreamChunk }) => { ... }",
                    evidence_category="Direct AST invocation",
                    is_direct_evidence=True,
                    confidence_score=0.95,
                    ast_node_type="ExportNamedDeclaration",
                    rationale="Typed React functional component declaration with typed props.",
                    github_url="https://github.com/alex-morgan-dev/ai-career-companion/blob/1a2b3c4d5e6f7a8b/src/components/CompanionView.tsx#L12-L28"
                )
            ]
        },

        # Jordan Chen
        {
            "assessment": SkillAssessment(
                id="asmt-jordan-01",
                user_id="user_jordan_chen",
                repo_full_name="jordan-chen/accessible-tokens-core",
                commit_sha="7a8b9c0d1e2f3a4b",
                version=1,
                overall_score=88.5,
                match_percentage=85.0,
                status="completed",
                summary="Demonstrated high proficiency in token definitions, CSS custom properties, and WCAG accessibility utilities.",
                total_skills_assessed=4,
                skills_demonstrated=3,
                skills_partially_demonstrated=1,
                skills_not_demonstrated=0
            ),
            "results": [
                AssessmentSkillResult(
                    id="res-jordan-1",
                    assessment_id="asmt-jordan-01",
                    skill_name="Design Tokens & CSS",
                    requirement_type="required",
                    status="Demonstrated",
                    score=92.0,
                    rationale="Comprehensive semantic color and typography token architecture with automated CSS export.",
                    evidence_count=2,
                    direct_evidence_count=2
                ),
                AssessmentSkillResult(
                    id="res-jordan-2",
                    assessment_id="asmt-jordan-01",
                    skill_name="WCAG 2.2 Accessibility",
                    requirement_type="required",
                    status="Demonstrated",
                    score=88.0,
                    rationale="Algorithmic contrast ratio calculation ensuring 4.5:1 text and 3:1 graphical elements.",
                    evidence_count=1,
                    direct_evidence_count=1
                )
            ],
            "evidence": [
                RepositoryEvidence(
                    id="evi-jordan-1",
                    assessment_id="asmt-jordan-01",
                    skill_name="Design Tokens & CSS",
                    repo_full_name="jordan-chen/accessible-tokens-core",
                    commit_sha="7a8b9c0d1e2f3a4b",
                    file_path="src/tokens/typography.tokens.json",
                    start_line=1,
                    end_line=20,
                    code_snippet='{\n  "fontFamily": { "editorial": { "value": "Newsreader, Georgia, serif" } },\n  "fontSize": { "scale-sm": { "value": "0.875rem" } }\n}',
                    evidence_category="Direct Token Definition",
                    is_direct_evidence=True,
                    confidence_score=0.98,
                    ast_node_type="JSONTokenManifest",
                    rationale="W3C Design Token Community Group compliant token structure.",
                    github_url="https://github.com/jordan-chen/accessible-tokens-core/blob/7a8b9c0d1e2f3a4b/src/tokens/typography.tokens.json#L1-L20"
                ),
                RepositoryEvidence(
                    id="evi-jordan-2",
                    assessment_id="asmt-jordan-01",
                    skill_name="WCAG 2.2 Accessibility",
                    repo_full_name="jordan-chen/accessible-tokens-core",
                    commit_sha="7a8b9c0d1e2f3a4b",
                    file_path="src/utils/contrast.ts",
                    start_line=14,
                    end_line=30,
                    code_snippet="export function getContrastRatio(fgLuminance: number, bgLuminance: number): number {\n  const l1 = Math.max(fgLuminance, bgLuminance);\n  const l2 = Math.min(fgLuminance, bgLuminance);\n  return (l1 + 0.05) / (l2 + 0.05);\n}",
                    evidence_category="Direct AST invocation",
                    is_direct_evidence=True,
                    confidence_score=0.96,
                    ast_node_type="FunctionDeclaration",
                    rationale="Mathematical implementation of W3C relative luminance contrast formula.",
                    github_url="https://github.com/jordan-chen/accessible-tokens-core/blob/7a8b9c0d1e2f3a4b/src/utils/contrast.ts#L14-L30"
                )
            ]
        },

        # Priya Sharma
        {
            "assessment": SkillAssessment(
                id="asmt-priya-01",
                user_id="user_priya_sharma",
                repo_full_name="priya-sharma/financial-analytics-marts",
                commit_sha="4c5d6e7f8a9b0c1d",
                version=1,
                overall_score=91.0,
                match_percentage=90.0,
                status="completed",
                summary="Exemplary dbt models, multi-level analytical CTEs, window aggregates, and Kimball dimensional marts.",
                total_skills_assessed=4,
                skills_demonstrated=4,
                skills_partially_demonstrated=0,
                skills_not_demonstrated=0
            ),
            "results": [
                AssessmentSkillResult(
                    id="res-priya-1",
                    assessment_id="asmt-priya-01",
                    skill_name="Advanced SQL & Window Functions",
                    requirement_type="required",
                    status="Demonstrated",
                    score=95.0,
                    rationale="Expert use of LEAD, LAG, DENSE_RANK and sliding window partitions.",
                    evidence_count=2,
                    direct_evidence_count=2
                ),
                AssessmentSkillResult(
                    id="res-priya-2",
                    assessment_id="asmt-priya-01",
                    skill_name="Data Modeling (Kimball/Dimensional)",
                    requirement_type="required",
                    status="Demonstrated",
                    score=92.0,
                    rationale="Conformed customer and transaction dimensions with surrogate primary keys.",
                    evidence_count=1,
                    direct_evidence_count=1
                )
            ],
            "evidence": [
                RepositoryEvidence(
                    id="evi-priya-1",
                    assessment_id="asmt-priya-01",
                    skill_name="Advanced SQL & Window Functions",
                    repo_full_name="priya-sharma/financial-analytics-marts",
                    commit_sha="4c5d6e7f8a9b0c1d",
                    file_path="models/marts/finance/fct_daily_revenue_cohorts.sql",
                    start_line=25,
                    end_line=42,
                    code_snippet="SELECT customer_id, transaction_date, amount,\n  SUM(amount) OVER (PARTITION BY customer_id ORDER BY transaction_date ROWS BETWEEN 29 PRECEDING AND CURRENT ROW) as rolling_30d_spend,\n  DENSE_RANK() OVER (PARTITION BY cohort_month ORDER BY total_spend DESC) as cohort_rank\nFROM base_transactions",
                    evidence_category="Direct SQL Query",
                    is_direct_evidence=True,
                    confidence_score=0.99,
                    ast_node_type="SelectStatement",
                    rationale="Window frame specification with rolling aggregations and partition ranking.",
                    github_url="https://github.com/priya-sharma/financial-analytics-marts/blob/4c5d6e7f8a9b0c1d/models/marts/finance/fct_daily_revenue_cohorts.sql#L25-L42"
                )
            ]
        },

        # Marcus Vance
        {
            "assessment": SkillAssessment(
                id="asmt-marcus-01",
                user_id="user_marcus_vance",
                repo_full_name="marcus-vance/virtualized-canvas-grid",
                commit_sha="9e8d7c6b5a4f3e2d",
                version=1,
                overall_score=94.0,
                match_percentage=92.0,
                status="completed",
                summary="Exceptional performance engineering with virtualized viewport rendering, RAF timing loops, and zero memory thrashing.",
                total_skills_assessed=5,
                skills_demonstrated=4,
                skills_partially_demonstrated=1,
                skills_not_demonstrated=0
            ),
            "results": [
                AssessmentSkillResult(
                    id="res-marcus-1",
                    assessment_id="asmt-marcus-01",
                    skill_name="Browser Internals & Performance",
                    requirement_type="required",
                    status="Demonstrated",
                    score=96.0,
                    rationale="Non-blocking requestAnimationFrame paint schedule and memory-pooled row structures.",
                    evidence_count=2,
                    direct_evidence_count=2
                ),
                AssessmentSkillResult(
                    id="res-marcus-2",
                    assessment_id="asmt-marcus-01",
                    skill_name="TypeScript & Modern React",
                    requirement_type="required",
                    status="Demonstrated",
                    score=94.0,
                    rationale="Strict generic row data constraints with Zero-Any compilation guarantee.",
                    evidence_count=1,
                    direct_evidence_count=1
                )
            ],
            "evidence": [
                RepositoryEvidence(
                    id="evi-marcus-1",
                    assessment_id="asmt-marcus-01",
                    skill_name="Browser Internals & Performance",
                    repo_full_name="marcus-vance/virtualized-canvas-grid",
                    commit_sha="9e8d7c6b5a4f3e2d",
                    file_path="src/engine/ViewportScheduler.ts",
                    start_line=30,
                    end_line=50,
                    code_snippet="export class ViewportScheduler {\n  private rafId: number | null = null;\n  scheduleRender(callback: FrameRequestCallback) {\n    if (this.rafId) cancelAnimationFrame(this.rafId);\n    this.rafId = requestAnimationFrame(callback);\n  }\n}",
                    evidence_category="Direct AST invocation",
                    is_direct_evidence=True,
                    confidence_score=0.98,
                    ast_node_type="ClassDeclaration",
                    rationale="De-bouncing layout passes synchronized to the hardware display refresh rate.",
                    github_url="https://github.com/marcus-vance/virtualized-canvas-grid/blob/9e8d7c6b5a4f3e2d/src/engine/ViewportScheduler.ts#L30-L50"
                )
            ]
        }
    ]

    for item in assessments_data:
        asmt = item["assessment"]
        if not db.query(SkillAssessment).filter(SkillAssessment.id == asmt.id).first():
            db.add(asmt)
            db.commit()

        for res in item["results"]:
            if not db.query(AssessmentSkillResult).filter(AssessmentSkillResult.id == res.id).first():
                db.add(res)
        for evi in item["evidence"]:
            if not db.query(RepositoryEvidence).filter(RepositoryEvidence.id == evi.id).first():
                db.add(evi)
        db.commit()

    # Starter roadmap tasks
    starter_tasks = [
        RoadmapTask(
            id="task-1",
            user_id="default_user",
            career_id="ai-product-engineer",
            phase_id=1,
            phase_name="Phase 1: Foundations",
            title="Master modern TypeScript fundamentals & strict type safety",
            description="Understand union types, generics, type narrowing, and interface composition to prevent runtime bugs.",
            skill="TypeScript",
            estimated_time="4 hours",
            deadline="Completed",
            status="completed",
            resource_name="TypeScript Handbook",
            resource_type="Documentation",
            resource_url="https://www.typescriptlang.org/docs/handbook/intro.html",
            completed_at=datetime.utcnow()
        ),
        RoadmapTask(
            id="task-2",
            user_id="default_user",
            career_id="ai-product-engineer",
            phase_id=1,
            phase_name="Phase 1: Foundations",
            title="Study asynchronous JavaScript & Server-Sent Events (SSE)",
            description="Learn how streaming responses work from server to client with ReadableStream and fetch abort controllers.",
            skill="Asynchronous Programming",
            estimated_time="3 hours",
            deadline="Completed",
            status="completed",
            resource_name="MDN Web Docs: Streams API",
            resource_type="Documentation",
            resource_url="https://developer.mozilla.org/en-US/docs/Web/API/Streams_API",
            completed_at=datetime.utcnow()
        ),
        RoadmapTask(
            id="task-3",
            user_id="default_user",
            career_id="ai-product-engineer",
            phase_id=2,
            phase_name="Phase 2: Core Skills",
            title="Implement structured schema validation with Pydantic & Zod",
            description="Enforce deterministic schemas on model outputs to guarantee reliable UI rendering without runtime parsing errors.",
            skill="Schema Validation",
            estimated_time="25 mins",
            deadline="In 3 days",
            status="in_progress",
            resource_name="Zod TypeScript First Schema Validation",
            resource_type="Documentation",
            resource_url="https://zod.dev"
        ),
        RoadmapTask(
            id="task-4",
            user_id="default_user",
            career_id="ai-product-engineer",
            phase_id=2,
            phase_name="Phase 2: Core Skills",
            title="Build graceful UI fallback states for AI rate limits & network timeouts",
            description="Design human-friendly error banners, retry mechanisms, and non-blocking background task indicators.",
            skill="Resilient UX",
            estimated_time="2 hours",
            deadline="Next week",
            status="not_started",
            resource_name="Designing for System Recovery & Error States",
            resource_type="Interactive",
            resource_url="https://www.nngroup.com/articles/error-message-guidelines/"
        ),
        RoadmapTask(
            id="task-5",
            user_id="default_user",
            career_id="ai-product-engineer",
            phase_id=3,
            phase_name="Phase 3: Applied Projects",
            title="Develop an end-to-end Career Research Companion with vector search",
            description="Combine a clean editorial frontend with a semantic embedding index of job roles, skills, and open-access courses.",
            skill="Full-Stack AI Application",
            estimated_time="12 hours",
            deadline="End of month",
            status="not_started",
            resource_name="Project Specification & Architecture Guide",
            resource_type="Project Spec",
            resource_url="https://github.com"
        )
    ]
    for task in starter_tasks:
        if not db.query(RoadmapTask).filter(RoadmapTask.id == task.id).first():
            db.add(task)
    db.commit()

    # 5. Seed Skills (Idempotent with is_gap)
    starter_skills = [
        UserSkill(id="skill-ts", user_id="default_user", name="TypeScript & React", category="Frontend Engineering", status="practicing", hours_spent=28.0, target_hours=50.0, is_gap=False, last_practiced="Today"),
        UserSkill(id="skill-py", user_id="default_user", name="Python Fundamentals", category="Backend & Scripting", status="practicing", hours_spent=16.0, target_hours=40.0, is_gap=False, last_practiced="Yesterday"),
        UserSkill(id="skill-api", user_id="default_user", name="API Design & Streaming", category="System Architecture", status="learning", hours_spent=8.0, target_hours=30.0, is_gap=False, last_practiced="3 days ago"),
        UserSkill(id="skill-a11y", user_id="default_user", name="WCAG 2.2 Accessibility", category="Design & UX Standards", status="proficient", hours_spent=22.0, target_hours=25.0, is_gap=False, last_practiced="4 days ago"),
        UserSkill(id="skill-prompt", user_id="default_user", name="Context & Prompt Architecture", category="AI Systems", status="learning", hours_spent=10.0, target_hours=35.0, is_gap=False, last_practiced="1 week ago"),
        UserSkill(id="skill-eval", user_id="default_user", name="Vector Embeddings & RAG", category="AI Systems", status="learning", hours_spent=0.0, target_hours=20.0, is_gap=True, last_practiced="Identified gap")
    ]
    for skill in starter_skills:
        if not db.query(UserSkill).filter(UserSkill.id == skill.id).first():
            db.add(skill)
    db.commit()

    # 6. Seed Initial Chat Message (Idempotent with session_id)
    initial_msg = ChatMessage(
        id="msg-welcome",
        user_id="default_user",
        session_id="default_session",
        sender="assistant",
        text="Hello. I am NEXORA, your career mentor.\n\nYour career is a journey, and you do not need to figure everything out today. Whether you want to reflect on what path fits your strengths, structure your weekly learning, or prepare for internship applications, I am here to work through it with you step-by-step.\n\nWhere would you like to start today?",
        suggested_actions=[
            "Help me choose a career direction.",
            "What should I learn to become an AI engineer?",
            "Can you help me prepare for an internship?",
            "Let's make a realistic weekly learning plan."
        ]
    )
    if not db.query(ChatMessage).filter(ChatMessage.id == initial_msg.id).first():
        db.add(initial_msg)
    db.commit()

if __name__ == "__main__":
    db = SessionLocal()
    seed_database(db)
    db.close()
    print("Database seeding completed.")
