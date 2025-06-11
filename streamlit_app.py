import streamlit as st
import os
from openai import OpenAI
from dotenv import load_dotenv
import json
import time
from async_docs_scraper import load_docs, update_docs, update_docs_fast
from prompts import get_tweet_prompt_with_thinking, get_tweet_prompt_without_thinking

# Load environment variables
load_dotenv()

# Initialize kluster.ai client
@st.cache_resource
def init_kluster_client():
    return OpenAI(
        api_key=os.getenv("KLUSTER_API_KEY"),
        base_url="https://api.kluster.ai/v1"
    )

@st.cache_data(ttl=300)  # Cache for 5 minutes
def fetch_available_models():
    """Fetch available models from kluster.ai API and filter for text models"""
    client = init_kluster_client()
    
    try:
        # Fetch all models
        models_response = client.models.list()
        models_data = models_response.to_dict()
        
        # Filter for text models (exclude image/audio models)
        text_model_keywords = ['llama', 'deepseek', 'mistral', 'qwen', 'gemma', 'gpt', 'claude', 'chat', 'instruct', 'text']
        image_audio_keywords = ['stable-diffusion', 'sdxl', 'flux', 'whisper', 'audio', 'image', 'vision']
        
        text_models = []
        for model in models_data.get('data', []):
            model_id = model['id'].lower()
            
            # Skip if it's an image/audio model
            if any(keyword in model_id for keyword in image_audio_keywords):
                continue
            
            # Include if it has text model keywords or no specific keywords (assume text)
            if any(keyword in model_id for keyword in text_model_keywords) or \
               not any(keyword in model_id for keyword in image_audio_keywords):
                text_models.append(model['id'])
        
        # Sort models for better display
        text_models.sort()
        
        # Default to DeepSeek if available, otherwise first model
        default_model = "deepseek-ai/DeepSeek-V3-0324"
        if default_model not in text_models and text_models:
            default_model = text_models[0]
        
        return text_models, default_model
        
    except Exception as e:
        st.error(f"Error fetching models: {str(e)}")
        # Fallback to known text models
        fallback_models = [
            "deepseek-ai/DeepSeek-V3-0324",
            "klusterai/Meta-Llama-3.1-8B-Instruct-Turbo",
            "klusterai/Meta-Llama-3.3-70B-Instruct-Turbo"
        ]
        return fallback_models, fallback_models[0]

@st.cache_data(ttl=60)  # Cache for 60 seconds to allow updates
def load_topics_from_docs():
    """Load topics and subtopics from scraped documentation"""
    docs_data = load_docs()
    
    if not docs_data or 'topics' not in docs_data:
        # Fallback to hardcoded topics if no docs available
        return {
            "🚀 Getting Started": [
                "API Key Setup",
                "Model Selection", 
                "OpenAI Compatibility",
                "First API Call"
            ],
            "⚙️ Core Features": [
                "Real-time Inferences",
                "Batch Processing",
                "Fine-tuning",
                "Dedicated Deployments"
            ],
            "🔧 Integrations": [
                "LangChain Integration",
                "CrewAI Integration", 
                "Custom Integrations"
            ],
            "📈 Use Cases": [
                "Text Classification",
                "Sentiment Analysis",
                "Keyword Extraction",
                "Image Analysis",
                "LLM Evaluation",
                "Prompt Engineering"
            ],
            "🛠️ Advanced": [
                "Large File Uploads",
                "Reliability Checks",
                "Performance Optimization"
            ]
        }
    
    # Extract topics and subtopics from real docs
    topics = {}
    for topic, subtopics_data in docs_data['topics'].items():
        topics[topic] = list(subtopics_data.keys())
    
    return topics

TONE_OPTIONS = [
    "Professional & Trustworthy",
    "Technical & Detailed", 
    "Problem-Focused & Urgent",
    "Educational & Helpful",
    "Confident & Bold"
]

