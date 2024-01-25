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
    receiver = "deeptha.tirumala@gmail.com"
    subject = 'Daily reminder - BigMarket'
    body='Hii, please have a check adn get your requirements done in seconds'
    yag = yagmail.SMTP(user='deeptha.tirumala@gmail.com', password='nsrl cojd tdxm hyyp')
    yag.send(to=receiver, subject=subject, contents=body)
    # print("daily")
    return 'Daily reminder successfully sent'



@celery.task()
def monthly_report():
    receiver = "deeptha.tirumala@gmail.com"
    subject = 'Daily reminder - BigMarket'
    body='Please find the Monthly report for this month'
    yag = yagmail.SMTP(user='deeptha.tirumala@gmail.com', password='nsrl cojd tdxm hyyp')
    yag.send(to=receiver, subject=subject, contents=body)
    # print("daily")
    return 'Monthly report sent successfully'
    
@celery.task()
def export():
    print("test")
    return 'exported'


# redis
# redis-server "C:\Program Files\Redis\redis.windows.conf"
# & "C:\Program Files\Redis\redis-server.exe" "C:\Program Files\Redis\redis.windows.conf"
# celery
# python -m celery -A main.celery worker -l info -P solo
# python -m celery -A main.celery beat --max-interval 1 -l info