import streamlit as st
import pandas as pd
import numpy as np
import time
from utils.model_trainer import ModelTrainer
from utils.visualizer import Visualizer
from utils.dtypes import is_categorical_series, categorical_columns
from utils.theme import page_header

def show():
    page_header("brain", "Predict")

    if st.session_state.data is None:
        st.warning("⚠️ Please upload data first!")
        return

    df = st.session_state.data
    trainer = ModelTrainer()

    st.markdown("""
    <div class="ai-panel">
        <div class="ai-panel-header">What do you want to predict?</div>
        <div class="ai-panel-sub">Pick a column and we'll build and compare several models automatically - no setup required.</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<div style='height: 0.75rem'></div>", unsafe_allow_html=True)

    # Detect potential target columns (same detection logic as before,
    # just no longer exposed as a separate "task type" decision the user
    # has to make themselves - we detect it automatically at train time).
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    categorical_cols = categorical_columns(df)
    potential_targets = categorical_cols.copy()
    for col in numeric_cols:
        if df[col].nunique() <= 10:
            potential_targets.append(col)
    if not potential_targets:
        potential_targets = df.columns.tolist()

    target_col = st.selectbox(
        "Column to predict",
        potential_targets,
        help="We'll use every other column in your data to predict this one."
    )

    # Advanced controls - hidden by default. Non-technical users never see
    # CV folds / test size / random seed; analysts who want control can
    # still get it here instead of it being forced on every user.
    test_size, cv_folds, random_state, selected_features = 0.2, 5, 42, []
    with st.expander("⚙️ Advanced options"):
        adv_col1, adv_col2, adv_col3 = st.columns(3)
        with adv_col1:
            test_size = st.slider("Test size", 0.1, 0.4, 0.2, 0.05)
        with adv_col2:
            cv_folds = st.selectbox("Cross-validation folds", [3, 5, 10], index=1)
        with adv_col3:
            random_state = st.number_input("Random seed", 0, 100, 42)
        feature_cols = [c for c in df.columns if c != target_col]
        selected_features = st.multiselect(
            "Features to use (leave empty to use all)",
            feature_cols
        )

    if st.button("Predict", type="primary", use_container_width=True, icon=":material/bolt:"):
        feature_cols = [c for c in df.columns if c != target_col]
        X = df[selected_features] if selected_features else df[feature_cols]
        y = df[target_col]

        if is_categorical_series(y) or y.nunique() <= 10:
            task_type = "Classification"
        else:
            task_type = "Regression"

        with st.spinner("Training and comparing models..."):
            start_time = time.time()
            try:
                results = trainer.train_models(
                    X, y,
                    task_type=task_type,
                    test_size=test_size,
                    random_state=random_state,
                    cv_folds=cv_folds
                )
                st.session_state.model_results = results
                st.session_state.model_task_type = task_type
                st.session_state.model_target = target_col
                training_time = time.time() - start_time
                display_results(results, task_type, target_col, training_time)
            except Exception as e:
                st.error(f"Something went wrong training models on this data: {str(e)}")
                st.caption("This can happen if the target column has too few examples of one category, or if there aren't enough usable rows after removing missing values.")


def display_results(results, task_type, target_col, training_time):
    st.markdown("---")

    metrics_df = pd.DataFrame(results['metrics'])
    if task_type == "Classification":
        best_idx = metrics_df['accuracy'].idxmax()
        score_label = "accuracy"
        score_value = metrics_df.iloc[best_idx]['accuracy']
        score_display = f"{score_value*100:.0f}%"
    else:
        best_idx = metrics_df['r2'].idxmax()
        score_label = "R² score"
        score_value = metrics_df.iloc[best_idx]['r2']
        score_display = f"{score_value:.2f}"
    best_model = metrics_df.iloc[best_idx]

    # Plain-English headline result first - this is what a non-technical
    # user actually needs, before any table or chart.
    quality_word = "strong" if score_value > 0.8 else ("reasonable" if score_value > 0.6 else "weak")
    quality_note = {
        "strong": "ready to use for real decisions.",
        "reasonable": "useful as a starting signal, but treat it as directional.",
        "weak": "worth more data or different features before relying on it.",
    }[quality_word]

    st.markdown(f"""
    <div class="ai-panel">
        <div class="ai-panel-header">✅ We can predict <b>{target_col}</b> with {score_display} {score_label}</div>
        <div class="ai-panel-sub">
            Best approach: <b>{best_model['Model']}</b>. That's a {quality_word} result - {quality_note}
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Best model", best_model['Model'])
    with col2:
        st.metric(score_label.title(), score_display)
    with col3:
        st.metric("Training time", f"{training_time:.1f}s")

    if results.get('feature_importance'):
        st.markdown("#### What matters most")
        viz = Visualizer()
        fig = viz.create_feature_importance(
            results['feature_importance']['features'],
            results['feature_importance']['importance']
        )
        st.plotly_chart(fig, use_container_width=True)

    # Full technical comparison - collapsed by default, for analysts who
    # want to see every model side by side rather than just the winner.
    with st.expander("📊 See the full model comparison"):
        st.dataframe(metrics_df.style.highlight_max(axis=0), use_container_width=True)

        metric_names = ['accuracy', 'precision', 'recall', 'f1', 'roc_auc'] if task_type == "Classification" else ['r2', 'mae', 'mse', 'rmse']
        available_metrics = [m for m in metric_names if m in metrics_df.columns]
        if available_metrics:
            models_dict = {row['Model']: {m: row[m] for m in available_metrics} for _, row in metrics_df.iterrows()}
            viz = Visualizer()
            fig = viz.create_radar_chart(models_dict, available_metrics)
            st.plotly_chart(fig, use_container_width=True)
