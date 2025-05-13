import pandas as pd

def read_and_display_parquet(file_path):
    """
    读取 parquet 文件并展示其总体信息
    :param file_path: parquet 文件的路径
    """
    try:
        # 读取 parquet 文件
        df = pd.read_parquet(file_path)
        
        # 展示总体信息
        print("===== 数据总体信息 =====")
        print(f"行数: {len(df)}")
        print(f"列数: {len(df.columns)}")
        print("\n===== 字段信息 =====")
        print(df.info())
        print("\n===== 前 5 行数据 =====")
        print(df.head())
    except Exception as e:
        print(f"读取或解析 parquet 文件时出错: {e}")

if __name__ == "__main__":
    # parquet 文件路径
    file_path = "reduced_data.parquet"
    # 读取并展示信息
    read_and_display_parquet(file_path)
