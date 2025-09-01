"""
Analytics Conductor V2
======================

LLM-powered chart selection with playbook rules and fallback strategies.
Intelligently selects the best chart type based on user intent and data characteristics.

Author: Analytics Agent System V2
Date: 2024
Version: 2.0
"""

import logging
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from pydantic_ai import Agent

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.model_utils import create_model_with_fallback
from .models import (
    AnalyticsRequest, ChartType, GenerationMethod,
    ChartPlan, DataSource, SyntheticDataConfig, ThemeConfig
)
from .analytics_playbook import (
    ANALYTICS_PLAYBOOK_V2,
    get_chart_spec,
    get_chart_when_to_use,
    find_charts_for_intent,
    get_chart_synthetic_features
)

logger = logging.getLogger(__name__)


class ChartSelection(BaseModel):
    """Result of LLM chart selection."""
    primary_chart: str = Field(description="Primary chart type from playbook")
    secondary_chart: Optional[str] = Field(None, description="Fallback chart if primary fails")
    reasoning: str = Field(description="Why this chart was selected")
    confidence: float = Field(0.8, description="Confidence in selection (0-1)")
    data_characteristics: List[str] = Field(default_factory=list, description="Key data characteristics")
    matched_rules: List[str] = Field(default_factory=list, description="Playbook rules that matched")


