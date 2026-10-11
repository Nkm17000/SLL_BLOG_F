from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from app.run_agent import should_skip_for_daily_limit

def test_push_is_not_blocked_by_existing_post_today():
    state={"history":[{"status":"published","published_at_utc":"2026-10-11T07:00:00+00:00"}]}
    now=datetime(2026,10,11,13,0,tzinfo=ZoneInfo("Asia/Kolkata"))
    assert should_skip_for_daily_limit(state, "push", now=now) is False

def test_schedule_is_skipped_after_post_today():
    state={"history":[{"status":"published","published_at_utc":"2026-10-11T07:00:00+00:00"}]}
    now=datetime(2026,10,11,13,0,tzinfo=ZoneInfo("Asia/Kolkata"))
    assert should_skip_for_daily_limit(state, "schedule", now=now) is True

def test_schedule_runs_if_no_post_today():
    state={"history":[]}
    now=datetime(2026,10,11,13,0,tzinfo=ZoneInfo("Asia/Kolkata"))
    assert should_skip_for_daily_limit(state, "schedule", now=now) is False

def test_dry_run_does_not_skip():
    state={"history":[{"status":"published","published_at_utc":"2026-10-11T07:00:00+00:00"}]}
    now=datetime(2026,10,11,13,0,tzinfo=ZoneInfo("Asia/Kolkata"))
    assert should_skip_for_daily_limit(state, "schedule", dry_run=True, now=now) is False
