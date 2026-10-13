package com.promutualfund.analytics

import android.annotation.SuppressLint
import android.content.Context
import android.content.SharedPreferences
import android.graphics.Bitmap
import android.net.ConnectivityManager
import android.net.NetworkCapabilities
import android.os.Build
import android.os.Bundle
import android.view.View
import android.webkit.*
import android.widget.EditText
import android.widget.ProgressBar
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.core.content.ContextCompat
import androidx.swiperefreshlayout.widget.SwipeRefreshLayout
import com.google.android.material.dialog.MaterialAlertDialogBuilder

class MainActivity : AppCompatActivity() {

    private lateinit var webView: WebView
    private lateinit var swipeRefresh: SwipeRefreshLayout
    private lateinit var progressBar: ProgressBar
    private lateinit var errorLayout: View
    private lateinit var prefs: SharedPreferences

    private var backPressedTime: Long = 0
    private val PREFS_NAME = "pmf_prefs"
    private val KEY_SERVER_URL = "server_url"
    private val DEFAULT_URL = "https://mftool-master.up.railway.app/"

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        prefs = getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)

        initViews()
        setupWebView()
        setupSwipeRefresh()
        setupErrorHandling()

        loadDashboard()
    }

    private fun initViews() {
        webView = findViewById(R.id.webView)
        swipeRefresh = findViewById(R.id.swipeRefresh)
        progressBar = findViewById(R.id.progressBar)
        errorLayout = findViewById(R.id.errorLayout)
    }

    @SuppressLint("SetJavaScriptEnabled")
    private fun setupWebView() {
        val settings = webView.settings
        settings.javaScriptEnabled = true
        settings.domStorageEnabled = true
        settings.databaseEnabled = true
        settings.useWideViewPort = true
        settings.loadWithOverviewMode = true
        settings.setSupportZoom(false)
        settings.builtInZoomControls = false
        settings.displayZoomControls = false
        settings.allowFileAccess = true
        settings.allowContentAccess = true

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.LOLLIPOP) {
            settings.mixedContentMode = WebSettings.MIXED_CONTENT_ALWAYS_ALLOW
            CookieManager.getInstance().setAcceptThirdPartyCookies(webView, true)
        }

        settings.cacheMode = if (isNetworkAvailable()) {
            WebSettings.LOAD_DEFAULT
        } else {
            WebSettings.LOAD_CACHE_ELSE_NETWORK
        }

        webView.webViewClient = object : WebViewClient() {
            override fun onPageStarted(view: WebView?, url: String?, favicon: Bitmap?) {
                super.onPageStarted(view, url, favicon)
                progressBar.visibility = View.VISIBLE
                errorLayout.visibility = View.GONE
            }

            override fun onPageFinished(view: WebView?, url: String?) {
                super.onPageFinished(view, url)
                progressBar.visibility = View.GONE
                swipeRefresh.isRefreshing = false
            }

            override fun onReceivedError(
                view: WebView?,
                request: WebResourceRequest?,
                error: WebResourceError?
            ) {
                super.onReceivedError(view, request, error)
                if (request?.isForMainFrame == true) {
                    showError()
                }
            }

            override fun shouldOverrideUrlLoading(view: WebView?, request: WebResourceRequest?): Boolean {
                val url = request?.url?.toString() ?: return false
                // Keep internal app navigation inside the WebView
                return false
            }
        }

        webView.webChromeClient = object : WebChromeClient() {
            override fun onProgressChanged(view: WebView?, newProgress: Int) {
                progressBar.progress = newProgress
                if (newProgress >= 100) {
                    progressBar.visibility = View.GONE
                }
            }
        }
    }

    private fun setupSwipeRefresh() {
        swipeRefresh.setColorSchemeResources(R.color.cyan, R.color.purple)
        swipeRefresh.setProgressBackgroundColorSchemeResource(R.color.bg_card)
        swipeRefresh.setOnRefreshListener {
            webView.reload()
        }
    }

    private fun setupErrorHandling() {
        findViewById<View>(R.id.btnRetry).setOnClickListener {
            loadDashboard()
        }

        findViewById<View>(R.id.btnChangeUrl).setOnClickListener {
            showChangeUrlDialog()
        }
    }

    private fun loadDashboard() {
        val currentUrl = prefs.getString(KEY_SERVER_URL, DEFAULT_URL) ?: DEFAULT_URL
        if (isNetworkAvailable()) {
            errorLayout.visibility = View.GONE
            webView.visibility = View.VISIBLE
            webView.loadUrl(currentUrl)
        } else {
            showError("No internet connection detected.")
        }
    }

    private fun showError(customMsg: String? = null) {
        progressBar.visibility = View.GONE
        swipeRefresh.isRefreshing = false
        webView.visibility = View.GONE
        errorLayout.visibility = View.VISIBLE

        val currentUrl = prefs.getString(KEY_SERVER_URL, DEFAULT_URL) ?: DEFAULT_URL
        val detailText = findViewById<TextView>(R.id.errorDetailText)
        detailText.text = customMsg ?: "Could not connect to:\n$currentUrl\n\nEnsure your Flask server is running or configure the server URL."
    }

    private fun showChangeUrlDialog() {
        val currentUrl = prefs.getString(KEY_SERVER_URL, DEFAULT_URL) ?: DEFAULT_URL
        val input = EditText(this).apply {
            setText(currentUrl)
            setSelection(text.length)
            setTextColor(ContextCompat.getColor(this@MainActivity, R.color.white))
            setBackgroundColor(ContextCompat.getColor(this@MainActivity, R.color.bg_card))
            setPadding(32, 24, 32, 24)
        }

        MaterialAlertDialogBuilder(this)
            .setTitle("Configure Server URL")
            .setMessage("Enter the URL where your Pro Mutual Fund Flask backend is running (Local IP or Cloud Domain):")
            .setView(input)
            .setPositiveButton("Save & Connect") { _, _ ->
                val newUrl = input.text.toString().trim()
                if (newUrl.isNotEmpty()) {
                    prefs.edit().putString(KEY_SERVER_URL, newUrl).apply()
                    Toast.makeText(this, "URL updated!", Toast.LENGTH_SHORT).show()
                    loadDashboard()
                }
            }
            .setNegativeButton("Cancel", null)
            .setNeutralButton("Reset to Default") { _, _ ->
                prefs.edit().putString(KEY_SERVER_URL, DEFAULT_URL).apply()
                loadDashboard()
            }
            .show()
    }

    private fun isNetworkAvailable(): Boolean {
        val cm = getSystemService(Context.CONNECTIVITY_SERVICE) as ConnectivityManager
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
            val network = cm.activeNetwork ?: return false
            val capabilities = cm.getNetworkCapabilities(network) ?: return false
            return capabilities.hasCapability(NetworkCapabilities.NET_CAPABILITY_INTERNET)
        } else {
            @Suppress("DEPRECATION")
            val networkInfo = cm.activeNetworkInfo ?: return false
            @Suppress("DEPRECATION")
            return networkInfo.isConnected
        }
    }

    @Deprecated("Deprecated in Java")
    override fun onBackPressed() {
        if (webView.canGoBack()) {
            webView.goBack()
        } else {
            if (backPressedTime + 2000 > System.currentTimeMillis()) {
                super.onBackPressed()
            } else {
                Toast.makeText(this, "Press back again to exit", Toast.LENGTH_SHORT).show()
                backPressedTime = System.currentTimeMillis()
            }
        }
    }

    override fun onDestroy() {
        webView.destroy()
        super.onDestroy()
    }
}
