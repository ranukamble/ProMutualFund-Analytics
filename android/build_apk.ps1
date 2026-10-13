# Build Pro Mutual Fund Analytics Android APK (PowerShell Script)
$Host.UI.RawUI.WindowTitle = "Build Pro Mutual Fund Analytics APK"

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "      Pro Mutual Fund Analytics - Android APK Builder (PowerShell)" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

# 1. Check for Java / JDK
if ($env:JAVA_HOME -and (Test-Path $env:JAVA_HOME)) {
    Write-Host "[OK] JAVA_HOME is set to: $env:JAVA_HOME" -ForegroundColor Green
} else {
    Write-Host "[INFO] Searching for installed JDK..." -ForegroundColor Yellow
    $msftDirs = Get-ChildItem -Path "C:\Program Files\Microsoft" -Filter "jdk*" -ErrorAction SilentlyContinue
    if ($msftDirs) {
        $env:JAVA_HOME = $msftDirs[0].FullName
        Write-Host "[OK] Found Microsoft OpenJDK at: $env:JAVA_HOME" -ForegroundColor Green
    } elseif (Test-Path "C:\Program Files\Android\Android Studio\jbr") {
        $env:JAVA_HOME = "C:\Program Files\Android\Android Studio\jbr"
        Write-Host "[OK] Found Android Studio JBR at: $env:JAVA_HOME" -ForegroundColor Green
    } elseif (Test-Path "C:\Program Files\Android\Android Studio\jre") {
        $env:JAVA_HOME = "C:\Program Files\Android\Android Studio\jre"
        Write-Host "[OK] Found Android Studio JRE at: $env:JAVA_HOME" -ForegroundColor Green
    } else {
        $jdkDirs = Get-ChildItem -Path "C:\Program Files\Java" -Filter "jdk*" -ErrorAction SilentlyContinue
        if ($jdkDirs) {
            $env:JAVA_HOME = $jdkDirs[0].FullName
            Write-Host "[OK] Found JDK at: $env:JAVA_HOME" -ForegroundColor Green
        }
    }
}

if (-not $env:JAVA_HOME) {
    Write-Host "[WARNING] Java JDK not found in PATH or standard directories." -ForegroundColor Red
    Write-Host "Please install JDK 17+ or open this project in Android Studio." -ForegroundColor Yellow
} else {
    $env:PATH = "$env:JAVA_HOME\bin;$env:PATH"
}

# 2. Check for Android SDK
if ($env:ANDROID_HOME -and (Test-Path $env:ANDROID_HOME)) {
    Write-Host "[OK] ANDROID_HOME is set to: $env:ANDROID_HOME" -ForegroundColor Green
} elseif (Test-Path "$env:LOCALAPPDATA\Android\Sdk") {
    $env:ANDROID_HOME = "$env:LOCALAPPDATA\Android\Sdk"
    Write-Host "[OK] Found Android SDK at: $env:ANDROID_HOME" -ForegroundColor Green
} else {
    Write-Host "[INFO] ANDROID_HOME not set in environment. (Android Studio handles this automatically)" -ForegroundColor Gray
}

# 3. Check for Gradle Wrapper JAR
$wrapperJar = Join-Path $ScriptDir "gradle\wrapper\gradle-wrapper.jar"
if (-not (Test-Path $wrapperJar)) {
    Write-Host ""
    Write-Host "[INFO] Downloading gradle-wrapper.jar..." -ForegroundColor Cyan
    try {
        [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
        $url = "https://raw.githubusercontent.com/gradle/gradle/v8.2.0/gradle/wrapper/gradle-wrapper.jar"
        Invoke-WebRequest -Uri $url -OutFile $wrapperJar -UseBasicParsing
        Write-Host "[OK] Gradle wrapper downloaded successfully." -ForegroundColor Green
    } catch {
        Write-Host "[NOTICE] Could not auto-download wrapper. If needed, open this folder in Android Studio!" -ForegroundColor Yellow
    }
}

# 4. Build APK using gradlew
Write-Host ""
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "  Compiling Debug APK (Running gradlew.bat assembleDebug)..." -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""

if (Test-Path ".\gradlew.bat") {
    & ".\gradlew.bat" assembleDebug
} else {
    Write-Host "gradlew.bat not found." -ForegroundColor Red
}

$apkOutput = Join-Path $ScriptDir "app\build\outputs\apk\debug\app-debug.apk"
$finalApk = Join-Path $ScriptDir "ProMutualFund-Analytics.apk"

if (Test-Path $apkOutput) {
    Copy-Item -Path $apkOutput -Destination $finalApk -Force
    Write-Host ""
    Write-Host "======================================================================" -ForegroundColor Green
    Write-Host "[SUCCESS] APK BUILT SUCCESSFULLY!" -ForegroundColor Green
    Write-Host "======================================================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Ready-to-install APK created at:" -ForegroundColor Yellow
    Write-Host "$finalApk" -ForegroundColor White
    Write-Host ""
    Write-Host "Transfer this APK to your phone via USB cable, WhatsApp, or Google Drive and tap to install!" -ForegroundColor Cyan
    Write-Host "======================================================================" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "======================================================================" -ForegroundColor Yellow
    Write-Host "  If the command line build needs SDK setup, use the 2-minute Easy Method:" -ForegroundColor Yellow
    Write-Host "======================================================================" -ForegroundColor Yellow
    Write-Host "1. Open Android Studio" -ForegroundColor White
    Write-Host "2. Click 'Open' and select: $ScriptDir" -ForegroundColor White
    Write-Host "3. In top menu, click: Build -> Build Bundle(s) / APK(s) -> Build APK(s)" -ForegroundColor White
    Write-Host "4. Android Studio will notify you with a 'locate' link to your ready APK!" -ForegroundColor White
    Write-Host "======================================================================" -ForegroundColor Yellow
}

Write-Host ""
