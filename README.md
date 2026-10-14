# 安全面试刷题 (Sec-Interview Quiz)

一个轻量的安全工程师面试刷题应用，**PC 和手机浏览器都能用**（响应式布局，支持添加到手机主屏幕）。

题库来源：[duckpigdog/Sec-Interview](https://github.com/duckpigdog/Sec-Interview)（351 道安全面试真题，覆盖信息收集、SQL 注入、XSS、内网渗透、蓝队防守、代码审计、二进制逆向等 32 个方向）。

## 功能

- 📚 **刷题**：按分类顺序刷 / 随机刷 / 背题模式；练习模式先思考再点开答案，标记「掌握 / 没掌握」自动跳题
- 🔁 **复习**：错题本、收藏夹集中重练，一键"全部标为已掌握"
- 💼 **面经**：按企业分类的面经库，支持粘贴链接（公众号/牛客/知乎/CSDN 等）或文本导入，网页自动提取正文
- 📰 **公众号文章转题库**：粘贴微信公众号文章链接，自动抓取正文（图片本地化防防盗链）、按小标题切分成多道题
- 🔍 **搜索**：全文搜索题目和面经
- 📊 **进度**：已掌握 / 没掌握 / 收藏统计，进度保存在服务端

## 目录结构

```
├── backend/               # FastAPI + SQLite 后端
│   ├── app/
│   │   ├── main.py        # 应用入口（同时托管前端静态文件）
│   │   ├── models.py      # 题目 / 面经 / 刷题进度
│   │   ├── routers/       # API 路由
│   │   └── ingest/        # 数据导入模块
│   ├── cli.py             # 数据导入命令行工具
│   └── requirements.txt
├── frontend/              # Vue3 + Vite 前端（含离线数据层，APK 复用同一套代码）
├── desktop/               # PC 桌面版打包（PyInstaller + pywebview）
├── apk/                   # Android APK 打包源（WebView 壳）
├── data/                  # 运行数据（SQLite 数据库、题库仓库、图片缓存）
├── dist/SecQuiz/          # PC 版打包产物
├── SecQuiz.apk            # Android 安装包
├── build-desktop.bat      # 一键打包 PC 版
├── build-apk.bat          # 一键打包 APK
└── start.bat              # 网页版一键启动
```

## 三种使用形态

| 形态 | 启动方式 | 说明 |
|------|---------|------|
| 网页版 | `start.bat` | 完整功能（面经/导入），PC 浏览器和手机浏览器均可访问 |
| PC 桌面版 | `dist\SecQuiz\SecQuiz.exe` | 双击弹出独立窗口，内置服务，无需命令行 |
| Android APK | 安装 `SecQuiz.apk` | **离线刷题**，351 题全部内置，进度存手机本地 |

## 快速开始

### 1. 安装依赖（首次）

```bash
# 后端（Python 3.10+）
cd backend
pip install -r requirements.txt

# 前端（Node 18+，仅构建时需要）
cd ../frontend
npm install
npm run build
```

### 2. 导入题库（首次）

```bash
cd backend
python cli.py import-repo
```

会自动克隆 Sec-Interview 仓库到 `data/sec-interview-repo/` 并解析导入。之后随时重新运行该命令即可拉取并导入最新题目（已导入的会更新，进度不丢失）。

### 3. 启动

**Windows**：双击 `start.bat`

**其他 / 手动**：

```bash
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

- 电脑访问：<http://127.0.0.1:8000>
- 手机访问：确保手机和电脑在同一局域网，用 `http://<电脑IP>:8000` 打开（电脑 IP 用 `ipconfig` 查看；如无法访问，检查 Windows 防火墙是否放行 8000 端口）
- 手机端可通过浏览器「添加到主屏幕」当 App 用（PWA）

> 开发前端时用 `cd frontend && npm run dev`（已配置 API 代理），改完 `npm run build` 即可。

## 打包成独立软件

**PC 桌面版**（需要 Node + Python，首次还需 `pip install pyinstaller pywebview pillow`）：

```bat
build-desktop.bat
```

产物为 `dist\SecQuiz\` 文件夹，双击 `SecQuiz.exe` 即可运行，整个文件夹拷给别人也能用。数据存在 exe 旁边的 `data\` 目录里。

**Android APK**（需要 JDK 17+ 和 Android SDK，自动安装到 `%USERPROFILE%\android-sdk`）：

```bat
build-apk.bat
```

产物为项目根目录的 `SecQuiz.apk`，传到手机直接安装（签名密钥在 `apk\secquiz.keystore`，删掉会重新生成，届时需卸载重装）。

**APK 是离线快照**：只包含打包时的题库。之后通过公众号链接新增了题目，想让 APK 也更新，就重新跑一次 `build-apk.bat`；手机和电脑在同一局域网时，用手机浏览器访问网页版可以随时看到最新题目和面经。


## 添加题目

### 方式一：更新 GitHub 题库

```bash
cd backend && python cli.py import-repo
```

### 方式二：微信公众号文章（推荐用于新增题目）

网页端：**设置 → 导入公众号文章为题目**，粘贴文章链接即可。
会自动下载文章图片到本地、按小标题切分为多道题（可取消勾选整篇一题）。

命令行：

```bash
python cli.py wechat https://mp.weixin.qq.com/s/xxxxxx
python cli.py wechat https://mp.weixin.qq.com/s/xxxxxx --no-split          # 整篇一题
python cli.py wechat https://mp.weixin.qq.com/s/xxxxxx --category 应急响应  # 自定义分类
```

### 方式三：手动出题

直接操作 SQLite（`data/app.db`）或告诉我扩展 `import-wechat` 接口，支持批量 JSON 导入。

## 面经导入

在「面经」页点击 **＋ 导入**：

- **网页链接**：粘贴牛客/知乎/CSDN/公众号等文章链接，自动提取正文，填写企业名保存（同链接自动去重）
- **粘贴文本**：把面经内容直接粘进来，填企业名（如"腾讯"）即可按企业分类

命令行：

```bash
python cli.py add-exp --url https://... --company 腾讯
python cli.py add-exp --file mianjing.txt --company 字节跳动 --position 安全工程师
```

## 常用命令

```bash
python cli.py import-repo     # 导入/更新题库
python cli.py stats           # 查看题库/面经统计
```

## 说明

- 数据全部存在本地 `data/app.db`（SQLite），备份这个文件即可备份全部数据
- 刷题进度按浏览器区分（本机标识），同一浏览器自动同步；换设备进度不迁移
- 网页抓取为 best-effort：需要登录或强反爬的页面（部分知乎/牛客页面）会提示失败，改用「粘贴文本」即可
- API 文档：<http://127.0.0.1:8000/api/docs>
