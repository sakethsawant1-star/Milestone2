import json
import os
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime

CONFIG_PATH = os.path.join(os.path.dirname(__file__), '..', 'phase0_config', 'config.json')
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')

def load_config():
    with open(CONFIG_PATH, 'r') as f:
        return json.load(f)

def clean_html(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Remove irrelevant tags
    for tag in soup(['script', 'style', 'nav', 'footer', 'header', 'svg', 'iframe', 'noscript', 'path']):
        tag.decompose()
        
    # Extract text with spaces
    text = soup.get_text(separator=' ', strip=True)
    
    # Remove extra whitespaces
    text = re.sub(r'\s+', ' ', text)
    return text

def scrape_data():
    os.makedirs(DATA_DIR, exist_ok=True)
    config = load_config()
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    print(f"Starting ingestion for {config['project_context']['selected_amc']}...")
    
    for scheme in config['target_schemes']:
        name = scheme['name']
        url = scheme['url']
        
        # Create a slug from the name for the filename
        slug = re.sub(r'[^a-zA-Z0-9]+', '-', name).strip('-').lower()
        filepath = os.path.join(DATA_DIR, f"{slug}.txt")
        
        print(f"Fetching: {name} ({url})")
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            clean_text = clean_html(response.text)
            
            # Save the clean text along with metadata
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"Source URL: {url}\n")
                f.write(f"Scheme Name: {name}\n")
                f.write(f"Scraped At: {datetime.now().isoformat()}\n")
                f.write("-" * 50 + "\n\n")
                f.write(clean_text)
                
            print(f"Successfully saved to {filepath} (Size: {len(clean_text)} bytes)")
            
        except Exception as e:
            print(f"Error fetching {name}: {str(e)}")

if __name__ == '__main__':
    scrape_data()
