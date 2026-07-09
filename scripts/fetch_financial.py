"""
财务数据采集脚本
使用 akshare 免费获取上市公司财务数据
"""
import json
import os
import pandas as pd
import akshare as ak
from datetime import datetime

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
RAW_DIR = os.path.join(DATA_DIR, "raw")
PROCESSED_DIR = os.path.join(DATA_DIR, "processed")

def load_companies():
    """加载公司列表"""
    with open(os.path.join(DATA_DIR, "companies.json"), "r", encoding="utf-8") as f:
        return json.load(f)

def fetch_financial_indicator(stock_code, market="sh"):
    """获取主要财务指标"""
    try:
        # A股主要财务指标
        symbol = f"{stock_code}"
        df = ak.stock_financial_analysis_indicator(symbol=symbol)
        return df
    except Exception as e:
        print(f"  获取财务指标失败 {stock_code}: {e}")
        return None

def fetch_income_statement(stock_code, market="sh"):
    """获取利润表"""
    try:
        df = ak.stock_profit_sheet_by_report_em(symbol=stock_code)
        return df
    except Exception as e:
        print(f"  获取利润表失败 {stock_code}: {e}")
        return None

def fetch_balance_sheet(stock_code, market="sh"):
    """获取资产负债表"""
    try:
        df = ak.stock_balance_sheet_by_report_em(symbol=stock_code)
        return df
    except Exception as e:
        print(f"  获取资产负债表失败 {stock_code}: {e}")
        return None

def extract_key_metrics(income_df, balance_df):
    """从报表中提取关键指标"""
    metrics = {}
    
    if income_df is not None and len(income_df) > 0:
        # 取最近几期数据
        recent = income_df.head(8)  # 最近8个报告期
        for _, row in recent.iterrows():
            date = str(row.get("REPORT_DATE", ""))[:10]
            if not date:
                continue
            metrics[date] = {
                "营业收入": row.get("TOTAL_OPERATE_INCOME", 0),
                "营业成本": row.get("OPERATE_COST", 0),
                "研发费用": row.get("RD_EXPENSE", 0),
                "销售费用": row.get("SALE_EXPENSE", 0),
                "管理费用": row.get("MANAGE_EXPENSE", 0),
                "营业利润": row.get("OPERATE_PROFIT", 0),
                "净利润": row.get("PARENT_NETPROFIT", 0),
                "归母净利润": row.get("PARENT_NETPROFIT", 0),
            }
    
    return metrics

def collect_ashare_financials():
    """采集A股公司财务数据"""
    companies = load_companies()
    all_metrics = {}
    
    for comp in companies:
        stock_code = comp["stock_code_sh"]
        if not stock_code:
            print(f"跳过 {comp['name']} (无A股代码)")
            continue
        
        print(f"正在采集 {comp['name']} ({stock_code})...")
        
        # 获取利润表
        income_df = fetch_income_statement(stock_code)
        
        # 获取资产负债表
        balance_df = fetch_balance_sheet(stock_code)
        
        # 提取关键指标
        metrics = extract_key_metrics(income_df, balance_df)
        if metrics:
            all_metrics[comp["name"]] = metrics
            print(f"  成功获取 {len(metrics)} 个报告期数据")
        
        # 保存原始数据
        if income_df is not None:
            income_df.to_csv(
                os.path.join(RAW_DIR, f"{comp['name']}_利润表.csv"),
                index=False, encoding="utf-8-sig"
            )
        if balance_df is not None:
            balance_df.to_csv(
                os.path.join(RAW_DIR, f"{comp['name']}_资产负债表.csv"),
                index=False, encoding="utf-8-sig"
            )
    
    # 保存处理后的关键指标
    with open(os.path.join(PROCESSED_DIR, "financial_metrics.json"), "w", encoding="utf-8") as f:
        json.dump(all_metrics, f, ensure_ascii=False, indent=2)
    
    print(f"\n完成！共采集 {len(all_metrics)} 家公司财务数据")
    return all_metrics

def collect_stock_info():
    """采集股票基本信息和行情"""
    companies = load_companies()
    stock_data = {}
    
    for comp in companies:
        stock_code = comp["stock_code_sh"]
        if not stock_code:
            continue
        
        print(f"正在获取 {comp['name']} 行情数据...")
        try:
            # 获取实时行情
            df = ak.stock_zh_a_spot_em()
            row = df[df["代码"] == stock_code]
            if len(row) > 0:
                stock_data[comp["name"]] = {
                    "最新价": float(row["最新价"].values[0]),
                    "涨跌幅": float(row["涨跌幅"].values[0]),
                    "总市值": float(row["总市值"].values[0]),
                    "流通市值": float(row["流通市值"].values[0]),
                    "市盈率-动态": float(row["市盈率-动态"].values[0]) if row["市盈率-动态"].values[0] != "-" else None,
                    "市净率": float(row["市净率"].values[0]) if row["市净率"].values[0] != "-" else None,
                }
                print(f"  现价: {stock_data[comp['name']]['最新价']}, 市值: {stock_data[comp['name']]['总市值']/1e8:.0f}亿")
        except Exception as e:
            print(f"  获取行情失败: {e}")
    
    with open(os.path.join(PROCESSED_DIR, "stock_info.json"), "w", encoding="utf-8") as f:
        json.dump(stock_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n完成！共获取 {len(stock_data)} 家公司行情数据")
    return stock_data

if __name__ == "__main__":
    os.makedirs(RAW_DIR, exist_ok=True)
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    
    print("=" * 50)
    print("开始采集财务数据...")
    print("=" * 50)
    collect_ashare_financials()
    
    print("\n" + "=" * 50)
    print("开始采集股票行情...")
    print("=" * 50)
    collect_stock_info()
