import os
import requests
import json
from collections import Counter
import re

class RedditMiner:
    def __init__(self):
        self.apify_token = os.environ.get('APIFY_API_TOKEN')
        self.actor_id = 'trudax~reddit-scraper'  # Apify Reddit Scraper actor - use ~ not /
        print(f"Reddit: Apify token {'found' if self.apify_token else 'not found'} (length: {len(self.apify_token) if self.apify_token else 0})")
        
    def mine_problems(self, keywords, niche):
        """Mine Reddit for customer problems and pain points"""
        try:
            # Re-enable Apify integration with correct actor ID
            if not self.apify_token:
                print("Reddit: No Apify token found, using mock data")
                # Return mock data if no API token
                return self._get_mock_problems(niche)

            print(f"Reddit: Mining problems for keywords: {keywords[:3]}, niche: {niche}")
            
            # Build search queries
            queries = self._build_problem_queries(keywords, niche)
            print(f"Reddit: Built {len(queries)} queries")

            # Collect posts and comments
            all_content = []
            for query in queries[:2]:  # Limit to save credits
                print(f"Reddit: Searching for: '{query}'")
                content = self._search_reddit(query)
                print(f"Reddit: Found {len(content)} results for '{query}'")
                all_content.extend(content)
            
            # Extract problem statements
            problems = self._extract_problems(all_content)
            
            # Categorize and cluster
            categorized = self._categorize_problems(problems)
            
            # Get top 5 pain clusters
            top_clusters = self._get_top_clusters(categorized)
            
            return top_clusters
            
        except Exception as e:
            print(f"Reddit mining error: {e}")
            return self._get_mock_problems(niche)
    
    def _build_problem_queries(self, keywords, niche):
        """Build search queries for finding problems"""
        queries = []
        
        # Problem-focused queries
        problem_terms = ['problem', 'issue', 'struggle', 'frustrated', 'annoying', 'hate', 'wish']
        
        for keyword in keywords[:2]:  # Limit keywords
            for term in problem_terms[:3]:  # Limit terms
                queries.append(f"{keyword} {term}")
        
        # Add niche-specific query
        queries.append(f"{niche} advice help")
        
        return queries
    
    def _search_reddit(self, query):
        """Search Reddit using Apify"""
        try:
            # Apify API endpoint
            url = f"https://api.apify.com/v2/acts/{self.actor_id}/runs"
            
            # Configuration for Reddit Scraper
            payload = {
                "searchBy": "searchTerm",  # Search by keyword
                "searchTerm": query,
                "sort": "relevance",
                "time": "year",  # Last year
                "maxItems": 30,   # Limit results
                "includeComments": True,  # Include comments
                "debugMode": False
            }
            
            headers = {
                'Content-Type': 'application/json',
            }
            
            # Start the actor run
            print(f"Reddit: Starting Apify actor for query '{query}'")
            response = requests.post(
                url,
                json=payload,
                headers=headers,
                params={'token': self.apify_token}
            )
            print(f"Reddit: Apify response status: {response.status_code}")
            
            if response.status_code == 201:
                run_id = response.json()['data']['id']
                
                # Wait for completion and get results
                results = self._get_run_results(run_id)
                return results
                
        except Exception as e:
            print(f"Reddit search error: {e}")
        
        return []
    
    def _get_run_results(self, run_id):
        """Get results from Apify run"""
        try:
            # Poll for completion
            import time
            max_wait = 60  # seconds
            waited = 0
            
            while waited < max_wait:
                # Check run status
                status_url = f"https://api.apify.com/v2/actor-runs/{run_id}"
                response = requests.get(status_url, params={'token': self.apify_token})
                
                if response.status_code == 200:
                    status = response.json()['data']['status']
                    
                    if status == 'SUCCEEDED':
                        # Get dataset
                        dataset_id = response.json()['data']['defaultDatasetId']
                        dataset_url = f"https://api.apify.com/v2/datasets/{dataset_id}/items"
                        
                        results_response = requests.get(
                            dataset_url,
                            params={'token': self.apify_token}
                        )
                        
                        if results_response.status_code == 200:
                            return results_response.json()
                    
                    elif status in ['FAILED', 'ABORTED']:
                        break
                
                time.sleep(5)
                waited += 5
                
        except Exception as e:
            print(f"Error getting results: {e}")
        
        return []
    
    def _extract_problems(self, content):
        """Extract problem statements from content"""
        problems = []
        
        # Patterns for finding problems
        patterns = [
            r"I (?:hate|can't stand|struggle with|have problems? with) (.+?)(?:\.|,|!)",
            r"(?:My biggest|The main) (?:problem|issue|challenge) is (.+?)(?:\.|,|!)",
            r"I wish (?:I could|there was) (.+?)(?:\.|,|!)",
            r"It's (?:so |really )?(?:annoying|frustrating) (?:that|when) (.+?)(?:\.|,|!)",
            r"Why (?:is it so hard|can't I|doesn't) (.+?)(?:\.|,|\?)",
        ]
        
        for item in content:
            text = item.get('text', '')
            
            for pattern in patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                for match in matches:
                    if 10 < len(match) < 200:  # Reasonable length
                        problems.append({
                            'statement': match.strip(),
                            'score': item.get('score', 0),
                            'source': item.get('subreddit', ''),
                            'full_text': text[:500]
                        })
        
        return problems
    
    def _categorize_problems(self, problems):
        """Categorize problems into themes"""
        categories = {
            'cost': ['expensive', 'cost', 'price', 'afford', 'money', 'budget'],
            'quality': ['quality', 'cheap', 'break', 'last', 'durable', 'reliable'],
            'usability': ['hard to use', 'complicated', 'confusing', 'difficult', 'complex'],
            'time': ['takes too long', 'slow', 'time', 'wait', 'quick', 'fast'],
            'support': ['support', 'help', 'customer service', 'response', 'answer'],
            'selection': ['choice', 'option', 'variety', 'find', 'available'],
            'effectiveness': ['work', 'effective', 'result', 'actually', 'really'],
            'other': []
        }
        
        categorized = {cat: [] for cat in categories}
        
        for problem in problems:
            statement = problem['statement'].lower()
            matched = False
            
            for category, keywords in categories.items():
                if category == 'other':
                    continue
                    
                if any(keyword in statement for keyword in keywords):
                    categorized[category].append(problem)
                    matched = True
                    break
            
            if not matched:
                categorized['other'].append(problem)
        
        return categorized
    
    def _get_top_clusters(self, categorized):
        """Get top 5 pain point clusters"""
        clusters = []
        
        for category, problems in categorized.items():
            if not problems:
                continue
                
            # Sort by score
            problems.sort(key=lambda x: x['score'], reverse=True)
            
            # Get top example
            top_example = problems[0]['statement'] if problems else ""
            
            clusters.append({
                'category': category.title(),
                'count': len(problems),
                'example_quote': top_example,
                'problems': problems[:3]  # Top 3 examples
            })
        
        # Sort by count
        clusters.sort(key=lambda x: x['count'], reverse=True)
        
        return clusters[:5]
    
    def _get_enhanced_mock_problems(self, niche, keywords):
        """Return enhanced mock Reddit problems based on niche and keywords"""
        # Generate contextual problems based on the first keyword
        main_topic = keywords[0] if keywords else niche

        return [
            {
                'category': 'User Experience',
                'count': 52,
                'example_quote': f"I struggle with {main_topic} because the interface is so confusing",
                'problems': [
                    {'statement': f"The {main_topic} UI is not intuitive at all", 'score': 342},
                    {'statement': "Too many steps to do simple tasks", 'score': 289},
                    {'statement': "New users get lost immediately", 'score': 234}
                ]
            },
            {
                'category': 'Performance',
                'count': 41,
                'example_quote': f"Why is {main_topic} always so slow and buggy",
                'problems': [
                    {'statement': f"{main_topic} crashes when handling large files", 'score': 298},
                    {'statement': "Loading times are unbearable", 'score': 256},
                    {'statement': "Sync issues happen constantly", 'score': 198}
                ]
            },
            {
                'category': 'Pricing',
                'count': 38,
                'example_quote': f"The cost of {main_topic} services keeps increasing",
                'problems': [
                    {'statement': "Free tier is too limited to be useful", 'score': 267},
                    {'statement': "Pricing jumps are huge between tiers", 'score': 223},
                    {'statement': "Hidden fees everywhere", 'score': 187}
                ]
            },
            {
                'category': 'Integration',
                'count': 29,
                'example_quote': f"I wish {main_topic} worked better with other tools",
                'problems': [
                    {'statement': "Doesn't integrate with my existing workflow", 'score': 212},
                    {'statement': "API limitations are frustrating", 'score': 178},
                    {'statement': "Export options are too restrictive", 'score': 156}
                ]
            },
            {
                'category': 'Support',
                'count': 24,
                'example_quote': "Getting help is nearly impossible",
                'problems': [
                    {'statement': "Support tickets take weeks to get responses", 'score': 189},
                    {'statement': "Documentation is outdated or missing", 'score': 167},
                    {'statement': "Community forums are the only real help", 'score': 134}
                ]
            }
        ]

    def _get_mock_problems(self, niche):
        """Return mock Reddit problems for testing"""
        return [
            {
                'category': 'Quality',
                'count': 47,
                'example_quote': f"I hate how most {niche} products break after just a few months",
                'problems': [
                    {'statement': f"Most {niche} products don't last long enough", 'score': 234},
                    {'statement': "The quality has gone downhill in recent years", 'score': 189},
                    {'statement': "You get what you pay for, and cheap ones are terrible", 'score': 156}
                ]
            },
            {
                'category': 'Cost',
                'count': 35,
                'example_quote': f"Why are good {niche} products so expensive these days",
                'problems': [
                    {'statement': f"Can't afford the high-quality {niche} options", 'score': 201},
                    {'statement': "The price keeps going up but quality stays the same", 'score': 167},
                    {'statement': "Looking for affordable alternatives that actually work", 'score': 143}
                ]
            },
            {
                'category': 'Selection',
                'count': 28,
                'example_quote': "It's so hard to find the right one with so many options",
                'problems': [
                    {'statement': "Too many choices make it impossible to decide", 'score': 178},
                    {'statement': "Wish there was a clear guide on what to buy", 'score': 145},
                    {'statement': "Every review says something different", 'score': 123}
                ]
            },
            {
                'category': 'Support',
                'count': 22,
                'example_quote': "Customer service is non-existent with most brands",
                'problems': [
                    {'statement': "No one responds when you have issues", 'score': 156},
                    {'statement': "The warranty process is a nightmare", 'score': 134},
                    {'statement': "Can't get help when something goes wrong", 'score': 98}
                ]
            },
            {
                'category': 'Effectiveness',
                'count': 18,
                'example_quote': f"Most {niche} products don't actually deliver on their promises",
                'problems': [
                    {'statement': "The marketing promises more than it delivers", 'score': 145},
                    {'statement': "Tried three different brands and none worked", 'score': 112},
                    {'statement': "Beginning to think the whole industry is a scam", 'score': 89}
                ]
            }
        ]