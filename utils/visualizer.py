import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np

class Visualizer:
    @staticmethod
    def create_parallel_coordinates(df, numeric_cols):
        """Create parallel coordinates plot"""
        df_norm = df[numeric_cols].copy()
        for col in numeric_cols:
            df_norm[col] = (df[col] - df[col].min()) / (df[col].max() - df[col].min())
        
        fig = px.parallel_coordinates(
            df_norm,
            dimensions=numeric_cols,
            color=numeric_cols[0],
            color_continuous_scale=px.colors.diverging.Tealrose,
            title="Parallel Coordinates Plot"
        )
        fig.update_layout(height=500, margin=dict(l=0, r=0, t=50, b=0))
        return fig
    
    @staticmethod
    def create_correlation_heatmap(df, numeric_cols):
        """Create correlation heatmap"""
        corr = df[numeric_cols].corr()
        fig = go.Figure(data=go.Heatmap(
            z=corr.values,
            x=corr.columns,
            y=corr.columns,
            colorscale='RdBu',
            zmin=-1,
            zmax=1,
            text=corr.values.round(2),
            texttemplate='%{text}',
            textfont={"size": 10},
            hoverongaps=False
        ))
        fig.update_layout(height=500)
        return fig
    
    @staticmethod
    def create_distribution_plots(df, numeric_cols):
        """Create distribution histograms"""
        n_cols = min(3, len(numeric_cols))
        n_rows = (len(numeric_cols) + n_cols - 1) // n_cols
        fig = make_subplots(rows=n_rows, cols=n_cols, subplot_titles=numeric_cols)
        
        for idx, col in enumerate(numeric_cols):
            row = idx // n_cols + 1
            col_pos = idx % n_cols + 1
            fig.add_trace(
                go.Histogram(x=df[col], nbinsx=30, name=col, showlegend=False, opacity=0.7),
                row=row, col=col_pos
            )
        fig.update_layout(height=300 * n_rows)
        return fig
    
    @staticmethod
    def create_categorical_plot(df, cat_col):
        """Create bar chart for categorical data"""
        value_counts = df[cat_col].value_counts()
        fig = go.Figure(data=[
            go.Bar(
                x=value_counts.index,
                y=value_counts.values,
                text=value_counts.values,
                textposition='outside',
                marker_color='lightblue'
            )
        ])
        fig.update_layout(
            title=f"{cat_col} Distribution",
            xaxis_title=cat_col,
            yaxis_title="Count",
            height=350
        )
        return fig
    
    @staticmethod
    def create_box_plots(df, numeric_cols):
        """Create box plots for outlier detection"""
        n_cols = min(3, len(numeric_cols))
        n_rows = (len(numeric_cols) + n_cols - 1) // n_cols
        fig = make_subplots(rows=n_rows, cols=n_cols, subplot_titles=numeric_cols)
        
        for idx, col in enumerate(numeric_cols):
            row = idx // n_cols + 1
            col_pos = idx % n_cols + 1
            fig.add_trace(
                go.Box(y=df[col], name=col, showlegend=False, boxmean='sd'),
                row=row, col=col_pos
            )
        fig.update_layout(height=300 * n_rows)
        return fig
    
    @staticmethod
    def create_radar_chart(models, metrics):
        """Create radar chart for model comparison"""
        fig = go.Figure()
        for model_name, scores in models.items():
            fig.add_trace(go.Scatterpolar(
                r=[scores.get(metric, 0) for metric in metrics],
                theta=metrics,
                fill='toself',
                name=model_name
            ))
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
            showlegend=True,
            height=500,
            title="Model Performance Comparison"
        )
        return fig
    
    @staticmethod
    def create_feature_importance(features, importance):
        """Create feature importance bar chart"""
        sorted_idx = np.argsort(importance)[::-1]
        fig = go.Figure(data=[
            go.Bar(
                x=[features[i] for i in sorted_idx[:10]],
                y=[importance[i] for i in sorted_idx[:10]],
                text=[f"{v*100:.1f}%" for v in importance[:10]],
                textposition='outside',
                marker_color=px.colors.sequential.Blues_r
            )
        ])
        fig.update_layout(
            title="Top 10 Feature Importance",
            xaxis_title="Features",
            yaxis_title="Importance",
            height=400
        )
        return fig