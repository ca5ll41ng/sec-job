@echo off
chcp 65001 >nul
cd /d %~dp0
setlocal
set SDK=%USERPROFILE%\android-sdk
set BT=%SDK%\build-tools\34.0.0
set AJ=%SDK%\platforms\android-34\android.jar

echo [1/3] 导出题库 JSON...
cd backend && python cli.py export-static || goto :err
cd ..

echo [2/3] 构建离线前端...
cd frontend && call npx vite build --base=./ --outDir dist-apk || goto :err
cd ..

echo [3/3] 编译 APK...
cd apk
if exist build rmdir /s /q build
if exist assets rmdir /s /q assets
mkdir build
xcopy /e /i /y ..\frontend\dist-apk assets >nul
"%BT%\aapt2.exe" compile --dir res -o build\res.zip || goto :err
"%BT%\aapt2.exe" link -o build\base.apk -I "%AJ%" --manifest AndroidManifest.xml -R build\res.zip -A assets --min-sdk-version 24 --target-sdk-version 34 --auto-add-overlay || goto :err
javac -nowarn -source 8 -target 8 -classpath "%AJ%" -d build\classes java\com\secquiz\app\MainActivity.java || goto :err
call "%BT%\d8.bat" --release --lib "%AJ%" --output build build\classes\com\secquiz\app\MainActivity.class || goto :err
python -c "import zipfile,shutil; shutil.copy('build/base.apk','build/unsigned.apk'); zipfile.ZipFile('build/unsigned.apk','a',zipfile.ZIP_DEFLATED).write('build/classes.dex','classes.dex')" || goto :err
"%BT%\zipalign.exe" -f 4 build\unsigned.apk build\aligned.apk || goto :err
if not exist secquiz.keystore keytool -genkeypair -keystore secquiz.keystore -alias secquiz -keyalg RSA -keysize 2048 -validity 10000 -storepass secquiz2025 -keypass secquiz2025 -dname "CN=SecQuiz, OU=Personal, O=SecQuiz, C=CN"
call "%BT%\apksigner.bat" sign --ks secquiz.keystore --ks-key-alias secquiz --ks-pass pass:secquiz2025 --out ..\SecQuiz.apk build\aligned.apk || goto :err
cd ..
echo.
echo 完成！产物: SecQuiz.apk （传到手机直接安装）
pause
exit /b 0

:err
echo 构建失败，请检查上方报错
pause
