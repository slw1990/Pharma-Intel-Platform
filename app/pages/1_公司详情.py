"""
公司详情页
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st
import pandas as pd
import json

from utils import (
    load_companies, load_stock_quotes, load_financial_metrics,
    load_pipeline_data, get_company_by_name, get_financial_df,
    get_pipeline_df, format_value, init_lang, render_lang_switcher, t,
    get_company_name, get_company_field, get_sector_name,
    get_currency_unit, get_fin_field_name, format_year_date, format_quarter_date
)

init_lang()
lang = st.session_state.get("lang", "zh")

st.set_page_config(
    page_title=f"{t('company_detail')} - {t('platform_name')}",
    page_icon="🏢",
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

st.title(f"🏢 {t('company_detail')}")

# 公司选择器（显示双语名称，内部用中文名匹配）
company_display_names = [get_company_name(c, lang) for c in companies]
company_names = [c["name"] for c in companies]
selected_display = st.selectbox(
    t("select_company"),
    company_display_names,
    index=0,
    key="company_selector"
)

# 找到对应的中文公司名
selected_idx = company_display_names.index(selected_display)
selected_company = company_names[selected_idx]

comp = get_company_by_name(selected_company)
q = quotes.get(selected_company, {})

if comp:
    # 公司头部信息
    col1, col2 = st.columns([3, 1])

    with col1:
        st.markdown(f"## {get_company_name(comp, lang)}")
        st.caption(get_company_field(comp, "full_name", lang))
        st.markdown(f"**{t('sector')}**：{get_sector_name(comp['sector'], lang)}  |  **{t('hq')}**：{comp['headquarters']}")
        st.markdown(get_company_field(comp, "description", lang))
        st.markdown(f"[{t('official_website')}]({comp['website']})")

    with col2:
        # 行情卡片
        st.markdown(f"### 💰 {t('market_data')}")
        if q:
            currency = get_currency_unit(lang)
            st.metric(
                t("latest_price"),
                f"{q['最新价']:.2f} {currency}",
                delta=f"{q['涨跌幅']:+.2f}%",
                delta_color="normal"
            )
            st.markdown(f"**{t('mkt_cap')}**：{format_value(q['总市值'], '亿')}")
            pe_str = f"{q['市盈率']:.1f}x" if q['市盈率'] else '-'
            pb_str = f"{q['市净率']:.1f}x" if q.get('市净率') else '-'
            st.markdown(f"**{t('pe_ratio')}**：{pe_str}")
            st.markdown(f"**{t('pb_ratio')}**：{pb_str}")
        else:
            st.info(t("no_market_data"))

    st.markdown("---")

    # 财务分析
    st.markdown(f"### 📊 {t('financial_analysis')}")

    tab1, tab2, tab3 = st.tabs([t("trend_tab"), t("annual_tab"), t("quarterly_tab")])

    with tab1:
        # 营收和利润趋势图
        fin_df = get_financial_df(selected_company, period="quarterly")
        if not fin_df.empty:
            fin_df_sorted = fin_df.sort_index()

            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**{t('revenue_trend')}**")
                rev_series = fin_df_sorted["营业收入"] / 1e8
                rev_series.name = get_fin_field_name("营业收入", lang)
                st.line_chart(rev_series, color="#2196F3")

            with col2:
                st.markdown(f"**{t('net_profit_trend')}**")
                np_series = fin_df_sorted["归母净利润"] / 1e8
                np_series.name = get_fin_field_name("归母净利润", lang)
                st.line_chart(np_series, color="#4CAF50")

            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**{t('rd_trend')}**")
                rd_series = fin_df_sorted["研发费用"] / 1e8
                rd_series.name = get_fin_field_name("研发费用", lang)
                st.bar_chart(rd_series, color="#9C27B0")

            with col2:
                st.markdown(f"**{t('sales_expense_trend')}**")
                sale_series = fin_df_sorted["销售费用"] / 1e8
                sale_series.name = get_fin_field_name("销售费用", lang)
                st.bar_chart(sale_series, color="#FF9800")
        else:
            st.info(t("no_financial_data"))

    with tab2:
        # 年度对比表
        annual_df = get_financial_df(selected_company, period="annual")
        if not annual_df.empty:
            annual_df = annual_df.sort_index(ascending=False)

            # 格式化显示
            display_df = pd.DataFrame()
            display_df[t("report_period")] = [format_year_date(d, lang) for d in annual_df.index]
            display_df[t("operating_revenue")] = annual_df["营业收入"].apply(lambda x: format_value(x, "亿")).values
            display_df[t("net_profit_attr")] = annual_df["归母净利润"].apply(lambda x: format_value(x, "亿")).values
            display_df[t("rd_expense")] = annual_df["研发费用"].apply(lambda x: format_value(x, "亿")).values
            display_df[t("sales_expense")] = annual_df["销售费用"].apply(lambda x: format_value(x, "亿")).values

            # 计算同比
            if len(annual_df) > 1:
                rev_yoy = []
                np_yoy = []
                values = annual_df.sort_index(ascending=False).values
                for i in range(len(values)):
                    if i < len(values) - 1:
                        rev_y = (values[i][0] - values[i+1][0]) / values[i+1][0] * 100 if values[i+1][0] else 0
                        np_y = (values[i][2] - values[i+1][2]) / values[i+1][2] * 100 if values[i+1][2] else 0
                        rev_yoy.append(f"{rev_y:+.1f}%")
                        np_yoy.append(f"{np_y:+.1f}%")
                    else:
                        rev_yoy.append("-")
                        np_yoy.append("-")
                display_df[t("revenue_yoy")] = rev_yoy
                display_df[t("profit_yoy")] = np_yoy

            st.dataframe(display_df, use_container_width=True, hide_index=True)
        else:
            st.info(t("no_annual_data"))

    with tab3:
        # 季度明细
        fin_df = get_financial_df(selected_company, period="quarterly")
        if not fin_df.empty:
            fin_df = fin_df.sort_index(ascending=False)
            display_df = pd.DataFrame()
            display_df[t("report_period")] = [format_quarter_date(d, lang) for d in fin_df.index]
            display_df[t("operating_revenue")] = fin_df["营业收入"].apply(lambda x: format_value(x, "亿")).values
            display_df[t("net_profit_attr")] = fin_df["归母净利润"].apply(lambda x: format_value(x, "亿")).values
            display_df[t("rd_expense")] = fin_df["研发费用"].apply(lambda x: format_value(x, "亿")).values
            display_df[t("sales_expense")] = fin_df["销售费用"].apply(lambda x: format_value(x, "亿")).values

            st.dataframe(display_df, use_container_width=True, hide_index=True)
        else:
            st.info(t("no_financial_data"))

    st.markdown("---")

    # 管线分析
    st.markdown(f"### 💊 {t('pipeline_analysis')}")

    pipe_df = get_pipeline_df(selected_company, lang=lang)
    if not pipe_df.empty:
        # 统计 - 用中文原始阶段名匹配（内部数据用stage字段，已经按语言切换了）
        total = len(pipe_df)
        
        # 阶段匹配用翻译后的标签
        marketed_stage = "已上市" if lang == "zh" else "Marketed"
        phase3_stage = "III期临床" if lang == "zh" else "Phase III"
        phase2_stage = "II期临床" if lang == "zh" else "Phase II"
        phase1_stage = "I期临床" if lang == "zh" else "Phase I"
        
        marketed = len(pipe_df[pipe_df["stage"] == marketed_stage])
        phase3 = len(pipe_df[pipe_df["stage"].str.contains(phase3_stage if lang=="zh" else "Phase III", na=False)])
        phase2 = len(pipe_df[pipe_df["stage"].str.contains(phase2_stage if lang=="zh" else "Phase II", na=False)])
        phase1 = len(pipe_df[pipe_df["stage"].str.contains(phase1_stage if lang=="zh" else "Phase I", na=False)])

        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.metric(t("total_pipeline"), f"{total}")
        with col2:
            st.metric(t("marketed"), f"{marketed}")
        with col3:
            st.metric(t("phase3"), f"{phase3}")
        with col4:
            st.metric(t("phase2"), f"{phase2}")
        with col5:
            st.metric(t("phase1_earlier"), f"{phase1}")

        st.markdown(f"#### {t('pipeline_detail')}")

        # 阶段筛选（双语选项）
        stage_options = [
            t("stage_all"),
            t("stage_marketed"),
            t("stage_phase3"),
            t("stage_phase2"),
            t("stage_phase1"),
            t("stage_ind"),
            t("stage_preclinical"),
        ]
        selected_stage_label = st.selectbox(t("filter_by_stage"), stage_options, key="stage_filter")

        # 将选中的标签映射回数据中的实际阶段值
        if selected_stage_label == t("stage_all"):
            filtered = pipe_df
        else:
            # 找到对应的阶段值
            stage_value = selected_stage_label  # t()返回的就是当前语言的显示值，和数据中一致
            filtered = pipe_df[pipe_df["stage"] == stage_value]

        # 阶段排序 - 用中英文都兼容的方式
        if lang == "zh":
            stage_order = {"已上市": 0, "III期临床": 1, "II期临床": 2, "I期临床": 3, "IND阶段": 4, "临床前": 5, "运营中": 6, "增长期": 7, "领先": 8, "特色服务": 9, "布局期": 10, "临床阶段": 11, "快速增长": 12}
        else:
            stage_order = {"Marketed": 0, "Phase III": 1, "Phase II": 2, "Phase I": 3, "IND": 4, "Preclinical": 5, "Operational": 6, "Growth Stage": 7, "Leading": 8, "Featured Services": 9, "Planning Stage": 10, "Clinical Stage": 11, "Rapid Growth": 12}
        
        filtered = filtered.copy()
        filtered["sort_key"] = filtered["stage"].map(lambda x: stage_order.get(x, 99))
        filtered = filtered.sort_values("sort_key").drop("sort_key", axis=1)

        # 显示管线表格
        st.dataframe(
            filtered[["name", "type", "stage", "target", "indication", "approval_date"]],
            use_container_width=True,
            hide_index=True,
            column_config={
                "name": t("product_name"),
                "type": t("type"),
                "stage": t("stage"),
                "target": t("target"),
                "indication": t("indication"),
                "approval_date": t("approval_date")
            }
        )
    else:
        st.info(t("no_pipeline_data"))

    st.markdown("---")

    # 联系我们模块
    st.markdown(f"### {t('contact_title')}")
    st.markdown(t('contact_intro'))

    contact_email = t("contact_email")
    company_display = get_company_name(comp, lang)
    subject = t("contact_subject_prefix") + company_display
    # 构建mailto链接
    import urllib.parse
    mailto_link = f"mailto:{contact_email}?subject={urllib.parse.quote(subject)}"

    col_btn, _ = st.columns([1, 3])
    with col_btn:
        st.link_button(
            f"✉️ {t('contact_button')}",
            mailto_link,
            use_container_width=True,
            type="primary"
        )
    st.caption(f"📧 {contact_email}")

    st.markdown("---")
    st.caption(f"📅 {t('data_update')}：2026年7月 | {t('data_source')}：公开财报、公司公告 | {t('disclaimer')}")

else:
    st.error(t("company_not_found"))
