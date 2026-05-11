import pandas as pd
from sklearn.ensemble import IsolationForest
import joblib

def fit_df():
    sentinel = IsolationForest(contamination=0.005, random_state=42)
    sentinel.fit(pd.read_csv('data/processed/healthy_diff_scaled.csv'))
    joblib.dump(sentinel, 'src/models/sentinel_model.pkl')



if __name__ == "__main__":
    df_healthy = pd.read_csv('data/processed/healthy_diff_scaled.csv')
    print(df_healthy.shape)
    fit_df()