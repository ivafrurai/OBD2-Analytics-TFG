def add_temporal_features(df):
    df['coolant_temp_diff'] = df['coolant_temp'].diff().fillna(0)
    df['rpm_diff'] = df['rpm'].diff().fillna(0)
    df['speed_diff'] = df['speed'].diff().fillna(0)
    df['stft_mean'] = df['stft'].rolling(window = 5).mean().bfill()
    df['MAF_mean'] = df['MAF'].rolling(window = 5).mean().bfill()
    
    return df
