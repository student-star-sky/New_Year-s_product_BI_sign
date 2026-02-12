import pandas as pd
import re
import logging
from models import db, Product

# 配置日志
logger = logging.getLogger(__name__)

def clean_chengjiaov(value):
    """将成交金额字符串转为万元数值"""
    if pd.isna(value):
        return 0.0
    
    s = str(value).strip()
    
    # 处理特殊情况
    if s == '0' or '同行已购买' in s or '销' in s:
        return 0.0
    
    # 提取数字
    match = re.search(r'([\d.]+)', s)
    if match:
        try:
            num = float(match.group(1))
            if '万' in s:
                return num
            else:
                # 小于1000的可能是元，转换为万元
                if num < 1000:
                    return round(num / 10000, 4)
                return round(num / 10000, 2)
        except ValueError:
            return 0.0
    return 0.0

def clean_saleVolume(value):
    """清洗销量，如'9000', '销40+件' -> 40, '1万' -> 10000"""
    if pd.isna(value):
        return 0
    
    s = str(value).strip()
    
    if s == '' or s == '0':
        return 0
    
    # 提取数字
    match = re.search(r'([\d.]+)', s)
    if match:
        try:
            num = float(match.group(1))
            if '万' in s:
                return int(num * 10000)
            else:
                return int(num)
        except ValueError:
            return 0
    return 0

def load_csv_to_db(filepath, category):
    """加载CSV文件到数据库"""
    try:
        df = pd.read_csv(filepath, delimiter=';', encoding='utf-8')
        # 去除列名BOM
        df.columns = df.columns.str.replace('\ufeff', '')
        
        # 检查必要列
        required_columns = ['company', 'bangdan_name', 'ranking', 'subject', 'price', 'unit', 'chengjiaov', 'saleVolume', 'odUrl']
        for col in required_columns:
            if col not in df.columns:
                logger.warning(f"Column '{col}' not found in {filepath}")
                return
        
        logger.info(f"Processing {len(df)} rows from {filepath}")
        
        records = []
        error_count = 0
        
        for i, row in df.iterrows():
            try:
                # 构建商品对象
                product = Product(
                    company=str(row['company']) if pd.notna(row['company']) else '',
                    bangdan_name=str(row['bangdan_name']) if pd.notna(row['bangdan_name']) else '',
                    ranking=int(row['ranking']) if pd.notna(row['ranking']) else 0,
                    subject=str(row['subject']) if pd.notna(row['subject']) else '',
                    price=float(row['price']) if pd.notna(row['price']) else 0.0,
                    unit=str(row['unit']) if pd.notna(row['unit']) else '',
                    chengjiaov=clean_chengjiaov(row['chengjiaov']),
                    saleVolume=clean_saleVolume(row['saleVolume']),
                    odUrl=str(row['odUrl']) if pd.notna(row['odUrl']) else '',
                    category=category
                )
                records.append(product)
            except Exception as e:
                logger.error(f"Error processing row {i}: {e}")
                error_count += 1
                continue
        
        # 按 odUrl 去重
        seen = set()
        unique = []
        for rec in records:
            if rec.odUrl and rec.odUrl not in seen:
                seen.add(rec.odUrl)
                unique.append(rec)
        
        logger.info(f"Filtered to {len(unique)} unique records (removed {len(records) - len(unique)} duplicates)")
        
        # 批量保存
        if unique:
            try:
                db.session.bulk_save_objects(unique)
                db.session.commit()
                logger.info(f"Successfully loaded {len(unique)} records for {category}")
            except Exception as e:
                logger.error(f"Error saving to database: {e}")
                db.session.rollback()
        else:
            logger.info(f"No valid records found for {category}")
            
    except Exception as e:
        logger.error(f"Error loading {filepath}: {e}")
        db.session.rollback()