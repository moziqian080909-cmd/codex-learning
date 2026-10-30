# codex-learning

一个使用 Python 标准库实现的命令行待办事项工具。需要 Python 3.8 或更新版本，无需安装依赖。

```bash
python3 todo.py add "学习 Python"
python3 todo.py add "完成练习"
python3 todo.py list
python3 todo.py done 1
python3 todo.py list
```

任务自动保存至 `~/.local/share/codex-learning/tasks.json`，重新运行程序后仍然保留。
已完成任务显示为 `[x]`，未完成任务显示为 `[ ]`。

可以在子命令前指定其他数据文件：

```bash
python3 todo.py --file /tmp/my-tasks.json add "测试任务"
python3 todo.py --file /tmp/my-tasks.json list
python3 todo.py --help
```

空任务、不存在的编号、损坏的数据文件及文件读写失败会输出错误并以非零状态退出。

运行自动化测试：

```bash
python3 -m unittest discover -s tests -v
```
