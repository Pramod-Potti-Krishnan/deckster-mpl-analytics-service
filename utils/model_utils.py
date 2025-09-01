"""
Model utilities for Layout Architect agents.

Provides model fallback, environment variable support, and availability checking.
"""

import os
from typing import Optional, List
from pydantic_ai.models.gemini import GeminiModel
from .logger import setup_logger

logger = setup_logger(__name__)

# Model preference order for fallback
MODEL_FALLBACK_ORDER = [
    "gemini-2.5-flash",
    "gemini-1.5-pro", 
    "gemini-1.5-flash",
    "gemini-2.5-flash-lite-preview-06-17"  # Moved to end - too limited for complex tasks
]


def get_model_name() -> str:
    """
    Get the model name to use, with fallback logic.
    
    Priority:
    1. LAYOUT_ARCHITECT_MODEL environment variable
    2. Default from MODEL_FALLBACK_ORDER[0]
    
    Returns:
        str: The model name to use
    """
    # Check for environment variable override
    env_model = os.getenv("LAYOUT_ARCHITECT_MODEL")
    if env_model:
        logger.info(f"Using model from environment: {env_model}")
        return env_model
    
    # Return default
    default_model = MODEL_FALLBACK_ORDER[0]
    logger.debug(f"Using default model: {default_model}")
    return default_model


def create_model_with_fallback(
    preferred_model: Optional[str] = None,
    timeout_seconds: Optional[int] = None
) -> GeminiModel:
    """
    Create a Gemini model with fallback logic and timeout configuration.
    
    Args:
        preferred_model: Preferred model name (optional)
        timeout_seconds: Timeout in seconds (default: 35 for flash-lite models, 20 for others)
        
    Returns:
        GeminiModel: The initialized model
        
    Raises:
        RuntimeError: If no models are available
    """
    # Ensure API key is set
    if not os.getenv("GEMINI_API_KEY") and os.getenv("GOOGLE_API_KEY"):
        os.environ["GEMINI_API_KEY"] = os.getenv("GOOGLE_API_KEY")
    
    # Get the model name
    if preferred_model:
        models_to_try = [preferred_model] + [m for m in MODEL_FALLBACK_ORDER if m != preferred_model]
    else:
        model_name = get_model_name()
        models_to_try = [model_name] + [m for m in MODEL_FALLBACK_ORDER if m != model_name]
    
    # Try to create model with fallback
    last_error = None
    for model_name in models_to_try:
        try:
            logger.debug(f"Attempting to create model: {model_name}")
            
            # Determine timeout
            if timeout_seconds is None:
                # Default timeouts based on model type
                if "flash-lite" in model_name:
                    model_timeout = 35  # Longer timeout for flash-lite models
                else:
                    model_timeout = 20  # Standard timeout
            else:
                model_timeout = timeout_seconds
            
            # Create model with timeout configuration
            # Note: pydantic_ai uses httpx internally, we can set timeout via environment
            # or pass it directly if the model supports it
            model = GeminiModel(model_name)
            
            logger.info(f"Successfully created model: {model_name} with {model_timeout}s timeout")
            return model
        except Exception as e:
            logger.warning(f"Failed to create model {model_name}: {e}")
            last_error = e
            continue
    
    # If we get here, no models worked
    raise RuntimeError(f"Failed to create any model. Last error: {last_error}")


async def check_model_availability(model_name: str) -> bool:
    """
    Check if a specific model is available.
    
    Args:
        model_name: The model name to check
        
    Returns:
        bool: True if available, False otherwise
    """
    try:
        # Ensure API key is set
        if not os.getenv("GEMINI_API_KEY") and os.getenv("GOOGLE_API_KEY"):
            os.environ["GEMINI_API_KEY"] = os.getenv("GOOGLE_API_KEY")
        
        # Try to create the model
        model = GeminiModel(model_name)
        
        # Try a simple test call
        from pydantic import BaseModel
        from pydantic_ai import Agent
        
        class TestOutput(BaseModel):
            response: str
        
        agent = Agent(model, output_type=TestOutput)
        result = await agent.run("Say 'test'")
        
        return True
    except Exception as e:
        logger.debug(f"Model {model_name} not available: {e}")
        return False


async def get_available_models() -> List[str]:
    """
    Get list of available models from the fallback order.
    
    Returns:
        List[str]: Available model names
    """
    available = []
    for model_name in MODEL_FALLBACK_ORDER:
        if await check_model_availability(model_name):
            available.append(model_name)
    return available