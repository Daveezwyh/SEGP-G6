from dataprep.clean import clean_df
import pandas as pd

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    使用 DataPrep 自动清理数据。
    处理包括：
    - 缺失值填充
    - 数据类型自动转换
    - 处理异常值
    - 归一化或标准化（可选）
    
    参数：
    df (pd.DataFrame): 需要清理的原始数据。
    
    返回：
    pd.DataFrame: 清理后的数据。
    """
    df_cleaned = clean_df(df)
    return df_cleaned

# 示例用法
if __name__ == "__main__":
    df_sample = pd.DataFrame({
        'age': [25, 30, None, 35, 40, 1000],  # 包含缺失值和异常值
        'salary': [50000, 60000, 70000, None, 90000, 1000000],  # 包含缺失值和异常值
        'gender': ['Male', 'Female', None, 'Male', 'Female', 'Unknown']  # 缺失值和不常见类别
    })
    
    df_cleaned = clean_data(df_sample)
    print(df_cleaned)
