"""
新闻动态页
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st
import pandas as pd
import json
from datetime import datetime, timedelta

from utils import init_lang, render_lang_switcher, t, get_company_name, load_companies

init_lang()
lang = st.session_state.get("lang", "zh")

st.set_page_config(
    page_title=f"{t('news_dynamics')} - {t('platform_name')}",
    page_icon="📰",
    layout="wide"
)

# 侧边栏
with st.sidebar:
    st.title(f"💊 {t('platform_name')}")
    st.caption(t("platform_subtitle"))
    render_lang_switcher()

st.title(f"📰 {t('news_dynamics')}")
st.caption(t("news_subtitle"))

# 示例新闻数据（中英文）
news_data_zh = [
    {
        "date": "2026-07-07",
        "title": "恒瑞医药HRS-7535 III期临床取得积极结果",
        "company": "恒瑞医药",
        "category": "研发进展",
        "summary": "恒瑞医药宣布其GLP-1受体激动剂HRS-7535在治疗2型糖尿病的III期临床试验中达到主要终点，预计将于今年底提交NDA申请。",
        "source": "公司公告",
        "tag": "重要"
    },
    {
        "date": "2026-07-06",
        "title": "百济神州泽布替尼海外销售持续高增长",
        "company": "百济神州",
        "category": "经营动态",
        "summary": "百济神州公布泽布替尼（百悦泽）二季度全球销售额达5.8亿美元，同比增长42%，美国市场贡献超60%。",
        "source": "公司公告",
        "tag": "重要"
    },
    {
        "date": "2026-07-06",
        "title": "CDE发布《创新药临床试验技术指导原则》修订版",
        "company": "行业政策",
        "category": "政策法规",
        "summary": "国家药监局药品审评中心发布修订后的创新药临床试验技术指导原则，进一步明确早期临床试验设计要求，鼓励以临床价值为导向的创新。",
        "source": "CDE官网",
        "tag": "政策"
    },
    {
        "date": "2026-07-05",
        "title": "科伦博泰TROP2 ADC获FDA快速通道资格",
        "company": "科伦药业",
        "category": "研发进展",
        "summary": "科伦药业子公司科伦博泰宣布，其TROP2 ADC产品SKB264（MK-2870）获美国FDA快速通道资格认定，用于治疗经治三阴性乳腺癌。",
        "source": "公司公告",
        "tag": "重要"
    },
    {
        "date": "2026-07-05",
        "title": "药明康德与全球Top20药企续签多年战略合作",
        "company": "药明康德",
        "category": "经营动态",
        "summary": "药明康德宣布与多家全球Top20制药企业续签多年战略合作协议，涵盖药物发现、开发及生产全流程服务。",
        "source": "公司公告",
        "tag": ""
    },
    {
        "date": "2026-07-04",
        "title": "国家医保局：第八批国家集采落地执行",
        "company": "行业政策",
        "category": "政策法规",
        "summary": "国家医保局宣布第八批国家组织药品集中采购正式在全国落地执行，涉及41种药品，平均降价56%。",
        "source": "国家医保局",
        "tag": "政策"
    },
    {
        "date": "2026-07-04",
        "title": "荣昌生物维迪西妥单抗新适应症获批",
        "company": "荣昌生物",
        "category": "研发进展",
        "summary": "荣昌生物宣布，维迪西妥单抗（爱地希）联合特瑞普利单抗治疗HER2表达胃癌的新适应症获NMPA批准上市。",
        "source": "NMPA",
        "tag": "重要"
    },
    {
        "date": "2026-07-03",
        "title": "信达生物玛仕度肽III期临床达到主要终点",
        "company": "信达生物",
        "category": "研发进展",
        "summary": "信达生物宣布，其GLP-1R/GCGR双激动剂玛仕度肽（IBI362）在肥胖适应症的III期临床试验中达到主要终点，减重效果显著。",
        "source": "公司公告",
        "tag": "重要"
    },
    {
        "date": "2026-07-03",
        "title": "迈瑞医疗海外营收占比首次突破50%",
        "company": "迈瑞医疗",
        "category": "经营动态",
        "summary": "迈瑞医疗发布半年报预告，上半年海外营业收入同比增长超25%，占总营收比例首次突破50%，国际化战略成效显著。",
        "source": "业绩预告",
        "tag": ""
    },
    {
        "date": "2026-07-02",
        "title": "康方生物开坦尼新适应症申报上市",
        "company": "康方生物",
        "category": "研发进展",
        "summary": "康方生物宣布，其PD-1/CTLA-4双抗卡度尼利单抗（开坦尼）用于一线治疗非小细胞肺癌的新适应症上市申请获NMPA受理。",
        "source": "公司公告",
        "tag": "重要"
    },
    {
        "date": "2026-07-02",
        "title": "华润三九完成昆药集团整合",
        "company": "华润三九",
        "category": "并购整合",
        "summary": "华润三九宣布完成对昆药集团的全面整合，整合后公司在中药及OTC领域的市场地位进一步巩固。",
        "source": "公司公告",
        "tag": ""
    },
    {
        "date": "2026-07-01",
        "title": "NMPA发布《药品附条件批准上市申请审评审批工作程序》",
        "company": "行业政策",
        "category": "政策法规",
        "summary": "国家药监局发布修订后的药品附条件批准上市申请审评审批工作程序，自2026年9月1日起施行，进一步优化附条件批准路径。",
        "source": "NMPA官网",
        "tag": "政策"
    },
    {
        "date": "2026-06-30",
        "title": "片仔癀上半年净利润预增15%-20%",
        "company": "片仔癀",
        "category": "经营动态",
        "summary": "片仔癀发布上半年业绩预告，预计归母净利润同比增长15%-20%，核心产品销售持续稳健增长。",
        "source": "业绩预告",
        "tag": ""
    },
    {
        "date": "2026-06-30",
        "title": "联影医疗PET-CT获FDA 510(k) clearance",
        "company": "联影医疗",
        "category": "研发进展",
        "summary": "联影医疗宣布其新一代数字化PET-CT产品获得美国FDA 510(k) clearance，正式进入美国市场。",
        "source": "公司公告",
        "tag": "重要"
    },
    {
        "date": "2026-06-29",
        "title": "泰格医药收购海外CRO公司布局拉美市场",
        "company": "泰格医药",
        "category": "并购整合",
        "summary": "泰格医药宣布收购南美地区一家临床CRO公司，进一步完善全球布局，预计今年内完成交割。",
        "source": "公司公告",
        "tag": ""
    },
]

news_data_en = [
    {
        "date": "2026-07-07",
        "title": "Hengrui's HRS-7535 Shows Positive Phase III Results",
        "company": "恒瑞医药",
        "category": "R&D Progress",
        "summary": "Hengrui announced that its GLP-1 receptor agonist HRS-7535 met primary endpoints in a Phase III trial for type 2 diabetes. NDA submission expected by year-end.",
        "source": "Company Announcement",
        "tag": "Important"
    },
    {
        "date": "2026-07-06",
        "title": "BeiGene's Brukinsa Overseas Sales Continue Strong Growth",
        "company": "百济神州",
        "category": "Business Update",
        "summary": "BeiGene reported Q2 global sales of Brukinsa (zanubrutinib) reached $580 million, up 42% YoY, with US market contributing over 60%.",
        "source": "Company Announcement",
        "tag": "Important"
    },
    {
        "date": "2026-07-06",
        "title": "CDE Releases Revised Guidelines for Innovative Drug Clinical Trials",
        "company": "Industry Policy",
        "category": "Policy & Regulation",
        "summary": "China's CDE released revised technical guidelines for innovative drug clinical trials, further clarifying early trial design requirements and encouraging clinical value-oriented innovation.",
        "source": "CDE Official",
        "tag": "Policy"
    },
    {
        "date": "2026-07-05",
        "title": "Kelun's TROP2 ADC SKB264 Receives FDA Fast Track Designation",
        "company": "科伦药业",
        "category": "R&D Progress",
        "summary": "Kelun Pharma's subsidiary Sichuan Kelun-Biotech announced that its TROP2 ADC SKB264 (MK-2870) received FDA Fast Track designation for previously treated triple-negative breast cancer.",
        "source": "Company Announcement",
        "tag": "Important"
    },
    {
        "date": "2026-07-05",
        "title": "WuXi AppTec Renews Multi-Year Partnerships with Top 20 Pharma",
        "company": "药明康德",
        "category": "Business Update",
        "summary": "WuXi AppTec announced renewal of multi-year strategic partnerships with multiple global Top 20 pharma companies, covering end-to-end drug discovery, development and manufacturing.",
        "source": "Company Announcement",
        "tag": ""
    },
    {
        "date": "2026-07-04",
        "title": "NHSA: 8th Round of National VBP Implemented Nationwide",
        "company": "Industry Policy",
        "category": "Policy & Regulation",
        "summary": "China's National Healthcare Security Administration announced the 8th round of national volume-based procurement is now implemented nationwide, covering 41 drugs with average price reduction of 56%.",
        "source": "NHSA",
        "tag": "Policy"
    },
    {
        "date": "2026-07-04",
        "title": "Remegen's Disitamab Vedotin Approved for New Indication",
        "company": "荣昌生物",
        "category": "R&D Progress",
        "summary": "Remegen announced that disitamab vedotin (Ai Di Xi) combined with toripalimab received NMPA approval for HER2-expressing gastric cancer.",
        "source": "NMPA",
        "tag": "Important"
    },
    {
        "date": "2026-07-03",
        "title": "Innovent's Mazdutide Meets Primary Endpoint in Phase III Obesity Trial",
        "company": "信达生物",
        "category": "R&D Progress",
        "summary": "Innovent announced that its GLP-1R/GCGR dual agonist mazdutide (IBI362) met primary endpoints in a Phase III obesity trial with significant weight reduction.",
        "source": "Company Announcement",
        "tag": "Important"
    },
    {
        "date": "2026-07-03",
        "title": "Mindray's Overseas Revenue Exceeds 50% for First Time",
        "company": "迈瑞医疗",
        "category": "Business Update",
        "summary": "Mindray issued H1 pre-announcement: overseas revenue grew over 25% YoY, exceeding 50% of total revenue for the first time. Internationalization strategy delivering results.",
        "source": "Earnings Preview",
        "tag": ""
    },
    {
        "date": "2026-07-02",
        "title": "Akeso's Cadonilimab NDA Accepted for First-Line NSCLC",
        "company": "康方生物",
        "category": "R&D Progress",
        "summary": "Akeso announced that NMPA accepted the NDA for cadonilimab (Kaitani), its PD-1/CTLA-4 bispecific antibody, for first-line treatment of non-small cell lung cancer.",
        "source": "Company Announcement",
        "tag": "Important"
    },
    {
        "date": "2026-07-02",
        "title": "CR Sanjiu Completes Kunming Pharma Integration",
        "company": "华润三九",
        "category": "M&A",
        "summary": "CR Sanjiu announced completion of full integration of Kunming Pharmaceutical Group, further strengthening market position in TCM and OTC segments.",
        "source": "Company Announcement",
        "tag": ""
    },
    {
        "date": "2026-07-01",
        "title": "NMPA Releases Revised Accelerated Approval Procedures",
        "company": "Industry Policy",
        "category": "Policy & Regulation",
        "summary": "NMPA released revised procedures for conditional approval marketing applications, effective September 1, 2026, further optimizing the accelerated approval pathway.",
        "source": "NMPA Official",
        "tag": "Policy"
    },
    {
        "date": "2026-06-30",
        "title": "Pianzaihuang H1 Net Profit Expected to Grow 15%-20%",
        "company": "片仔癀",
        "category": "Business Update",
        "summary": "Pianzaihuang issued H1 earnings guidance, expecting net profit attributable to shareholders to grow 15%-20% YoY, with steady growth in core product sales.",
        "source": "Earnings Preview",
        "tag": ""
    },
    {
        "date": "2026-06-30",
        "title": "United Imaging's PET-CT Receives FDA 510(k) Clearance",
        "company": "联影医疗",
        "category": "R&D Progress",
        "summary": "United Imaging announced that its next-generation digital PET-CT received FDA 510(k) clearance, officially entering the US market.",
        "source": "Company Announcement",
        "tag": "Important"
    },
    {
        "date": "2026-06-29",
        "title": "Tigermed Acquires Overseas CRO to Expand Latin America",
        "company": "泰格医药",
        "category": "M&A",
        "summary": "Tigermed announced acquisition of a clinical CRO in South America to further expand global footprint. Deal expected to close within this year.",
        "source": "Company Announcement",
        "tag": ""
    },
]

# 根据语言选择新闻数据
news_data = news_data_en if lang == "en" else news_data_zh

# 加载公司信息用于双语显示
companies = load_companies()
company_name_map = {c["name"]: get_company_name(c, lang) for c in companies}
# 行业政策也翻译一下
policy_zh = "行业政策"
policy_en = "Industry Policy"
company_name_map[policy_zh] = policy_en if lang == "en" else policy_zh

# 侧边栏筛选
with st.sidebar:
    st.markdown(f"### 🔍 {t('filter')}")

    # 分类筛选
    categories = [t("all")] + sorted(list(set(n["category"] for n in news_data)))
    selected_category = st.selectbox(t("news_category"), categories, key="news_category")

    # 公司筛选（显示双语名称）
    unique_companies = sorted(list(set(n["company"] for n in news_data if n["company"] != policy_zh)))
    company_display = [t("all")] + [company_name_map.get(c, c) for c in unique_companies]
    selected_company_display = st.selectbox(t("related_company"), company_display, key="news_company")

    # 时间范围
    time_range = st.selectbox(
        t("time_range"),
        [t("time_all"), t("time_7d"), t("time_30d"), t("time_90d")],
        key="news_time"
    )

    st.markdown("---")
    st.caption(f"{len(news_data)} {t('news_count')}")

# 应用筛选
filtered_news = news_data.copy()

all_str = t("all")
if selected_category != all_str:
    filtered_news = [n for n in filtered_news if n["category"] == selected_category]

# 将选中的显示名映射回原始公司名
if selected_company_display != all_str:
    # 反向查找原始公司名
    selected_company_zh = None
    for c in unique_companies:
        if company_name_map.get(c, c) == selected_company_display:
            selected_company_zh = c
            break
    if selected_company_zh:
        filtered_news = [n for n in filtered_news if n["company"] == selected_company_zh]

if time_range != t("time_all"):
    days_map = {t("time_7d"): 7, t("time_30d"): 30, t("time_90d"): 90}
    cutoff = datetime.now() - timedelta(days=days_map.get(time_range, 9999))
    filtered_news = [n for n in filtered_news if datetime.strptime(n["date"], "%Y-%m-%d") >= cutoff]

# 新闻列表
st.markdown(f"### 📑 {t('news_list')}（{len(filtered_news)}）")

for i, news in enumerate(filtered_news):
    tag_label = ""
    if news["tag"]:
        tag_color = "#ff4d4f" if news["tag"] in ["重要", "Important"] else "#1890ff"
        tag_label = f'<span style="background:{tag_color};color:white;padding:2px 8px;border-radius:4px;font-size:12px;">{news["tag"]}</span>'

    company_display = company_name_map.get(news["company"], news["company"])
    with st.expander(
        f"**{news['title']}**  \n📅 {news['date']} | 🏢 {company_display} | 🏷️ {news['category']}",
        expanded=(i == 0)
    ):
        st.markdown(news["summary"])
        st.caption(f"📰 {t('source')}：{news['source']}")

# 月度统计
st.markdown("---")
st.markdown(f"### 📊 {t('news_category_stats')}")

cat_counts = {}
for n in news_data:
    cat = n["category"]
    cat_counts[cat] = cat_counts.get(cat, 0) + 1

cat_col = t("count")
cat_df = pd.DataFrame.from_dict(cat_counts, orient="index", columns=[cat_col])
st.bar_chart(cat_df, color="#2196F3", horizontal=True)

# 每日新闻数
st.markdown(f"### 📈 {t('daily_news_count')}")

date_counts = {}
for n in news_data:
    d = n["date"]
    date_counts[d] = date_counts.get(d, 0) + 1

news_count_col = t("daily_count")
date_df = pd.DataFrame.from_dict(date_counts, orient="index", columns=[news_count_col])
date_df.index = pd.to_datetime(date_df.index)
date_df = date_df.sort_index()
st.line_chart(date_df, color="#4CAF50")

st.markdown("---")
st.info(t("news_tip"))
st.caption(f"📅 {t('data_update')}：2026-07-07 | {t('disclaimer')}")
