import pdfplumber
import re
import json
from pathlib import Path
from tqdm import tqdm  # 进度条库
import pandas as pd

def parse_report(pdf_path):
    data = {
        "contract": None,
        "epochs": None,
        "test_cases": None,
        "risks": []
    }
    with pdfplumber.open(pdf_path) as pdf:
        text = "\n".join(page.extract_text() or "" for page in pdf.pages)

    # 合约地址
    m = re.search(r"Contract Detected:\s*(0x[a-fA-F0-9]{40})", text)
    if m: data["contract"] = m.group(1)

    # 运行 epochs
    m = re.search(r"Running for\s*(\d+)\s*epochs", text)
    if m: data["epochs"] = int(m.group(1))

    # 生成测试用例数
    m = re.search(r"Generate\s*(\d+)\s*valid test cases", text)
    if m: data["test_cases"] = int(m.group(1))

    # 风险项
    pattern = (
        r"Risk:\s*(.+?)\s*"                # 风险类别
        r"Function:\s*(\w+)\s*"            # 函数名
        r"Input\(s\):\s*"
        r"(\[[\s\S]*?\]|'.*?')"            # inputs：支持跨行，也懒惰匹配到首个 ] 或 '
        r"(?=\nRisk:|$)"                   # 向前预查，下一个是换行+Risk: 或 文档末尾
    )
    for risk_match in re.finditer(pattern, text):
        data["risks"].append({
            "category": risk_match.group(1),
            "function": risk_match.group(2),
            "inputs": eval(risk_match.group(3))
        })

        # 如果是出问题的那个 PDF，就打印所有匹配片段，看看到底匹配到哪儿了
    # if pdf_path.name.endswith("0x56af6596f28d9e6f289521d31affdb95c412265e_report.pdf"):
    #     print(f"\n=== 调试 {pdf_path.name} 的风险匹配 ===")
    #     all_matches = list(re.finditer(pattern, text))
    #     print(f"共找到 {len(all_matches)} 个匹配：")
    #     for i, m in enumerate(all_matches, 1):
    #         print(f"  匹配 #{i}:")
    #         print("    来源：", repr(m.group(0)))
    #         print("    inputs：", m.group(3))
    #     print("=== 调试结束 ===\n")

    return data

# 批量处理并显示进度条
reports = []
pdf_files = list(Path("./result").glob("*.pdf"))
for pdf_file in tqdm(pdf_files, desc="Processing PDF reports"):
    tqdm.write(f'Processing {pdf_file.name}')
    reports.append(parse_report(pdf_file))

# 保存为 JSON
with open("all_reports.json", "w", encoding="utf-8") as f:
    json.dump(reports, f, ensure_ascii=False, indent=2)

# 把 list of dict 转成 DataFrame
# 为了能在单元格里保存复杂的 risks 结构，这里先把它序列化为 JSON 字符串
for r in reports:
    r["risks"] = json.dumps(r["risks"], ensure_ascii=False)

df = pd.DataFrame(reports)

# 导出为 CSV，不带行索引
df.to_csv("all_reports.csv", index=False, encoding="utf-8-sig")