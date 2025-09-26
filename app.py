from flask import Flask, render_template, request, jsonify
import os
import json
import uuid
from datetime import datetime
import asyncio
from concurrent.futures import ThreadPoolExecutor
import threading
from modules.brand_analyzer import BrandAnalyzer
from modules.competitor_finder import CompetitorFinder
from modules.foreplay_client import ForeplayClient
from modules.reddit_miner import RedditMiner
from modules.ai_engine import AIEngine
from modules.coda_publisher import CodaPublisher
from modules.error_logger import error_logger

# Log startup info
print("Starting app with requests-based OpenAI implementation")
print("Environment: Production on Render")

app = Flask(__name__)

# Store job status in memory (in production, use Redis or database)
job_status = {}
executor = ThreadPoolExecutor(max_workers=4)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/debug')
def debug():
    """Debug endpoint to check API status and errors"""
    debug_info = {
        'api_status': error_logger.check_api_status(),
        'recent_errors': error_logger.get_errors()[-10:],  # Last 10 errors
        'error_count': len(error_logger.get_errors()),
        'environment': {
            'OPENAI_API_KEY': 'Set' if os.environ.get('OPENAI_API_KEY') else 'Not set',
            'FOREPLAY_API_KEY': 'Set' if os.environ.get('FOREPLAY_API_KEY') else 'Not set',
            'APIFY_API_TOKEN': 'Set' if os.environ.get('APIFY_API_TOKEN') else 'Not set',
            'CODA_API_TOKEN': 'Set' if os.environ.get('CODA_API_TOKEN') else 'Not set',
            'CODA_DOC_ID': os.environ.get('CODA_DOC_ID', 'Not set'),
            'CODA_TABLE_ID': os.environ.get('CODA_TABLE_ID', 'Not set')
        }
    }
    return jsonify(debug_info)

@app.route('/api/generate', methods=['POST'])
def generate_brief():
    """Main endpoint to generate creative brief"""
    try:
        data = request.get_json()
        brand_url = data.get('url')
        
        if not brand_url:
            return jsonify({'error': 'URL is required'}), 400
        
        # Create job ID
        job_id = str(uuid.uuid4())
        job_status[job_id] = {
            'status': 'processing',
            'progress': 0,
            'message': 'Initializing...',
            'result': None,
            'error': None,
            'started_at': datetime.now().isoformat()
        }
        
        # Start processing in background
        executor.submit(process_brief, job_id, brand_url)
        
        return jsonify({'job_id': job_id}), 202
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def process_brief(job_id, brand_url):
    """Process the brief generation in background"""
    try:
        # Initialize components
        brand_analyzer = BrandAnalyzer()
        competitor_finder = CompetitorFinder()
        foreplay = ForeplayClient()
        reddit_miner = RedditMiner()
        ai_engine = AIEngine()
        coda_publisher = CodaPublisher()
        
        # Step 1: Analyze brand (15%)
        job_status[job_id]['progress'] = 5
        job_status[job_id]['message'] = 'Analyzing brand website...'
        brand_data = brand_analyzer.analyze(brand_url)
        
        # Step 2: Find competitors (30%)
        job_status[job_id]['progress'] = 20
        job_status[job_id]['message'] = 'Finding competitors...'
        competitors = competitor_finder.find(brand_data)
        
        # Step 3: Get Meta ads (50%)
        job_status[job_id]['progress'] = 35
        job_status[job_id]['message'] = 'Analyzing Meta ads...'
        meta_ads = foreplay.get_top_advertisers(brand_data['keywords'], competitors)
        
        # Step 4: Mine Reddit (65%)
        job_status[job_id]['progress'] = 50
        job_status[job_id]['message'] = 'Mining Reddit for customer problems...'
        reddit_problems = reddit_miner.mine_problems(brand_data['keywords'], brand_data['niche'])
        
        # Step 5: AI Analysis (85%)
        job_status[job_id]['progress'] = 70
        job_status[job_id]['message'] = 'Generating creative strategy...'
        brief = ai_engine.generate_brief({
            'brand': brand_data,
            'competitors': competitors,
            'meta_ads': meta_ads,
            'reddit_problems': reddit_problems
        })
        
        # Step 6: Create Coda doc (100%)
        job_status[job_id]['progress'] = 90
        job_status[job_id]['message'] = 'Creating Coda document...'
        coda_url = coda_publisher.create_doc(brief)
        
        # Complete
        job_status[job_id]['status'] = 'completed'
        job_status[job_id]['progress'] = 100
        job_status[job_id]['message'] = 'Brief generated successfully!'
        job_status[job_id]['result'] = {
            'coda_url': coda_url,
            'brand_name': brand_data.get('brand_name', 'Unknown'),
            'completed_at': datetime.now().isoformat()
        }
        
    except Exception as e:
        error_logger.log_error('process_brief', e, {'job_id': job_id, 'url': brand_url})
        job_status[job_id]['status'] = 'failed'
        job_status[job_id]['error'] = str(e)
        job_status[job_id]['message'] = f'Error: {str(e)}'
        print(f"Process brief error: {e}")

@app.route('/api/status/<job_id>')
def check_status(job_id):
    """Check progress of generation"""
    if job_id not in job_status:
        return jsonify({'error': 'Job not found'}), 404
    
    return jsonify(job_status[job_id])

@app.route('/health')
def health():
    """Health check endpoint for Render"""
    return jsonify({'status': 'healthy'}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)