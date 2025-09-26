import os
import json
import openai

class AIEngine:
    def __init__(self):
        openai.api_key = os.environ.get('OPENAI_API_KEY')
        self.model = "gpt-3.5-turbo"  # Using GPT-3.5 for cost efficiency
        
    def generate_brief(self, data):
        """Generate complete creative strategy brief"""
        try:
            # Extract data components
            brand = data.get('brand', {})
            competitors = data.get('competitors', [])
            meta_ads = data.get('meta_ads', [])
            reddit_problems = data.get('reddit_problems', [])
            
            # Step 1: Analyze creative trends
            trends = self._analyze_trends(meta_ads)
            
            # Step 2: Identify opportunities
            opportunities = self._find_opportunities(brand, competitors, meta_ads, reddit_problems)
            
            # Step 3: Generate ad concepts
            concepts = self._generate_concepts(brand, trends, opportunities, reddit_problems)
            
            # Compile full brief
            brief = {
                'brand_overview': {
                    'brand_name': brand.get('brand_name', 'Unknown'),
                    'website': brand.get('url', ''),
                    'industry': brand.get('industry', 'Unknown'),
                    'niche': brand.get('niche', 'Unknown'),
                    'usp': brand.get('usp', []),
                    'funnel_type': brand.get('funnel_type', 'Unknown'),
                    'keywords': brand.get('keywords', [])
                },
                'competitors': competitors,
                'meta_advertisers': meta_ads,
                'reddit_problems': reddit_problems,
                'creative_trends': trends,
                'opportunities': opportunities,
                'ad_concepts': concepts
            }
            
            return brief
            
        except Exception as e:
            print(f"AI generation error: {e}")
            return self._get_fallback_brief(data)
    
    def _analyze_trends(self, meta_ads):
        """Analyze creative trends from Meta ads"""
        if not meta_ads:
            return self._get_default_trends()
        
        # Prepare ads data for analysis
        ads_summary = []
        for advertiser in meta_ads[:3]:
            for ad in advertiser.get('top_ads', [])[:3]:
                ads_summary.append({
                    'headline': ad.get('headline', ''),
                    'body': ad.get('body', ''),
                    'cta': ad.get('cta', ''),
                    'days_running': ad.get('days_running', 0)
                })
        
        prompt = f"""Analyze these top-performing Meta ads and identify creative trends:

Ads Data:
{json.dumps(ads_summary, indent=2)}

Provide a JSON response with:
1. headline_patterns - Array of 3-5 common headline patterns/styles
2. visual_themes - Array of 3-5 common visual/design themes
3. cta_styles - Array of 3-5 effective CTA approaches
4. hook_types - Array of 3-5 successful hook strategies

Focus on patterns that appear in long-running, successful ads."""

        try:
            response = openai.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a creative strategist analyzing ad trends. Respond with valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            result = response.choices[0].message.content
            if result.startswith('```json'):
                result = result[7:]
            if result.endswith('```'):
                result = result[:-3]
            
            return json.loads(result.strip())
            
        except Exception as e:
            print(f"Trend analysis error: {e}")
            return self._get_default_trends()
    
    def _find_opportunities(self, brand, competitors, meta_ads, reddit_problems):
        """Identify strategic opportunities"""
        prompt = f"""Based on this competitive analysis, identify strategic opportunities:

Brand: {brand.get('brand_name')}
Industry: {brand.get('industry')}
Niche: {brand.get('niche')}
Current USP: {json.dumps(brand.get('usp', []))}

Competitors: {len(competitors)} analyzed
Common funnel types: {[c.get('funnel_type') for c in competitors[:3]]}

Top Reddit Problems:
{json.dumps([p.get('example_quote') for p in reddit_problems[:3]])}

Current Ad Trends:
- Most ads focus on: [analyze from meta_ads data]
- Common angles: [analyze from meta_ads data]

Provide a JSON response with exactly 3 opportunities:
[
  {{
    "type": "angle|design|funnel",
    "title": "Opportunity title",
    "description": "Why this is a strategic opportunity",
    "implementation": "How to leverage this opportunity"
  }}
]

Focus on gaps in the current market that align with customer pain points."""

        try:
            response = openai.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a strategic marketing consultant. Respond with valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=600
            )
            
            result = response.choices[0].message.content
            if result.startswith('```json'):
                result = result[7:]
            if result.endswith('```'):
                result = result[:-3]
            
            return json.loads(result.strip())
            
        except Exception as e:
            print(f"Opportunity analysis error: {e}")
            return self._get_default_opportunities()
    
    def _generate_concepts(self, brand, trends, opportunities, reddit_problems):
        """Generate 5 ad concepts"""
        # Prepare context
        pain_points = [p.get('example_quote', '') for p in reddit_problems[:3]]
        
        prompt = f"""Generate 5 unique static ad concepts for this brand:

Brand: {brand.get('brand_name')}
Industry: {brand.get('industry')}
Niche: {brand.get('niche')}
USP: {json.dumps(brand.get('usp', []))}

Top Customer Pain Points:
{json.dumps(pain_points)}

Strategic Opportunities:
{json.dumps([opp.get('title') for opp in opportunities[:3]])}

Current Trends to Consider:
{json.dumps(trends.get('headline_patterns', [])[:3])}

Generate exactly 5 ad concepts with this JSON structure:
[
  {{
    "hook_type": "problem|solution|story|comparison|question|statistic",
    "headline": "Compelling headline text",
    "body_copy": "2-3 lines of supporting copy",
    "cta": "Call-to-action button text",
    "visual_direction": "Description of visual style/imagery",
    "rationale": "Why this concept will resonate with the target audience",
    "pain_point_addressed": "Which customer pain point this addresses"
  }}
]

Make each concept unique and aligned with different opportunities/angles."""

        try:
            response = openai.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert copywriter creating high-converting ad concepts. Respond with valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.9,
                max_tokens=1500
            )
            
            result = response.choices[0].message.content
            if result.startswith('```json'):
                result = result[7:]
            if result.endswith('```'):
                result = result[:-3]
            
            concepts = json.loads(result.strip())
            
            # Ensure we have exactly 5 concepts
            if len(concepts) > 5:
                concepts = concepts[:5]
            elif len(concepts) < 5:
                # Generate additional concepts if needed
                additional = 5 - len(concepts)
                for i in range(additional):
                    concepts.append(self._get_default_concept(i))
            
            return concepts
            
        except Exception as e:
            print(f"Concept generation error: {e}")
            return [self._get_default_concept(i) for i in range(5)]
    
    def _get_default_trends(self):
        """Return default trends structure"""
        return {
            'headline_patterns': [
                'Problem-agitation headlines focusing on pain points',
                'Social proof with specific numbers/statistics',
                'Curiosity-driven "secret" or "trick" angles',
                'Time-sensitive urgency with limited offers',
                'Transformation/before-after narratives'
            ],
            'visual_themes': [
                'Before/after comparison imagery',
                'Lifestyle shots showing desired outcome',
                'Product close-ups with key features',
                'User-generated content and testimonials',
                'Bold text overlays on gradient backgrounds'
            ],
            'cta_styles': [
                'Direct action: Shop Now, Get Started',
                'Value-focused: Claim Your Discount, Get 50% Off',
                'Curiosity: Learn More, See How',
                'Urgency: Limited Time, While Supplies Last',
                'Free value: Get Free Guide, Try Free'
            ],
            'hook_types': [
                'Problem identification hooks',
                'Statistical/data hooks',
                'Story-based emotional hooks',
                'Question hooks that create curiosity',
                'Comparison hooks showing superiority'
            ]
        }
    
    def _get_default_opportunities(self):
        """Return default opportunities"""
        return [
            {
                'type': 'angle',
                'title': 'Underserved Pain Point Angle',
                'description': 'Competitors focus on features while customers care about specific outcomes',
                'implementation': 'Create ads that directly address the #1 customer frustration with clear solutions'
            },
            {
                'type': 'design',
                'title': 'Visual Differentiation Opportunity',
                'description': 'Most competitors use similar stock imagery and color schemes',
                'implementation': 'Develop unique visual identity with custom illustrations or authentic user photos'
            },
            {
                'type': 'funnel',
                'title': 'Interactive Funnel Innovation',
                'description': 'Direct purchase funnels dominate but customers want education first',
                'implementation': 'Implement quiz or calculator funnel to provide personalized recommendations'
            }
        ]
    
    def _get_default_concept(self, index):
        """Return a default concept"""
        concepts = [
            {
                'hook_type': 'problem',
                'headline': 'Still Struggling With [Problem]? You\'re Not Alone',
                'body_copy': 'Join thousands who finally found relief with our proven solution. See real results in days, not months.',
                'cta': 'Discover The Solution',
                'visual_direction': 'Split image showing frustrated person transforming to happy/relieved',
                'rationale': 'Acknowledges pain point and offers hope with social proof',
                'pain_point_addressed': 'Feeling alone in their struggle'
            },
            {
                'hook_type': 'statistic',
                'headline': '87% of Users See Results in Just 14 Days',
                'body_copy': 'Clinical studies prove our method works faster than anything else on the market. Try it risk-free.',
                'cta': 'Start Your Trial',
                'visual_direction': 'Clean infographic showing impressive statistics with product shot',
                'rationale': 'Uses specific data to build credibility and set expectations',
                'pain_point_addressed': 'Skepticism about effectiveness'
            },
            {
                'hook_type': 'story',
                'headline': 'How Sarah Finally Overcame [Problem] After 10 Years',
                'body_copy': 'Her secret? A simple 5-minute routine that changed everything. Get her exact method free.',
                'cta': 'Get The Free Guide',
                'visual_direction': 'Authentic photo of relatable person with quote overlay',
                'rationale': 'Personal story creates emotional connection and curiosity',
                'pain_point_addressed': 'Long-term suffering without solution'
            },
            {
                'hook_type': 'question',
                'headline': 'What If You Could [Desired Outcome] in Half the Time?',
                'body_copy': 'Our revolutionary approach is helping people achieve what usually takes months in just weeks.',
                'cta': 'Learn How',
                'visual_direction': 'Time-lapse or clock imagery showing accelerated progress',
                'rationale': 'Plants possibility and appeals to desire for faster results',
                'pain_point_addressed': 'Frustration with slow progress'
            },
            {
                'hook_type': 'comparison',
                'headline': 'Why Smart Shoppers Choose Us Over [Competitor]',
                'body_copy': 'Better quality, lower price, and a guarantee that actually means something. See the difference.',
                'cta': 'Compare Now',
                'visual_direction': 'Side-by-side comparison chart or versus imagery',
                'rationale': 'Positions as superior choice for informed buyers',
                'pain_point_addressed': 'Confusion about best option'
            }
        ]
        
        return concepts[index] if index < len(concepts) else concepts[0]
    
    def _get_fallback_brief(self, data):
        """Return a fallback brief structure"""
        brand = data.get('brand', {})
        
        return {
            'brand_overview': {
                'brand_name': brand.get('brand_name', 'Unknown'),
                'website': brand.get('url', ''),
                'industry': brand.get('industry', 'Unknown'),
                'niche': brand.get('niche', 'Unknown'),
                'usp': brand.get('usp', ['Quality products', 'Great service']),
                'funnel_type': brand.get('funnel_type', 'direct_purchase'),
                'keywords': brand.get('keywords', ['product', 'service'])
            },
            'competitors': data.get('competitors', []),
            'meta_advertisers': data.get('meta_ads', []),
            'reddit_problems': data.get('reddit_problems', []),
            'creative_trends': self._get_default_trends(),
            'opportunities': self._get_default_opportunities(),
            'ad_concepts': [self._get_default_concept(i) for i in range(5)]
        }