class AnalyticsConductor:
    """
    Intelligent conductor for chart selection using LLM and playbook rules.
    """
    
    def __init__(self):
        """Initialize the conductor."""
        self.agent = self._create_agent()
        self.playbook = ANALYTICS_PLAYBOOK_V2
    
    def _create_agent(self) -> Agent:
        """Create LLM agent for chart selection."""
        return Agent(
            create_model_with_fallback("gemini-2.0-flash-exp"),
            result_type=ChartSelection,
            system_prompt="""You are an expert data visualization consultant.
            Your role is to select the most appropriate chart type based on:
            1. The user's analytics request and intent
            2. The data characteristics described
            3. The analytics playbook rules
            
            You have access to 23 chart types:
            - Line, Step, Area, Stacked Area (trends)
            - Bar (vertical/horizontal), Grouped Bar, Stacked Bar (comparisons)
            - Histogram, Box Plot, Violin Plot (distributions)
            - Scatter, Bubble, Hexbin (correlations)
            - Pie, Waterfall, Funnel (composition)
            - Radar, Heatmap (multi-dimensional comparison)
            - Error Bar, Control Chart, Pareto (statistical)
            - Gantt (project timeline)
            
            Consider:
            - What story the user wants to tell
            - The type and structure of data
            - Visual effectiveness for the use case
            - Provide a fallback option when possible
            
            Be specific about WHY you chose each chart type."""
        )
    
    async def select_chart(self, request: AnalyticsRequest) -> ChartPlan:
        """
        Select the best chart type for the request.
        
        Args:
            request: Analytics request
            
        Returns:
            Chart execution plan
        """
        logger.info(f"Selecting chart for: {request.content[:100]}...")
        
        try:
            # Get LLM selection if chart not specified
            if request.chart_preference:
                # User specified a chart type
                selection = ChartSelection(
                    primary_chart=request.chart_preference.value,
                    secondary_chart=None,
                    reasoning="User specified chart type",
                    confidence=1.0,
                    data_characteristics=[],
                    matched_rules=[]
                )
            else:
                # Use LLM to select chart
                selection = await self._get_llm_selection(request)
            
            # Build execution plan
            plan = self._build_plan(selection, request)
            
            logger.info(f"Selected {selection.primary_chart} with {selection.confidence:.0%} confidence")
            logger.debug(f"Reasoning: {selection.reasoning}")
            
            return plan
            
        except Exception as e:
            logger.error(f"Chart selection failed: {e}")
            return self._get_fallback_plan(request)
    
    async def _get_llm_selection(self, request: AnalyticsRequest) -> ChartSelection:
        """Get chart selection from LLM."""
        
        # Build context with playbook information
        playbook_context = self._build_playbook_context()
        
        prompt = f"""
        Analyze this analytics request and select the best chart type:
        
        REQUEST:
        Content: {request.content}
        Title: {request.title or 'No title'}
        Has User Data: {request.data is not None and len(request.data) > 0}
        
        PLAYBOOK RULES:
        {playbook_context}
        
        Select the most appropriate chart type based on:
        1. What the user wants to visualize
        2. The data structure (if provided) or expected structure
        3. The story they want to tell
        
        Provide:
        - Primary chart type (must be from the 23 available types)
        - Secondary chart as fallback (different from primary)
        - Clear reasoning for your selection
        - Confidence level (0-1)
        - Key data characteristics you identified
        - Which playbook rules matched your selection
        """
        
        try:
            result = await self.agent.run(prompt)
            selection = result.data
            
            # Validate chart types
            selection.primary_chart = self._normalize_chart_type(selection.primary_chart)
            if selection.secondary_chart:
                selection.secondary_chart = self._normalize_chart_type(selection.secondary_chart)
            
            return selection
            
        except Exception as e:
            logger.error(f"LLM selection failed: {e}")
            # Fallback to rule-based selection
            return self._rule_based_selection(request)
    
    def _build_playbook_context(self) -> str:
        """Build context string from playbook."""
        context_lines = []
        
        for chart_type, spec in self.playbook["charts"].items():
            when_to_use = spec.get("when_to_use", [])
            if when_to_use:
                context_lines.append(f"{chart_type}:")
                for rule in when_to_use[:3]:  # Top 3 rules
                    context_lines.append(f"  - {rule}")
        
        return "\n".join(context_lines)
    
    def _normalize_chart_type(self, chart_name: str) -> str:
        """Normalize chart type name to match enum."""
        # Remove spaces and convert to lowercase
        normalized = chart_name.lower().replace(" ", "_").replace("-", "_")
        
        # Common mappings
        mappings = {
            "bar": "bar_chart_vertical",
            "bar_vertical": "bar_chart_vertical",
            "bar_horizontal": "bar_chart_horizontal",
            "line": "line_chart",
            "area": "area_chart",
            "stacked_area": "stacked_area_chart",
            "scatter": "scatter_plot",
            "bubble": "bubble_chart",
            "box": "box_plot",
            "violin": "violin_plot",
            "pie": "pie_chart",
            "radar": "radar_chart",
            "grouped_bar": "grouped_bar_chart",
            "stacked_bar": "stacked_bar_chart",
            "error_bar": "error_bar_chart",
            "control": "control_chart"
        }
        
        # Check mappings
        if normalized in mappings:
            return mappings[normalized]
        
        # Check if it's already valid
        if normalized in self.playbook["charts"]:
            return normalized
        
        # Default fallback
        logger.warning(f"Unknown chart type: {chart_name}, defaulting to bar chart")
        return "bar_chart_vertical"
    
    def _rule_based_selection(self, request: AnalyticsRequest) -> ChartSelection:
        """Fallback rule-based chart selection."""
        content_lower = request.content.lower()
        
        # Keywords for different chart types
        rules = [
            (["trend", "over time", "timeline", "growth", "decline"], "line_chart"),
            (["distribution", "frequency", "histogram", "spread"], "histogram"),
            (["correlation", "relationship", "vs", "versus"], "scatter_plot"),
            (["composition", "breakdown", "parts", "percentage", "%"], "pie_chart"),
            (["comparison", "compare", "ranking", "top", "bottom"], "bar_chart_vertical"),
            (["process", "funnel", "conversion", "pipeline"], "funnel"),
            (["project", "gantt", "schedule", "timeline", "tasks"], "gantt"),
            (["heatmap", "matrix", "grid"], "heatmap"),
            (["radar", "spider", "web", "multi-dimensional"], "radar_chart"),
            (["waterfall", "bridge", "incremental"], "waterfall"),
            (["box", "quartile", "outlier", "statistical"], "box_plot"),
            (["violin", "density", "distribution shape"], "violin_plot"),
            (["bubble", "three dimension", "3d"], "bubble_chart"),
            (["error", "confidence", "uncertainty"], "error_bar_chart"),
            (["control", "process", "limits", "monitoring"], "control_chart"),
            (["pareto", "80/20", "cumulative"], "pareto"),
            (["stacked", "cumulative", "composition over time"], "stacked_area_chart"),
            (["grouped", "side by side", "multiple series"], "grouped_bar_chart")
        ]
        
        # Find matching rule
        for keywords, chart_type in rules:
            if any(keyword in content_lower for keyword in keywords):
                return ChartSelection(
                    primary_chart=chart_type,
                    secondary_chart="bar_chart_vertical",
                    reasoning=f"Matched keywords: {', '.join(k for k in keywords if k in content_lower)}",
                    confidence=0.7,
                    data_characteristics=["rule-based selection"],
                    matched_rules=keywords
                )
        
        # Default to bar chart
        return ChartSelection(
            primary_chart="bar_chart_vertical",
            secondary_chart="line_chart",
            reasoning="No specific patterns detected, defaulting to bar chart",
            confidence=0.5,
            data_characteristics=["generic"],
            matched_rules=[]
        )
    
    def _build_plan(self, selection: ChartSelection, request: AnalyticsRequest) -> ChartPlan:
        """Build execution plan from selection."""
        
        # Determine chart type enum
        try:
            chart_type = ChartType(selection.primary_chart)
        except ValueError:
            # Map to enum
            chart_type = self._map_to_chart_enum(selection.primary_chart)
        
        # Determine fallback
        fallback_chart = None
        if selection.secondary_chart:
            try:
                fallback_chart = ChartType(selection.secondary_chart)
            except ValueError:
                fallback_chart = self._map_to_chart_enum(selection.secondary_chart)
        
        # Get chart spec
        chart_spec = get_chart_spec(selection.primary_chart)
        
        # Determine generation method
        if chart_spec and chart_spec.get("renderer") == "mermaid":
            generation_method = GenerationMethod.MERMAID
        else:
            generation_method = GenerationMethod.PYTHON_MCP
        
        # Get data configuration
        synthetic_features = get_chart_synthetic_features(selection.primary_chart) or {}
        data_config = {
            "num_points": synthetic_features.get("rows", 12),
            "pattern": synthetic_features.get("pattern", "random"),
            "distribution": synthetic_features.get("distribution", "normal"),
            "noise_level": synthetic_features.get("noise_level", 0.1)
        }
        
        # Determine data source
        if request.data and len(request.data) > 0:
            data_source = DataSource.USER_PROVIDED
        else:
            data_source = DataSource.SYNTHETIC
        
        # Build plan
        plan = ChartPlan(
            chart_type=chart_type,
            generation_method=generation_method,
            data_source=data_source,
            data_config=data_config,
            theme=request.theme or ThemeConfig(),  # Use provided theme or default
            confidence=selection.confidence,
            reasoning=selection.reasoning,
            fallback_chart=fallback_chart
        )
        
        return plan
    
    def _map_to_chart_enum(self, chart_name: str) -> ChartType:
        """Map chart name to ChartType enum."""
        # Normalize name
        normalized = self._normalize_chart_type(chart_name)
        
        # Try to map to enum
        enum_mapping = {
            "line_chart": ChartType.LINE_CHART,
            "step_chart": ChartType.STEP_CHART,
            "area_chart": ChartType.AREA_CHART,
            "stacked_area_chart": ChartType.STACKED_AREA_CHART,
            "bar_chart_vertical": ChartType.BAR_VERTICAL,
            "bar_chart_horizontal": ChartType.BAR_HORIZONTAL,
            "grouped_bar_chart": ChartType.GROUPED_BAR,
            "stacked_bar_chart": ChartType.STACKED_BAR,
            "histogram": ChartType.HISTOGRAM,
            "box_plot": ChartType.BOX_PLOT,
            "violin_plot": ChartType.VIOLIN_PLOT,
            "scatter_plot": ChartType.SCATTER_PLOT,
            "bubble_chart": ChartType.BUBBLE_CHART,
            "hexbin": ChartType.HEXBIN,
            "pie_chart": ChartType.PIE_CHART,
            "waterfall": ChartType.WATERFALL,
            "funnel": ChartType.FUNNEL,
            "radar_chart": ChartType.RADAR_CHART,
            "heatmap": ChartType.HEATMAP,
            "error_bar_chart": ChartType.ERROR_BAR,
            "control_chart": ChartType.CONTROL_CHART,
            "pareto": ChartType.PARETO,
            "gantt": ChartType.GANTT
        }
        
        return enum_mapping.get(normalized, ChartType.BAR_VERTICAL)
    
    def _get_fallback_plan(self, request: AnalyticsRequest) -> ChartPlan:
        """Get fallback plan when selection fails."""
        logger.warning("Using fallback plan")
        
        return ChartPlan(
            chart_type=ChartType.BAR_VERTICAL,
            generation_method=GenerationMethod.PYTHON_MCP,
            data_source=DataSource.SYNTHETIC if not request.data else DataSource.USER_PROVIDED,
            data_config={
                "num_points": 8,
                "pattern": "random",
                "distribution": "uniform"
            },
            theme=request.theme or ThemeConfig(),
            confidence=0.3,
            reasoning="Fallback to bar chart due to selection failure",
            fallback_chart=ChartType.LINE_CHART
        )
    
    async def validate_selection(self, plan: ChartPlan, request: AnalyticsRequest) -> bool:
        """
        Validate that the selected chart is appropriate.
        
        Args:
            plan: Chart execution plan
            request: Original request
            
        Returns:
            True if valid, False otherwise
        """
        # Check if chart type is supported
        chart_spec = get_chart_spec(plan.chart_type.value)
        if not chart_spec:
            logger.error(f"Chart type {plan.chart_type} not in playbook")
            return False
        
        # Check data requirements
        data_requirements = chart_spec.get("data_requirements", [])
        
        # If user provided data, validate structure
        if request.data and len(request.data) > 0:
            sample_data = request.data[0]
            
            for req in data_requirements:
                if req.get("required", False):
                    role = req["role"]
                    
                    # Check for required fields
                    if role == "x" and "x" not in sample_data and "label" not in sample_data:
                        logger.warning(f"Missing required x-axis data for {plan.chart_type}")
                        return False
                    
                    if role == "y" and "y" not in sample_data and "value" not in sample_data:
                        logger.warning(f"Missing required y-axis data for {plan.chart_type}")
                        return False
        
        return True
    
    def get_chart_metadata(self, chart_type: ChartType) -> Dict[str, Any]:
        """Get metadata about a chart type."""
        chart_spec = get_chart_spec(chart_type.value)
        
        if not chart_spec:
            return {
                "name": chart_type.value,
                "category": "unknown",
                "renderer": "matplotlib",
                "when_to_use": [],
                "supports_theme": True
            }
        
        return {
            "name": chart_spec.get("name", chart_type.value),
            "category": chart_spec.get("category", "general"),
            "renderer": chart_spec.get("renderer", "matplotlib"),
            "when_to_use": chart_spec.get("when_to_use", []),
            "supports_theme": chart_spec.get("theme_config", {}) != {},
            "data_requirements": chart_spec.get("data_requirements", []),
            "max_series": chart_spec.get("data_requirements", [{}])[0].get("max", 10)
        }