def get_context_from_docs(topic, subtopic):
    """Get real context from scraped documentation"""
    docs_data = load_docs()
    
    if not docs_data or 'topics' not in docs_data:
        # Fallback context
        context_map = {
            "API Key Setup": "kluster.ai provides simple API key generation through platform.kluster.ai with OpenAI compatibility",
            "Real-time Inferences": "kluster.ai offers high-performance real-time AI inference with adaptive scaling",
            "Reliability Checks": "kluster.ai's Verify tool helps catch AI hallucinations before they reach production",
        }
        return context_map.get(subtopic, f"kluster.ai's {subtopic.lower()} capabilities")
    
    # Get real content from docs
    if topic in docs_data['topics'] and subtopic in docs_data['topics'][topic]:
        subtopic_data = docs_data['topics'][topic][subtopic]
        return subtopic_data.get('summary', subtopic_data.get('content', '')[:500])
    
    return f"kluster.ai's {subtopic.lower()} capabilities"

def generate_tweet(topic, subtopic, audience="", tone="Professional & Trustworthy", example_tweet="", mission="", model="deepseek-ai/DeepSeek-V3-0324"):
    client = init_kluster_client()
    
    # Get context from real docs
    context = get_context_from_docs(topic, subtopic)
    
    # Log context to console
    print("\n" + "="*80)
    print(f"🚀 GENERATING TWEET")
    print("="*80)
    print(f"📍 Topic: {topic}")
    print(f"📍 Subtopic: {subtopic}")
    print(f"🤖 Model: {model}")
    print(f"🎨 Tone: {tone}")
    print(f"📄 Context from docs:\n{context}")
    print("-"*80)
    
    # Check if model supports thinking (DeepSeek R1 models)
    supports_thinking = "deepseek-r1" in model.lower()
    
    # Build prompt using appropriate function
    if supports_thinking:
        prompt = get_tweet_prompt_with_thinking(
            context=context,
            topic=topic,
            subtopic=subtopic,
            tone=tone,
            audience=audience,
            example_tweet=example_tweet,
            mission=mission
        )
    else:
        prompt = get_tweet_prompt_without_thinking(
            context=context,
            topic=topic,
            subtopic=subtopic,
            tone=tone,
            audience=audience,
            example_tweet=example_tweet,
            mission=mission
        )

    # Log the full prompt
    print("\n📝 FULL PROMPT SENT TO MODEL:")
    print("-"*80)
    print(prompt)
    print("="*80 + "\n")

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150,
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error generating tweet: {str(e)}"

