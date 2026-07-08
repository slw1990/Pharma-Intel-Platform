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
    get_company_name, get_sector_name
)

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

# 顶部核心指标
st.markdown(f"### 📈 {t('market_overview')}")
col1, col2, col3, col4 = st.columns(4)

total_mkt_cap = sum(q["总市值"] for q in quotes.values())
avg_pe = sum(q["市盈率"] for q in quotes.values() if q["市盈率"]) / len([q for q in quotes.values() if q["市盈率"]])
up_count = sum(1 for q in quotes.values() if q["涨跌幅"] > 0)
down_count = sum(1 for q in quotes.values() if q["涨跌幅"] < 0)

with col1:
    st.metric(t("total_mkt_cap"), format_value(total_mkt_cap, "亿"), delta=None)
with col2:
    st.metric(t("avg_pe"), f"{avg_pe:.1f}x", delta=None)
with col3:
    st.metric(t("up_down"), f"{up_count} / {down_count}", delta=None)
with col4:
    st.metric(t("sectors_covered"), "5", delta=None)

st.markdown("---")

# 分赛道统计
st.markdown(f"### 🏷️ {t('sector_distribution')}")
sectors = get_sector_list()
cols = st.columns(len(sectors))

for i, sector in enumerate(sectors):
    sector_companies = get_companies_by_sector(sector)
    sector_mkt_cap = sum(quotes.get(c["name"], {}).get("总市值", 0) for c in sector_companies)
    sector_display = get_sector_name(sector, lang)
    with cols[i]:
        st.metric(
            sector_display,
            f"{len(sector_companies)}{t('companies') if len(sector_companies) > 1 else ''}",
            delta=f"Mkt Cap {format_value(sector_mkt_cap, '亿')}",
            delta_color="off"
        )

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

# 筛选器
col1, col2 = st.columns([1, 3])
with col1:
    sector_options = [t("all")] + [get_sector_name(s, lang) for s in sectors]
    filter_sector_display = st.selectbox(t("filter_sector"), sector_options, key="filter_sector")

# 将显示名称映射回原始赛道名
if filter_sector_display == t("all"):
    filter_sector = t("all")
else:
    filter_sector = None
    for s in sectors:
        if get_sector_name(s, lang) == filter_sector_display:
            filter_sector = s
            break

if filter_sector != t("all") and filter_sector:
    df = df[df[t("sector")] == get_sector_name(filter_sector, lang)]

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
            "公司": name_display,
            t("rd_billion"): round(latest_annual["研发费用"] / 1e8, 2),
            t("revenue_billion"): round(latest_annual["营业收入"] / 1e8, 2),
            t("rd_ratio"): f"{latest_annual['研发费用']/latest_annual['营业收入']*100:.1f}%" if latest_annual["营业收入"] else "-",
        })

rd_df = pd.DataFrame(rd_data).sort_values(t("rd_billion"), ascending=False)
st.bar_chart(rd_df.set_index("公司")[t("rd_billion")], color="#4CAF50")

st.markdown("---")
st.caption(f"📅 {t('data_update')}：2026年7月 | {t('data_source')}：公开财报、东方财富 | {t('disclaimer')}")
