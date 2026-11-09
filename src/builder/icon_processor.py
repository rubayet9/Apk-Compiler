"""APK Compiler - App Icon Processor Module.

Generates Android launcher icons in square and circular formats across all
standard Android display densities (mdpi, hdpi, xhdpi, xxhdpi, xxxhdpi).
"""

import os
import sys
from typing import Dict, Optional, Tuple

try:
    from PIL import Image, ImageDraw, ImageFont
    # Pillow 9.0+ uses Image.Resampling.LANCZOS; older versions use Image.LANCZOS
    RESAMPLE_LANCZOS = getattr(Image, "Resampling", Image).LANCZOS
except ImportError:
    Image = None  # type: ignore
    ImageDraw = None  # type: ignore
    ImageFont = None  # type: ignore
    RESAMPLE_LANCZOS = None


class IconProcessor:
    """Processes, resizes, and generates Android application launcher icons."""

    DENSITIES: Dict[str, int] = {
        "mipmap-mdpi": 48,
        "mipmap-hdpi": 72,
        "mipmap-xhdpi": 96,
        "mipmap-xxhdpi": 144,
        "mipmap-xxxhdpi": 192,
    }

    def __init__(self):
        if Image is None:
            raise ImportError(
                "Pillow (PIL) is required for IconProcessor. "
                "Install it with: pip install pillow"
            )

    def process_icon(self, icon_path: str, output_res_dir: str) -> None:
        """Resize source icon image to all standard Android mipmap densities.

        Saves ic_launcher.png into each mipmap-* directory.

        Args:
            icon_path: Path to square source icon (preferably >= 512x512).
            output_res_dir: Path to Android 'res' directory.
        """
        if not os.path.isfile(icon_path):
            raise FileNotFoundError(f"Icon source file not found: {icon_path}")

        os.makedirs(output_res_dir, exist_ok=True)

        with Image.open(icon_path) as src_img:
            rgba_img = src_img.convert("RGBA")

            for density, size in self.DENSITIES.items():
                dest_dir = os.path.join(output_res_dir, density)
                os.makedirs(dest_dir, exist_ok=True)

                resized = rgba_img.resize((size, size), resample=RESAMPLE_LANCZOS)
                out_path = os.path.join(dest_dir, "ic_launcher.png")
                resized.save(out_path, format="PNG", optimize=True)

    def create_round_icon(self, icon_path: str, output_res_dir: str) -> None:
        """Generate circular launcher icons for all Android densities.

        Saves ic_launcher_round.png into each mipmap-* directory.

        Args:
            icon_path: Path to source icon.
            output_res_dir: Path to Android 'res' directory.
        """
        if not os.path.isfile(icon_path):
            raise FileNotFoundError(f"Icon source file not found: {icon_path}")

        os.makedirs(output_res_dir, exist_ok=True)

        with Image.open(icon_path) as src_img:
            rgba_img = src_img.convert("RGBA")

            for density, size in self.DENSITIES.items():
                dest_dir = os.path.join(output_res_dir, density)
                os.makedirs(dest_dir, exist_ok=True)

                resized = rgba_img.resize((size, size), resample=RESAMPLE_LANCZOS)

                # Create antialiased circular mask
                mask_scale = 4  # 4x supersampling for ultra smooth circle
                mask_size = size * mask_scale
                mask = Image.new("L", (mask_size, mask_size), 0)
                draw = ImageDraw.Draw(mask)
                draw.ellipse((0, 0, mask_size - 1, mask_size - 1), fill=255)
                mask = mask.resize((size, size), resample=RESAMPLE_LANCZOS)

                # Apply mask to alpha channel
                r, g, b, a = resized.split()
                # Multiply existing alpha by mask
                final_a = Image.new("L", (size, size))
                for y in range(size):
                    for x in range(size):
                        orig_val = a.getpixel((x, y))
                        mask_val = mask.getpixel((x, y))
                        final_a.putpixel((x, y), int((orig_val * mask_val) / 255))

                round_img = Image.merge("RGBA", (r, g, b, final_a))
                out_path = os.path.join(dest_dir, "ic_launcher_round.png")
                round_img.save(out_path, format="PNG", optimize=True)

    def _get_font(self, size: int) -> ImageFont.ImageFont:
        """Load a suitable truetype font or fallback to default."""
        font_candidates = [
            "arialbd.ttf",  # Arial Bold
            "arial.ttf",
            "segoeuib.ttf",  # Segoe UI Bold
            "segoeui.ttf",
            "Roboto-Bold.ttf",
            "Roboto-Regular.ttf",
        ]
        for font_name in font_candidates:
            try:
                return ImageFont.truetype(font_name, size)
            except (IOError, OSError):
                continue
        try:
            return ImageFont.load_default()
        except Exception:
            return None  # type: ignore

    def create_default_icon(self, output_res_dir: str, app_name: str) -> None:
        """Generate a clean, modern default icon featuring the app's first letter.

        Generates both standard and round launcher icons across all densities.

        Args:
            output_res_dir: Path to Android 'res' directory.
            app_name: Name of the application.
        """
        os.makedirs(output_res_dir, exist_ok=True)

        char = app_name.strip()[0].upper() if (app_name and app_name.strip()) else "A"
        master_size = 512

        # Create master icon image (512x512)
        img = Image.new("RGBA", (master_size, master_size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Draw rounded rectangle background with modern vibrant gradient / solid color
        bg_color = (67, 97, 238, 255)  # Modern vibrant indigo (#4361EE)
        corner_radius = 96
        draw.rounded_rectangle(
            (0, 0, master_size - 1, master_size - 1),
            radius=corner_radius,
            fill=bg_color,
        )

        # Draw letter centered
        font_size = 280
        font = self._get_font(font_size)
        text_color = (255, 255, 255, 255)

        # Calculate text bounding box to center it
        bbox = draw.textbbox((0, 0), char, font=font) if font else (0, 0, 200, 200)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (master_size - text_width) // 2 - bbox[0]
        y = (master_size - text_height) // 2 - bbox[1]

        draw.text((x, y), char, fill=text_color, font=font)

        # Save to temp master file and process all mipmaps
        temp_master_path = os.path.join(output_res_dir, "_temp_master_icon.png")
        try:
            img.save(temp_master_path, format="PNG")
            self.process_icon(temp_master_path, output_res_dir)
            self.create_round_icon(temp_master_path, output_res_dir)
        finally:
            if os.path.isfile(temp_master_path):
                try:
                    os.remove(temp_master_path)
                except OSError:
                    pass