def main():
    st.set_page_config(
        page_title="kluster.ai Tweet Generator", 
        page_icon="🚀",
        layout="wide"
    )
    
    st.title("🚀 kluster.ai Tweet Generator")
    st.markdown("*Create compelling tweets to promote kluster.ai's AI platform*")
    
    # Check API key
    if not os.getenv("KLUSTER_API_KEY"):
        st.error("⚠️ Please set your KLUSTER_API_KEY in the .env file")
        st.code("KLUSTER_API_KEY=your_key_here")
        return
    
    # Sidebar for inputs
    with st.sidebar:
        st.header("📝 Tweet Configuration")
        
        # Documentation controls
        docs_data = load_docs()
        if docs_data:
            st.success(f"📚 Docs loaded: {docs_data.get('total_pages', 0)} pages")
            st.caption(f"Last updated: {time.ctime(docs_data.get('scraped_at', 0))}")
        else:
            st.warning("📚 No docs loaded - using fallback topics")
        
        col_update, col_fast = st.columns(2)
        with col_update:
            if st.button("🔄 Regular", help="Sequential scraping (slow but proven)"):
                with st.spinner("Scraping docs.kluster.ai..."):
                    try:
                        update_docs()
                        load_topics_from_docs.clear()
                        st.success("Documentation updated!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error updating docs: {str(e)}")
        
        with col_fast:
            if st.button("⚡ FAST Update", help="Super fast async scraping!"):
                with st.spinner("⚡ FAST: Async scraping all pages..."):
                    try:
                        start_time = time.time()
                        update_docs_fast()
                        elapsed = time.time() - start_time
                        load_topics_from_docs.clear()
                        st.success(f"⚡ FAST complete! All pages in {elapsed:.1f}s")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error with fast update: {str(e)}")
        
        st.divider()
        
        # Model selection
        st.subheader("🤖 Model Selection")
        available_models, default_model = fetch_available_models()
        selected_model = st.selectbox(
            "Select AI Model:",
            options=available_models,
            index=available_models.index(default_model) if default_model in available_models else 0,
            help="Choose the AI model to generate tweets"
        )
        
        st.divider()
        
        # Topic selection
        topics = load_topics_from_docs()
        selected_topic = st.selectbox("Select Topic:", list(topics.keys()))
        selected_subtopic = st.selectbox("Select Subtopic:", topics[selected_topic])
        
        # Optional parameters
        st.subheader("Optional Parameters")
        
        example_tweet = st.text_area(
            "Example Tweet URL or Text:", 
            placeholder="Paste a tweet URL or text for style reference",
            height=100
        )
        
        audience = st.text_input(
            "Target Audience:", 
            placeholder="e.g., AI developers, CTOs, ML engineers"
        )
        
        tone = st.selectbox("Tone/Style:", TONE_OPTIONS)
        
        mission = st.text_area(
            "Specific Mission/Focus:", 
            placeholder="e.g., focus on cost savings, emphasize reliability",
            height=80
        )
        
        # Advanced settings placeholder
        # (Removed prompt style selector as it's now handled automatically based on model)
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader(f"📱 Generate Tweets: {selected_topic} → {selected_subtopic}")
        
        if st.button("🎯 Generate 3 Tweet Options", type="primary", use_container_width=True):
            with st.spinner("Generating tweets..."):
                tweets = []
                for i in range(3):
                    tweet = generate_tweet(
                        selected_topic, 
                        selected_subtopic, 
                        audience, 
                        tone, 
                        example_tweet, 
                        mission,
                        selected_model
                    )
                    tweets.append(tweet)
                
                st.session_state.generated_tweets = tweets
        
        # Display generated tweets
        if hasattr(st.session_state, 'generated_tweets'):
            st.subheader("✨ Generated Tweets")
            
            for i, tweet in enumerate(st.session_state.generated_tweets, 1):
                with st.container():
                    st.markdown(f"**Option {i}:**")
                    st.text_area(
                        f"Tweet {i}", 
                        value=tweet,
                        height=120,
                        key=f"tweet_{i}",
                        label_visibility="collapsed"
                    )
                    
                    col_copy, col_chars = st.columns([1, 1])
                    with col_copy:
                        if st.button(f"📋 Copy Tweet {i}", key=f"copy_{i}"):
                            st.success(f"Tweet {i} copied to clipboard!")
                    with col_chars:
                        char_count = len(tweet)
                        color = "green" if char_count <= 280 else "red"
                        st.markdown(f"<span style='color: {color}'>{char_count}/280 chars</span>", unsafe_allow_html=True)
                    
                    st.divider()
        
        # Regenerate button
        if hasattr(st.session_state, 'generated_tweets'):
            if st.button("🔄 Regenerate All Tweets", use_container_width=True):
                with st.spinner("Regenerating tweets..."):
                    tweets = []
                    for i in range(3):
                        tweet = generate_tweet(
                            selected_topic, 
                            selected_subtopic, 
                            audience, 
                            tone, 
                            example_tweet, 
                            mission,
                            selected_model
                        )
                        tweets.append(tweet)
                    
                    st.session_state.generated_tweets = tweets
                    st.rerun()
    
    with col2:
        st.subheader("ℹ️ How it works")
        st.markdown("""
        1. **Select AI Model** from available text models
        2. **Select Topic & Subtopic** from kluster.ai docs
        3. **Add Optional Context:**
           - Example tweet for style
           - Target audience 
           - Preferred tone
           - Specific mission
        4. **Generate 3 Options** with one click
        5. **Copy & Paste** your favorite
        6. **Regenerate** as many times as needed
        """)
        
        st.subheader("📊 Current Selection")
        st.info(f"**Topic:** {selected_topic}\n\n**Subtopic:** {selected_subtopic}")
        
        st.info(f"**Model:** {selected_model}")
        
        if audience:
            st.info(f"**Audience:** {audience}")
        
        st.info(f"**Tone:** {tone}")
        
        st.subheader("⚡ Performance")
        st.markdown("""
        **Regular Update**: Sequential scraping (~30-40s, 41 pages)
        **HYBRID Update**: Sync discovery + Async scraping (~5-8s, 41+ pages)
        
        *Use HYBRID for best of both worlds!* 🚀
        """)

if __name__ == "__main__":
    main()