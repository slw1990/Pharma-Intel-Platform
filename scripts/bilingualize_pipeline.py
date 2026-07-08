"""
将管线数据从纯中文转换为中英双语结构
每条记录增加 _en 后缀的英文字段
"""
import json
import os
import re

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")

# ========== 阶段翻译映射 ==========
STAGE_MAP = {
    "已上市": "Marketed",
    "III期临床": "Phase III",
    "II期临床": "Phase II",
    "I期临床": "Phase I",
    "IND阶段": "IND",
    "临床前": "Preclinical",
    "临床阶段": "Clinical Stage",
    "增长期": "Growth Stage",
    "布局期": "Planning Stage",
    "快速增长": "Rapid Growth",
    "特色服务": "Featured Services",
    "运营中": "Operational",
    "领先": "Leading",
}

# ========== 类型翻译映射 ==========
TYPE_MAP = {
    "PD-1单抗": "PD-1 mAb",
    "PD-L1/TGF-β双抗": "PD-L1/TGF-β Bispecific",
    "PD-1/CTLA-4双抗": "PD-1/CTLA-4 Bispecific",
    "PD-1/VEGF双抗": "PD-1/VEGF Bispecific",
    "小分子靶向药": "Small Molecule Targeted Drug",
    "PARP抑制剂": "PARP Inhibitor",
    "AR抑制剂": "AR Inhibitor",
    "CDK4/6抑制剂": "CDK4/6 Inhibitor",
    "BTK抑制剂": "BTK Inhibitor",
    "BTK降解剂": "BTK Degrader",
    "BCL-2抑制剂": "BCL-2 Inhibitor",
    "CD20单抗": "CD20 mAb",
    "VEGF单抗": "VEGF mAb",
    "HER2单抗": "HER2 mAb",
    "TNF-α单抗": "TNF-α mAb",
    "IL-17A单抗": "IL-17A mAb",
    "IL-23抑制剂": "IL-23 Inhibitor",
    "IL-4Rα单抗": "IL-4Rα mAb",
    "LAG-3单抗": "LAG-3 mAb",
    "TIGIT单抗": "TIGIT mAb",
    "OX40单抗": "OX40 mAb",
    "CD47单抗": "CD47 mAb",
    "CD73单抗": "CD73 mAb",
    "ADC（HER2）": "ADC (HER2)",
    "ADC（MSLN）": "ADC (MSLN)",
    "ADC（c-Met）": "ADC (c-Met)",
    "ADC（CLDN18.2）": "ADC (CLDN18.2)",
    "ADC": "ADC",
    "TROP2 ADC": "TROP2 ADC",
    "CLDN18.2 ADC": "CLDN18.2 ADC",
    "ADC+免疫": "ADC + Immunotherapy",
    "多激酶抑制剂": "Multi-kinase Inhibitor",
    "VEGFR抑制剂": "VEGFR Inhibitor",
    "FGFR抑制剂": "FGFR Inhibitor",
    "RET抑制剂": "RET Inhibitor",
    "MEK抑制剂": "MEK Inhibitor",
    "KRAS G12C抑制剂": "KRAS G12C Inhibitor",
    "SGLT2抑制剂": "SGLT2 Inhibitor",
    "XPO1抑制剂": "XPO1 Inhibitor",
    "HPK1抑制剂": "HPK1 Inhibitor",
    "GLP-1R激动剂": "GLP-1R Agonist",
    "GLP-1R/GCGR双激动剂": "GLP-1R/GCGR Dual Agonist",
    "GLP-1口服制剂": "Oral GLP-1",
    "PROTAC": "PROTAC",
    "TPO-R激动剂": "TPO-R Agonist",
    "BLyS/APRIL双靶点抑制剂": "BLyS/APRIL Dual Inhibitor",
    "VEGF/Tie2双抗": "VEGF/Tie2 Bispecific",
    "mRNA疫苗": "mRNA Vaccine",
    "微管抑制剂": "Microtubule Inhibitor",
    "α-葡萄糖苷酶抑制剂": "α-Glucosidase Inhibitor",
    "注射用重组人促卵泡激素": "Recombinant FSH for Injection",
    "糖尿病复方制剂": "Diabetes Combination Therapy",
    "中成药": "Chinese Patent Medicine",
    "中药注射剂": "TCM Injection",
    "中成药贴剂": "TCM Patch",
    "外用贴剂": "Topical Patch",
    "外用软膏": "Topical Ointment",
    "输液": "Infusion",
    "保肝药": "Hepatoprotective Drug",
    "滋补品": "Tonic",
    "营养补充": "Nutritional Supplement",
    "血制品": "Blood Product",
    "疫苗": "Vaccine",
    "医疗器械": "Medical Device",
    "高值耗材": "High-value Consumable",
    "诊断试剂": "Diagnostic Reagent",
    "医美产品": "Aesthetic Product",
    "美妆护肤": "Beauty & Skincare",
    "日化产品": "Daily Chemical Product",
    "软件": "Software",
    "CRO服务": "CRO Services",
    "CDMO服务": "CDMO Services",
    "CRO+CDMO": "CRO + CDMO",
    "CXO服务": "CXO Services",
}

