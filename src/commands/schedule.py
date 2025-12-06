def build_followups(parent_page_id, event_date_str):
    """
    Creates T+1, T+3, T+7, T+14, and T+30 follow-up tasks
    for events, K12 programs, accelerator cohorts, or clients.
    """
    event_dt = datetime.strptime(event_date_str, "%Y-%m-%d")

    followups = [
        ("T+1: Send Thank-You Emails + Feedback Form", 1),
        ("T+3: Sponsor / Stakeholder Follow-Up", 3),
        ("T+7: Team Debrief Notes", 7),
        ("T+14: Submit Client Follow-Up Report", 14),
        ("T+30: Review Insights & Update Knowledge Base", 30)
    ]

    for name, offset in followups:
        due_dt = add_days(event_dt, offset)
        # Pass due_dt as timeline_start and timeline_end
        create_task(name, parent_page_id, timeline_start=due_dt, timeline_end=due_dt)
def build_countdown(event_page_id, event_date_str):
    """
    Creates T-30, T-21, T-14, T-7, T-3, T-1, and T+1 tasks.
    """
    event_dt = datetime.strptime(event_date_str, "%Y-%m-%d")

    countdowns = [
        ("T-30: Confirm Speakers, Location, Vendors", -30),
        ("T-21: Confirm Agenda & Assets", -21),
        ("T-14: Begin Marketing Push", -14),
        ("T-7: Final Logistics Check", -7),
        ("T-3: Send Final Emails to Clients", -3),
        ("T-1: Day-Before Readiness Checklist", -1),
        ("T+1: Send Thank-You Emails & Feedback Forms", 1)
    ]

    for name, offset in countdowns:
        task_date = add_days(event_dt, offset)
        globals()["_timeline_start"] = to_iso(task_date)
        globals()["_timeline_end"] = to_iso(task_date)
        task_id = create_task(name, event_page_id)
        globals().pop("_timeline_start", None)
        globals().pop("_timeline_end", None)
def create_recurring_tasks(parent_page_id, base_date_str, items, frequency="daily", occurrences=10):
    """
    Creates recurring tasks under a parent (like 'IPE Operations').
    items: list of task names (strings)
    frequency: 'daily', 'weekly', 'monthly'
    occurrences: how many times to repeat
    """
    base_dt = datetime.strptime(base_date_str, "%Y-%m-%d")
    for i in range(occurrences):
        if frequency == "daily":
            task_date = add_days(base_dt, i)
        elif frequency == "weekly":
            task_date = add_weeks(base_dt, i)
        elif frequency == "monthly":
            task_date = add_days(base_dt, i * 30)  # rough monthly step
        else:
            task_date = base_dt
        for name in items:
            globals()["_timeline_start"] = to_iso(task_date)
            globals()["_timeline_end"] = to_iso(task_date)
            task_id = create_task(name, parent_page_id)
            globals().pop("_timeline_start", None)
            globals().pop("_timeline_end", None)

def build_daily_ipe_cycle(parent_page_id, start_date):
    tasks = [
        "Check IPE inbox & reply to priority emails",
        "Review today’s events & sessions",
        "Review top 3 priorities",
        "Quick cashflow check",
        "15-minute planning for tomorrow"
    ]
    create_recurring_tasks(parent_page_id, start_date, tasks, frequency="daily", occurrences=30)

def build_weekly_ipe_cycle(parent_page_id, start_date):
    tasks = [
        "Review revenue & invoices",
        "Review upcoming events & programs",
        "Check progress on key projects",
        "Team check-in & delegation",
        "Marketing content planning"
    ]
    create_recurring_tasks(parent_page_id, start_date, tasks, frequency="weekly", occurrences=12)

def build_monthly_ipe_cycle(parent_page_id, start_date):
    tasks = [
        "Full financial review",
        "Update KPIs & dashboards",
        "Strategic planning for next month",
        "Update proposals & pipeline",
        "Review IndigiRise Accelerator & K12 program status"
    ]
    create_recurring_tasks(parent_page_id, start_date, tasks, frequency="monthly", occurrences=6)
from datetime import datetime, timedelta
from commands.notion import update_page_property, create_task
import pytz

def add_days(start_date, days):
    """ Returns a date + N days. """
    return start_date + timedelta(days=days)

def add_weeks(start_date, weeks):
    """ Returns a date + N weeks. """
    return start_date + timedelta(weeks=weeks)

def to_iso(date):
    """ Convert datetime to Notion ISO date string. """
    return date.strftime("%Y-%m-%d")

def set_timeline(page_id, start_date, end_date):
    """ Writes Timeline Start/End into a Notion record. """
    update_page_property(page_id, "Timeline Start", to_iso(start_date))
    update_page_property(page_id, "Timeline End", to_iso(end_date))

def build_event_timeline(event_page_id, event_date):
    """Creates a standardized event timeline inside Notion."""
    event_dt = datetime.strptime(event_date, "%Y-%m-%d")
    timeline_items = [
        ("Confirm speakers", -30),
        ("Finalize agenda", -21),
        ("Marketing push begins", -14),
        ("Confirm logistics", -7),
        ("Final reminders to clients", -3),
        ("Day-of event operations", 0),
        ("Collect testimonials", 1),
        ("Send client follow-up report", 7),
    ]
    for task_name, offset in timeline_items:
        task_dt = add_days(event_dt, offset)
        # Pass timeline dates at creation time
        globals()["_timeline_start"] = to_iso(task_dt)
        globals()["_timeline_end"] = to_iso(task_dt)
        task_page_id = create_task(task_name, event_page_id)
        globals().pop("_timeline_start", None)
        globals().pop("_timeline_end", None)

def build_k12_timeline(program_page_id, start_date):
    """Builds a 10-week K12 teaching timeline."""
    start_dt = datetime.strptime(start_date, "%Y-%m-%d")
    weeks = [
        "Week 1: Introduction & Teachings",
        "Week 2: Cultural Storytelling",
        "Week 3: Language Basics",
        "Week 4: Traditional Games",
        "Week 5: Land-Based Learning",
        "Week 6: Drumming & Song",
        "Week 7: Art & Craft",
        "Week 8: Ceremony Teachings",
        "Week 9: Review & Practice",
        "Week 10: Celebration & Sharing Circle"
    ]
    for i, lesson in enumerate(weeks):
        lesson_date = add_weeks(start_dt, i)
        globals()["_timeline_start"] = to_iso(lesson_date)
        globals()["_timeline_end"] = to_iso(lesson_date)
        task_id = create_task(lesson, program_page_id)
        globals().pop("_timeline_start", None)
        globals().pop("_timeline_end", None)

def build_accelerator_timeline(page_id, start_date):
    """Builds a 12-week IndigiRise Accelerator timeline."""
    start_dt = datetime.strptime(start_date, "%Y-%m-%d")
    topics = [
        "Week 1: Identity & Attitude",
        "Week 2: Stories",
        "Week 3: Freedom",
        "Week 4: Habits",
        "Week 5: Vision & Planning",
        "Week 6: Marketing Foundations",
        "Week 7: Financial Wellness",
        "Week 8: Sales & Clients",
        "Week 9: Leadership Development",
        "Week 10: Pitching Your Business",
        "Week 11: Final Adjustments",
        "Week 12: Pitch Night"
    ]
    for i, topic in enumerate(topics):
        week_start = add_weeks(start_dt, i)
        globals()["_timeline_start"] = to_iso(week_start)
        globals()["_timeline_end"] = to_iso(week_start)
        task_id = create_task(topic, page_id)
        globals().pop("_timeline_start", None)
        globals().pop("_timeline_end", None)
