# B站视频下载器

一款小巧精致的 Windows 桌面应用，用于下载 Bilibili 视频。

---

## 快速获取 .exe（无需安装 Python）

### 方法一：GitHub Actions 自动打包（推荐）

1. **Fork 或创建 GitHub 仓库**，将本项目代码上传
2. 进入仓库 → **Actions** → **Build Windows EXE**
3. 点击 **Run workflow** 手动触发构建
4. 约 3 分钟后，进入 **Actions → 最新运行记录 → Artifacts**
5. 下载 `B站视频下载器-Windows.zip`，解压后即可得到 `.exe`

> 也可以直接 push 代码到 `main` 分支，会自动触发构建。

---

## 方法二：有 Python 环境时直接运行

```bash
pip install -r requirements.txt
python backend/main.py
```

---

## 方法三：有 Python 环境时打包为 exe

双击运行 `scripts/build-windows.bat`，或在 PowerShell 执行 `scripts/build.ps1`。

---

## 界面特性

- **界面小巧精致** — 深色主题，B站品牌粉色点缀
- **一键解析** — 粘贴链接获取视频信息、封面、分P、清晰度
- **多清晰度选择** — 360P ~ 1080P（取决于视频源）
- **下载路径选择** — 自由指定保存位置
- **下载进度实时显示** — 进度条 + 下载速度
- **下载记录查询** — 本地 SQLite 存储，支持打开文件/所在文件夹

---

## 使用说明

1. 打开应用，在**下载视频**标签页粘贴 B站视频链接
2. 点击**解析**按钮，获取视频标题、封面、UP主、分P列表和清晰度
3. 选择需要的清晰度和分P（如果有多P）
4. 点击**浏览**选择保存文件夹
5. 点击**开始下载**
6. 切换到**下载记录**标签页查看历史，可打开视频或所在文件夹

---

## 注意事项

1. **清晰度限制** — 未登录状态下 B站 API 返回的通常是 480P/360P。如需 1080P，需自行在 `backend/bilibili_api.py` 中添加有效的 SESSDATA Cookie。
2. **版权内容** — 番剧、电影等版权视频无法下载，仅支持普通 UP主 投稿视频。
3. **Windows 预装** — Windows 10/11 已自带 Edge Chromium 内核，无需额外安装 WebView2。

---

## 项目结构

```
.
├── backend/              # Python 后端
│   ├── main.py           # PyWebview 入口
│   ├── api.py            # 暴露给前端的 API
│   ├── bilibili_api.py   # B站视频解析与下载
│   ├── download_manager.py # 下载任务管理
│   └── database.py       # SQLite 下载记录
├── src/                  # React + TypeScript 前端源码
│   ├── App.tsx           # 主界面
│   ├── api.ts            # 前端 API 封装
│   └── types.ts          # 类型定义
├── dist/                 # 前端构建产物
├── scripts/
│   ├── build-windows.bat # Windows 打包脚本 (CMD)
│   └── build.ps1         # Windows 打包脚本 (PowerShell)
├── .github/workflows/
│   └── build.yml         # GitHub Actions 自动打包配置
├── requirements.txt      # Python 依赖
└── README.md
```

---

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端框架 | React 19 + TypeScript + Vite |
| UI 组件 | shadcn/ui + Tailwind CSS |
| 桌面容器 | PyWebview (Edge/Chromium 内核) |
| 后端语言 | Python 3.12 |
| 下载引擎 | Requests + Bilibili API |
| 数据存储 | SQLite |
| 打包工具 | PyInstaller |

---

## 免责声明

本工具仅供个人学习研究使用，下载的视频版权归原 UP主 及 Bilibili 所有。请遵守相关法律法规和平台用户协议，勿用于商业用途或大规模传播。
