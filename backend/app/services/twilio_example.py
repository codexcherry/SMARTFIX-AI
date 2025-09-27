"""
Example usage of TwilioService
This file shows how to use the TwilioService class to send SMS and WhatsApp messages.
"""

import asyncio
import os
from twilio_service import TwilioService

async def main():
    """Main function to demonstrate Twilio service usage"""
    
    # Method 1: Initialize with credentials directly
    twilio_service = TwilioService(
        account_sid="your_twilio_account_sid_here",
        auth_token="your_twilio_auth_token_here",
        from_phone="your_twilio_phone_number_here"
    )
    
    # Method 2: Initialize with environment variables
    # Set these environment variables before running:
    # export TWILIO_SID="your_account_sid"
    # export TWILIO_AUTH_TOKEN="your_auth_token"
    # export TWILIO_FROM_PHONE="your_twilio_phone"
    # twilio_service = TwilioService()
    
    # Test phone number (replace with your actual number)
    test_phone = "+1234567890"  # Replace with your test phone number
    
    print("=== Twilio Service Test ===")
    
    # Test SMS sending
    print("\n1. Testing SMS...")
    sms_result = await twilio_service.send_sms(
        to_phone=test_phone,
        message="Hello! This is a test SMS from your SmartFix application."
    )
    
    if sms_result["success"]:
        print(f"✅ SMS sent successfully!")
        print(f"   Message ID: {sms_result['message_id']}")
        print(f"   Status: {sms_result['status']}")
        print(f"   To: {sms_result['to_phone']}")
    else:
        print(f"❌ SMS failed: {sms_result['error']}")
    
    # Test WhatsApp sending
    print("\n2. Testing WhatsApp...")
    whatsapp_result = await twilio_service.send_whatsapp(
        to_phone=test_phone,
        message="Hello! This is a test WhatsApp message from your SmartFix application."
    )
    
    if whatsapp_result["success"]:
        print(f"✅ WhatsApp message sent successfully!")
        print(f"   Message ID: {whatsapp_result['message_id']}")
        print(f"   Status: {whatsapp_result['status']}")
        print(f"   To: {whatsapp_result['to_phone']}")
    else:
        print(f"❌ WhatsApp failed: {whatsapp_result['error']}")
    
    # Test with different phone number formats
    print("\n3. Testing different phone number formats...")
    
    test_numbers = [
        "1234567890",        # Without +
        "+1 234567890",      # With space
        "+1-234-567-890",    # With dashes
        "(+1) 234567890",    # With parentheses
    ]
    
    for phone in test_numbers:
        print(f"\nTesting format: {phone}")
        result = await twilio_service.send_sms(
            to_phone=phone,
            message=f"Test message for format: {phone}"
        )
        
        if result["success"]:
            print(f"✅ Successfully formatted and sent to: {result['to_phone']}")
        else:
            print(f"❌ Failed: {result['error']}")

if __name__ == "__main__":
    # Run the example
    asyncio.run(main())





