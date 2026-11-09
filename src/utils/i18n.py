"""
APK Compiler - Internationalization (i18n) Module.
Provides centralized bilingual support (English and Bengali) with reactive listeners.
"""

from typing import Callable, Dict, List, Optional

class I18NManager:
    """Manages bilingual localization state and UI subscriber callbacks."""

    def __init__(self, default_lang: str = "en"):
        self._current_lang = default_lang if default_lang in ("en", "bn") else "en"
        self._listeners: List[Callable[[str], None]] = []

    @property
    def current_lang(self) -> str:
        return self._current_lang

    def set_language(self, lang: str):
        if lang in ("en", "bn") and lang != self._current_lang:
            self._current_lang = lang
            self._notify_listeners()

    def toggle_language(self) -> str:
        new_lang = "bn" if self._current_lang == "en" else "en"
        self.set_language(new_lang)
        return new_lang

    def register_listener(self, callback: Callable[[str], None]):
        """Register a component callback to update text when language switches."""
        if callback not in self._listeners:
            self._listeners.append(callback)

    def unregister_listener(self, callback: Callable[[str], None]):
        if callback in self._listeners:
            self._listeners.remove(callback)

    def _notify_listeners(self):
        for cb in list(self._listeners):
            try:
                cb(self._current_lang)
            except Exception as e:
                print(f"Error notifying i18n listener: {e}")

    def t(self, key: str, **kwargs) -> str:
        """Translate a key into the active language, formatting placeholders if provided."""
        text = TRANSLATIONS.get(self._current_lang, {}).get(key)
        if text is None:
            text = TRANSLATIONS.get("en", {}).get(key, key)
        if kwargs:
            try:
                return text.format(**kwargs)
            except Exception:
                return text
        return text


# Global instance
i18n = I18NManager(default_lang="en")


