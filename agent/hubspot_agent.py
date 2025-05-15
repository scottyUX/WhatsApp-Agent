import os
from dotenv import load_dotenv
from hubspot import HubSpot
from typing import Dict, Optional
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables


class HubspotAgent:
    def __init__(self):
        """Initialize the HubSpot agent with API credentials."""
        self.api_key = os.getenv("HUBSPOT_API_KEY")
        if not self.api_key:
            raise ValueError("HUBSPOT_API_KEY environment variable is not set")
        
        self.client = HubSpot(access_token=self.api_key)
        
    def create_contact(self, 
                      phone: str,
                      firstname: Optional[str] = None,
                      lastname: Optional[str] = None,
                      email: Optional[str] = None,
                      company: Optional[str] = None,
                      additional_properties: Optional[Dict] = None) -> Dict:
        """
        Create a new contact in HubSpot.
        
        Args:
            email (str): Contact's email address (required)
            firstname (str, optional): Contact's first name
            lastname (str, optional): Contact's last name
            phone (str, optional): Contact's phone number
            company (str, optional): Contact's company name
            additional_properties (dict, optional): Additional properties to set for the contact
            
        Returns:
            Dict: The created contact's data
        """
        try:
            # Prepare properties
            properties = {
                "email": email
            }
            
            # Add optional properties if provided
            if firstname:
                properties["firstname"] = firstname
            if lastname:
                properties["lastname"] = lastname
            if phone:
                properties["phone"] = phone
            if company:
                properties["company"] = company
                
            # Add any additional properties
            if additional_properties:
                properties.update(additional_properties)
            
            # Create the contact
            contact = self.client.crm.contacts.basic_api.create(
                properties=properties
            )
            
            logger.info(f"Successfully created contact with email: {email}")
            return contact
            
        except Exception as e:
            logger.error(f"Error creating contact: {str(e)}")
            raise
    
    def get_contact(self, email: str) -> Optional[Dict]:
        """
        Get a contact by phone number.
        
        Args:
            phone (str): The email address to search for
            
        Returns:
            Optional[Dict]: The contact data if found, None otherwise
        """
        try:
            # Search for the contact by email
            filter_groups = [{
                "filters": [{
                    "propertyName": "email",
                    "operator": "EQ",
                    "value": email
                }]
            }]
            
            response = self.client.crm.contacts.search_api.do_search(
                filter_groups=filter_groups
            )
            
            if response.results:
                return response.results[0]
            return None
            
        except Exception as e:
            logger.error(f"Error searching for contact: {str(e)}")
            raise

def main():
    """Example usage of the HubspotAgent."""
    try:
        # Initialize the agent
        agent = HubspotAgent()
        
        # Example: Create a new contact
        new_contact = agent.create_contact(
            email="example@example.com",
            firstname="John",
            lastname="Doe",
            phone="+1234567890",
            company="Example Corp",
            additional_properties={
                "lifecyclestage": "lead",
                "source": "website"
            }
        )
        
        print(f"Created contact: {new_contact}")
        
        # Example: Search for a contact
        contact = agent.get_contact("+18312959447")
        if contact:
            print(f"Found contact: {contact}")
        else:
            print("Contact not found")
            
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main() 