import os
import pandas as pd

# CSV 文件路径
csv_path = 'decoded_constructor_args.csv'
# 输出目录
output_dir = './constructor'
os.makedirs(output_dir, exist_ok=True)

# 读取 CSV
df = pd.read_csv(csv_path, dtype=str)

for _, row in df.iterrows():
    address = row['address']
    args = row.get('encoded_constructor_args', None)

    # 构造输出文件名
    filename = os.path.join(output_dir, f"{address}.txt")

    # 无论 args 是否存在，都先创建文件；如果 args 非空，则写入内容
    with open(filename, 'w', encoding='utf-8') as f:
        if pd.notna(args) and args != '':
            f.write(args)

print(f"已处理 {len(df)} 条记录，文件保存在：{output_dir}")
