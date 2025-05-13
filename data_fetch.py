import requests

def download_file(url, save_path):
    """
    下载文件并保存到指定路径
    :param url: 文件的下载链接
    :param save_path: 本地保存路径
    """
    try:
        # 发送 HTTP GET 请求
        response = requests.get(url, stream=True)
        response.raise_for_status()  # 检查请求是否成功

        # 写入文件
        with open(save_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        print(f"文件已成功下载并保存到: {save_path}")
    except requests.exceptions.RequestException as e:
        print(f"下载文件时出错: {e}")

if __name__ == "__main__":
    # 下载链接
    url = "https://d37ci6vzurychx.cloudfront.net/trip-data/fhvhv_tripdata_2024-01.parquet"
    
    # 本地保存路径
    save_path = "data.parquet"
    
    # 下载文件
    download_file(url, save_path)
