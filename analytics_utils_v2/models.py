"""
Analytics Agent V2 Models
=========================

Data structures for the enhanced analytics generation pipeline.
Includes request/response models, theme configuration, and data structures.

Author: Analytics Agent System V2
Date: 2024
Version: 2.0
"""

from typing import Dict, Any, List, Optional, Literal, Union
from enum import Enum
from pydantic import BaseModel, Field, validator
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ChartType(str, Enum):
    """All 23 supported chart types."""
    # Line and Trend Charts
    LINE_CHART = "line_chart"
    STEP_CHART = "step_chart"
    AREA_CHART = "area_chart"
    STACKED_AREA_CHART = "stacked_area_chart"
    
    # Bar Charts
    BAR_VERTICAL = "bar_chart_vertical"
    BAR_HORIZONTAL = "bar_chart_horizontal"
    GROUPED_BAR = "grouped_bar_chart"
    STACKED_BAR = "stacked_bar_chart"
    
    # Distribution Charts
    HISTOGRAM = "histogram"
    BOX_PLOT = "box_plot"
    VIOLIN_PLOT = "violin_plot"
    
    # Correlation Charts
    SCATTER_PLOT = "scatter_plot"
    BUBBLE_CHART = "bubble_chart"
    HEXBIN = "hexbin"
    
    # Composition Charts
    PIE_CHART = "pie_chart"
    WATERFALL = "waterfall"
    FUNNEL = "funnel"
    
    # Comparison Charts
    RADAR_CHART = "radar_chart"
    HEATMAP = "heatmap"
    
    # Statistical Charts
    ERROR_BAR = "error_bar_chart"
    CONTROL_CHART = "control_chart"
    PARETO = "pareto"
    
    # Project Charts
    GANTT = "gantt"


class GenerationMethod(str, Enum):
    """Methods for chart generation."""
    PYTHON_MCP = "python_mcp"
    MERMAID = "mermaid"
    PYTHON_CODE = "python_code"  # Code only, no execution
    FALLBACK = "fallback"


class DataSource(str, Enum):
    """Source of data for charts."""
    USER_PROVIDED = "user"
    SYNTHETIC = "synthetic"
    HYBRID = "hybrid"  # User data enhanced with synthetic


class ThemeStyle(str, Enum):
    """Available theme styles."""
    MODERN = "modern"
    CLASSIC = "classic"
    MINIMAL = "minimal"
    DARK = "dark"
    CORPORATE = "corporate"


