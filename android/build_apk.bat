@echo off
setlocal enabledelayedexpansion
title Build Pro Mutual Fund Analytics Android APK

echo ======================================================================
echo       Pro Mutual Fund Analytics - Android APK Builder
echo ======================================================================
echo.

cd /d "%~dp0"

:: 1. Check for Java / JDK
if defined JAVA_HOME (
    echo [OK] JAVA_HOME is set to: %JAVA_HOME%
) else (
    echo [INFO] Searching for installed JDK or Android Studio bundled JBR...
    if exist "C:\Program Files\Microsoft" (
        for /d %%D in ("C:\Program Files\Microsoft\jdk*") do (
            set "JAVA_HOME=%%D"
        )
    )
    if not defined JAVA_HOME if exist "C:\Program Files\Java" (
        for /d %%D in ("C:\Program Files\Java\jdk*") do (
            set "JAVA_HOME=%%D"
        )
    )
    if not defined JAVA_HOME if exist "C:\Program Files\Eclipse Adoptium" (
        for /d %%D in ("C:\Program Files\Eclipse Adoptium\jdk*") do (
            set "JAVA_HOME=%%D"
        )
    )
    if not defined JAVA_HOME if exist "C:\Program Files\Android\Android Studio\jbr" (
        set "JAVA_HOME=C:\Program Files\Android\Android Studio\jbr"
    ) else if not defined JAVA_HOME if exist "C:\Program Files\Android\Android Studio\jre" (
        set "JAVA_HOME=C:\Program Files\Android\Android Studio\jre"
    )
    if defined JAVA_HOME echo [OK] Found JDK at: !JAVA_HOME!
)

if not defined JAVA_HOME (
    echo [WARNING] Java JDK not found in PATH or standard directories.
    echo Please install JDK 17+ or open this project in Android Studio.
) else (
    set "PATH=%JAVA_HOME%\bin;%PATH%"
)

:: 2. Check for Android SDK
if defined ANDROID_HOME (
    echo [OK] ANDROID_HOME is set to: %ANDROID_HOME%
) else if exist "%LOCALAPPDATA%\Android\Sdk" (
    set "ANDROID_HOME=%LOCALAPPDATA%\Android\Sdk"
    echo [OK] Found Android SDK at: !ANDROID_HOME!
) else (
    echo [INFO] ANDROID_HOME not set. Android Studio handles this automatically.
)

:: 3. Check for Gradle Wrapper JAR
if not exist "gradle\wrapper\gradle-wrapper.jar" (
    echo.
    echo [INFO] Downloading gradle-wrapper.jar...
    powershell -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; (New-Object System.Net.WebClient).DownloadFile('https://raw.githubusercontent.com/gradle/gradle/v8.2.0/gradle/wrapper/gradle-wrapper.jar', 'gradle\wrapper\gradle-wrapper.jar')"
    if exist "gradle\wrapper\gradle-wrapper.jar" (
        echo [OK] Gradle wrapper downloaded successfully.
    ) else (
        echo [NOTICE] If download fails, you can simply open this 'android' folder in Android Studio!
    )
)

:: 4. Build APK using gradlew
echo.
echo ======================================================================
echo   Compiling Debug APK (Running gradle assembleDebug)...
echo ======================================================================
echo.

if exist "gradlew.bat" (
    call gradlew.bat assembleDebug
) else (
    echo gradlew.bat not found. Generating gradlew wrapper script...
    call gradle wrapper
    call gradlew.bat assembleDebug
)

if exist "app\build\outputs\apk\debug\app-debug.apk" (
    echo.
    echo ======================================================================
    echo [SUCCESS] APK BUILT SUCCESSFULLY!
    echo ======================================================================
    copy /y "app\build\outputs\apk\debug\app-debug.apk" "ProMutualFund-Analytics.apk"
    echo.
    echo Ready-to-install APK created at:
    echo %~dp0ProMutualFund-Analytics.apk
    echo.
    echo You can transfer 'ProMutualFund-Analytics.apk' to your Android phone via
    echo USB cable, WhatsApp, Google Drive, or email and tap to install!
    echo ======================================================================
) else (
    echo.
    echo [RECOMMENDED EASY METHOD]:
    echo 1. Open Android Studio
    echo 2. Click 'Open' and select this folder: %~dp0
    echo 3. Wait for Gradle Sync to complete (it auto-downloads everything)
    echo 4. Go to Menu: Build -> Build Bundle(s) / APK(s) -> Build APK(s)
    echo 5. Android Studio will notify you with a 'locate' link to your APK!
)

echo.
pause
