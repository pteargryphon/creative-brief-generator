# Creative Brief Generator

A web application that generates comprehensive creative strategy briefs for brands, analyzing competitors, Meta ads, Reddit discussions, and creating ad concepts - all delivered to a Coda document.

**Latest Update (January 2025):** Now powered by GPT-5-mini for enhanced analysis with better cost efficiency.

## Features

- 🔍 **Brand Analysis**: Automatically analyzes brand websites to extract industry, niche, USP, and funnel types
- 🏆 **Competitor Research**: Finds and analyzes top 5 competitors in the space
- 📱 **Meta Ads Intelligence**: Retrieves top-performing ads via Foreplay API
- 💬 **Reddit Mining**: Discovers customer pain points from Reddit discussions
- 🤖 **AI-Powered Strategy**: Uses GPT-5-mini (latest model) to generate creative trends, opportunities, and ad concepts
- 🔧 **Production-Ready**: Custom OpenAI implementation bypasses proxy issues in cloud environments
- 📊 **Advanced Debugging**: Comprehensive error tracking with Coda integration
- 📄 **Coda Integration**: Outputs everything to a beautifully formatted Coda document

## Quick Start

### Prerequisites

- Python 3.11+
- API Keys for:
  - OpenAI (GPT-5 access - August 2025 release)
  - Foreplay (Meta ads data)
  - Apify (Reddit scraping)
  - Coda (document creation)

### Local Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/creative-brief-generator.git
   cd creative-brief-generator
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env and add your API keys
   ```

5. **Run locally**
   ```bash
   python app.py
   ```
   Visit `http://localhost:5000`

## Deployment to Render

### One-Click Deploy

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

### Manual Deployment

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Initial commit"
   git push origin main
   ```

2. **Create Render Account**
   - Sign up at [render.com](https://render.com)

3. **Create New Web Service**
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Render will auto-detect the `render.yaml` configuration

4. **Add Environment Variables**
   In Render dashboard, add:
   - `OPENAI_API_KEY`
   - `FOREPLAY_API_KEY`
   - `APIFY_API_TOKEN`
   - `CODA_API_TOKEN`
   - `CODA_DOC_TEMPLATE_ID` (optional)
   - `SERP_API_KEY` (optional)

5. **Deploy**
   - Click "Create Web Service"
   - Your app will be available at: `https://creative-brief-generator.onrender.com`

## Usage

1. **Enter Brand URL**: Input the brand's website URL
2. **Click Generate**: The system will start analyzing
3. **Monitor Progress**: Watch real-time progress updates
4. **Access Brief**: Click the Coda link to view your comprehensive brief

## API Keys Setup

### OpenAI
1. Get API key from [platform.openai.com](https://platform.openai.com)
2. Ensure you have GPT-5 access (models available: gpt-5, gpt-5-mini, gpt-5-nano)
3. The system uses gpt-5-mini by default for optimal performance/cost balance

### Foreplay
1. Sign up at [foreplay.co](https://foreplay.co)
2. Access API documentation for your key

### Apify
1. Create account at [apify.com](https://apify.com)
2. Get API token from Account Settings
3. Free tier includes 5,000 credits/month

### Coda
1. Get API token from [coda.io/account](https://coda.io/account)
2. Create a template doc (optional)
3. Note the template doc ID if using one

**Default Coda Configuration:**
- Document ID: `TeddWcsh5U`
- Table ID: `grid-XSXEqW-PnP`
- The system can read from and write to this Coda table via the API
- **Debug Columns**: The table includes:
  - `Debug_Errors`: Comprehensive error logging
  - `API_Status`: Track API response statuses
  - `Processing_Time`: Performance metrics

## Cost Estimates

Per brief generation:
- OpenAI GPT-5-mini: ~$0.50-1.00 (more efficient than GPT-4)
- Apify: ~200 credits (free tier)
- Foreplay: Included in subscription
- **Total: ~$0.50-1.00 per brief** (50% cost reduction from GPT-4)

## Project Structure

```
creative-brief-generator/
├── app.py                    # Main Flask application
├── templates/
│   └── index.html           # Web interface
├── static/
│   ├── style.css           # Styling
│   └── script.js           # Frontend JavaScript
├── modules/
│   ├── brand_analyzer.py   # Website scraping
│   ├── competitor_finder.py # Competitor research
│   ├── foreplay_client.py  # Meta ads API
│   ├── reddit_miner.py     # Reddit scraping
│   ├── ai_engine.py        # GPT-5 analysis
│   ├── coda_publisher.py   # Coda integration
│   ├── openai_helper.py    # Custom OpenAI implementation (bypasses proxy issues)
│   └── error_logger.py     # Comprehensive error tracking
├── requirements.txt         # Python dependencies
├── render.yaml             # Render config
└── README.md              # This file
```

## Technical Implementation Details

### Custom OpenAI Integration

The system uses a custom `openai_helper.py` module that:
- **Bypasses proxy issues** in Render and other cloud environments
- **Uses requests library** directly instead of OpenAI SDK (avoids httpx conflicts)
- **Optimized for GPT-5**: Automatically configures GPT-5-specific parameters:
  - `reasoning_effort`: Controls computational intensity (default: 'low' for speed)
  - `verbosity`: Controls response detail (default: 'medium')
  - Note: GPT-5 doesn't use `max_tokens` parameter

### Error Handling

Comprehensive error tracking system:
- All errors logged to Coda table's `Debug_Errors` column
- API response statuses tracked in `API_Status` column
- Processing times recorded for performance monitoring
- Detailed error context preserved for debugging

## Troubleshooting

### Common Issues

**"Failed to start generation"**
- Check that all API keys are correctly set
- Ensure the brand URL is accessible

**"Brief generation failed"**
- Verify API quotas haven't been exceeded
- Check Render logs for specific errors

**Slow generation**
- Reddit scraping can take 30-60 seconds
- Free tier Render may spin down after inactivity

**"Unsupported parameter: max_tokens" error**
- This occurs with GPT-5 models
- The system automatically handles this by omitting max_tokens for GPT-5

**OpenAI proxy errors in Render**
- The custom `openai_helper.py` module bypasses this issue
- Uses requests library instead of OpenAI SDK

### Logs

View logs in Render dashboard or locally:
```bash
tail -f app.log
```

## Development

### Running Tests
```bash
python -m pytest tests/
```

### Adding New Features

1. Create feature branch
2. Add module in `modules/`
3. Update `app.py` to integrate
4. Test locally
5. Deploy to Render

## Support

For issues or questions:
- Open an issue on GitHub
- Check logs in Render dashboard
- Verify API keys are active

## License

MIT License - see LICENSE file for details

## Recent Updates

### January 2025
- **GPT-5 Integration**: Upgraded to GPT-5-mini for better performance and lower costs
- **Proxy Issue Resolution**: Custom OpenAI implementation bypasses Render environment conflicts
- **Enhanced Debugging**: Added comprehensive error logging to Coda table
- **Performance Tracking**: Added processing time metrics

## Acknowledgments

- OpenAI for GPT-5 (August 2025 release)
- Foreplay for Meta ads data
- Apify for Reddit scraping
- Coda for document platform
- Render for hosting

---

Built with ❤️ for marketers and creative strategists