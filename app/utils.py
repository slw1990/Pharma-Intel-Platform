"""
数据加载工具模块
"""
import json
import os
import pandas as pd

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")

def load_companies():
    """加载公司基础信息（双语版）"""
    bilingual_path = os.path.join(DATA_DIR, "companies_bilingual.json")
    if os.path.exists(bilingual_path):
        with open(bilingual_path, "r", encoding="utf-8") as f:
            return json.load(f)
    with open(os.path.join(DATA_DIR, "companies.json"), "r", encoding="utf-8") as f:
        return json.load(f)

def load_financial_metrics():
    """加载财务指标数据"""
    with open(os.path.join(DATA_DIR, "processed", "financial_metrics.json"), "r", encoding="utf-8") as f:
        return json.load(f)

def load_pipeline_data():
    """加载管线数据（双语版）"""
    bilingual_path = os.path.join(DATA_DIR, "processed", "pipeline_data_bilingual.json")
    if os.path.exists(bilingual_path):
        with open(bilingual_path, "r", encoding="utf-8") as f:
            return json.load(f)
    with open(os.path.join(DATA_DIR, "processed", "pipeline_data.json"), "r", encoding="utf-8") as f:
        return json.load(f)


def is_bilingual_pipeline():
    """检查管线数据是否为双语格式"""
    bilingual_path = os.path.join(DATA_DIR, "processed", "pipeline_data_bilingual.json")
    return os.path.exists(bilingual_path)


def get_pipeline_field(field, lang="zh"):
    """根据语言获取对应字段名"""
    if lang == "en" and field in ["name", "type", "stage", "indication", "target"]:
        return f"{field}_en"
    return field

def load_stock_quotes():
    """加载股票行情数据"""
    with open(os.path.join(DATA_DIR, "processed", "stock_quotes.json"), "r", encoding="utf-8") as f:
        return json.load(f)

def get_company_by_name(name):
    """根据公司名获取公司信息"""
    companies = load_companies()
    for c in companies:
        if c["name"] == name:
            return c
    return None


def get_company_name(company_data, lang="zh"):
    """获取公司名称（根据语言）"""
    if lang == "en" and isinstance(company_data, dict) and "name_en" in company_data:
        return company_data["name_en"]
    if isinstance(company_data, dict):
        return company_data.get("name", "")
    return str(company_data)


def get_company_field(company_data, field, lang="zh"):
    """获取公司字段（根据语言）"""
    if not isinstance(company_data, dict):
        return ""
    if lang == "en":
        en_field = f"{field}_en"
        if en_field in company_data and company_data[en_field]:
            return company_data[en_field]
    return company_data.get(field, "")


def get_sector_category(sector_zh):
    """将细分赛道映射到5大赛道类别"""
    # 创新药大类
    innovative_drugs = [
        "创新药（化学药）", "创新药（生物药）", "创新药+输液",
        "创新药（ADC/自身免疫）", "创新药（双抗/肿瘤免疫）",
        "创新药+医美", "综合制药", "创新药（双抗）", "创新药"
    ]
    # CXO大类
    cxo_list = [
        "CXO（CDMO）", "CXO（临床CRO）", "CXO（临床前+CDMO）",
        "CXO（全产业链）", "CXO"
    ]
    # 中药大类
    tcm_list = [
        "中药+日化", "中药（现代中药/OTC）", "中药（绝密配方）",
        "中药（老字号）", "中药（经典）", "中药（现代）", "中药"
    ]
    # 生物制品大类
    bio_list = [
        "生物制品（疫苗）", "生物制品（血制品+疫苗）",
        "生物制品（疫苗/诊断）", "生物制品"
    ]
    # 医疗器械大类
    device_list = [
        "医疗器械", "医疗器械（影像）"
    ]

    if sector_zh in innovative_drugs:
        return "创新药"
    elif sector_zh in cxo_list:
        return "CXO"
    elif sector_zh in tcm_list:
        return "中药"
    elif sector_zh in bio_list:
        return "生物制品"
    elif sector_zh in device_list:
        return "医疗器械"
    else:
        return "其他"


