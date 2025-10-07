#!/usr/bin/env python3
"""
Lenus Clinic Website Scraper
Scrapes all pages from https://lenusclinic.com/ and saves content to text file
"""

import requests
from bs4 import BeautifulSoup
import time
import re
from urllib.parse import urljoin, urlparse
import os
from datetime import datetime

class LenusClinicScraper:
    def __init__(self, base_url="https://lenusclinic.com"):
        self.base_url = base_url
        self.visited_urls = set()
        self.scraped_content = []
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
    def is_valid_url(self, url):
        """Check if URL is valid and belongs to the same domain"""
        try:
            parsed = urlparse(url)
            return (
                parsed.netloc == 'lenusclinic.com' and
                not any(ext in url for ext in ['.pdf', '.jpg', '.png', '.gif', '.css', '.js', '.mp4', '.avi'])
            )
        except:
            return False
    
    def clean_text(self, text):
        """Clean and format text content"""
        if not text:
            return ""
        
        # Remove extra whitespace and normalize
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Remove common unwanted patterns
        text = re.sub(r'^\s*[•·]\s*', '', text)  # Remove bullet points at start
        text = re.sub(r'\s*[•·]\s*$', '', text)  # Remove bullet points at end
        text = re.sub(r'^\s*[→]\s*', '', text)  # Remove arrows at start
        text = re.sub(r'\s*[→]\s*$', '', text)  # Remove arrows at end
        
        return text
    
    def extract_page_content(self, url):
        """Extract content from a single page"""
        try:
            print(f"📄 Scraping: {url}")
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script, style, and navigation elements
            for script in soup(["script", "style", "nav", "footer", "header", "form"]):
                script.decompose()
            
            # Extract main content
            content = {
                'url': url,
                'title': '',
                'content': '',
                'sections': []
            }
            
            # Get page title
            title_tag = soup.find('title')
            if title_tag:
                content['title'] = self.clean_text(title_tag.get_text())
            
            # Extract main content from various sections
            main_content = soup.find('main') or soup.find('div', class_='content') or soup.find('body')
            
            if main_content:
                # Extract headings and their content
                headings = main_content.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
                
                for heading in headings:
                    heading_text = self.clean_text(heading.get_text())
                    if heading_text and len(heading_text) > 3:  # Only substantial headings
                        section_content = []
                        
                        # Get content after this heading until next heading
                        next_element = heading.find_next_sibling()
                        while next_element and next_element.name not in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                            if next_element.name in ['p', 'div', 'span', 'li', 'ul', 'ol']:
                                text = self.clean_text(next_element.get_text())
                                if text and len(text) > 10:  # Only include substantial text
                                    section_content.append(text)
                            next_element = next_element.find_next_sibling()
                        
                        if section_content:
                            content['sections'].append({
                                'heading': heading_text,
                                'content': ' '.join(section_content)
                            })
                
                # If no sections found, extract all paragraphs
                if not content['sections']:
                    paragraphs = main_content.find_all('p')
                    for p in paragraphs:
                        text = self.clean_text(p.get_text())
                        if text and len(text) > 20:
                            content['content'] += text + '\n\n'
            
            # Extract all links for further crawling
            links = []
            for link in soup.find_all('a', href=True):
                href = link['href']
                full_url = urljoin(url, href)
                if self.is_valid_url(full_url) and full_url not in self.visited_urls:
                    links.append(full_url)
            
            return content, links
            
        except Exception as e:
            print(f"❌ Error scraping {url}: {e}")
            return None, []
    
    def scrape_all_pages(self):
        """Scrape all pages starting from the base URL"""
        print("🚀 Starting Lenus Clinic website scraping...")
        
        urls_to_visit = [self.base_url]
        
        while urls_to_visit:
            current_url = urls_to_visit.pop(0)
            
            if current_url in self.visited_urls:
                continue
                
            self.visited_urls.add(current_url)
            
            content, new_links = self.extract_page_content(current_url)
            
            if content:
                self.scraped_content.append(content)
                urls_to_visit.extend(new_links)
            
            # Be respectful - add delay between requests
            time.sleep(1)
            
            # Limit to prevent infinite crawling
            if len(self.visited_urls) > 30:
                print("⚠️ Reached maximum page limit (30)")
                break
        
        print(f"✅ Scraping complete! Visited {len(self.visited_urls)} pages")
    
    def save_to_file(self, filename="lenus_clinic_content.txt"):
        """Save all scraped content to a text file"""
        print(f"💾 Saving content to {filename}...")
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("LENUS CLINIC WEBSITE CONTENT\n")
            f.write("=" * 50 + "\n")
            f.write(f"Scraped on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total pages: {len(self.scraped_content)}\n")
            f.write("=" * 50 + "\n\n")
            
            for page in self.scraped_content:
                f.write(f"PAGE: {page['url']}\n")
                f.write("-" * 30 + "\n")
                
                if page['title']:
                    f.write(f"TITLE: {page['title']}\n\n")
                
                if page['sections']:
                    for section in page['sections']:
                        f.write(f"## {section['heading']}\n")
                        f.write(f"{section['content']}\n\n")
                elif page['content']:
                    f.write(f"{page['content']}\n\n")
                
                f.write("\n" + "=" * 50 + "\n\n")
        
        print(f"✅ Content saved to {filename}")
        return filename

def main():
    """Main function to run the scraper"""
    scraper = LenusClinicScraper()
    
    try:
        # Scrape all pages
        scraper.scrape_all_pages()
        
        # Save to file
        filename = scraper.save_to_file()
        
        print(f"\n🎉 Scraping completed successfully!")
        print(f"📄 Content saved to: {filename}")
        print(f"📊 Total pages scraped: {len(scraper.scraped_content)}")
        print(f"🔗 Total URLs visited: {len(scraper.visited_urls)}")
        
        # Show some statistics
        total_sections = sum(len(page['sections']) for page in scraper.scraped_content)
        print(f"📝 Total sections found: {total_sections}")
        
    except Exception as e:
        print(f"❌ Scraping failed: {e}")

if __name__ == "__main__":
    main()
