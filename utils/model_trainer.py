import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, r2_score, mean_absolute_error, mean_squared_error
from xgboost import XGBClassifier, XGBRegressor
import time
from utils.dtypes import is_categorical_series, categorical_columns

class ModelTrainer:
    def __init__(self):
        self.models = {}
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.target_encoder = None
    
    def prepare_data(self, X, y, task_type='Classification'):
        X_processed = X.copy()
        for col in categorical_columns(X_processed):
            le = LabelEncoder()
            X_processed[col] = le.fit_transform(X_processed[col].astype(str))
            self.label_encoders[col] = le
        
        y_processed = y.copy()
        if is_categorical_series(y_processed):
            le = LabelEncoder()
            y_processed = le.fit_transform(y_processed)
            self.target_encoder = le
            task_type = 'Classification'
        
        numeric_cols = X_processed.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            X_processed[numeric_cols] = self.scaler.fit_transform(X_processed[numeric_cols])
        
        return X_processed, y_processed, task_type
    
    def train_models(self, X, y, task_type='Auto-detect', test_size=0.2, random_state=42, cv_folds=5):
        # Auto-detect task type
        if task_type == 'Auto-detect':
            if is_categorical_series(y) or y.nunique() <= 10:
                task_type = 'Classification'
            else:
                task_type = 'Regression'
        
        X_processed, y_processed, task_type = self.prepare_data(X, y, task_type)
        X_train, X_test, y_train, y_test = train_test_split(
            X_processed, y_processed, test_size=test_size, random_state=random_state
        )
        
        results = {'metrics': [], 'best_model': None, 'best_score': -np.inf}
        
        if task_type == 'Classification':
            models = {
                'Random Forest': RandomForestClassifier(n_estimators=100, random_state=random_state, n_jobs=-1),
                'XGBoost': XGBClassifier(n_estimators=100, random_state=random_state, n_jobs=-1, eval_metric='logloss'),
                'Logistic Regression': LogisticRegression(random_state=random_state, max_iter=1000),
                'Decision Tree': DecisionTreeClassifier(random_state=random_state)
            }
        else:
            models = {
                'Random Forest': RandomForestRegressor(n_estimators=100, random_state=random_state, n_jobs=-1),
                'XGBoost': XGBRegressor(n_estimators=100, random_state=random_state, n_jobs=-1),
                'Linear Regression': LinearRegression(),
                'Decision Tree': DecisionTreeRegressor(random_state=random_state)
            }
        
        for name, model in models.items():
            start_time = time.time()
            model.fit(X_train, y_train)
            training_time = time.time() - start_time
            
            y_pred = model.predict(X_test)
            
            metric_scores = {'Model': name, 'training_time': training_time}
            
            try:
                cv_scores = cross_val_score(model, X_train, y_train, cv=cv_folds, scoring='accuracy' if task_type == 'Classification' else 'r2')
                metric_scores['cv_mean'] = cv_scores.mean()
                metric_scores['cv_std'] = cv_scores.std()
            except:
                metric_scores['cv_mean'] = 0
                metric_scores['cv_std'] = 0
            
            if task_type == 'Classification':
                try:
                    metric_scores['accuracy'] = accuracy_score(y_test, y_pred)
                    metric_scores['precision'] = precision_score(y_test, y_pred, average='weighted', zero_division=0)
                    metric_scores['recall'] = recall_score(y_test, y_pred, average='weighted', zero_division=0)
                    metric_scores['f1'] = f1_score(y_test, y_pred, average='weighted', zero_division=0)
                    
                    if hasattr(model, 'predict_proba') and len(np.unique(y_train)) == 2:
                        try:
                            metric_scores['roc_auc'] = roc_auc_score(y_test, model.predict_proba(X_test)[:, 1])
                        except:
                            metric_scores['roc_auc'] = 0.5
                    else:
                        metric_scores['roc_auc'] = 0.5
                except:
                    metric_scores['accuracy'] = 0
                    metric_scores['precision'] = 0
                    metric_scores['recall'] = 0
                    metric_scores['f1'] = 0
                    metric_scores['roc_auc'] = 0.5
            else:
                try:
                    metric_scores['r2'] = r2_score(y_test, y_pred)
                    metric_scores['mae'] = mean_absolute_error(y_test, y_pred)
                    metric_scores['mse'] = mean_squared_error(y_test, y_pred)
                    metric_scores['rmse'] = np.sqrt(mean_squared_error(y_test, y_pred))
                except:
                    metric_scores['r2'] = 0
                    metric_scores['mae'] = 0
                    metric_scores['mse'] = 0
                    metric_scores['rmse'] = 0
            
            results['metrics'].append(metric_scores)
            
            if task_type == 'Classification':
                score = metric_scores.get('accuracy', 0)
            else:
                score = metric_scores.get('r2', 0)
            
            if score > results['best_score']:
                results['best_score'] = score
                results['best_model'] = name
        
        results['metrics_df'] = pd.DataFrame(results['metrics'])
        results['task_type'] = task_type
        
        return results