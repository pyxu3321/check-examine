import pandas as pd 
import numpy as np 

def analyze_inventory_adjustment(file_path, output_path, qty_threshold=100, ratio_threshold=0.1): 
    """ 
    qty_threshold: 绝对数量差异阈值（如变化超过100个） 
    ratio_threshold: 比率差异阈值（如比率变化超过10%） 
    """
    try: 
        df = pd.read_excel(file_path, header=0) 
    except Exception as e: 
        return f"读取失败: {e}" 

    result_df = df.copy() 
    
    # 存储每个月的影响得分列名 
    score_cols = [] 

    for i in range(6): 
        m = i + 1 
        # 定义原始列索引 
        idx_pre_inv = 1 + i 
        idx_pre_tgt = 7 + i 
        idx_post_inv = 13 + i 
        idx_post_tgt = 19 + i 

        # 1. 计算基础比率 
        pre_ratio = df.iloc[:, idx_pre_inv] / df.iloc[:, idx_pre_tgt].replace(0, np.nan) 
        post_ratio = df.iloc[:, idx_post_inv] / df.iloc[:, idx_post_tgt].replace(0, np.nan) 
        
        # 2. 计算比率差异 (Ratio Diff) 
        ratio_diff = (post_ratio - pre_ratio).abs().fillna(0) 
        
        # 3. 计算数量绝对差异 (Qty Diff) - 这里取库存和目标差异的最大值，捕捉全方位变动 
        inv_qty_diff = (df.iloc[:, idx_post_inv] - df.iloc[:, idx_pre_inv]).abs() 
        tgt_qty_diff = (df.iloc[:, idx_post_tgt] - df.iloc[:, idx_pre_tgt]).abs() 
        max_qty_diff = np.maximum(inv_qty_diff, tgt_qty_diff) 
        
        # 4. 计算影响得分 (Impact Score) = 数量差异 * 比率差异 
        # 这个得分能平衡"小体量大波动"和"大体量小波动" 
        impact_score = max_qty_diff * ratio_diff 
        
        # 将中间结果存入结果表 
        result_df[f'M{m}_数量差异'] = max_qty_diff 
        result_df[f'M{m}_比率差异'] = ratio_diff 
        result_df[f'M{m}_影响得分'] = impact_score 
        score_cols.append(f'M{m}_影响得分') 

    # 5. 综合判定 
    # 计算6个月的最大影响得分 
    result_df['最大影响得分'] = result_df[score_cols].max(axis=1) 
    
    # 筛选规则： 
    # 必须满足：最大数量差异 > 阈值 AND 最大比率差异 > 阈值 
    # 或者：影响得分极高 
    qty_diff_cols = [f'M{i+1}_数量差异' for i in range(6)] 
    ratio_diff_cols = [f'M{i+1}_比率差异' for i in range(6)] 
    
    mask = ( 
        (result_df[qty_diff_cols].max(axis=1) >= qty_threshold) & 
        (result_df[ratio_diff_cols].max(axis=1) >= ratio_threshold) 
    ) 
    
    anomaly_df = result_df[mask].sort_values(by='最大影响得分', ascending=False) 

    # 6. 保存结果 
    try: 
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer: 
            # 主sheet：简化输出，只显示SKU和最大影响得分
            simple_anomaly_df = anomaly_df[['SKU', '最大影响得分']]
            simple_anomaly_df.to_excel(writer, sheet_name='需复核异常SKU', index=False) 
            # 全量计算结果sheet：包含所有计算过程
            result_df.to_excel(writer, sheet_name='全量计算结果', index=False) 
            # 源数据sheet：直接复制原始数据
            df.to_excel(writer, sheet_name='源数据', index=False) 
        
        return (f"✅ 分析完成！\n" 
                f"找出需复核SKU: {len(anomaly_df)} 个\n" 
                f"筛选标准: 数量差异 > {qty_threshold} 且 比率变动 > {int(ratio_threshold*100)}%\n" 
                f"结果已保存至: {output_path}") 
    except Exception as e: 
        return f"保存失败: {e}" 

if __name__ == "__main__": 
    input_file = 'inventory_data.xlsx' 
    output_file = '异常复核报告.xlsx' 
    
    # 建议参数设置： 
    # qty_threshold: 根据你的业务，比如 500 以上才算大变动 
    # ratio_threshold: 0.1 表示比率变动超过 10% 
    res = analyze_inventory_adjustment(input_file, output_file, qty_threshold=50, ratio_threshold=0.1) 
    print(res) 
