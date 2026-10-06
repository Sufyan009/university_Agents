"""Initial schema — all university platform tables.

Revision ID: 0001
Revises:
Create Date: 2026-06-16
"""
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql as pg
from alembic import op

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # users (FK to universities added after universities exists — circular dep)
    op.create_table(
        "users",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String, nullable=False),
        sa.Column("name", sa.String, nullable=True),
        sa.Column("phone", sa.String, nullable=True),
        sa.Column("role", sa.String(20), nullable=False, server_default="operator"),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column("password_hash", sa.String, nullable=False),
        sa.Column("university_id", pg.UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=False),
        sa.Column("updated_at", sa.DateTime, nullable=False),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "universities",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True),
        sa.Column("admin_id", pg.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("name", sa.String, nullable=False),
        sa.Column("description", sa.String, nullable=True),
        sa.Column("location", pg.JSON, nullable=True),
        sa.Column("contact_info", pg.JSON, nullable=True),
        sa.Column("admission_office", pg.JSON, nullable=True),
        sa.Column("phone", sa.String, nullable=True),
        sa.Column("website", sa.String, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=False),
        sa.Column("updated_at", sa.DateTime, nullable=False),
    )
    op.create_index("ix_universities_name", "universities", ["name"], unique=True)
    op.create_index("ix_universities_phone", "universities", ["phone"], unique=True)

    op.create_foreign_key(
        "fk_users_university_id", "users", "universities", ["university_id"], ["id"]
    )

    op.create_table(
        "role_permissions",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "university_id", pg.UUID(as_uuid=True),
            sa.ForeignKey("universities.id", ondelete="CASCADE"), nullable=False,
        ),
        sa.Column("role", sa.String(20), nullable=False),
        sa.Column("permission", sa.String(50), nullable=False),
        sa.Column("enabled", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.UniqueConstraint("university_id", "role", "permission", name="uq_role_permissions"),
    )
    op.create_index("ix_role_permissions_university_id", "role_permissions", ["university_id"])

    op.create_table(
        "agent_configs",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "university_id", pg.UUID(as_uuid=True),
            sa.ForeignKey("universities.id"), nullable=False, unique=True,
        ),
        sa.Column("agent_name", sa.String, nullable=False, server_default="Assistant"),
        sa.Column("personality", sa.String, nullable=False, server_default="friendly"),
        sa.Column("greeting_message", sa.String, nullable=False,
                  server_default="Hello! Thanks for calling. How can I help with admissions, courses, or fees?"),
        sa.Column("special_instructions", sa.String, nullable=True),
        sa.Column("voice_config", pg.JSON, nullable=False, server_default="{}"),
        sa.Column("context_text", sa.String, nullable=True),
        sa.Column("enable_admissions", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column("enable_courses", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column("enable_scholarships", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column("enable_faq", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime, nullable=False),
        sa.Column("updated_at", sa.DateTime, nullable=False),
    )

    op.create_table(
        "courses",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True),
        sa.Column("university_id", pg.UUID(as_uuid=True), sa.ForeignKey("universities.id"), nullable=False),
        sa.Column("name", sa.String, nullable=False),
        sa.Column("degree_type", sa.String, nullable=True),
        sa.Column("description", sa.String, nullable=True),
        sa.Column("duration", sa.String, nullable=True),
        sa.Column("fee_structure", pg.JSON, nullable=True),
        sa.Column("admission_requirements", sa.String, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=False),
        sa.Column("updated_at", sa.DateTime, nullable=False),
    )
    op.create_index("ix_courses_university_id", "courses", ["university_id"])
    op.create_index("ix_courses_degree_type", "courses", ["degree_type"])

    op.create_table(
        "subjects",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True),
        sa.Column("course_id", pg.UUID(as_uuid=True), sa.ForeignKey("courses.id"), nullable=False),
        sa.Column("university_id", pg.UUID(as_uuid=True), sa.ForeignKey("universities.id"), nullable=False),
        sa.Column("name", sa.String, nullable=False),
        sa.Column("description", sa.String, nullable=True),
        sa.Column("credits", sa.Integer, nullable=True),
        sa.Column("prerequisites", sa.String, nullable=True),
        sa.Column("additional_info", sa.String, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=False),
        sa.Column("updated_at", sa.DateTime, nullable=False),
    )
    op.create_index("ix_subjects_course_id", "subjects", ["course_id"])
    op.create_index("ix_subjects_university_id", "subjects", ["university_id"])

    op.create_table(
        "admission_info",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True),
        sa.Column("university_id", pg.UUID(as_uuid=True), sa.ForeignKey("universities.id"), nullable=False, unique=True),
        sa.Column("criteria", sa.String, nullable=True),
        sa.Column("eligibility", sa.String, nullable=True),
        sa.Column("deadlines", pg.JSON, nullable=True),
        sa.Column("application_process", sa.String, nullable=True),
        sa.Column("required_documents", pg.JSON, nullable=True),
        sa.Column("scholarship_info", sa.String, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=False),
        sa.Column("updated_at", sa.DateTime, nullable=False),
    )

    op.create_table(
        "scholarships",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True),
        sa.Column("university_id", pg.UUID(as_uuid=True), sa.ForeignKey("universities.id"), nullable=False),
        sa.Column("course_id", pg.UUID(as_uuid=True), sa.ForeignKey("courses.id"), nullable=True),
        sa.Column("name", sa.String, nullable=False),
        sa.Column("amount", sa.String, nullable=True),
        sa.Column("eligibility", sa.String, nullable=True),
        sa.Column("deadline", sa.String, nullable=True),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime, nullable=False),
        sa.Column("updated_at", sa.DateTime, nullable=False),
    )
    op.create_index("ix_scholarships_university_id", "scholarships", ["university_id"])

    op.create_table(
        "faqs",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True),
        sa.Column("university_id", pg.UUID(as_uuid=True), sa.ForeignKey("universities.id"), nullable=False),
        sa.Column("question", sa.String, nullable=False),
        sa.Column("answer", sa.String, nullable=False),
        sa.Column("category", sa.String, nullable=True),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime, nullable=False),
        sa.Column("updated_at", sa.DateTime, nullable=False),
    )
    op.create_index("ix_faqs_university_id", "faqs", ["university_id"])

    op.create_table(
        "call_sessions",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True),
        sa.Column("university_id", pg.UUID(as_uuid=True), sa.ForeignKey("universities.id"), nullable=False),
        sa.Column("livekit_room_id", sa.String, nullable=False),
        sa.Column("agent_type", sa.String, nullable=False, server_default="main"),
        sa.Column("status", sa.String, nullable=False, server_default="active"),
        sa.Column("caller_identity", sa.String, nullable=True),
        sa.Column("started_at", sa.DateTime, nullable=False),
        sa.Column("ended_at", sa.DateTime, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=False),
        sa.Column("updated_at", sa.DateTime, nullable=False),
    )
    op.create_index("ix_call_sessions_university_id", "call_sessions", ["university_id"])
    op.create_index("ix_call_sessions_livekit_room_id", "call_sessions", ["livekit_room_id"])
    op.create_index("ix_call_sessions_status", "call_sessions", ["status"])

    op.create_table(
        "call_messages",
        sa.Column("id", pg.UUID(as_uuid=True), primary_key=True),
        sa.Column("call_session_id", pg.UUID(as_uuid=True), sa.ForeignKey("call_sessions.id"), nullable=False),
        sa.Column("role", sa.String, nullable=False),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("sequence", sa.Integer, nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime, nullable=False),
    )
    op.create_index("ix_call_messages_call_session_id", "call_messages", ["call_session_id"])


