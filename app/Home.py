"""
首页 - 行业总览 Dashboard
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st
import pandas as pd
import json

from utils import (
    load_companies, load_stock_quotes, load_financial_metrics,
    format_value, get_sector_list, get_companies_by_sector,
    init_lang, render_lang_switcher, t,
    get_company_name, get_sector_name, get_fin_field_name,
    get_sector_category, get_sector_category_name
)
import plotly.express as px

init_lang()
lang = st.session_state.get("lang", "zh")

st.set_page_config(
    page_title=t("platform_name"),
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 加载数据
companies = load_companies()
quotes = load_stock_quotes()
financials = load_financial_metrics()

# 侧边栏
with st.sidebar:
    st.title(f"💊 {t('platform_name')}")
    st.caption(t("platform_subtitle"))
    render_lang_switcher()
    st.markdown(f"**{t('data_coverage')}**")
    st.markdown(f"- 🏢 {t('companies')}：{len(companies)}")
    st.markdown(f"- 📊 {t('financial_data')}：{len(financials)}")
    st.markdown(f"- 💉 {t('pipeline_data')}：20")
    st.markdown("---")
    st.info(t("sidebar_nav"))

# 主页面
st.title(f"🏥 {t('home_title')}")
st.caption(t("home_subtitle"))

# 赛道分布（5大类饼图）
st.markdown(f"### 🏷️ {t('sector_distribution')}")

# 按5大赛道统计
cat_counts = {}
cat_mkt_cap = {}
for comp in companies:
    cat = get_sector_category(comp["sector"])
    cat_counts[cat] = cat_counts.get(cat, 0) + 1
    q = quotes.get(comp["name"], {})
    cat_mkt_cap[cat] = cat_mkt_cap.get(cat, 0) + q.get("总市值", 0)

# 准备饼图数据
pie_labels = []
pie_values = []
pie_colors = []
for cat in ["创新药", "CXO", "中药", "生物制品", "医疗器械"]:
    if cat in cat_counts:
        cat_name, cat_color = get_sector_category_name(cat, lang)
        pie_labels.append(f"{cat_name} ({cat_counts[cat]})")
        pie_values.append(cat_counts[cat])
        pie_colors.append(cat_color)

# 画饼图
fig = px.pie(
    names=pie_labels,
    values=pie_values,
    color_discrete_sequence=pie_colors,
    hole=0.4,
)
fig.update_traces(
    textposition="inside",
    textinfo="label+percent",
    showlegend=True,
    hovertemplate="%{label}<br>%{value} 家企业<extra></extra>" if lang == "zh" else "%{label}<br>%{value} companies<extra></extra>"
)
fig.update_layout(
    showlegend=True,
    legend=dict(orientation="h", yanchor="bottom", y=-0.1, xanchor="center", x=0.5),
    margin=dict(l=20, r=20, t=20, b=20),
    height=400,
)
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# 公司行情表格
st.markdown(f"### 📋 {t('company_list')}")

# 构建表格数据
table_data = []
for comp in companies:
    name = comp["name"]
    name_display = get_company_name(comp, lang)
    q = quotes.get(name, {})
    # 获取最新年报数据
    fin = financials.get(name, {})
    latest_annual = None
    for date in sorted(fin.keys(), reverse=True):
        if "12-31" in date:
            latest_annual = fin[date]
            break

    row = {
        t("company_name"): name_display,
        t("sector"): get_sector_name(comp["sector"], lang),
        t("latest_price"): f"{q.get('最新价', '-'):.2f}" if q.get('最新价') else "-",
        t("change_pct"): f"{q.get('涨跌幅', 0):+.2f}%" if q.get('涨跌幅') else "-",
        t("mkt_cap"): format_value(q.get("总市值", 0), "亿"),
        t("pe_ratio"): f"{q.get('市盈率', '-'):.1f}x" if q.get('市盈率') else "-",
        t("latest_revenue"): format_value(latest_annual.get("营业收入", 0), "亿") if latest_annual else "-",
        t("latest_net_profit"): format_value(latest_annual.get("归母净利润", 0), "亿") if latest_annual else "-",
        t("rd_investment"): format_value(latest_annual.get("研发费用", 0), "亿") if latest_annual else "-",
    }
    table_data.append(row)

df = pd.DataFrame(table_data)

# 筛选器（5大赛道）
col1, col2 = st.columns([1, 3])
with col1:
    # 5大赛道选项
    cat_options = [t("all")]
    for cat in ["创新药", "CXO", "中药", "生物制品", "医疗器械"]:
        cat_name, _ = get_sector_category_name(cat, lang)
        cat_options.append(cat_name)
    filter_cat_display = st.selectbox(t("filter_sector"), cat_options, key="filter_sector")

# 筛选逻辑
if filter_cat_display != t("all"):
    # 找到对应的大赛道
    filter_cat = None
    for cat in ["创新药", "CXO", "中药", "生物制品", "医疗器械"]:
        cat_name, _ = get_sector_category_name(cat, lang)
        if cat_name == filter_cat_display:
            filter_cat = cat
            break
    if filter_cat:
        # 过滤出属于该大赛道的公司
        filtered_companies = [c for c in companies if get_sector_category(c["sector"]) == filter_cat]
        filtered_names = [get_company_name(c, lang) for c in filtered_companies]
        df = df[df[t("company_name")].isin(filtered_names)]

# 显示表格
st.dataframe(
    df,
    use_container_width=True,
    hide_index=True,
)

st.markdown("---")

# 研发投入排行
st.markdown(f"### 🔬 {t('rd_ranking')}")

rd_data = []
for comp in companies:
    name = comp["name"]
    name_display = get_company_name(comp, lang)
    fin = financials.get(name, {})
    latest_annual = None
    for date in sorted(fin.keys(), reverse=True):
        if "12-31" in date and "2025" in date:
            latest_annual = fin[date]
            break
    if latest_annual and latest_annual.get("研发费用", 0) > 0:
        rd_data.append({
            t("company_name"): name_display,
            t("rd_billion"): round(latest_annual["研发费用"] / 1e8, 2),
            t("revenue_billion"): round(latest_annual["营业收入"] / 1e8, 2),
            t("rd_ratio"): f"{latest_annual['研发费用']/latest_annual['营业收入']*100:.1f}%" if latest_annual["营业收入"] else "-",
        })

rd_df = pd.DataFrame(rd_data).sort_values(t("rd_billion"), ascending=False)
st.bar_chart(rd_df.set_index(t("company_name"))[t("rd_billion")], color="#4CAF50")

st.markdown("---")
st.caption(f"📅 {t('data_update')}：2026年7月 | {t('data_source')}：公开财报、东方财富 | {t('disclaimer')}")
