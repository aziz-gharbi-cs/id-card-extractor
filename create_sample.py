from PIL import Image, ImageDraw, ImageFont
import os

def create_sample_passport(filename="sample_passport.jpg"):
    # Create white canvas
    width, height = 600, 400
    img = Image.new('RGB', (width, height), color=(255, 255, 255))
    d = ImageDraw.Draw(img)
    
    # Needs a font, default might be too small/ugly but works for OCR
    # Try to load arial if possible, else default
    try:
        font = ImageFont.truetype("arial.ttf", 20)
        mrz_font = ImageFont.truetype("arial.ttf", 16)
        header_font = ImageFont.truetype("arial.ttf", 24)
    except IOError:
        font = ImageFont.load_default()
        mrz_font = ImageFont.load_default()
        header_font = ImageFont.load_default()

    # Draw Header
    d.text((20, 20), "UTOPIA PASSPORT", fill=(0,0,0), font=header_font)
    
    # Draw Photo Placeholder
    d.rectangle([20, 60, 120, 180], outline=(0,0,0), width=2)
    d.text((35, 110), "PHOTO", fill=(0,0,0), font=font)
    
    # Draw Fields
    labels = ["Type", "Code", "Passport No"]
    values = ["P", "UTO", "123456789"]
    
    for i, (label, val) in enumerate(zip(labels, values)):
        d.text((140 + i*100, 70), label, fill=(100,100,100), font=font)
        d.text((140 + i*100, 95), val, fill=(0,0,0), font=font)
    
    d.text((140, 130), "Surname", fill=(100,100,100), font=font)
    d.text((140, 155), "DOE", fill=(0,0,0), font=font)
    
    d.text((140, 190), "Given Names", fill=(100,100,100), font=font)
    d.text((140, 215), "JOHN", fill=(0,0,0), font=font)
    
    d.text((140, 250), "Nationality", fill=(100,100,100), font=font)
    d.text((140, 275), "UTOPIAN", fill=(0,0,0), font=font)
    
    d.text((300, 250), "Date of birth", fill=(100,100,100), font=font)
    d.text((300, 275), "01 JAN 1980", fill=(0,0,0), font=font)

    # Draw MRZ (Machine Readable Zone)
    # TD3 format (2 lines, 44 chars)
    # Line 1: P<UTO(Issuer)DOE<<JOHN<<<<<<<<<<<<<<<<<<<<<<
    # Line 2: 123456789(Pass#)7(Check)UTO(Nat)800101(DOB)8(Check)M(Sex)270101(Exp)8(Check)<<<<<<<<<<<<<<0(Check)
    
    # We will make sure this is decently clear
    
    mrz_line1 = "P<UTODOE<<JOHN<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<"
    mrz_line2 = "1234567897UTO8001018M2701018<<<<<<<<<<<<<<00"
    
    # Using monospaced font is critical for MRZ usually, but OCR handles arial ok mostly
    # Try to verify if consolas exists for better simulation
    try:
        mono_font = ImageFont.truetype("consola.ttf", 18)
    except:
        mono_font = mrz_font

    d.text((20, 340), mrz_line1, fill=(0,0,0), font=mono_font)
    d.text((20, 365), mrz_line2, fill=(0,0,0), font=mono_font)
    
    img.save(filename)
    print(f"Sample passport saved to {filename}")

if __name__ == "__main__":
    create_sample_passport()
