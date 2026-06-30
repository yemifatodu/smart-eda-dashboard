import streamlit as st
import pandas as pd
import numpy as np  # ← ADDED
import plotly.graph_objects as go
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
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
                # Try to generate PDF
                pdf_content = generate_pdf_report(html_content)
                if pdf_content:
                    st.download_button(
                        label="📑 Download PDF Report",
                        data=pdf_content,
                        file_name="eda_report.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
                else:
                    st.warning("⚠️ PDF generation requires weasyprint. Install with: pip install weasyprint")
            
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

def generate_pdf_report(html_content):
    """Convert HTML to PDF"""
    try:
        from weasyprint import HTML
        import tempfile
        
        with tempfile.NamedTemporaryFile(suffix='.html', delete=False) as f:
            f.write(html_content.encode('utf-8'))
            html_file = f.name
        
        pdf_file = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
        HTML(html_file).write_pdf(pdf_file.name)
        
        with open(pdf_file.name, 'rb') as f:
            pdf_content = f.read()
        
        return pdf_content
        
    except ImportError:
        return None
    except Exception as e:
        st.warning(f"PDF generation error: {str(e)}")
        return None