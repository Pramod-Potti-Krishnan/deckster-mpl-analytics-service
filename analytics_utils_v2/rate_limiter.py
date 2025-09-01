"""
Rate Limiter V2
===============

Handles API rate limiting with exponential backoff and request queuing.
Designed for Gemini API (10 requests/minute) and other rate-limited services.

Author: Analytics Agent System V2
Date: 2024
Version: 2.0
"""

import asyncio
import time
import logging
from typing import Any, Callable, Optional, Dict
from collections import deque
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class RateLimiter:
    """
    Rate limiter with exponential backoff and request tracking.
    """
    
    def __init__(
        self,
        requests_per_minute: int = 10,
        requests_per_hour: Optional[int] = None,
        requests_per_day: Optional[int] = None
    ):
        """
        Initialize rate limiter.
        
        Args:
            requests_per_minute: Maximum requests per minute
            requests_per_hour: Maximum requests per hour (optional)
            requests_per_day: Maximum requests per day (optional)
        """
        self.rpm = requests_per_minute
        self.rph = requests_per_hour
        self.rpd = requests_per_day
        
        # Calculate minimum delay between requests
        self.min_delay = 60.0 / requests_per_minute if requests_per_minute > 0 else 0
        
        # Request history for tracking
        self.request_times = deque(maxlen=max(requests_per_minute, requests_per_hour or 0, requests_per_day or 0))
        
        # Lock for thread safety
        self.lock = asyncio.Lock()
        
        # Statistics
        self.stats = {
            "total_requests": 0,
            "rate_limit_hits": 0,
            "total_wait_time": 0,
            "last_request_time": None
        }
    
    async def acquire(self):
        """
        Acquire permission to make a request.
        Waits if necessary to respect rate limits.
        """
        async with self.lock:
            now = time.time()
            
            # Check minute limit
            if self.rpm > 0:
                minute_ago = now - 60
                recent_requests = [t for t in self.request_times if t > minute_ago]
                
                if len(recent_requests) >= self.rpm:
                    # Need to wait
                    wait_time = 60 - (now - recent_requests[0])
                    if wait_time > 0:
                        logger.info(f"Rate limit: waiting {wait_time:.1f}s (minute limit)")
                        self.stats["rate_limit_hits"] += 1
                        self.stats["total_wait_time"] += wait_time
                        await asyncio.sleep(wait_time)
                        now = time.time()
            
            # Check hour limit
            if self.rph and self.rph > 0:
                hour_ago = now - 3600
                hourly_requests = [t for t in self.request_times if t > hour_ago]
                
                if len(hourly_requests) >= self.rph:
                    wait_time = 3600 - (now - hourly_requests[0])
                    if wait_time > 0:
                        logger.info(f"Rate limit: waiting {wait_time:.1f}s (hour limit)")
                        self.stats["rate_limit_hits"] += 1
                        self.stats["total_wait_time"] += wait_time
                        await asyncio.sleep(wait_time)
                        now = time.time()
            
            # Check day limit
            if self.rpd and self.rpd > 0:
                day_ago = now - 86400
                daily_requests = [t for t in self.request_times if t > day_ago]
                
                if len(daily_requests) >= self.rpd:
                    wait_time = 86400 - (now - daily_requests[0])
                    if wait_time > 0:
                        logger.info(f"Rate limit: waiting {wait_time:.1f}s (day limit)")
                        self.stats["rate_limit_hits"] += 1
                        self.stats["total_wait_time"] += wait_time
                        await asyncio.sleep(wait_time)
                        now = time.time()
            
            # Ensure minimum delay between requests
            if self.stats["last_request_time"]:
                elapsed = now - self.stats["last_request_time"]
                if elapsed < self.min_delay:
                    wait_time = self.min_delay - elapsed
                    logger.debug(f"Minimum delay: waiting {wait_time:.1f}s")
                    await asyncio.sleep(wait_time)
                    now = time.time()
            
            # Record this request
            self.request_times.append(now)
            self.stats["last_request_time"] = now
            self.stats["total_requests"] += 1
    
    async def execute_with_retry(
        self,
        func: Callable,
        *args,
        max_retries: int = 3,
        initial_backoff: float = 60.0,
        **kwargs
    ) -> Any:
        """
        Execute function with rate limiting and exponential backoff.
        
        Args:
            func: Async function to execute
            max_retries: Maximum number of retries
            initial_backoff: Initial backoff time in seconds
            
        Returns:
            Result from function
        """
        last_error = None
        
        for attempt in range(max_retries):
            try:
                # Acquire rate limit permission
                await self.acquire()
                
                # Execute function
                result = await func(*args, **kwargs)
                return result
                
            except Exception as e:
                error_str = str(e)
                last_error = e
                
                # Check if it's a rate limit error
                if any(indicator in error_str.lower() for indicator in ['429', 'rate', 'quota', 'limit']):
                    backoff_time = initial_backoff * (2 ** attempt)  # Exponential backoff
                    logger.warning(f"Rate limit error on attempt {attempt + 1}/{max_retries}, waiting {backoff_time}s")
                    self.stats["rate_limit_hits"] += 1
                    await asyncio.sleep(backoff_time)
                else:
                    # Non-rate-limit error, propagate immediately
                    raise
        
        # All retries exhausted
        logger.error(f"Max retries ({max_retries}) exceeded")
        raise last_error or Exception("Max retries exceeded")
    
    async def batch_execute(
        self,
        tasks: list,
        batch_size: int = 5,
        batch_delay: float = 30.0
    ) -> list:
        """
        Execute multiple tasks in batches with delays.
        
        Args:
            tasks: List of async functions to execute
            batch_size: Number of tasks per batch
            batch_delay: Delay between batches in seconds
            
        Returns:
            List of results
        """
        results = []
        
        for i in range(0, len(tasks), batch_size):
            batch = tasks[i:i + batch_size]
            
            # Execute batch with rate limiting
            batch_tasks = []
            for task in batch:
                # Each task will acquire rate limit permission
                batch_tasks.append(self.execute_with_retry(task))
            
            # Wait for batch to complete
            batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
            results.extend(batch_results)
            
            # Wait between batches if not the last batch
            if i + batch_size < len(tasks):
                logger.info(f"Batch {i//batch_size + 1} complete, waiting {batch_delay}s before next batch")
                await asyncio.sleep(batch_delay)
        
        return results
    
    def get_stats(self) -> Dict[str, Any]:
        """Get rate limiter statistics."""
        return {
            **self.stats,
            "current_rpm": len([t for t in self.request_times if t > time.time() - 60]),
            "requests_in_queue": len(self.request_times)
        }
    
    def reset_stats(self):
        """Reset statistics."""
        self.stats = {
            "total_requests": 0,
            "rate_limit_hits": 0,
            "total_wait_time": 0,
            "last_request_time": None
        }
    
    def can_make_request(self) -> bool:
        """
        Check if a request can be made without waiting.
        
        Returns:
            True if request can be made immediately
        """
        now = time.time()
        
        # Check minute limit
        if self.rpm > 0:
            minute_ago = now - 60
            recent_requests = [t for t in self.request_times if t > minute_ago]
            if len(recent_requests) >= self.rpm:
                return False
        
        # Check minimum delay
        if self.stats["last_request_time"]:
            elapsed = now - self.stats["last_request_time"]
            if elapsed < self.min_delay:
                return False
        
        return True
    
    def get_wait_time(self) -> float:
        """
        Get estimated wait time before next request can be made.
        
        Returns:
            Wait time in seconds (0 if can make request now)
        """
        if self.can_make_request():
            return 0
        
        now = time.time()
        wait_times = []
        
        # Check minute limit
        if self.rpm > 0:
            minute_ago = now - 60
            recent_requests = [t for t in self.request_times if t > minute_ago]
            if len(recent_requests) >= self.rpm:
                wait_times.append(60 - (now - recent_requests[0]))
        
        # Check minimum delay
        if self.stats["last_request_time"]:
            elapsed = now - self.stats["last_request_time"]
            if elapsed < self.min_delay:
                wait_times.append(self.min_delay - elapsed)
        
        return max(wait_times) if wait_times else 0


