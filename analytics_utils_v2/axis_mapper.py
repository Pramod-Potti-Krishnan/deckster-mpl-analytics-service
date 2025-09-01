"""
Axis Label Mapper for Analytics Charts
======================================

Maps chart types to appropriate axis labels and types.
Provides consistent labeling across all 23 chart types.

Author: Analytics Agent System V2
Date: 2024
Version: 2.0
"""

from typing import Tuple
from .models import ChartType


def get_axis_labels(chart_type: ChartType) -> Tuple[str, str, str, str]:
    """
    Get appropriate axis labels and types for a chart type.
    
    Args:
        chart_type: The type of chart being generated
        
    Returns:
        Tuple of (x_label, y_label, x_type, y_type)
        - x_label: Label for X-axis
        - y_label: Label for Y-axis
        - x_type: Type of X-axis (categorical/numerical/temporal)
        - y_type: Type of Y-axis (numerical/percentage/count)
    """
    
    AXIS_MAPPINGS = {
        # Line and Trend Charts
        ChartType.LINE_CHART: ("Period", "Value", "temporal", "numerical"),
        ChartType.STEP_CHART: ("Time", "Value", "temporal", "numerical"),
        ChartType.AREA_CHART: ("Period", "Value", "temporal", "numerical"),
        ChartType.STACKED_AREA_CHART: ("Period", "Value", "temporal", "numerical"),
        
        # Bar Charts
        ChartType.BAR_VERTICAL: ("Category", "Value", "categorical", "numerical"),
        ChartType.BAR_HORIZONTAL: ("Value", "Category", "numerical", "categorical"),
        ChartType.GROUPED_BAR: ("Category", "Value", "categorical", "numerical"),
        ChartType.STACKED_BAR: ("Category", "Value", "categorical", "numerical"),
        
        # Distribution Charts
        ChartType.HISTOGRAM: ("Value", "Frequency", "numerical", "count"),
        ChartType.BOX_PLOT: ("Category", "Distribution", "categorical", "numerical"),
        ChartType.VIOLIN_PLOT: ("Category", "Distribution", "categorical", "numerical"),
        
        # Correlation Charts
        ChartType.SCATTER_PLOT: ("X Value", "Y Value", "numerical", "numerical"),
        ChartType.BUBBLE_CHART: ("X Value", "Y Value", "numerical", "numerical"),
        ChartType.HEXBIN: ("X Value", "Y Value", "numerical", "numerical"),
        
        # Composition Charts
        ChartType.PIE_CHART: ("Category", "Percentage", "categorical", "percentage"),
        ChartType.WATERFALL: ("Stage", "Change", "categorical", "numerical"),
        ChartType.FUNNEL: ("Stage", "Value", "categorical", "numerical"),
        
        # Comparison Charts
        ChartType.RADAR_CHART: ("Dimension", "Value", "categorical", "numerical"),
        ChartType.HEATMAP: ("X Category", "Y Category", "categorical", "categorical"),
        
        # Statistical Charts
        ChartType.ERROR_BAR: ("Condition", "Measurement", "categorical", "numerical"),
        ChartType.CONTROL_CHART: ("Sample", "Value", "temporal", "numerical"),
        ChartType.PARETO: ("Cause", "Frequency", "categorical", "count"),
        
        # Project Charts
        ChartType.GANTT: ("Task", "Timeline", "categorical", "temporal"),
    }
    
    # Return the mapping or default values
    return AXIS_MAPPINGS.get(chart_type, ("X", "Y", "categorical", "numerical"))


def get_chart_description(chart_type: ChartType) -> str:
    """
    Get a human-readable description of what the chart type is best for.
    
    Args:
        chart_type: The type of chart
        
    Returns:
        Description of the chart type's purpose
    """
    
    CHART_DESCRIPTIONS = {
        ChartType.LINE_CHART: "Shows trends and changes over time",
        ChartType.STEP_CHART: "Shows discrete changes at specific points",
        ChartType.AREA_CHART: "Shows volume/magnitude changes over time",
        ChartType.STACKED_AREA_CHART: "Shows composition changes over time",
        
        ChartType.BAR_VERTICAL: "Compares values across categories",
        ChartType.BAR_HORIZONTAL: "Compares values with long category names",
        ChartType.GROUPED_BAR: "Compares multiple series across categories",
        ChartType.STACKED_BAR: "Shows composition within categories",
        
        ChartType.HISTOGRAM: "Shows distribution of continuous data",
        ChartType.BOX_PLOT: "Shows statistical distribution and outliers",
        ChartType.VIOLIN_PLOT: "Shows distribution shape and density",
        
        ChartType.SCATTER_PLOT: "Shows correlation between two variables",
        ChartType.BUBBLE_CHART: "Shows three-dimensional relationships",
        ChartType.HEXBIN: "Shows density in scatter plot data",
        
        ChartType.PIE_CHART: "Shows proportions of a whole",
        ChartType.WATERFALL: "Shows cumulative effect of changes",
        ChartType.FUNNEL: "Shows progressive reduction through stages",
        
        ChartType.RADAR_CHART: "Compares multiple dimensions",
        ChartType.HEATMAP: "Shows intensity across two dimensions",
        
        ChartType.ERROR_BAR: "Shows variability and confidence intervals",
        ChartType.CONTROL_CHART: "Monitors process stability over time",
        ChartType.PARETO: "Shows most significant factors (80/20 rule)",
        
        ChartType.GANTT: "Shows project timeline and dependencies",
    }
    
    return CHART_DESCRIPTIONS.get(chart_type, "Visualizes data relationships")


def infer_axis_from_content(content: str, chart_type: ChartType) -> Tuple[str, str]:
    """
    Try to infer better axis labels from the request content.
    
    Args:
        content: User's request content
        chart_type: The type of chart being generated
        
    Returns:
        Tuple of (x_label, y_label) - may return defaults if inference fails
    """
    
    # Get defaults first
    default_x, default_y, _, _ = get_axis_labels(chart_type)
    
    # Common patterns to look for
    content_lower = content.lower()
    
    # Time-based patterns
    if any(word in content_lower for word in ["quarterly", "monthly", "yearly", "daily", "weekly"]):
        if chart_type in [ChartType.LINE_CHART, ChartType.AREA_CHART, ChartType.BAR_VERTICAL]:
            default_x = "Time Period"
    
    # Sales/Revenue patterns
    if any(word in content_lower for word in ["sales", "revenue", "income", "profit"]):
        if chart_type not in [ChartType.PIE_CHART, ChartType.FUNNEL]:
            default_y = "Amount ($)"
    
    # Product patterns
    if "product" in content_lower:
        if chart_type in [ChartType.BAR_VERTICAL, ChartType.BAR_HORIZONTAL]:
            default_x = "Product"
    
    # Department/Team patterns
    if any(word in content_lower for word in ["department", "team", "division"]):
        if chart_type in [ChartType.BAR_VERTICAL, ChartType.GROUPED_BAR]:
            default_x = "Department"
    
    # Performance patterns
    if "performance" in content_lower:
        if chart_type in [ChartType.RADAR_CHART]:
            default_x = "Metric"
            default_y = "Score"
    
    # Distribution patterns
    if any(word in content_lower for word in ["distribution", "spread", "range"]):
        if chart_type in [ChartType.HISTOGRAM]:
            default_y = "Count"
    
    return default_x, default_y