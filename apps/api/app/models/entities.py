from __future__ import annotations
from datetime import date, datetime, time
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship


# ────────────────────────────────────────────────
# ENUM-LIKE CLASSES
# ────────────────────────────────────────────────

class Frequency(str):
    ONE_TIME = "one_time"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"   # ✅ New frequency option
    YEARLY = "yearly"
    TODAY = "today"


class Pillar(str):
    HARD_WORK = "HARD_WORK"
    CALMNESS = "CALMNESS"
    FAMILY = "FAMILY"


class GoalType(str):
    WEEK = "week"
    MONTH = "month"
    QUARTER = "quarter"       # ✅ New goal type
    YEAR = "year"


# ────────────────────────────────────────────────
# MODELS
# ────────────────────────────────────────────────

class Goal(SQLModel, table=True):
    """
    Represents a high-level milestone (weekly / monthly / quarterly / yearly).
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    goal_type: str = Field(default=GoalType.WEEK)
    description: Optional[str] = None

    target_minutes: int = 0
    used_minutes: int = 0
    due_date: Optional[date] = None

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    tasks: List["Task"] = Relationship(back_populates="goal")

    @property
    def progress_percent(self) -> float:
        """Compute goal progress based on time used."""
        if self.target_minutes == 0:
            return 0
        return min(100, round((self.used_minutes / self.target_minutes) * 100, 1))

    @property
    def remaining_minutes(self) -> int:
        """Time still available to meet target."""
        return max(0, self.target_minutes - self.used_minutes)


class Task(SQLModel, table=True):
    """
    Represents an actionable task or habit.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    pillar: str
    frequency: str = Field(default=Frequency.DAILY)
    success_target_percent: int = Field(default=90)
    ideal_gap_days: Optional[int] = None

    # Relationships
    goal_id: Optional[int] = Field(default=None, foreign_key="goal.id")
    parent_task_id: Optional[int] = Field(default=None, foreign_key="task.id")

    is_daily_followup: bool = False
    is_separately_monitored: bool = False
    archived: bool = False

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # ORM relationships
    goal: Optional[Goal] = Relationship(back_populates="tasks")
    parent_task: Optional["Task"] = Relationship(
        back_populates="subtasks",
        sa_relationship_kwargs={"remote_side": "Task.id"},
    )
    subtasks: List["Task"] = Relationship(back_populates="parent_task")
    timelogs: List["TimeLog"] = Relationship(back_populates="task")

    @property
    def total_minutes(self) -> int:
        """Sum of all logged minutes for this task."""
        return sum(log.minutes for log in self.timelogs)


class TimeLog(SQLModel, table=True):
    """
    Represents time entries for a specific task and date.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    task_id: int = Field(foreign_key="task.id")

    day: date = Field(default_factory=date.today)
    slot_start: Optional[time] = None
    slot_end: Optional[time] = None
    minutes: int = 0
    note: Optional[str] = None

    created_at: datetime = Field(default_factory=datetime.utcnow)
    task: Optional[Task] = Relationship(back_populates="timelogs")