def downgrade() -> None:
    op.drop_index("ix_call_messages_call_session_id", table_name="call_messages")
    op.drop_table("call_messages")
    op.drop_index("ix_call_sessions_status", table_name="call_sessions")
    op.drop_index("ix_call_sessions_livekit_room_id", table_name="call_sessions")
    op.drop_index("ix_call_sessions_university_id", table_name="call_sessions")
    op.drop_table("call_sessions")
    op.drop_index("ix_faqs_university_id", table_name="faqs")
    op.drop_table("faqs")
    op.drop_index("ix_scholarships_university_id", table_name="scholarships")
    op.drop_table("scholarships")
    op.drop_table("admission_info")
    op.drop_index("ix_subjects_university_id", table_name="subjects")
    op.drop_index("ix_subjects_course_id", table_name="subjects")
    op.drop_table("subjects")
    op.drop_index("ix_courses_degree_type", table_name="courses")
    op.drop_index("ix_courses_university_id", table_name="courses")
    op.drop_table("courses")
    op.drop_table("agent_configs")
    op.drop_index("ix_role_permissions_university_id", table_name="role_permissions")
    op.drop_table("role_permissions")
    op.drop_constraint("fk_users_university_id", "users", type_="foreignkey")
    op.drop_index("ix_universities_phone", table_name="universities")
    op.drop_index("ix_universities_name", table_name="universities")
    op.drop_table("universities")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
