import unittest
from unittest.mock import patch, MagicMock
import json

from startup_agent.agents.startup_collector import StartupCollector

class TestStartupCollector(unittest.TestCase):
    """Tests for the StartupCollector agent"""
    
    @patch('startup_agent.agents.startup_collector.requests.post')
    def test_get_recent_funding_rounds(self, mock_post):
        """Test that get_recent_funding_rounds processes API response correctly"""
        # Mock the API response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "entities": [
                {
                    "properties": {
                        "identifier": {"value": "123"},
                        "entity_identifier": {"value": "org-123"},
                        "announced_on": {"value": "2023-04-01"},
                        "investment_type": {"value": "seed"},
                        "money_raised": {"value": 1000000},
                        "money_raised_currency_code": {"value": "USD"}
                    }
                }
            ]
        }
        mock_post.return_value = mock_response
        
        # Mock the _get_organization_details method
        with patch.object(StartupCollector, '_get_organization_details') as mock_get_org:
            mock_get_org.return_value = {
                "name": "Test Company",
                "description": "A test company",
                "website": "https://testcompany.com",
                "location": "San Francisco, CA, USA",
                "categories": ["Software", "AI"],
                "company_size": "1-10",
                "founded_year": "2023"
            }
            
            # Create the collector and call the method
            collector = StartupCollector()
            result = collector.get_recent_funding_rounds()
            
            # Check that the result is as expected
            self.assertEqual(len(result), 1)
            self.assertEqual(result[0]["company_name"], "Test Company")
            self.assertEqual(result[0]["funding_round"], "seed")
            self.assertEqual(result[0]["funding_amount"], 1000000)
            
            # Verify that the API was called with the correct parameters
            mock_post.assert_called_once()
            
    @patch('startup_agent.agents.startup_collector.requests.get')
    def test_get_organization_details(self, mock_get):
        """Test that _get_organization_details processes API response correctly"""
        # Mock the API response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "properties": {
                "name": "Test Company",
                "short_description": "A test company",
                "website": {"value": "https://testcompany.com"},
                "headquarters": [
                    {"value": {"city": "San Francisco", "region": "California", "country": "United States"}}
                ],
                "categories": [
                    {"value": {"name": "Software"}},
                    {"value": {"name": "AI"}}
                ],
                "num_employees_enum": "1-10",
                "founded_on": {"value": {"year": "2023"}}
            }
        }
        mock_get.return_value = mock_response
        
        # Create the collector and call the method
        collector = StartupCollector()
        result = collector._get_organization_details("org-123")
        
        # Check that the result is as expected
        self.assertEqual(result["name"], "Test Company")
        self.assertEqual(result["website"], "https://testcompany.com")
        self.assertEqual(result["location"], "San Francisco, California, United States")
        self.assertEqual(result["categories"], ["Software", "AI"])
        self.assertEqual(result["company_size"], "1-10")
        self.assertEqual(result["founded_year"], "2023")

if __name__ == '__main__':
    unittest.main() 