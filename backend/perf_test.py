import pandas as pd
import numpy as np
from tsdownsample import M4Downsampler
import time
import os

def run_perf_test():
    filepath = 'backend/data/stress_test_100k.csv'
    if not os.path.exists(filepath):
        print("File not found!")
        return

    print(f"--- Performance Test (100k points) ---")
    
    # 1. Loading
    start = time.time()
    df = pd.read_csv(filepath)
    print(f"Pandas Load Time: {time.time() - start:.4f}s")
    
    # 2. Downsampling
    for limit in [5000, 10000, 20000]:
        ds_start = time.time()
        y_values = df['value'].values.astype(np.float64)
        x_values = np.arange(len(y_values), dtype=np.float64)
        
        indices = M4Downsampler().downsample(x_values, y_values, n_out=limit)
        indices = np.sort(indices)
        df_ds = df.iloc[indices]
        print(f"M4 Downsample (limit={limit}) Time: {time.time() - ds_start:.4f}s")

if __name__ == '__main__':
    run_perf_test()
