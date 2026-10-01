from __future__ import annotations
from datetime import datetime
from zoneinfo import ZoneInfo
from app.content_agents import AGENTS,SCHEDULE,agent_for_hour,get_agent
IST=ZoneInfo('Asia/Kolkata')
def current_ist()->datetime: return datetime.now(IST)
def scheduled_agent(now:datetime|None=None): return agent_for_hour((now or current_ist()).hour)
def schedule_table(): return [{'time':f'{h:02d}:00','agent':a,'name':AGENTS[a].name} for h,a in SCHEDULE]
