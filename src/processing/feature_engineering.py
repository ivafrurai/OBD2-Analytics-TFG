def add_temporal_features(df):

    group = df.groupby('segment_file') 
    
    df['coolant_temp_diff'] = group['coolant_temp'].diff().fillna(0)
    df['rpm_diff'] = group['rpm'].diff().fillna(0)
    df['speed_diff'] = group['speed'].diff().fillna(0)
    
    # Las medias móviles también deben ser por grupo para no mezclar viajes
    df['stft_mean'] = group['stft'].transform(lambda x: x.rolling(window=5).mean()).bfill()
    df['MAF_mean'] = group['MAF'].transform(lambda x: x.rolling(window=5).mean()).bfill()

    return df