# ========== 常见适应症翻译映射 ==========
INDICATION_MAP = {
    "霍奇金淋巴瘤": "Hodgkin's lymphoma",
    "肝癌": "liver cancer",
    "肺癌": "lung cancer",
    "食管癌": "esophageal cancer",
    "胃癌": "gastric cancer",
    "乳腺癌": "breast cancer",
    "卵巢癌": "ovarian cancer",
    "前列腺癌": "prostate cancer",
    "非小细胞肺癌": "non-small cell lung cancer",
    "HER2阳性乳腺癌": "HER2-positive breast cancer",
    "三阴性乳腺癌": "triple-negative breast cancer",
    "HER2低表达乳腺癌": "HER2-low breast cancer",
    "结直肠癌": "colorectal cancer",
    "尿路上皮癌": "urothelial carcinoma",
    "胆管癌": "cholangiocarcinoma",
    "多发性骨髓瘤": "multiple myeloma",
    "套细胞淋巴瘤": "mantle cell lymphoma",
    "慢性淋巴细胞白血病": "chronic lymphocytic leukemia",
    "华氏巨球蛋白血症": "Waldenstrom's macroglobulinemia",
    "B细胞淋巴瘤": "B-cell lymphoma",
    "非霍奇金淋巴瘤": "non-Hodgkin's lymphoma",
    "B细胞恶性肿瘤": "B-cell malignancies",
    "实体瘤": "solid tumors",
    "血液肿瘤": "hematological malignancies",
    "肿瘤": "oncology",
    "银屑病": "psoriasis",
    "强直性脊柱炎": "ankylosing spondylitis",
    "类风湿关节炎": "rheumatoid arthritis",
    "系统性红斑狼疮": "systemic lupus erythematosus",
    "炎症性肠病": "inflammatory bowel disease",
    "2型糖尿病": "type 2 diabetes",
    "肥胖": "obesity",
    "糖尿病": "diabetes",
    "慢性肾病": "chronic kidney disease",
    "肾癌": "renal cell carcinoma",
    "甲状腺癌": "thyroid cancer",
    "胰腺癌": "pancreatic cancer",
    "间皮瘤": "mesothelioma",
    "不孕不育": "infertility",
    "肠外营养": "parenteral nutrition",
    "新冠病毒感染": "COVID-19",
    "血小板减少症": "thrombocytopenia",
    "MSI-H/dMMR实体瘤": "MSI-H/dMMR solid tumors",
    "食管鳞癌": "esophageal squamous cell carcinoma",
    "NSCLC": "NSCLC",
    "乙肝": "hepatitis B",
    "丙肝": "hepatitis C",
    "艾滋病": "HIV/AIDS",
    "高血压": "hypertension",
    "高血脂": "hyperlipidemia",
    "心脑血管": "cardiovascular & cerebrovascular",
    "心血管": "cardiovascular",
    "脑血管": "cerebrovascular",
    "消化系统": "digestive system",
    "呼吸系统": "respiratory system",
    "神经系统": "nervous system",
    "抗感染": "anti-infective",
    "抗过敏": "anti-allergy",
    "眼科": "ophthalmology",
    "骨科": "orthopedics",
    "皮肤科": "dermatology",
    "妇科": "gynecology",
    "儿科": "pediatrics",
    "老年病": "geriatrics",
    "营养支持": "nutritional support",
    "麻醉": "anesthesia",
    "造影剂": "contrast media",
    "诊断": "diagnosis",
    "治疗": "treatment",
    "预防": "prevention",
}

