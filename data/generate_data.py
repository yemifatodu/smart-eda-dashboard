
# Run this to create sample data
import pandas as pd
import numpy as np
from pathlib import Path

def create_sample_data():
    data_dir = Path('data')
    data_dir.mkdir(exist_ok=True)
    
    np.random.seed(42)
    n = 5000
    
    categories = ['Furniture', 'Office Supplies', 'Technology']
    sub_categories = ['Chairs', 'Tables', 'Phones', 'Computers', 'Paper', 'Binders', 'Storage', 'Art']
    regions = ['North', 'South', 'East', 'West']
    segments = ['Consumer', 'Corporate', 'Home Office']
    states = ['CA', 'NY', 'TX', 'FL', 'IL', 'PA', 'OH', 'GA', 'NC', 'MI']
    
    df = pd.DataFrame({
        'Order_ID': [f'ORD-{i:05d}' for i in range(n)],
        'Order_Date': pd.date_range('2023-01-01', periods=n, freq='D'),
        'Ship_Date': pd.date_range('2023-01-03', periods=n, freq='D'),
        'Category': np.random.choice(categories, n, p=[0.3, 0.4, 0.3]),
        'Sub_Category': np.random.choice(sub_categories, n),
        'Region': np.random.choice(regions, n),
        'State': np.random.choice(states, n),
        'Segment': np.random.choice(segments, n, p=[0.4, 0.3, 0.3]),
        'Sales': np.random.uniform(5, 1500, n),
        'Quantity': np.random.poisson(3, n) + 1,
        'Discount': np.random.uniform(0, 0.5, n),
        'Profit': np.random.normal(100, 250, n),
        'Profit_Margin': np.random.uniform(0, 0.8, n),
        'Customer_Count': np.random.poisson(2, n) + 1,
        'Shipping_Cost': np.random.uniform(5, 50, n)
    })
    
    # Ensure profit is reasonable relative to sales
    df['Profit'] = df['Profit'].clip(lower=-df['Sales']*0.5, upper=df['Sales']*0.8)
    
    # Add some missing values for realism
    missing_mask = np.random.random(df.shape) < 0.01
    df = df.mask(missing_mask)
    
    file_path = data_dir / 'sample_superstore.csv'
    df.to_csv(file_path, index=False)
    print(f"✅ Sample data created: {file_path}")
    return df

if __name__ == "__main__":
    create_sample_data()