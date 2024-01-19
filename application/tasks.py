from application.workers import celery
from datetime import datetime
from flask import current_app as app, make_response, Response, render_template
import pandas as pd
import json
from celery.schedules import crontab
import yagmail
from jinja2 import Template
from application.models import *
import uuid
from datetime import datetime as dt
# import matplotlib.pyplot as plt



@celery.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(5.0, daily_reminder.s(), name='Daily Reminder at 6am')
    sender.add_periodic_task(5.0, monthly_report.s(), name='At 00:00 on day-of-month 1')
    # sender.add_periodic_task(10.0, daily_reminder.s(), name='Daily Reminder at 6am')
    # sender.add_periodic_task(20.0, monthly_report.s(), name='At 00:00 on day-of-month 1')



@celery.task()
def daily_reminder():
    receiver = "rishikesh.vankayala@gmail.com"
    subject = 'Daily reminder - Kanban App'
    body='Please find the below attachment for the pending tasks'
    yag = yagmail.SMTP(user='rishikesh.vankayala@gmail.com', password='wfkcdtiplzoiqaar')
    yag.send(to=receiver, subject=subject, contents=body)
    print("daily")
    return 'Daily reminder sent successfully'



@celery.task()
def monthly_report():
    receiver = "rishikesh.vankayala@gmail.com"
    subject = 'Daily reminder - Kanban App'
    body='Please find the below attachment for the pending tasks'
    yag = yagmail.SMTP(user='rishikesh.vankayala@gmail.com', password='wfkcdtiplzoiqaar')
    yag.send(to=receiver, subject=subject, contents=body)
    print("daily")
    return 'Monthly report sent successfully'
    
@celery.task()
def export():
    print("test")
    return 'exported'