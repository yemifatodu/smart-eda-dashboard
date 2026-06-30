import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder

class DataProcessor:
    def __init__(self):
        self.label_encoders = {}
    
    def process_data(self, df):
        results = {
            'summary_stats': self.get_summary_stats(df),
            'missing_values': self.get_missing_values(df),
            'data_types': self.get_data_types(df),
            'outliers': self.detect_outliers(df),
            'correlation': self.get_correlation(df),
            'quality_score': self.calculate_quality_score(df)
        }
        return results
    
    def get_summary_stats(self, df):
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        stats = df[numeric_cols].describe()
        return stats
    
    def get_missing_values(self, df):
        missing = df.isnull().sum()
        missing_pct = (missing / len(df) * 100).round(2)
        missing_df = pd.DataFrame({
            'Column': missing.index,
            'Missing_Count': missing.values,
            'Missing_Percentage': missing_pct.values
        })
        return missing_df[missing_df['Missing_Count'] > 0]
    
    def get_data_types(self, df):
        return pd.DataFrame({
            'Column': df.columns,
            'Data_Type': df.dtypes.astype(str),
            'Unique_Values': df.nunique(),
            'Null_Count': df.isnull().sum()
        })
    
    def detect_outliers(self, df, method='iqr'):
        outliers = {}
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            outliers[col] = {
                'lower_bound': lower_bound,
                'upper_bound': upper_bound,
                'outlier_count': len(df[(df[col] < lower_bound) | (df[col] > upper_bound)]),
                'outlier_percentage': (len(df[(df[col] < lower_bound) | (df[col] > upper_bound)]) / len(df)) * 100
            }
        return outliers
    
    def get_correlation(self, df):
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) >= 2:
            return df[numeric_cols].corr()
        return None
    
    def calculate_quality_score(self, df):
        score = 100
        missing_pct = (df.isnull().sum().sum() / (df.shape[0] * df.shape[1])) * 100
        score -= missing_pct * 0.5
        duplicate_pct = (len(df) - len(df.drop_duplicates())) / len(df) * 100
        score -= duplicate_pct * 0.3
        null_columns = df.columns[df.isnull().all()].tolist()
        if null_columns:
            score -= len(null_columns) * 5
        return max(0, int(score))
