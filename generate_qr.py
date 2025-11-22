#!/usr/bin/env python3
"""
Generate QR code for easy phone access to MIMIQ monitoring interface
"""

import qrcode
from pathlib import Path

# Your phone monitoring URL
PHONE_URL = "http://10.0.0.8:5000/phone_monitor.html"

def generate_qr():
    """Generate QR code for phone access"""
    
    # Create QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    
    qr.add_data(PHONE_URL)
    qr.make(fit=True)
    
    # Create image
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Save
    output_path = Path(__file__).parent / "phone_qr_code.png"
    img.save(output_path)
    
    print("✅ QR Code generated!")
    print(f"📁 Saved to: {output_path}")
    print(f"📱 URL: {PHONE_URL}")
    print("\n📸 Scan this QR code with your phone to access the monitoring interface!")
    
    # Also print ASCII QR code
    print("\n" + "="*50)
    print("ASCII QR CODE (for quick reference):")
    print("="*50 + "\n")
    
    qr_ascii = qrcode.QRCode()
    qr_ascii.add_data(PHONE_URL)
    qr_ascii.make()
    qr_ascii.print_ascii(invert=True)
    
    print("\n" + "="*50)
    print(f"Scan this to open: {PHONE_URL}")
    print("="*50)

if __name__ == "__main__":
    try:
        generate_qr()
    except ImportError:
        print("⚠️  qrcode library not installed")
        print("📦 Install it: .venv/bin/pip install qrcode[pil]")
        print("\nFor now, just type this URL on your phone:")
        print(f"📱 {PHONE_URL}")
