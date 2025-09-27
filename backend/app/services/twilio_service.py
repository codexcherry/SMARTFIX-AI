from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from typing import Dict, Any, Optional
import logging
import re
import os

# Set up logging
logger = logging.getLogger(__name__)

class TwilioService:
    def __init__(
        self, 
        account_sid: Optional[str] = None,
        auth_token: Optional[str] = None,
        from_phone: Optional[str] = None
    ):
        # Get credentials from environment variables or parameters
        self.account_sid = account_sid or os.getenv('TWILIO_SID')
        self.auth_token = auth_token or os.getenv('TWILIO_AUTH_TOKEN')
        self.from_phone = from_phone or os.getenv('TWILIO_FROM_PHONE')
        
        # Initialize client if credentials are available
        self.client = None
        if self.account_sid and self.auth_token:
            try:
                self.client = Client(self.account_sid, self.auth_token)
                logger.info("Twilio client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Twilio client: {str(e)}")
                self.client = None
        else:
            logger.warning("Twilio credentials not provided")
    
    def validate_phone_number(self, phone_number: str) -> bool:
        """Validate phone number format"""
        # Remove any spaces or dashes
        cleaned = re.sub(r'[\s\-]', '', phone_number)
        
        # Must start with + and have valid length
        if not cleaned.startswith('+'):
            return False
        
        # Remove the + for length checking
        number_part = cleaned[1:]
        
        # Check if it's all digits
        if not number_part.isdigit():
            return False
        
        # Length validation (7-15 digits is standard for international numbers)
        if len(number_part) < 7 or len(number_part) > 15:
            return False
        
        # Specific validation for common countries
        if cleaned.startswith('+91'):  # India
            return len(number_part) == 12  # +91 + 10 digits
        elif cleaned.startswith('+1'):  # US/Canada
            return len(number_part) == 11  # +1 + 10 digits
        elif cleaned.startswith('+44'):  # UK
            return len(number_part) >= 10 and len(number_part) <= 12
        
        # General validation for other countries
        return len(number_part) >= 7 and len(number_part) <= 15
    
    def format_phone_number(self, phone_number: str) -> str:
        """Format phone number to E.164 format"""
        # Remove any spaces, dashes, or parentheses
        cleaned = re.sub(r'[\s\-\(\)]', '', phone_number)
        
        # Handle different input formats
        if cleaned.startswith('+'):
            # Already has country code
            result = cleaned
        elif cleaned.startswith('91') and len(cleaned) == 12:
            # Indian number without + (91XXXXXXXXXX)
            result = '+' + cleaned
        elif cleaned.startswith('91') and len(cleaned) == 13:
            # Indian number with extra digit (91XXXXXXXXXXX)
            result = '+' + cleaned
        elif len(cleaned) == 10 and cleaned.startswith(('6', '7', '8', '9')):
            # Indian mobile number without country code
            result = '+91' + cleaned
        elif len(cleaned) == 11 and cleaned.startswith('0'):
            # Indian number with leading 0
            result = '+91' + cleaned[1:]
        else:
            # Default: add + if not present
            if not cleaned.startswith('+'):
                result = '+' + cleaned
            else:
                result = cleaned
        return result
    
    async def send_sms(self, to_phone: str, message: str) -> Dict[str, Any]:
        """Send SMS notification using Twilio"""
        if not self.client or not self.from_phone:
            error_msg = "Twilio credentials not configured properly"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "message_id": None
            }
        
        try:
            # Format and validate phone number
            formatted_phone = self.format_phone_number(to_phone)
            
            if not self.validate_phone_number(formatted_phone):
                error_msg = f"Invalid phone number format: {to_phone} -> {formatted_phone}"
                logger.error(error_msg)
                return {
                    "success": False,
                    "error": error_msg,
                    "message_id": None
                }
            
            # Send the message
            message_obj = self.client.messages.create(
                body=message,
                from_=self.from_phone,
                to=formatted_phone
            )
            
            logger.info(f"SMS sent successfully to {formatted_phone}. Message SID: {message_obj.sid}")
            
            return {
                "success": True,
                "message_id": message_obj.sid,
                "error": None,
                "status": message_obj.status,
                "to_phone": formatted_phone
            }
        
        except TwilioRestException as e:
            error_msg = f"Twilio API error: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "message_id": None
            }
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "message_id": None
            }
    
    async def send_whatsapp(self, to_phone: str, message: str) -> Dict[str, Any]:
        """Send WhatsApp notification using Twilio"""
        if not self.client or not self.from_phone:
            error_msg = "Twilio credentials not configured properly"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "message_id": None
            }
        
        try:
            # Format and validate phone number
            formatted_phone = self.format_phone_number(to_phone)
            
            if not self.validate_phone_number(formatted_phone):
                error_msg = f"Invalid phone number format: {to_phone} -> {formatted_phone}"
                logger.error(error_msg)
                return {
                    "success": False,
                    "error": error_msg,
                    "message_id": None
                }
            
            # Format WhatsApp numbers
            from_whatsapp = f"whatsapp:{self.from_phone}"
            to_whatsapp = f"whatsapp:{formatted_phone}"
            
            # Send the message
            message_obj = self.client.messages.create(
                body=message,
                from_=from_whatsapp,
                to=to_whatsapp
            )
            
            logger.info(f"WhatsApp message sent successfully to {formatted_phone}. Message SID: {message_obj.sid}")
            
            return {
                "success": True,
                "message_id": message_obj.sid,
                "error": None,
                "status": message_obj.status,
                "to_phone": formatted_phone
            }
        
        except TwilioRestException as e:
            error_msg = f"Twilio API error: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "message_id": None
            }
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "message_id": None
            }

# Example usage and test function
async def test_twilio_service():
    """Test function to verify Twilio service works"""
    # Initialize with your credentials
    twilio_service = TwilioService(
        account_sid="your_twilio_account_sid_here",
        auth_token="your_twilio_auth_token_here",
        from_phone="your_twilio_phone_number_here"
    )
    
    # Test phone number
    test_phone = "+1234567890"  # Replace with your test phone number
    
    # Test SMS
    print("Testing SMS...")
    sms_result = await twilio_service.send_sms(
        to_phone=test_phone,
        message="Hello! This is a test SMS from your Twilio service."
    )
    print(f"SMS Result: {sms_result}")
    
    # Test WhatsApp
    print("\nTesting WhatsApp...")
    whatsapp_result = await twilio_service.send_whatsapp(
        to_phone=test_phone,
        message="Hello! This is a test WhatsApp message from your Twilio service."
    )
    print(f"WhatsApp Result: {whatsapp_result}")

# Run the test if this file is executed directly
if __name__ == "__main__":
    import asyncio
    asyncio.run(test_twilio_service())