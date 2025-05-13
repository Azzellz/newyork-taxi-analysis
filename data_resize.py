import pandas as pd
import os

def reduce_parquet_size(input_file, output_file, max_size_mb=100, compression="snappy"):
    """
    减少 Parquet 文件的数据量，确保文件不超过指定大小
    :param input_file: 输入 Parquet 文件路径
    :param output_file: 输出 Parquet 文件路径
    :param max_size_mb: 最大文件大小（MB），默认 100MB
    :param compression: 压缩算法（默认 "snappy"），可选 "gzip", "brotli", "zstd"
    """
    # 读取 Parquet 文件
    df = pd.read_parquet(input_file)
    
    # 计算当前文件大小
    current_size_mb = df.memory_usage(deep=True).sum() / (1024 * 1024)
    
    # 如果文件大小超过限制，则进行采样
    if current_size_mb > max_size_mb:
        # 计算采样比例
        sample_ratio = max_size_mb / current_size_mb
        # 随机采样数据
        df = df.sample(frac=sample_ratio, random_state=42)
    
    # 保存为新的 Parquet 文件，并启用压缩
    df.to_parquet(output_file, compression=compression)
    
    # 打印文件大小变化
    original_size = os.path.getsize(input_file) / (1024 * 1024)
    new_size = os.path.getsize(output_file) / (1024 * 1024)
    print(f"原始文件大小: {original_size:.2f} MB")
    print(f"新文件大小: {new_size:.2f} MB")
    print(f"压缩率: {(1 - new_size / original_size) * 100:.2f}%")

# 示例用法
input_file = "data.parquet"  # 输入文件路径
output_file = "reduced_data.parquet"  # 输出文件路径
reduce_parquet_size(input_file, output_file, max_size_mb=100, compression="gzip")
