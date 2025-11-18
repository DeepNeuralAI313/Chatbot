import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Pricing per 1M tokens (Gemini 1.5 Flash - as of 2025)
GEMINI_INPUT_COST = 0.075 / 1_000_000  # $0.075 per 1M input tokens
GEMINI_OUTPUT_COST = 0.30 / 1_000_000  # $0.30 per 1M output tokens

def generate_response(system_instructions: str, context: str, user_message: str) -> str:
    """Generate a response using Google Gemini"""
    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        # Combine system instructions, context, and user message
        prompt = f"{system_instructions}\n\nContext: {context}\n\nQuestion: {user_message}"
        
        response = model.generate_content(prompt)
        
        return response.text
    except Exception as e:
        print(f"Error generating response: {e}")
        return "Sorry, an error occurred. Please try again."

def generate_response_with_tokens(system_instructions: str, context: str, user_message: str, memory_context: str = "") -> tuple:
    """Generate a response and return token usage information"""
    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        # Build natural, conversational prompt
        prompt = f"""{system_instructions}

Here's some relevant information that might help you:

{context}
"""
        
        if memory_context:
            prompt += f"""
Our conversation so far:

{memory_context}
"""
        
        prompt += f"""
Now, the user is asking: {user_message}

Remember to write naturally like a human having a conversation - no robotic language or unnecessary lists. Just explain things clearly in flowing paragraphs, the way you'd talk to a friend. Be warm, genuine, and helpful!"""
        
        response = model.generate_content(prompt)
        
        # Extract token usage from response
        # Note: Gemini API provides token counts in usage_metadata
        try:
            prompt_tokens = response.usage_metadata.prompt_token_count
            completion_tokens = response.usage_metadata.candidates_token_count
            total_tokens = response.usage_metadata.total_token_count
        except:
            # Fallback: estimate tokens if metadata not available
            prompt_tokens = len(prompt.split()) * 1.3  # rough estimate
            completion_tokens = len(response.text.split()) * 1.3
            total_tokens = prompt_tokens + completion_tokens
        
        # Calculate cost
        cost = (prompt_tokens * GEMINI_INPUT_COST) + (completion_tokens * GEMINI_OUTPUT_COST)
        
        token_info = {
            "prompt_tokens": int(prompt_tokens),
            "completion_tokens": int(completion_tokens),
            "total_tokens": int(total_tokens),
            "cost": cost
        }
        
        return response.text, token_info
    except Exception as e:
        print(f"Error generating response: {e}")
        return "Sorry, an error occurred. Please try again.", None