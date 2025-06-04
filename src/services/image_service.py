"""
Image generation service for birthday cards.
"""

import os
import random
import math
import datetime
from pathlib import Path
from typing import Optional, Dict, Tuple
from io import BytesIO
import logging

from PIL import Image, ImageDraw, ImageFont


class ImageService:
    """Service for generating birthday images."""
    
    def __init__(
        self,
        base_image_path: Optional[str] = None,
        output_dir: str = "output_img",
        width: int = 800,
        height: int = 624,
        background_color: str = "#e40000"
    ):
        """
        Initialize image service.
        
        Args:
            base_image_path: Path to custom base image template
            output_dir: Directory to save generated images
            width: Image width in pixels
            height: Image height in pixels
            background_color: Background color hex code
        """
        self.base_image_path = Path(base_image_path) if base_image_path else None
        self.output_dir = Path(output_dir)
        self.width = width
        self.height = height
        self.background_color = background_color
        self.logger = logging.getLogger(__name__)
        
        # Create output directory
        self.output_dir.mkdir(exist_ok=True)
        
        # Cache for base image and fonts
        self._base_image: Optional[Image.Image] = None
        self._fonts: Dict[str, ImageFont.FreeTypeFont] = {}
        self._fonts_loaded = False
        
        # Asset paths
        self.logo_path = Path("assets/airtel_logo.png")
        self.cake_path = Path("assets/cake.png")
    
    def _load_fonts(self) -> None:
        """Load fonts with fallbacks."""
        if self._fonts_loaded:
            return
        
        font_configs = [
            ('header', 'arialbd.ttf', 36),
            ('main', 'arialbd.ttf', 80),
            ('sub', 'arialbd.ttf', 28),
            ('name', 'arialbd.ttf', 32),
            ('small', 'arial.ttf', 24),
        ]
        
        for font_key, font_file, size in font_configs:
            try:
                self._fonts[font_key] = ImageFont.truetype(font_file, size)
            except (OSError, IOError):
                self.logger.warning(f"Could not load font {font_file}, using default")
                self._fonts[font_key] = ImageFont.load_default()
        
        self._fonts_loaded = True
        self.logger.info("Fonts loaded successfully")
    
    def _create_base_image(self) -> Image.Image:
        """Create or load the base birthday image template."""
        if self._base_image is not None:
            return self._base_image
        
        self._load_fonts()
        
        # Try to load custom base image
        if self.base_image_path and self.base_image_path.exists():
            try:
                self._base_image = Image.open(self.base_image_path).convert('RGB')
                self.logger.info(f"Using custom base image: {self.base_image_path}")
                return self._base_image
            except Exception as e:
                self.logger.warning(f"Error loading custom base image: {e}")
                self.logger.info("Falling back to generated base image")
        
        # Generate base image
        self._base_image = self._generate_base_image()
        self.logger.info("Generated base birthday image template")
        return self._base_image
    
    def _generate_base_image(self) -> Image.Image:
        """Generate the default base image with company branding."""
        # Create base image
        img = Image.new('RGB', (self.width, self.height), color=self.background_color)
        draw = ImageDraw.Draw(img)
        
        # Add company logo
        self._add_logo(img)
        
        # Add static text elements
        self._add_static_text(draw)
        
        # Add cake image
        cake_y = self._add_cake_image(img)
        
        # Add birthday message
        self._add_birthday_message(draw, cake_y + 220)
        
        # Add confetti effect
        self._add_confetti_effect(img)
        
        return img
    
    def _add_logo(self, img: Image.Image) -> None:
        """Add company logo to the image."""
        try:
            if self.logo_path.exists():
                logo = Image.open(self.logo_path).convert("RGBA")
                logo.thumbnail((150, 150), Image.Resampling.LANCZOS)
                
                # Position logo at top-right
                logo_x = self.width - logo.width - 20
                logo_y = 20
                img.paste(logo, (logo_x, logo_y), mask=logo)
            else:
                self.logger.warning(f"Logo file not found: {self.logo_path}")
        except Exception as e:
            self.logger.warning(f"Could not load company logo: {e}")
    
    def _add_static_text(self, draw: ImageDraw.Draw) -> None:
        """Add static text elements to the image."""
        # Header text
        header_text = "Wishing you a very"
        header_bbox = draw.textbbox((0, 0), header_text, font=self._fonts['header'])
        header_w = header_bbox[2] - header_bbox[0]
        draw.text(
            ((self.width - header_w) // 2, 120),
            header_text,
            fill="white",
            font=self._fonts['header']
        )
        
        # Main birthday text
        main_text = "Happy Birthday!"
        main_bbox = draw.textbbox((0, 0), main_text, font=self._fonts['main'])
        main_w = main_bbox[2] - main_bbox[0]
        draw.text(
            ((self.width - main_w) // 2, 180),
            main_text,
            fill="white",
            font=self._fonts['main']
        )
    
    def _add_cake_image(self, img: Image.Image) -> int:
        """Add cake image and return its bottom Y coordinate."""
        try:
            if self.cake_path.exists():
                cake = Image.open(self.cake_path).convert("RGBA")
                cake.thumbnail((200, 200), Image.Resampling.LANCZOS)
                
                cake_x = (self.width - cake.width) // 2
                cake_y = 300
                img.paste(cake, (cake_x, cake_y), mask=cake)
                return cake_y + cake.height
            else:
                self.logger.warning(f"Cake image not found: {self.cake_path}")
                return 400
        except Exception as e:
            self.logger.warning(f"Could not load cake image: {e}")
            return 400
    
    def _add_birthday_message(self, draw: ImageDraw.Draw, start_y: int) -> None:
        """Add birthday message text."""
        message_lines = [
            "May your birthday be full of happy hours",
            "and special moments to remember for a",
            "long long time!"
        ]
        
        y = start_y
        for line in message_lines:
            line_bbox = draw.textbbox((0, 0), line, font=self._fonts['sub'])
            line_w = line_bbox[2] - line_bbox[0]
            draw.text(
                ((self.width - line_w) // 2, y),
                line,
                fill="white",
                font=self._fonts['sub']
            )
            y += 35
    
    def _add_confetti_effect(self, img: Image.Image) -> None:
        """Add confetti effect to the image."""
        confetti_colors = ['#ffffff', '#ffd700', '#00ffcc', '#ff69b4', '#add8e6']
        confetti_img = Image.new('RGBA', img.size, (255, 0, 0, 0))
        confetti_draw = ImageDraw.Draw(confetti_img)
        
        # Generate confetti particles
        for _ in range(100):
            x = random.randint(0, self.width)
            y = random.randint(self.height - 150, self.height)
            r = random.randint(2, 4)
            color = random.choice(confetti_colors)
            
            # Calculate alpha based on position
            alpha = int(255 * (y - (self.height - 150)) / 150)
            confetti_color = tuple(int(color[i:i+2], 16) for i in (1, 3, 5)) + (alpha,)
            
            confetti_draw.ellipse((x - r, y - r, x + r, y + r), fill=confetti_color)
        
        # Composite confetti onto main image
        img_rgba = img.convert('RGBA')
        img_with_confetti = Image.alpha_composite(img_rgba, confetti_img)
        img.paste(img_with_confetti.convert('RGB'))
    
    def _add_name_to_image(self, base_img: Image.Image, name: str) -> Image.Image:
        """Add personalized name to the base image."""
        # Create a copy to modify
        img = base_img.copy()
        draw = ImageDraw.Draw(img)
        
        # Add personalized greeting
        dear_text = f"Dear {name},"
        dear_bbox = draw.textbbox((0, 0), dear_text, font=self._fonts['name'])
        dear_w = dear_bbox[2] - dear_bbox[0]
        
        # Position the name text
        name_y_position = 50
        if self.base_image_path:
            # For custom images, adjust position as needed
            name_y_position = 50
        
        draw.text(
            ((self.width - dear_w) // 2, name_y_position),
            dear_text,
            fill="white",
            font=self._fonts['name']
        )
        
        return img
    
    def create_birthday_image(self, first_name: str) -> Optional[bytes]:
        """
        Create a personalized birthday image.
        
        Args:
            first_name: Employee's first name
            
        Returns:
            Image data as bytes or None if error
        """
        try:
            # Get base image
            base_img = self._create_base_image()
            
            # Add name to create personalized version
            personalized_img = self._add_name_to_image(base_img, first_name)
            
            # Convert to bytes
            img_byte_arr = BytesIO()
            personalized_img.save(img_byte_arr, format='PNG', optimize=True)
            
            self.logger.debug(f"Created birthday image for {first_name}")
            return img_byte_arr.getvalue()
            
        except Exception as e:
            self.logger.error(f"Error creating birthday image for {first_name}: {e}")
            return None
    
    def save_birthday_image(
        self,
        image_data: bytes,
        empid: str,
        full_name: str,
        custom_filename: Optional[str] = None
    ) -> Optional[str]:
        """
        Save birthday image to disk.
        
        Args:
            image_data: Image data as bytes
            empid: Employee ID
            full_name: Employee's full name
            custom_filename: Custom filename (optional)
            
        Returns:
            Path to saved image or None if error
        """
        try:
            if custom_filename:
                filename = custom_filename
            else:
                # Generate filename
                safe_name = full_name.replace(' ', '_').replace('/', '_')
                date_str = datetime.date.today().strftime('%Y%m%d')
                filename = f"birthday_{empid}_{safe_name}_{date_str}.png"
            
            file_path = self.output_dir / filename
            
            # Save image
            with open(file_path, 'wb') as f:
                f.write(image_data)
            
            self.logger.info(f"Saved birthday image: {file_path}")
            return str(file_path)
            
        except Exception as e:
            self.logger.error(f"Error saving birthday image for {full_name}: {e}")
            return None
    
    def create_and_save_birthday_image(
        self,
        first_name: str,
        empid: str,
        full_name: str,
        save_to_disk: bool = True
    ) -> Tuple[Optional[bytes], Optional[str]]:
        """
        Create and optionally save birthday image.
        
        Args:
            first_name: Employee's first name
            empid: Employee ID
            full_name: Employee's full name
            save_to_disk: Whether to save image to disk
            
        Returns:
            Tuple of (image_data, file_path)
        """
        # Create image
        image_data = self.create_birthday_image(first_name)
        if image_data is None:
            return None, None
        
        # Save if requested
        file_path = None
        if save_to_disk:
            file_path = self.save_birthday_image(image_data, empid, full_name)
        
        return image_data, file_path
    
    def get_base_image_info(self) -> Dict[str, any]:
        """Get information about the base image."""
        base_img = self._create_base_image()
        return {
            'width': base_img.width,
            'height': base_img.height,
            'mode': base_img.mode,
            'format': base_img.format,
            'is_custom': self.base_image_path is not None and self.base_image_path.exists(),
            'custom_path': str(self.base_image_path) if self.base_image_path else None,
        }
    
    def clear_cache(self) -> None:
        """Clear cached base image and fonts."""
        self._base_image = None
        self._fonts.clear()
        self._fonts_loaded = False
        self.logger.info("Image service cache cleared")
    
    def validate_assets(self) -> Dict[str, bool]:
        """Validate that required assets exist."""
        assets = {
            'logo': self.logo_path.exists(),
            'cake': self.cake_path.exists(),
            'custom_base': self.base_image_path.exists() if self.base_image_path else True,
        }
        
        # Check fonts
        font_files = ['arialbd.ttf', 'arial.ttf']
        for font_file in font_files:
            try:
                ImageFont.truetype(font_file, 12)
                assets[f'font_{font_file}'] = True
            except (OSError, IOError):
                assets[f'font_{font_file}'] = False
        
        return assets


class CardGeneratorLegacy:
    """Legacy card generator for backwards compatibility."""
    
    def __init__(
        self,
        width=600,
        height=800,
        output_dir="gen_img",
        cake_path="assets/cake.png",
        logo_path="assets/airtel_logo.png"
    ):
        """Initialize legacy card generator."""
        self.image_service = ImageService(
            base_image_path=None,
            output_dir=output_dir,
            width=width,
            height=height
        )
        self.image_service.cake_path = Path(cake_path)
        self.image_service.logo_path = Path(logo_path)
    
    def generate(self, first_name: str, output_name: str = "birthday_card.png") -> str:
        """Generate birthday card (legacy interface)."""
        image_data = self.image_service.create_birthday_image(first_name)
        if image_data is None:
            raise RuntimeError(f"Failed to generate birthday card for {first_name}")
        
        # Save with custom filename
        file_path = self.image_service.save_birthday_image(
            image_data, "legacy", first_name, output_name
        )
        
        if file_path is None:
            raise RuntimeError(f"Failed to save birthday card for {first_name}")
        
        return file_path


# Example usage and testing
if __name__ == "__main__":
    import sys
    
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    # Test the service
    service = ImageService()
    
    # Validate assets
    asset_status = service.validate_assets()
    print("Asset validation:", asset_status)
    
    # Create test image
    test_names = ["Alice", "Bob", "José", "Jean-Pierre"]
    
    for name in test_names:
        print(f"Creating birthday image for {name}...")
        image_data, file_path = service.create_and_save_birthday_image(
            first_name=name,
            empid=f"TEST{hash(name) % 1000:03d}",
            full_name=f"{name} Test",
            save_to_disk=True
        )
        
        if image_data:
            print(f"  ✓ Created image ({len(image_data)} bytes)")
            if file_path:
                print(f"  ✓ Saved to: {file_path}")
        else:
            print(f"  ✗ Failed to create image")
    
    # Test legacy interface
    print("\nTesting legacy interface...")
    legacy_gen = CardGeneratorLegacy()
    try:
        legacy_path = legacy_gen.generate("Legacy Test")
        print(f"✓ Legacy card saved to: {legacy_path}")
    except Exception as e:
        print(f"✗ Legacy generation failed: {e}")
    
    print("Image service testing completed!")