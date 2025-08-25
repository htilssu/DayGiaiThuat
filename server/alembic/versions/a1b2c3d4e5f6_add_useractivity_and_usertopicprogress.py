"""Add UserActivity and UserTopicProgress models for real profile data

Revision ID: a1b2c3d4e5f6
Revises: 024e1f42c42f
Create Date: 2025-08-23 20:00:14.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, None] = "59b7be7ed199"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create enum type for activity types
    activity_type_enum = sa.Enum(
        "exercise",
        "course",
        "discussion",
        "lesson",
        "test",
        "badge",
        name="activitytype",
    )

    # Create user_activities table
    op.create_table(
        "user_activities",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("activity_type", activity_type_enum, nullable=False),
        sa.Column("activity_name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("score", sa.Integer(), nullable=True),
        sa.Column("progress", sa.String(length=50), nullable=True),
        sa.Column("related_id", sa.Integer(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_user_activities_id"), "user_activities", ["id"], unique=False
    )
    op.create_index(
        op.f("ix_user_activities_user_id"), "user_activities", ["user_id"], unique=False
    )
    op.create_index(
        op.f("ix_user_activities_activity_type"),
        "user_activities",
        ["activity_type"],
        unique=False,
    )

    # Create user_topic_progress table
    op.create_table(
        "user_topic_progress",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("topic_id", sa.Integer(), nullable=False),
        sa.Column(
            "progress_percentage", sa.Float(), nullable=False, server_default="0.0"
        ),
        sa.Column(
            "lessons_completed", sa.Integer(), nullable=False, server_default="0"
        ),
        sa.Column(
            "exercises_completed", sa.Integer(), nullable=False, server_default="0"
        ),
        sa.Column("last_activity_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["topic_id"], ["topics.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_user_topic_progress_id"), "user_topic_progress", ["id"], unique=False
    )
    op.create_index(
        op.f("ix_user_topic_progress_user_id"),
        "user_topic_progress",
        ["user_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_user_topic_progress_topic_id"),
        "user_topic_progress",
        ["topic_id"],
        unique=False,
    )


def downgrade() -> None:
    # Drop tables
    op.drop_index(
        op.f("ix_user_topic_progress_topic_id"), table_name="user_topic_progress"
    )
    op.drop_index(
        op.f("ix_user_topic_progress_user_id"), table_name="user_topic_progress"
    )
    op.drop_index(op.f("ix_user_topic_progress_id"), table_name="user_topic_progress")
    op.drop_table("user_topic_progress")

    op.drop_index(
        op.f("ix_user_activities_activity_type"), table_name="user_activities"
    )
    op.drop_index(op.f("ix_user_activities_user_id"), table_name="user_activities")
    op.drop_index(op.f("ix_user_activities_id"), table_name="user_activities")
    op.drop_table("user_activities")

    # Drop enum type
    activity_type_enum = sa.Enum(name="activitytype")
    activity_type_enum.drop(op.get_bind())
