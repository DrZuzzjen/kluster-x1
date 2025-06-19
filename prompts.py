"""
Real kluster.ai tweet generation using actual template and full documentation context.
Dynamically adapts to documentation content without hardcoded bias.
"""

TWEET_EXAMPLES = [
    # Existing example (if present)
    "🚨 Just launched:\nMeet Verify by http://kluster.ai: Out-of-the-box reliability for LLMs.\n\nA drop-in API that flags hallucinations, false claims, and low-quality outputs before they reach users or downstream tools.\n\nNo fine-tuning. No thresholds. No infra changes.\n🔗 https://kluster.ai/verify-by-kluster.ai",
    # New Example 1
    "Deploy AI without fear.\n\nA single hallucination can shatter customer trust or derail critical processes.\n\nEvery AI deployment faces the same critical question: “How do we know when our model gets it wrong?”\n\nIn our latest blog about Verify by http://kluster.ai, our new reliability tool for LLMs, we break down how it helps teams catch mistakes before they reach production.\n\nRead more here: https://bit.ly/45gbcRz",
    # New Example 2
    "The Hugging Face model you need isn’t hosted?\nhttp://kluster.ai lets you run it anyway.\n\nSpin up a private, production-ready endpoint in ~30 mins using Dedicated Deployments.\n\n🧠 https://docs.kluster.ai/get-started/dedicated-deployments/",
    # New Example 3
    "Jupyter notebooks in one click. Hyperbolic keeps you coding, not context switching.\n\nWith our VS @code / @cursor_ai extension, rent a remote H100 GPU and spin up a fully managed Jupyter server on a public URL to run your ML workloads from right inside your editor.\n\nFollow along with @theamrelhady and see comments for install instructions! + [Short Video]",
]

tweet_examples_text = "\n\n---\n\n".join(TWEET_EXAMPLES)

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
    Uses all kluster.ai tweet examples and full documentation context.
    """
    prompt = f"""You are kluster.ai's senior social media strategist. You write tweets that consistently drive signups and engagement.

DOCUMENTATION CONTEXT FOR {topic} - {subtopic}:
{context}

TARGET AUDIENCE: {audience if audience else "AI developers and engineering teams"}
TONE: {tone}
MISSION: {mission if mission else "Convert readers into kluster.ai users"}

KLUSTER.AI TWEET EXAMPLES TO FOLLOW:
{tweet_examples_text}

Take all these examples into consideration to craft the perfect tweet.
Try to reference something from the docs passed as context.

<think>
Let me analyze these kluster.ai tweet structures:

1. ATTENTION GRABBER: Hooks the reader with urgency, novelty, or a bold claim.
2. PRODUCT INTRODUCTION: Clearly introduces a kluster.ai capability or update.
3. BENEFIT EXPLANATION: Describes what it does and why it matters, referencing real pain points.
4. FRICTION REMOVAL: "No [pain point]. No [pain point]. No [pain point]." - Removes objections.
5. CALL TO ACTION: Clean link with branded URL or resource.

Now I need to extract from the documentation context:
- What specific capability/feature should I highlight?
- What pain points does this solve that I can negate with "No X. No Y. No Z."?
- What's the core value proposition that would stop someone scrolling?
- How does this fit kluster.ai's positioning as reliable AI infrastructure?

Looking at the documentation: {context[:500]}...

I should craft this to match kluster.ai's voice - direct, technical but accessible, benefit-focused.
</think>

Using the kluster.ai template structure above, create a tweet about {subtopic} that:

1. Starts with an attention-grabbing opener (emoji or bold statement)
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
    Uses all kluster.ai tweet examples and full documentation context.
    """
    prompt = f"""You are kluster.ai's senior social media strategist. You write tweets that drive signups.

DOCUMENTATION CONTEXT FOR {topic} - {subtopic}:
{context}

TARGET: {audience if audience else "AI developers and engineering teams"}
TONE: {tone}
MISSION: {mission if mission else "Convert readers into kluster.ai users"}

KLUSTER.AI TWEET EXAMPLES TO FOLLOW:
{tweet_examples_text}

Take all these examples into consideration to craft the perfect tweet.
Try to reference something from the docs passed as context.

TEMPLATE STRUCTURE ANALYSIS:
1. ATTENTION: Hooks the reader with urgency, novelty, or a bold claim.
2. INTRO: Clearly introduces a kluster.ai capability or update.
3. BENEFIT: Explains capability and impact based on documentation context.
4. FRICTION REMOVAL: "No [pain]. No [pain]. No [pain]."
5. CTA: Clean branded link or resource.

YOUR TASK:
Create a tweet about {subtopic} using this structure.

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
