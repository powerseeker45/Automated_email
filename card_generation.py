import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import datetime
import os
import io
import logging
from typing import Optional, List, Dict, Tuple
from dotenv import load_dotenv

class BirthdayAnniversaryGenerator:
    def __init__(self, output_folder: str = "output"):
        """
        Initialize birthday and anniversary card generator
        
        Args:
            output_folder: Folder to save generated images and logs
        """
        self.output_folder = output_folder
        
        # Create output folder if it doesn't exist
        os.makedirs(output_folder, exist_ok=True)
        
        # Setup logging
        self.setup_logging()
        
        # Track statistics
        self.stats = {
            'birthday_cards_created': 0,
            'anniversary_cards_created': 0,
            'errors': [],
            'birthdays_today': [],
            'anniversaries_today': [],
            'start_time': datetime.datetime.now(),
            'end_time': None
        }
        
    def setup_logging(self):
        """Setup logging configuration"""
        log_filename = os.path.join(self.output_folder, "card_generator.log")
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Setup file handler
        file_handler = logging.FileHandler(log_filename, mode='a', encoding='utf-8')
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.INFO)
        
        # Setup console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(logging.INFO)
        
        # Setup logger
        self.logger = logging.getLogger('CardGenerator')
        self.logger.setLevel(logging.INFO)
        
        # Clear existing handlers to avoid duplicates
        self.logger.handlers.clear()
        
        # Add handlers
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
    def log_error(self, error_msg: str, exception: Optional[Exception] = None):
        """Log error and add to stats"""
        if exception:
            import traceback
            full_error = f"{error_msg}: {str(exception)}\n{traceback.format_exc()}"
        else:
            full_error = error_msg
            
        self.logger.error(full_error)
        self.stats['errors'].append({
            'timestamp': datetime.datetime.now().isoformat(),
            'message': error_msg,
            'exception': str(exception) if exception else None
        })
    
    def hex_to_rgb(self, hex_color: str) -> tuple:
        """
        Convert hex color to RGB tuple
        
        Args:
            hex_color: Hex color string (e.g., '#FF0000' or 'FF0000')
            
        Returns:
            tuple: (R, G, B) values
        """
        try:
            # Remove # if present
            hex_color = hex_color.lstrip('#')
            
            # Ensure we have a 6-character hex code
            if len(hex_color) == 3:
                # Convert short form (e.g., 'F0A') to long form ('FF00AA')
                hex_color = ''.join([c*2 for c in hex_color])
            elif len(hex_color) != 6:
                raise ValueError(f"Invalid hex color length: {hex_color}")
            
            # Convert to RGB
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            
            return (r, g, b)
            
        except Exception as e:
            self.logger.warning(f"Invalid hex color '{hex_color}', using black as default: {e}")
            return (0, 0, 0)  # Default to black
        
    def load_employee_data(self, csv_file: str) -> pd.DataFrame:
        """
        Load employee data from CSV file with error handling
        """
        try:
            if not os.path.exists(csv_file):
                raise FileNotFoundError(f"CSV file not found: {csv_file}")
                
            df = pd.read_csv(csv_file)
            self.logger.info(f"Loaded {len(df)} employee records from {csv_file}")
            
            # Validate required columns
            required_columns = ['first_name', 'last_name', 'email', 'birthday']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                raise ValueError(f"Missing required columns: {missing_columns}")
            
            # Convert date columns to datetime with error handling
            try:
                df['birthday'] = pd.to_datetime(df['birthday'], errors='coerce')
                invalid_birthdays = df[df['birthday'].isna()]['email'].tolist()
                if invalid_birthdays:
                    self.logger.warning(f"Invalid birthday dates for employees: {invalid_birthdays}")
            except Exception as e:
                self.log_error("Error parsing birthday dates", e)
                
            if 'anniversary' in df.columns:
                try:
                    df['anniversary'] = pd.to_datetime(df['anniversary'], errors='coerce')
                    invalid_anniversaries = df[df['anniversary'].isna() & df['anniversary'].notna()]['email'].tolist()
                    if invalid_anniversaries:
                        self.logger.warning(f"Invalid anniversary dates for employees: {invalid_anniversaries}")
                except Exception as e:
                    self.log_error("Error parsing anniversary dates", e)
            
            return df
            
        except Exception as e:
            self.log_error(f"Error loading CSV file: {csv_file}", e)
            return pd.DataFrame()
    
    def add_text_to_image(self, image_path: str, text: str, 
                         position: tuple = (50, 50), 
                         font_size: int = 40,
                         font_color: str = "#000000",
                         custom_font_path: Optional[str] = None,
                         output_filename: Optional[str] = None,
                         center_align: bool = False,
                         multiline: bool = False) -> Tuple[Optional[bytes], Optional[str]]:
        """
        Add personalized text to greeting card image and save to output folder
        
        CUSTOMIZATION GUIDE:
        ===================
        
        1. FONT SIZE:
           - Change font_size parameter: font_size=60 (larger) or font_size=20 (smaller)
           - Default is 40
        
        2. TEXT POSITION:
           - Change position parameter: position=(x, y)
           - (0, 0) = top-left corner
           - (100, 50) = 100 pixels right, 50 pixels down
           - For center text: set center_align=True
        
        3. FONT COLOR (HEX):
           - Change font_color parameter: font_color="#FF0000" (red)
           - "#000000" = Black (default)
           - "#FFFFFF" = White
           - "#FF0000" = Red
           - "#00FF00" = Green
           - "#0000FF" = Blue
           - "#FFD700" = Gold
           - "#800080" = Purple
        
        4. CUSTOM FONTS:
           - Set custom_font_path parameter to your font file
           - Example: custom_font_path="fonts/Arial.ttf"
        
        5. CENTER ALIGNMENT:
           - Set center_align=True to center text horizontally
           - position parameter becomes the Y-coordinate for vertical placement
        
        6. MULTILINE TEXT:
           - Set multiline=True for text with line breaks
           - Useful for "Happy Anniversary\nJohn" format
        
        Args:
            image_path: Path to the greeting card image
            text: Text to add (e.g., "Happy Birthday John" or "Happy Anniversary\nJohn")
            position: (x, y) position for text placement, or (ignored, y) if center_align=True
            font_size: Size of the font
            font_color: Hex color string for text (e.g., "#FF0000")
            custom_font_path: Path to custom font file
            output_filename: Optional filename to save the image
            center_align: If True, center text horizontally (position[0] ignored)
            multiline: If True, handle text with line breaks properly
            
        Returns:
            tuple: (image_bytes, saved_file_path) or (None, None) on error
        """
        try:
            if not os.path.exists(image_path):
                raise FileNotFoundError(f"Image file not found: {image_path}")
                
            # Open the image
            with Image.open(image_path) as img:
                # Convert to RGB if necessary
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Create drawing context
                draw = ImageDraw.Draw(img)
                
                # Convert hex color to RGB
                rgb_color = self.hex_to_rgb(font_color)
                
                # ================================================================
                # FONT LOADING SECTION
                # ================================================================
                font = None
                
                # Option 1: Try custom font if provided
                if custom_font_path:
                    try:
                        if os.path.exists(custom_font_path):
                            font = ImageFont.truetype(custom_font_path, font_size)
                            self.logger.info(f"Using custom font: {custom_font_path} with size {font_size}")
                        else:
                            self.logger.warning(f"Custom font not found: {custom_font_path}")
                    except Exception as e:
                        self.logger.warning(f"Failed to load custom font {custom_font_path}: {e}")
                
                # Option 2: Try system fonts if custom font failed
                if not font:
                    font_paths = [
                        # Windows fonts
                        "arial.ttf",
                        "calibri.ttf", 
                        "times.ttf",
                        "C:/Windows/Fonts/arial.ttf",
                        "C:/Windows/Fonts/calibri.ttf",
                        "C:/Windows/Fonts/times.ttf",
                        
                        # macOS fonts
                        "/System/Library/Fonts/Arial.ttf",
                        "/System/Library/Fonts/Times.ttc", 
                        "/System/Library/Fonts/Helvetica.ttc",
                        
                        # Linux fonts
                        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
                    ]
                    
                    for font_path in font_paths:
                        try:
                            font = ImageFont.truetype(font_path, font_size)
                            self.logger.info(f"Using system font: {font_path} with size {font_size}")
                            break
                        except:
                            continue
                
                # Option 3: Fallback to default font
                if not font:
                    font = ImageFont.load_default()
                    self.logger.warning(f"Using default font with size {font_size} - text may not display optimally")
                
                # Get image dimensions
                img_width, img_height = img.size
                
                # Calculate text positioning
                if center_align:
                    if multiline:
                        # Handle multiline text (for anniversary cards)
                        lines = text.split('\n')
                        line_height = font_size + 10  # Add some spacing between lines
                        total_text_height = len(lines) * line_height
                        
                        # Start Y position (use position[1] or center vertically)
                        start_y = position[1] if position[1] > 0 else (img_height - total_text_height) // 2
                        
                        # Draw each line centered
                        for i, line in enumerate(lines):
                            line_width = draw.textlength(line, font=font)
                            line_x = (img_width - line_width) // 2
                            line_y = start_y + (i * line_height)
                            draw.text((line_x, line_y), line, font=font, fill=rgb_color)
                    else:
                        # Single line text (for birthday cards)
                        text_width = draw.textlength(text, font=font)
                        text_x = (img_width - text_width) // 2
                        text_y = position[1]  # Use provided Y position
                        draw.text((text_x, text_y), text, font=font, fill=rgb_color)
                else:
                    # Use exact position provided (legacy behavior)
                    draw.text(position, text, font=font, fill=rgb_color)
                
                # Save to bytes
                img_bytes = io.BytesIO()
                img.save(img_bytes, format='JPEG', quality=95)
                img_bytes.seek(0)
                
                # Save to output folder
                if output_filename:
                    output_path = os.path.join(self.output_folder, output_filename)
                    img.save(output_path, format='JPEG', quality=95)
                    self.logger.info(f"Personalized image saved: {output_path}")
                    return img_bytes.getvalue(), output_path
                
                return img_bytes.getvalue(), None
                
        except Exception as e:
            self.log_error(f"Error processing image: {image_path}", e)
            return None, None
    
    def find_birthdays_today(self, df: pd.DataFrame) -> List[Dict]:
        """
        Find employees with birthdays today
        
        Returns:
            List of dictionaries with employee birthday information
        """
        try:
            today = datetime.date.today()
            self.logger.info("Checking for birthdays today...")
            
            # Filter employees with birthdays today
            birthday_employees = df[
                (df['birthday'].dt.month == today.month) & 
                (df['birthday'].dt.day == today.day) &
                (df['birthday'].notna())
            ]
            
            self.logger.info(f"Found {len(birthday_employees)} employees with birthdays today")
            
            birthdays_today = []
            for _, employee in birthday_employees.iterrows():
                birthday_info = {
                    'first_name': employee['first_name'],
                    'last_name': employee['last_name'],
                    'email': employee['email'],
                    'birthday': employee['birthday'],
                    'age': today.year - employee['birthday'].year
                }
                birthdays_today.append(birthday_info)
                self.stats['birthdays_today'].append(birthday_info)
            
            return birthdays_today
            
        except Exception as e:
            self.log_error("Error finding birthdays", e)
            return []
    
    def find_anniversaries_today(self, df: pd.DataFrame) -> List[Dict]:
        """
        Find employees with marriage anniversaries today
        
        Returns:
            List of dictionaries with employee anniversary information
        """
        try:
            today = datetime.date.today()
            self.logger.info("Checking for marriage anniversaries today...")
            
            # Check if anniversary column exists
            if 'anniversary' not in df.columns:
                self.logger.warning("No anniversary column found in employee data")
                return []
            
            # Filter employees with marriage anniversaries today
            anniversary_employees = df[
                (df['anniversary'].dt.month == today.month) & 
                (df['anniversary'].dt.day == today.day) &
                (df['anniversary'].notna())
            ]
            
            self.logger.info(f"Found {len(anniversary_employees)} employees with marriage anniversaries today")
            
            anniversaries_today = []
            for _, employee in anniversary_employees.iterrows():
                years = today.year - employee['anniversary'].year
                anniversary_info = {
                    'first_name': employee['first_name'],
                    'last_name': employee['last_name'],
                    'email': employee['email'],
                    'anniversary': employee['anniversary'],
                    'years': years
                }
                anniversaries_today.append(anniversary_info)
                self.stats['anniversaries_today'].append(anniversary_info)
            
            return anniversaries_today
            
        except Exception as e:
            self.log_error("Error finding anniversaries", e)
            return []
    
    def create_birthday_cards(self, birthdays: List[Dict], birthday_card_path: str,
                             text_position: tuple = (50, 50),
                             font_size: int = 40,
                             font_color: str = "#000000",
                             custom_font_path: Optional[str] = None,
                             center_align: bool = False) -> List[str]:
        """
        Create birthday cards for employees with birthdays today
        
        Args:
            birthdays: List of birthday information dictionaries
            birthday_card_path: Path to the birthday card template image
            text_position: (x, y) position for text placement
            font_size: Size of the font
            font_color: Hex color string for text
            custom_font_path: Path to custom font file
            center_align: If True, center text horizontally
            
        Returns:
            List of paths to created birthday card images
        """
        created_cards = []
        today = datetime.date.today()
        
        try:
            if not os.path.exists(birthday_card_path):
                self.log_error(f"Birthday card template not found: {birthday_card_path}")
                return created_cards
            
            for birthday_info in birthdays:
                try:
                    first_name = birthday_info['first_name']
                    last_name = birthday_info['last_name']
                    
                    # Create personalized greeting
                    greeting_text = f"Happy Birthday {first_name}"
                    
                    # Generate unique filename for this image
                    output_filename = f"birthday_{first_name}_{last_name}_{today.strftime('%Y%m%d')}.jpg"
                    
                    # Add text to birthday card
                    image_bytes, saved_path = self.add_text_to_image(
                        birthday_card_path, 
                        greeting_text, 
                        text_position,
                        font_size,
                        font_color,
                        custom_font_path,
                        output_filename=output_filename,
                        center_align=center_align,
                        multiline=False  # Birthday cards are single line
                    )
                    
                    if saved_path:
                        created_cards.append(saved_path)
                        self.stats['birthday_cards_created'] += 1
                        self.logger.info(f"Created birthday card for {first_name} {last_name}")
                    else:
                        self.log_error(f"Failed to create birthday card for {first_name} {last_name}")
                        
                except Exception as e:
                    self.log_error(f"Error creating birthday card for {birthday_info.get('first_name', 'Unknown')}", e)
                    
        except Exception as e:
            self.log_error("Error in birthday card creation process", e)
            
        return created_cards
    
    def create_anniversary_cards(self, anniversaries: List[Dict], anniversary_card_path: str,
                                text_position: tuple = (0, 300),
                                font_size: int = 40,
                                font_color: str = "#000000",
                                custom_font_path: Optional[str] = None,
                                center_align: bool = True) -> List[str]:
        """
        Create anniversary cards for employees with anniversaries today
        
        Args:
            anniversaries: List of anniversary information dictionaries
            anniversary_card_path: Path to the anniversary card template image
            text_position: (x, y) position for text placement (x ignored if center_align=True)
            font_size: Size of the font
            font_color: Hex color string for text
            custom_font_path: Path to custom font file
            center_align: If True, center text horizontally (default: True)
            
        Returns:
            List of paths to created anniversary card images
        """
        created_cards = []
        today = datetime.date.today()
        
        try:
            if not os.path.exists(anniversary_card_path):
                self.log_error(f"Anniversary card template not found: {anniversary_card_path}")
                return created_cards
            
            for anniversary_info in anniversaries:
                try:
                    first_name = anniversary_info['first_name']
                    last_name = anniversary_info['last_name']
                    years = anniversary_info['years']
                    
                    # Create personalized greeting with name on next line
                    greeting_text = f"Happy Anniversary\n{first_name}"
                    
                    # Generate unique filename for this image
                    output_filename = f"anniversary_{first_name}_{last_name}_{today.strftime('%Y%m%d')}.jpg"
                    
                    # Add text to anniversary card
                    image_bytes, saved_path = self.add_text_to_image(
                        anniversary_card_path, 
                        greeting_text, 
                        text_position,
                        font_size,
                        font_color,
                        custom_font_path,
                        output_filename=output_filename,
                        center_align=center_align,
                        multiline=True  # Anniversary cards have name on next line
                    )
                    
                    if saved_path:
                        created_cards.append(saved_path)
                        self.stats['anniversary_cards_created'] += 1
                        self.logger.info(f"Created anniversary card for {first_name} {last_name} ({years} years)")
                    else:
                        self.log_error(f"Failed to create anniversary card for {first_name} {last_name}")
                        
                except Exception as e:
                    self.log_error(f"Error creating anniversary card for {anniversary_info.get('first_name', 'Unknown')}", e)
                    
        except Exception as e:
            self.log_error("Error in anniversary card creation process", e)
            
        return created_cards
    
    def process_daily_cards(self, csv_file: str, birthday_card_path: str, 
                           anniversary_card_path: str,
                           birthday_text_pos: tuple = (50, 50),
                           anniversary_text_pos: tuple = (0, 300),
                           birthday_font_size: int = 40,
                           anniversary_font_size: int = 40,
                           birthday_font_color: str = "#000000",
                           anniversary_font_color: str = "#000000",
                           birthday_font_path: Optional[str] = None,
                           anniversary_font_path: Optional[str] = None,
                           birthday_center_align: bool = False,
                           anniversary_center_align: bool = True) -> Dict:
        """
        Process daily cards for both birthdays and anniversaries
        
        Returns:
            Dictionary with results and statistics
        """
        try:
            self.logger.info(f"Starting daily card generation for {datetime.date.today()}")
            
            # Load employee data
            df = self.load_employee_data(csv_file)
            
            if df.empty:
                self.log_error("No employee data found or failed to load CSV file")
                return {'success': False, 'error': 'No employee data found'}
            
            # Find birthdays and anniversaries today
            birthdays_today = self.find_birthdays_today(df)
            anniversaries_today = self.find_anniversaries_today(df)
            
            # Create birthday cards
            birthday_cards = []
            if birthdays_today:
                birthday_cards = self.create_birthday_cards(
                    birthdays_today, 
                    birthday_card_path,
                    birthday_text_pos,
                    birthday_font_size,
                    birthday_font_color,
                    birthday_font_path,
                    birthday_center_align
                )
            
            # Create anniversary cards
            anniversary_cards = []
            if anniversaries_today:
                anniversary_cards = self.create_anniversary_cards(
                    anniversaries_today,
                    anniversary_card_path,
                    anniversary_text_pos,
                    anniversary_font_size,
                    anniversary_font_color,
                    anniversary_font_path,
                    anniversary_center_align
                )
            
            self.stats['end_time'] = datetime.datetime.now()
            
            result = {
                'success': True,
                'birthdays_today': birthdays_today,
                'anniversaries_today': anniversaries_today,
                'birthday_cards_created': birthday_cards,
                'anniversary_cards_created': anniversary_cards,
                'stats': self.stats
            }
            
            self.logger.info(f"Card generation completed. Created {len(birthday_cards)} birthday cards and {len(anniversary_cards)} anniversary cards")
            
            return result
            
        except Exception as e:
            self.log_error("Critical error in daily card processing", e)
            return {'success': False, 'error': str(e)}


