# kluster.ai Tweet Generator

Generate compelling tweets to promote kluster.ai's distributed AI platform using AI-powered content generation.

## Features

- **AI-Powered Generation**: Uses kluster.ai's API to generate professional marketing tweets
- **Documentation-Based**: Automatically indexes kluster.ai documentation for accurate content
- **Multiple Options**: Generates 3 tweet variations for each request
- **Customizable**: Adjust tone, audience, and mission for targeted messaging
- **Fast Updates**: Async documentation scraper updates in 3-5 seconds

## Quick Start

### Deploy on Streamlit Cloud

1. Fork this repository
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Deploy your forked repo
4. Add your `KLUSTER_API_KEY` in the Secrets section:
   ```toml
   KLUSTER_API_KEY = "your-api-key-here"
   ```
5. Your app will be live!

### Local Development

1. Clone the repository:
   ```bash
   git clone https://github.com/DrZuzzjen/kluster-x1.git
   cd kluster-x1
   ```

2. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create `.env` file with your API key:
   ```bash
   echo "KLUSTER_API_KEY=your-api-key-here" > .env
   ```

5. Run the app:
   ```bash
   streamlit run streamlit_app.py
   ```

## Usage

1. **Select Model**: Choose from available kluster.ai text generation models
2. **Pick Topic**: Select documentation topic and subtopic
3. **Optional Settings**:
   - Add target audience
   - Choose tone/style
   - Provide example tweet for style matching
   - Add specific mission/focus
4. **Generate**: Click to create 3 tweet options
5. **Copy & Use**: Click copy button to use your favorite tweet

## Architecture

- `streamlit_app.py`: Main Streamlit application
- `prompts.py`: Tweet generation prompts (with/without thinking)
- `async_docs_scraper.py`: Fast async documentation indexer
- `kluster_docs.json`: Pre-scraped documentation cache

## Security

- Never commit API keys to the repository
- Use Streamlit's secrets management for deployment
- API keys should only be set via environment variables

## About kluster.ai

kluster.ai is a distributed AI infrastructure platform offering:
- OpenAI-compatible API
- Reliability checks & hallucination prevention
- Scalable deployments
- 100+ models available

Get your API key at [docs.kluster.ai](https://docs.kluster.ai/get-started/get-api-key/)

## License

This project is licensed under the MIT License - see the LICENSE file for details.