#!/usr/bin/env python3
"""只读检查 Git 两个快照间新增的 Python 防御性模式；候选项不等于违规。"""

import argparse
import ast
from collections import Counter
import io
import json
import os
from pathlib import Path
import subprocess
import tokenize


RULES = {
    "D001": ("error", "裸捕获或宽泛异常捕获后仅 pass，静默丢弃失败"),
    "D101": ("review", "校验或提前抛错：确认消费方自然报错是否已足够"),
    "D102": ("review", "默认值兜底：确认这是已定义的可选项，而非掩盖内部契约缺失"),
    "D103": ("review", "宽泛异常处理：确认实际失败边界、清理或隔离职责"),
    "D104": ("review", "数值替换或裁剪：确认有算法定义依据"),
    "D105": ("review", "运行时类型或字段探测：确认有真实的多态或外部输入契约"),
}


def broad_exception(node):
    if node is None:
        return True
    if isinstance(node, ast.Tuple):
        return any(broad_exception(item) for item in node.elts)
    return (
        isinstance(node, ast.Name) and node.id in {"Exception", "BaseException"}
    ) or (
        isinstance(node, ast.Attribute)
        and isinstance(node.value, ast.Name)
        and node.value.id == "builtins"
        and node.attr in {"Exception", "BaseException"}
    )


class Patterns(ast.NodeVisitor):
    """按词法 owner 和语法结构比较；行号变化不构成新模式。"""

    def __init__(self, source):
        self.lines = source.splitlines()
        self.scope = []
        self.items = []

    def add(self, rule, node, signature=None):
        severity, message = RULES[rule]
        key = (tuple(self.scope), rule, ast.dump(node if signature is None else signature))
        self.items.append((key, {
            "rule": rule, "severity": severity, "line": node.lineno,
            "scope": ".".join(self.scope) or "<module>",
            "source": self.lines[node.lineno - 1].strip(), "message": message,
        }))

    def visit_owner(self, node):
        self.scope.append(node.name)
        self.generic_visit(node)
        self.scope.pop()

    visit_FunctionDef = visit_owner
    visit_AsyncFunctionDef = visit_owner
    visit_ClassDef = visit_owner

    def visit_ExceptHandler(self, node):
        if broad_exception(node.type):
            only_pass = all(isinstance(stmt, ast.Pass) for stmt in node.body)
            self.add("D001" if only_pass else "D103", node)
        self.generic_visit(node)

    def visit_If(self, node):
        if any(isinstance(stmt, ast.Raise) for stmt in node.body):
            self.add("D101", node, node.test)
        elif any(
            isinstance(item, ast.Call) and isinstance(item.func, ast.Name)
            and item.func.id in {"isinstance", "hasattr", "getattr"}
            for item in ast.walk(node.test)
        ):
            self.add("D105", node, node.test)
        self.generic_visit(node)

    def visit_Assert(self, node):
        self.add("D101", node, node.test)
        self.generic_visit(node)

    def visit_Call(self, node):
        func = node.func
        if (
            isinstance(func, ast.Attribute) and func.attr == "get" and len(node.args) >= 2
        ) or (
            isinstance(func, ast.Name) and func.id == "getattr" and len(node.args) >= 3
        ):
            self.add("D102", node)
        if (
            isinstance(func, ast.Attribute)
            and func.attr in {"nan_to_num", "nan_to_num_", "clamp", "clamp_", "clip", "clip_"}
        ) or (isinstance(func, ast.Name) and func.id in {"nan_to_num", "clamp", "clip"}):
            self.add("D104", node)
        self.generic_visit(node)

    def visit_value(self, node):
        if isinstance(node.value, ast.BoolOp) and isinstance(node.value.op, ast.Or):
            self.add("D102", node, node.value)
        self.generic_visit(node)

    visit_Assign = visit_value
    visit_AnnAssign = visit_value
    visit_Return = visit_value


def patterns(data, filename):
    encoding, _ = tokenize.detect_encoding(io.BytesIO(data).readline)
    source = data.decode(encoding)
    visitor = Patterns(source)
    visitor.visit(ast.parse(source, filename=filename))
    return visitor.items


def git(repo, *args):
    return subprocess.run(
        ["git", "-C", str(repo), *args], check=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        env={**os.environ, "GIT_OPTIONAL_LOCKS": "0"},
    ).stdout


def selected(path, paths):
    return not paths or any(path == item or path.startswith(item.rstrip("/") + "/") for item in paths)


