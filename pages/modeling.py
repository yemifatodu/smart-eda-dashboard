import streamlit as st
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import time
from utils.model_trainer import ModelTrainer
from utils.visualizer import Visualizer

def show():
    st.markdown('<h1 class="main-header">🤖 Auto-ML Modeling</h1>', unsafe_allow_html=True)
    
    if st.session_state.data is None:
        st.warning("⚠️ Please upload data first!")
        return
    
    df = st.session_state.data
    trainer = ModelTrainer()
    viz = Visualizer()
    
    # Task selection
    col1, col2 = st.columns(2)
    
    with col1:
        # Detect potential target columns
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
        
        # For classification, we can use categorical or binary numeric
        potential_targets = categorical_cols.copy()
        for col in numeric_cols:
            if df[col].nunique() <= 10:  # Binary/multi-class numeric
                potential_targets.append(col)
        
        target_col = st.selectbox(
            "🎯 Select Target Column",
            potential_targets if potential_targets else df.columns.tolist(),
            help="Select the column you want to predict"
        )
    
    with col2:
        task_type = st.selectbox(
            "📊 Task Type",
            ["Auto-detect", "Classification", "Regression"],
            help="Choose the ML task type"
        )
    
    # Feature selection
    feature_cols = [col for col in df.columns if col != target_col]
    selected_features = st.multiselect(
        "📊 Select Features (Optional - leave empty to use all)",
        feature_cols,
        default=feature_cols[:min(10, len(feature_cols))]
    )
    
    # Training options
    st.markdown("---")
    st.subheader("⚙️ Training Options")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        test_size = st.slider("Test Size", 0.1, 0.4, 0.2, 0.05)
    with col2:
        random_state = st.number_input("Random Seed", 0, 100, 42)
    with col3:
        cv_folds = st.selectbox("CV Folds", [3, 5, 10], index=1)
    
    # Train button
    if st.button("🚀 Train Models", type="primary", use_container_width=True):
        if target_col is None:
            st.error("Please select a target column!")
            return
        
        # Prepare data
        X = df[selected_features] if selected_features else df.drop(columns=[target_col])
        y = df[target_col]
        
        # Detect task type
        if task_type == "Auto-detect":
            if y.dtype == 'object' or y.nunique() <= 10:
                task_type = "Classification"
            else:
                task_type = "Regression"
        
        with st.spinner("Training models... This may take a moment."):
            start_time = time.time()
            
            try:
                # Train models
                results = trainer.train_models(
                    X, y,
                    task_type=task_type,
                    test_size=test_size,
                    random_state=random_state,
                    cv_folds=cv_folds
                )
                
                # Store results
                st.session_state.model_results = results
                
                # Display results
                display_results(results, task_type)
                
                # Feature importance
                if results.get('feature_importance'):
                    st.subheader("📊 Feature Importance")
                    fig = viz.create_feature_importance(
                        results['feature_importance']['features'],
                        results['feature_importance']['importance']
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                training_time = time.time() - start_time
                st.success(f"✅ Models trained successfully in {training_time:.2f} seconds!")
                
            except Exception as e:
                st.error(f"Error training models: {str(e)}")

def display_results(results, task_type):
    """Display model results"""
    st.markdown("---")
    st.subheader("📈 Model Performance")
    
    # Create metrics dataframe
    metrics_df = pd.DataFrame(results['metrics'])
    
    # Display metrics table
    st.dataframe(metrics_df.style.highlight_max(axis=0), use_container_width=True)
    
    # Radar chart for model comparison
    st.subheader("🎯 Model Comparison (Radar Chart)")
    
    # Get metrics for radar
    metric_names = ['accuracy', 'precision', 'recall', 'f1', 'roc_auc'] if task_type == "Classification" else ['r2', 'mae', 'mse', 'rmse']
    available_metrics = [m for m in metric_names if m in metrics_df.columns]
    
    if available_metrics:
        models_dict = {}
        for idx, row in metrics_df.iterrows():
            models_dict[row['Model']] = {m: row[m] for m in available_metrics}
        
        viz = Visualizer()
        fig = viz.create_radar_chart(models_dict, available_metrics)
        st.plotly_chart(fig, use_container_width=True)
    
    # Best model recommendation
    st.subheader("🏆 Best Model Recommendation")
    
    if task_type == "Classification":
        best_idx = metrics_df['accuracy'].idxmax()
    else:
        best_idx = metrics_df['r2'].idxmax()
    
    best_model = metrics_df.iloc[best_idx]
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Best Model", best_model['Model'])
    with col2:
        if task_type == "Classification":
            st.metric("Accuracy", f"{best_model['accuracy']*100:.1f}%")
        else:
            st.metric("R² Score", f"{best_model['r2']:.3f}")
    with col3:
        st.metric("Training Time", f"{best_model['training_time']:.2f}s")