# Example usage
def main():
    """Example usage of the birthday and anniversary card generator"""
    
    # Load environment variables from .env file
    load_dotenv()
    
    # Configuration from .env file
    OUTPUT_FOLDER = os.getenv('OUTPUT_FOLDER', 'output')
    CSV_FILE = os.getenv('CSV_FILE', 'employees_test_today.csv')
    BIRTHDAY_CARD = os.getenv('BIRTHDAY_CARD', 'assets\\Slide2.PNG')
    ANNIVERSARY_CARD = os.getenv('ANNIVERSARY_CARD', 'assets\\Slide1.PNG')
    
    # Text positioning for 1280x720 images from .env
    BIRTHDAY_TEXT_X = int(os.getenv('BIRTHDAY_TEXT_X', '50'))
    BIRTHDAY_TEXT_Y = int(os.getenv('BIRTHDAY_TEXT_Y', '300'))
    ANNIVERSARY_TEXT_X = int(os.getenv('ANNIVERSARY_TEXT_X', '0'))
    ANNIVERSARY_TEXT_Y = int(os.getenv('ANNIVERSARY_TEXT_Y', '200'))
    
    BIRTHDAY_TEXT_POSITION = (BIRTHDAY_TEXT_X, BIRTHDAY_TEXT_Y)
    ANNIVERSARY_TEXT_POSITION = (ANNIVERSARY_TEXT_X, ANNIVERSARY_TEXT_Y)
    
    # Font customization from .env
    BIRTHDAY_FONT_SIZE = int(os.getenv('BIRTHDAY_FONT_SIZE', '64'))
    ANNIVERSARY_FONT_SIZE = int(os.getenv('ANNIVERSARY_FONT_SIZE', '72'))
    BIRTHDAY_FONT_COLOR = os.getenv('BIRTHDAY_FONT_COLOR', '#4b446a')
    ANNIVERSARY_FONT_COLOR = os.getenv('ANNIVERSARY_FONT_COLOR', '#72719f')
    
    # Font paths from .env
    BIRTHDAY_FONT_PATH = os.getenv('BIRTHDAY_FONT_PATH', 'fonts/Inkfree.ttf')
    ANNIVERSARY_FONT_PATH = os.getenv('ANNIVERSARY_FONT_PATH', 'C:/Windows/Fonts/HTOWERT.TTF')
    
    # Alignment from .env
    BIRTHDAY_CENTER_ALIGN = os.getenv('BIRTHDAY_CENTER_ALIGN', 'false').lower() == 'true'
    ANNIVERSARY_CENTER_ALIGN = os.getenv('ANNIVERSARY_CENTER_ALIGN', 'true').lower() == 'true'
    
    print("🚀 Starting Birthday & Anniversary Card Generator")
    print(f"📁 Output Folder: {OUTPUT_FOLDER}")
    print(f"📊 CSV File: {CSV_FILE}")
    print(f"🎂 Birthday Card Template: {BIRTHDAY_CARD}")
    print(f"💕 Anniversary Card Template: {ANNIVERSARY_CARD}")
    print(f"🎨 Birthday Font: {BIRTHDAY_FONT_PATH} (Size: {BIRTHDAY_FONT_SIZE}, Color: {BIRTHDAY_FONT_COLOR})")
    print(f"🎨 Anniversary Font: {ANNIVERSARY_FONT_PATH} (Size: {ANNIVERSARY_FONT_SIZE}, Color: {ANNIVERSARY_FONT_COLOR})")
    print(f"📍 Birthday Position: {BIRTHDAY_TEXT_POSITION} {'(Center Aligned)' if BIRTHDAY_CENTER_ALIGN else ''}")
    print(f"📍 Anniversary Position: {ANNIVERSARY_TEXT_POSITION} {'(Center Aligned)' if ANNIVERSARY_CENTER_ALIGN else ''}")
    
    # Initialize card generator
    generator = BirthdayAnniversaryGenerator(output_folder=OUTPUT_FOLDER)
    
    # Process daily cards
    result = generator.process_daily_cards(
        csv_file=CSV_FILE,
        birthday_card_path=BIRTHDAY_CARD,
        anniversary_card_path=ANNIVERSARY_CARD,
        birthday_text_pos=BIRTHDAY_TEXT_POSITION,
        anniversary_text_pos=ANNIVERSARY_TEXT_POSITION,
        birthday_font_size=BIRTHDAY_FONT_SIZE,
        anniversary_font_size=ANNIVERSARY_FONT_SIZE,
        birthday_font_color=BIRTHDAY_FONT_COLOR,
        anniversary_font_color=ANNIVERSARY_FONT_COLOR,
        birthday_font_path=BIRTHDAY_FONT_PATH,
        anniversary_font_path=ANNIVERSARY_FONT_PATH,
        birthday_center_align=BIRTHDAY_CENTER_ALIGN,
        anniversary_center_align=ANNIVERSARY_CENTER_ALIGN
    )
    
    if result['success']:
        print("✅ Card generation completed successfully!")
        print(f"🎂 Birthdays today: {len(result['birthdays_today'])}")
        print(f"💕 Anniversaries today: {len(result['anniversaries_today'])}")
        print(f"🖼️ Birthday cards created: {len(result['birthday_cards_created'])}")
        print(f"🖼️ Anniversary cards created: {len(result['anniversary_cards_created'])}")
        
        # Print individual results
        if result['birthdays_today']:
            print("\n🎉 BIRTHDAYS TODAY:")
            for birthday in result['birthdays_today']:
                print(f"  - {birthday['first_name']} {birthday['last_name']} (Age: {birthday['age']})")
        
        if result['anniversaries_today']:
            print("\n💝 ANNIVERSARIES TODAY:")
            for anniversary in result['anniversaries_today']:
                print(f"  - {anniversary['first_name']} {anniversary['last_name']} ({anniversary['years']} years)")
                
    else:
        print(f"❌ Error: {result.get('error', 'Unknown error occurred')}")


if __name__ == "__main__":
    main()


# Example CSV structure (save as employees_test_today.csv)
"""
first_name,last_name,email,birthday,anniversary
John,Doe,john.doe@company.com,1990-06-20,2018-05-20
Jane,Smith,jane.smith@company.com,1985-12-25,2015-08-15
Bob,Johnson,bob.johnson@company.com,1992-06-20,2020-10-12
Alice,Brown,alice.brown@company.com,1988-03-14,
Sarah,Wilson,sarah.wilson@company.com,1991-06-20,2019-09-14
"""