import json
import streamlit as st
from pathlib import Path
import pandas as pd
import plotly.graph_objects as go

class DashboardManager:
    def __init__(self):
        self.dashboards_dir = Path('dashboards')
        self.dashboards_dir.mkdir(exist_ok=True)
        self.load_dashboards()
    
    def load_dashboards(self):
        # Load all saved dashboards
        self.dashboards = {}
        for file in self.dashboards_dir.glob('*.json'):
            with open(file, 'r') as f:
                data = json.load(f)
                self.dashboards[data['name']] = data
    
    def save_dashboard(self, name, layout, widgets, theme='light'):
        # Save dashboard configuration
        dashboard = {
            'name': name,
            'layout': layout,
            'widgets': widgets,
            'theme': theme,
            'created_at': pd.Timestamp.now().isoformat()
        }
        
        file_path = self.dashboards_dir / f"{name.replace(' ', '_')}.json"
        with open(file_path, 'w') as f:
            json.dump(dashboard, f, indent=2)
        
        self.dashboards[name] = dashboard
        return dashboard
    
    def load_dashboard(self, name):
        # Load a specific dashboard
        return self.dashboards.get(name)
    
    def delete_dashboard(self, name):
        # Delete a dashboard
        file_path = self.dashboards_dir / f"{name.replace(' ', '_')}.json"
        if file_path.exists():
            file_path.unlink()
        if name in self.dashboards:
            del self.dashboards[name]
        return True
    
    def get_widget_types(self):
        # Available widget types
        return {
            'chart': ['Bar Chart', 'Line Chart', 'Scatter Plot', 'Histogram', 'Box Plot'],
            'metric': ['Number', 'Percentage', 'Currency'],
            'table': ['Data Table', 'Summary Table'],
            'text': ['Heading', 'Paragraph', 'Markdown']
        }
    
    def get_default_layout(self):
        # Default grid layout
        return {
            'columns': 3,
            'rows': 2,
            'gap': 20
        }
