"""
Real kluster.ai tweet generation using actual template and full documentation context.
Dynamically adapts to documentation content without hardcoded bias.
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
    For reasoning models that support thinking tags.
    Uses real kluster.ai tweet template and full documentation context.
    """
    
    # Use provided example or kluster.ai template
    template_example = example_tweet if example_tweet else """🚨 Just launched:
Meet Verify by http://kluster.ai: Out-of-the-box reliability for LLMs.

A drop-in API that flags hallucinations, false claims, and low-quality outputs before they reach users or downstream tools.

No fine-tuning. No thresholds. No infra changes.
🔗 https://kluster.ai/verify-by-kluster.ai"""

    prompt = f"""You are kluster.ai's senior social media strategist. You write tweets that consistently drive signups and engagement.

DOCUMENTATION CONTEXT FOR {topic} - {subtopic}:
{context}

TARGET AUDIENCE: {audience if audience else "AI developers and engineering teams"}
TONE: {tone}
MISSION: {mission if mission else "Convert readers into kluster.ai users"}

KLUSTER.AI TWEET TEMPLATE TO FOLLOW:
{template_example}

<think>
Let me analyze this kluster.ai template structure:

1. ATTENTION GRABBER: "🚨 Just launched:" - Creates urgency and novelty
2. PRODUCT INTRODUCTION: "Meet [Product] by http://kluster.ai: [One-line value prop]"
3. BENEFIT EXPLANATION: Clear description of what it does and why it matters
4. FRICTION REMOVAL: "No [pain point]. No [pain point]. No [pain point]." - Removes objections
5. CALL TO ACTION: Clean link with branded URL

Now I need to extract from the documentation context:
- What specific capability/feature should I highlight?
- What pain points does this solve that I can negate with "No X. No Y. No Z."?
- What's the core value proposition that would stop someone scrolling?
- How does this fit kluster.ai's positioning as reliable AI infrastructure?

Looking at the documentation: {context[:500]}...

I should craft this to match kluster.ai's voice - direct, technical but accessible, benefit-focused.
</think>

Using the kluster.ai template structure above, create a tweet about {subtopic} that:

1. Starts with an attention-grabbing opener (emoji + urgency/novelty)
2. Introduces the kluster.ai capability with clear value prop
3. Explains the benefit using insights from the documentation
4. Removes friction with "No X. No Y. No Z." format using real pain points from the docs
5. Ends with a clear call to action

CRITICAL REQUIREMENTS:
- Extract specific details from the documentation context provided
- Use kluster.ai's confident, technical tone
- Focus on the exact capability described in the docs
- Maximum 280 characters
- Include "http://kluster.ai" naturally in the messaging

Output only the tweet text."""

    return prompt


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
    For regular models without thinking capabilities.
    Uses real kluster.ai tweet template and full documentation context.
    """
    
    # Use provided example or kluster.ai template
    template_example = example_tweet if example_tweet else """🚨 Just launched:
Meet Verify by http://kluster.ai: Out-of-the-box reliability for LLMs.

A drop-in API that flags hallucinations, false claims, and low-quality outputs before they reach users or downstream tools.

No fine-tuning. No thresholds. No infra changes.
🔗 https://kluster.ai/verify-by-kluster.ai"""

    prompt = f"""You are kluster.ai's senior social media strategist. You write tweets that drive signups.

DOCUMENTATION CONTEXT FOR {topic} - {subtopic}:
{context}

TARGET: {audience if audience else "AI developers and engineering teams"}
TONE: {tone}
MISSION: {mission if mission else "Convert readers into kluster.ai users"}

PROVEN KLUSTER.AI TWEET TEMPLATE:
{template_example}

TEMPLATE STRUCTURE ANALYSIS:
1. ATTENTION: "🚨 Just launched:" (urgency + novelty)
2. INTRO: "Meet [Product] by http://kluster.ai: [Value prop]"  
3. BENEFIT: Clear explanation of capability and impact
4. FRICTION REMOVAL: "No [pain]. No [pain]. No [pain]."
5. CTA: Clean branded link

YOUR TASK:
Create a tweet about {subtopic} using this exact template structure.

INSTRUCTIONS:
- Mine the documentation context for specific technical details
- Identify real pain points this kluster.ai capability solves
- Use the "No X. No Y. No Z." pattern with actual friction points from docs
- Include "http://kluster.ai" naturally
- Match kluster.ai's confident, technical tone
- Stay under 280 characters
- Focus on business impact, not just features

Extract insights directly from the provided documentation context. Do not add generic claims not supported by the docs.

Output only the tweet text."""

    return prompt