class APIRateLimiter:
    """
    Specialized rate limiter for specific APIs.
    """
    
    # Preset configurations for common APIs
    PRESETS = {
        "gemini": {
            "requests_per_minute": 10,
            "requests_per_hour": None,
            "requests_per_day": None
        },
        "openai": {
            "requests_per_minute": 60,
            "requests_per_hour": None,
            "requests_per_day": 10000
        },
        "anthropic": {
            "requests_per_minute": 50,
            "requests_per_hour": None,
            "requests_per_day": None
        }
    }
    
    @classmethod
    def create(cls, api_name: str) -> RateLimiter:
        """
        Create rate limiter for specific API.
        
        Args:
            api_name: Name of API (gemini, openai, anthropic)
            
        Returns:
            Configured RateLimiter instance
        """
        if api_name in cls.PRESETS:
            config = cls.PRESETS[api_name]
            logger.info(f"Creating rate limiter for {api_name} API")
            return RateLimiter(**config)
        else:
            logger.warning(f"Unknown API {api_name}, using default rate limits")
            return RateLimiter(requests_per_minute=10)


# Global rate limiter instance for convenience
_global_limiter = None


def get_global_rate_limiter(api_name: str = "gemini") -> RateLimiter:
    """
    Get or create global rate limiter instance.
    
    Args:
        api_name: API to configure for
        
    Returns:
        Global RateLimiter instance
    """
    global _global_limiter
    if _global_limiter is None:
        _global_limiter = APIRateLimiter.create(api_name)
    return _global_limiter


async def rate_limited(func: Callable, *args, **kwargs) -> Any:
    """
    Convenience function to execute with global rate limiter.
    
    Args:
        func: Async function to execute
        
    Returns:
        Result from function
    """
    limiter = get_global_rate_limiter()
    return await limiter.execute_with_retry(func, *args, **kwargs)