def get_sector_category_name(category, lang="zh"):
    """获取5大赛道类别的双语名称"""
    cat_map = {
        "创新药": ("Innovative Drug", "#2196F3"),
        "CXO": ("CXO", "#9C27B0"),
        "中药": ("TCM", "#4CAF50"),
        "生物制品": ("Biologics", "#FF9800"),
        "医疗器械": ("Medical Device", "#F44336"),
        "其他": ("Other", "#9E9E9E"),
    }
    if category not in cat_map:
        return (category, "#9E9E9E")
    en_name, color = cat_map[category]
    return (en_name if lang == "en" else category, color)


def get_sector_name(sector_zh, lang="zh"):
    """获取赛道名称（根据语言）"""
    if lang == "zh":
        return sector_zh
    # 英文翻译
    sector_map = {
        "创新药（化学药）": "Innovative Drug (Small Molecule)",
        "创新药（生物药）": "Innovative Drug (Biologics)",
        "创新药+输液": "Innovative Drug + Infusion",
        "创新药（ADC/自身免疫）": "Innovative Drug (ADC/Autoimmune)",
        "创新药（双抗/肿瘤免疫）": "Innovative Drug (Bispecific/Immuno-oncology)",
        "创新药+医美": "Innovative Drug + Medical Aesthetics",
        "创新药（双抗）": "Innovative Drug (Bispecific)",
        "创新药": "Innovative Drug",
        "综合制药": "Integrated Pharma",
        "CXO（CDMO）": "CXO (CDMO)",
        "CXO（临床CRO）": "CXO (Clinical CRO)",
        "CXO（临床前+CDMO）": "CXO (Preclinical + CDMO)",
        "CXO（全产业链）": "CXO (Full-service)",
        "CXO": "CXO",
        "中药+日化": "TCM + Personal Care",
        "中药（现代中药/OTC）": "TCM (Modern/OTC)",
        "中药（绝密配方）": "TCM (Secret Formula)",
        "中药（老字号）": "TCM (Time-honored Brand)",
        "中药（经典）": "TCM (Classic)",
        "中药（现代）": "TCM (Modern)",
        "中药": "TCM",
        "生物制品": "Biologics",
        "生物制品（疫苗）": "Biologics (Vaccine)",
        "生物制品（血制品+疫苗）": "Biologics (Blood + Vaccine)",
        "生物制品（疫苗/诊断）": "Biologics (Vaccine/Diagnostic)",
        "医疗器械": "Medical Device",
        "医疗器械（影像）": "Medical Device (Imaging)",
    }
    return sector_map.get(sector_zh, sector_zh)

def get_financial_df(company_name, period="annual"):
    """获取指定公司的财务DataFrame"""
    metrics = load_financial_metrics()
    if company_name not in metrics:
        return pd.DataFrame()
    
    data = metrics[company_name]
    df = pd.DataFrame.from_dict(data, orient="index")
    df.index = pd.to_datetime(df.index)
    df = df.sort_index(ascending=False)
    
    if period == "annual":
        # 只取年报（12月31日）
        df = df[df.index.month == 12]
    elif period == "quarterly":
        # 取所有季度
        pass
    
    return df

def get_pipeline_df(company_name, lang="zh"):
    """获取指定公司的管线DataFrame"""
    pipeline = load_pipeline_data()
    if company_name not in pipeline:
        return pd.DataFrame()
    
    # 兼容两种数据格式
    if is_bilingual_pipeline():
        drugs = pipeline[company_name]["drugs"]
    else:
        drugs = pipeline[company_name]
    
    df = pd.DataFrame(drugs)
    
    # 如果是英文模式，重命名列以使用英文字段
    if lang == "en" and is_bilingual_pipeline():
        # 用_en字段替换原字段，然后去掉_en后缀方便显示
        for field in ["name", "type", "stage", "indication", "target"]:
            if f"{field}_en" in df.columns:
                df[field] = df[f"{field}_en"]
    
    return df

def get_all_pipeline_df(lang="zh"):
    """获取所有公司的管线DataFrame"""
    pipeline = load_pipeline_data()
    all_data = []
    for company, data in pipeline.items():
        # 兼容两种格式
        if is_bilingual_pipeline():
            drugs = data["drugs"]
        else:
            drugs = data
        for drug in drugs:
            drug_copy = dict(drug)
            drug_copy["company"] = company
            if is_bilingual_pipeline():
                drug_copy["company_en"] = pipeline[company].get("name_en", company)
            all_data.append(drug_copy)
    
    df = pd.DataFrame(all_data)
    
    # 英文模式
    if lang == "en" and is_bilingual_pipeline():
        for field in ["name", "type", "stage", "indication", "target", "company"]:
            en_field = f"{field}_en"
            if en_field in df.columns:
                df[field] = df[en_field]
    
    return df

