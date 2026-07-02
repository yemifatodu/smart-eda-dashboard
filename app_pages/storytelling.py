import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
from utils.dtypes import categorical_columns, meaningful_numeric_columns

def show():
    st.markdown('<h1 class="main-header">📖 Data Storytelling</h1>', unsafe_allow_html=True)
    
    if st.session_state.data is None:
        st.warning("⚠️ Please upload data first!")
        return
    
    df = st.session_state.data
    
    st.markdown("### 🤖 AI-Generated Data Story")
    st.caption("Automated narrative that explains what your data is telling you")
    
    if st.button("📖 Generate Story", type="primary"):
        with st.spinner("Analyzing your data and crafting a story..."):
            story = generate_story(df)
            st.session_state.story = story
            st.rerun()
    
    if 'story' in st.session_state:
        display_story(st.session_state.story)

def generate_story(df):
    story = {
        'title': generate_title(df),
        'executive_summary': generate_executive_summary(df),
        'key_findings': generate_key_findings(df),
        'insights': generate_insights(df),
        'recommendations': generate_recommendations(df),
        'statistics': generate_statistics(df)
    }
    return story

def generate_title(df):
    # Generate a meaningful title
    numeric_cols = meaningful_numeric_columns(df)
    if len(numeric_cols) > 0:
        main_col = numeric_cols[0]
        return f"📊 Analysis of {main_col}: What the Data Reveals"
    return "📊 Data Analysis: Key Insights and Findings"

def generate_executive_summary(df):
    numeric_cols = meaningful_numeric_columns(df)
    cat_cols = categorical_columns(df)
    
    summary = f"""
    Your dataset contains **{df.shape[0]:,} records** with **{df.shape[1]} attributes**.
    """
    
    if len(numeric_cols) > 0:
        summary += f" The analysis focuses on **{len(numeric_cols)} numeric metrics**"
        if len(cat_cols) > 0:
            summary += f" across **{len(cat_cols)} categorical dimensions**."
        else:
            summary += "."
    
    if len(cat_cols) > 0:
        summary += f" Key categorical variables include: **{', '.join(cat_cols[:3])}**"
    
    summary += f"\n\nData quality assessment: **{calculate_quality_assessment(df)}**"
    
    return summary

def generate_key_findings(df):
    findings = []
    numeric_cols = meaningful_numeric_columns(df)
    cat_cols = categorical_columns(df)
    
    # Find top performers
    if len(numeric_cols) > 0:
        col = numeric_cols[0]
        max_val = df[col].max()
        min_val = df[col].min()
        mean_val = df[col].mean()
        
        findings.append(f"📈 **Highest {col}:** {max_val:,.2f} (The peak performance in your data)")
        findings.append(f"📉 **Lowest {col}:** {min_val:,.2f} (Significant variation in performance)")
        findings.append(f"📊 **Average {col}:** {mean_val:,.2f} (Typical performance level)")
    
    # Find most common category
    if len(cat_cols) > 0:
        col = cat_cols[0]
        top_cat = df[col].value_counts().index[0]
        top_pct = (df[col].value_counts().iloc[0] / len(df)) * 100
        findings.append(f"🏆 **Dominant {col}:** '{top_cat}' ({top_pct:.1f}% of data)")
    
    # Missing values
    missing_pct = (df.isnull().sum().sum() / (df.shape[0] * df.shape[1])) * 100
    if missing_pct > 5:
        findings.append(f"⚠️ **Data Quality:** {missing_pct:.1f}% missing values detected")
    else:
        findings.append(f"✅ **Data Quality:** High quality data with only {missing_pct:.1f}% missing")
    
    return findings

def generate_insights(df):
    insights = []
    numeric_cols = meaningful_numeric_columns(df)
    
    if len(numeric_cols) >= 2:
        # Find correlations
        corr = df[numeric_cols].corr()
        for i in range(len(corr.columns)):
            for j in range(i+1, len(corr.columns)):
                if abs(corr.iloc[i, j]) > 0.5:
                    col1 = corr.columns[i]
                    col2 = corr.columns[j]
                    strength = abs(corr.iloc[i, j])
                    direction = "positive" if corr.iloc[i, j] > 0 else "negative"
                    
                    insights.append({
                        'title': f'Strong {direction} correlation',
                        'detail': f'**{col1}** and **{col2}** have a {strength:.2f} {direction} relationship',
                        'suggestion': f'Consider how changes in {col1} affect {col2}'
                    })
    
    # Distribution insights - scan every meaningful numeric column, not
    # just the first two, so skew in later columns doesn't get missed.
    for col in numeric_cols:
        skew = df[col].skew()
        if abs(skew) > 1:
            direction = "right" if skew > 0 else "left"
            insights.append({
                'title': f'Skewed distribution in {col}',
                'detail': f'The data is {direction}-skewed (skewness: {skew:.2f})',
                'suggestion': f'Consider using median instead of mean for {col}'
            })
    
    return insights[:3]  # Limit to top 3 insights

