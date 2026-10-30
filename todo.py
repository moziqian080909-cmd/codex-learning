"""A small persistent command-line todo list, using only Python's standard library."""

import argparse
import json
import os
from pathlib import Path
import tempfile


def load_tasks(path):
    if not path.exists():
        return []
    tasks = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(tasks, list):
        raise ValueError("任务文件必须包含列表")
    ids = set()
    for task in tasks:
        if (
            not isinstance(task, dict)
            or type(task.get("id")) is not int
            or task["id"] <= 0
            or task["id"] in ids
            or not isinstance(task.get("title"), str)
            or not task["title"].strip()
            or type(task.get("done")) is not bool
        ):
            raise ValueError("任务文件格式错误")
        ids.add(task["id"])
    return tasks


def save_tasks(path, tasks):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=path.parent, delete=False
        ) as stream:
            temporary = Path(stream.name)
            json.dump(tasks, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
        os.replace(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def main(argv=None):
    parser = argparse.ArgumentParser(description="命令行待办事项工具")
    parser.add_argument(
        "--file", type=Path,
        default=Path.home() / ".local" / "share" / "codex-learning" / "tasks.json",
        help="任务文件路径（默认保存在用户目录）",
    )
    commands = parser.add_subparsers(dest="command", required=True)
    add = commands.add_parser("add", help="添加任务")
    add.add_argument("title", help="任务内容，含空格时请使用引号")
    commands.add_parser("list", help="查看所有任务")
    done = commands.add_parser("done", help="完成任务")
    done.add_argument("id", type=int, help="任务编号")
    args = parser.parse_args(argv)
    try:
        tasks = load_tasks(args.file)
        if args.command == "add":
            title = args.title.strip()
            if not title:
                raise ValueError("任务内容不能为空")
            task_id = max((task["id"] for task in tasks), default=0) + 1
            tasks.append({"id": task_id, "title": title, "done": False})
            save_tasks(args.file, tasks)
            print(f"已添加任务 {task_id}：{title}")
        elif args.command == "list":
            if not tasks:
                print("暂无任务")
            for task in tasks:
                status = "x" if task["done"] else " "
                print(f"{task['id']}. [{status}] {task['title']}")
        else:
            task = next((task for task in tasks if task["id"] == args.id), None)
            if task is None:
                raise ValueError(f"找不到任务 {args.id}")
            task["done"] = True
            save_tasks(args.file, tasks)
            print(f"已完成任务 {args.id}：{task['title']}")
    except (OSError, ValueError) as error:
        parser.exit(1, f"错误：{error}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
