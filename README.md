# 安全面试刷题 (sec-job)

安全工程师面试刷题应用，题库来自 [duckpigdog/Sec-Interview](https://github.com/duckpigdog/Sec-Interview)（351 题，32 个方向）。PC / 手机 / APK 三端可用。

## 下载

| 形态 | 获取方式 | 说明 |
|------|---------|------|
| Android APK | [Releases](https://github.com/ca5ll41ng/sec-job/releases/latest) | 离线刷题，进度存手机本地 |
| PC 桌面版 | [Releases](https://github.com/ca5ll41ng/sec-job/releases/latest) | 解压后双击 `SecQuiz.exe` |
| 网页版（完整功能） | `start.bat` 启动后访问 `http://127.0.0.1:8000` | 含面经、公众号导入等全部功能；手机同一局域网访问 `http://电脑IP:8000` |

应用启动时会自动检查本页 Release 更新，有新版本会强制提示下载。

## 使用

```bash
# 首次：装依赖 + 导题库
cd backend && pip install -r requirements.txt && python cli.py import-repo
cd ../frontend && npm install && npm run build && cd ..

# 之后：start.bat 一键启动
```

**添加题目**：设置页粘贴公众号文章链接，或 `python cli.py wechat <文章链接>`；题库上游更新后跑 `python cli.py import-repo`。

**添加面经**：面经页点「导入」，粘贴链接或文本并填企业名，自动按企业分类。

**数据**：全部在 `data/app.db`（SQLite，无需装数据库），复制即备份。

## 打包

```bat
build-desktop.bat   :: 产出 dist\SecQuiz\SecQuiz.exe
build-apk.bat       :: 产出 SecQuiz.apk
```

发版：改根目录 `VERSION` → 跑对应打包脚本 → 在 GitHub 新建 Release 上传产物。旧版本应用会自动收到强制更新提示。
