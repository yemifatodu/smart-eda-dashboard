import json
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime, timedelta
import pandas as pd
import streamlit as st
from pathlib import Path

class ReportScheduler:
    def __init__(self):
        self.schedule_file = Path('reports/schedules.json')
        self.load_schedules()
    
    def load_schedules(self):
        # Load schedules from file
        if self.schedule_file.exists():
            with open(self.schedule_file, 'r') as f:
                self.schedules = json.load(f)
        else:
            self.schedules = {}
    
    def save_schedules(self):
        # Save schedules to file
        self.schedule_file.parent.mkdir(exist_ok=True)
        with open(self.schedule_file, 'w') as f:
            json.dump(self.schedules, f, indent=2)
    
    def add_schedule(self, name, frequency, email, report_config):
        # Add a new schedule
        schedule_id = f"schedule_{len(self.schedules) + 1}"
        self.schedules[schedule_id] = {
            'name': name,
            'frequency': frequency,
            'email': email,
            'report_config': report_config,
            'created_at': datetime.now().isoformat(),
            'last_sent': None,
            'next_send': self.calculate_next_send(frequency)
        }
        self.save_schedules()
        return schedule_id
    
    def calculate_next_send(self, frequency):
        # Calculate next send date based on frequency
        now = datetime.now()
        if frequency == 'daily':
            next_send = now + timedelta(days=1)
        elif frequency == 'weekly':
            next_send = now + timedelta(days=7)
        elif frequency == 'monthly':
            next_send = now + timedelta(days=30)
        else:
            next_send = now + timedelta(days=1)
        return next_send.isoformat()
    
    def get_due_schedules(self):
        # Get schedules that are due to run
        due = []
        now = datetime.now()
        for sid, schedule in self.schedules.items():
            if schedule.get('next_send'):
                next_send = datetime.fromisoformat(schedule['next_send'])
                if next_send <= now:
                    due.append((sid, schedule))
        return due
    
    def send_report_email(self, schedule, report_html):
        # Send report via email
        try:
            print(f"Email would send to {schedule['email']}")
            print(f"Report: {schedule['name']}")
            
            # Update last sent
            schedule['last_sent'] = datetime.now().isoformat()
            schedule['next_send'] = self.calculate_next_send(schedule['frequency'])
            self.save_schedules()
            
            return True
        except Exception as e:
            print(f"Error sending email: {e}")
            return False
    
    def delete_schedule(self, schedule_id):
        # Delete a schedule
        if schedule_id in self.schedules:
            del self.schedules[schedule_id]
            self.save_schedules()
            return True
        return False

def create_report_html(df, title):
    # Create a simple HTML report
    html = f"""
    <html>
    <head>
        <title>{title}</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; }}
            table {{ border-collapse: collapse; width: 100%; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background-color: #1f77b4; color: white; }}
        </style>
    </head>
    <body>
        <h1>{title}</h1>
        <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p>Total Records: {len(df):,}</p>
        <h2>Summary Statistics</h2>
        {df.describe().to_html()}
        <h2>Data Sample</h2>
        {df.head(10).to_html()}
    </body>
    </html>
    """
    return html