class DataPoint(BaseModel):
    """Individual data point for charts."""
    label: str = Field(description="Label or category")
    value: Union[float, int] = Field(description="Numeric value")
    category: Optional[str] = Field(default=None, description="Grouping category")
    series: Optional[str] = Field(default=None, description="Series name for multi-series")
    timestamp: Optional[datetime] = Field(default=None, description="Optional timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class ThemeConfig(BaseModel):
    """Theme configuration for charts."""
    primary: str = Field(default="#1E40AF", description="Primary color (hex)")
    secondary: str = Field(default="#10B981", description="Secondary color (hex)")
    tertiary: str = Field(default="#F59E0B", description="Tertiary color (hex)")
    style: ThemeStyle = Field(default=ThemeStyle.MODERN, description="Theme style")
    gradient: bool = Field(default=True, description="Use gradients")
    transparency: float = Field(default=0.8, description="Transparency level (0-1)")
    font_family: str = Field(default="Arial", description="Font family")
    font_size: int = Field(default=12, description="Base font size")
    
    @validator('primary', 'secondary', 'tertiary')
    def validate_color(cls, v):
        """Ensure colors are valid hex codes."""
        if not v.startswith('#') or len(v) not in [4, 7]:
            raise ValueError(f"Invalid hex color: {v}")
        return v
    
    @validator('transparency')
    def validate_transparency(cls, v):
        """Ensure transparency is between 0 and 1."""
        if not 0 <= v <= 1:
            raise ValueError(f"Transparency must be between 0 and 1: {v}")
        return v


class AnalyticsRequest(BaseModel):
    """Request structure for analytics generation."""
    content: str = Field(description="Chart description/request")
    title: Optional[str] = Field(default=None, description="Chart title")
    data: Optional[List[Dict[str, Any]]] = Field(default=None, description="User-provided data")
    use_synthetic_data: bool = Field(default=True, description="Generate synthetic if no data")
    theme: Optional[ThemeConfig] = Field(default=None, description="Theme configuration")
    chart_preference: Optional[ChartType] = Field(default=None, description="Preferred chart type")
    output_format: Literal["png", "svg", "base64"] = Field(default="png", description="Output format")
    include_raw_data: bool = Field(default=True, description="Include JSON data in response")
    enhance_labels: bool = Field(default=True, description="Use LLM to enhance labels")
    
    @validator('data')
    def validate_data(cls, v):
        """Validate user-provided data structure with flexible field recognition."""
        if v is not None and len(v) > 0:
            # More flexible validation - just ensure we have some numeric data
            for item in v:
                # Look for any numeric field that could be a value
                has_numeric = any(
                    isinstance(item.get(key), (int, float)) 
                    for key in ['value', 'y', 'amount', 'count', 'total', 
                               'quantity', 'measure', 'metric', 'score', 
                               'price', 'sales', 'revenue', 'market_share',
                               'satisfaction', 'purchase_value', 'traffic']
                )
                
                # Or check if any field contains a number
                if not has_numeric:
                    # Check all fields for numeric values
                    has_numeric = any(
                        isinstance(val, (int, float))
                        for val in item.values()
                    )
                
                if not has_numeric:
                    logger.warning(f"Data point may lack numeric value: {item}")
                    # Don't raise error - let transformer handle it
        return v
    
    def get_data_source(self) -> DataSource:
        """Determine the data source."""
        if self.data and len(self.data) > 0:
            return DataSource.USER_PROVIDED
        elif self.use_synthetic_data:
            return DataSource.SYNTHETIC
        else:
            raise ValueError("No data provided and synthetic data disabled")


class ChartMetadata(BaseModel):
    """Metadata about generated chart."""
    chart_type: ChartType = Field(description="Actual chart type used")
    generation_method: GenerationMethod = Field(description="Method used for generation")
    data_source: DataSource = Field(description="Source of data")
    theme_applied: ThemeConfig = Field(description="Theme configuration used")
    insights: List[str] = Field(default_factory=list, description="Auto-generated insights")
    timestamp: datetime = Field(default_factory=datetime.now, description="Generation timestamp")
    generation_time_ms: float = Field(default=0, description="Time taken to generate (ms)")
    data_points_count: int = Field(default=0, description="Number of data points")
    llm_enhanced: bool = Field(default=False, description="Whether LLM enhancement was used")
    
    # Chart display information
    title: str = Field(default="", description="Chart title")
    x_axis_label: str = Field(default="X", description="X-axis label")
    y_axis_label: str = Field(default="Y", description="Y-axis label")
    x_axis_type: str = Field(default="categorical", description="Type: categorical/numerical/temporal")
    y_axis_type: str = Field(default="numerical", description="Type: numerical/percentage/count")


class DataStatistics(BaseModel):
    """Statistics about the data."""
    min: float = Field(description="Minimum value")
    max: float = Field(description="Maximum value")
    mean: float = Field(description="Mean value")
    median: float = Field(description="Median value")
    std: float = Field(description="Standard deviation")
    total: float = Field(description="Sum of all values")
    count: int = Field(description="Number of data points")


class ChartData(BaseModel):
    """Structured data included in response."""
    labels: List[str] = Field(description="X-axis labels")
    values: List[Union[float, int]] = Field(description="Y-axis values")
    series: Optional[List[Dict[str, Any]]] = Field(default=None, description="Multiple series data")
    categories: Optional[List[str]] = Field(default=None, description="Category names")
    statistics: Optional[DataStatistics] = Field(default=None, description="Data statistics")
    raw_data: Optional[List[DataPoint]] = Field(default=None, description="Raw data points")
    
    # Table-ready format
    table_data: Optional[List[Dict[str, Any]]] = Field(
        default=None, 
        description="Data formatted as table rows"
    )
    table_columns: Optional[List[str]] = Field(
        default=None,
        description="Column names for table display"
    )


class AnalyticsResponse(BaseModel):
    """Response structure for analytics generation."""
    success: bool = Field(description="Whether generation succeeded")
    chart: Optional[str] = Field(default=None, description="Base64 encoded PNG/SVG")
    data: Optional[ChartData] = Field(default=None, description="Underlying chart data")
    metadata: ChartMetadata = Field(description="Chart metadata")
    error: Optional[str] = Field(default=None, description="Error message if failed")
    python_code: Optional[str] = Field(default=None, description="Generated Python code")
    
    def to_api_response(self) -> Dict[str, Any]:
        """Convert to API response format."""
        # Use model_dump for Pydantic v2 compatibility and handle datetime
        metadata_dict = self.metadata.model_dump()
        # Convert datetime to ISO format string
        if 'timestamp' in metadata_dict:
            metadata_dict['timestamp'] = metadata_dict['timestamp'].isoformat()
        
        response = {
            "success": self.success,
            "metadata": metadata_dict
        }
        
        if self.success:
            response["chart"] = self.chart
            if self.data:
                response["data"] = self.data.model_dump()
            if self.python_code:
                response["code"] = self.python_code
        else:
            response["error"] = self.error
        
        return response


class ChartPlan(BaseModel):
    """Execution plan for chart generation."""
    chart_type: ChartType = Field(description="Selected chart type")
    generation_method: GenerationMethod = Field(description="Generation method")
    data_source: DataSource = Field(description="Data source")
    data_config: Dict[str, Any] = Field(description="Data generation configuration")
    theme: ThemeConfig = Field(description="Theme to apply")
    confidence: float = Field(default=0.8, description="Confidence in selection (0-1)")
    reasoning: str = Field(default="", description="Reasoning for selection")
    fallback_chart: Optional[ChartType] = Field(default=None, description="Fallback if primary fails")


class SyntheticDataConfig(BaseModel):
    """Configuration for synthetic data generation."""
    num_points: int = Field(default=12, description="Number of data points")
    pattern: Literal["trend", "seasonal", "random", "mixed"] = Field(default="random")
    trend_direction: Literal["increasing", "decreasing", "stable"] = Field(default="stable")
    noise_level: float = Field(default=0.1, description="Noise level (0-1)")
    value_range: List[float] = Field(default=[0, 100], description="Min/max values")
    include_outliers: bool = Field(default=False, description="Include outlier points")
    distribution: Literal["normal", "uniform", "exponential", "bimodal"] = Field(default="normal")
    
    @validator('noise_level')
    def validate_noise(cls, v):
        """Ensure noise level is between 0 and 1."""
        if not 0 <= v <= 1:
            raise ValueError(f"Noise level must be between 0 and 1: {v}")
        return v


class LLMEnhancementConfig(BaseModel):
    """Configuration for LLM enhancement of data."""
    enhance_labels: bool = Field(default=True, description="Generate professional labels")
    enhance_values: bool = Field(default=True, description="Generate realistic values")
    context: str = Field(default="", description="Context for generation")
    industry: Optional[str] = Field(default=None, description="Industry context")
    style: Literal["formal", "casual", "technical"] = Field(default="formal")
    locale: str = Field(default="en-US", description="Locale for formatting")