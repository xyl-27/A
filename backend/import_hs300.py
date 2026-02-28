import csv
import pymysql
from datetime import datetime

def import_hs300():
    connection = pymysql.connect(
        host='localhost',
        port=3306,
        user='root',
        password='qwe123',
        database='stock_analysis',
        charset='utf8mb4'
    )
    
    try:
        with connection.cursor() as cursor:
            with open('/opt/A/hs300.csv', 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                for row in reader:
                    code = row['股票代码'].zfill(6)
                    name = row['股票名称']
                    industry = row['行业']
                    
                    # 解析上市时间
                    listing_date_str = row['上市时间']
                    try:
                        listing_date = datetime.strptime(listing_date_str, '%Y%m%d').date()
                    except:
                        listing_date = None
                    
                    # 处理市值
                    market_cap = float(row['总市值']) if row['总市值'] else None
                    float_market_cap = float(row['流通市值']) if row['流通市值'] else None
                    
                    # 市盈率
                    try:
                        pe_ratio = float(row['市盈率-动态']) if row['市盈率-动态'] else None
                    except:
                        pe_ratio = None
                    
                    # 确定市场类型
                    if code.startswith('688'):
                        market_type = 'STAR'  # 科创板
                    elif code.startswith('000') or code.startswith('001'):
                        market_type = 'MAIN'  # 主板
                    elif code.startswith('300'):
                        market_type = 'CHINEXT'  # 创业板
                    else:
                        market_type = 'MAIN'
                    
                    sql = """
                    INSERT INTO stocks (code, name, industry_l1, market_type, listing_date, market_cap, float_market_cap, pe_ratio)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE 
                        name=VALUES(name), 
                        industry_l1=VALUES(industry_l1),
                        market_type=VALUES(market_type),
                        listing_date=VALUES(listing_date),
                        market_cap=VALUES(market_cap),
                        float_market_cap=VALUES(float_market_cap),
                        pe_ratio=VALUES(pe_ratio)
                    """
                    cursor.execute(sql, (code, name, industry, market_type, listing_date, market_cap, float_market_cap, pe_ratio))
                
        connection.commit()
        print(f"Successfully imported HS300 stocks!")
        
    finally:
        connection.close()

if __name__ == '__main__':
    import_hs300()