# ========== 靶点/技术翻译（大部分本身就是英文，少量中文需翻译） ==========
TARGET_MAP = {
    "未披露": "Undisclosed",
    "营养支持": "Nutritional Support",
    "微管蛋白": "Tubulin",
}

# ========== 公司名称英文映射 ==========
COMPANY_NAME_MAP = {
    "恒瑞医药": "Hengrui Medicine",
    "百济神州": "BeiGene",
    "信达生物": "Innovent Biologics",
    "科伦药业": "Kelun Pharma",
    "荣昌生物": "Remegen",
    "康方生物": "Akeso Bio",
    "复星医药": "Fosun Pharma",
    "华东医药": "Huadong Medicine",
    "药明康德": "WuXi AppTec",
    "泰格医药": "Hangzhou Tigermed",
    "凯莱英": "Asymchem",
    "康龙化成": "Pharmaron",
    "片仔癀": "Pien Tze Huang",
    "云南白药": "Yunnan Baiyao",
    "同仁堂": "Tongrentang",
    "华润三九": "CR Sanjiu",
    "万泰生物": "Wantai Bio",
    "华兰生物": "Hualan Bio",
    "迈瑞医疗": "Mindray Medical",
    "联影医疗": "United Imaging",
}

# ========== 赛道翻译 ==========
SECTOR_MAP = {
    "创新药（化学药）": "Innovative Drug (Small Molecule)",
    "创新药（生物药）": "Innovative Drug (Biologics)",
    "创新药+输液": "Innovative Drug + Infusion",
    "创新药（ADC/自身免疫）": "Innovative Drug (ADC/Autoimmune)",
    "创新药（双抗）": "Innovative Drug (Bispecific)",
    "创新药": "Innovative Drug",
    "CXO": "CXO",
    "中药": "Traditional Chinese Medicine",
    "中药（经典）": "TCM (Classic)",
    "中药（现代）": "TCM (Modern)",
    "生物制品": "Biologics",
    "生物制品（疫苗/诊断）": "Biologics (Vaccine/Diagnostic)",
    "生物制品（血制品/疫苗）": "Biologics (Blood/Vaccine)",
    "医疗器械": "Medical Device",
    "医疗器械（影像）": "Medical Device (Imaging)",
}


def translate_indication(indication_zh):
    """翻译适应症，支持逗号、顿号分隔的多个适应症"""
    if not indication_zh:
        return ""
    
    # 替换常见分隔符为统一格式
    text = indication_zh.replace("、", ", ").replace("，", ", ")
    
    # 逐个替换已知术语（从长到短，避免部分匹配问题）
    sorted_indications = sorted(INDICATION_MAP.keys(), key=len, reverse=True)
    for zh in sorted_indications:
        en = INDICATION_MAP[zh]
        text = text.replace(zh, en)
    
    # 如果替换后还是有很多中文字符，说明有未映射的，保留原文并标注
    chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
    if chinese_chars > 3:
        # 保留原文，同时给出英文
        return indication_zh
    
    # 首字母大写
    if text:
        text = text[0].upper() + text[1:]
    
    return text


def translate_name(name_zh):
    """翻译产品名：通用名(商品名)格式 -> Generic (Brand)"""
    # 处理 代号 格式（如 SHR-1701, BGB-16673等英文代号）
    if re.match(r'^[A-Za-z]{2,4}[-_]?\d+', name_zh):
        return name_zh
    
    # 处理 通用名（商品名） 格式
    match = re.match(r'(.+?)（(.+?)）', name_zh)
    if match:
        generic = match.group(1)
        brand = match.group(2)
        # 商品名通常保留拼音或英文，这里直接保留
        return f"{generic} ({brand})"
    
    return name_zh


def translate_target(target_zh):
    """翻译靶点"""
    if not target_zh:
        return ""
    if target_zh in TARGET_MAP:
        return TARGET_MAP[target_zh]
    # 大部分靶点本身就是英文缩写，直接返回
    return target_zh


