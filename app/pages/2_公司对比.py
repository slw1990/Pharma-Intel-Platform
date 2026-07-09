"""
公司对比页
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st
import pandas as pd
import json

from utils import (
    load_companies, load_stock_quotes, load_financial_metrics,
    load_pipeline_data, format_value, init_lang, render_lang_switcher, t,
    get_company_name, get_sector_name, get_pipeline_df, is_bilingual_pipeline,
    get_all_pipeline_df, get_fin_field_name
)

init_lang()
lang = st.session_state.get("lang", "zh")

st.set_page_config(
    page_title=f"{t('company_compare')} - {t('platform_name')}",
    page_icon="⚖️",
    layout="wide"
)

# 加载数据
companies = load_companies()
quotes = load_stock_quotes()
financials = load_financial_metrics()
pipeline = load_pipeline_data()

# 侧边栏
with st.sidebar:
    st.title(f"💊 {t('platform_name')}")
    st.caption(t("platform_subtitle"))
    render_lang_switcher()

st.title(f"⚖️ {t('company_compare')}")
st.caption(t("compare_subtitle"))

# 公司选择（显示双语名称）
company_names = [c["name"] for c in companies]
company_display_names = [get_company_name(c, lang) for c in companies]
default_selection_zh = ["恒瑞医药", "百济神州", "信达生物"]
# 找到默认选中项的显示名
default_display = []
for name in default_selection_zh:
    for c in companies:
        if c["name"] == name:
            default_display.append(get_company_name(c, lang))
            break

selected_display = st.multiselect(
    t("select_to_compare"),
    company_display_names,
    default=default_display,
    max_selections=6,
    key="compare_select"
)

# 映射回中文公司名
selected = []
for disp in selected_display:
    idx = company_display_names.index(disp)
    selected.append(company_names[idx])

if len(selected) < 2:
    st.warning(t("select_at_least_2"))
    st.stop()

st.markdown("---")

# 1. 基本信息对比
st.markdown(f"### 📋 {t('basic_info_compare')}")

basic_data = []
for name in selected:
    comp = next((c for c in companies if c["name"] == name), None)
    q = quotes.get(name, {})
    if comp:
        basic_data.append({
            t("metric"): get_company_name(comp, lang),
            t("sector"): get_sector_name(comp["sector"], lang),
            t("hq"): comp["headquarters"],
            t("a_share_code"): comp["stock_code_sh"] or "-",
            t("hk_share_code"): comp["stock_code_hk"] or "-",
            t("mkt_cap"): format_value(q.get("总市值", 0), "亿"),
            t("pe_ratio"): f"{q['市盈率']:.1f}x" if q.get('市盈率') else "-",
            t("pb_ratio"): f"{q['市净率']:.1f}x" if q.get('市净率') else "-",
        })

basic_df = pd.DataFrame(basic_data).T
basic_df.columns = basic_df.iloc[0]
basic_df = basic_df.drop(t("metric"))
st.dataframe(basic_df, use_container_width=True)

st.markdown("---")

# 2. 财务指标对比
st.markdown(f"### 💰 {t('financial_compare')}")

fin_data = []
for name in selected:
    comp = next((c for c in companies if c["name"] == name), None)
    name_display = get_company_name(comp, lang) if comp else name
    fin = financials.get(name, {})
    # 找2025年报
    annual_2025 = None
    for date in sorted(fin.keys(), reverse=True):
        if "2025-12-31" in date:
            annual_2025 = fin[date]
            break

    if annual_2025:
        rev = annual_2025.get("营业收入", 0)
        np_ = annual_2025.get("归母净利润", 0)
        rd = annual_2025.get("研发费用", 0)
        sale = annual_2025.get("销售费用", 0)

        fin_data.append({
            t("metric"): name_display,
            t("operating_revenue"): format_value(rev, "亿"),
            t("net_profit_attr"): format_value(np_, "亿"),
            t("rd_investment"): format_value(rd, "亿"),
            t("rd_ratio_text"): f"{rd/rev*100:.1f}%" if rev else "-",
            t("sales_expense"): format_value(sale, "亿"),
            t("sales_ratio"): f"{sale/rev*100:.1f}%" if rev else "-",
            t("net_margin"): f"{np_/rev*100:.1f}%" if rev else "-",
        })

if fin_data:
    fin_df = pd.DataFrame(fin_data).T
    fin_df.columns = fin_df.iloc[0]
    fin_df = fin_df.drop(t("metric"))
    st.dataframe(fin_df, use_container_width=True)

    # 营收对比柱状图
    st.markdown(f"#### {t('revenue_compare_chart')}")
    rev_data = {}
    for name in selected:
        comp = next((c for c in companies if c["name"] == name), None)
        name_display = get_company_name(comp, lang) if comp else name
        rev_data[name_display] = financials.get(name, {}).get("2025-12-31", {}).get("营业收入", 0) / 1e8
    rev_df = pd.DataFrame.from_dict(rev_data, orient="index", columns=[get_fin_field_name("营业收入", lang)])
    st.bar_chart(rev_df, color="#2196F3", horizontal=True)

    # 研发投入对比
    st.markdown(f"#### {t('rd_compare_chart')}")
    rd_data = {}
    for name in selected:
        comp = next((c for c in companies if c["name"] == name), None)
        name_display = get_company_name(comp, lang) if comp else name
        rd_data[name_display] = financials.get(name, {}).get("2025-12-31", {}).get("研发费用", 0) / 1e8
    rd_df = pd.DataFrame.from_dict(rd_data, orient="index", columns=[get_fin_field_name("研发费用", lang)])
    st.bar_chart(rd_df, color="#9C27B0", horizontal=True)

st.markdown("---")

# 3. 营收趋势对比
st.markdown(f"### 📈 {t('revenue_trend_compare')}")

col1, col2 = st.columns(2)
with col1:
    st.markdown(f"**{t('revenue_trend')}**")
    # 收集所有公司的季度营收
    trend_data = {}
    for name in selected:
        comp = next((c for c in companies if c["name"] == name), None)
        name_display = get_company_name(comp, lang) if comp else name
        fin = financials.get(name, {})
        dates = sorted(fin.keys())
        values = [fin[d]["营业收入"] / 1e8 for d in dates]
        trend_data[name_display] = pd.Series(values, index=pd.to_datetime(dates))

    trend_df = pd.DataFrame(trend_data)
    trend_df = trend_df.sort_index()
    st.line_chart(trend_df)

with col2:
    st.markdown(f"**{t('np_trend_compare')}**")
    np_trend_data = {}
    for name in selected:
        comp = next((c for c in companies if c["name"] == name), None)
        name_display = get_company_name(comp, lang) if comp else name
        fin = financials.get(name, {})
        dates = sorted(fin.keys())
        values = [fin[d]["归母净利润"] / 1e8 for d in dates]
        np_trend_data[name_display] = pd.Series(values, index=pd.to_datetime(dates))

    np_trend_df = pd.DataFrame(np_trend_data)
    np_trend_df = np_trend_df.sort_index()
    st.line_chart(np_trend_df)

st.markdown("---")

# 4. 管线对比
st.markdown(f"### 💊 {t('pipeline_compare')}")

# 管线数量统计（使用双语数据）
pipe_stats = []
for name in selected:
    comp = next((c for c in companies if c["name"] == name), None)
    name_display = get_company_name(comp, lang) if comp else name
    pipe_df = get_pipeline_df(name, lang=lang)
    
    if not pipe_df.empty:
        total = len(pipe_df)
        
        marketed_stage = "已上市" if lang == "zh" else "Marketed"
        phase3_stage = "III期临床" if lang == "zh" else "Phase III"
        phase2_stage = "II期临床" if lang == "zh" else "Phase II"
        phase1_stage = "I期临床" if lang == "zh" else "Phase I"
        
        marketed = len(pipe_df[pipe_df["stage"] == marketed_stage])
        phase3 = len(pipe_df[pipe_df["stage"].str.contains(phase3_stage, na=False)])
        phase2 = len(pipe_df[pipe_df["stage"].str.contains(phase2_stage, na=False)])
        phase1 = len(pipe_df[pipe_df["stage"].str.contains(phase1_stage, na=False)])
    else:
        total = marketed = phase3 = phase2 = phase1 = 0

    pipe_stats.append({
        t("company"): name_display,
        t("total_pipeline"): total,
        t("marketed"): marketed,
        t("phase3"): phase3,
        t("phase2"): phase2,
        t("phase1_earlier"): phase1,
    })

pipe_stats_df = pd.DataFrame(pipe_stats)
st.dataframe(pipe_stats_df, use_container_width=True, hide_index=True)

# 管线结构对比图
st.markdown(f"#### {t('pipeline_struct_compare')}")
pipe_struct = pd.DataFrame(pipe_stats).set_index(t("company"))[[t("marketed"), t("phase3"), t("phase2"), t("phase1_earlier")]]
st.bar_chart(pipe_struct, color=["#4CAF50", "#2196F3", "#FF9800", "#9E9E9E"])

st.markdown("---")

# 5. 靶点/适应症对比
st.markdown(f"### 🎯 {t('target_platform_compare')}")

for name in selected:
    comp = next((c for c in companies if c["name"] == name), None)
    name_display = get_company_name(comp, lang) if comp else name
    pipe_df = get_pipeline_df(name, lang=lang)
    
    if not pipe_df.empty:
        targets = set()
        types = set()
        for _, p in pipe_df.iterrows():
            t_val = p.get("target", "")
            type_val = p.get("type", "")
            if t_val and t_val not in ["未披露", "Undisclosed", "营养支持", "Nutritional Support"]:
                targets.add(t_val)
            if type_val:
                types.add(type_val)

        with st.expander(f"**{name_display}** - {t('target')} & {t('type')}"):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**{t('main_targets')}**")
                for t_item in sorted(list(targets))[:15]:
                    st.markdown(f"- {t_item}")
            with col2:
                st.markdown(f"**{t('tech_types')}**")
                for t_item in sorted(list(types)):
                    st.markdown(f"- {t_item}")

st.markdown("---")
st.caption(f"📅 {t('data_update')}：2026年7月 | {t('data_source')}：公开财报、公司公告 | {t('disclaimer')}")
