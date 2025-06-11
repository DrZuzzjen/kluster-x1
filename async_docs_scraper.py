import asyncio
import aiohttp
from bs4 import BeautifulSoup
import json
import time
from urllib.parse import urljoin, urlparse
from typing import Dict, List, Set
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AsyncKlusterDocsScaper:
    def __init__(self, base_url: str = "https://docs.kluster.ai", max_concurrent: int = 10):
        self.base_url = base_url
        self.max_concurrent = max_concurrent
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.session = None
        
    async def __aenter__(self):
        connector = aiohttp.TCPConnector(limit=self.max_concurrent, limit_per_host=self.max_concurrent)
        timeout = aiohttp.ClientTimeout(total=30, connect=10)
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def get_all_known_urls(self) -> List[str]:
        """Get all known documentation URLs - same as sync version"""
        known_urls = [
            f"{self.base_url}/get-started/get-api-key/",
            f"{self.base_url}/get-started/models/",
            f"{self.base_url}/get-started/openai-compatibility/",
            f"{self.base_url}/get-started/start-building/",
            f"{self.base_url}/get-started/integrations/",
            f"{self.base_url}/get-started/dedicated-deployments/",
            f"{self.base_url}/get-started/fine-tuning/",
            f"{self.base_url}/get-started/fine-tuning/overview/",
            f"{self.base_url}/get-started/fine-tuning/api/",
            f"{self.base_url}/get-started/verify/",
            f"{self.base_url}/get-started/verify/overview/",
            f"{self.base_url}/get-started/verify/reliability/",
            f"{self.base_url}/get-started/verify/reliability/overview/",
            f"{self.base_url}/get-started/verify/reliability/dedicated-api/",
            f"{self.base_url}/api-reference/",
            f"{self.base_url}/tutorials/",
            f"{self.base_url}/tutorials/text-classification/",
            f"{self.base_url}/tutorials/sentiment-analysis/",
            f"{self.base_url}/tutorials/keyword-extraction/",
            f"{self.base_url}/tutorials/image-analysis/",
            f"{self.base_url}/tutorials/llm-evaluation/",
            f"{self.base_url}/tutorials/prompt-engineering/",
            f"{self.base_url}/tutorials/batch-predictions/",
            f"{self.base_url}/tutorials/fine-tuning/",
            f"{self.base_url}/tutorials/tool-integrations/",
            f"{self.base_url}/tutorials/uploading-large-files/",
            f"{self.base_url}/tutorials/reliability-check/"
        ]
        return known_urls
    
    async def scrape_page(self, url: str) -> Dict:
        """Async scrape a single documentation page"""
        async with self.semaphore:  # Limit concurrent requests
            try:
                logger.info(f"🔄 Scraping: {url}")
                
                async with self.session.get(url) as response:
                    if response.status == 404:
                        logger.warning(f"❌ 404: {url}")
                        return {'url': url, 'content': '', 'error': '404 Not Found'}
                    
                    response.raise_for_status()
                    html = await response.text()
                
                # Parse with BeautifulSoup
                soup = BeautifulSoup(html, 'html.parser')
                
                # Extract title
                title = soup.find('title')
                title_text = title.text.strip() if title else ""
                
                # Extract main content
                content_selectors = [
                    'main', '.content', '.documentation', '.docs-content',
                    'article', '.markdown-body', '.prose'
                ]
                
                content = None
                for selector in content_selectors:
                    content = soup.select_one(selector)
                    if content:
                        break
                
                if not content:
                    content = soup.find('body')
                
                # Clean and extract text
                if content:
                    # Remove unwanted elements
                    for element in content.find_all(['nav', 'footer', 'aside', '.sidebar', '.navigation', 'script', 'style']):
                        element.decompose()
                    
                    text_content = content.get_text(separator=' ', strip=True)
                    text_content = ' '.join(text_content.split())  # Clean whitespace
                else:
                    text_content = ""
                
                # Extract links for discovery
                nav_links = []
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    if (href.startswith('/') or 'docs.kluster.ai' in href) and not href.startswith('#'):
                        full_url = urljoin(self.base_url, href)
                        if 'docs.kluster.ai' in full_url and not full_url.endswith('.pdf'):
                            nav_links.append(full_url)
                
                logger.info(f"✅ Success: {url} ({len(text_content)} chars)")
                
                return {
                    'url': url,
                    'title': title_text,
                    'content': text_content,
                    'nav_links': nav_links,
                    'scraped_at': time.time()
                }
                
            except asyncio.TimeoutError:
                logger.error(f"⏰ Timeout: {url}")
                return {'url': url, 'content': '', 'error': 'Timeout'}
            except Exception as e:
                logger.error(f"💥 Error scraping {url}: {str(e)}")
                return {'url': url, 'content': '', 'error': str(e)}
    
    async def discover_urls_iterative(self, start_url: str) -> Set[str]:
        """Iterative URL discovery like sync version but async"""
        logger.info(f"🔍 Starting iterative discovery from: {start_url}")
        
        urls_to_visit = {start_url}
        discovered_urls = set()
        
        # Iterative discovery with more rounds
        round_num = 0
        while urls_to_visit and len(discovered_urls) < 100 and round_num < 5:  # Multiple rounds
            round_num += 1
            current_batch = list(urls_to_visit)
            urls_to_visit.clear()
            
            logger.info(f"🔍 Discovery round {round_num}: {len(current_batch)} URLs")
            
            # Scrape current batch
            tasks = [self.scrape_page(url) for url in current_batch]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results and find new URLs
            for result in results:
                if isinstance(result, dict):
                    url = result.get('url')
                    if url:
                        discovered_urls.add(url)
                    
                    # Add newly discovered links for next round
                    for link in result.get('nav_links', []):
                        if (link not in discovered_urls and 
                            'docs.kluster.ai' in link and 
                            not link.endswith('.pdf') and 
                            not link.endswith('.zip')):
                            urls_to_visit.add(link)
            
            await asyncio.sleep(0.1)  # Small delay between rounds
        
        logger.info(f"🎯 Discovered {len(discovered_urls)} URLs in {round_num} rounds")
        return discovered_urls
    
    async def scrape_all_docs_async(self, start_url: str = None) -> Dict:
        """Async scrape all documentation - MEGA EFFICIENT! 🚀"""
        if not start_url:
            start_url = f"{self.base_url}/get-started/get-api-key/"
        
        start_time = time.time()
        logger.info(f"🚀 ASYNC scraping starting from: {start_url}")
        
        # Start with known URLs + comprehensive discovery
        known_urls = set(self.get_all_known_urls())
        discovered_urls = await self.discover_urls_iterative(start_url)
        
        # Combine all URLs
        all_urls = known_urls.union(discovered_urls)
        unique_urls = list(all_urls)
        
        logger.info(f"📊 Found {len(unique_urls)} unique URLs to scrape")
        logger.info(f"  - Known URLs: {len(known_urls)}")
        logger.info(f"  - Discovered URLs: {len(discovered_urls)}")
        
        # Create batches for concurrent processing
        batch_size = self.max_concurrent
        batches = [unique_urls[i:i + batch_size] for i in range(0, len(unique_urls), batch_size)]
        
        scraped_data = {}
        successful_scrapes = 0
        
        # Initialize scraped_data if we got some during discovery
        scraped_data = {}
        for url in unique_urls:
            if url in discovered_urls:
                # We might already have this data from discovery
                continue
        
        # Create batches for final scraping
        batch_size = self.max_concurrent
        batches = [unique_urls[i:i + batch_size] for i in range(0, len(unique_urls), batch_size)]
        
        for i, batch in enumerate(batches, 1):
            logger.info(f"🎯 Processing batch {i}/{len(batches)} ({len(batch)} URLs)")
            
            # Create tasks for this batch
            tasks = [self.scrape_page(url) for url in batch]
            
            # Execute batch concurrently
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            for result in batch_results:
                if isinstance(result, dict) and result.get('content') and len(result['content']) > 50:
                    scraped_data[result['url']] = result
                    successful_scrapes += 1
        
        elapsed = time.time() - start_time
        logger.info(f"🎉 ASYNC scraping complete! {successful_scrapes} pages in {elapsed:.2f}s")
        if elapsed > 0:
            logger.info(f"⚡ Speed: {successful_scrapes/elapsed:.1f} pages/second")
        
        # Add any data we collected during discovery
        final_data = {}
        for url, data in scraped_data.items():
            if data.get('content') and len(data['content']) > 50:
                final_data[url] = data
        
        logger.info(f"📊 Final dataset: {len(final_data)} pages with content")
        return final_data
    
    def extract_topics_and_content(self, scraped_data: Dict) -> Dict:
        """Extract topics, subtopics, and their content - same as sync version"""
        topics_content = {}
        
        for url, page_data in scraped_data.items():
            if not page_data.get('content'):
                continue
                
            # Extract topic/subtopic from URL path
            path = urlparse(url).path
            path_parts = [p for p in path.split('/') if p and p != 'docs']
            
            if len(path_parts) >= 1:
                # Better topic mapping based on URL structure
                if 'get-started' in path:
                    if 'verify' in path:
                        topic = '🛡️ Verify & Reliability'
                    elif 'fine-tuning' in path:
                        topic = '🎯 Fine-tuning'
                    else:
                        topic = '🚀 Getting Started'
                elif 'api-reference' in path:
                    topic = '⚙️ API Reference'
                elif 'tutorials' in path:
                    topic = '📈 Use Cases & Tutorials'
                else:
                    topic = f"🛠️ {path_parts[0].replace('-', ' ').title()}"
                
                # Create meaningful subtopic names
                if len(path_parts) > 1:
                    subtopic_raw = path_parts[-1] if path_parts[-1] not in ['overview', 'api'] else path_parts[-2]
                    subtopic = subtopic_raw.replace('-', ' ').title()
                    
                    # Special cases for better naming
                    special_names = {
                        'api-key': 'API Key Setup',
                        'openai-compatibility': 'OpenAI Compatibility',
                        'start-building': 'Start Building',
                        'dedicated-deployments': 'Dedicated Deployments',
                        'reliability': 'Reliability Checks',
                        'dedicated-api': 'Dedicated API',
                        'text-classification': 'Text Classification',
                        'sentiment-analysis': 'Sentiment Analysis',
                        'keyword-extraction': 'Keyword Extraction',
                        'image-analysis': 'Image Analysis',
                        'llm-evaluation': 'LLM Evaluation',
                        'prompt-engineering': 'Prompt Engineering',
                        'batch-predictions': 'Batch Predictions',
                        'tool-integrations': 'Tool Integrations',
                        'uploading-large-files': 'Large File Upload',
                        'reliability-check': 'Reliability Check'
                    }
                    
                    subtopic = special_names.get(subtopic_raw, subtopic)
                else:
                    subtopic = topic.replace('🚀 ', '').replace('⚙️ ', '').replace('📈 ', '').replace('🛡️ ', '').replace('🎯 ', '')
                
                if topic not in topics_content:
                    topics_content[topic] = {}
                
                topics_content[topic][subtopic] = {
                    'url': url,
                    'title': page_data.get('title', ''),
                    'content': page_data.get('content', ''),
                    'summary': page_data.get('content', '')[:400] + "..." if len(page_data.get('content', '')) > 400 else page_data.get('content', '')
                }
        
        return topics_content
    
    async def save_docs_async(self, filename: str = "kluster_docs.json"):
        """Async save scraped documentation to JSON file"""
        scraped_data = await self.scrape_all_docs_async()
        topics_content = self.extract_topics_and_content(scraped_data)
        
        docs_data = {
            'scraped_at': time.time(),
            'total_pages': len(scraped_data),
            'topics': topics_content,
            'raw_data': scraped_data
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(docs_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"💾 Documentation saved to {filename}")
        logger.info(f"📊 Total pages scraped: {len(scraped_data)}")
        logger.info(f"📁 Topics found: {list(topics_content.keys())}")
        for topic, subtopics in topics_content.items():
            logger.info(f"  {topic}: {len(subtopics)} subtopics")
        
        return docs_data

# Async wrapper functions
async def update_docs_async():
    """Async update documentation by scraping kluster.ai docs"""
    async with AsyncKlusterDocsScaper(max_concurrent=15) as scraper:  # 15 concurrent = ULTRA FAST! 
        return await scraper.save_docs_async()

def update_docs_fast():
    """Sync wrapper for async scraping - MEGA EFFICIENT!"""
    return asyncio.run(update_docs_async())

def load_docs(filename: str = "kluster_docs.json") -> Dict:
    """Load documentation from JSON file"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.warning(f"Documentation file {filename} not found")
        return None
    except json.JSONDecodeError:
        logger.error(f"Error decoding {filename}")
        return None

def update_docs():
    """Alias for update_docs_fast for compatibility"""
    return update_docs_fast()

if __name__ == "__main__":
    # Test the MEGA EFFICIENT async scraper
    asyncio.run(update_docs_async())