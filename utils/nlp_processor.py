import pandas as pd
import numpy as np
import re
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

class NLPProcessor:
    def __init__(self, df):
        self.df = df
        self.numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        self.categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
        self.date_cols = df.select_dtypes(include=['datetime64']).columns.tolist()
    
    def process_query(self, query):
        # Process natural language query and return response
        query_lower = query.lower()
        
        # Intent detection
        if any(word in query_lower for word in ['summary', 'overview', 'describe', 'tell me about']):
            return self.generate_summary()
        
        elif any(word in query_lower for word in ['show', 'display', 'plot', 'chart', 'graph']) and \
             any(word in query_lower for word in ['by', 'group', 'per', 'for each']):
            return self.generate_grouped_chart(query_lower)
        
        elif any(word in query_lower for word in ['correlation', 'related', 'affect', 'impact', 'factor']):
            return self.generate_correlation_analysis(query_lower)
        
        elif any(word in query_lower for word in ['top', 'best', 'highest', 'most', 'maximum']):
            return self.generate_top_analysis(query_lower)
        
        elif any(word in query_lower for word in ['trend', 'over time', 'timeline', 'growth']):
            return self.generate_time_analysis(query_lower)
        
        elif any(word in query_lower for word in ['anomaly', 'outlier', 'unusual', 'strange', 'weird']):
            return self.generate_anomaly_detection(query_lower)
        
        elif any(word in query_lower for word in ['predict', 'forecast', 'future']):
            return self.generate_prediction(query_lower)
        
        else:
            return self.generate_general_response(query_lower)
    
    def generate_summary(self):
        # Generate data summary
        response = {
            'type': 'summary',
            'title': 'Data Summary',
            'text': f"""
Your dataset contains:
- {self.df.shape[0]:,} rows and {self.df.shape[1]} columns
- {len(self.numeric_cols)} numeric columns: {', '.join(self.numeric_cols[:5])}
- {len(self.categorical_cols)} categorical columns: {', '.join(self.categorical_cols[:5])}
- {len(self.date_cols)} date columns: {', '.join(self.date_cols[:3])}
"""
        }
        
        # Add key statistics
        if self.numeric_cols:
            response['stats'] = self.df[self.numeric_cols].mean().to_dict()
        
        return response
    
    def generate_grouped_chart(self, query):
        # Generate grouped chart based on query
        columns = self.extract_columns(query)
        
        if len(columns) >= 2:
            group_col = columns[0]
            value_col = columns[1] if columns[1] in self.numeric_cols else self.numeric_cols[0]
            
            if group_col in self.categorical_cols and value_col in self.numeric_cols:
                grouped = self.df.groupby(group_col)[value_col].mean().reset_index()
                fig = px.bar(grouped, x=group_col, y=value_col, 
                            title=f'{value_col} by {group_col}',
                            color=group_col)
                
                response = {
                    'type': 'chart',
                    'title': f'{value_col} by {group_col}',
                    'fig': fig,
                    'text': f'Showing average {value_col} for each {group_col}.'
                }
                
                max_val = grouped[value_col].max()
                max_group = grouped[group_col][grouped[value_col].idxmax()]
                response['insight'] = f'Insight: {max_group} has the highest {value_col} at {max_val:.2f}'
                
                return response
        
        return self.generate_simple_visualization(query)
    
    def generate_correlation_analysis(self, query):
        # Analyze correlations
        if len(self.numeric_cols) >= 2:
            corr = self.df[self.numeric_cols].corr()
            
            corr_pairs = []
            for i in range(len(corr.columns)):
                for j in range(i+1, len(corr.columns)):
                    if abs(corr.iloc[i, j]) > 0.3:
                        corr_pairs.append({
                            'col1': corr.columns[i],
                            'col2': corr.columns[j],
                            'corr': corr.iloc[i, j]
                        })
            
            corr_pairs = sorted(corr_pairs, key=lambda x: abs(x['corr']), reverse=True)
            
            if corr_pairs:
                top_pair = corr_pairs[0]
                response = {
                    'type': 'insight',
                    'title': 'Correlation Analysis',
                    'text': f'Strongest correlation: {top_pair["col1"]} and {top_pair["col2"]} ({top_pair["corr"]:.2f})',
                    'recommendation': f'Suggestion: {top_pair["col1"]} and {top_pair["col2"]} are strongly related.'
                }
                
                fig = px.imshow(corr, text_auto=True, aspect='auto',
                               title='Correlation Heatmap',
                               color_continuous_scale='RdBu')
                response['fig'] = fig
                
                return response
        
        return {
            'type': 'info',
            'title': 'Correlation Analysis',
            'text': 'Not enough numeric columns for correlation analysis.'
        }
    
    def generate_top_analysis(self, query):
        # Find top values
        columns = self.extract_columns(query)
        
        if columns:
            col = columns[0]
            if col in self.numeric_cols:
                top_val = self.df[col].max()
                top_row = self.df[self.df[col] == top_val]
                
                response = {
                    'type': 'insight',
                    'title': f'Top {col}',
                    'text': f'The highest {col} is {top_val:,.2f}',
                    'details': top_row.to_dict('records')[0] if not top_row.empty else {},
                    'recommendation': f'Suggestion: Investigate what makes this {col} so high.'
                }
                
                fig = px.histogram(self.df, x=col, title=f'Distribution of {col}')
                response['fig'] = fig
                
                return response
        
        return {
            'type': 'info',
            'title': 'Top Analysis',
            'text': 'Please specify what you want to find the top of (e.g., "top sales")'
        }
    
    def generate_time_analysis(self, query):
        # Analyze trends over time
        if self.date_cols:
            date_col = self.date_cols[0]
            value_col = self.numeric_cols[0] if self.numeric_cols else None
            
            if value_col:
                self.df[date_col] = pd.to_datetime(self.df[date_col])
                daily = self.df.groupby(self.df[date_col].dt.date)[value_col].sum().reset_index()
                
                fig = px.line(daily, x=date_col, y=value_col, 
                             title=f'{value_col} Over Time')
                
                response = {
                    'type': 'chart',
                    'title': f'{value_col} Trend',
                    'fig': fig,
                    'text': f'Showing {value_col} over time.',
                    'insight': f'Insight: Total {value_col}: {daily[value_col].sum():,.2f}'
                }
                
                return response
        
        return {
            'type': 'info',
            'title': 'Time Analysis',
            'text': 'No date columns found in your data.'
        }
    
    def generate_anomaly_detection(self, query):
        # Detect anomalies
        anomalies = {}
        
        for col in self.numeric_cols[:3]:
            Q1 = self.df[col].quantile(0.25)
            Q3 = self.df[col].quantile(0.75)
            IQR = Q3 - Q1
            lower = Q1 - 1.5 * IQR
            upper = Q3 + 1.5 * IQR
            
            outliers = self.df[(self.df[col] < lower) | (self.df[col] > upper)]
            if len(outliers) > 0:
                anomalies[col] = {
                    'count': len(outliers),
                    'percentage': (len(outliers) / len(self.df)) * 100,
                    'lower': lower,
                    'upper': upper
                }
        
        if anomalies:
            text = 'Found anomalies in:\n'
            for col, data in anomalies.items():
                text += f'- {col}: {data["count"]} outliers ({data["percentage"]:.1f}%)\n'
            
            response = {
                'type': 'warning',
                'title': 'Anomaly Detection',
                'text': text,
                'recommendation': 'Suggestion: Review these outliers. They could indicate errors or valuable insights.'
            }
            
            return response
        
        return {
            'type': 'success',
            'title': 'No Anomalies Found',
            'text': 'Your data appears to be clean with no significant outliers.'
        }
    
    def generate_prediction(self, query):
        # Simple prediction
        if len(self.numeric_cols) >= 1:
            col = self.numeric_cols[0]
            mean_val = self.df[col].mean()
            trend = self.df[col].iloc[-1] - self.df[col].iloc[0] if len(self.df) > 1 else 0
            
            response = {
                'type': 'insight',
                'title': 'Simple Prediction',
                'text': f'Average {col}: {mean_val:.2f}',
                'insight': f'Insight: Based on current trend, {col} is {"increasing" if trend > 0 else "decreasing"}'
            }
            
            return response
        
        return {
            'type': 'info',
            'title': 'Prediction',
            'text': 'Not enough data for prediction.'
        }
    
    def generate_general_response(self, query):
        # Fallback response
        return {
            'type': 'info',
            'title': 'I am not sure what you meant',
            'text': 'Try asking about:\n- "Show me sales by region"\n- "What factors affect profit?"\n- "Top products"\n- "Trends over time"\n- "Find anomalies"\n- "Summarize my data"'
        }
    
    def generate_simple_visualization(self, query):
        # Generate simple visualization
        if self.numeric_cols:
            col = self.numeric_cols[0]
            fig = px.histogram(self.df, x=col, title=f'Distribution of {col}')
            
            return {
                'type': 'chart',
                'title': f'{col} Distribution',
                'fig': fig,
                'text': f'Showing distribution of {col}.'
            }
        
        return {
            'type': 'info',
            'title': 'No Data',
            'text': 'No numeric columns available for visualization.'
        }
    
    def extract_columns(self, query):
        # Extract column names from query
        found_cols = []
        all_cols = self.numeric_cols + self.categorical_cols + self.date_cols
        
        for col in all_cols:
            if col.lower() in query.lower():
                found_cols.append(col)
        
        return found_cols
