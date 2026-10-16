from sqlalchemy.orm import Session
from datetime import datetime
from .database import engine, Base, SessionLocal, migrate_database
from .models import UserProfile, CareerPath, SavedCareer, RoadmapTask, UserSkill, ChatMessage

def seed_database(db: Session):
    # Ensure tables and migrations exist safely
    migrate_database()

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
    for c in careers:
        if not db.query(CareerPath).filter(CareerPath.id == c.id).first():
            db.add(c)
    db.commit()

    # 2. Seed Default User Profile
    user = db.query(UserProfile).filter(UserProfile.id == "default_user").first()
    if not user:
        user = UserProfile(
            id="default_user",
            name="Alex Morgan",
            study_status="Third-year CS & HCI Student",
            target_career_id="ai-product-engineer",
            interests=["Human-Centered AI", "Web Architecture", "Design Systems", "Interface Ergonomics"],
            current_skills=["TypeScript", "React", "Basic Python", "Semantic HTML"],
            primary_goal="Secure a Summer 2027 AI Product Engineering Internship",
            weekly_hours=8,
            onboarding_completed=True
        )
        db.add(user)
        db.commit()

    # 3. Seed Saved Careers (Idempotent)
    starter_saved = [
        SavedCareer(id="sc-1", user_id="default_user", career_id="ai-product-engineer"),
        SavedCareer(id="sc-2", user_id="default_user", career_id="product-designer")
    ]
    for sc in starter_saved:
        if not db.query(SavedCareer).filter(SavedCareer.user_id == sc.user_id, SavedCareer.career_id == sc.career_id).first():
            db.add(sc)
    db.commit()

    # 4. Seed Roadmap Tasks (Idempotent with career_id and deadline)
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
        text="Hello Alex. I am your career mentor.\n\nYour career is a journey, and you do not need to figure everything out today. Whether you want to reflect on what path fits your strengths, structure your weekly learning, or prepare for internship applications, I am here to work through it with you step-by-step.\n\nWhere would you like to start today?",
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
