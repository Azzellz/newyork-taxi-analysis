# 纽约出租车流量时空可视化分析

## 项目概述

本项目是一个基于 Streamlit 开发的交互式数据可视化应用，旨在对纽约市出租车的运行数据进行时空分析和可视化展示。通过多维度的数据分析和直观的可视化界面，帮助用户理解纽约市出租车的流量分布、热门路线、时间规律以及区域特征，为城市交通规划和出行决策提供数据支持。

## 功能特点

### 数据过滤与概览

-   **多维度过滤**：支持按日期范围、时间段、工作日/周末和天气条件进行数据筛选
-   **数据概览**：展示总行程数、平均行程时长、平均行程距离和平均费用等关键指标

### 可视化分析

#### 1. 热力图分析

-   基于地理位置的出租车活动热力图
-   支持按小时查看热力分布变化

#### 2. 轨迹聚类分析

-   使用 DBSCAN 算法对出租车路线进行聚类
-   可视化展示热门路线和流量模式

#### 3. 时间分布分析

-   24 小时行程分布趋势图
-   工作日与周末行程对比分析

#### 4. 区域流量分析

-   区域流量热力地图
-   区域间流量连接图，展示主要区域间的交通流向

## 技术实现

### 数据处理

-   使用 Pandas 和 NumPy 进行数据清洗和预处理
-   采用 DBSCAN 算法进行路线聚类
-   实现区域划分和区域间流量计算

### 可视化技术

-   使用 Streamlit 构建交互式 Web 应用界面
-   采用 Plotly 和 Folium 实现地图可视化
-   支持多种图表类型：热力图、折线图、柱状图、散点图等

## 数据结构

项目使用 Parquet 格式的数据文件，包含以下主要字段：

-   上车时间（pickup_datetime）
-   下车时间（dropoff_datetime）
-   上车位置经纬度（pickup_latitude, pickup_longitude）
-   下车位置经纬度（dropoff_latitude, dropoff_longitude）
-   行程距离（trip_distance）
-   费用信息（fare_amount 等）

## 安装与使用

### 环境要求

-   Python 3.7+
-   依赖包：streamlit, pandas, numpy, plotly, folium, scikit-learn

### 安装步骤

1. 克隆项目到本地

    ```bash
    git clone https://github.com/Azzellz/newyork-taxi-analysis.git
    cd newyork-taxi-analysis
    ```

2. 激活虚拟环境

    ```bash
    python -m venv venv
    source venv/bin/activate  # 在 Windows 上使用 `venv\Scripts\activate`
    ```

3. 安装依赖包

    ```bash
    pip install -r requirements.txt
    ```

4. 下载数据文件
   执行以下命令自动下载数据（数据来源于NYC Taxi & Limousine Commission Trip Record Data）：
    ```bash
    python data_fetch.py
    ```

### 运行应用

```bash
# 启动Streamlit应用
streamlit run app.py
```

应用将在本地启动，通常可通过浏览器访问 http://localhost:8501 查看

## 使用指南

1. **数据过滤**：使用左侧边栏的过滤选项，选择感兴趣的日期范围、时间段、日期类型和天气条件
2. **查看数据概览**：页面顶部显示关键指标统计
3. **热力图分析**：在"热力图"标签页，使用时间滑块查看不同时段的出租车活动热点
4. **轨迹聚类**：在"轨迹聚类"标签页，查看聚类后的热门路线
5. **时间分析**：在"时间分析"标签页，查看行程的时间分布特征
6. **区域分析**：在"区域分析"标签页，查看区域流量分布和区域间流动关系

## 项目扩展

-   集成实时天气 API，获取真实天气数据
-   添加预测模型，预测未来出租车需求
-   扩展更多可视化类型，如 3D 流量图、动态时间演变图等
-   支持更多数据源，如 Uber、Lyft 等网约车数据

## 许可证

本项目采用 MIT 许可证，详情请参阅 LICENSE 文件。