def changed_files(repo, base, head, staged):
    """raw -z 保留空格、换行、非 ASCII 文件名及重命名的两个路径。"""
    args = ["diff", "--raw", "-z", "--no-ext-diff", "--no-textconv", "--find-renames"]
    if staged:
        args.append("--cached")
    args.append(base)
    if head:
        args.append(head)
    fields = iter(git(repo, *args, "--").split(b"\0")[:-1])
    changes = []
    for header in fields:
        old_mode, new_mode, _, _, status = header.decode("ascii").split()
        old_path = os.fsdecode(next(fields))
        new_path = os.fsdecode(next(fields)) if status.startswith(("R", "C")) else old_path
        if status == "U":
            raise ValueError(f"存在未合并文件，无法确定比较快照：{new_path}")
        if status != "D":
            changes.append((old_path, new_path, old_mode[1:], new_mode))
    if not head and not staged:
        for path in git(repo, "ls-files", "--others", "--exclude-standard", "-z").split(b"\0")[:-1]:
            name = os.fsdecode(path)
            mode = "120000" if (repo / name).is_symlink() else "100644"
            changes.append((name, name, "000000", mode))
    return changes


def inspect(args):
    repo = Path(os.fsdecode(git(args.repo, "rev-parse", "--show-toplevel")).rstrip("\n"))
    base = git(repo, "rev-parse", "--verify", "--end-of-options", args.base + "^{commit}").decode().strip()
    head = None
    if args.head:
        head = git(repo, "rev-parse", "--verify", "--end-of-options", args.head + "^{commit}").decode().strip()
    findings, scanned, unscanned = [], [], []
    for old_path, path, old_mode, new_mode in changed_files(repo, base, head, args.staged):
        if not selected(path, args.path):
            continue
        if new_mode not in {"100644", "100755"} or not path.endswith(".py"):
            unscanned.append(path)
            continue
        before = git(repo, "show", f"{base}:{old_path}") if old_mode in {"100644", "100755"} else b""
        if head:
            after = git(repo, "show", f"{head}:{path}")
        elif args.staged:
            after = git(repo, "show", f":{path}")
        else:
            after = (repo / path).read_bytes()
        previous = Counter(key for key, _ in patterns(before, f"{base}:{old_path}"))
        for key, finding in patterns(after, path):
            if previous[key]:
                previous[key] -= 1
            else:
                findings.append({"path": path, **finding})
        scanned.append(path)
    blocked = any(item["severity"] == "error" for item in findings)
    return {
        "status": "blocked" if blocked else "needs_review" if findings else "no_candidates",
        "base": base, "target": head or ("index" if args.staged else "working_tree"),
        "scanned_python": scanned, "unscanned": unscanned, "findings": findings,
        "semantic_review_required": True,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=".", help="Git 仓库或其子目录")
    parser.add_argument("--base", default="HEAD", help="基线提交，默认 HEAD")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--head", help="目标提交；省略时检查工作区，含暂存和未跟踪文件")
    group.add_argument("--staged", action="store_true", help="仅比较暂存区与 base")
    parser.add_argument("--path", action="append", default=[], help="限定仓库根相对路径，文件或目录，可重复")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    parser.add_argument("--fail-on-review", action="store_true", help="严格门禁：候选项也返回 1")
    args = parser.parse_args()
    try:
        report = inspect(args)
    except (OSError, SyntaxError, UnicodeError, ValueError, subprocess.CalledProcessError) as exc:
        # CLI 必须区分工具/解析失败与检查无命中，避免 CI 误报通过。
        detail = exc.stderr.decode(errors="replace") if isinstance(exc, subprocess.CalledProcessError) else str(exc)
        report = {"status": "incomplete", "error": detail, "semantic_review_required": True}
        code = 2
    else:
        code = int(report["status"] == "blocked" or (args.fail_on_review and bool(report["findings"])))
    if args.format == "json":
        print(json.dumps(report, ensure_ascii=True, indent=2))
    elif report["status"] == "incomplete":
        print("incomplete: " + report["error"])
    else:
        print(f"{report['status']}: {len(report['scanned_python'])} Python 文件，{len(report['findings'])} 项")
        for item in report["findings"]:
            print(f"{item['path']!r}:{item['line']} {item['severity']} {item['rule']} {item['message']}")
        if report["unscanned"]:
            print("未覆盖文件（需按类型另行检查）：" + repr(report["unscanned"]))
        print("本工具仅定位有限的语法模式；退出 0 不代表已完成语义审查。")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
