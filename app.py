import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from scipy.stats import chi2_contingency

# 1. 页面基本配置
st.set_page_config(page_title="Insight Engine - 增长分析看板", layout="wide", initial_sidebar_state="expanded")

# 2. 注入高阶极简 CSS
st.markdown("""
    <style>
    .main { background-color: #F9FAFB; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }
    section[data-testid="stSidebar"] { background-color: #FFFFFF !important; border-right: 1px solid #F3F4F6; }
    .mapping-highlight { background-color: #EFF6FF; border-left: 4px solid #3B82F6; padding: 12px 16px; border-radius: 0 8px 8px 0; margin-bottom: 15px; }
    .mapping-highlight h4 { color: #1D4ED8; margin: 0 0 5px 0; font-size: 16px;}
    .mapping-highlight p { color: #3B82F6; margin: 0; font-size: 13px; }
    div[data-testid="stMetric"] { background-color: #FFFFFF; padding: 20px; border-radius: 16px; box-shadow: 0 4px 20px rgba(0, 0, 0, 0.03); border: 1px solid #F3F4F6; }
    div[data-testid="stMetricValue"] { color: #111827; font-weight: 700; }
    div[data-testid="stMetricLabel"] { color: #6B7280; font-weight: 500; }
    </style>
    """, unsafe_allow_html=True)

# 3. Session State 状态管理
if 'raw_data' not in st.session_state:
    st.session_state['raw_data'] = None

# 4. 侧边栏：参数配置中心
with st.sidebar:
    st.markdown("<h2 style='color: #111827; margin-bottom: 0;'>⚡ Insight Engine</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color: #9CA3AF; font-size: 13px; margin-top: 0;'>A/B Testing & Growth Analytics</p>", unsafe_allow_html=True)
    st.divider()
    
    uploaded_file = st.file_uploader("📂 上传最新业务日志 (CSV)", type="csv")
    use_demo = st.button("🚀 加载内置大盘数据 (面试演示)")

    if uploaded_file is not None:
        st.session_state['raw_data'] = pd.read_csv(uploaded_file)
    elif use_demo:
        try:
            st.session_state['raw_data'] = pd.read_csv("user_data.csv")
        except:
            st.error("未找到 user_data.csv")

    if st.session_state['raw_data'] is not None:
        df = st.session_state['raw_data']
        cols = df.columns.tolist()
        
        st.markdown("""
            <div class="mapping-highlight">
                <h4>⚙️ 字段自动映射系统</h4>
                <p>已捕捉底层数据，请确认分析维度是否准确匹配。</p>
            </div>
        """, unsafe_allow_html=True)
        
        # 智能默认值寻找逻辑
        def find_index(keywords, options):
            for i, col in enumerate(options):
                if any(kw in col.lower() for kw in keywords):
                    return i
            return 0
            
        target_geo = st.selectbox("🎯 维度拆解 (切片依据)", cols, index=find_index(['geo', 'region', 'source', 'channel'], cols))
        target_group = st.selectbox("🧪 实验分组 (A/B组)", cols, index=find_index(['group', 'ab', 'layout', 'version'], cols))
        target_metric = st.selectbox("📈 留存指标 (0/1)", cols, index=find_index(['retain', 'purchase', 'convert'], cols))
        
        # 【修复点 1】：新增活跃度字段的动态映射
        target_active = st.selectbox("⏳ 活跃度字段 (如活跃天数)", cols, index=find_index(['active', 'day', 'open', 'visit'], cols))
        
        st.divider()
        st.markdown("<h4 style='color: #374151;'>🎛️ 业务口径定义</h4>", unsafe_allow_html=True)
        
        # 【修复点 2】：滑块的最大值根据上传的数据自动适应
        max_val = 7
        if pd.api.types.is_numeric_dtype(df[target_active]) and not df[target_active].empty:
            max_val = max(1, int(df[target_active].max()))
            
        active_threshold = st.slider("有效激活门槛", 0, max_val, 1)

