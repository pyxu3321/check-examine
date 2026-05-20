import pandas as pd
import numpy as np

# 生成测试数据
# 列结构：SKU, 调整前库存(M1-M6), 调整前目标(M1-M6), 调整后库存(M1-M6), 调整后目标(M1-M6)
# 总共1 + 6 + 6 + 6 + 6 = 25列

# 定义列名
columns = ['SKU']
# 调整前库存 (M1-M6)
for i in range(1, 7):
    columns.append(f'调整前库存_M{i}')
# 调整前目标 (M1-M6)
for i in range(1, 7):
    columns.append(f'调整前目标_M{i}')
# 调整后库存 (M1-M6)
for i in range(1, 7):
    columns.append(f'调整后库存_M{i}')
# 调整后目标 (M1-M6)
for i in range(1, 7):
    columns.append(f'调整后目标_M{i}')

# 生成测试数据
# 场景1: 差异较大的SKU（差异 > 0.5）
data = []
# SKU1: M1差异大（调整前比率=1.0，调整后=1.6，差异0.6）
data.append([
    'SKU001', 
    100, 80, 90, 70, 85, 95,  # 调整前库存
    100, 80, 90, 70, 85, 95,  # 调整前目标
    160, 80, 90, 70, 85, 95,  # 调整后库存
    100, 80, 90, 70, 85, 95   # 调整后目标
])
# SKU2: M2差异大（调整前比率=2.0，调整后=1.3，差异0.7）
data.append([
    'SKU002', 
    80, 160, 70, 60, 75, 85,  # 调整前库存
    40, 80, 70, 60, 75, 85,   # 调整前目标
    80, 104, 70, 60, 75, 85,  # 调整后库存
    40, 80, 70, 60, 75, 85    # 调整后目标
])

# 场景2: 差异较小的SKU（差异 < 0.5）
# SKU3: 所有月份差异小
for i in range(3, 6):
    sku = f'SKU00{i}'
    row = [sku]
    # 生成调整前库存和目标（比率约1.0）
    pre_inv = [np.random.randint(80, 120) for _ in range(6)]
    pre_tgt = pre_inv.copy()
    # 生成调整后库存（比调整前略高或略低，比率差异 < 0.5）
    post_inv = [int(x * (1 + np.random.uniform(-0.3, 0.3))) for x in pre_inv]
    post_tgt = pre_tgt.copy()
    row.extend(pre_inv)
    row.extend(pre_tgt)
    row.extend(post_inv)
    row.extend(post_tgt)
    data.append(row)

# 场景3: 边界情况（分母为0）
# SKU6: M3调整前目标为0
row = ['SKU006']
pre_inv = [90, 85, 100, 75, 80, 95]  # M3库存=100
pre_tgt = [90, 85, 0, 75, 80, 95]    # M3目标=0
post_inv = [90, 85, 100, 75, 80, 95]
post_tgt = [90, 85, 100, 75, 80, 95]  # 调整后目标非0
row.extend(pre_inv)
row.extend(pre_tgt)
row.extend(post_inv)
row.extend(post_tgt)
data.append(row)

# 场景4: 更多测试数据（随机生成）
for i in range(6, 21):
    sku = f'SKU0{i:02d}'
    row = [sku]
    # 生成随机调整前库存和目标
    pre_inv = [np.random.randint(50, 150) for _ in range(6)]
    pre_tgt = [np.random.randint(50, 150) for _ in range(6)]
    # 生成调整后库存和目标（部分月份差异大，部分小）
    post_inv = []
    post_tgt = []
    for j in range(6):
        # 30%概率差异大
        if np.random.random() < 0.3:
            # 调整后库存或目标变化大
            if np.random.random() < 0.5:
                # 库存变化大
                post_inv.append(int(pre_inv[j] * (1 + np.random.uniform(-0.6, 0.6))))
                post_tgt.append(pre_tgt[j])
            else:
                # 目标变化大
                post_inv.append(pre_inv[j])
                post_tgt.append(int(pre_tgt[j] * (1 + np.random.uniform(-0.6, 0.6))))
        else:
            # 差异小
            post_inv.append(int(pre_inv[j] * (1 + np.random.uniform(-0.2, 0.2))))
            post_tgt.append(pre_tgt[j])
    row.extend(pre_inv)
    row.extend(pre_tgt)
    row.extend(post_inv)
    row.extend(post_tgt)
    data.append(row)

# 创建DataFrame
df = pd.DataFrame(data, columns=columns)

# 保存为Excel文件
output_path = 'inventory_data.xlsx'
df.to_excel(output_path, index=False)

print(f"测试数据生成完成，保存至: {output_path}")
print(f"生成了 {len(df)} 条测试数据")
print("数据包含以下情况:")
print("- 差异较大的SKU（差异 > 0.5）")
print("- 差异较小的SKU（差异 < 0.5）")
print("- 边界情况（分母为0）")
print("- 随机生成的混合情况")