def translate_type(type_zh):
    """翻译类型"""
    if type_zh in TYPE_MAP:
        return TYPE_MAP[type_zh]
    return type_zh


def translate_stage(stage_zh):
    """翻译阶段"""
    if stage_zh in STAGE_MAP:
        return STAGE_MAP[stage_zh]
    return stage_zh


def bilingualize_pipeline():
    """将管线数据转换为双语结构"""
    input_path = os.path.join(DATA_DIR, "processed", "pipeline_data.json")
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    result = {}
    for company_zh, drugs in data.items():
        company_en = COMPANY_NAME_MAP.get(company_zh, company_zh)
        result[company_zh] = {
            "name_en": company_en,
            "drugs": []
        }
        for drug in drugs:
            bilingual_drug = {
                "name": drug["name"],
                "name_en": translate_name(drug["name"]),
                "type": drug["type"],
                "type_en": translate_type(drug["type"]),
                "stage": drug["stage"],
                "stage_en": translate_stage(drug["stage"]),
                "indication": drug["indication"],
                "indication_en": translate_indication(drug["indication"]),
                "target": drug["target"],
                "target_en": translate_target(drug["target"]),
                "approval_date": drug.get("approval_date", ""),
            }
            result[company_zh]["drugs"].append(bilingual_drug)
    
    output_path = os.path.join(DATA_DIR, "processed", "pipeline_data_bilingual.json")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    total = sum(len(v["drugs"]) for v in result.values())
    print(f"完成！{len(result)}家公司，{total}条管线已双语化")
    print(f"输出文件: {output_path}")
    return result


def bilingualize_companies():
    """将公司基础信息双语化"""
    input_path = os.path.join(DATA_DIR, "companies.json")
    with open(input_path, 'r', encoding='utf-8') as f:
        companies = json.load(f)
    
    # 公司描述英文翻译
    DESC_MAP = {
        "国内创新药绝对龙头，研发投入行业第一，管线最丰富，涵盖肿瘤、自身免疫、糖尿病、心血管等多个治疗领域":
            "China's absolute leader in innovative drugs, with the highest R&D investment and richest pipeline, covering oncology, autoimmune, diabetes, cardiovascular and other therapeutic areas.",
        "中国创新药出海标杆，首家跑通\"中国研发+全球销售\"模式，专注于肿瘤药物开发":
            "China's benchmark for innovative drug globalization. First company to successfully execute the 'China R&D + Global Sales' model, focused on oncology drug development.",
        "PD-1国产龙头，生物药领军企业，减重药管线重磅，布局肿瘤、自身免疫、代谢等领域":
            "Domestic PD-1 leader and biologics pioneer, with a promising weight-loss drug pipeline. Focused on oncology, autoimmune, and metabolic diseases.",
        "全产业链龙头，子公司科伦博泰ADC赛道核心玩家，输液+创新药双轮驱动":
            "Full industry chain leader. Subsidiary Kelun-Biotech is a key player in ADC field. Dual-driven by infusion and innovative drugs.",
        "国产ADC先行者，维迪西妥单抗商业化放量，自身免疫与肿瘤双赛道布局":
            "Pioneer of domestic ADCs. Disitamab vedotin is experiencing strong commercial growth. Dual focus on autoimmune and oncology.",
    }
    
    result = []
    for c in companies:
        name_en = COMPANY_NAME_MAP.get(c["name"], c["name"])
        sector_en = SECTOR_MAP.get(c["sector"], c["sector"])
        desc_en = DESC_MAP.get(c["description"], c["description"])
        
        bilingual = {
            **c,
            "name_en": name_en,
            "full_name_en": name_en,  # 简化处理
            "sector_en": sector_en,
            "description_en": desc_en,
            "headquarters_en": c.get("headquarters", ""),  # 城市名保留拼音
        }
        result.append(bilingual)
    
    output_path = os.path.join(DATA_DIR, "companies_bilingual.json")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"完成！{len(result)}家公司信息已双语化")
    print(f"输出文件: {output_path}")
    return result


if __name__ == "__main__":
    bilingualize_pipeline()
    bilingualize_companies()