# 5. 主面板：展示动线
if st.session_state['raw_data'] is not None:
    df = st.session_state['raw_data'].copy()
    
    # --- 数据处理 ---
    total_n = len(df)
    
    # 严苛的类型清洗兜底：确保 target_metric 和 target_active 绝对为数值型
    df[target_metric] = pd.to_numeric(df[target_metric], errors='coerce').fillna(0)
    df[target_active] = pd.to_numeric(df[target_active], errors='coerce').fillna(0)
         
    df['is_active'] = df[target_active] >= active_threshold
    active_n = df['is_active'].sum()
    group_stats = df.groupby(target_group)[target_metric].mean()
    
    # 标题与下钻
    title_col, filter_col = st.columns([2, 1])
    with title_col:
        st.markdown("<h3 style='color: #111827;'>📊 增长实验归因大盘</h3>", unsafe_allow_html=True)
    with filter_col:
        selected_geo = st.selectbox("🔍 实时数据下钻 (筛选维度)", ["全部大盘"] + df[target_geo].unique().tolist())
    
    st.markdown("<br>", unsafe_allow_html=True)

    # --- 第一层：宏观 KPI 概览 ---
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("总参与样本", f"{total_n:,}")
    c2.metric(f"当前口径激活率", f"{(active_n/total_n):.1%}" if total_n > 0 else "0.0%")
    
    # 保护因为异常切片导致的 group_stats 为空的除零及溢界问题
    g1_name = group_stats.index[0] if len(group_stats) > 0 else "未知组"
    g1_val = group_stats.values[0] if len(group_stats) > 0 else 0
    g2_name = group_stats.index[1] if len(group_stats) > 1 else "对照组"
    g2_val = group_stats.values[1] if len(group_stats) > 1 else 0
    
    c3.metric(f"{g1_name} 转化率", f"{g1_val:.1%}")
    c4.metric(f"{g2_name} 转化率", f"{g2_val:.1%}")
    
    st.markdown("<br>", unsafe_allow_html=True)

    # --- 第二层与第三层：可视化分析与结论 ---
    plot_df = df if selected_geo == "全部大盘" else df[df[target_geo] == selected_geo]
    
    # 增加空切片拦截器
    if plot_df.empty:
        st.warning("⚠️ 当前筛选条件下无符合要求的数据，请调整左侧的激活门槛或切换地域。")
    else:
        col_left, col_right = st.columns([1.2, 1])
        
        with col_left:
            counts = [len(plot_df), plot_df['is_active'].sum(), plot_df[target_metric].sum()]
            stages = ["1. 初始分配池", "2. 成功激活", "3. 最终转化"]
            fig_funnel = go.Figure(go.Funnel(
                y=stages, x=counts, textinfo="value+percent initial",
                marker={"color": ["#D1D5DB", "#93C5FD", "#3B82F6"], "line": {"width": 0}}
            ))
            fig_funnel.update_layout(
                title="当前切片转化漏斗", template="plotly_white", height=380, 
                margin=dict(l=20, r=20, t=50, b=20),
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig_funnel, use_container_width=True)
    
        with col_right:
            # 【终极防爆裂修复】：强制重命名聚合后的列名，防止用户选错字段导致的 Pandas 命名冲突
            bar_data = plot_df.groupby(target_group)[target_metric].mean().reset_index(name='核心转化表现')
            fig_bar = px.bar(bar_data, x=target_group, y='核心转化表现', color=target_group, 
                             color_discrete_sequence=["#AEC6CF", "#4A90E2"], text_auto='.1%')
            fig_bar.update_traces(marker_line_width=0, opacity=0.9, textfont=dict(color='white', size=14))
            fig_bar.update_layout(
                title="A/B组核心指标对比", template="plotly_white", height=380,
                xaxis=dict(showgrid=False, zeroline=False, showline=False, title=""),
                yaxis=dict(showgrid=False, zeroline=False, showline=False, showticklabels=False, title=""),
                margin=dict(l=20, r=20, t=50, b=20),
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', showlegend=False
            )
            st.plotly_chart(fig_bar, use_container_width=True)
    
        # --- 第三层：统计检验结论 ---
        # 增加越界保护：防止因切片导致某组人数为 0 时卡方检验报错
        if len(plot_df[target_group].unique()) > 1 and len(plot_df[target_metric].unique()) > 1:
            contingency_table = pd.crosstab(plot_df[target_group], plot_df[target_metric])
            chi2, p, dof, ex = chi2_contingency(contingency_table)
            
            st.markdown("<h4 style='color: #374151;'>🧠 AI 业务洞察与决策建议</h4>", unsafe_allow_html=True)
            
            if p < 0.05:
                st.success(f"**✅ 统计显著 (P-Value: {p:.4f})**：当前维度下实验结果具备显著的统计学意义，证明策略调整带来了实质性影响！")
            else:
                st.warning(f"**⚠️ 差异不显著 (P-Value: {p:.4f})**：当前切片下，两组差异未达到显著标准。可能是被其他维度数据稀释，建议继续切换维度下钻排查。")
        else:
            st.info("⚠️ 当前维度的样本过于单一，无法进行 A/B 显著性检验。")

else:
    st.markdown("""
        <div style='text-align: center; padding: 60px; color: #6B7280; background-color: #FFFFFF; border-radius: 16px; border: 1px dashed #E5E7EB;'>
            <h2 style='color: #3B82F6;'>Welcome to Insight Engine</h2>
            <p>请在左侧栏上传您的 CSV 业务日志，或点击“加载内置大盘数据”开启您的归因分析。</p>
        </div>
    """, unsafe_allow_html=True)
