import streamlit as st
import pandas as pd
import numpy as np  # ← ADDED
import plotly.graph_objects as go
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER
import io
import base64
from datetime import datetime

def show():
    st.markdown('<h1 class="main-header">📄 Report Generator</h1>', unsafe_allow_html=True)
    
    if st.session_state.data is None:
        st.warning("⚠️ Please upload data first!")
        return
    
    # Check if we have model results
    has_models = st.session_state.model_results is not None
    
    # Report configuration
    st.subheader("📋 Report Configuration")
    
    col1, col2 = st.columns(2)
    with col1:
        report_title = st.text_input("Report Title", "Smart EDA & Auto-ML Report")
        include_eda = st.checkbox("Include EDA Visualizations", True)
    
    with col2:
        include_models = st.checkbox("Include Model Results", has_models)
        include_summary = st.checkbox("Include Executive Summary", True)
    
    # Generate report button
    if st.button("📥 Generate Report", type="primary", use_container_width=True):
        with st.spinner("Generating your report..."):
            report_data = {
                'title': report_title,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'data_shape': st.session_state.data.shape,
                'include_eda': include_eda,
                'include_models': include_models and has_models,
                'include_summary': include_summary
            }
            
            # Generate HTML report
            html_content = generate_html_report(report_data)
            
            # Provide download buttons
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.download_button(
                    label="📄 Download HTML Report",
                    data=html_content,
                    file_name="eda_report.html",
                    mime="text/html",
                    use_container_width=True
                )
            
            with col2:
                # Generate PDF (ReportLab - no native/GTK dependencies, works on Windows)
                pdf_content = generate_pdf_report(report_data)
                st.download_button(
                    label="📑 Download PDF Report",
                    data=pdf_content,
                    file_name="eda_report.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            
            with col3:
                st.button("🖨️ Print Report", on_click=lambda: st.markdown(
                    '<script>window.print()</script>', unsafe_allow_html=True
                ), use_container_width=True)
            
            # Show preview
            st.success("✅ Report generated successfully!")
            st.markdown("---")
            st.subheader("📄 Report Preview")
            st.components.v1.html(html_content, height=600, scrolling=True)

def generate_html_report(data):
    """Generate HTML report"""
    df = st.session_state.data
    results = st.session_state.model_results
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>{data['title']}</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; }}
            .header {{ text-align: center; padding: 20px; background: #f0f2f6; }}
            .section {{ margin: 30px 0; padding: 20px; border: 1px solid #ddd; }}
            .metric {{ display: inline-block; margin: 10px; padding: 15px; background: #f8f9fa; }}
            table {{ width: 100%%; border-collapse: collapse; }}
            th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
            th {{ background-color: #f0f2f6; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>{data['title']}</h1>
            <p>Generated: {data['timestamp']}</p>
            <p>Dataset: {data['data_shape'][0]:,} rows × {data['data_shape'][1]} columns</p>
        </div>
    """
    
    # Executive Summary
    if data['include_summary']:
        html += """
        <div class="section">
            <h2>📋 Executive Summary</h2>
            <p>This report provides an automated analysis of your dataset using advanced EDA and machine learning techniques.</p>
        """
        
        # Data quality metrics
        missing_pct = (df.isnull().sum().sum() / (df.shape[0] * df.shape[1])) * 100
        duplicate_pct = (len(df) - len(df.drop_duplicates())) / len(df) * 100
        
        html += f"""
            <div>
                <div class="metric"><strong>Data Quality Score:</strong> {100 - missing_pct*0.5 - duplicate_pct*0.3:.0f}%</div>
                <div class="metric"><strong>Missing Values:</strong> {missing_pct:.1f}%</div>
                <div class="metric"><strong>Duplicate Rows:</strong> {duplicate_pct:.1f}%</div>
            </div>
        """
        
        # Key insights
        numeric_cols = df.select_dtypes(include=['number']).columns
        if len(numeric_cols) > 0:
            html += """
            <h3>Key Insights</h3>
            <ul>
            """
            for col in numeric_cols[:3]:
                html += f"<li><strong>{col}:</strong> Mean = {df[col].mean():.2f}, Median = {df[col].median():.2f}</li>"
            html += "</ul>"
        
        html += "</div>"
    
    # EDA Visualizations
    if data['include_eda']:
        html += """
        <div class="section">
            <h2>📊 Exploratory Data Analysis</h2>
            <p>Key visualizations to understand your data distribution and relationships.</p>
        """
        
        # Show correlation matrix
        numeric_cols = df.select_dtypes(include=['number']).columns
        if len(numeric_cols) >= 2:
            corr = df[numeric_cols].corr()
            html += """
            <h3>Correlation Matrix</h3>
            <table>
                <tr><th>Feature</th>
            """
            for col in numeric_cols:
                html += f"<th>{col}</th>"
            html += "</tr>"
            
            for i, col1 in enumerate(numeric_cols):
                html += f"<tr><td><strong>{col1}</strong></td>"
                for col2 in numeric_cols:
                    val = corr.loc[col1, col2]
                    html += f"<td>{val:.2f}</td>"
                html += "</tr>"
            html += "</table>"
        
        # Distribution stats
        if len(numeric_cols) > 0:
            html += """
            <h3>Distribution Statistics</h3>
            <table>
                <tr><th>Feature</th><th>Mean</th><th>Std</th><th>Min</th><th>Max</th></tr>
            """
            for col in numeric_cols:
                html += f"""
                <tr>
                    <td>{col}</td>
                    <td>{df[col].mean():.2f}</td>
                    <td>{df[col].std():.2f}</td>
                    <td>{df[col].min():.2f}</td>
                    <td>{df[col].max():.2f}</td>
                </tr>
                """
            html += "</table>"
        
        html += "</div>"
    
    # Model Results
    if data['include_models'] and results:
        html += """
        <div class="section">
            <h2>🤖 Auto-ML Results</h2>
            <p>Model performance comparison and feature importance analysis.</p>
        """
        
        # Model comparison table
        metrics_df = results['metrics_df']
        html += """
        <h3>Model Performance Comparison</h3>
        <table>
            <tr><th>Model</th>
        """
        for col in metrics_df.columns:
            if col != 'Model':
                html += f"<th>{col}</th>"
        html += "</tr>"
        
        for idx, row in metrics_df.iterrows():
            html += "<tr>"
            for col in metrics_df.columns:
                if col == 'Model':
                    html += f"<td><strong>{row[col]}</strong></td>"
                elif isinstance(row[col], float):
                    html += f"<td>{row[col]:.3f}</td>"
                else:
                    html += f"<td>{row[col]}</td>"
            html += "</tr>"
        html += "</table>"
        
        # Best model
        html += f"""
        <h3>🏆 Best Model: {results['best_model']}</h3>
        <p>Score: {results['best_score']:.3f}</p>
        """
        
        # Feature importance
        if results.get('feature_importance'):
            html += """
            <h3>Feature Importance</h3>
            <ul>
            """
            features = results['feature_importance']['features']
            importance = results['feature_importance']['importance']
            
            # Sort features by importance
            sorted_idx = np.argsort(importance)[::-1]
            for i in sorted_idx[:10]:
                html += f"<li><strong>{features[i]}:</strong> {importance[i]*100:.1f}%</li>"
            html += "</ul>"
        
        html += "</div>"
    
    # Business Recommendations
    html += """
    <div class="section">
        <h2>💡 Business Recommendations</h2>
        <ul>
            <li><strong>Data Quality:</strong> Focus on collecting more complete data to improve model accuracy</li>
            <li><strong>Feature Engineering:</strong> Consider creating new features based on existing ones for better insights</li>
            <li><strong>Model Selection:</strong> Use the best performing model for your prediction tasks</li>
        </ul>
    </div>
    
    <div style="text-align: center; margin-top: 40px; color: #666;">
        <p>Generated by Smart EDA & Auto-ML Dashboard</p>
        <p>© 2024 All Rights Reserved</p>
    </div>
    """
    
    html += "</body></html>"
    return html

def generate_pdf_report(data):
    """Build a PDF report with ReportLab (pure Python, no native GTK
    dependency - this replaces the old weasyprint path which failed on
    Windows with a 'libgobject-2.0-0' load error)."""
    df = st.session_state.data
    results = st.session_state.model_results

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                             topMargin=0.6*inch, bottomMargin=0.6*inch)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('ReportTitle', parent=styles['Title'], alignment=TA_CENTER)
    section_style = ParagraphStyle('Section', parent=styles['Heading2'], spaceBefore=16, spaceAfter=8)
    body_style = styles['BodyText']

    story = []
    story.append(Paragraph(data['title'], title_style))
    story.append(Paragraph(f"Generated: {data['timestamp']}", body_style))
    story.append(Paragraph(
        f"Dataset: {data['data_shape'][0]:,} rows x {data['data_shape'][1]} columns", body_style))
    story.append(Spacer(1, 0.2*inch))

    def make_table(rows, col_widths=None):
        t = Table(rows, colWidths=col_widths, repeatRows=1)
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2D5BFF')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E4E7EC')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F7F8FA')]),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        return t

    if data['include_summary']:
        story.append(Paragraph("Executive Summary", section_style))
        story.append(Paragraph(
            "This report provides an automated analysis of your dataset "
            "using EDA and machine learning techniques.", body_style))

        missing_pct = (df.isnull().sum().sum() / (df.shape[0] * df.shape[1])) * 100
        duplicate_pct = (len(df) - len(df.drop_duplicates())) / len(df) * 100
        quality_score = 100 - missing_pct * 0.5 - duplicate_pct * 0.3

        story.append(Spacer(1, 0.1*inch))
        story.append(make_table([
            ['Metric', 'Value'],
            ['Data Quality Score', f"{quality_score:.0f}%"],
            ['Missing Values', f"{missing_pct:.1f}%"],
            ['Duplicate Rows', f"{duplicate_pct:.1f}%"],
        ], col_widths=[3*inch, 2*inch]))

        numeric_cols = df.select_dtypes(include=['number']).columns
        if len(numeric_cols) > 0:
            story.append(Spacer(1, 0.15*inch))
            story.append(Paragraph("Key Insights", styles['Heading3']))
            for col in numeric_cols[:3]:
                story.append(Paragraph(
                    f"<b>{col}:</b> Mean = {df[col].mean():.2f}, Median = {df[col].median():.2f}",
                    body_style))

    if data['include_eda']:
        story.append(Paragraph("Exploratory Data Analysis", section_style))
        numeric_cols = df.select_dtypes(include=['number']).columns

        if len(numeric_cols) >= 2:
            story.append(Paragraph("Correlation Matrix", styles['Heading3']))
            corr = df[numeric_cols].corr()
            header = ['Feature'] + list(numeric_cols)
            rows = [header]
            for col1 in numeric_cols:
                rows.append([col1] + [f"{corr.loc[col1, col2]:.2f}" for col2 in numeric_cols])
            story.append(make_table(rows))
            story.append(Spacer(1, 0.15*inch))

        if len(numeric_cols) > 0:
            story.append(Paragraph("Distribution Statistics", styles['Heading3']))
            rows = [['Feature', 'Mean', 'Std', 'Min', 'Max']]
            for col in numeric_cols:
                rows.append([
                    col, f"{df[col].mean():.2f}", f"{df[col].std():.2f}",
                    f"{df[col].min():.2f}", f"{df[col].max():.2f}"
                ])
            story.append(make_table(rows))

    if data['include_models'] and results:
        story.append(PageBreak())
        story.append(Paragraph("Auto-ML Results", section_style))
        story.append(Paragraph(
            "Model performance comparison and best-performing model.", body_style))

        metrics_df = results['metrics_df']
        header = list(metrics_df.columns)
        rows = [header]
        for _, row in metrics_df.iterrows():
            rows.append([
                f"{row[c]:.3f}" if isinstance(row[c], float) else str(row[c])
                for c in header
            ])
        story.append(Spacer(1, 0.1*inch))
        story.append(make_table(rows))

        story.append(Spacer(1, 0.15*inch))
        story.append(Paragraph(
            f"<b>Best Model:</b> {results['best_model']} "
            f"(Score: {results['best_score']:.3f})", body_style))

        if results.get('feature_importance'):
            story.append(Paragraph("Feature Importance", styles['Heading3']))
            features = results['feature_importance']['features']
            importance = results['feature_importance']['importance']
            sorted_idx = np.argsort(importance)[::-1]
            for i in sorted_idx[:10]:
                story.append(Paragraph(
                    f"<b>{features[i]}:</b> {importance[i]*100:.1f}%", body_style))

    story.append(Paragraph("Recommendations", section_style))
    for rec in [
        "Data Quality: Focus on collecting more complete data to improve model accuracy",
        "Feature Engineering: Consider creating new features for better insights",
        "Model Selection: Use the best performing model for prediction tasks",
    ]:
        story.append(Paragraph(f"• {rec}", body_style))

    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph(
        "Generated by Smart EDA & Auto-ML Dashboard",
        ParagraphStyle('Footer', parent=styles['Normal'], alignment=TA_CENTER,
                        textColor=colors.grey, fontSize=8)))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()