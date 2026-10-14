@echo off
chcp 65001 >nul
cd /d %~dp0

echo [1/4] 导出题库 JSON...
cd backend && python cli.py export-static || goto :err
cd ..

echo [2/4] 构建前端...
cd frontend && call npm run build || goto :err
cd ..

echo [3/4] 打包 exe（约 1-3 分钟）...
python -m PyInstaller desktop\SecQuiz.spec --noconfirm || goto :err

echo [4/4] 复制数据库...
if not exist dist\SecQuiz\data mkdir dist\SecQuiz\data
copy /y data\app.db dist\SecQuiz\data\app.db >nul

echo.
echo 完成！产物: dist\SecQuiz\SecQuiz.exe （整个 SecQuiz 文件夹即可分发）
pause
exit /b 0

:err
echo 构建失败，请检查上方报错
pause
