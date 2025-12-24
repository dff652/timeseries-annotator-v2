import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

def generate_stress_data():
    n = 100000
    start_time = datetime(2025, 1, 1)
    
    print(f"Generating {n} data points...")
    times = [start_time + timedelta(minutes=i) for i in range(n)]
    values = np.sin(np.linspace(0, 100, n)) + np.random.normal(0, 0.1, n)
    
    # Add some anomalies
    values[15000:15010] += 8.0
    values[45000:45050] -= 6.0
    values[80000:80100] += 4.0
    
    df = pd.DataFrame({
        'timestamp': [t.isoformat() for t in times],
        'value': values,
        'series': 'performance_test'
    })
    
    output_path = 'backend/data/stress_test_100k.csv'
    df.to_csv(output_path, index=False)
    print(f"File saved to {output_path}")
    print(f"File size: {os.path.getsize(output_path) / 1024 / 1024:.2f} MB")

if __name__ == '__main__':
    generate_stress_data()
