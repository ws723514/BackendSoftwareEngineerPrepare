#!/usr/bin/env python
"""在 generated/ 目录下的所有 .py 代码生成文件顶部插入时间戳与 git 提交短 SHA。

用法：
    python scripts/add_header.py

执行前请确保已运行 `buf generate`，并位于仓库根目录。
"""

import datetime
import pathlib
import subprocess
import sys
from typing import List

def get_git_sha() -> str:
    """获取当前 HEAD 的短 SHA，如失败则返回 'unknown'."""
    try:
        return (
            subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], stderr=subprocess.DEVNULL)
            .decode()
            .strip()
        )
    except Exception:
        return "unknown"


def add_header_to_file(py_file: pathlib.Path, header: str) -> None:
    """在文件开头插入 header，如果尚未插入过。"""
    text = py_file.read_text(encoding="utf-8")
    if text.startswith(header.split("\n")[0]):
        return  # 已插入过
    py_file.write_text(header + text, encoding="utf-8")


def main(argv: List[str] | None = None) -> None:
    # 使用本地时间而不是 UTC 时间
    ts = datetime.datetime.now().isoformat(timespec="seconds")
    sha = get_git_sha()
    header = f"# Code-gen time: {ts} (local)  commit: {sha}\n"

    generated_dir = pathlib.Path("generated")
    if not generated_dir.exists():
        print("[add_header] generated/ 目录不存在，请先运行 buf generate", file=sys.stderr)
        sys.exit(1)

    py_files = list(generated_dir.rglob("*.py"))
    if not py_files:
        print("[add_header] 未找到任何 .py 文件，是否已经生成？", file=sys.stderr)
        sys.exit(1)

    for py in py_files:
        add_header_to_file(py, header)
    print(f"[add_header] 已处理 {len(py_files)} 个文件，header: {header.strip()}")


if __name__ == "__main__":
    main()
