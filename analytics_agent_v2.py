"""
Analytics Agent V2
==================

Enhanced analytics generation system with comprehensive chart support.
Features LLM-enhanced data, theme customization, and robust error handling.

Author: Analytics Agent System V2
Date: 2024
Version: 2.0
"""

import logging
import time
import json
from typing import Dict, Any, Optional, List
from datetime import datetime

from analytics_utils_v2.models import (
    AnalyticsRequest, AnalyticsResponse, ChartMetadata,
    ChartType, GenerationMethod, DataSource, ThemeConfig,
    ChartPlan, ChartData, DataStatistics
)
from analytics_utils_v2.conductor import AnalyticsConductor
from analytics_utils_v2.data_manager import DataManager
from analytics_utils_v2.theme_engine import ThemeEngine
from analytics_utils_v2.python_chart_agent import PythonChartAgent
from analytics_utils_v2.mcp_executor import MCPExecutor
from analytics_utils_v2.rate_limiter import get_global_rate_limiter
from analytics_utils_v2.file_utils import save_analytics_output, create_output_package
from analytics_utils_v2.axis_mapper import get_axis_labels, infer_axis_from_content

logger = logging.getLogger(__name__)


class AnalyticsAgentV2:
    """
    Main orchestrator for analytics generation v2.
    Coordinates all components for chart creation.
    """
    
    def __init__(self, mcp_tool=None, api_name: str = "gemini"):
        """
        Initialize the analytics agent.
        
        Args:
            mcp_tool: Optional MCP tool for code execution
            api_name: API name for rate limiting configuration
        """
        # Initialize components
        self.conductor = AnalyticsConductor()
        self.data_manager = DataManager()
        self.mcp_executor = MCPExecutor(mcp_tool)
        self.python_agent = PythonChartAgent(self.mcp_executor)
        self.rate_limiter = get_global_rate_limiter(api_name)
        
        # Statistics
        self.stats = {
            "total_requests": 0,
            "successful_charts": 0,
            "failed_charts": 0,
            "chart_types": {},
            "data_sources": {"user": 0, "synthetic": 0},
            "average_generation_time": 0
        }
        
        logger.info("Analytics Agent V2 initialized")
    
    async def generate(self, request: AnalyticsRequest) -> AnalyticsResponse:
        """
        Generate analytics based on request.
        
        Args:
            request: Analytics request with configuration
            
        Returns:
            Analytics response with chart and data
        """
        start_time = time.time()
        self.stats["total_requests"] += 1
        
        try:
            # Step 1: Select chart type with conductor
            logger.info(f"Processing request: {request.content[:100]}...")
            plan = await self._select_chart_with_rate_limit(request)
            
            # Step 2: Get or generate data
            logger.info(f"Getting data (source: {plan.data_source.value})")
            data_points, data_source, statistics = await self._get_data_with_rate_limit(
                request, plan.chart_type
            )
            
            # Update stats
            self.stats["data_sources"][data_source.value] += 1
            
            # Step 3: Generate chart
            logger.info(f"Generating {plan.chart_type.value} chart")
            chart_result = await self._generate_chart(
                plan, data_points, request.title or "Analytics Chart"
            )
            
            # Step 4: Format data for response
            chart_data = self.data_manager.format_data_for_chart(data_points, plan.chart_type)
            
            # Step 5: Build response
            generation_time = (time.time() - start_time) * 1000  # Convert to ms
            
            if chart_result["success"]:
                self.stats["successful_charts"] += 1
                self.stats["chart_types"][plan.chart_type.value] = \
                    self.stats["chart_types"].get(plan.chart_type.value, 0) + 1
                
                # Get axis labels and types for the chart
                x_label, y_label, x_type, y_type = get_axis_labels(plan.chart_type)
                
                # Try to infer better labels from content
                inferred_x, inferred_y = infer_axis_from_content(request.content, plan.chart_type)
                if inferred_x != x_label:
                    x_label = inferred_x
                if inferred_y != y_label:
                    y_label = inferred_y
                
                # Use request title or generate one
                chart_title = request.title or self._generate_default_title(request.content, plan.chart_type)
                
                metadata = ChartMetadata(
                    chart_type=plan.chart_type,
                    generation_method=plan.generation_method,
                    data_source=data_source,
                    theme_applied=plan.theme,
                    insights=self._generate_insights(data_points, statistics),
                    generation_time_ms=generation_time,
                    data_points_count=len(data_points),
                    llm_enhanced=request.enhance_labels,
                    title=chart_title,
                    x_axis_label=x_label,
                    y_axis_label=y_label,
                    x_axis_type=x_type,
                    y_axis_type=y_type
                )
                
                response = AnalyticsResponse(
                    success=True,
                    chart=chart_result.get("chart"),  # Base64 PNG or None
                    data=chart_data,
                    metadata=metadata,
                    python_code=chart_result.get("python_code")
                )
                
                logger.info(f"Successfully generated {plan.chart_type.value} in {generation_time:.0f}ms")
                
            else:
                self.stats["failed_charts"] += 1
                
                # Get axis labels even for failed charts
                x_label, y_label, x_type, y_type = get_axis_labels(plan.chart_type)
                chart_title = request.title or self._generate_default_title(request.content, plan.chart_type)
                
                metadata = ChartMetadata(
                    chart_type=plan.chart_type,
                    generation_method=plan.generation_method,
                    data_source=data_source,
                    theme_applied=plan.theme,
                    generation_time_ms=generation_time,
                    data_points_count=len(data_points),
                    title=chart_title,
                    x_axis_label=x_label,
                    y_axis_label=y_label,
                    x_axis_type=x_type,
                    y_axis_type=y_type
                )
                
                response = AnalyticsResponse(
                    success=False,
                    chart=None,
                    data=chart_data,
                    metadata=metadata,
                    error=chart_result.get("error", "Chart generation failed")
                )
                
                logger.error(f"Failed to generate chart: {chart_result.get('error')}")
            
            # Update average generation time
            self._update_average_time(generation_time)
            
            return response
            
        except Exception as e:
            logger.error(f"Analytics generation failed: {e}")
            self.stats["failed_charts"] += 1
            
            # Get default chart type and axis labels
            default_chart = request.chart_preference or ChartType.BAR_VERTICAL
            x_label, y_label, x_type, y_type = get_axis_labels(default_chart)
            chart_title = request.title or "Analytics Chart"
            
            # Return error response
            metadata = ChartMetadata(
                chart_type=default_chart,
                generation_method=GenerationMethod.FALLBACK,
                data_source=DataSource.SYNTHETIC,
                theme_applied=request.theme or ThemeConfig(),
                generation_time_ms=(time.time() - start_time) * 1000,
                title=chart_title,
                x_axis_label=x_label,
                y_axis_label=y_label,
                x_axis_type=x_type,
                y_axis_type=y_type
            )
            
            return AnalyticsResponse(
                success=False,
                chart=None,
                data=None,
                metadata=metadata,
                error=str(e)
            )
    
    async def _select_chart_with_rate_limit(self, request: AnalyticsRequest) -> ChartPlan:
        """Select chart type with rate limiting."""
        return await self.rate_limiter.execute_with_retry(
            self.conductor.select_chart,
            request
        )
    
    async def _get_data_with_rate_limit(
        self,
        request: AnalyticsRequest,
        chart_type: ChartType
    ) -> tuple:
        """Get data with rate limiting for LLM calls."""
        # Data manager handles its own LLM calls with rate limiting
        return await self.data_manager.get_data(request, chart_type)
    
    async def _generate_chart(
        self,
        plan: ChartPlan,
        data_points: List,
        title: str
    ) -> Dict[str, Any]:
        """Generate chart based on plan."""
        # Check if we should use Mermaid
        if plan.generation_method == GenerationMethod.MERMAID:
            # For now, fall back to Python for all charts
            # TODO: Implement Mermaid agent when needed
            plan.generation_method = GenerationMethod.PYTHON_MCP
        
        # Generate with Python agent
        result = await self.python_agent.generate_chart(plan, data_points, title)
        
        # Handle fallback if primary fails
        if not result["success"] and plan.fallback_chart:
            logger.info(f"Primary chart failed, trying fallback: {plan.fallback_chart.value}")
            plan.chart_type = plan.fallback_chart
            result = await self.python_agent.generate_chart(plan, data_points, title)
        
        return result
    
    def _generate_insights(self, data_points: List, statistics: DataStatistics) -> List[str]:
        """Generate insights from data."""
        insights = []
        
        if statistics:
            # Basic statistics insights
            insights.append(f"Data range: {statistics.min:.1f} to {statistics.max:.1f}")
            insights.append(f"Average value: {statistics.mean:.1f}")
            
            # Spread insight
            if statistics.std > statistics.mean * 0.3:
                insights.append("High variability in data")
            elif statistics.std < statistics.mean * 0.1:
                insights.append("Low variability in data")
            
            # Skewness
            if abs(statistics.mean - statistics.median) > statistics.std * 0.5:
                if statistics.mean > statistics.median:
                    insights.append("Data is right-skewed")
                else:
                    insights.append("Data is left-skewed")
        
        # Data point insights
        if len(data_points) > 0:
            insights.append(f"Total data points: {len(data_points)}")
            
            # Check for trends if time series
            if len(data_points) > 10:
                first_half_avg = sum(p.value for p in data_points[:len(data_points)//2]) / (len(data_points)//2)
                second_half_avg = sum(p.value for p in data_points[len(data_points)//2:]) / (len(data_points) - len(data_points)//2)
                
                if second_half_avg > first_half_avg * 1.1:
                    insights.append("Increasing trend detected")
                elif second_half_avg < first_half_avg * 0.9:
                    insights.append("Decreasing trend detected")
        
        return insights
    
    def _update_average_time(self, generation_time: float):
        """Update average generation time."""
        total = self.stats["successful_charts"] + self.stats["failed_charts"]
        if total > 0:
            current_avg = self.stats["average_generation_time"]
            self.stats["average_generation_time"] = \
                (current_avg * (total - 1) + generation_time) / total
    
    def _generate_default_title(self, content: str, chart_type: ChartType) -> str:
        """Generate a default title based on content and chart type."""
        # Try to extract key phrases from content
        content_lower = content.lower()
        
        # Common patterns
        if "sales" in content_lower:
            return "Sales Analysis"
        elif "revenue" in content_lower:
            return "Revenue Overview"
        elif "performance" in content_lower:
            return "Performance Metrics"
        elif "distribution" in content_lower:
            return "Data Distribution"
        elif "comparison" in content_lower:
            return "Comparative Analysis"
        elif "trend" in content_lower:
            return "Trend Analysis"
        elif "growth" in content_lower:
            return "Growth Analysis"
        elif "quarterly" in content_lower or "q1" in content_lower or "q2" in content_lower:
            return "Quarterly Report"
        elif "monthly" in content_lower:
            return "Monthly Report"
        elif "yearly" in content_lower or "annual" in content_lower:
            return "Annual Report"
        
        # Chart type specific defaults
        chart_defaults = {
            ChartType.PIE_CHART: "Distribution Overview",
            ChartType.LINE_CHART: "Trend Analysis",
            ChartType.BAR_VERTICAL: "Comparative Analysis",
            ChartType.HISTOGRAM: "Frequency Distribution",
            ChartType.SCATTER_PLOT: "Correlation Analysis",
            ChartType.HEATMAP: "Intensity Map",
            ChartType.GANTT: "Project Timeline",
            ChartType.FUNNEL: "Conversion Funnel",
            ChartType.WATERFALL: "Cumulative Analysis"
        }
        
        return chart_defaults.get(chart_type, "Data Visualization")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get agent statistics."""
        total = self.stats["successful_charts"] + self.stats["failed_charts"]
        success_rate = self.stats["successful_charts"] / total * 100 if total > 0 else 0
        
        return {
            **self.stats,
            "success_rate": success_rate,
            "rate_limiter_stats": self.rate_limiter.get_stats()
        }
    
    def reset_stats(self):
        """Reset statistics."""
        self.stats = {
            "total_requests": 0,
            "successful_charts": 0,
            "failed_charts": 0,
            "chart_types": {},
            "data_sources": {"user": 0, "synthetic": 0},
            "average_generation_time": 0
        }
        self.rate_limiter.reset_stats()


# Public API Functions

async def create_analytics_v2(
    content: str,
    title: Optional[str] = None,
    data: Optional[List[Dict[str, Any]]] = None,
    use_synthetic_data: bool = True,
    theme: Optional[Dict[str, Any]] = None,
    chart_type: Optional[str] = None,
    enhance_labels: bool = True,
    mcp_tool=None,
    save_files: bool = False,
    output_dir: str = "analytics_output"
) -> Dict[str, Any]:
    """
    Public API for analytics generation v2.
    
    Args:
        content: Description of analytics needed
        title: Optional chart title
        data: Optional user-provided data
        use_synthetic_data: Generate synthetic data if no user data
        theme: Theme configuration with primary/secondary/tertiary colors
        chart_type: Optional preferred chart type
        enhance_labels: Use LLM to enhance labels
        mcp_tool: Optional MCP tool for code execution
        save_files: Save PNG and JSON files to disk
        output_dir: Directory for saved files
        
    Returns:
        API response dictionary with chart and data
    """
    # Build request
    request = AnalyticsRequest(
        content=content,
        title=title,
        data=data,
        use_synthetic_data=use_synthetic_data,
        theme=ThemeConfig(**theme) if theme else None,
        chart_preference=ChartType(chart_type) if chart_type else None,
        enhance_labels=enhance_labels
    )
    
    # Create agent and generate
    agent = AnalyticsAgentV2(mcp_tool)
    response = await agent.generate(request)
    
    # Convert to API format
    api_response = response.to_api_response()
    
    # Save files if requested
    if save_files and api_response.get('success'):
        saved_files = save_analytics_output(api_response, output_dir)
        api_response['saved_files'] = saved_files
        logger.info(f"Files saved to {output_dir}: {saved_files}")
    
    return api_response


async def batch_create_analytics_v2(
    requests: List[Dict[str, Any]],
    mcp_tool=None,
    batch_size: int = 5,
    batch_delay: float = 30.0
) -> List[Dict[str, Any]]:
    """
    Generate multiple analytics charts in batches.
    
    Args:
        requests: List of request dictionaries
        mcp_tool: Optional MCP tool
        batch_size: Number of charts per batch
        batch_delay: Delay between batches
        
    Returns:
        List of API responses
    """
    agent = AnalyticsAgentV2(mcp_tool)
    
    # Convert to request objects
    request_objects = []
    for req in requests:
        request_objects.append(AnalyticsRequest(
            content=req.get("content", ""),
            title=req.get("title"),
            data=req.get("data"),
            use_synthetic_data=req.get("use_synthetic_data", True),
            theme=ThemeConfig(**req["theme"]) if req.get("theme") else None,
            chart_preference=ChartType(req["chart_type"]) if req.get("chart_type") else None,
            enhance_labels=req.get("enhance_labels", True)
        ))
    
    # Process in batches
    tasks = [agent.generate(req) for req in request_objects]
    results = await agent.rate_limiter.batch_execute(
        tasks,
        batch_size=batch_size,
        batch_delay=batch_delay
    )
    
    # Convert to API format
    return [r.to_api_response() if not isinstance(r, Exception) else 
            {"success": False, "error": str(r)} for r in results]


# Example usage
if __name__ == "__main__":
    import asyncio
    
    async def test_analytics_v2():
        """Test the analytics agent v2."""
        
        # Test 1: Simple chart with synthetic data
        result = await create_analytics_v2(
            content="Show quarterly revenue growth for 2024",
            title="Q1-Q4 2024 Revenue",
            theme={
                "primary": "#1E40AF",
                "secondary": "#10B981",
                "tertiary": "#F59E0B"
            }
        )
        print(f"Test 1 - Success: {result['success']}")
        print(f"Test 1 - Chart type: {result['metadata']['chart_type']}")
        
        # Test 2: Chart with user data
        user_data = [
            {"label": "Q1", "value": 45000},
            {"label": "Q2", "value": 52000},
            {"label": "Q3", "value": 48000},
            {"label": "Q4", "value": 61000}
        ]
        
        result = await create_analytics_v2(
            content="Visualize quarterly performance",
            title="2024 Performance",
            data=user_data,
            chart_type="bar_chart_vertical"
        )
        print(f"Test 2 - Success: {result['success']}")
        print(f"Test 2 - Data source: {result['metadata']['data_source']}")
        
        # Test 3: Complex visualization
        result = await create_analytics_v2(
            content="Create a violin plot showing distribution of customer satisfaction scores by department",
            title="Satisfaction by Department",
            enhance_labels=True
        )
        print(f"Test 3 - Success: {result['success']}")
        if result['success'] and result.get('data'):
            print(f"Test 3 - Data points: {result['data']['count']}")
    
    asyncio.run(test_analytics_v2())