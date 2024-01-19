from application.workers import celery
from datetime import datetime
from flask import current_app as app, make_response, Response, render_template
import pandas as pd
import json
from celery.schedules import crontab
import yagmail
from jinja2 import Template
from application.models import User, List, Card
from weasyprint import HTML
import uuid
from datetime import datetime as dt
import matplotlib.pyplot as plt
from main import cache


@celery.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(crontab('*/10 * * * * *'), daily_reminder.s(), name='Daily Reminder at 6am')
    sender.add_periodic_task(crontab('*/10 * * * * *'), monthly_report.s(), nanme='At 00:00 on day-of-month 1')
    # sender.add_periodic_task(10.0, daily_reminder.s(), name='Daily Reminder at 6am')
    # sender.add_periodic_task(20.0, monthly_report.s(), name='At 00:00 on day-of-month 1')


@cache.cached(timeout=50,key_prefix='daily_reminder')
@celery.task()
def daily_reminder():
    users = User.query.all()
    data = {}
    for user in users:
        lists = user.lists
        template_data = []
        for l in lists:
            for card in l.cards:
                if card.toggle == '0':
                    temp = {}
                    temp['listname'] = l.name
                    temp['cardname'] = card.name
                    temp['cardcontent'] = card.content
                    temp['deadline'] = card.deadline
                    template_data.append(temp)
        data[user.email] = template_data
    print(data)
    for user in data:
        if data[user] != []:
            template = render_template('daily_reminder.html', data = data[user])
            receiver = user
            subject = 'Daily reminder - Kanban App'
            body='Please find the below attachment for the pending tasks'
            html = HTML(string=template)
            html.write_pdf(target='reminder.pdf')
            yag = yagmail.SMTP(user='shabarish.14b@gmail.com', password='onuoljimpjnprnwp')
            yag.send(to=receiver, subject=subject, contents=body, attachments='./reminder.pdf')
    return 'Daily reminder sent successfully'


@celery.task()
def monthly_report():
    users = User.query.all()
    data = {}
    for user in users:
        lists = user.lists
        plot = {'x':[], 'y1': [], 'y0': []}
        template_data = {'total':0,'completed':0,'pending':0,'incomplete':0}
        template_data['username'] = user.name
        for l in lists:
            plot['x'].append(l.name)
            tog_1 = 0
            tog_0 = 0
            for card in l.cards:
                template_data['total'] += 1
                if card.toggle == '1':
                    tog_1 += 1
                    template_data['completed'] += 1
                else:
                    tog_0 += 1
                    today = dt.today().strftime('%Y-%m-%d')
                    if card.deadline > today:
                        template_data['pending'] += 1
                    else:
                        template_data['incomplete'] += 1
            plot['y1'].append(tog_1)
            plot['y0'].append(tog_0)
        template_data['plot'] = plot
        data[user.email] = template_data

    for user in data:
        print(data[user]['plot'])
        x = data[user]['plot']['x']
        y1 = data[user]['plot']['y1']
        y0 = data[user]['plot']['y0']
        plt.bar(x, y1, color='r')
        plt.bar(x, y0, bottom=y1, color='b')
        plt.savefig('monthly_report.png')
        template = render_template('monthly_report.html',data=data[user])
        receiver = user
        subject = 'Monthly Report - Kanban App'
        body='Please find the below attachment for the Monthly report'
        html = HTML(string=template)
        html.write_pdf(target='report.pdf')
        yag = yagmail.SMTP(user='shabarish.14b@gmail.com', password='onuoljimpjnprnwp')
        yag.send(to=receiver, subject=subject, contents=body, attachments=['./report.pdf','./monthly_report.png'])
    
    return 'Monthly report sent successfully'

@celery.task()
def export():
    df = pd.DataFrame({'id':[1,2,3,4],'name':['one','two','three','four']})
    resp = Response(
       df.to_csv(),
       mimetype="text/csv",
       headers={"Content-disposition":
       "attachment; filename=filename.csv"})
    yield resp
    return 'exported'