def generate_recommendations(df):
    recs = []
    numeric_cols = meaningful_numeric_columns(df)
    cat_cols = categorical_columns(df)
    
    if len(numeric_cols) > 0:
        col = numeric_cols[0]
        mean_val = df[col].mean()
        median_val = df[col].median()
        
        if abs(mean_val - median_val) / mean_val > 0.2:
            recs.append("💡 **Use median instead of mean** - Your data shows significant skewness")
    
    if len(cat_cols) > 0:
        recs.append(f"💡 **Analyze {cat_cols[0]} segments** - Different segments may show different patterns")
    
    if len(numeric_cols) >= 2:
        recs.append("💡 **Look for interactions** - Consider how different metrics work together")
    
    recs.append("💡 **Focus on outliers** - Investigate extreme values for opportunities or issues")
    
    return recs

def generate_statistics(df):
    numeric_cols = meaningful_numeric_columns(df)
    stats = {}
    
    for col in numeric_cols[:5]:
        stats[col] = {
            'mean': df[col].mean(),
            'median': df[col].median(),
            'std': df[col].std(),
            'min': df[col].min(),
            'max': df[col].max()
        }
    
    return stats

def calculate_quality_assessment(df):
    missing_pct = (df.isnull().sum().sum() / (df.shape[0] * df.shape[1])) * 100
    duplicate_pct = (len(df) - len(df.drop_duplicates())) / len(df) * 100
    score = 100 - missing_pct * 0.5 - duplicate_pct * 0.3
    
    if score > 85:
        return "Excellent 🌟"
    elif score > 70:
        return "Good 👍"
    elif score > 50:
        return "Fair ⚠️"
    else:
        return "Needs Improvement 🔧"

def display_story(story):
    st.markdown("---")
    
    # Title
    st.markdown(f"## {story['title']}")
    
    # Executive Summary
    st.markdown("### 📋 Executive Summary")
    st.info(story['executive_summary'])
    
    # Key Findings
    st.markdown("### 🔍 Key Findings")
    for finding in story['key_findings']:
        st.write(finding)
    
    # Insights
    st.markdown("### 💡 Key Insights")
    if story['insights']:
        for insight in story['insights']:
            with st.expander(insight['title']):
                st.write(insight['detail'])
                st.caption(f"💡 {insight['suggestion']}")
    else:
        st.caption("No strong correlations or skewed distributions were found — your numeric data looks fairly balanced.")
    
    # Recommendations
    st.markdown("### 🎯 Recommendations")
    for rec in story['recommendations']:
        st.success(rec)
    
    # Statistics
    st.markdown("### 📊 Key Statistics")
    stats_df = pd.DataFrame(story['statistics']).T
    st.dataframe(stats_df, use_container_width=True)
    
    # Export
    st.markdown("---")
    if st.button("📄 Export Story as Report"):
        html = generate_story_html(story)
        st.download_button(
            label="📥 Download Story Report",
            data=html,
            file_name="data_story.html",
            mime="text/html"
        )

def generate_story_html(story):
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Data Story Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; }}
            .header {{ text-align: center; padding: 20px; background: #1f77b4; color: white; }}
            .section {{ margin: 30px 0; padding: 20px; border: 1px solid #ddd; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>{story['title']}</h1>
            <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        <div class="section">
            <h2>Executive Summary</h2>
            <p>{story['executive_summary']}</p>
        </div>
        <div class="section">
            <h2>Key Findings</h2>
            <ul>
                {''.join([f'<li>{f}</li>' for f in story['key_findings']])}
            </ul>
        </div>
        <div class="section">
            <h2>Recommendations</h2>
            <ul>
                {''.join([f'<li>{r}</li>' for r in story['recommendations']])}
            </ul>
        </div>
        <p style="text-align:center;color:#666;margin-top:40px;">
            Generated by Smart EDA & Auto-ML Dashboard
        </p>
    </body>
    </html>
    """
