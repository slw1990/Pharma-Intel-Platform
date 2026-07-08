"""
管线追踪页
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st
import pandas as pd
import json

from utils import (
    load_companies, load_pipeline_data, get_all_pipeline_df,
    init_lang, render_lang_switcher, t,
    get_company_name, get_sector_name, is_bilingual_pipeline
)

init_lang()
lang = st.session_state.get("lang", "zh")

st.set_page_config(
    page_title=f"{t('pipeline_tracking')} - {t('platform_name')}",
    page_icon="💊",
    layout="wide"
)

# 侧边栏
with st.sidebar:
    st.title(f"💊 {t('platform_name')}")
    st.caption(t("platform_subtitle"))
    render_lang_switcher()

st.title(f"💊 {t('pipeline_tracking')}")
st.caption(t("pipeline_subtitle"))

# 加载数据
all_pipe = get_all_pipeline_df(lang=lang)
companies = load_companies()

# 筛选器
st.markdown(f"### 🔍 {t('filter_conditions')}")

col1, col2, col3, col4 = st.columns(4)

with col1:
    # 公司筛选
    company_list = sorted(all_pipe["company"].unique().tolist())
    company_options = [t("all")] + company_list
    selected_company = st.selectbox(t("company"), company_options, key="pipe_company")

with col2:
    # 研发阶段筛选（双语）
    stages = [t("stage_all"), t("stage_marketed"), t("stage_phase3"), t("stage_phase2"), t("stage_phase1"), t("stage_ind"), t("stage_preclinical")]
    selected_stage = st.selectbox(t("rd_stage"), stages, key="pipe_stage")

with col3:
    # 类型筛选
    types = [t("all")] + sorted(all_pipe["type"].unique().tolist())
    selected_type = st.selectbox(t("type"), types, key="pipe_type")

with col4:
    # 靶点搜索
    target_search = st.text_input(t("search_target"), placeholder=t("search_target_placeholder"), key="pipe_target")

# 应用筛选
filtered = all_pipe.copy()

if selected_company != t("all"):
    filtered = filtered[filtered["company"] == selected_company]

if selected_stage != t("stage_all"):
    filtered = filtered[filtered["stage"] == selected_stage]

if selected_type != t("all"):
    filtered = filtered[filtered["type"] == selected_type]

if target_search:
    filtered = filtered[filtered["target"].str.contains(target_search, case=False, na=False)]

st.markdown("---")

# 统计概览
st.markdown(f"### 📊 {t('filter_results')} {len(filtered)} {t('pipeline_items')}")

col1, col2, col3, col4, col5 = st.columns(5)

marketed_stage = "已上市" if lang == "zh" else "Marketed"
phase3_stage = "III期临床" if lang == "zh" else "Phase III"
phase2_stage = "II期临床" if lang == "zh" else "Phase II"
phase1_stage = "I期临床" if lang == "zh" else "Phase I"

marketed = len(filtered[filtered["stage"] == marketed_stage])
phase3 = len(filtered[filtered["stage"].str.contains(phase3_stage, na=False)])
phase2 = len(filtered[filtered["stage"].str.contains(phase2_stage, na=False)])
phase1 = len(filtered[filtered["stage"].str.contains(phase1_stage, na=False)])
companies_count = filtered["company"].nunique()

with col1:
    st.metric(t("companies_involved"), f"{companies_count}")
with col2:
    st.metric(t("marketed"), f"{marketed}")
with col3:
    st.metric(t("phase3"), f"{phase3}")
with col4:
    st.metric(t("phase2"), f"{phase2}")
with col5:
    st.metric(t("phase1_earlier"), f"{phase1}")

st.markdown("---")

# 管线阶段分布图
st.markdown(f"### 📈 {t('stage_distribution')}")

stage_counts = filtered["stage"].value_counts()
st.bar_chart(stage_counts, color="#2196F3", horizontal=True)

st.markdown("---")

# 管线类型分布
st.markdown(f"### 🧬 {t('type_distribution')}")

type_counts = filtered["type"].value_counts().head(15)
st.bar_chart(type_counts, color="#4CAF50", horizontal=True)

st.markdown("---")

# 管线明细表
st.markdown(f"### 📋 {t('pipeline_detail_list')}")

# 阶段排序
if lang == "zh":
    stage_order = {"已上市": 0, "III期临床": 1, "II期临床": 2, "I期临床": 3, "IND阶段": 4, "临床前": 5,
                   "运营中": 6, "增长期": 7, "领先": 8, "特色服务": 9, "布局期": 10, "临床阶段": 11, "快速增长": 12}
else:
    stage_order = {"Marketed": 0, "Phase III": 1, "Phase II": 2, "Phase I": 3, "IND": 4, "Preclinical": 5,
                   "Operational": 6, "Growth Stage": 7, "Leading": 8, "Featured Services": 9, "Planning Stage": 10,
                   "Clinical Stage": 11, "Rapid Growth": 12}

filtered = filtered.copy()
filtered["sort_key"] = filtered["stage"].map(lambda x: stage_order.get(x, 99))
filtered = filtered.sort_values(["sort_key", "company"]).drop("sort_key", axis=1)

# 显示表格
st.dataframe(
    filtered[["company", "name", "type", "stage", "target", "indication", "approval_date"]],
    use_container_width=True,
    hide_index=True,
    column_config={
        "company": t("company"),
        "name": t("product_name"),
        "type": t("type"),
        "stage": t("stage"),
        "target": t("target"),
        "indication": t("indication"),
        "approval_date": t("approval_date")
    }
)

# 靶点云
st.markdown("---")
st.markdown(f"### 🎯 {t('hot_targets')}")

# 中英文排除列表
exclude_targets_zh = ["未披露", "营养支持", "免疫调节", "全球药企", "biotech客户", "药企和biotech",
                    "药企和CRO", "CGT企业", "器械企业", "大型药企", "各科室", "医疗机构",
                    "外伤出血", "活血化瘀", "清热解毒", "补气养血", "补血滋阴", "补钙补锌",
                    "肝细胞修复", "胶原刺激", "皮肤填充", "热毒血瘀", "保肝护肝", "血糖调节",
                    "开窍醒神", "清心化痰", "滋阴补肾", "温补肾阳", "清热解毒开窍", "中风昏迷",
                    "疏风散寒", "回阳救逆", "益气固脱", "止吐", "促凝血", "解热镇痛",
                    "HPV 16/18", "SARS-CoV-2", "HEV", "轮状病毒", "水痘-带状疱疹病毒", "HIV",
                    "HAV/HBV/HCV", "CEA", "白蛋白补充", "止血", "凝血因子VIII",
                    "ICU/手术室/病房", "手术室", "ICU/急救", "急诊/ICU", "检验科", "超声科",
                    "放射科", "核医学科", "放疗科", "公共场所", "宠物医院", "骨科",
                    "核医学", "床旁"]
exclude_targets_en = ["Undisclosed", "Nutritional Support", "Immunomodulation"]
exclude_targets = set(exclude_targets_zh + exclude_targets_en)

all_targets = []
for t_item in all_pipe["target"].dropna():
    if t_item and t_item not in exclude_targets:
        # 拆分复合靶点
        if "/" in t_item:
            all_targets.extend([x.strip() for x in t_item.split("/")])
        else:
            all_targets.append(t_item)

target_counts = pd.Series(all_targets).value_counts().head(20)
st.bar_chart(target_counts, color="#9C27B0", horizontal=True)

st.markdown("---")
st.caption(f"📅 {t('data_update')}：2026年7月 | {t('data_source')}：公司公告、CDE、公开信息整理 | {t('disclaimer')}")
