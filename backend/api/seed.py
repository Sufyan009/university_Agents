"""Seed the database with one university, admin user, courses, subjects, FAQs, scholarships, and admission info."""
import os
import asyncio
import uuid
from datetime import datetime

from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql+asyncpg://postgres:Pakistan%4012345@localhost:5432/Universities_Voice_Agent")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
now = datetime.utcnow()


def uid() -> uuid.UUID:
    return uuid.uuid4()


async def seed(session: AsyncSession) -> None:
    from sqlalchemy import text

    # ── IDs ──────────────────────────────────────────────────────────────────
    admin_id = uid()
    operator_id = uid()
    uni_id = uid()
    agent_cfg_id = uid()
    course_cs_id = uid()
    course_biz_id = uid()
    course_ai_id = uid()
    admission_id = uid()

    # ── 1. Admin user (no university yet) ────────────────────────────────────
    await session.execute(text("""
        INSERT INTO users (id, email, name, phone, role, is_active, password_hash, university_id, created_at, updated_at)
        VALUES (:id, :email, :name, :phone, :role, true, :pw, NULL, :ca, :ua)
        ON CONFLICT (email) DO NOTHING
    """), {
        "id": admin_id, "email": "admin@greenvalley.edu",
        "name": "Admin User", "phone": "+14843174117",
        "role": "admin", "pw": pwd_context.hash("Admin@1234"),
        "ca": now, "ua": now,
    })

    # ── 2. University ─────────────────────────────────────────────────────────
    await session.execute(text("""
        INSERT INTO universities (id, admin_id, name, description, location, contact_info, admission_office, phone, website, created_at, updated_at)
        VALUES (:id, :admin_id, :name, :desc, CAST(:loc AS JSON), CAST(:contact AS JSON), CAST(:adm_office AS JSON), :phone, :website, :ca, :ua)
        ON CONFLICT (name) DO NOTHING
    """), {
        "id": uni_id, "admin_id": admin_id,
        "name": "Green Valley University",
        "desc": "A leading institution offering world-class education in technology, business, and sciences.",
        "loc": '{"city": "Philadelphia", "state": "PA", "country": "USA", "address": "123 University Ave"}',
        "contact": '{"email": "info@greenvalley.edu", "phone": "+14843174117"}',
        "adm_office": '{"email": "admissions@greenvalley.edu", "phone": "+14843174118", "hours": "Mon-Fri 9am-5pm"}',
        "phone": "+14843174117",
        "website": "https://www.greenvalley.edu",
        "ca": now, "ua": now,
    })

    # ── 3. Link admin to university ───────────────────────────────────────────
    await session.execute(text("""
        UPDATE users SET university_id = :uni_id WHERE id = :admin_id
    """), {"uni_id": uni_id, "admin_id": admin_id})

    # ── 4. Operator user ──────────────────────────────────────────────────────
    await session.execute(text("""
        INSERT INTO users (id, email, name, phone, role, is_active, password_hash, university_id, created_at, updated_at)
        VALUES (:id, :email, :name, :phone, :role, true, :pw, :uni_id, :ca, :ua)
        ON CONFLICT (email) DO NOTHING
    """), {
        "id": operator_id, "email": "operator@greenvalley.edu",
        "name": "Operator User", "phone": "+14843174119",
        "role": "operator", "pw": pwd_context.hash("Operator@1234"),
        "uni_id": uni_id, "ca": now, "ua": now,
    })

    # ── 5. Agent config ───────────────────────────────────────────────────────
    await session.execute(text("""
        INSERT INTO agent_configs (id, university_id, agent_name, personality, greeting_message, special_instructions, voice_config, context_text, enable_admissions, enable_courses, enable_scholarships, enable_faq, created_at, updated_at)
        VALUES (:id, :uni_id, :name, :personality, :greeting, :instructions, CAST(:vc AS JSON), :ctx, true, true, true, true, :ca, :ua)
        ON CONFLICT (university_id) DO NOTHING
    """), {
        "id": agent_cfg_id, "uni_id": uni_id,
        "name": "Aria",
        "personality": "friendly and professional",
        "greeting": "Hello! Thank you for calling Green Valley University. I'm Aria, your admissions assistant. How can I help you today?",
        "instructions": "Always confirm the caller's name at the start. Speak clearly and at a moderate pace.",
        "vc": '{"voice": "alloy", "speed": 1.0}',
        "ctx": "Green Valley University is a top-ranked institution in Philadelphia, PA, known for its CS, Business, and AI programs.",
        "ca": now, "ua": now,
    })

    # ── 6. Courses ────────────────────────────────────────────────────────────
    courses = [
        {
            "id": course_cs_id, "uni_id": uni_id,
            "name": "BSc Computer Science", "degree_type": "Bachelor",
            "desc": "A comprehensive 4-year program covering algorithms, software engineering, databases, and AI.",
            "duration": "4 years",
            "fee": '{"annual": 12000, "currency": "USD", "payment_plans": ["annual", "semester"]}',
            "req": "High school diploma with Mathematics and Physics. Minimum GPA 3.0.",
        },
        {
            "id": course_biz_id, "uni_id": uni_id,
            "name": "BSc Business Administration", "degree_type": "Bachelor",
            "desc": "A 4-year program focused on management, finance, marketing, and entrepreneurship.",
            "duration": "4 years",
            "fee": '{"annual": 10000, "currency": "USD", "payment_plans": ["annual", "semester"]}',
            "req": "High school diploma. Minimum GPA 2.8.",
        },
        {
            "id": course_ai_id, "uni_id": uni_id,
            "name": "MSc Artificial Intelligence", "degree_type": "Master",
            "desc": "An advanced 2-year program in machine learning, deep learning, NLP, and AI ethics.",
            "duration": "2 years",
            "fee": '{"annual": 18000, "currency": "USD", "payment_plans": ["annual", "semester"]}',
            "req": "Bachelor's degree in CS, Engineering, or related field. Minimum GPA 3.2.",
        },
    ]
    for c in courses:
        await session.execute(text("""
            INSERT INTO courses (id, university_id, name, degree_type, description, duration, fee_structure, admission_requirements, created_at, updated_at)
            VALUES (:id, :uni_id, :name, :degree_type, :desc, :duration, CAST(:fee AS JSON), :req, :ca, :ua)
        """), {**c, "ca": now, "ua": now})

    # ── 7. Subjects ───────────────────────────────────────────────────────────
    subjects = [
        # BSc CS
        (course_cs_id, "Introduction to Programming", "Fundamentals of Python and problem-solving.", 3, None),
        (course_cs_id, "Data Structures and Algorithms", "Arrays, trees, graphs, sorting, and complexity.", 4, "Introduction to Programming"),
        (course_cs_id, "Database Systems", "Relational databases, SQL, normalization, and transactions.", 3, "Introduction to Programming"),
        # BSc Business
        (course_biz_id, "Principles of Management", "Introduction to organizational behavior and management theory.", 3, None),
        (course_biz_id, "Financial Accounting", "Basics of accounting, balance sheets, and financial statements.", 3, None),
        (course_biz_id, "Marketing Fundamentals", "Market research, branding, and digital marketing.", 3, "Principles of Management"),
        # MSc AI
        (course_ai_id, "Machine Learning", "Supervised, unsupervised learning, and model evaluation.", 4, None),
        (course_ai_id, "Deep Learning", "Neural networks, CNNs, RNNs, and transformer architectures.", 4, "Machine Learning"),
        (course_ai_id, "Natural Language Processing", "Text processing, embeddings, LLMs, and chatbot design.", 4, "Machine Learning"),
    ]
    for course_id, name, desc, credits, prereq in subjects:
        await session.execute(text("""
            INSERT INTO subjects (id, course_id, university_id, name, description, credits, prerequisites, additional_info, created_at, updated_at)
            VALUES (:id, :course_id, :uni_id, :name, :desc, :credits, :prereq, NULL, :ca, :ua)
        """), {
            "id": uid(), "course_id": course_id, "uni_id": uni_id,
            "name": name, "desc": desc, "credits": credits,
            "prereq": prereq, "ca": now, "ua": now,
        })

    # ── 8. Admission info ─────────────────────────────────────────────────────
    await session.execute(text("""
        INSERT INTO admission_info (id, university_id, criteria, eligibility, deadlines, application_process, required_documents, scholarship_info, created_at, updated_at)
        VALUES (:id, :uni_id, :criteria, :eligibility, CAST(:deadlines AS JSON), :process, CAST(:docs AS JSON), :scholarship_info, :ca, :ua)
        ON CONFLICT (university_id) DO NOTHING
    """), {
        "id": admission_id, "uni_id": uni_id,
        "criteria": "Academic performance, personal statement, and letters of recommendation.",
        "eligibility": "Open to all students who meet the minimum GPA requirements for their chosen program.",
        "deadlines": '{"fall_semester": "August 1", "spring_semester": "December 15", "summer": "April 30"}',
        "process": "1. Submit online application. 2. Upload required documents. 3. Pay application fee ($50). 4. Await admission decision within 3-4 weeks.",
        "docs": '["Official transcripts", "Personal statement (500-800 words)", "Two letters of recommendation", "Government-issued ID", "English proficiency test scores (IELTS/TOEFL) for international students"]',
        "scholarship_info": "Merit and need-based scholarships are available. Apply separately via the scholarship portal.",
        "ca": now, "ua": now,
    })

    # ── 9. Scholarships ───────────────────────────────────────────────────────
    scholarships = [
        (uid(), uni_id, None, "Merit Excellence Scholarship", "$5,000/year", "GPA 3.8+ and full-time enrollment.", "July 15"),
        (uid(), uni_id, course_cs_id, "STEM Future Leaders Grant", "$3,000/year", "Enrolled in a STEM program with GPA 3.5+.", "July 31"),
        (uid(), uni_id, None, "Need-Based Financial Aid", "Up to $8,000/year", "Demonstrated financial need. Submit FAFSA or equivalent.", "June 30"),
    ]
    for s_id, s_uni_id, s_course_id, name, amount, eligibility, deadline in scholarships:
        await session.execute(text("""
            INSERT INTO scholarships (id, university_id, course_id, name, amount, eligibility, deadline, is_active, created_at, updated_at)
            VALUES (:id, :uni_id, :course_id, :name, :amount, :eligibility, :deadline, true, :ca, :ua)
        """), {
            "id": s_id, "uni_id": s_uni_id, "course_id": s_course_id,
            "name": name, "amount": amount, "eligibility": eligibility,
            "deadline": deadline, "ca": now, "ua": now,
        })

    # ── 10. FAQs ──────────────────────────────────────────────────────────────
    faqs = [
        ("What are the application deadlines?", "Fall semester deadline is August 1st, Spring is December 15th, and Summer is April 30th.", "admissions"),
        ("How do I apply for financial aid?", "Submit your FAFSA or equivalent financial aid form by June 30th. Visit the Financial Aid office or apply online through the student portal.", "financial"),
        ("What programs does Green Valley University offer?", "We offer BSc Computer Science, BSc Business Administration, and MSc Artificial Intelligence, among other programs.", "general"),
        ("Is on-campus housing available?", "Yes, we offer on-campus dormitories for full-time students. Applications open March 1st each year on a first-come, first-served basis.", "campus life"),
        ("What English proficiency tests are accepted?", "We accept IELTS (minimum 6.5) and TOEFL iBT (minimum 80) for international applicants.", "admissions"),
    ]
    for question, answer, category in faqs:
        await session.execute(text("""
            INSERT INTO faqs (id, university_id, question, answer, category, is_active, created_at, updated_at)
            VALUES (:id, :uni_id, :question, :answer, :category, true, :ca, :ua)
        """), {
            "id": uid(), "uni_id": uni_id,
            "question": question, "answer": answer,
            "category": category, "ca": now, "ua": now,
        })

    await session.commit()
    print("✓ Seeding complete.")
    print(f"  University : Green Valley University  (id={uni_id})")
    print(f"  Admin      : admin@greenvalley.edu    / Admin@1234")
    print(f"  Operator   : operator@greenvalley.edu / Operator@1234")
    print(f"  Courses    : BSc CS, BSc Business Admin, MSc AI")
    print(f"  Subjects   : 9 total")
    print(f"  Scholarships: 3")
    print(f"  FAQs       : 5")


async def main() -> None:
    engine = create_async_engine(DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        await seed(session)
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
