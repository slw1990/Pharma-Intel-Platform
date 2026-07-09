"""
轻量级财务数据采集 - 直接调用东方财富公开API
无需akshare，纯requests实现
"""
import json
import os
import requests
import pandas as pd

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
RAW_DIR = os.path.join(DATA_DIR, "raw")
PROCESSED_DIR = os.path.join(DATA_DIR, "processed")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

def load_companies():
    with open(os.path.join(DATA_DIR, "companies.json"), "r", encoding="utf-8") as f:
        return json.load(f)

def get_financial_report(stock_code, report_type="profit"):
    """
    获取财务报表
    report_type: profit=利润表, balance=资产负债表, cashflow=现金流量表
    """
    # 东方财富财务报表API
    type_map = {
        "profit": "lrb",
        "balance": "zcfzb",
        "cashflow": "xjllb"
    }
    
    url = f"https://emweb.securities.eastmoney.com/PC_HSF10/NewFinanceAnalysis/{type_map[report_type]}AjaxNew"
    params = {
        "companyType": "4",
        "reportDateType": "0",
        "dataType": "1",
        "code": _format_code(stock_code)
    }
    
    try:
        resp = requests.get(url, params=params, headers=HEADERS, timeout=10)
        data = resp.json()
        if data.get("data"):
            return data["data"]
        return None
    except Exception as e:
        print(f"  获取{report_type}失败 {stock_code}: {e}")
        return None

def _format_code(stock_code):
    """格式化股票代码"""
    if stock_code.startswith("6"):
        return f"SH{stock_code}"
    elif stock_code.startswith(("0", "3")):
        return f"SZ{stock_code}"
    return stock_code

def get_stock_quote(stock_code):
    """获取股票实时行情"""
    secid = _format_code(stock_code)
    url = "https://push2.eastmoney.com/api/qt/stock/get"
    params = {
        "secid": secid,
        "fields": "f43,f44,f45,f46,f57,f58,f60,f116,f117,f162,f167,f168,f169,f170,f171"
    }
    
    try:
        resp = requests.get(url, params=params, headers=HEADERS, timeout=10)
        data = resp.json()
        if data.get("data"):
            d = data["data"]
            return {
                "名称": d.get("f58", ""),
                "最新价": d.get("f43", 0) / 100 if d.get("f43") else 0,
                "涨跌幅": d.get("f170", 0) / 100 if d.get("f170") else 0,
                "总市值": d.get("f116", 0),
                "流通市值": d.get("f117", 0),
                "市盈率": d.get("f162", 0) / 100 if d.get("f162") else None,
                "市净率": d.get("f167", 0) / 100 if d.get("f167") else None,
            }
    except Exception as e:
        print(f"  获取行情失败 {stock_code}: {e}")
    return None

def extract_key_metrics(report_data, company_name):
    """从利润表提取关键指标"""
    if not report_data:
        return {}
    
    metrics = {}
    for item in report_data[:8]:  # 最近8个报告期
        date = item.get("REPORT_DATE", "")[:10]
        if not date:
            continue
        
        # 字段名可能不同，做个兼容
        revenue = item.get("TOTAL_OPERATE_INCOME") or item.get("TOTAL_OPERATE_INCOME_") or 0
        net_profit = item.get("PARENT_NETPROFIT") or item.get("NETPROFIT") or 0
        rd_expense = item.get("RD_EXPENSE") or item.get("RESEARCH_EXPENSE") or 0
        sale_expense = item.get("SALE_EXPENSE") or 0
        operate_profit = item.get("OPERATE_PROFIT") or 0
        gross_profit = item.get("TOTAL_OPERATE_INCOME", 0) - item.get("OPERATE_COST", 0) if item.get("OPERATE_COST") else 0
        
        metrics[date] = {
            "营业收入": float(revenue) if revenue else 0,
            "营业成本": float(item.get("OPERATE_COST", 0)) if item.get("OPERATE_COST") else 0,
            "毛利润": float(gross_profit) if gross_profit else 0,
            "研发费用": float(rd_expense) if rd_expense else 0,
            "销售费用": float(sale_expense) if sale_expense else 0,
            "管理费用": float(item.get("MANAGE_EXPENSE", 0)) if item.get("MANAGE_EXPENSE") else 0,
            "营业利润": float(operate_profit) if operate_profit else 0,
            "归母净利润": float(net_profit) if net_profit else 0,
        }
    
    return metrics

def collect_all_financials():
    """采集所有公司财务数据"""
    companies = load_companies()
    all_metrics = {}
    all_quotes = {}
    
    for comp in companies:
        stock_code = comp["stock_code_sh"]
        if not stock_code:
            print(f"跳过 {comp['name']} (暂无A股数据)")
            continue
        
        print(f"采集 {comp['name']} ({stock_code})...")
        
        # 利润表
        profit_data = get_financial_report(stock_code, "profit")
        metrics = extract_key_metrics(profit_data, comp["name"])
        
        if metrics:
            all_metrics[comp["name"]] = metrics
            latest = list(metrics.keys())[0]
            rev = metrics[latest]["营业收入"] / 1e8
            np = metrics[latest]["归母净利润"] / 1e8
            print(f"  {latest}: 营收{rev:.1f}亿, 净利润{np:.1f}亿")
        
        # 行情数据
        quote = get_stock_quote(stock_code)
        if quote:
            all_quotes[comp["name"]] = quote
            print(f"  现价: {quote['最新价']:.2f}, 市值: {quote['总市值']/1e8:.0f}亿")
        
        # 保存原始数据
        if profit_data:
            with open(os.path.join(RAW_DIR, f"{comp['name']}_利润表_raw.json"), "w", encoding="utf-8") as f:
                json.dump(profit_data, f, ensure_ascii=False, indent=2)
    
    # 保存处理后的数据
    with open(os.path.join(PROCESSED_DIR, "financial_metrics.json"), "w", encoding="utf-8") as f:
        json.dump(all_metrics, f, ensure_ascii=False, indent=2)
    
    with open(os.path.join(PROCESSED_DIR, "stock_quotes.json"), "w", encoding="utf-8") as f:
        json.dump(all_quotes, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 财务数据采集完成: {len(all_metrics)}家公司")
    print(f"✅ 行情数据采集完成: {len(all_quotes)}家公司")
    return all_metrics, all_quotes

if __name__ == "__main__":
    os.makedirs(RAW_DIR, exist_ok=True)
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    collect_all_financials()
