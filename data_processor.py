import pandas as pd
import numpy as np
import datetime
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
import matplotlib.colors as mcolors
import random

class DataProcessor:
    def __init__(self):
        # 数据文件路径
        self.data_file = 'reduced_data.parquet'
        # 加载数据
        self.load_data()
        # 初始化区域地理信息
        self.init_zone_geojson()
        
    def load_data(self):
        """加载并预处理数据"""

        # 读取parquet文件
        self.data = pd.read_parquet(self.data_file)
        
        # 确保日期时间列是datetime类型
        if 'pickup_datetime' in self.data.columns:
            self.data['pickup_datetime'] = pd.to_datetime(self.data['pickup_datetime'])
        else:
            # 如果列名不同，尝试找到类似的列
            datetime_cols = [col for col in self.data.columns if 'time' in col.lower() and 'pickup' in col.lower()]
            if datetime_cols:
                self.data['pickup_datetime'] = pd.to_datetime(self.data[datetime_cols[0]])
            else:
                # 如果找不到，使用第一个时间列
                datetime_cols = [col for col in self.data.columns if 'time' in col.lower()]
                if datetime_cols:
                    self.data['pickup_datetime'] = pd.to_datetime(self.data[datetime_cols[0]])
                else:
                    raise ValueError("无法找到日期时间列")
        
        # 同样处理下车时间
        if 'dropoff_datetime' in self.data.columns:
            self.data['dropoff_datetime'] = pd.to_datetime(self.data['dropoff_datetime'])
        else:
            datetime_cols = [col for col in self.data.columns if 'time' in col.lower() and 'drop' in col.lower()]
            if datetime_cols:
                self.data['dropoff_datetime'] = pd.to_datetime(self.data[datetime_cols[0]])
        
        # 确保经纬度列存在
        lat_lon_cols = {
            'pickup_latitude': ['pickup_latitude', 'pickup_lat', 'start_lat'],
            'pickup_longitude': ['pickup_longitude', 'pickup_lon', 'start_lon'],
            'dropoff_latitude': ['dropoff_latitude', 'dropoff_lat', 'end_lat'],
            'dropoff_longitude': ['dropoff_longitude', 'dropoff_lon', 'end_lon']
        }
        
        for target_col, possible_cols in lat_lon_cols.items():
            if target_col not in self.data.columns:
                for col in possible_cols:
                    if col in self.data.columns:
                        self.data[target_col] = self.data[col]
                        break
        
        # 添加额外的时间特征
        self.data['pickup_date'] = self.data['pickup_datetime'].dt.date
        self.data['pickup_hour'] = self.data['pickup_datetime'].dt.hour
        self.data['pickup_day_of_week'] = self.data['pickup_datetime'].dt.dayofweek
        self.data['is_weekend'] = self.data['pickup_day_of_week'].apply(lambda x: 1 if x >= 5 else 0)
        
        # 计算行程时长（分钟）
        if 'dropoff_datetime' in self.data.columns:
            self.data['trip_duration'] = (self.data['dropoff_datetime'] - self.data['pickup_datetime']).dt.total_seconds() / 60
        
        # 模拟天气数据（实际项目中应该使用真实天气API数据）
        weather_conditions = ['晴天', '雨天', '雪天']
        weather_probs = [0.7, 0.2, 0.1]  # 各天气出现概率
        unique_dates = self.data['pickup_date'].unique()
        weather_dict = {}
        
        for date in unique_dates:
            weather_dict[date] = np.random.choice(weather_conditions, p=weather_probs)
        
        self.data['weather'] = self.data['pickup_date'].map(weather_dict)
        
        # 数据清洗：移除异常值
        self.clean_data()
        
    def clean_data(self):
        """清洗数据，移除异常值"""
        # 移除行程距离异常值
        if 'trip_miles' in self.data.columns:
            self.data = self.data[(self.data['trip_miles'] >= 0) & (self.data['trip_miles'] < 100)]
        
        # 移除行程时长异常值
        if 'trip_duration' in self.data.columns:
            self.data = self.data[(self.data['trip_duration'] >= 0) & (self.data['trip_duration'] < 300)]
        
        # 移除经纬度异常值
        lat_cols = ['pickup_latitude', 'dropoff_latitude']
        lon_cols = ['pickup_longitude', 'dropoff_longitude']
        
        for col in lat_cols:
            if col in self.data.columns:
                self.data = self.data[(self.data[col] >= 40.5) & (self.data[col] <= 41.0)]
        
        for col in lon_cols:
            if col in self.data.columns:
                self.data = self.data[(self.data[col] >= -74.3) & (self.data[col] <= -73.7)]
        
        # 如果数据量太大，可以采样减少数据量
        if len(self.data) > 100000:
            self.data = self.data.sample(n=100000, random_state=42)
    
    def init_zone_geojson(self):
        """初始化区域地理信息"""
        # 这里使用简化的区域数据，实际项目中应该使用真实的纽约区域GeoJSON数据
        # 创建一个简单的区域划分（曼哈顿、布鲁克林、皇后区、布朗克斯、斯塔顿岛）
        self.zones = {
            1: {"name": "曼哈顿", "center": [40.7831, -73.9712]},
            2: {"name": "布鲁克林", "center": [40.6782, -73.9442]},
            3: {"name": "皇后区", "center": [40.7282, -73.7949]},
            4: {"name": "布朗克斯", "center": [40.8448, -73.8648]},
            5: {"name": "斯塔顿岛", "center": [40.5795, -74.1502]}
        }
        
        # 创建简化的GeoJSON
        self.zone_geojson = {
            "type": "FeatureCollection",
            "features": []
        }
        
        # 为每个区域创建一个简单的多边形
        for zone_id, zone_info in self.zones.items():
            center = zone_info["center"]
            # 创建一个以中心点为基础的简单矩形
            coords = [
                [center[1] - 0.05, center[0] - 0.05],
                [center[1] + 0.05, center[0] - 0.05],
                [center[1] + 0.05, center[0] + 0.05],
                [center[1] - 0.05, center[0] + 0.05],
                [center[1] - 0.05, center[0] - 0.05]
            ]
            
            feature = {
                "type": "Feature",
                "properties": {
                    "zone_id": zone_id,
                    "name": zone_info["name"]
                },
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [coords]
                }
            }
            
            self.zone_geojson["features"].append(feature)
    
    def get_date_range(self):
        """获取数据集的日期范围"""
        min_date = self.data['pickup_datetime'].min().date()
        max_date = self.data['pickup_datetime'].max().date()
        return min_date, max_date
    
    def filter_data(self, start_date, end_date, start_time, end_time, day_type='所有', weather='所有'):
        """根据条件过滤数据"""
        # 转换日期为datetime.date类型
        if isinstance(start_date, str):
            start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
        if isinstance(end_date, str):
            end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()
        
        # 日期过滤
        filtered = self.data[(self.data['pickup_date'] >= start_date) & (self.data['pickup_date'] <= end_date)]
        
        # 时间过滤
        start_minutes = start_time.hour * 60 + start_time.minute
        end_minutes = end_time.hour * 60 + end_time.minute
        
        pickup_minutes = filtered['pickup_datetime'].dt.hour * 60 + filtered['pickup_datetime'].dt.minute
        filtered = filtered[(pickup_minutes >= start_minutes) & (pickup_minutes <= end_minutes)]
        
        # 工作日/周末过滤
        if day_type == '工作日':
            filtered = filtered[filtered['is_weekend'] == 0]
        elif day_type == '周末':
            filtered = filtered[filtered['is_weekend'] == 1]
        
        # 天气过滤
        if weather != '所有':
            filtered = filtered[filtered['weather'] == weather]
        
        return filtered
    
    def get_avg_trip_duration(self, data):
        """获取平均行程时长（分钟）"""
        if 'trip_duration' in data.columns:
            return data['trip_duration'].mean()
        return 0
    
    def get_avg_trip_miles(self, data):
        """获取平均行程距离（英里）"""
        if 'trip_miles' in data.columns:
            return data['trip_miles'].mean()
        return 0
    
    def get_avg_fare(self, data):
        """获取平均费用"""
        if 'driver_pay' in data.columns:
            return data["driver_pay"].mean()
        return 0
    
    def get_heatmap_data(self, data, hour=None):
        """获取热力图数据"""
        if hour is not None:
            data = data[data['pickup_hour'] == hour]
        
        # 确保有经纬度数据
        if 'pickup_latitude' not in data.columns or 'pickup_longitude' not in data.columns:
            return pd.DataFrame()
        
        # 创建热力图数据
        heatmap_data = data[['pickup_latitude', 'pickup_longitude']].copy()
        # 添加权重列
        heatmap_data['weight'] = 1
        
        return heatmap_data
    
    def get_route_clusters(self, data, min_samples=5, eps=0.01):
        """获取路线聚类数据"""
        if len(data) < min_samples:
            return None
        
        # 确保有起点和终点的经纬度数据
        required_cols = ['pickup_latitude', 'pickup_longitude', 'dropoff_latitude', 'dropoff_longitude']
        if not all(col in data.columns for col in required_cols):
            return None
        
        # 准备聚类数据
        X = data[required_cols].copy()
        
        # 标准化数据
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # 使用DBSCAN进行聚类
        dbscan = DBSCAN(eps=eps, min_samples=min_samples)
        clusters = dbscan.fit_predict(X_scaled)
        
        # 添加聚类标签到数据中
        data_with_clusters = data.copy()
        data_with_clusters['cluster'] = clusters
        
        # 过滤掉噪声点（标签为-1）
        clustered_data = data_with_clusters[data_with_clusters['cluster'] != -1]
        
        # 如果没有有效聚类，返回None
        if len(clustered_data) == 0:
            return None
        
        # 获取聚类结果
        cluster_results = []
        colors = list(mcolors.TABLEAU_COLORS.values())
        
        for cluster_id in sorted(clustered_data['cluster'].unique()):
            cluster_points = clustered_data[clustered_data['cluster'] == cluster_id]
            
            # 计算聚类中心点
            center_lat = cluster_points[['pickup_latitude', 'dropoff_latitude']].values.mean()
            center_lon = cluster_points[['pickup_longitude', 'dropoff_longitude']].values.mean()
            
            # 获取聚类中最常见的路线
            pickup_points = cluster_points[['pickup_latitude', 'pickup_longitude']].values
            dropoff_points = cluster_points[['dropoff_latitude', 'dropoff_longitude']].values
            
            # 创建路线坐标
            coordinates = []
            for i in range(min(5, len(pickup_points))):
                coordinates.append([pickup_points[i][1], pickup_points[i][0]])  # 注意：folium使用[lon, lat]格式
                coordinates.append([dropoff_points[i][1], dropoff_points[i][0]])
            
            # 随机选择颜色
            color = random.choice(colors)
            
            # 计算路线权重（基于该聚类中的行程数量）
            weight = min(5, 1 + len(cluster_points) / 50)
            
            cluster_results.append({
                'name': f'路线 {cluster_id + 1}',
                'coordinates': coordinates,
                'color': color,
                'weight': weight,
                'count': len(cluster_points)
            })
        
        return cluster_results
    
    def get_hourly_distribution(self, data):
        """获取按小时分布的数据"""
        hourly_counts = data.groupby('pickup_hour').size().reset_index(name='count')
        return hourly_counts
    
    def get_weekday_weekend_comparison(self, data):
        """获取工作日vs周末的对比数据"""
        # 按小时和日期类型分组
        grouped = data.groupby(['pickup_hour', 'is_weekend']).size().reset_index(name='count')
        
        # 添加日期类型标签
        grouped['day_type'] = grouped['is_weekend'].apply(lambda x: '周末' if x == 1 else '工作日')
        
        return grouped
    
    def get_zone_traffic(self, data):
        """获取区域流量数据"""
        # 为每个上车点分配区域ID
        def assign_zone(lat, lon):
            min_dist = float('inf')
            assigned_zone = 1  # 默认区域
            
            for zone_id, zone_info in self.zones.items():
                center = zone_info["center"]
                dist = ((lat - center[0]) ** 2 + (lon - center[1]) ** 2) ** 0.5
                if dist < min_dist:
                    min_dist = dist
                    assigned_zone = zone_id
            
            return assigned_zone
        
        # 确保有经纬度数据
        if 'pickup_latitude' not in data.columns or 'pickup_longitude' not in data.columns:
            # 创建一个空的DataFrame，包含必要的列
            return pd.DataFrame({'zone_id': list(self.zones.keys()), 'count': [0] * len(self.zones)})
        
        # 分配区域ID
        data_with_zones = data.copy()
        data_with_zones['zone_id'] = data_with_zones.apply(
            lambda row: assign_zone(row['pickup_latitude'], row['pickup_longitude']), axis=1
        )
        
        # 计算每个区域的行程数
        zone_counts = data_with_zones.groupby('zone_id').size().reset_index(name='count')
        
        # 确保所有区域都在结果中
        for zone_id in self.zones.keys():
            if zone_id not in zone_counts['zone_id'].values:
                zone_counts = pd.concat([zone_counts, pd.DataFrame({'zone_id': [zone_id], 'count': [0]})], ignore_index=True)
        
        return zone_counts
    
    def get_zone_geojson(self):
        """获取区域GeoJSON数据"""
        return self.zone_geojson
    
    def get_zone_flow(self, data):
        """获取区域间流量数据"""
        # 确保有经纬度数据
        required_cols = ['pickup_latitude', 'pickup_longitude', 'dropoff_latitude', 'dropoff_longitude']
        if not all(col in data.columns for col in required_cols):
            # 返回一个包含必要列的空DataFrame
            return pd.DataFrame({
                'zone_id': [], 'zone_name': [], 'latitude': [], 'longitude': [],
                'count': [], 'type': [], 'start_lat': [], 'start_lon': [], 'end_lat': [], 'end_lon': []
            })
        
        # 创建区域流量数据
        flow_data = []
        
        # 添加区域中心点
        for zone_id, zone_info in self.zones.items():
            flow_data.append({
                'zone_id': zone_id,
                'zone_name': zone_info['name'],
                'latitude': zone_info['center'][0],
                'longitude': zone_info['center'][1],
                'count': 0,
                'type': 'center'
            })
        
        # 计算区域间流量
        def assign_zone(lat, lon):
            min_dist = float('inf')
            assigned_zone = 1  # 默认区域
            
            for zone_id, zone_info in self.zones.items():
                center = zone_info["center"]
                dist = ((lat - center[0]) ** 2 + (lon - center[1]) ** 2) ** 0.5
                if dist < min_dist:
                    min_dist = dist
                    assigned_zone = zone_id
            
            return assigned_zone
        
        # 分配起点和终点区域
        data_with_zones = data.copy()
        data_with_zones['pickup_zone'] = data_with_zones.apply(
            lambda row: assign_zone(row['pickup_latitude'], row['pickup_longitude']), axis=1
        )
        data_with_zones['dropoff_zone'] = data_with_zones.apply(
            lambda row: assign_zone(row['dropoff_latitude'], row['dropoff_longitude']), axis=1
        )
        
        # 计算区域间流量
        zone_flows = data_with_zones.groupby(['pickup_zone', 'dropoff_zone']).size().reset_index(name='count')
        
        # 只保留流量较大的区域间连接
        threshold = zone_flows['count'].quantile(0.8) if len(zone_flows) > 0 else 0
        significant_flows = zone_flows[zone_flows['count'] >= threshold]
        
        # 添加区域间流量数据
        for _, flow in significant_flows.iterrows():
            if flow['pickup_zone'] != flow['dropoff_zone']:  # 排除同一区域内的流量
                start_zone = self.zones[flow['pickup_zone']]
                end_zone = self.zones[flow['dropoff_zone']]
                
                flow_data.append({
                    'zone_id': f"{flow['pickup_zone']}-{flow['dropoff_zone']}",
                    'zone_name': f"{start_zone['name']} → {end_zone['name']}",
                    'latitude': (start_zone['center'][0] + end_zone['center'][0]) / 2,
                    'longitude': (start_zone['center'][1] + end_zone['center'][1]) / 2,
                    'start_lat': start_zone['center'][0],
                    'start_lon': start_zone['center'][1],
                    'end_lat': end_zone['center'][0],
                    'end_lon': end_zone['center'][1],
                    'count': flow['count'],
                    'type': 'flow'
                })
        
        return pd.DataFrame(flow_data)