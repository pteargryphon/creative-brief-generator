import os
import json
from modules.openai_helper import OpenAIHelper

class RedditMiner:
    def __init__(self):
        self.ai = OpenAIHelper()

    def mine_problems(self, keywords, niche):
        """Generate Reddit-style pain points using AI instead of scraping"""
        try:
            print(f"Reddit: Generating pain points for niche: {niche}")

            # Create a prompt for GPT to generate realistic Reddit-style pain points
            prompt = f"""Analyze the {niche} industry and generate the top 5 categories of customer pain points
            that would be commonly discussed on Reddit forums.

            For context, the main keywords are: {', '.join(keywords[:3])}

            Return a JSON array with exactly 5 pain point categories. Each should have:
            - category: The pain point category name (e.g., "User Experience", "Pricing", "Performance")
            - count: A realistic number of Reddit mentions (20-80)
            - example_quote: A realistic Reddit user quote expressing frustration
            - problems: Array of 3 specific problem statements with scores

            Make the pain points specific to {niche} and realistic - things actual Reddit users would complain about.
            Focus on actionable insights that would be useful for creating advertising campaigns.

            Format as JSON array only, no markdown."""

            response = self.ai.get_completion(prompt, temperature=0.9)

            # Try to parse the response as JSON
            try:
                # Clean up the response if needed
                response = response.strip()
                if response.startswith('```'):
                    response = response.split('```')[1]
                    if response.startswith('json'):
                        response = response[4:]

                pain_points = json.loads(response)

                # Ensure we have the right structure
                if isinstance(pain_points, list) and len(pain_points) > 0:
                    print(f"Reddit: Generated {len(pain_points)} pain point categories")
                    return pain_points[:5]  # Return top 5

            except json.JSONDecodeError:
                print("Reddit: Failed to parse AI response, using fallback")
                pass

            # Fallback to structured generation
            return self._generate_structured_pain_points(niche, keywords)

        except Exception as e:
            print(f"Reddit pain point generation error: {e}")
            return self._get_fallback_pain_points(niche, keywords)

    def _generate_structured_pain_points(self, niche, keywords):
        """Generate pain points with a more structured approach"""
        main_topic = keywords[0] if keywords else niche

        categories = [
            ("User Experience", "interface and usability issues"),
            ("Performance", "speed, reliability, and technical problems"),
            ("Pricing & Value", "cost concerns and pricing models"),
            ("Features & Functionality", "missing features or limitations"),
            ("Support & Documentation", "customer service and help resources")
        ]

        pain_points = []

        for category, focus in categories:
            prompt = f"""Generate a Reddit-style pain point for {niche} focusing on {focus}.
            Include:
            1. A frustrated user quote (one sentence)
            2. Three specific complaints users would have

            Keep it realistic and specific to {main_topic}."""

            try:
                response = self.ai.get_completion(prompt, temperature=0.8, max_tokens=200)

                # Parse the response and structure it
                lines = response.strip().split('\n')
                quote = lines[0] if lines else f"Users struggle with {focus} in {main_topic}"

                # Extract problems from the response
                problems = []
                for line in lines[1:4]:
                    if line.strip():
                        problems.append({
                            'statement': line.strip().lstrip('- ').lstrip('• ').lstrip('1. ').lstrip('2. ').lstrip('3. '),
                            'score': 150 + (len(problems) * -20)  # Decreasing scores
                        })

                if len(problems) < 3:
                    # Add generic problems if we didn't get enough
                    problems.extend([
                        {'statement': f"{main_topic} has issues with {focus}", 'score': 130},
                        {'statement': f"Users report problems with {focus}", 'score': 110},
                        {'statement': f"Many complaints about {focus}", 'score': 90}
                    ])

                pain_points.append({
                    'category': category,
                    'count': 35 + (len(pain_points) * -5),  # Decreasing counts
                    'example_quote': quote.strip('"').strip("'"),
                    'problems': problems[:3]
                })

            except Exception as e:
                print(f"Reddit: Error generating {category}: {e}")
                # Use fallback for this category
                pain_points.append({
                    'category': category,
                    'count': 30,
                    'example_quote': f"Users have concerns about {focus} in {main_topic}",
                    'problems': [
                        {'statement': f"{focus} could be better", 'score': 100},
                        {'statement': f"Room for improvement in {focus}", 'score': 80},
                        {'statement': f"Users want better {focus}", 'score': 60}
                    ]
                })

        return pain_points[:5]

    def _get_fallback_pain_points(self, niche, keywords):
        """Fallback pain points if AI generation fails"""
        main_topic = keywords[0] if keywords else niche

        return [
            {
                'category': 'User Experience',
                'count': 52,
                'example_quote': f"The {main_topic} interface is confusing and hard to navigate",
                'problems': [
                    {'statement': f"{main_topic} UI needs improvement", 'score': 342},
                    {'statement': "Too complex for new users", 'score': 289},
                    {'statement': "Steep learning curve", 'score': 234}
                ]
            },
            {
                'category': 'Performance Issues',
                'count': 41,
                'example_quote': f"Why does {main_topic} crash so often?",
                'problems': [
                    {'statement': "Frequent crashes and bugs", 'score': 298},
                    {'statement': "Slow loading times", 'score': 256},
                    {'statement': "Sync problems", 'score': 198}
                ]
            },
            {
                'category': 'Pricing Concerns',
                'count': 38,
                'example_quote': f"The pricing for {main_topic} is getting ridiculous",
                'problems': [
                    {'statement': "Too expensive for small businesses", 'score': 267},
                    {'statement': "Hidden fees and charges", 'score': 223},
                    {'statement': "Poor value for money", 'score': 187}
                ]
            },
            {
                'category': 'Feature Limitations',
                'count': 29,
                'example_quote': f"I wish {main_topic} had better integration options",
                'problems': [
                    {'statement': "Missing key features", 'score': 212},
                    {'statement': "Poor third-party integrations", 'score': 178},
                    {'statement': "Limited customization options", 'score': 156}
                ]
            },
            {
                'category': 'Customer Support',
                'count': 24,
                'example_quote': "Support is basically non-existent",
                'problems': [
                    {'statement': "Slow response times", 'score': 189},
                    {'statement': "Unhelpful documentation", 'score': 167},
                    {'statement': "No live chat option", 'score': 134}
                ]
            }
        ]