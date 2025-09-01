"""
Smart Data Transformer for Analytics Microservice V2
=====================================================

Intelligently transforms various input data formats into the internal DataPoint format
based on the chart type context. Uses AI to understand data structure and intent.

Author: Analytics Agent System V2
Date: 2025
"""

import json
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import re

from .models import DataPoint, ChartType, DataSource, DataStatistics

logger = logging.getLogger(__name__)


class SmartDataTransformer:
    """
    AI-powered data transformation that adapts input data to chart requirements.
    
    Key Features:
    - Flexible field name recognition
    - Context-aware transformation based on chart type
    - Intelligent parsing of compound labels
    - Metadata extraction for specialized charts
    """
    
    def __init__(self, llm_agent=None):
        """Initialize the transformer with optional LLM agent for advanced detection."""
        self.llm_agent = llm_agent
        
        # Common field name mappings for different roles
        self.field_mappings = {
            'label': ['label', 'name', 'category', 'x', 'key', 'item', 'id', 'title'],
            'value': ['value', 'y', 'amount', 'count', 'total', 'quantity', 'measure', 
                     'metric', 'score', 'price', 'sales', 'revenue'],
            'series': ['series', 'group', 'type', 'class', 'segment', 'product'],
            'category': ['category', 'group', 'type', 'classification', 'segment'],
            'time': ['date', 'time', 'timestamp', 'period', 'month', 'year', 'day', 
                    'datetime', 'when', 'created', 'updated'],
            'row': ['row', 'y_category', 'vertical', 'day', 'weekday'],
            'col': ['col', 'column', 'x_category', 'horizontal', 'hour', 'time'],
        }
    
    async def transform_for_chart(
        self, 
        user_data: List[Dict[str, Any]], 
        chart_type: ChartType,
        request_content: str = ""
    ) -> Tuple[List[DataPoint], DataSource, DataStatistics]:
        """
        Transform user data based on the specific chart type requirements.
        
        Args:
            user_data: Raw user-provided data in any reasonable format
            chart_type: The selected chart type
            request_content: Original request text for context
        
        Returns:
            Tuple of (transformed data points, data source, statistics)
        """
        if not user_data or len(user_data) == 0:
            return [], DataSource.USER_PROVIDED, self._empty_statistics()
        
        # Apply chart-specific transformation
        if chart_type == ChartType.HEATMAP:
            data_points = await self._transform_heatmap_data(user_data, request_content)
        elif chart_type in [ChartType.SCATTER_PLOT, ChartType.BUBBLE_CHART]:
            data_points = await self._transform_scatter_data(user_data, request_content)
        elif chart_type in [ChartType.LINE_CHART, ChartType.AREA_CHART, ChartType.STEP_CHART]:
            data_points = await self._transform_time_series_data(user_data, request_content)
        elif chart_type == ChartType.GANTT:
            data_points = await self._transform_gantt_data(user_data, request_content)
        else:
            # Default transformation for standard charts
            data_points = await self._transform_standard_data(user_data, request_content)
        
        # Calculate statistics
        values = [dp.value for dp in data_points if dp.value is not None]
        statistics = self._calculate_statistics(values)
        
        return data_points, DataSource.USER_PROVIDED, statistics
    
    async def _transform_heatmap_data(
        self, 
        user_data: List[Dict[str, Any]], 
        context: str
    ) -> List[DataPoint]:
        """
        Transform data specifically for heatmap visualization.
        Extracts row/column information from various formats.
        """
        data_points = []
        
        for item in user_data:
            # Get the main label and value
            label = self._extract_field(item, 'label')
            value = self._extract_field(item, 'value')
            
            if value is None:
                logger.warning(f"No value found in item: {item}")
                continue
            
            # Extract or parse row/column information
            row, col = self._parse_matrix_position(item, label)
            
            # Create data point with metadata
            data_point = DataPoint(
                label=label,
                value=float(value),
                metadata={'row': row, 'col': col}
            )
            data_points.append(data_point)
        
        return data_points
    
    async def _transform_scatter_data(
        self, 
        user_data: List[Dict[str, Any]], 
        context: str
    ) -> List[DataPoint]:
        """Transform data for scatter plot visualization."""
        data_points = []
        
        for item in user_data:
            label = self._extract_field(item, 'label')
            
            # For scatter plots, we need x and y coordinates
            x_value = item.get('x') or item.get('satisfaction') or item.get('x_value')
            y_value = self._extract_field(item, 'value')
            
            if x_value is not None and y_value is not None:
                data_point = DataPoint(
                    label=label,
                    value=float(y_value),
                    metadata={'x': float(x_value)}
                )
                data_points.append(data_point)
        
        return data_points
    
    async def _transform_time_series_data(
        self, 
        user_data: List[Dict[str, Any]], 
        context: str
    ) -> List[DataPoint]:
        """Transform data for time-series charts."""
        data_points = []
        
        for item in user_data:
            # Look for time-related fields
            time_label = self._extract_time_field(item)
            value = self._extract_field(item, 'value')
            series = self._extract_field(item, 'series')
            
            if value is not None:
                data_point = DataPoint(
                    label=time_label,
                    value=float(value),
                    series=series,
                    timestamp=self._parse_timestamp(time_label)
                )
                data_points.append(data_point)
        
        return data_points
    
    async def _transform_gantt_data(
        self, 
        user_data: List[Dict[str, Any]], 
        context: str
    ) -> List[DataPoint]:
        """Transform data for Gantt chart visualization."""
        data_points = []
        
        for item in user_data:
            label = self._extract_field(item, 'label') or item.get('task', 'Task')
            start = item.get('start') or item.get('start_date')
            end = item.get('end') or item.get('end_date')
            progress = item.get('progress', 0)
            
            if start and end:
                data_point = DataPoint(
                    label=label,
                    value=progress,
                    metadata={'start': start, 'end': end}
                )
                data_points.append(data_point)
        
        return data_points
    
    async def _transform_standard_data(
        self, 
        user_data: List[Dict[str, Any]], 
        context: str
    ) -> List[DataPoint]:
        """Default transformation for standard charts."""
        data_points = []
        
        for item in user_data:
            label = self._extract_field(item, 'label')
            value = self._extract_field(item, 'value')
            
            if value is None:
                logger.warning(f"No value found in item: {item}")
                continue
            
            series = self._extract_field(item, 'series')
            category = self._extract_field(item, 'category')
            
            data_point = DataPoint(
                label=label,
                value=float(value),
                series=series,
                category=category,
                metadata=self._extract_metadata(item)
            )
            data_points.append(data_point)
        
        return data_points
    
    def _extract_field(self, item: Dict[str, Any], field_type: str) -> Optional[Any]:
        """
        Extract a field value using flexible field name matching.
        
        Args:
            item: Data item dictionary
            field_type: Type of field to extract ('label', 'value', 'series', etc.)
        
        Returns:
            Extracted value or None
        """
        # Get possible field names for this type
        possible_names = self.field_mappings.get(field_type, [field_type])
        
        # Try each possible field name
        for field_name in possible_names:
            if field_name in item:
                return item[field_name]
        
        # Special fallback for label
        if field_type == 'label':
            # Use first string field or generate one
            for key, value in item.items():
                if isinstance(value, str) and key not in ['series', 'category', 'type']:
                    return value
            return f"Item_{id(item)}"
        
        return None
    
    def _extract_time_field(self, item: Dict[str, Any]) -> str:
        """Extract and format time-related field from item."""
        time_fields = self.field_mappings['time']
        
        for field in time_fields:
            if field in item:
                return str(item[field])
        
        # Fallback to label
        return self._extract_field(item, 'label')
    
    def _parse_matrix_position(
        self, 
        item: Dict[str, Any], 
        label: str
    ) -> Tuple[str, str]:
        """
        Parse row and column position for matrix-based charts.
        
        Handles formats like:
        - "Mon-09:00" -> (Mon, 09:00)
        - "Monday 9AM" -> (Monday, 9AM)
        - {"day": "Mon", "hour": "09:00"} -> (Mon, 09:00)
        """
        # Check for explicit row/col fields
        if 'row' in item and 'col' in item:
            return str(item['row']), str(item['col'])
        
        # Check for day/hour pattern (common for heatmaps)
        if 'day' in item and 'hour' in item:
            return str(item['day']), str(item['hour'])
        
        # Try to parse the label
        if '-' in label:
            parts = label.split('-', 1)
            if len(parts) == 2:
                return parts[0].strip(), parts[1].strip()
        
        if ' ' in label:
            parts = label.split(' ', 1)
            if len(parts) == 2:
                return parts[0].strip(), parts[1].strip()
        
        # Fallback: use label and value
        return label, "Value"
    
    def _parse_timestamp(self, time_str: str) -> Optional[datetime]:
        """Parse timestamp from various string formats."""
        if not time_str:
            return None
        
        # Common date formats to try
        formats = [
            '%Y-%m-%d',
            '%Y-%m',
            '%Y/%m/%d',
            '%m/%d/%Y',
            '%d-%m-%Y',
            '%B %Y',
            '%b %Y',
            '%Y'
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(time_str, fmt)
            except ValueError:
                continue
        
        return None
    
    def _extract_metadata(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Extract additional metadata from item."""
        # Exclude known primary fields
        exclude_keys = set()
        for field_list in self.field_mappings.values():
            exclude_keys.update(field_list)
        
        metadata = {}
        for key, value in item.items():
            if key not in exclude_keys:
                metadata[key] = value
        
        return metadata
    
    def _calculate_statistics(self, values: List[float]) -> DataStatistics:
        """Calculate basic statistics from values."""
        if not values:
            return self._empty_statistics()
        
        import statistics
        
        return DataStatistics(
            min=min(values),
            max=max(values),
            mean=statistics.mean(values),
            median=statistics.median(values),
            std=statistics.stdev(values) if len(values) > 1 else 0,
            total=sum(values),
            count=len(values)
        )
    
    def _empty_statistics(self) -> DataStatistics:
        """Return empty statistics object."""
        return DataStatistics(
            min=0, max=0, mean=0, median=0, std=0, total=0, count=0
        )
    
    async def detect_field_roles_with_llm(
        self, 
        sample_data: List[Dict[str, Any]], 
        chart_type: ChartType
    ) -> Dict[str, str]:
        """
        Use LLM to intelligently detect field roles for a given chart type.
        
        This is an advanced feature that can be enabled when LLM agent is available.
        """
        if not self.llm_agent:
            return {}
        
        prompt = f"""
        Analyze this data sample for a {chart_type.value} chart:
        {json.dumps(sample_data[:3], indent=2)}
        
        Identify which fields should be used for:
        - X-axis/labels/categories
        - Y-axis/values/measures  
        - Series/groups (if applicable)
        - Time dimension (if applicable)
        
        Return as JSON mapping: {{"x": "field_name", "y": "field_name", ...}}
        """
        
        try:
            result = await self.llm_agent.run(prompt)
            return json.loads(result.data)
        except Exception as e:
            logger.warning(f"LLM field detection failed: {e}")
            return {}