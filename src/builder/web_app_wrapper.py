"""APK Compiler - Web App Wrapper Module.

Generates the native Android Java MainActivity and XML file provider configuration
for wrapping web applications inside a high-performance, full-featured WebView.
"""

from typing import Any, Dict


class WebAppWrapper:
    """Generates Java source code for WebView MainActivity and supporting assets."""

    def generate_main_activity(self, package_name: str, config: Dict[str, Any]) -> str:
        """Generate complete MainActivity.java source code.

        Config options:
            fullscreen (bool): Immersive full-screen mode.
            status_bar_color (str): Hex color code (e.g. "#1E1E2E").
            dark_status_icons (bool): Dark icons on light status bar.
            app_url (str): Custom initial URL (defaults to assets/www/index.html).
            allow_zoom (bool): Allow pinch to zoom.
            cache_mode (str): Cache setting ("LOAD_DEFAULT", etc.).
        """
        fullscreen = config.get("fullscreen", False)
        status_bar_color = config.get("status_bar_color", "#1E1E2E")
        allow_zoom = config.get("allow_zoom", True)
        app_url = config.get("app_url", "file:///android_asset/www/index.html")

        # Java code generation
        java_code = f"""package {package_name};

import android.annotation.SuppressLint;
import android.annotation.TargetApi;
import android.app.Activity;
import android.app.AlertDialog;
import android.content.ClipData;
import android.content.DialogInterface;
import android.content.Intent;
import android.content.res.Configuration;
import android.graphics.Bitmap;
import android.graphics.Color;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.view.ViewGroup;
import android.view.Window;
import android.view.WindowManager;
import android.webkit.ConsoleMessage;
import android.webkit.GeolocationPermissions;
import android.webkit.JsPromptResult;
import android.webkit.JsResult;
import android.webkit.ValueCallback;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceError;
import android.webkit.WebResourceRequest;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.EditText;
import android.widget.FrameLayout;
import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.appcompat.app.AppCompatActivity;

public class MainActivity extends AppCompatActivity {{

    private static final String TAG = "MainActivity";
    private static final int FILE_CHOOSER_REQUEST_CODE = 1001;

    private WebView webView;
    private ValueCallback<Uri[]> mUploadCallback;
    private View mCustomView;
    private WebChromeClient.CustomViewCallback mCustomViewCallback;
    private FrameLayout mCustomViewContainer;

    @SuppressLint("SetJavaScriptEnabled")
    @Override
    protected void onCreate(Bundle savedInstanceState) {{
        super.onCreate(savedInstanceState);

        // Configure window display
        configureWindow();

        setContentView(R.layout.activity_main);

        webView = findViewById(R.id.webview);
        mCustomViewContainer = findViewById(R.id.customViewContainer);

        setupWebViewSettings();
        setupWebViewClients();

        // Restore state or load entry point
        if (savedInstanceState != null) {{
            webView.restoreState(savedInstanceState);
        }} else {{
            webView.loadUrl("{app_url}");
        }}
    }}

    private void configureWindow() {{
        Window window = getWindow();

        {"applyFullscreen(window);" if fullscreen else f"applyStatusBarColor(window, \"{status_bar_color}\");"}
    }}

    private void applyStatusBarColor(Window window, String colorHex) {{
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.LOLLIPOP) {{
            try {{
                window.addFlags(WindowManager.LayoutParams.FLAG_DRAWS_SYSTEM_BAR_BACKGROUNDS);
                window.clearFlags(WindowManager.LayoutParams.FLAG_TRANSLUCENT_STATUS);
                window.setStatusBarColor(Color.parseColor(colorHex));
            }} catch (Exception e) {{
                Log.e(TAG, "Error applying status bar color: " + e.getMessage());
            }}
        }}
    }}

    private void applyFullscreen(Window window) {{
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) {{
            window.setDecorFitsSystemWindows(false);
            android.view.WindowInsetsController controller = window.getInsetsController();
            if (controller != null) {{
                controller.hide(android.view.WindowInsets.Type.statusBars() | android.view.WindowInsets.Type.navigationBars());
                controller.setSystemBarsBehavior(android.view.WindowInsetsController.BEHAVIOR_SHOW_TRANSIENT_BARS_BY_SWIPE);
            }}
        }} else {{
            window.getDecorView().setSystemUiVisibility(
                View.SYSTEM_UI_FLAG_LAYOUT_STABLE
                | View.SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION
                | View.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN
                | View.SYSTEM_UI_FLAG_HIDE_NAVIGATION
                | View.SYSTEM_UI_FLAG_FULLSCREEN
                | View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY
            );
        }}
    }}

    @Override
    public void onWindowFocusChanged(boolean hasFocus) {{
        super.onWindowFocusChanged(hasFocus);
        {"if (hasFocus) { applyFullscreen(getWindow()); }" if fullscreen else ""}
    }}

    @SuppressLint({{"SetJavaScriptEnabled", "AllowFileAccessFromFileURLs", "AllowUniversalAccessFromFileURLs"}})
    private void setupWebViewSettings() {{
        WebSettings settings = webView.getSettings();

        // JavaScript & DOM Storage
        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);
        settings.setDatabaseEnabled(true);

        // File and Asset Access
        settings.setAllowFileAccess(true);
        settings.setAllowContentAccess(true);
        settings.setAllowFileAccessFromFileURLs(true);
        settings.setAllowUniversalAccessFromFileURLs(true);

        // Mixed content
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.LOLLIPOP) {{
            settings.setMixedContentMode(WebSettings.MIXED_CONTENT_ALWAYS_ALLOW);
        }}

        // Viewport and Scaling
        settings.setUseWideViewPort(true);
        settings.setLoadWithOverviewMode(true);
        settings.setSupportZoom({"true" if allow_zoom else "false"});
        settings.setBuiltInZoomControls({"true" if allow_zoom else "false"});
        settings.setDisplayZoomControls(false);

        // Media and Caching
        settings.setMediaPlaybackRequiresUserGesture(false);
        settings.setCacheMode(WebSettings.LOAD_DEFAULT);

        // Geolocation
        settings.setGeolocationEnabled(true);

        // Performance
        webView.setScrollBarStyle(View.SCROLLBARS_INSIDE_OVERLAY);
        webView.setFocusable(true);
        webView.setFocusableInTouchMode(true);
    }}

    private void setupWebViewClients() {{
        webView.setWebViewClient(new WebViewClient() {{
            @Override
            public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest request) {{
                return handleUrl(view, request.getUrl().toString());
            }}

            @SuppressWarnings("deprecation")
            @Override
            public boolean shouldOverrideUrlLoading(WebView view, String url) {{
                return handleUrl(view, url);
            }}

            private boolean handleUrl(WebView view, String url) {{
                if (url == null) return false;

                // Handle system schemes: tel, mailto, sms, geo, market, whatsapp
                if (url.startsWith("tel:") ||
                    url.startsWith("mailto:") ||
                    url.startsWith("sms:") ||
                    url.startsWith("geo:") ||
                    url.startsWith("market:") ||
                    url.startsWith("intent:") ||
                    url.startsWith("whatsapp:")) {{
                    try {{
                        Intent intent = new Intent(Intent.ACTION_VIEW, Uri.parse(url));
                        startActivity(intent);
                        return true;
                    }} catch (Exception e) {{
                        Log.e(TAG, "Cannot handle URL scheme: " + url, e);
                        return true;
                    }}
                }}

                // Keep local or web URLs inside the WebView
                return false;
            }}

            @Override
            public void onReceivedError(WebView view, WebResourceRequest request, WebResourceError error) {{
                super.onReceivedError(view, request, error);
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {{
                    Log.w(TAG, "WebView error: " + error.getDescription() + " for " + request.getUrl());
                }}
            }}
        }});

        webView.setWebChromeClient(new WebChromeClient() {{
            // Console logging
            @Override
            public boolean onConsoleMessage(ConsoleMessage consoleMessage) {{
                Log.d("WebConsole", consoleMessage.message() + " -- From line "
                    + consoleMessage.lineNumber() + " of " + consoleMessage.sourceId());
                return true;
            }}

            // JavaScript alert dialog
            @Override
            public boolean onJsAlert(WebView view, String url, String message, final JsResult result) {{
                new AlertDialog.Builder(MainActivity.this)
                    .setTitle(R.string.app_name)
                    .setMessage(message)
                    .setPositiveButton(android.R.string.ok, new DialogInterface.OnClickListener() {{
                        public void onClick(DialogInterface dialog, int which) {{
                            result.confirm();
                        }}
                    }})
                    .setCancelable(false)
                    .create()
                    .show();
                return true;
            }}

            // JavaScript confirm dialog
            @Override
            public boolean onJsConfirm(WebView view, String url, String message, final JsResult result) {{
                new AlertDialog.Builder(MainActivity.this)
                    .setTitle(R.string.app_name)
                    .setMessage(message)
                    .setPositiveButton(android.R.string.ok, new DialogInterface.OnClickListener() {{
                        public void onClick(DialogInterface dialog, int which) {{
                            result.confirm();
                        }}
                    }})
                    .setNegativeButton(android.R.string.cancel, new DialogInterface.OnClickListener() {{
                        public void onClick(DialogInterface dialog, int which) {{
                            result.cancel();
                        }}
                    }})
                    .setCancelable(false)
                    .create()
                    .show();
                return true;
            }}

            // JavaScript prompt dialog
            @Override
            public boolean onJsPrompt(WebView view, String url, String message, String defaultValue, final JsPromptResult result) {{
                final EditText input = new EditText(MainActivity.this);
                input.setText(defaultValue);
                new AlertDialog.Builder(MainActivity.this)
                    .setTitle(R.string.app_name)
                    .setMessage(message)
                    .setView(input)
                    .setPositiveButton(android.R.string.ok, new DialogInterface.OnClickListener() {{
                        public void onClick(DialogInterface dialog, int which) {{
                            result.confirm(input.getText().toString());
                        }}
                    }})
                    .setNegativeButton(android.R.string.cancel, new DialogInterface.OnClickListener() {{
                        public void onClick(DialogInterface dialog, int which) {{
                            result.cancel();
                        }}
                    }})
                    .setCancelable(false)
                    .create()
                    .show();
                return true;
            }}

            // Geolocation permission request
            @Override
            public void onGeolocationPermissionsShowPrompt(String origin, GeolocationPermissions.Callback callback) {{
                callback.invoke(origin, true, false);
            }}

            // File uploads support (HTML5 input type="file")
            @Override
            public boolean onShowFileChooser(WebView webView, ValueCallback<Uri[]> filePathCallback, FileChooserParams fileChooserParams) {{
                if (mUploadCallback != null) {{
                    mUploadCallback.onReceiveValue(null);
                    mUploadCallback = null;
                }}
                mUploadCallback = filePathCallback;

                Intent intent = null;
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.LOLLIPOP) {{
                    intent = fileChooserParams.createIntent();
                }} else {{
                    intent = new Intent(Intent.ACTION_GET_CONTENT);
                    intent.addCategory(Intent.CATEGORY_OPENABLE);
                    intent.setType("*/*");
                }}

                try {{
                    startActivityForResult(Intent.createChooser(intent, "Select File"), FILE_CHOOSER_REQUEST_CODE);
                    return true;
                }} catch (Exception e) {{
                    Log.e(TAG, "File chooser error: " + e.getMessage());
                    if (mUploadCallback != null) {{
                        mUploadCallback.onReceiveValue(null);
                        mUploadCallback = null;
                    }}
                    return false;
                }}
            }}

            // Fullscreen video support
            @Override
            public void onShowCustomView(View view, CustomViewCallback callback) {{
                if (mCustomView != null) {{
                    callback.onCustomViewHidden();
                    return;
                }}
                mCustomView = view;
                mCustomViewCallback = callback;
                mCustomViewContainer.addView(view);
                mCustomViewContainer.setVisibility(View.VISIBLE);
                webView.setVisibility(View.GONE);
            }}

            @Override
            public void onHideCustomView() {{
                if (mCustomView == null) return;
                mCustomViewContainer.removeView(mCustomView);
                mCustomViewContainer.setVisibility(View.GONE);
                webView.setVisibility(View.VISIBLE);
                if (mCustomViewCallback != null) {{
                    mCustomViewCallback.onCustomViewHidden();
                }}
                mCustomView = null;
                mCustomViewCallback = null;
            }}
        }});
    }}

    @Override
    protected void onActivityResult(int requestCode, int resultCode, @Nullable Intent data) {{
        super.onActivityResult(requestCode, resultCode, data);

        if (requestCode == FILE_CHOOSER_REQUEST_CODE) {{
            if (mUploadCallback == null) return;

            Uri[] results = null;
            if (resultCode == Activity.RESULT_OK && data != null) {{
                String dataString = data.getDataString();
                ClipData clipData = data.getClipData();

                if (clipData != null) {{
                    results = new Uri[clipData.getItemCount()];
                    for (int i = 0; i < clipData.getItemCount(); i++) {{
                        results[i] = clipData.getItemAt(i).getUri();
                    }}
                }} else if (dataString != null) {{
                    results = new Uri[]{{Uri.parse(dataString)}};
                }}
            }}
            mUploadCallback.onReceiveValue(results);
            mUploadCallback = null;
        }}
    }}

    @Override
    public void onBackPressed() {{
        if (mCustomView != null) {{
            // Exit fullscreen video if active
            WebChromeClient client = webView.getWebChromeClient();
            if (client != null) {{
                client.onHideCustomView();
            }}
        }} else if (webView != null && webView.canGoBack()) {{
            webView.goBack();
        }} else {{
            super.onBackPressed();
        }}
    }}

    @Override
    protected void onSaveInstanceState(@NonNull Bundle outState) {{
        super.onSaveInstanceState(outState);
        if (webView != null) {{
            webView.saveState(outState);
        }}
    }}

    @Override
    protected void onPause() {{
        super.onPause();
        if (webView != null) {{
            webView.onPause();
            webView.pauseTimers();
        }}
    }}

    @Override
    protected void onResume() {{
        super.onResume();
        if (webView != null) {{
            webView.onResume();
            webView.resumeTimers();
        }}
    }}

    @Override
    protected void onDestroy() {{
        if (webView != null) {{
            webView.loadUrl("about:blank");
            webView.stopLoading();
            webView.setWebChromeClient(null);
            webView.setWebViewClient(null);
            ((ViewGroup) webView.getParent()).removeView(webView);
            webView.destroy();
            webView = null;
        }}
        super.onDestroy();
    }}
}}
"""
        return java_code

    def generate_file_provider_paths(self) -> str:
        """Generate file_paths.xml for FileProvider."""
        return """<?xml version="1.0" encoding="utf-8"?>
<paths xmlns:android="http://schemas.android.com/apk/res/android">
    <external-path name="external_files" path="." />
    <external-cache-path name="external_cache" path="." />
    <cache-path name="internal_cache" path="." />
    <files-path name="internal_files" path="." />
</paths>
"""
