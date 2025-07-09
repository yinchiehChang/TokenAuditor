#!/usr/bin/env python3
import csv
import subprocess
import sys
import platform
from tqdm import tqdm

# 固定的 CSV 文件名
CSV_FILE = "contracts/decoded_constructor_args.csv"
# 结果输出文件
RESULT_FILE = "contracts/result.csv"
# 每个子进程最大运行时间（秒），超过则跳过
TIMEOUT = 300 + 10  # 300 秒运行时间，加10秒缓冲

# Ganache 终止命令
if platform.system() == "Windows":
    GANACHE_KILL_CMD = ["taskkill", "/F", "/IM", "node.exe"]
else:
    GANACHE_KILL_CMD = ["pkill", "-f", "ganache"]


def kill_ganache():
    """终止当前 Ganache 实例"""
    try:
        subprocess.run(GANACHE_KILL_CMD, capture_output=True)
        tqdm.write("Ganache 实例已被终止")
    except Exception as e:
        tqdm.write(f"终止 Ganache 实例出错：{e}")


def run_commands(csv_path):
    success_count = 0
    failure_count = 0
    timeout_count = 0
    error_count = 0

    # 读取地址列表
    try:
        with open(csv_path, newline='', encoding='utf-8') as f:
            reader = list(csv.DictReader(f))
    except FileNotFoundError:
        print(f"错误：找不到文件 {csv_path}", file=sys.stderr)
        sys.exit(1)

    if not reader or 'address' not in reader[0]:
        print(f"错误：CSV 格式不正确，需包含 'address' 列", file=sys.stderr)
        sys.exit(1)

    addresses = [row['address'].strip() for row in reader if row.get('address', '').strip()]
    total = len(addresses)
    if total == 0:
        print("错误：未找到任何有效的地址", file=sys.stderr)
        sys.exit(1)

    tqdm.write(f"发现 {total} 个地址，开始处理...\n")

    # 打开结果文件并写入表头
    with open(RESULT_FILE, 'w', newline='', encoding='utf-8') as rf:
        writer = csv.writer(rf)
        # 新增 reason 列说明失败原因
        writer.writerow(['address', 'status', 'exit_code', 'reason'])
        print('address,status,exit_code,reason')

        # 创建 tqdm 进度条
        pbar = tqdm(addresses, desc="处理地址进度", unit="addr", file=sys.stderr)
        for idx, address in enumerate(pbar, start=1):
            # 在进度条上显示当前 address
            pbar.set_postfix(address=address)
            tqdm.write(f"[{idx}/{total}] 开始处理地址 {address}")

            try:
                result = subprocess.run(
                    [
                        sys.executable, 'main.py',
                        '-c', address,
                        '-l', '300',
                        '-b', '10',
                        '-e', '50'
                    ],
                    capture_output=True,
                    text=True,
                    timeout=TIMEOUT
                )
                exit_code = result.returncode
                if exit_code == 0:
                    status = 'success'
                    reason = ''
                    success_count += 1
                    tqdm.write(f"[{idx}/{total}] [成功] 地址 {address}")
                else:
                    status = 'failure'
                    # 收集 stderr 的第一行作为原因
                    reason = result.stderr.strip().splitlines()[0] if result.stderr else f"非零退出码 {exit_code}"
                    failure_count += 1
                    tqdm.write(f"[{idx}/{total}] [失败] 地址 {address}：{reason}")

            except subprocess.TimeoutExpired:
                exit_code = ''
                status = 'timeout'
                reason = f"超过 {TIMEOUT} 秒超时"
                timeout_count += 1
                tqdm.write(f"[{idx}/{total}] [超时跳过] 地址 {address}：{reason}")

            except Exception as e:
                exit_code = ''
                status = 'error'
                reason = str(e)
                error_count += 1
                tqdm.write(f"[{idx}/{total}] [异常跳过] 地址 {address}：{reason}")

            # 写入结果并实时输出
            writer.writerow([address, status, exit_code, reason])
            rf.flush()
            print(f"{address},{status},{exit_code},{reason}")

            # 若执行成功或失败，打印原脚本输出
            if status in ('success', 'failure') and result.stdout:
                tqdm.write(f"--- {address} STDOUT 开始 ---")
                tqdm.write(result.stdout.strip())
                tqdm.write(f"--- {address} STDOUT 结束 ---")
            # 失败或 error 情形打印 stderr
            if status in ('failure', 'error') and result.stderr:
                tqdm.write(f"--- {address} STDERR 开始 ---")
                tqdm.write(result.stderr.strip())
                tqdm.write(f"--- {address} STDERR 结束 ---")

            # 每运行完一个地址检测后，终止 Ganache 实例
            kill_ganache()

    # 汇总信息
    tqdm.write("\n执行完毕")
    tqdm.write(f"成功: {success_count}/{total}")
    tqdm.write(f"失败: {failure_count}/{total}")
    tqdm.write(f"超时跳过: {timeout_count}/{total}")
    tqdm.write(f"异常跳过: {error_count}/{total}")
    tqdm.write(f"结果已保存到 {RESULT_FILE}")


if __name__ == "__main__":
    run_commands(CSV_FILE)
