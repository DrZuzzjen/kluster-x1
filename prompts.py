"""
Simplified prompt templates for kluster.ai tweet generation.
Two types: with thinking (for reasoning models) and without.
"""

def get_tweet_prompt_with_thinking(
    context: str,
    topic: str,
    subtopic: str,
    tone: str,
    audience: str = "",
    example_tweet: str = "",
    mission: str = ""
) -> str:
    """
    For reasoning models like DeepSeek R1 that support thinking tags.
    """
    
    base_context = f"""You are an expert social media strategist for kluster.ai, a distributed AI platform.

<context>
Company: kluster.ai - Distributed AI infrastructure platform
Key features: Reliability checks, OpenAI compatibility, scalable deployments, hallucination prevention

Documentation context:
{context}

Topic focus: {topic} - {subtopic}
Tone: {tone}
{"Audience: " + audience if audience else ""}
{"Mission: " + mission if mission else ""}
{"Reference style: " + example_tweet if example_tweet else ""}
</context>

<think>
I need to create a compelling tweet for kluster.ai. Let me think through this step by step:

1. What's the core message from the documentation context?
2. What pain point does this topic address for the target audience?
3. How can I create a hook that stops scrolling?
4. What's the emotional trigger here?
5. How do I position kluster.ai as the solution?
6. What's the call to action?

kluster.ai's best tweets follow this structure:
- Bold hook (5-10 words)
- Problem amplification (15-25 words) 
- Universal question (10-15 words)
- Solution reveal (20-30 words)
- Clear CTA (5-10 words)

Let me craft something that follows this formula while staying under 280 characters.
</think>

Create a compelling tweet for kluster.ai following the structure above. Focus on emotional impact and urgency. 

Output only the tweet text, nothing else."""

    return base_context


def get_tweet_prompt_without_thinking(
    context: str,
    topic: str,
    subtopic: str,
    tone: str,
    audience: str = "",
    example_tweet: str = "",
    mission: str = ""
) -> str:
    """
    For regular models that don't support thinking tags.
    """
    
    optional_sections = []
    if audience:
        optional_sections.append(f"Target audience: {audience}")
    if mission:
        optional_sections.append(f"Mission: {mission}")
    if example_tweet:
        optional_sections.append(f"Reference style: {example_tweet}")
    
    optional_text = "\n".join(optional_sections)
    if optional_text:
        optional_text = "\n\n" + optional_text
    
    return f"""You are an expert social media strategist for kluster.ai, a distributed AI platform.

Company: kluster.ai - Distributed AI infrastructure platform  
Key features: Reliability checks, OpenAI compatibility, scalable deployments, hallucination prevention

Documentation context:
{context}

Topic focus: {topic} - {subtopic}
Tone: {tone}{optional_text}

Create a compelling tweet following this proven structure:
1. Bold hook (5-10 words) - stop scrolling
2. Problem amplification (15-25 words) - make them feel the pain
3. Universal question (10-15 words) - read their mind
4. Solution reveal (20-30 words) - position kluster.ai 
5. Clear CTA (5-10 words) - drive action

Requirements:
- Maximum 280 characters
- No hashtags or emojis unless essential
- Focus on emotional impact and urgency
- Make it feel like urgent insider information

Output only the tweet text, nothing else."""