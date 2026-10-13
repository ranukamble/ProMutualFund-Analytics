# Proguard rules for Pro Mutual Fund Analytics
-keepattributes *Annotation*
-keepclassmembers class * {
    @android.webkit.JavascriptInterface <methods>;
}
