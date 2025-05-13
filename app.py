import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import folium
from folium.plugins import HeatMap, MarkerCluster
from streamlit_folium import folium_static
import datetime
import os
from data_processor import DataProcessor

# 设置页面配置
st.set_page_config(page_title="纽约出租车流量可视化分析", page_icon="🚕", layout="wide")

# 页面标题
st.title("纽约出租车流量时空可视化分析")

# 初始化数据处理器
data_processor = DataProcessor()

# 侧边栏 - 数据过滤选项
st.sidebar.header("数据过滤选项")

# 日期选择器
date_min, date_max = data_processor.get_date_range()
selected_date = st.sidebar.date_input(
    "选择日期范围",
    value=(date_min, date_max),
    min_value=date_min,
    max_value=date_max
)

# 时间范围选择器
time_range = st.sidebar.slider(
    "选择时间范围",
    value=(datetime.time(0, 0), datetime.time(23, 59)),
    format="HH:mm"
)

# 工作日/周末选择
day_type = st.sidebar.radio(
    "选择日期类型",
    options=["所有", "工作日", "周末"]
)

# 天气条件选择（模拟数据）
weather_condition = st.sidebar.selectbox(
    "天气条件",
    options=["所有", "晴天", "雨天", "雪天"]
)

# 应用过滤器获取数据
filtered_data = data_processor.filter_data(
    start_date=selected_date[0] if len(selected_date) > 0 else date_min,
    end_date=selected_date[1] if len(selected_date) > 1 else date_max,
    start_time=time_range[0],
    end_time=time_range[1],
    day_type=day_type,
    weather=weather_condition
)

# 主页面内容
st.header("数据概览")

# 显示数据统计信息
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("总行程数", f"{len(filtered_data):,}")
with col2:
    st.metric("平均行程时长", f"{data_processor.get_avg_trip_duration(filtered_data):.1f} 分钟")
with col3:
    avg_miles = data_processor.get_avg_trip_miles(filtered_data)
    st.metric("平均行程距离", f"{avg_miles:.2f} 英里" if avg_miles > 0 else "数据不可用")
with col4:
    avg_fare = data_processor.get_avg_fare(filtered_data)
    st.metric("平均费用", f"${avg_fare:.2f}" if avg_fare > 0 else "数据不可用")

# 创建标签页
tab1, tab2, tab3, tab4 = st.tabs(["热力图", "轨迹聚类", "时间分析", "区域分析"])

# 热力图标签页
with tab1:
    st.subheader("出租车活动热力图")
    
    # 热力图时间滑块
    selected_hour = st.slider("选择小时", 0, 23, 12)
    
    # 获取指定小时的热力图数据
    heatmap_data = data_processor.get_heatmap_data(filtered_data, selected_hour)
    
    # 创建地图
    m = folium.Map(location=[40.7128, -74.0060], zoom_start=11)
    
    # 添加热力图层
    if not heatmap_data.empty:
        HeatMap(data=heatmap_data[['pickup_latitude', 'pickup_longitude', 'weight']].values.tolist(),
                radius=8, max_zoom=13).add_to(m)
    
    # 显示地图
    folium_static(m)

# 轨迹聚类标签页
with tab2:
    st.subheader("热门路线聚类分析")
    
    # 获取聚类数据
    cluster_data = data_processor.get_route_clusters(filtered_data)
    
    # 创建地图
    cluster_map = folium.Map(location=[40.7128, -74.0060], zoom_start=11)
    
    # 添加聚类标记
    if cluster_data is not None:
        for cluster in cluster_data:
            folium.PolyLine(
                locations=cluster['coordinates'],
                color=cluster['color'],
                weight=cluster['weight'],
                opacity=0.7,
                tooltip=f"路线: {cluster['name']} (行程数: {cluster['count']})"
            ).add_to(cluster_map)
    
    # 显示地图
    folium_static(cluster_map)

# 时间分析标签页
with tab3:
    st.subheader("时间分布分析")
    
    # 获取按小时分布的数据
    hourly_data = data_processor.get_hourly_distribution(filtered_data)
    
    # 创建小时分布图表
    fig_hourly = px.line(
        hourly_data, 
        x="pickup_hour", 
        y="count", 
        title="24小时行程分布",
        labels={"pickup_hour": "小时", "count": "行程数"},
        markers=True
    )
    st.plotly_chart(fig_hourly, use_container_width=True)
    
    # 获取工作日vs周末的对比数据
    weekday_vs_weekend = data_processor.get_weekday_weekend_comparison(filtered_data)
    
    # 创建工作日vs周末对比图
    fig_comparison = px.bar(
        weekday_vs_weekend, 
        x="pickup_hour", 
        y="count", 
        color="day_type",
        barmode="group",
        title="工作日 vs 周末行程对比",
        labels={"pickup_hour": "小时", "count": "行程数", "day_type": "日期类型"}
    )
    st.plotly_chart(fig_comparison, use_container_width=True)

# 区域分析标签页
with tab4:
    st.subheader("区域流量分析")
    
    # 获取区域流量数据
    zone_data = data_processor.get_zone_traffic(filtered_data)
    
    # 创建区域流量热力图
    fig_zone = px.choropleth_mapbox(
        zone_data,
        geojson=data_processor.get_zone_geojson(),
        locations="zone_id",
        color="count",
        color_continuous_scale="Viridis",
        mapbox_style="carto-positron",
        zoom=10,
        center={"lat": 40.7128, "lon": -74.0060},
        opacity=0.7,
        labels={"count": "行程数"}
    )
    st.plotly_chart(fig_zone, use_container_width=True)
    
    # 获取区域间流量数据
    zone_flow = data_processor.get_zone_flow(filtered_data)
    
    # 创建区域流量图
    fig_flow = px.scatter_mapbox(
        zone_flow,
        lat="latitude",
        lon="longitude",
        size="count",
        color="type",
        hover_name="zone_name",
        mapbox_style="carto-positron",
        zoom=10,
        center={"lat": 40.7128, "lon": -74.0060},
        opacity=0.7,
        size_max=15,
        labels={"count": "行程数", "type": "类型"}
    )
    
    # 添加连接线
    for _, row in zone_flow.iterrows():
        if row['type'] == 'flow':
            fig_flow.add_trace(
                go.Scattermapbox(
                    lat=[row['start_lat'], row['end_lat']],
                    lon=[row['start_lon'], row['end_lon']],
                    mode='lines',
                    line=dict(width=1, color='rgba(102, 102, 102, 0.5)'),
                    showlegend=False
                )
            )
    
    st.plotly_chart(fig_flow, use_container_width=True)

# 添加页脚
st.markdown("---")
st.markdown("© 2024 纽约出租车流量可视化分析项目")