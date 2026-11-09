"""APK Compiler - File Utilities Module.

Provides robust file and directory manipulation, ZIP extraction,
web app validation, filename sanitization, and size formatting.
"""

import os
import re
import shutil
import tempfile
import zipfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Union

from src.utils.config import TEMP_DIR


def extract_zip(zip_path: str, dest_dir: str) -> bool:
    """Extract a ZIP archive safely with Zip Slip directory traversal protection.

    Args:
        zip_path: Path to the .zip archive.
        dest_dir: Destination directory where files should be extracted.

    Returns:
        True if extraction succeeded, raises exception or False otherwise.
    """
    if not os.path.isfile(zip_path):
        raise FileNotFoundError(f"Archive not found: {zip_path}")

    os.makedirs(dest_dir, exist_ok=True)
    resolved_dest = os.path.abspath(dest_dir)

    with zipfile.ZipFile(zip_path, "r") as archive:
        for member in archive.infolist():
            # Resolve target path and verify it stays inside destination
            target_path = os.path.abspath(os.path.join(resolved_dest, member.filename))
            if not target_path.startswith(resolved_dest + os.sep) and target_path != resolved_dest:
                raise ValueError(f"Security error: Archive member attempts directory traversal: {member.filename}")

            archive.extract(member, resolved_dest)
    return True


def copy_directory(src: str, dest: str, overwrite: bool = True) -> bool:
    """Copy an entire directory tree from src to dest.

    Args:
        src: Source directory path.
        dest: Destination directory path.
        overwrite: If True, overwrite files in destination.

    Returns:
        True if copy succeeded.
    """
    if not os.path.isdir(src):
        raise NotADirectoryError(f"Source directory does not exist: {src}")

    os.makedirs(dest, exist_ok=True)

    for root, dirs, files in os.walk(src):
        rel_path = os.path.relpath(root, src)
        dest_sub = os.path.join(dest, rel_path) if rel_path != "." else dest
        os.makedirs(dest_sub, exist_ok=True)

        for file_name in files:
            src_file = os.path.join(root, file_name)
            dest_file = os.path.join(dest_sub, file_name)
            if overwrite or not os.path.exists(dest_file):
                shutil.copy2(src_file, dest_file)
    return True


def get_directory_size(path: str) -> int:
    """Calculate total size in bytes of all files inside path."""
    total_size = 0
    if not os.path.exists(path):
        return 0

    if os.path.isfile(path):
        return os.path.getsize(path)

    for root, _, files in os.walk(path):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            try:
                if not os.path.islink(file_path):
                    total_size += os.path.getsize(file_path)
            except OSError:
                continue
    return total_size


def format_file_size(size_bytes: Union[int, float]) -> str:
    """Format byte count into human-readable string (B, KB, MB, GB)."""
    if size_bytes < 0:
        return "0 B"
    units = ["B", "KB", "MB", "GB", "TB"]
    size = float(size_bytes)
    unit_idx = 0
    while size >= 1024.0 and unit_idx < len(units) - 1:
        size /= 1024.0
        unit_idx += 1
    if unit_idx == 0:
        return f"{int(size)} {units[unit_idx]}"
    return f"{size:.2f} {units[unit_idx]}"


def find_files(directory: str, extensions: List[str]) -> List[str]:
    """Find all files in directory matching given extensions.

    Args:
        directory: Path to search in.
        extensions: List of extensions (e.g. ['.html', '.htm', 'css']).

    Returns:
        List of absolute file paths matching extensions.
    """
    matched: List[str] = []
    if not os.path.isdir(directory):
        return matched

    normalized_exts: Set[str] = {
        ext.lower() if ext.startswith(".") else f".{ext.lower()}"
        for ext in extensions
    }

    for root, _, files in os.walk(directory):
        for file_name in files:
            ext = os.path.splitext(file_name)[1].lower()
            if ext in normalized_exts:
                matched.append(os.path.join(root, file_name))
    return matched


