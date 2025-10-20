# ──────────────────────────────────────────────────────────────
# add_task.py — Task creation, listing, details, and edit routes
# Making Me Happier App
# ──────────────────────────────────────────────────────────────

from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session
from app.db.session import get_session
from app.models.entities import Task, TimeLog, Pillar, Frequency, Goal

router = APIRouter(tags=["Tasks"])  # ✅ no prefix here

templates = Jinja2Templates(directory="app/templates")

# ───────────────────────────────────────────────
# 1️⃣ Add Task — form page
# ───────────────────────────────────────────────
@router.get("/add_task", response_class=HTMLResponse)
def add_task_form(request: Request):
    """Render the Add Task HTML form."""
    return templates.TemplateResponse(
        "add_task.html",
        {
            "request": request,
            "pillars": [Pillar.HARD_WORK, Pillar.CALMNESS, Pillar.FAMILY],
            "frequencies": [
                Frequency.ONE_TIME,
                Frequency.DAILY,
                Frequency.WEEKLY,
                Frequency.MONTHLY,
                Frequency.YEARLY,
            ],
        },
    )

# ───────────────────────────────────────────────
# 2️⃣ Add Task — form submission
# ───────────────────────────────────────────────
@router.post("/add_task", response_class=HTMLResponse)
def create_task(
    request: Request,
    name: str = Form(...),
    pillar: str = Form(...),
    allocated_time: int = Form(...),
    frequency: str = Form(...),
    success_target_percent: int = Form(90),
    ideal_gap_days: int | None = Form(None),
    is_daily_followup: bool = Form(False),
    is_separately_monitored: bool = Form(False),
    session: Session = Depends(get_session),
):
    """Create a new task and save to DB."""

    # Create schedule if recurring
    # No separate schedule needed now; frequency is stored directly in the Task
    goal_id = None
    if frequency in [Frequency.WEEKLY, Frequency.MONTHLY, Frequency.QUARTERLY, Frequency.YEARLY]:
    # optionally, you can link this task to an existing goal (to be added in Milestone 2)
        goal_id = None


    # Create task
    task = Task(
        name=name,
        pillar=pillar,
        frequency=frequency,
        success_target_percent=success_target_percent,
        ideal_gap_days=ideal_gap_days,
        is_daily_followup=is_daily_followup,
        is_separately_monitored=is_separately_monitored,
        goal_id=goal_id,
    )
    session.add(task)
    session.commit()

    return templates.TemplateResponse(
        "success.html",
        {"request": request, "message": f"Task '{name}' added successfully!"},
    )

# ───────────────────────────────────────────────
# 3️⃣ List all tasks
# ───────────────────────────────────────────────
@router.get("/tasks", response_class=HTMLResponse)
def list_tasks(request: Request, session: Session = Depends(get_session)):
    tasks = session.exec(select(Task)).all()
    return templates.TemplateResponse(
        "tasks_list.html", {"request": request, "tasks": tasks}
    )

# ───────────────────────────────────────────────
# 4️⃣ Task detail + weekly/monthly graphs
# ───────────────────────────────────────────────
@router.get("/task/{task_id}", response_class=HTMLResponse)
def task_detail(task_id: int, request: Request, session: Session = Depends(get_session)):
    task = session.get(Task, task_id)
    if not task:
        return HTMLResponse("Task not found", status_code=404)

    # Compute recent logs
    end_date = date.today()
    start_week = end_date - timedelta(days=7)
    start_month = end_date - timedelta(days=30)

    week_logs = session.exec(
        select(TimeLog).where(TimeLog.task_id == task_id, TimeLog.day >= start_week)
    ).all()
    month_logs = session.exec(
        select(TimeLog).where(TimeLog.task_id == task_id, TimeLog.day >= start_month)
    ).all()

    def aggregate(logs):
        data = {}
        for l in logs:
            data[str(l.day)] = data.get(str(l.day), 0) + l.minutes
        return data

    week_data = aggregate(week_logs)
    month_data = aggregate(month_logs)

    return templates.TemplateResponse(
        "task_detail.html",
        {
            "request": request,
            "task": task,
            "week_data": week_data,
            "month_data": month_data,
        },
    )

# ───────────────────────────────────────────────
# 5️⃣ Edit task — form
# ───────────────────────────────────────────────
@router.get("/task/{task_id}/edit", response_class=HTMLResponse)
def edit_task_form(task_id: int, request: Request, session: Session = Depends(get_session)):
    task = session.get(Task, task_id)
    if not task:
        return HTMLResponse("Task not found", status_code=404)
    return templates.TemplateResponse("edit_task.html", {"request": request, "task": task})

# ───────────────────────────────────────────────
# 6️⃣ Edit task — submission
# ───────────────────────────────────────────────
@router.post("/task/{task_id}/edit", response_class=HTMLResponse)
def edit_task_submit(
    task_id: int,
    request: Request,
    name: str = Form(...),
    pillar: str = Form(...),
    is_daily_followup: bool = Form(False),
    is_separately_monitored: bool = Form(False),
    session: Session = Depends(get_session),
):
    task = session.get(Task, task_id)
    if not task:
        return HTMLResponse("Task not found", status_code=404)

    task.name = name
    task.pillar = pillar
    task.is_daily_followup = is_daily_followup
    task.is_separately_monitored = is_separately_monitored
    session.add(task)
    session.commit()

    return RedirectResponse(url=f"/makingmehappier/task/{task_id}", status_code=303)