TRANSLATIONS: Dict[str, Dict[str, str]] = {
    "en": {
        # App branding
        "app_title": "APK Compiler",
        "app_subtitle": "PRO COMPILER",
        "window_title": "APK Compiler - Web & Native Android Compiler",
        "dashboard_desc": "Convert Web Apps and Google AI Studio projects into production-ready Android packages.",
        
        # Navigation
        "nav_heading": "NAVIGATION",
        "nav_dashboard": "⚡  Dashboard",
        "nav_new_build": "📦  New Build",
        "nav_history": "📜  Build History",
        "nav_settings": "⚙️  Settings",
        "quick_hint_title": "💡 Quick Hint",
        "quick_hint_desc": "Drag & drop your ZIP archive or project folder anywhere on the upload screen to start building.",
        
        # Topbar
        "engine_ready": "● Engine Ready (JDK 17 + SDK)",
        "engine_missing": "⚠ Setup Required (JDK/SDK)",
        "theme_light": "☀ Light",
        "theme_dark": "🌙 Dark",
        "lang_toggle_btn": "🌐 বাংলা",  # Click to switch to Bangla
        "status_ready": "System Ready  •  No Issues Detected",
        "status_active": "{page} Active",
        
        # Breadcrumbs
        "page_dashboard": "Project Dashboard",
        "page_upload": "Source Package (Step 1/4)",
        "page_config": "App Configuration (Step 2/4)",
        "page_build": "APK Compilation (Step 3/4)",
        "page_result": "Release Artifact (Step 4/4)",
        "page_history": "Build History & Archive",
        "page_settings": "System Settings & Environment",

        # Wizard steps
        "step_1": "Source Package",
        "step_2": "Configuration",
        "step_3": "Compilation",
        "step_4": "Release Ready",

        # Dashboard / Welcome
        "dash_badge": "v1.0.0 • PRODUCTION READY ANDROID COMPILER",
        "dash_hero_title": "Compile Native Android APKs",
        "dash_hero_subtitle": "Convert Web Apps and Google AI Studio projects into production-ready Android packages.",
        "dash_hero_desc": "Fully automated APK toolchain bundling Adoptium OpenJDK 17 and Android SDK build tools. Supports native Kotlin Jetpack Compose projects or wraps HTML5/CSS/JavaScript web applications.",
        "btn_start_new_build": "⚡ Start New Build",
        "btn_env_settings": "⚙ Environment Settings",
        "features_title": "Key Platform Features",
        "features_subtitle": "Engineered for reliability, zero setup friction, and high-performance compilation.",
        "feat_zero_title": "Zero Setup Required",
        "feat_zero_desc": "Bundled OpenJDK 17 and Android SDK platforms 34/36. No external environment installations necessary.",
        "feat_support_title": "Web & Native Support",
        "feat_support_desc": "Directly builds Google AI Studio Kotlin/Compose exports or wraps HTML5, CSS3, & JS single-page web apps.",
        "feat_sign_title": "Signed & ZipAligned",
        "feat_sign_desc": "Automatic keystore generation, Android v1/v2 signature verification, and zip-aligned APK packages.",
        "recent_builds_title": "Recent Builds",
        "recent_builds_desc": "Quick access to your most recently compiled Android packages.",
        "no_recent_builds": "No builds yet. Click 'Start New Build' to compile your first APK.",
        
        # Upload Page
        "upload_title": "Upload Source Package",
        "upload_subtitle": "Drag and drop your project ZIP or folder below, or browse from your PC.",
        "dropzone_title": "Drag & Drop Project ZIP or Folder Here",
        "dropzone_subtitle": "Supports Google AI Studio exports (.zip), native Android projects, or Web Apps (with index.html)",
        "dropzone_selected_zip": "ZIP Archive Selected",
        "dropzone_selected_folder": "Project Directory Selected",
        "dropzone_click_to_change": "Drag another file here or click to change selection",
        "btn_browse_folder": "📁  Browse Folder",
        "btn_browse_zip": "📦  Select ZIP Archive",
        "btn_reset": "🔄  Reset",
        "selected_package_info": "Selected Package Details",
        "pkg_type_studio": "Google AI Studio Project (Kotlin / Compose)",
        "pkg_type_native": "Native Android Project (Gradle)",
        "pkg_type_web": "HTML5 Web Application (index.html)",
        "pkg_status_ready": "✓ Valid project structure verified and ready to compile",
        "pkg_status_missing": "⚠ Invalid package: Missing index.html or Android build configuration",
        "btn_back_dash": "← Dashboard",
        "btn_continue_config": "Continue to Configuration →",
        "alert_native_verified": "✅ Native Android Project Verified ({name})",
        "alert_web_verified": "✅ Valid Web Application Verified (Root index.html found)",
        "alert_invalid": "⚠️ Missing index.html or Android build configuration in source root",

        # Config Page
        "config_title": "Application Configuration",
        "config_subtitle": "Customize your Android app metadata, package identifier, styling, and permissions.",
        "app_identity_section": "Application Identity",
        "app_name_label": "App Display Name",
        "app_name_ph": "e.g. My Great App",
        "package_name_label": "Package Identifier (Application ID)",
        "package_name_ph": "e.g. com.company.myapp",
        "version_name_label": "Version Name",
        "version_name_ph": "1.0.0",
        "version_code_label": "Version Code (Integer)",
        "version_code_ph": "1",
        "app_icon_section": "App Icon & Branding",
        "app_icon_desc": "Select a custom PNG or JPEG image for your application launcher icon (512x512 recommended).",
        "btn_browse_icon": "🖼 Select Icon",
        "btn_reset_icon": "Default Icon",
        "behavior_section": "Display & Permissions",
        "orientation_label": "Screen Orientation",
        "orientation_portrait": "Portrait (Vertical)",
        "orientation_landscape": "Landscape (Horizontal)",
        "orientation_auto": "Auto-Rotate / Sensor",
        "chk_fullscreen": "Enable Fullscreen Mode (Hide Android system navigation & status bar)",
        "chk_internet": "Grant Internet Permission (Required for network and API access)",
        "chk_cleartext": "Allow HTTP Cleartext Traffic (Required for non-HTTPS local URLs)",
        "status_color_label": "Status Bar Tint Color",
        "btn_back_upload": "← Back to Upload",
        "btn_start_compilation": "🚀 Start APK Compilation",

        # Build Page
        "build_title": "APK Compilation & Assembly",
        "build_subtitle": "Real-time engine logs, step verification, and Android packaging pipeline.",
        "build_progress_title": "Overall Compilation Progress",
        "build_steps_title": "Pipeline Verification Steps",
        "step_prep": "Preparing project structure & environment...",
        "step_copy": "Copying and optimizing web assets...",
        "step_res": "Processing Android resources & manifest...",
        "step_compile": "Compiling source code and building release DEX...",
        "step_sign": "Signing APK with keystore and running zipalign...",
        "step_done": "Compilation finished successfully!",
        "console_logs_title": "Engine Console Output (Real-time)",
        "btn_clear_logs": "Clear Log",
        "btn_cancel_build": "✖ Cancel Build",
        "btn_view_result": "View Completed APK →",

        # Result Page
        "result_title": "Compilation Successful!",
        "result_subtitle": "Your release-ready Android APK has been compiled, signed, and optimized.",
        "apk_details_title": "Artifact Details",
        "apk_name": "App Name:",
        "apk_package": "Package ID:",
        "apk_version": "Version:",
        "apk_size": "File Size:",
        "apk_location": "Output Location:",
        "btn_open_folder": "📂 Open Output Folder",
        "btn_share_apk": "📤 Share / Send APK",
        "btn_build_another": "⚡ Build Another APK",
        "install_guide_title": "How to Install on Any Android Device",
        "install_guide_step1": "1. Transfer the .apk file to your Android phone via USB, WhatsApp, Telegram, or Google Drive.",
        "install_guide_step2": "2. Tap on the file in your phone's file manager to trigger Android Package Installer.",
        "install_guide_step3": "3. If prompted, allow 'Install Unknown Apps' for your file manager or browser.",
        "install_guide_step4": "4. Tap 'Install' and launch your brand-new Android app!",

        # History Page
        "history_title": "Build History & Archive",
        "history_subtitle": "Archive of all compiled Android packages, artifacts, and target output paths.",
        "history_empty_title": "No Build History Recorded Yet",
        "history_empty_desc": "Compile your first Web App or native project by clicking 'New Build' in the sidebar.",
        "btn_locate_file": "📂 Open Folder",

        # Settings Page
        "settings_title": "System Settings & Configuration",
        "settings_subtitle": "Manage bundled compiler tools (Adoptium JDK, Android SDK), directories, and signing preferences.",
        "tools_section": "Compiler Toolchain",
        "tools_desc": "Java Development Kit (JDK 17+) and Android SDK Command-line Tools are pre-bundled and configured.",
        "jdk_path_label": "Java JDK Path",
        "sdk_path_label": "Android SDK Path",
        "output_dir_label": "APK Output Directory",
        "btn_browse": "Browse",
        "btn_auto_setup": "⚡ Auto-Detect Tools",
        "btn_save_settings": "💾 Save Settings",
        "btn_reset_settings": "🔄 Reset Defaults",
        "appearance_section": "Appearance & Theme",
        "appearance_desc": "Select your preferred visual style. Default is Obsidian Glass Dark Theme.",
        "theme_dark_option": "Dark (Obsidian Glass)",
        "theme_light_option": "Light (Graphite Frost)",
        "saved_msg": "Settings saved successfully!",
    },

    "bn": {
        # App branding
        "app_title": "APK কম্পাইলার",
        "app_subtitle": "প্রো কম্পাইলার",
        "window_title": "APK কম্পাইলার - ওয়েব ও নেটিভ অ্যান্ড্রয়েড কম্পাইলার",
        "dashboard_desc": "ওয়েব অ্যাপ এবং গুগল AI স্টুডিও প্রজেক্ট থেকে সহজে তৈরি করুন ইনস্টলযোগ্য অ্যান্ড্রয়েড APK।",
        
        # Navigation
        "nav_heading": "মেনু তালিকা",
        "nav_dashboard": "⚡  ড্যাশবোর্ড",
        "nav_new_build": "📦  নতুন বিল্ড",
        "nav_history": "📜  বিল্ড ইতিহাস",
        "nav_settings": "⚙️  সেটিংস",
        "quick_hint_title": "💡 সহায়ক টিপস",
        "quick_hint_desc": "যেকোনো প্রজেক্ট ZIP বা ফোল্ডার সরাসরি ড্র্যাগ করে আপলোড স্ক্রিনে ছেড়ে দিলেই বিল্ড শুরু হবে।",
        
        # Topbar
        "engine_ready": "● ইঞ্জিন প্রস্তুত (JDK 17 + SDK)",
        "engine_missing": "⚠ সেটআপ প্রয়োজন (JDK/SDK)",
        "theme_light": "☀ লাইট",
        "theme_dark": "🌙 ডার্ক",
        "lang_toggle_btn": "🌐 English",  # Click to switch to English
        "status_ready": "সিস্টেম প্রস্তুত  •  কোনো সমস্যা নেই",
        "status_active": "{page} সক্রিয়",
        
        # Breadcrumbs
        "page_dashboard": "প্রজেক্ট ড্যাশবোর্ড",
        "page_upload": "সোর্স প্যাকেজ আপলোড (ধাপ ১/৪)",
        "page_config": "অ্যাপ কনফিগারেশন (ধাপ ২/৪)",
        "page_build": "APK কম্পাইলেশন (ধাপ ৩/৪)",
        "page_result": "রিলিজ প্রস্তুত APK (ধাপ ৪/৪)",
        "page_history": "বিল্ড ইতিহাস ও আর্কাইভ",
        "page_settings": "সিস্টেম সেটিংস ও পরিবেশ",

        # Wizard steps
        "step_1": "সোর্স প্যাকেজ",
        "step_2": "কনফিগারেশন",
        "step_3": "কম্পাইলেশন",
        "step_4": "রিলিজ প্রস্তুত",

        # Dashboard / Welcome
        "dash_badge": "v1.0.0 • প্রডাকশন রেডি অ্যান্ড্রয়েড কম্পাইলার",
        "dash_hero_title": "অ্যান্ড্রয়েড APK তৈরি করুন সহজে",
        "dash_hero_subtitle": "ওয়েব অ্যাপ ও গুগল AI স্টুডিও প্রজেক্ট থেকে নিখুঁত ইনস্টলেবল APK বানান।",
        "dash_hero_desc": "সম্পূর্ণ স্বয়ংক্রিয় বিল্ড ইঞ্জিন যাতে Adoptium OpenJDK 17 এবং Android SDK প্রি-ইন্সটল করা আছে। নেটিভ কোটলিন জেটপ্যাক কম্পোজ বা যেকোনো ওয়েব অ্যাপ সরাসরি রূপান্তর করে।",
        "btn_start_new_build": "⚡ নতুন বিল্ড শুরু করুন",
        "btn_env_settings": "⚙ পরিবেশ ও সেটিংস",
        "features_title": "প্রধান সুবিধাসমূহ",
        "features_subtitle": "উচ্চগতিসম্পন্ন, নির্ভরযোগ্য এবং সম্পূর্ণ স্বয়ংক্রিয় অ্যান্ড্রয়েড বিল্ড ব্যবস্থা।",
        "feat_zero_title": "জিরো কনফিগারেশন",
        "feat_zero_desc": "OpenJDK 17 ও Android SDK প্রি-ইন্সটল করা থাকে। আলাদা কোনো সেটআপের ঝামেলা নেই।",
        "feat_support_title": "ওয়েব ও নেটিভ সাপোর্ট",
        "feat_support_desc": "গুগল AI স্টুডিওর কোটলিন/কম্পোজ প্রজেক্ট এবং HTML5/CSS/JS ওয়েব অ্যাপ উভয়ই নিখুঁত সমর্থন করে।",
        "feat_sign_title": "স্বয়ংক্রিয় সাইনিং",
        "feat_sign_desc": "স্বয়ংক্রিয় কী-স্টোর তৈরি, Android v1/v2 ডিজিটাল সিগনেচার ও ZipAlign অপ্টিমাইজেশন সম্পন্ন করে।",
        "recent_builds_title": "সাম্প্রতিক বিল্ডসমূহ",
        "recent_builds_desc": "আপনার সাম্প্রতিক তৈরি করা অ্যান্ড্রয়েড প্যাকেজসমূহের তালিকা।",
        "no_recent_builds": "এখনো কোনো বিল্ড করা হয়নি। নতুন APK তৈরি করতে 'নতুন বিল্ড' বাটনে ক্লিক করুন।",

        # Upload Page
        "upload_title": "সোর্স প্যাকেজ আপলোড",
        "upload_subtitle": "আপনার প্রজেক্ট ZIP বা ফোল্ডারটি এখানে ড্র্যাগ করে ছেড়ে দিন অথবা ফাইল সিলেক্ট করুন।",
        "dropzone_title": "প্রজেক্টের ZIP ফাইল বা ফোল্ডার এখানে ড্র্যাগ করে ছেড়ে দিন",
        "dropzone_subtitle": "গুগল AI স্টুডিও এক্সপোর্ট (.zip), নেটিভ অ্যান্ড্রয়েড ফোল্ডার বা সাধারণ ওয়েব অ্যাপ (index.html সহ) সমর্থিত",
        "dropzone_selected_zip": "ZIP আর্কাইভ নির্বাচিত হয়েছে",
        "dropzone_selected_folder": "প্রজেক্ট ডিরেক্টরি নির্বাচিত হয়েছে",
        "dropzone_click_to_change": "অন্য ফাইল বা ফোল্ডার ড্র্যাগ করুন অথবা ক্লিক করে পরিবর্তন করুন",
        "btn_browse_folder": "📁  ফোল্ডার নির্বাচন করুন",
        "btn_browse_zip": "📦  ZIP ফাইল নির্বাচন করুন",
        "btn_reset": "🔄  রিসেট",
        "selected_package_info": "নির্বাচিত প্যাকেজের বিবরণ",
        "pkg_type_studio": "গুগল AI স্টুডিও প্রজেক্ট (Kotlin / Compose)",
        "pkg_type_native": "নেটিভ অ্যান্ড্রয়েড প্রজেক্ট (Gradle)",
        "pkg_type_web": "HTML5 ওয়েব অ্যাপ্লিকেশন (index.html)",
        "pkg_status_ready": "✓ বৈধ প্রজেক্ট ফরম্যাট নিশ্চিত হয়েছে এবং বিল্ডের জন্য প্রস্তুত",
        "pkg_status_missing": "⚠ ত্রুটি: রুট ডিরেক্টরিতে index.html অথবা অ্যান্ড্রয়েড বিল্ড ফাইল নেই",
        "btn_back_dash": "← ড্যাশবোর্ড",
        "btn_continue_config": "অ্যাপ কনফিগারেশনে যান →",
        "alert_native_verified": "✅ নেটিভ অ্যান্ড্রয়েড প্রজেক্ট সফলভাবে যাচাই হয়েছে ({name})",
        "alert_web_verified": "✅ বৈধ ওয়েব অ্যাপ্লিকেশন সফলভাবে যাচাই হয়েছে (index.html বিদ্যমান)",
        "alert_invalid": "⚠️ রুটে index.html অথবা অ্যান্ড্রয়েড বিল্ড কনফিগারেশন পাওয়া যায়নি",

        # Config Page
        "config_title": "অ্যাপ্লিকেশন কনফিগারেশন",
        "config_subtitle": "অ্যাপের নাম, প্যাকেজ আইডি, লোগো এবং অন্যান্য সেটিংস কাস্টমাইজ করুন।",
        "app_identity_section": "অ্যাপ পরিচিতি",
        "app_name_label": "অ্যাপ প্রদর্শনী নাম (App Name)",
        "app_name_ph": "যেমন: আমার অ্যাপ",
        "package_name_label": "প্যাকেজ আইডি (Package Name)",
        "package_name_ph": "যেমন: com.company.myapp",
        "version_name_label": "ভার্সন নাম (Version Name)",
        "version_name_ph": "1.0.0",
        "version_code_label": "ভার্সন কোড (Version Code)",
        "version_code_ph": "1",
        "app_icon_section": "অ্যাপ লোগো ও ব্র্যান্ডিং",
        "app_icon_desc": "আপনার অ্যাপের জন্য একটি কাস্টম PNG বা JPEG লোগো নির্বাচন করুন (৫১২x৫১২ সাইজ উপযুক্ত)।",
        "btn_browse_icon": "🖼 লোগো নির্বাচন",
        "btn_reset_icon": "ডিফল্ট লোগো",
        "behavior_section": "ডিসপ্লে ও পারমিশন",
        "orientation_label": "স্ক্রিন ওরিয়েন্টেশন",
        "orientation_portrait": "পোর্ট্রেট (খাড়া)",
        "orientation_landscape": "ল্যান্ডস্কেপ (শোয়ানো)",
        "orientation_auto": "অটো-রোটেট / সেন্সর",
        "chk_fullscreen": "ফুলস্ক্রিন মোড সক্রিয় করুন (অ্যান্ড্রয়েড স্ট্যাটাস বার লুকান)",
        "chk_internet": "ইন্টারনেট পারমিশন প্রদান করুন (অনলাইন ডেটা ও API এর জন্য আবশ্যক)",
        "chk_cleartext": "HTTP ক্লিয়ারটেক্সট ট্রাফিক অনুমোদন করুন (লোকাল বা নন-HTTPS এর জন্য)",
        "status_color_label": "স্ট্যাটাস বার কালার",
        "btn_back_upload": "← আপলোডে ফিরুন",
        "btn_start_compilation": "🚀 APK কম্পাইলেশন শুরু করুন",

        # Build Page
        "build_title": "APK কম্পাইলেশন প্রক্রিয়া",
        "build_subtitle": "লাইভ ইঞ্জিন লগ, ধাপসমূহ যাচাই এবং অ্যান্ড্রয়েড প্যাকেজ প্যাকেজিং।",
        "build_progress_title": "বিল্ড সামগ্রিক অগ্রগতি",
        "build_steps_title": "বিল্ড ধাপসমূহ",
        "step_prep": "প্রজেক্ট কাঠামো ও পরিবেশ প্রস্তুত হচ্ছে...",
        "step_copy": "ওয়েব অ্যাসেট ও ফাইল কপি হচ্ছে...",
        "step_res": "অ্যান্ড্রয়েড রিসোর্স প্রসেস ও অপ্টিমাইজ হচ্ছে...",
        "step_compile": "সোর্স কোড ও রিলিজ ডেক্স কম্পাইল হচ্ছে...",
        "step_sign": "APK প্যাকেজ সাইন ও অ্যালাইন হচ্ছে...",
        "step_done": "বিল্ড সফলভাবে সম্পন্ন হয়েছে!",
        "console_logs_title": "বিল্ড কনসোল লগ (রিয়েল-টাইম)",
        "btn_clear_logs": "মুছুন",
        "btn_cancel_build": "✖ বিল্ড বাতিল করুন",
        "btn_view_result": "ফলাফল দেখুন →",

        # Result Page
        "result_title": "APK সফলভাবে তৈরি হয়েছে!",
        "result_subtitle": "আপনার অ্যান্ড্রয়েড প্যাকেজটি ডিজিটালভাবে সাইন ও অপ্টিমাইজ করা হয়েছে।",
        "apk_details_title": "প্যাকেজ বিবরণ",
        "apk_name": "অ্যাপের নাম:",
        "apk_package": "প্যাকেজ আইডি:",
        "apk_version": "ভার্সন:",
        "apk_size": "ফাইল সাইজ:",
        "apk_location": "সংরক্ষণ অবস্থান:",
        "btn_open_folder": "📂 ফাইল লোকেশন খুলুন",
        "btn_share_apk": "📤 APK শেয়ার করুন",
        "btn_build_another": "⚡ আরেকটি APK তৈরি করুন",
        "install_guide_title": "যেকোনো ফোনে ইনস্টল করার সহজ নিয়ম",
        "install_guide_step1": "১. এই .apk ফাইলটি USB ক্যাবল, হোয়াটসঅ্যাপ বা গুগল ড্রাইভ দিয়ে ফোনে পাঠান।",
        "install_guide_step2": "২. ফোনে ফাইল ম্যানেজারে গিয়ে .apk ফাইলটিতে ট্যাপ করুন।",
        "install_guide_step3": "৩. সতর্কবার্তা দেখালে 'Install Unknown Apps' অপশনে পারমিশন দিন।",
        "install_guide_step4": "৪. 'Install' চাপুন এবং সরাসরি আপনার অ্যাপটি ব্যবহার শুরু করুন!",

        # History Page
        "history_title": "বিল্ড ইতিহাস ও আর্কাইভ",
        "history_subtitle": "পূর্বে তৈরি করা সকল APK ও প্যাকেজের বিবরণ।",
        "history_empty_title": "এখনো কোনো বিল্ড ইতিহাস পাওয়া যায়নি",
        "history_empty_desc": "বাম পাশের মেনু থেকে 'নতুন বিল্ড' নির্বাচন করে আপনার প্রথম APK তৈরি করুন।",
        "btn_locate_file": "📂 ফোল্ডার খুলুন",

        # Settings Page
        "settings_title": "সিস্টেম সেটিংস ও কনফিগারেশন",
        "settings_subtitle": "কম্পাইলার টুলস (Adoptium JDK, Android SDK), আউটপুট পাথ ও সাইনিং সেটিংস।",
        "tools_section": "টুলস ও ডিপেন্ডেন্সি",
        "tools_desc": "Java Development Kit (JDK 17+) এবং Android SDK বিল্ট-ইন ভাবে কনফিগার করা আছে।",
        "jdk_path_label": "Java JDK ডিরেক্টরি",
        "sdk_path_label": "Android SDK ডিরেক্টরি",
        "output_dir_label": "APK আউটপুট ডিরেক্টরি",
        "btn_browse": "ব্রাউজ",
        "btn_auto_setup": "⚡ অটো ডিটেক্ট টুলস",
        "btn_save_settings": "💾 সেটিংস সংরক্ষণ করুন",
        "btn_reset_settings": "🔄 ডিফল্ট রিসেট",
        "appearance_section": "অ্যাপের থিম ও প্রদর্শন",
        "appearance_desc": "আপনার পছন্দের লুক নির্বাচন করুন। ডিফল্ট হিসেবে Obsidian Glass ডার্ক থিম সক্রিয়।",
        "theme_dark_option": "ডার্ক (Obsidian Glass)",
        "theme_light_option": "লাইট (Graphite Frost)",
        "saved_msg": "সেটিংস সফলভাবে সংরক্ষিত হয়েছে!",
    }
}

