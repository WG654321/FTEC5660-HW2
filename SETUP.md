# 本地运行与提交

## Windows PowerShell

在本仓库目录中运行。以下命令直接使用虚拟环境中的 Python，不需要更改 PowerShell 的脚本执行策略。

```powershell
python -m venv .venv
New-Item -ItemType Directory -Force .tmp, .cache | Out-Null
$env:TEMP = Join-Path (Get-Location) '.tmp'
$env:TMP = $env:TEMP
$env:PIP_CACHE_DIR = Join-Path (Get-Location) '.cache'
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pip check
```

当前电脑 C 盘空间不足，因此上面的安装命令将临时文件及 pip 缓存放在项目所在的 D 盘。这些环境变量仅对当前 PowerShell 会话及其子进程生效，两个目录也已被 Git 忽略。

复制 `.env.example` 为 `.env` 并在本机填写自己的 DeepSeek key。已有 `.env` 时不要覆盖它。`.env`、`.venv/` 和 `results.csv` 已被 Git 忽略。老师会使用自己的 key，任何提交文件中都不应包含真实 key。

本机 Windows 系统代理指向 `127.0.0.1`，实测它会间歇性中断课程 MCP 和 DeepSeek 的 TLS 连接；直连两个服务可用。因此本机 `.env` 额外配置了 `NO_PROXY=ftec5660.ngrok.app,api.deepseek.com`。这不是模型或服务器地址的更改，也不改系统代理设置。其他机器应先检查自己的网络，不必照搬这项本机配置。

公开测试命令：

```powershell
.\.venv\Scripts\python.exe -X utf8 hw2.py --cv-folder public_test
```

Task 2 本地测试命令：

```powershell
.\.venv\Scripts\python.exe -X utf8 hw2.py --cv-folder task2
```

`hw2.py` 已实现核验逻辑。CSV 中 0.95 表示核验一致，0.05 表示发现明确差异，0.5 表示核验未完成或存在不确定性。按老师的评分规则，0.5 也会被判为负例，不能将这种结果解释成已发现造假。程序还会向 stderr 输出每份简历的核验摘要。

离线行为测试与实验复现：

```powershell
.\.venv\Scripts\python.exe -X utf8 -m unittest discover -s tests -v
.\.venv\Scripts\python.exe -X utf8 tools/evaluate.py --runs 3
.\.venv\Scripts\python.exe -X utf8 tools/build_adversarial_cv.py
.\.venv\Scripts\python.exe -X utf8 tools/evaluate.py --folder task2 --runs 3 --output experiments/task2
```

评测脚本串行运行各轮，将每次成功及失败的日志、CSV 和耗时保存到对应实验目录。网络启动失败最多重试三次；重试不会隐藏失败记录。不要同时运行多组在线评测，以免超过课程服务器的并发建议。

## GitHub fork

本地代码来源：<https://github.com/nguyenngocbaocmt02/FTEC5660-HW2>。

用户 fork：<https://github.com/WG654321/FTEC5660-HW2>。本地 `origin` 已关联该仓库，`upstream` 指向课程仓库。

检查远端：

```powershell
git remote -v
```

提交前检查 `git status` 和 diff，确认没有密钥。完成作业后在 Blackboard 填写 GitHub 用户名，评分期间保持仓库公开。

## 实现与环境

### 2026-10-13 环境验证记录

- 本地 Python：3.14.2；隔离环境位于 `.venv/`。
- 依赖安装完成，`pip check` 报告 `No broken requirements found`。
- 老师的 PDF loader 成功读取七份公开简历及目标简历，共八份。
- 老师的 `load_mcp_tools()` 成功返回全部六个工具。
- 通过 LangChain 使用 `deepseek-v4-flash` 发出最小请求，收到非空回复 `OK`。官方模型列表显示 `deepseek-flash`，但题面名称的请求可以成功，因此保留题面名称。
- 最初的空 starter 仅用于环境检查，得到 0/7；最终实现的实验结果以 README 和 `experiments/` 中的实际记录为准。
- MCP 连接曾出现间歇性的代理/TLS `ConnectError`，重试原命令成功。连通性已验证，但不代表网络长期稳定；连接发生在两个待实现函数之前，不应为此修改老师保护的 runner。
- 老师提供的 PDF 加载、MCP 初始化和评分代码均保持不变；只填写两个指定函数并在其上方新增辅助代码。依赖新增 PyMuPDF，用于复现攻击 PDF。

核验流程为提取声明、确认身份、获取资料、逐项比较和验证结构化结论。每份简历的两次尝试共用 210 秒期限，每次尝试最多 20 个模型轮次和 40 次工具调用，最多三份并发。错误或超时回退到 0.5。该时间预算控制核验阶段；原始 runner 的初始化与 PDF 加载不在每份简历的超时范围内。

Task 2 的一页 PDF 将可见学位夸大为 PhD，但隐藏文字层是 BSc，具体方法及限制见 README。`reflection.md` 基于本作业的实践进行反思，并非对未提供课件的复述。若老师另有提交位置或主题要求，以课程通知为准。

## 交付检查

- Task 1 实现与依赖完整，运行后生成 `results.csv`。
- Task 2 文件为 `task2/adversarial_cv.pdf`，最多两页。
- README 的 `Homework 2 solution` 包含 Task 1 和 Task 2 报告。
- 完成并检查 Task 3 反思，确认提交位置。
- 私有测试单次运行要求不超过 30 分钟。
- 截止时间以课程通知为准；题面写的是 10 月 20 日 23:59 HKT。
