"""Seed San Diego State University data scraped from sdsu.edu."""
import os
import asyncio
import uuid
from datetime import datetime

import bcrypt
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql+asyncpg://postgres:Pakistan%4012345@localhost:5432/Universities_Voice_Agent")

now = datetime.utcnow()


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def uid() -> uuid.UUID:
    return uuid.uuid4()


async def seed(session: AsyncSession) -> None:
    from sqlalchemy import text

    # Skip if already seeded
    result = await session.execute(text("SELECT id FROM universities WHERE name = 'San Diego State University'"))
    existing = result.fetchone()
    if existing:
        print("SDSU already seeded. Skipping.")
        return

    # ── IDs ───────────────────────────────────────────────────────────────────
    admin_id        = uid()
    uni_id          = uid()
    agent_cfg_id    = uid()
    course_bs_cs_id = uid()
    course_bs_biz_id= uid()
    course_ms_cs_id = uid()
    course_ms_ai_id = uid()
    course_mba_id   = uid()
    admission_id    = uid()

    # ── 1. Admin / owner user ─────────────────────────────────────────────────
    await session.execute(text("""
        INSERT INTO users (id, email, name, phone, role, is_active, password_hash, university_id, created_at, updated_at)
        VALUES (:id, :email, :name, :phone, :role, true, :pw, NULL, :ca, :ua)
        ON CONFLICT (email) DO NOTHING
    """), {
        "id": admin_id,
        "email": "mohsin@sdsu.com",
        "name": "Mohsin Ali",
        "phone": "+14843174117",
        "role": "owner",
        "pw": hash_password("Admin@123"),
        "ca": now, "ua": now,
    })

    # ── 2. University ─────────────────────────────────────────────────────────
    await session.execute(text("""
        INSERT INTO universities (
            id, admin_id, name, description, location, contact_info,
            admission_office, phone, website, created_at, updated_at
        )
        VALUES (
            :id, :admin_id, :name, :desc, CAST(:loc AS JSON), CAST(:contact AS JSON),
            CAST(:adm_office AS JSON), :phone, :website, :ca, :ua
        )
        ON CONFLICT (name) DO NOTHING
    """), {
        "id": uni_id,
        "admin_id": admin_id,
        "name": "San Diego State University",
        "desc": (
            "San Diego State University (SDSU) is a nationally ranked public research university "
            "located in San Diego, California. Founded over 128 years ago, SDSU offers more than "
            "220 undergraduate and graduate degree programs across eight colleges. Designated as an "
            "R1 research institution, SDSU is both a Hispanic-Serving Institution and an Asian American "
            "Native American Pacific Islander-Serving Institution. With 500,000+ living alumni, "
            "$230 million in annual research funding, and a mid-career salary average of $127,700, "
            "SDSU delivers exceptional academic and career outcomes rooted in one of the nation's most "
            "dynamic and diverse regions."
        ),
        "loc": (
            '{"city": "San Diego", "state": "CA", "country": "USA", '
            '"address": "5500 Campanile Drive, San Diego, CA 92182"}'
        ),
        "contact": (
            '{"email": "info@sdsu.edu", "phone": "619-594-5200"}'
        ),
        "adm_office": (
            '{"email": "admissions@sdsu.edu", "phone": "619-594-6336", '
            '"address": "5500 Campanile Drive, San Diego, CA 92182-7455", '
            '"hours": "Mon-Fri 9am-2:30pm PDT (in-person) | Mon-Fri 2-4pm PDT (virtual)"}'
        ),
        "phone": "+14843174117",
        "website": "https://www.sdsu.edu/",
        "ca": now, "ua": now,
    })

    # ── 3. Link admin to university ───────────────────────────────────────────
    await session.execute(text("""
        UPDATE users SET university_id = :uni_id WHERE id = :admin_id
    """), {"uni_id": uni_id, "admin_id": admin_id})

    # ── 4. Agent config ───────────────────────────────────────────────────────
    await session.execute(text("""
        INSERT INTO agent_configs (
            id, university_id, agent_name, personality, greeting_message,
            special_instructions, voice_config, context_text,
            enable_admissions, enable_courses, enable_scholarships, enable_faq,
            created_at, updated_at
        )
        VALUES (
            :id, :uni_id, :name, :personality, :greeting, :instructions,
            CAST(:vc AS JSON), :ctx, true, true, true, true, :ca, :ua
        )
        ON CONFLICT (university_id) DO NOTHING
    """), {
        "id": agent_cfg_id,
        "uni_id": uni_id,
        "name": "Aztec Assist",
        "personality": "friendly, knowledgeable, and encouraging",
        "greeting": (
            "Thank you for calling San Diego State University! I'm Aztec Assist, "
            "your SDSU admissions guide. Whether you have questions about programs, "
            "deadlines, or financial aid — I'm here to help. How can I assist you today?"
        ),
        "instructions": (
            "Always mention that SDSU no longer requires SAT/ACT scores for first-year admission. "
            "Remind callers about the Cal State Apply platform. "
            "If a caller asks about costs, quote approximate figures and direct them to the Bursar's Office."
        ),
        "vc": '{"voice": "alloy", "speed": 1.0}',
        "ctx": (
            "SDSU is a top-ranked public research university in San Diego, CA with 220+ programs "
            "across eight colleges. It is test-optional, Hispanic-Serving, and ranked among the "
            "Top 50 Best Value Public Colleges. Applications go through Cal State Apply."
        ),
        "ca": now, "ua": now,
    })

    # ── 5. Courses ────────────────────────────────────────────────────────────
    courses = [
        {
            "id": course_bs_cs_id,
            "name": "B.S. Computer Science",
            "degree_type": "Bachelor",
            "desc": (
                "A comprehensive undergraduate program covering software engineering, algorithms, "
                "data structures, databases, AI, cybersecurity, and computer networks. Students gain "
                "hands-on experience through research labs and industry internships. Graduates are "
                "prepared for careers at top tech companies or graduate study."
            ),
            "duration": "4 years",
            "fee": (
                '{"in_state_annual": 10160, "out_of_state_annual": 22640, "currency": "USD", '
                '"note": "Includes tuition and mandatory campus fees. Subject to CSU Board approval.", '
                '"payment_plans": ["annual", "semester"]}'
            ),
            "req": (
                "High school diploma with A-G coursework completed (grades C- or higher). "
                "Minimum GPA 2.5 (CA residents) or 3.0 (non-residents). Average admitted GPA: 3.9. "
                "No SAT/ACT required."
            ),
        },
        {
            "id": course_bs_biz_id,
            "name": "B.S. Business Administration",
            "degree_type": "Bachelor",
            "desc": (
                "Offered through the Fowler College of Business, this program prepares students in "
                "accounting, finance, management, marketing, and management information systems. "
                "Ranked #32 for part-time MBA (U.S. News). Students benefit from strong industry ties "
                "in San Diego's thriving business ecosystem."
            ),
            "duration": "4 years",
            "fee": (
                '{"in_state_annual": 10160, "out_of_state_annual": 22640, "currency": "USD", '
                '"note": "Includes tuition and mandatory campus fees.", '
                '"payment_plans": ["annual", "semester"]}'
            ),
            "req": (
                "High school diploma with A-G coursework. Minimum GPA 2.5 (CA residents) or 3.0 (non-residents). "
                "Average admitted GPA: 3.9. No SAT/ACT required."
            ),
        },
        {
            "id": course_ms_cs_id,
            "name": "M.S. Computer Science",
            "degree_type": "Master",
            "desc": (
                "An advanced graduate program offering specializations in machine learning, cybersecurity, "
                "autonomous systems, robotics, computer networks, and simulation. Faculty have industry "
                "experience at Google, Microsoft, and Adobe. Students complete a thesis or comprehensive exam."
            ),
            "duration": "2 years",
            "fee": (
                '{"in_state_annual": 9360, "out_of_state_annual": 16560, "currency": "USD", '
                '"note": "Graduate tuition rates. Subject to change.", '
                '"payment_plans": ["annual", "semester"]}'
            ),
            "req": (
                "Accredited bachelor's degree in Computer Science or closely related field. "
                "Minimum GPA 3.0 in last 60 units. Individual program may require GRE scores. "
                "Apply via Cal State Apply."
            ),
        },
        {
            "id": course_ms_ai_id,
            "name": "M.S. Artificial Intelligence and Technology",
            "degree_type": "Master",
            "desc": (
                "A newly launched graduate program in the Department of Computer Science covering "
                "deep learning, natural language processing, computer vision, autonomous systems, "
                "and AI ethics. Designed for students and professionals seeking to lead in the "
                "rapidly growing AI industry."
            ),
            "duration": "2 years",
            "fee": (
                '{"in_state_annual": 9360, "out_of_state_annual": 16560, "currency": "USD", '
                '"note": "Graduate tuition rates. Subject to change.", '
                '"payment_plans": ["annual", "semester"]}'
            ),
            "req": (
                "Accredited bachelor's degree in CS, Engineering, Mathematics, or related field. "
                "Minimum GPA 3.0. Programming proficiency in Python required."
            ),
        },
        {
            "id": course_mba_id,
            "name": "Master of Business Administration (MBA)",
            "degree_type": "Master",
            "desc": (
                "The Fowler College of Business MBA is ranked #32 nationally for part-time MBA at public "
                "universities (U.S. News). Offered in standard and Sports MBA tracks, the program develops "
                "leadership, strategic thinking, and business acumen. Available full-time, part-time, "
                "and online formats."
            ),
            "duration": "2 years (full-time) / 3 years (part-time)",
            "fee": (
                '{"in_state_annual": 11500, "out_of_state_annual": 20000, "currency": "USD", '
                '"note": "MBA program fees. Subject to change.", '
                '"payment_plans": ["annual", "semester"]}'
            ),
            "req": (
                "Accredited bachelor's degree. Minimum 2 years work experience recommended. "
                "GMAT or GRE scores (program-specific requirements). Letters of recommendation and "
                "personal statement required."
            ),
        },
    ]
    for c in courses:
        await session.execute(text("""
            INSERT INTO courses (
                id, university_id, name, degree_type, description, duration,
                fee_structure, admission_requirements, created_at, updated_at
            )
            VALUES (
                :id, :uni_id, :name, :degree_type, :desc, :duration,
                CAST(:fee AS JSON), :req, :ca, :ua
            )
        """), {**c, "uni_id": uni_id, "ca": now, "ua": now})

    # ── 6. Subjects ───────────────────────────────────────────────────────────
    subjects = [
        # B.S. Computer Science
        (course_bs_cs_id, "Introduction to Computer Science",
         "Foundations of programming using Python; problem-solving, control flow, data types, and functions.", 3, None),
        (course_bs_cs_id, "Data Structures",
         "Arrays, linked lists, stacks, queues, trees, hash tables, and graphs with algorithmic complexity analysis.", 3,
         "Introduction to Computer Science"),
        (course_bs_cs_id, "Algorithms",
         "Sorting, searching, dynamic programming, greedy algorithms, graph traversal, and NP-completeness.", 3,
         "Data Structures"),
        (course_bs_cs_id, "Software Engineering",
         "Software development lifecycle, Agile methodology, version control, testing, and design patterns.", 3,
         "Data Structures"),
        (course_bs_cs_id, "Database Management Systems",
         "Relational model, SQL, normalization, indexing, transactions, and introduction to NoSQL databases.", 3,
         "Data Structures"),

        # B.S. Business Administration
        (course_bs_biz_id, "Principles of Management",
         "Fundamentals of organizational behavior, planning, organizing, leading, and controlling.", 3, None),
        (course_bs_biz_id, "Financial Accounting",
         "Accounting cycle, financial statements, assets, liabilities, equity, and basic GAAP principles.", 3, None),
        (course_bs_biz_id, "Marketing Management",
         "Market segmentation, consumer behavior, branding, digital marketing, and marketing strategy.", 3,
         "Principles of Management"),
        (course_bs_biz_id, "Business Statistics",
         "Descriptive statistics, probability, hypothesis testing, regression analysis, and data-driven decisions.", 3,
         "Principles of Management"),

        # M.S. Computer Science
        (course_ms_cs_id, "Advanced Algorithms",
         "Complexity theory, approximation algorithms, randomized algorithms, and advanced graph algorithms.", 4, None),
        (course_ms_cs_id, "Machine Learning",
         "Supervised/unsupervised learning, SVMs, decision trees, neural networks, model evaluation, and feature engineering.", 4,
         "Advanced Algorithms"),
        (course_ms_cs_id, "Computer Networks",
         "TCP/IP stack, routing protocols, network security, SDN, and wireless networks.", 3, None),
        (course_ms_cs_id, "Cybersecurity",
         "Threat modeling, cryptography, network security, penetration testing, and secure software design.", 3,
         "Computer Networks"),

        # M.S. Artificial Intelligence and Technology
        (course_ms_ai_id, "Deep Learning",
         "Neural network architectures — CNNs, RNNs, transformers, GANs, and training at scale.", 4, None),
        (course_ms_ai_id, "Natural Language Processing",
         "Tokenization, word embeddings, attention mechanisms, large language models, and NLP pipelines.", 4,
         "Deep Learning"),
        (course_ms_ai_id, "Computer Vision",
         "Image classification, object detection, segmentation, and generative models for visual data.", 4,
         "Deep Learning"),
        (course_ms_ai_id, "AI Ethics and Policy",
         "Fairness, accountability, transparency, bias in AI systems, and regulatory frameworks.", 3, None),

        # MBA
        (course_mba_id, "Strategic Management",
         "Competitive analysis, business strategy formulation, execution, and case-study methodology.", 3, None),
        (course_mba_id, "Corporate Finance",
         "Capital structure, valuation, financial modeling, M&A, and investment decision-making.", 3, None),
        (course_mba_id, "Marketing Strategy",
         "Brand management, pricing strategy, digital marketing, and go-to-market planning.", 3,
         "Strategic Management"),
        (course_mba_id, "Organizational Behavior",
         "Leadership styles, team dynamics, motivation, organizational culture, and change management.", 3,
         "Strategic Management"),
    ]
    for course_id, name, desc, credits, prereq in subjects:
        await session.execute(text("""
            INSERT INTO subjects (
                id, course_id, university_id, name, description,
                credits, prerequisites, additional_info, created_at, updated_at
            )
            VALUES (
                :id, :course_id, :uni_id, :name, :desc,
                :credits, :prereq, NULL, :ca, :ua
            )
        """), {
            "id": uid(), "course_id": course_id, "uni_id": uni_id,
            "name": name, "desc": desc, "credits": credits,
            "prereq": prereq, "ca": now, "ua": now,
        })

    # ── 7. Admission info ─────────────────────────────────────────────────────
    await session.execute(text("""
        INSERT INTO admission_info (
            id, university_id, criteria, eligibility, deadlines,
            application_process, required_documents, scholarship_info,
            created_at, updated_at
        )
        VALUES (
            :id, :uni_id, :criteria, :eligibility, CAST(:deadlines AS JSON),
            :process, CAST(:docs AS JSON), :scholarship_info, :ca, :ua
        )
        ON CONFLICT (university_id) DO NOTHING
    """), {
        "id": admission_id,
        "uni_id": uni_id,
        "criteria": (
            "Completion of A-G college preparatory coursework (15-unit pattern) with grades of C- or higher. "
            "Minimum GPA of 2.5 for California residents and 3.0 for non-residents. "
            "Average GPA of admitted students is 3.9. "
            "SAT/ACT scores are NOT required for first-year admission eligibility."
        ),
        "eligibility": (
            "Open to all students who have earned or will earn an accredited high school diploma. "
            "Graduate applicants must hold an accredited bachelor's degree. "
            "International students must provide English proficiency scores (TOEFL/IELTS)."
        ),
        "deadlines": (
            '{"fall_semester": "October 1 – December 1 (Cal State Apply window)", '
            '"spring_semester": "August 1–31 (select graduate programs only)", '
            '"graduate_fall": "October 1, 2025 (opens) — deadline varies by program", '
            '"application_fee": "$70 nonrefundable filing fee"}'
        ),
        "process": (
            "1. Create an account on Cal State Apply (calstate.edu/apply). "
            "2. Select San Diego State University and your intended major. "
            "3. Complete the application form — report coursework, grades, and citizenship status. "
            "4. Pay the $70 nonrefundable application filing fee. "
            "5. Submit self-reported unofficial transcripts. "
            "6. Await admission decision (official transcripts requested only after admission). "
            "Note: Any misreporting or omissions will jeopardize your admission status."
        ),
        "docs": (
            '["Self-reported unofficial transcripts", '
            '"Official transcripts (requested after admission only)", '
            '"Personal statement", '
            '"Letters of recommendation (graduate programs)", '
            '"English proficiency scores — TOEFL or IELTS (international applicants)", '
            '"Government-issued photo ID", '
            '"$70 application filing fee"]'
        ),
        "scholarship_info": (
            "Merit and need-based scholarships are available through the SDSU Scholarship Office and "
            "individual colleges. Students are encouraged to apply early through the SDSU Scholarship Portal "
            "and submit a FAFSA or California Dream Act Application for need-based aid."
        ),
        "ca": now, "ua": now,
    })

    # ── 8. Scholarships ───────────────────────────────────────────────────────
    scholarships = [
        (
            uid(), uni_id, None,
            "SDSU Presidential Scholarship",
            "$5,000/year (renewable for 4 years)",
            "Incoming first-year students with a GPA of 3.9 or higher and demonstrated leadership. Full-time enrollment required.",
            "January 31",
        ),
        (
            uid(), uni_id, course_bs_cs_id,
            "SDSU STEM Excellence Award",
            "$3,500/year",
            "Enrolled in a STEM degree program with minimum GPA 3.5. Priority given to underrepresented groups in STEM.",
            "February 28",
        ),
        (
            uid(), uni_id, None,
            "SDSU Need-Based Financial Aid Grant",
            "Up to $8,000/year",
            "Demonstrated financial need. Must submit FAFSA or California Dream Act Application by the priority deadline.",
            "March 2",
        ),
        (
            uid(), uni_id, course_mba_id,
            "Fowler College of Business MBA Fellowship",
            "$4,000/year",
            "Incoming MBA students with a GMAT score of 600+ or GRE equivalent. Full-time enrollment required.",
            "April 15",
        ),
        (
            uid(), uni_id, None,
            "Aztec Diversity Scholarship",
            "$2,500/year",
            "Open to all students who contribute to campus diversity and have a minimum GPA of 3.0. Essay required.",
            "March 15",
        ),
    ]
    for s_id, s_uni_id, s_course_id, name, amount, eligibility, deadline in scholarships:
        await session.execute(text("""
            INSERT INTO scholarships (
                id, university_id, course_id, name, amount,
                eligibility, deadline, is_active, created_at, updated_at
            )
            VALUES (
                :id, :uni_id, :course_id, :name, :amount,
                :eligibility, :deadline, true, :ca, :ua
            )
        """), {
            "id": s_id, "uni_id": s_uni_id, "course_id": s_course_id,
            "name": name, "amount": amount, "eligibility": eligibility,
            "deadline": deadline, "ca": now, "ua": now,
        })

    # ── 9. FAQs ───────────────────────────────────────────────────────────────
    faqs = [
        (
            "What is the application deadline for fall semester?",
            "The Cal State Apply application window for fall admission is October 1 through December 1. "
            "We strongly recommend applying early as some programs fill up quickly.",
            "admissions",
        ),
        (
            "Does SDSU require SAT or ACT scores?",
            "No. SDSU no longer uses SAT or ACT scores to determine first-year admission eligibility. "
            "You may still submit scores voluntarily for course placement purposes.",
            "admissions",
        ),
        (
            "What GPA do I need to be admitted?",
            "California residents need a minimum GPA of 2.5, and non-residents need a minimum of 3.0 in A-G coursework. "
            "The average GPA of admitted students is 3.9, so a competitive GPA is recommended.",
            "admissions",
        ),
        (
            "How do I apply to SDSU?",
            "Applications are submitted through Cal State Apply at calstate.edu/apply. Create an account, "
            "select SDSU and your intended major, complete the form, and pay the $70 filing fee.",
            "admissions",
        ),
        (
            "What programs does SDSU offer?",
            "SDSU offers 97 bachelor's degrees, 115 master's programs, and 30 doctoral programs across "
            "eight colleges including Engineering, Business, Computer Science, Education, Sciences, "
            "Arts and Letters, Health and Human Services, and Professional Studies.",
            "academics",
        ),
        (
            "How much does it cost to attend SDSU?",
            "Approximate annual costs for undergraduate California residents are around $10,160 in tuition "
            "and fees, plus room, board, and personal expenses. Out-of-state students pay approximately "
            "$22,640. Note that the CSU Board of Trustees has approved annual 6% tuition increases through 2029. "
            "Visit the Bursar's Office website for exact current figures.",
            "financial",
        ),
        (
            "Is financial aid available?",
            "Yes. SDSU offers merit-based scholarships, need-based grants, work-study, and loans. "
            "Submit your FAFSA or California Dream Act Application as early as possible. "
            "The priority deadline for need-based aid is typically March 2.",
            "financial",
        ),
        (
            "How do I contact the Admissions Office?",
            "You can reach the SDSU Office of Admissions by phone at 619-594-6336, Monday through Friday "
            "from 9 a.m. to 11 a.m. PDT. In-person hours are Monday–Friday 9 a.m.–2:30 p.m. at the "
            "Prospective Student Center, 5500 Campanile Drive, San Diego, CA 92182.",
            "contact",
        ),
        (
            "Does SDSU offer programs for international students?",
            "Yes. SDSU welcomes international students for undergraduate, graduate, and transfer programs. "
            "International applicants must provide English proficiency scores — TOEFL iBT minimum 61 "
            "for undergraduate, or IELTS minimum 6.0. Visit admissions.sdsu.edu/international for details.",
            "admissions",
        ),
        (
            "What research opportunities are available at SDSU?",
            "SDSU is a designated R1 research university with $230 million in annual research funding and "
            "dozens of research centers. Students can engage in research in areas like AI, cybersecurity, "
            "autonomous vehicles, public health, and environmental science. "
            "Contact your department or the Office of Research for student opportunities.",
            "academics",
        ),
    ]
    for question, answer, category in faqs:
        await session.execute(text("""
            INSERT INTO faqs (
                id, university_id, question, answer,
                category, is_active, created_at, updated_at
            )
            VALUES (
                :id, :uni_id, :question, :answer,
                :category, true, :ca, :ua
            )
        """), {
            "id": uid(), "uni_id": uni_id,
            "question": question, "answer": answer,
            "category": category, "ca": now, "ua": now,
        })

    await session.commit()

    print("SDSU seeding complete.")
    print(f"  University  : San Diego State University  (id={uni_id})")
    print(f"  Admin/Owner : mohsin@sdsu.com / Admin@123")
    print(f"  Phone       : +14843174117")
    print(f"  Courses     : B.S. CS, B.S. Business Admin, M.S. CS, M.S. AI & Tech, MBA")
    print(f"  Subjects    : 21 total")
    print(f"  Scholarships: 5")
    print(f"  FAQs        : 10")


async def main() -> None:
    engine = create_async_engine(DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        await seed(session)
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
