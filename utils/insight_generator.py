import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
import warnings
from utils.dtypes import categorical_columns, meaningful_numeric_columns
warnings.filterwarnings('ignore')

class InsightGenerator:
    def __init__(self, df):
        self.df = df
        self.insights = []
    
    def generate_all_insights(self):
        """Generate all types of insights"""
        self.insights = []
        
        # 1. Data Quality Insights
        self.get_data_quality_insights()
        
        # 2. Correlation Insights
        self.get_correlation_insights()
        
        # 3. Business Insights
        self.get_business_insights()
        
        # 4. Outlier Insights
        self.get_outlier_insights()
        
        # 5. Recommendation Insights
        self.get_recommendations()
        
        return self.insights
    
    def get_data_quality_insights(self):
        """Data quality analysis"""
        missing_pct = (self.df.isnull().sum().sum() / (self.df.shape[0] * self.df.shape[1])) * 100
        duplicate_pct = (len(self.df) - len(self.df.drop_duplicates())) / len(self.df) * 100
        
        if missing_pct > 5:
            self.insights.append({
                'type': 'warning',
                'title': '⚠️ Missing Values Detected',
                'description': f'Your dataset has {missing_pct:.1f}% missing values. This may affect model accuracy.',
                'recommendation': 'Consider imputing missing values or removing columns with >30% missing data.'
            })
        else:
            self.insights.append({
                'type': 'success',
                'title': '✅ Good Data Quality',
                'description': f'Only {missing_pct:.1f}% missing values. Your data is well-maintained.',
                'recommendation': 'Your data quality is good! Proceed with analysis.'
            })
    
    def get_correlation_insights(self):
        """Find strong correlations"""
        numeric_cols = meaningful_numeric_columns(self.df)
        
        if len(numeric_cols) >= 2:
            corr = self.df[numeric_cols].corr()
            
            # Find top positive correlations
            for i in range(len(corr.columns)):
                for j in range(i+1, len(corr.columns)):
                    if abs(corr.iloc[i, j]) > 0.7:
                        col1 = corr.columns[i]
                        col2 = corr.columns[j]
                        strength = abs(corr.iloc[i, j])
                        direction = 'positive' if corr.iloc[i, j] > 0 else 'negative'
                        
                        self.insights.append({
                            'type': 'insight',
                            'title': f'📊 Strong {direction} correlation',
                            'description': f'"{col1}" and "{col2}" have a {strength:.2f} {direction} correlation.',
                            'recommendation': f'Consider using {col1} to predict {col2}, or investigate why they are related.'
                        })
    
    def get_business_insights(self):
        """Generate business-relevant insights"""
        numeric_cols = meaningful_numeric_columns(self.df)
        categorical_cols = categorical_columns(self.df)
        
        # Find highest and lowest values
        if len(numeric_cols) > 0:
            # Highest value insights
            high_col = numeric_cols[0]
            high_val = self.df[high_col].max()
            high_row = self.df[self.df[high_col] == high_val]
            
            self.insights.append({
                'type': 'insight',
                'title': f'📈 Highest {high_col} detected',
                'description': f'Your highest {high_col} is {high_val:,.2f}.',
                'recommendation': f'Investigate why this is so high. Consider if this is an outlier or a business opportunity.'
            })
            
            # Average insights
            mean_val = self.df[high_col].mean()
            median_val = self.df[high_col].median()
            
            if abs(mean_val - median_val) / mean_val > 0.2:
                self.insights.append({
                    'type': 'warning',
                    'title': '⚡ Skewed distribution detected',
                    'description': f'{high_col} has a skewed distribution (Mean: {mean_val:.2f}, Median: {median_val:.2f}).',
                    'recommendation': 'This suggests outliers or imbalanced data. Consider using median instead of mean.'
                })
        
        # Categorical insights
        if len(categorical_cols) > 0:
            for col in categorical_cols[:2]:
                top_category = self.df[col].value_counts().index[0]
                top_pct = (self.df[col].value_counts().iloc[0] / len(self.df)) * 100
                
                self.insights.append({
                    'type': 'insight',
                    'title': f'🏆 Top {col}',
                    'description': f'"{top_category}" is the most common {col} ({top_pct:.1f}% of data).',
                    'recommendation': f'Focus your strategy on "{top_category}" as it represents your largest segment.'
                })
    
    def get_outlier_insights(self):
        """Detect and explain outliers"""
        numeric_cols = meaningful_numeric_columns(self.df)
        
        for col in numeric_cols[:3]:
            Q1 = self.df[col].quantile(0.25)
            Q3 = self.df[col].quantile(0.75)
            IQR = Q3 - Q1
            lower = Q1 - 1.5 * IQR
            upper = Q3 + 1.5 * IQR
            
            outliers = self.df[(self.df[col] < lower) | (self.df[col] > upper)]
            
            if len(outliers) > len(self.df) * 0.05:
                self.insights.append({
                    'type': 'warning',
                    'title': f'🔍 Outliers found in {col}',
                    'description': f'{len(outliers)} outliers detected ({len(outliers)/len(self.df)*100:.1f}% of data).',
                    'recommendation': f'Review these outliers. They could indicate errors, or they could be valuable insights.'
                })
    
    def get_recommendations(self):
        """Generate actionable recommendations"""
        numeric_cols = meaningful_numeric_columns(self.df)
        
        if len(numeric_cols) >= 2:
            # Coefficient of variation (std/mean) instead of raw variance -
            # raw variance unfairly favors columns with a large numeric
            # range (like a sequential ID) over ones that are genuinely
            # more variable relative to their own scale.
            cv = (self.df[numeric_cols].std() / self.df[numeric_cols].mean().abs()).replace([np.inf, -np.inf], np.nan).dropna()
            if len(cv) > 0:
                most_variant = cv.idxmax()
                self.insights.append({
                    'type': 'recommendation',
                    'title': f'💡 Focus on {most_variant}',
                    'description': f'{most_variant} shows the most relative variation in your data (CV: {cv.max():.2f}).',
                    'recommendation': f'This is where you can have the biggest impact. Focus your analysis on {most_variant}.'
                })
        
        # Customer/segment recommendations
        categorical_cols = categorical_columns(self.df)
        if len(categorical_cols) > 0:
            most_diverse = max(categorical_cols, key=lambda x: self.df[x].nunique())
            
            self.insights.append({
                'type': 'recommendation',
                'title': f'📊 Explore {most_diverse} segments',
                'description': f'{most_diverse} has {self.df[most_diverse].nunique()} unique categories.',
                'recommendation': f'Analyze each {most_diverse} segment separately for deeper insights.'
            })
