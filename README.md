# Creative Brief Generator

A web application that generates comprehensive creative strategy briefs for brands, analyzing competitors, Meta ads, Reddit discussions, and creating ad concepts - all delivered to a Coda document.

## Features

- 🔍 **Brand Analysis**: Automatically analyzes brand websites to extract industry, niche, USP, and funnel types
- 🏆 **Competitor Research**: Finds and analyzes top 5 competitors in the space
- 📱 **Meta Ads Intelligence**: Retrieves top-performing ads via Foreplay API
- 💬 **Reddit Mining**: Discovers customer pain points from Reddit discussions
- 🤖 **AI-Powered Strategy**: Uses GPT-4 to generate creative trends, opportunities, and ad concepts
- 📄 **Coda Integration**: Outputs everything to a beautifully formatted Coda document

## Quick Start

### Prerequisites

- Python 3.11+
- API Keys for:
  - OpenAI (GPT-4 access)
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
2. Ensure you have GPT-4 access

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

## Cost Estimates

Per brief generation:
- OpenAI GPT-4: ~$1-2
- Apify: ~200 credits (free tier)
- Foreplay: Included in subscription
- **Total: ~$1-2 per brief**

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
│   ├── ai_engine.py        # GPT-4 analysis
│   └── coda_publisher.py   # Coda integration
├── requirements.txt         # Python dependencies
├── render.yaml             # Render config
└── README.md              # This file
```

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

## Acknowledgments

- OpenAI for GPT-4
- Foreplay for Meta ads data
- Apify for Reddit scraping
- Coda for document platform
- Render for hosting

---

Built with ❤️ for marketers and creative strategists