def format_value(value, unit="亿"):
    """格式化数值显示"""
    if value is None or pd.isna(value):
        return "-"
    if unit == "亿":
        return f"{value/1e8:.2f}亿"
    elif unit == "万":
        return f"{value/1e4:.2f}万"
    elif unit == "%":
        return f"{value*100:.2f}%"
    return f"{value:,.0f}"

def get_sector_list():
    """获取赛道列表"""
    companies = load_companies()
    sectors = list(set(c["sector"] for c in companies))
    return sorted(sectors)

def get_companies_by_sector(sector):
    """按赛道获取公司列表"""
    companies = load_companies()
    return [c for c in companies if c["sector"] == sector]

# ==================== 国际化 i18n ====================

TRANSLATIONS = {
    "zh": {
        # 通用
        "platform_name": "医药情报平台",
        "platform_subtitle": "Pharma Intelligence Platform",
        "data_coverage": "数据覆盖",
        "companies": "家企业",
        "financial_data": "家财务数据",
        "pipeline_data": "家管线数据",
        "sidebar_nav": "👈 左侧菜单导航",
        "data_update": "数据更新时间",
        "data_source": "数据来源",
        "disclaimer": "仅供研究参考",

        # 首页
        "home_title": "中国医药行业总览",
        "home_subtitle": "覆盖创新药、CXO、中药、生物制品、医疗器械五大赛道 · 20家代表性上市企业",
        "market_overview": "市场概览",
        "total_mkt_cap": "总市值（20家）",
        "avg_pe": "平均市盈率",
        "up_down": "上涨/下跌",
        "sectors_covered": "覆盖赛道",
        "sector_distribution": "赛道分布",
        "company_list": "企业行情一览",
        "filter_sector": "筛选赛道",
        "all": "全部",
        "company_name": "公司名称",
        "sector": "赛道",
        "latest_price": "最新价",
        "change_pct": "涨跌幅",
        "mkt_cap": "总市值",
        "pe_ratio": "市盈率",
        "latest_revenue": "最新营收",
        "latest_net_profit": "最新净利润",
        "rd_investment": "研发投入",
        "rd_ranking": "研发投入排行（2025年报）",
        "rd_billion": "研发投入（亿元）",
        "revenue_billion": "营业收入（亿元）",
        "rd_ratio": "研发占比",

        # 公司详情
        "company_detail": "公司详情",
        "select_company": "选择企业",
        "hq": "总部",
        "official_website": "官网",
        "market_data": "行情",
        "pb_ratio": "市净率",
        "no_market_data": "暂无行情数据",
        "financial_analysis": "财务分析",
        "trend_tab": "核心指标趋势",
        "annual_tab": "年度对比",
        "quarterly_tab": "季度数据",
        "revenue_trend": "营业收入趋势（亿元）",
        "net_profit_trend": "归母净利润趋势（亿元）",
        "rd_trend": "研发投入趋势（亿元）",
        "sales_expense_trend": "销售费用趋势（亿元）",
        "no_financial_data": "暂无财务数据",
        "report_period": "报告期",
        "operating_revenue": "营业收入",
        "net_profit_attr": "归母净利润",
        "rd_expense": "研发费用",
        "sales_expense": "销售费用",
        "revenue_yoy": "营收同比",
        "profit_yoy": "净利润同比",
        "no_annual_data": "暂无年度财务数据",
        "pipeline_analysis": "管线布局",
        "total_pipeline": "管线总数",
        "marketed": "已上市",
        "phase3": "III期临床",
        "phase2": "II期临床",
        "phase1_earlier": "I期及更早",
        "pipeline_detail": "管线详情",
        "filter_by_stage": "按研发阶段筛选",
        "product_name": "产品名称",
        "type": "类型",
        "stage": "研发阶段",
        "target": "靶点",
        "indication": "适应症",
        "approval_date": "获批时间",
        "no_pipeline_data": "暂无管线数据",
        "company_not_found": "未找到公司信息",

        # 公司对比
        "company_compare": "公司对比",
        "compare_subtitle": "选择多家企业进行多维度数据对比",
        "select_to_compare": "选择要对比的企业（建议2-4家）",
        "select_at_least_2": "请至少选择2家公司进行对比",
        "basic_info_compare": "基本信息对比",
        "a_share_code": "A股代码",
        "hk_share_code": "港股代码",
        "financial_compare": "财务指标对比（2025年报）",
        "rd_ratio_text": "研发占比",
        "sales_ratio": "销售费用率",
        "net_margin": "净利率",
        "revenue_compare_chart": "营业收入对比（亿元）",
        "rd_compare_chart": "研发投入对比（亿元）",
        "revenue_trend_compare": "营收趋势对比",
        "np_trend_compare": "归母净利润趋势（亿元）",
        "pipeline_compare": "管线对比",
        "pipeline_struct_compare": "管线结构对比",
        "target_platform_compare": "核心靶点/技术平台对比",
        "main_targets": "主要靶点：",
        "tech_types": "技术类型：",

        # 管线追踪
        "pipeline_tracking": "管线追踪",
        "pipeline_subtitle": "全行业管线数据筛选与分析",
        "filter_conditions": "筛选条件",
        "company": "企业",
        "rd_stage": "研发阶段",
        "search_target": "搜索靶点",
        "search_target_placeholder": "如：PD-1, HER2, GLP-1",
        "filter_results": "筛选结果：共",
        "pipeline_items": "条管线",
        "companies_involved": "涉及企业",
        "stage_distribution": "研发阶段分布",
        "type_distribution": "类型分布",
        "pipeline_detail_list": "管线明细",
        "hot_targets": "热门靶点 Top 20",

        # 新闻动态
        "news_dynamics": "行业新闻动态",
        "news_subtitle": "医药行业政策、企业动态、研发进展追踪",
        "filter": "筛选",
        "news_category": "新闻分类",
        "related_company": "相关企业",
        "time_range": "时间范围",
        "news_count": "条新闻",
        "news_list": "新闻列表",
        "important": "重要",
        "policy": "政策",
        "source": "来源",
        "view_company_detail": "查看公司详情 →",
        "news_category_stats": "新闻分类统计",
        "daily_news_count": "每日新闻数量",
        "news_tip": "💡 提示：当前为示例新闻数据。部署后可配置自动抓取CDE、NMPA、公司公告、行业媒体等数据源，实现每日自动更新。",

        # 赛道名称
        "sector_innovative_drug": "创新药",
        "sector_cxo": "CXO",
        "sector_tcm": "中药",
        "sector_biological": "生物制品",
        "sector_medical_device": "医疗器械",

        # 新闻分类
        "cat_rd_progress": "研发进展",
        "cat_business": "经营动态",
        "cat_policy": "政策法规",
        "cat_ma": "并购整合",
        "cat_industry_policy": "行业政策",

        # 阶段
        "stage_all": "全部",
        "stage_marketed": "已上市",
        "stage_phase3": "III期临床",
        "stage_phase2": "II期临床",
        "stage_phase1": "I期临床",
        "stage_ind": "IND阶段",
        "stage_preclinical": "临床前",

        # 时间范围
        "time_all": "全部",
        "time_7d": "最近7天",
        "time_30d": "最近30天",
        "time_90d": "最近90天",

        # 通用
        "metric": "指标",
        "count": "数量",
        "daily_count": "每日数量",

        # 联系我们
        "contact_title": "📧 联系我们",
        "contact_intro": "对这家公司感兴趣？想了解中东市场合作机会？欢迎联系我们的商务团队，获取定制化出海方案与当地资源对接。",
        "contact_button": "Contact Our Team",
        "contact_email": "lisa.wen@qgroup.co",
        "contact_subject_prefix": "合作咨询 - ",
    },
    "en": {
        # Common
        "platform_name": "Pharma Intel Platform",
        "platform_subtitle": "China Pharma Intelligence Platform",
        "data_coverage": "Data Coverage",
        "companies": "companies",
        "financial_data": "financial data",
        "pipeline_data": "pipeline data",
        "sidebar_nav": "👈 Navigate from sidebar",
        "data_update": "Data updated",
        "data_source": "Source",
        "disclaimer": "For research only",

        # Home
        "home_title": "China Pharma Industry Overview",
        "home_subtitle": "5 Sectors · 20 Leading Listed Companies",
        "market_overview": "Market Overview",
        "total_mkt_cap": "Total Mkt Cap (20 cos)",
        "avg_pe": "Avg P/E Ratio",
        "up_down": "Up / Down",
        "sectors_covered": "Sectors",
        "sector_distribution": "Sector Distribution",
        "company_list": "Company Market Overview",
        "filter_sector": "Filter by Sector",
        "all": "All",
        "company_name": "Company",
        "sector": "Sector",
        "latest_price": "Price",
        "change_pct": "Change %",
        "mkt_cap": "Mkt Cap",
        "pe_ratio": "P/E",
        "latest_revenue": "Latest Revenue",
        "latest_net_profit": "Latest Net Profit",
        "rd_investment": "R&D Investment",
        "rd_ranking": "R&D Investment Ranking (FY2025)",
        "rd_billion": "R&D (B RMB)",
        "revenue_billion": "Revenue (B RMB)",
        "rd_ratio": "R&D Ratio",

        # Company Detail
        "company_detail": "Company Detail",
        "select_company": "Select Company",
        "hq": "HQ",
        "official_website": "Website",
        "market_data": "Market Data",
        "pb_ratio": "P/B Ratio",
        "no_market_data": "No market data",
        "financial_analysis": "Financial Analysis",
        "trend_tab": "Key Metrics Trend",
        "annual_tab": "Annual Comparison",
        "quarterly_tab": "Quarterly Data",
        "revenue_trend": "Revenue Trend (B RMB)",
        "net_profit_trend": "Net Profit Trend (B RMB)",
        "rd_trend": "R&D Trend (B RMB)",
        "sales_expense_trend": "Sales Expense Trend (B RMB)",
        "no_financial_data": "No financial data",
        "report_period": "Period",
        "operating_revenue": "Revenue",
        "net_profit_attr": "Net Profit (attr.)",
        "rd_expense": "R&D Expense",
        "sales_expense": "Sales Expense",
        "revenue_yoy": "Revenue YoY",
        "profit_yoy": "Net Profit YoY",
        "no_annual_data": "No annual data",
        "pipeline_analysis": "Pipeline Analysis",
        "total_pipeline": "Total Pipeline",
        "marketed": "Marketed",
        "phase3": "Phase III",
        "phase2": "Phase II",
        "phase1_earlier": "Phase I & Earlier",
        "pipeline_detail": "Pipeline Detail",
        "filter_by_stage": "Filter by Stage",
        "product_name": "Product",
        "type": "Type",
        "stage": "Stage",
        "target": "Target",
        "indication": "Indication",
        "approval_date": "Approval Date",
        "no_pipeline_data": "No pipeline data",
        "company_not_found": "Company not found",

        # Company Compare
        "company_compare": "Company Compare",
        "compare_subtitle": "Multi-dimensional comparison across companies",
        "select_to_compare": "Select companies to compare (2-4 recommended)",
        "select_at_least_2": "Please select at least 2 companies",
        "basic_info_compare": "Basic Info Comparison",
        "a_share_code": "A-Share Code",
        "hk_share_code": "HK-Share Code",
        "financial_compare": "Financial Comparison (FY2025)",
        "rd_ratio_text": "R&D Ratio",
        "sales_ratio": "Sales Ratio",
        "net_margin": "Net Margin",
        "revenue_compare_chart": "Revenue Comparison (B RMB)",
        "rd_compare_chart": "R&D Comparison (B RMB)",
        "revenue_trend_compare": "Revenue Trend Comparison",
        "np_trend_compare": "Net Profit Trend (B RMB)",
        "pipeline_compare": "Pipeline Comparison",
        "pipeline_struct_compare": "Pipeline Structure Comparison",
        "target_platform_compare": "Key Targets / Tech Platforms",
        "main_targets": "Main Targets:",
        "tech_types": "Tech Types:",

        # Pipeline Tracking
        "pipeline_tracking": "Pipeline Tracking",
        "pipeline_subtitle": "Industry-wide pipeline screening & analysis",
        "filter_conditions": "Filters",
        "company": "Company",
        "rd_stage": "Stage",
        "search_target": "Search Target",
        "search_target_placeholder": "e.g. PD-1, HER2, GLP-1",
        "filter_results": "Results:",
        "pipeline_items": "pipeline items",
        "companies_involved": "Companies",
        "stage_distribution": "Stage Distribution",
        "type_distribution": "Type Distribution",
        "pipeline_detail_list": "Pipeline Detail",
        "hot_targets": "Top 20 Hot Targets",

        # News
        "news_dynamics": "Industry News",
        "news_subtitle": "Policy, corporate updates, R&D progress tracking",
        "filter": "Filter",
        "news_category": "Category",
        "related_company": "Company",
        "time_range": "Time Range",
        "news_count": "news items",
        "news_list": "News List",
        "important": "Important",
        "policy": "Policy",
        "source": "Source",
        "view_company_detail": "View Company Detail →",
        "news_category_stats": "News by Category",
        "daily_news_count": "Daily News Count",
        "news_tip": "💡 Tip: Sample news data. Configure auto-crawling from CDE, NMPA, company announcements, industry media for daily updates.",

        # Sectors
        "sector_innovative_drug": "Innovative Drug",
        "sector_cxo": "CXO",
        "sector_tcm": "TCM",
        "sector_biological": "Biologics",
        "sector_medical_device": "Medical Device",

        # News categories
        "cat_rd_progress": "R&D Progress",
        "cat_business": "Business Update",
        "cat_policy": "Policy & Regulation",
        "cat_ma": "M&A",
        "cat_industry_policy": "Industry Policy",

        # Stages
        "stage_all": "All",
        "stage_marketed": "Marketed",
        "stage_phase3": "Phase III",
        "stage_phase2": "Phase II",
        "stage_phase1": "Phase I",
        "stage_ind": "IND",
        "stage_preclinical": "Preclinical",

        # Time range
        "time_all": "All",
        "time_7d": "Last 7 days",
        "time_30d": "Last 30 days",
        "time_90d": "Last 90 days",

        # Common
        "metric": "Metric",
        "count": "Count",
        "daily_count": "Daily Count",

        # Contact
        "contact_title": "📧 Contact Our Team",
        "contact_intro": "Interested in this company? Looking for partnership opportunities in the Middle East market? Contact our business team for customized market entry solutions and local resource connections.",
        "contact_button": "Contact Our Team",
        "contact_email": "lisa.wen@qgroup.co",
        "contact_subject_prefix": "Partnership Inquiry - ",
    }
}

