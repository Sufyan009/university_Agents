"""Read-only retrieval tools. Every query is scoped to the resolved university_id,
so a caller can only ever reach their own university's data.
"""
import uuid

from livekit.agents import function_tool
from sqlalchemy import select

from config.helper import _get_session_maker
from tools.models import AdmissionInfo, Course, FAQ, Scholarship, Subject


def make_get_admission_info_tool(university_id: uuid.UUID):
    @function_tool
    async def get_admission_info() -> str:
        """Get this university's admission criteria, eligibility, deadlines, application
        process, and required documents. Use for any admissions question."""
        maker = _get_session_maker()
        async with maker() as session:
            result = await session.execute(
                select(AdmissionInfo).where(AdmissionInfo.university_id == university_id)
            )
            adm = result.scalars().first()
        if adm is None:
            return "Admission details are not available right now. I can connect you with the admissions office."

        parts: list[str] = []
        if adm.criteria:
            parts.append(f"Criteria: {adm.criteria}")
        if adm.eligibility:
            parts.append(f"Eligibility: {adm.eligibility}")
        if adm.application_process:
            parts.append(f"Application process: {adm.application_process}")
        if adm.required_documents:
            docs = ", ".join(str(d) for d in adm.required_documents)
            parts.append(f"Required documents: {docs}")
        if adm.deadlines:
            dl = "; ".join(
                f"{d.get('label', 'Deadline')}: {d.get('date', '')}" if isinstance(d, dict) else str(d)
                for d in adm.deadlines
            )
            parts.append(f"Deadlines: {dl}")
        if adm.scholarship_info:
            parts.append(f"Scholarships: {adm.scholarship_info}")
        return "\n".join(parts) if parts else "No admission details are configured yet."

    return get_admission_info


def make_list_courses_tool(university_id: uuid.UUID):
    @function_tool
    async def list_courses() -> str:
        """List the courses/programmes this university offers, with degree type and duration."""
        maker = _get_session_maker()
        async with maker() as session:
            result = await session.execute(
                select(Course).where(Course.university_id == university_id)
            )
            courses = result.scalars().all()
        if not courses:
            return "No courses are listed right now."
        lines = []
        for c in sorted(courses, key=lambda x: x.name):
            extras = ", ".join(p for p in [c.degree_type, c.duration] if p)
            lines.append(f"- {c.name}" + (f" ({extras})" if extras else ""))
        return "\n".join(lines)

    return list_courses


def make_get_course_detail_tool(university_id: uuid.UUID):
    @function_tool
    async def get_course_detail(course_name: str) -> str:
        """Get full detail for one course by name: description, duration, fees, entry
        requirements, and its subjects/modules. Match the caller's wording to the closest course."""
        maker = _get_session_maker()
        async with maker() as session:
            result = await session.execute(
                select(Course).where(
                    Course.university_id == university_id,
                    Course.name.ilike(f"%{course_name}%"),
                )
            )
            course = result.scalars().first()
            if course is None:
                return f"I couldn't find a course matching '{course_name}'. Would you like me to list our courses?"

            subj_result = await session.execute(
                select(Subject).where(Subject.course_id == course.id)
            )
            subjects = subj_result.scalars().all()

        parts = [f"{course.name}"]
        if course.degree_type:
            parts.append(f"Degree: {course.degree_type}")
        if course.duration:
            parts.append(f"Duration: {course.duration}")
        if course.description:
            parts.append(f"About: {course.description}")
        if course.admission_requirements:
            parts.append(f"Entry requirements: {course.admission_requirements}")
        if course.fee_structure:
            fs = course.fee_structure
            if isinstance(fs, dict):
                fee_bits = ", ".join(f"{k}: {v}" for k, v in fs.items())
                parts.append(f"Fees: {fee_bits}")
            else:
                parts.append(f"Fees: {fs}")
        if subjects:
            subj_names = ", ".join(s.name for s in subjects)
            parts.append(f"Subjects: {subj_names}")
        return "\n".join(parts)

    return get_course_detail


def make_list_subjects_tool(university_id: uuid.UUID):
    @function_tool
    async def list_subjects(course_name: str) -> str:
        """List the subjects/modules within a named course, including credits and prerequisites."""
        maker = _get_session_maker()
        async with maker() as session:
            course_result = await session.execute(
                select(Course).where(
                    Course.university_id == university_id,
                    Course.name.ilike(f"%{course_name}%"),
                )
            )
            course = course_result.scalars().first()
            if course is None:
                return f"I couldn't find a course matching '{course_name}'."
            subj_result = await session.execute(
                select(Subject).where(Subject.course_id == course.id)
            )
            subjects = subj_result.scalars().all()
        if not subjects:
            return f"No subjects are listed for {course.name} yet."
        lines = []
        for s in subjects:
            bits = []
            if s.credits is not None:
                bits.append(f"{s.credits} credits")
            if s.prerequisites:
                bits.append(f"prereq: {s.prerequisites}")
            suffix = f" ({'; '.join(bits)})" if bits else ""
            lines.append(f"- {s.name}{suffix}")
        return "\n".join(lines)

    return list_subjects


def make_list_scholarships_tool(university_id: uuid.UUID):
    @function_tool
    async def list_scholarships() -> str:
        """List active scholarships at this university with amounts, eligibility, and deadlines."""
        maker = _get_session_maker()
        async with maker() as session:
            result = await session.execute(
                select(Scholarship).where(
                    Scholarship.university_id == university_id,
                    Scholarship.is_active == True,  # noqa: E712
                )
            )
            scholarships = result.scalars().all()
        if not scholarships:
            return "There are no scholarships listed right now."
        lines = []
        for s in scholarships:
            bits = [s.name]
            if s.amount:
                bits.append(f"amount: {s.amount}")
            if s.eligibility:
                bits.append(f"eligibility: {s.eligibility}")
            if s.deadline:
                bits.append(f"deadline: {s.deadline}")
            lines.append("- " + ", ".join(bits))
        return "\n".join(lines)

    return list_scholarships


def make_search_faqs_tool(university_id: uuid.UUID):
    @function_tool
    async def search_faqs(query: str) -> str:
        """Search this university's FAQs (campus info, student services, general questions)
        for answers relevant to the caller's question."""
        maker = _get_session_maker()
        async with maker() as session:
            result = await session.execute(
                select(FAQ).where(
                    FAQ.university_id == university_id,
                    FAQ.is_active == True,  # noqa: E712
                    FAQ.question.ilike(f"%{query}%"),
                ).limit(5)
            )
            faqs = result.scalars().all()
            if not faqs:
                # fall back to returning a few general FAQs
                result = await session.execute(
                    select(FAQ).where(
                        FAQ.university_id == university_id,
                        FAQ.is_active == True,  # noqa: E712
                    ).limit(5)
                )
                faqs = result.scalars().all()
        if not faqs:
            return "I don't have information on that. I can connect you with student services."
        return "\n\n".join(f"Q: {f.question}\nA: {f.answer}" for f in faqs)

    return search_faqs