def _detect_native_android_project(directory: str) -> Optional[Dict[str, Any]]:
    """Check if the directory is a native Android project (e.g. from Google AI Studio).
    
    Returns extracted metadata dict if native project, otherwise None.
    """
    # Look for key Android project markers
    markers = [
        "app/build.gradle.kts",
        "app/build.gradle",
        "build.gradle.kts",
        "build.gradle",
        "settings.gradle.kts",
        "settings.gradle",
        "app/src/main/AndroidManifest.xml",
    ]
    
    found_marker = False
    for m in markers:
        if os.path.exists(os.path.join(directory, *m.split("/"))):
            found_marker = True
            break
            
    if not found_marker:
        return None
        
    info = {
        "is_native_android": True,
        "app_name": "My App",
        "package_name": "com.app.myapp",
        "version_name": "1.0",
        "version_code": 1,
        "kt_files": [],
        "java_files": [],
        "xml_files": [],
    }
    
    # 1. Try reading metadata.json (common in Google AI Studio)
    meta_path = os.path.join(directory, "metadata.json")
    if os.path.isfile(meta_path):
        try:
            import json
            with open(meta_path, "r", encoding="utf-8") as f:
                meta = json.load(f)
                if meta.get("name"):
                    info["app_name"] = meta["name"]
        except Exception:
            pass
            
    # 2. Try parsing app/build.gradle.kts or app/build.gradle
    import re
    app_gradle_candidates = [
        os.path.join(directory, "app", "build.gradle.kts"),
        os.path.join(directory, "app", "build.gradle"),
    ]
    for agc in app_gradle_candidates:
        if os.path.isfile(agc):
            try:
                with open(agc, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                    # Match applicationId = "com.xyz" or applicationId "com.xyz"
                    app_id = re.search(r'applicationId\s*=?\s*["\']([^"\']+)["\']', content)
                    if app_id:
                        info["package_name"] = app_id.group(1)
                    v_code = re.search(r'versionCode\s*=?\s*(\d+)', content)
                    if v_code:
                        info["version_code"] = int(v_code.group(1))
                    v_name = re.search(r'versionName\s*=?\s*["\']([^"\']+)["\']', content)
                    if v_name:
                        info["version_name"] = v_name.group(1)
            except Exception:
                pass
                
    # 3. Fallback to settings.gradle.kts rootProject.name
    if info["app_name"] == "My App":
        settings_candidates = [
            os.path.join(directory, "settings.gradle.kts"),
            os.path.join(directory, "settings.gradle"),
        ]
        for sc in settings_candidates:
            if os.path.isfile(sc):
                try:
                    with open(sc, "r", encoding="utf-8", errors="ignore") as f:
                        s_content = f.read()
                        r_name = re.search(r'rootProject\.name\s*=\s*["\']([^"\']+)["\']', s_content)
                        if r_name and r_name.group(1) != "My Application":
                            info["app_name"] = r_name.group(1)
                except Exception:
                    pass
                    
    # Scan source files
    for root, _, files in os.walk(directory):
        for f in files:
            rel = os.path.relpath(os.path.join(root, f), directory)
            if f.endswith(".kt"):
                info["kt_files"].append(rel)
            elif f.endswith(".java"):
                info["java_files"].append(rel)
            elif f.endswith(".xml"):
                info["xml_files"].append(rel)
                
    return info


def validate_web_app(directory: str) -> Dict[str, Any]:
    """Inspect and validate web application folder structure.

    Checks for index.html at root or immediate subdirectories,
    counts HTML, CSS, JavaScript, and image assets.

    Args:
        directory: Root path of the web application.

    Returns:
        Dictionary with validation results:
        {
            "valid": bool,
            "has_index": bool,
            "index_path": Optional[str],
            "html_files": List[str],
            "css_files": List[str],
            "js_files": List[str],
            "image_files": List[str],
            "total_files": int,
            "total_size": int,
            "formatted_size": str,
            "issues": List[str]
        }
    """
    result: Dict[str, Any] = {
        "valid": False,
        "has_index": False,
        "index_path": None,
        "html_files": [],
        "css_files": [],
        "js_files": [],
        "image_files": [],
        "total_files": 0,
        "total_size": 0,
        "formatted_size": "0 B",
        "issues": [],
    }

    if not os.path.isdir(directory):
        result["issues"].append(f"Directory does not exist: {directory}")
        return result

    # Check if this is a Native Android project (e.g. Google AI Studio)
    native_info = _detect_native_android_project(directory)
    if native_info:
        total_size = get_directory_size(directory)
        total_files = len(native_info["kt_files"]) + len(native_info["java_files"]) + len(native_info["xml_files"])
        return {
            "valid": True,
            "is_native_android": True,
            "has_index": True,  # Native projects don't require index.html
            "index_path": None,
            "html_files": [],
            "css_files": [],
            "js_files": [],
            "image_files": [],
            "total_files": total_files,
            "total_size": total_size,
            "formatted_size": format_file_size(total_size),
            "issues": [],
            "app_name": native_info["app_name"],
            "package_name": native_info["package_name"],
            "version_name": native_info["version_name"],
            "version_code": native_info["version_code"],
            "kt_files": native_info["kt_files"],
            "java_files": native_info["java_files"],
            "xml_files": native_info["xml_files"],
        }

    html_exts = {".html", ".htm"}
    css_exts = {".css"}
    js_exts = {".js", ".mjs"}
    image_exts = {".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".ico"}

    total_size = 0
    total_files = 0

    root_index = os.path.join(directory, "index.html")
    root_htm = os.path.join(directory, "index.htm")

    if os.path.isfile(root_index):
        result["has_index"] = True
        result["index_path"] = root_index
    elif os.path.isfile(root_htm):
        result["has_index"] = True
        result["index_path"] = root_htm

    for root, _, files in os.walk(directory):
        for file_name in files:
            abs_path = os.path.join(root, file_name)
            rel_path = os.path.relpath(abs_path, directory).replace("\\", "/")
            total_files += 1
            try:
                total_size += os.path.getsize(abs_path)
            except OSError:
                pass

            ext = os.path.splitext(file_name)[1].lower()
            if ext in html_exts:
                result["html_files"].append(rel_path)
                # If root index was not found, check nested index.html
                if not result["has_index"] and file_name.lower() in ("index.html", "index.htm"):
                    result["has_index"] = True
                    result["index_path"] = abs_path
            elif ext in css_exts:
                result["css_files"].append(rel_path)
            elif ext in js_exts:
                result["js_files"].append(rel_path)
            elif ext in image_exts:
                result["image_files"].append(rel_path)

    result["total_files"] = total_files
    result["total_size"] = total_size
    result["formatted_size"] = format_file_size(total_size)

    if not result["has_index"]:
        result["issues"].append("Missing required 'index.html' entry point.")
    if total_files == 0:
        result["issues"].append("Web app directory is completely empty.")

    result["valid"] = result["has_index"] and (total_files > 0)
    return result


def clean_directory(path: str) -> None:
    """Completely remove and recreate a directory."""
    if os.path.exists(path):
        try:
            shutil.rmtree(path)
        except OSError:
            # Fallback for Windows file locks or read-only files
            for root, dirs, files in os.walk(path, topdown=False):
                for f in files:
                    fp = os.path.join(root, f)
                    try:
                        os.chmod(fp, 0o777)
                        os.remove(fp)
                    except OSError:
                        pass
                for d in dirs:
                    dp = os.path.join(root, d)
                    try:
                        os.rmdir(dp)
                    except OSError:
                        pass
            try:
                shutil.rmtree(path, ignore_errors=True)
            except OSError:
                pass
    os.makedirs(path, exist_ok=True)


def safe_filename(name: str, replacement: str = "_") -> str:
    """Sanitize a filename by removing illegal characters on Windows, macOS, and Linux.

    Args:
        name: Proposed file name.
        replacement: Character used to replace invalid characters.

    Returns:
        Sanitized safe filename string.
    """
    if not name:
        return "unnamed"

    # Replace forbidden Windows / Unix characters: < > : " / \ | ? *
    sanitized = re.sub(r'[<>:"/\\|?*\x00-\x1f]', replacement, name)
    # Remove leading/trailing periods and spaces
    sanitized = sanitized.strip(". ")
    # Replace multiple replacements with single one
    sanitized = re.sub(f"\\{replacement}+", replacement, sanitized)

    if not sanitized:
        sanitized = "unnamed"
    return sanitized


def create_temp_dir(prefix: str = "apk_build_") -> str:
    """Create a temporary build directory inside TEMP_DIR or system temp.

    Args:
        prefix: Prefix for directory name.

    Returns:
        Absolute path to newly created temporary directory.
    """
    base_dir = TEMP_DIR if os.path.isdir(TEMP_DIR) else tempfile.gettempdir()
    os.makedirs(base_dir, exist_ok=True)
    temp_dir = tempfile.mkdtemp(prefix=prefix, dir=base_dir)
    return os.path.abspath(temp_dir)