def t(key, lang=None):
    """获取翻译后的文本"""
    if lang is None:
        import streamlit as st
        lang = st.session_state.get("lang", "zh")
    return TRANSLATIONS.get(lang, TRANSLATIONS["zh"]).get(key, key)


def get_fin_field_name(field, lang="zh"):
    """获取财务字段的翻译名称"""
    field_map = {
        "营业收入": ("operating_revenue", "Revenue"),
        "归母净利润": ("net_profit_attr", "Net Profit"),
        "研发费用": ("rd_expense", "R&D Expense"),
        "销售费用": ("sales_expense", "Sales Expense"),
    }
    if lang == "en":
        return field_map.get(field, (field, field))[1]
    return field


def get_currency_unit(lang="zh"):
    """获取货币单位"""
    return "RMB" if lang == "en" else "元"


def format_year_date(date_val, lang="zh"):
    """格式化年度日期"""
    if lang == "en":
        return date_val.strftime("%Y")
    return date_val.strftime("%Y年")


def format_quarter_date(date_val, lang="zh"):
    """格式化季度日期"""
    if lang == "en":
        return date_val.strftime("%Y-%m")
    return date_val.strftime("%Y年%m月")

def init_lang():
    """初始化语言设置（在每个页面顶部调用）"""
    import streamlit as st
    if "lang" not in st.session_state:
        st.session_state.lang = "zh"

def render_lang_switcher():
    """在侧边栏渲染语言切换器"""
    import streamlit as st
    lang = st.selectbox(
        "🌐 Language / 语言",
        ["中文", "English"],
        index=0 if st.session_state.get("lang", "zh") == "zh" else 1,
        key="lang_selector"
    )
    st.session_state.lang = "zh" if lang == "中文" else "en"
    st.markdown("---")
