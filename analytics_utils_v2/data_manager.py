"""
Data Manager V2
===============

Manages data sources with intelligent synthetic data generation.
Supports user-provided data and LLM-enhanced synthetic data with professional labels.

Author: Analytics Agent System V2
Date: 2024
Version: 2.0
"""

import json
import logging
import numpy as np
import random
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from pydantic_ai import Agent

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.model_utils import create_model_with_fallback
from .models import (
    DataPoint, DataSource, ChartType, 
    SyntheticDataConfig, LLMEnhancementConfig,
    DataStatistics, ChartData
)
from .analytics_playbook import get_chart_synthetic_features

logger = logging.getLogger(__name__)


class DataManager:
    """Manages data sources and generation for analytics."""
    
    def __init__(self, seed: Optional[int] = None):
        """Initialize data manager."""
        self.seed = seed or 42
        self.random_state = random.Random(self.seed)
        self.np_random = np.random.RandomState(self.seed)
        self.llm_agent = self._create_llm_agent()
    
    def _create_llm_agent(self) -> Agent:
        """Create LLM agent for data enhancement."""
        return Agent(
            create_model_with_fallback("gemini-2.0-flash-exp"),
            system_prompt="""You are a data generation expert for analytics.
            Your role is to generate professional, context-appropriate labels and realistic values.
            
            Focus on:
            - Industry-standard terminology
            - Logical relationships between values
            - Appropriate scale and ranges
            - Clear, concise naming
            
            Always return valid JSON arrays when requested."""
        )
    
    async def get_data(
        self,
        request: Any,
        chart_type: ChartType,
        synthetic_config: Optional[SyntheticDataConfig] = None
    ) -> Tuple[List[DataPoint], DataSource, DataStatistics]:
        """
        Get data from user or generate synthetic data.
        
        Args:
            request: Analytics request with potential user data
            chart_type: Type of chart to generate data for
            synthetic_config: Configuration for synthetic data
            
        Returns:
            Tuple of (data_points, data_source, statistics)
        """
        # Check for user-provided data
        if hasattr(request, 'data') and request.data and len(request.data) > 0:
            logger.info("Using user-provided data")
            return await self._process_user_data(request.data)
        
        # Generate synthetic data
        if not hasattr(request, 'use_synthetic_data') or request.use_synthetic_data:
            logger.info("Generating synthetic data")
            return await self._generate_synthetic_data(
                request,
                chart_type,
                synthetic_config or SyntheticDataConfig()
            )
        
        # No data available
        raise ValueError("No data provided and synthetic data generation disabled")
    
    async def _process_user_data(
        self, 
        user_data: List[Dict[str, Any]]
    ) -> Tuple[List[DataPoint], DataSource, DataStatistics]:
        """Process and validate user-provided data."""
        data_points = []
        values = []
        
        for item in user_data:
            # Extract label
            label = item.get('label') or item.get('x') or f"Item_{len(data_points) + 1}"
            
            # Extract value
            value = item.get('value') or item.get('y')
            if value is None:
                raise ValueError(f"No value found for data point: {item}")
            
            # Create data point
            data_point = DataPoint(
                label=str(label),
                value=float(value),
                category=item.get('category'),
                series=item.get('series'),
                metadata=item.get('metadata', {})
            )
            
            data_points.append(data_point)
            values.append(float(value))
        
        # Calculate statistics
        statistics = self._calculate_statistics(values)
        
        return data_points, DataSource.USER_PROVIDED, statistics
    
    async def _generate_synthetic_data(
        self,
        request: Any,
        chart_type: ChartType,
        config: SyntheticDataConfig
    ) -> Tuple[List[DataPoint], DataSource, DataStatistics]:
        """Generate synthetic data with optional LLM enhancement."""
        
        # Get chart-specific features from playbook
        playbook_features = get_chart_synthetic_features(chart_type.value)
        
        # Create a merged config dictionary for non-standard fields
        merged_config = {}
        if playbook_features:
            merged_config.update(playbook_features)
        
        # Override with config values
        for field in config.__fields__:
            merged_config[field] = getattr(config, field)
        
        # Generate based on chart type - pass merged_config as a dict
        if chart_type in [ChartType.LINE_CHART, ChartType.AREA_CHART, ChartType.STEP_CHART]:
            data_points = await self._generate_time_series(request, config, merged_config)
        elif chart_type in [ChartType.BAR_VERTICAL, ChartType.BAR_HORIZONTAL]:
            data_points = await self._generate_categorical(request, config, merged_config)
        elif chart_type == ChartType.STACKED_AREA_CHART:
            data_points = await self._generate_stacked_series(request, config, merged_config)
        elif chart_type in [ChartType.GROUPED_BAR, ChartType.STACKED_BAR]:
            data_points = await self._generate_grouped_categorical(request, config, merged_config)
        elif chart_type == ChartType.HISTOGRAM:
            data_points = await self._generate_distribution(request, config, merged_config)
        elif chart_type in [ChartType.BOX_PLOT, ChartType.VIOLIN_PLOT]:
            data_points = await self._generate_grouped_distribution(request, config, merged_config)
        elif chart_type == ChartType.SCATTER_PLOT:
            data_points = await self._generate_correlation(request, config, merged_config)
        elif chart_type == ChartType.BUBBLE_CHART:
            data_points = await self._generate_bubble(request, config, merged_config)
        elif chart_type == ChartType.PIE_CHART:
            data_points = await self._generate_proportional(request, config, merged_config)
        elif chart_type == ChartType.RADAR_CHART:
            data_points = await self._generate_multivariate(request, config, merged_config)
        elif chart_type == ChartType.HEATMAP:
            data_points = await self._generate_matrix(request, config, merged_config)
        elif chart_type == ChartType.WATERFALL:
            data_points = await self._generate_waterfall(request, config, merged_config)
        elif chart_type == ChartType.FUNNEL:
            data_points = await self._generate_funnel(request, config, merged_config)
        elif chart_type == ChartType.GANTT:
            data_points = await self._generate_gantt(request, config, merged_config)
        elif chart_type == ChartType.PARETO:
            data_points = await self._generate_pareto(request, config, merged_config)
        elif chart_type == ChartType.CONTROL_CHART:
            data_points = await self._generate_control(request, config, merged_config)
        elif chart_type == ChartType.ERROR_BAR:
            data_points = await self._generate_error_bar(request, config, merged_config)
        elif chart_type == ChartType.HEXBIN:
            data_points = await self._generate_dense_scatter(request, config, merged_config)
        else:
            # Default to categorical
            data_points = await self._generate_categorical(request, config, merged_config)
        
        # Calculate statistics
        values = [dp.value for dp in data_points]
        statistics = self._calculate_statistics(values)
        
        return data_points, DataSource.SYNTHETIC, statistics
    
    async def _generate_time_series(
        self, 
        request: Any, 
        config: SyntheticDataConfig,
        merged_config: Dict[str, Any] = None
    ) -> List[DataPoint]:
        """Generate time series data."""
        if merged_config is None:
            merged_config = {}
        num_points = merged_config.get('rows', merged_config.get('num_points', config.num_points))
        
        # Generate time labels with LLM if requested
        if hasattr(request, 'enhance_labels') and request.enhance_labels:
            labels = await self._generate_time_labels_llm(request, num_points)
        else:
            # Default time labels
            start_date = datetime.now() - timedelta(days=num_points)
            labels = [(start_date + timedelta(days=i)).strftime("%Y-%m-%d") 
                     for i in range(num_points)]
        
        # Generate values based on pattern
        if config.pattern == "trend":
            if config.trend_direction == "increasing":
                base = config.value_range[0]
                trend = (config.value_range[1] - config.value_range[0]) / num_points
                values = [base + trend * i + self.np_random.normal(0, config.noise_level * 10) 
                         for i in range(num_points)]
            elif config.trend_direction == "decreasing":
                base = config.value_range[1]
                trend = (config.value_range[1] - config.value_range[0]) / num_points
                values = [base - trend * i + self.np_random.normal(0, config.noise_level * 10) 
                         for i in range(num_points)]
            else:  # stable
                mean = (config.value_range[0] + config.value_range[1]) / 2
                values = [mean + self.np_random.normal(0, config.noise_level * 10) 
                         for _ in range(num_points)]
        elif config.pattern == "seasonal":
            amplitude = (config.value_range[1] - config.value_range[0]) / 2
            mean = (config.value_range[0] + config.value_range[1]) / 2
            values = [mean + amplitude * np.sin(2 * np.pi * i / 12) + 
                     self.np_random.normal(0, config.noise_level * 10)
                     for i in range(num_points)]
        else:  # random
            values = [self.np_random.uniform(config.value_range[0], config.value_range[1]) 
                     for _ in range(num_points)]
        
        # Add outliers if requested
        if config.include_outliers and num_points > 10:
            num_outliers = max(1, int(num_points * 0.05))
            outlier_indices = self.np_random.choice(num_points, num_outliers, replace=False)
            for idx in outlier_indices:
                values[idx] *= self.np_random.choice([0.3, 3.0])
        
        # Create data points
        data_points = []
        for label, value in zip(labels, values):
            data_points.append(DataPoint(
                label=label,
                value=round(float(value), 2),
                metadata={"synthetic": True}
            ))
        
        return data_points
    
    async def _generate_categorical(
        self,
        request: Any,
        config: SyntheticDataConfig,
        merged_config: Dict[str, Any] = None
    ) -> List[DataPoint]:
        """Generate categorical data."""
        if merged_config is None:
            merged_config = {}
        num_categories = merged_config.get('num_categories', getattr(config, 'num_categories', 8))
        
        # Generate category labels with LLM if requested
        if hasattr(request, 'enhance_labels') and request.enhance_labels:
            labels = await self._generate_category_labels_llm(request, num_categories)
        else:
            # Default labels
            labels = [f"Category {chr(65 + i)}" for i in range(num_categories)]
        
        # Generate values
        if config.distribution == "uniform":
            values = [self.np_random.uniform(config.value_range[0], config.value_range[1]) 
                     for _ in range(num_categories)]
        elif config.distribution == "normal":
            mean = (config.value_range[0] + config.value_range[1]) / 2
            std = (config.value_range[1] - config.value_range[0]) / 6
            values = [np.clip(self.np_random.normal(mean, std), 
                            config.value_range[0], config.value_range[1])
                     for _ in range(num_categories)]
        elif config.distribution == "exponential":
            values = sorted([self.np_random.exponential(50) for _ in range(num_categories)], 
                          reverse=True)
        else:
            values = [self.np_random.uniform(config.value_range[0], config.value_range[1]) 
                     for _ in range(num_categories)]
        
        # Create data points
        data_points = []
        for label, value in zip(labels, values):
            data_points.append(DataPoint(
                label=label,
                value=round(float(value), 2),
                metadata={"synthetic": True}
            ))
        
        return data_points
    
    async def _generate_proportional(
        self,
        request: Any,
        config: SyntheticDataConfig,
        merged_config: Dict[str, Any] = None
    ) -> List[DataPoint]:
        """Generate proportional data for pie charts."""
        if merged_config is None:
            merged_config = {}
        num_segments = merged_config.get('num_segments', getattr(config, 'num_segments', 5))
        
        # Generate segment labels with LLM if requested
        if hasattr(request, 'enhance_labels') and request.enhance_labels:
            labels = await self._generate_segment_labels_llm(request, num_segments)
        else:
            labels = [f"Segment {chr(65 + i)}" for i in range(num_segments)]
        
        # Generate proportions that sum to 100
        values = self.np_random.exponential(1, num_segments)
        values = (values / values.sum()) * 100
        
        # Sort by value for better visualization
        sorted_pairs = sorted(zip(labels, values), key=lambda x: x[1], reverse=True)
        
        data_points = []
        for label, value in sorted_pairs:
            data_points.append(DataPoint(
                label=label,
                value=round(float(value), 1),
                metadata={"percentage": float(value), "synthetic": True}
            ))
        
        return data_points
    
    async def _generate_correlation(
        self,
        request: Any,
        config: SyntheticDataConfig,
        merged_config: Dict[str, Any] = None
    ) -> List[DataPoint]:
        """Generate correlation data for scatter plots."""
        n_points = config.num_points
        correlation = getattr(config, 'correlation', 0.7)
        
        # Generate correlated data
        x = self.np_random.uniform(config.value_range[0], config.value_range[1], n_points)
        noise = self.np_random.normal(0, 10, n_points)
        y = correlation * x + (1 - correlation) * noise + 50
        
        # Generate labels
        if hasattr(request, 'enhance_labels') and request.enhance_labels:
            labels = await self._generate_point_labels_llm(request, n_points)
        else:
            labels = [f"Point_{i+1}" for i in range(n_points)]
        
        data_points = []
        for i, (label, xi, yi) in enumerate(zip(labels, x, y)):
            data_points.append(DataPoint(
                label=label,
                value=round(float(yi), 2),
                metadata={"x": round(float(xi), 2), "y": round(float(yi), 2), "synthetic": True}
            ))
        
        return data_points
    
    async def _generate_distribution(
        self,
        request: Any,
        config: SyntheticDataConfig,
        merged_config: Dict[str, Any] = None
    ) -> List[DataPoint]:
        """Generate distribution data for histograms."""
        n = getattr(config, 'n', 1000)
        
        # Generate raw values based on distribution type
        if config.distribution == "normal":
            mean = (config.value_range[0] + config.value_range[1]) / 2
            std = (config.value_range[1] - config.value_range[0]) / 6
            values = self.np_random.normal(mean, std, n)
        elif config.distribution == "bimodal":
            mode1 = config.value_range[0] + (config.value_range[1] - config.value_range[0]) * 0.3
            mode2 = config.value_range[0] + (config.value_range[1] - config.value_range[0]) * 0.7
            values1 = self.np_random.normal(mode1, 5, n // 2)
            values2 = self.np_random.normal(mode2, 5, n // 2)
            values = np.concatenate([values1, values2])
        elif config.distribution == "exponential":
            scale = (config.value_range[1] - config.value_range[0]) / 3
            values = self.np_random.exponential(scale, n) + config.value_range[0]
        else:
            values = self.np_random.uniform(config.value_range[0], config.value_range[1], n)
        
        # Clip to range
        values = np.clip(values, config.value_range[0], config.value_range[1])
        
        # Sample if too many points
        sample_size = min(1000, len(values))
        sampled_values = self.np_random.choice(values, sample_size, replace=False)
        
        # Create data points (raw values for histogram)
        data_points = []
        for i, value in enumerate(sampled_values):
            data_points.append(DataPoint(
                label=f"Sample_{i+1}",
                value=round(float(value), 2),
                metadata={"raw_value": float(value), "synthetic": True}
            ))
        
        return data_points
    
    async def _generate_stacked_series(
        self,
        request: Any,
        config: SyntheticDataConfig,
        merged_config: Dict[str, Any] = None
    ) -> List[DataPoint]:
        """Generate stacked series data."""
        num_points = config.num_points
        num_series = getattr(config, 'num_series', 4)
        
        # Generate time labels
        if hasattr(request, 'enhance_labels') and request.enhance_labels:
            time_labels = await self._generate_time_labels_llm(request, num_points)
            series_labels = await self._generate_series_labels_llm(request, num_series)
        else:
            time_labels = [f"Period_{i+1}" for i in range(num_points)]
            series_labels = [f"Series_{chr(65+i)}" for i in range(num_series)]
        
        # Generate values for each series
        data_points = []
        for t, time_label in enumerate(time_labels):
            for s, series_label in enumerate(series_labels):
                base_value = (config.value_range[1] - config.value_range[0]) / num_series
                value = base_value * (1 + self.np_random.uniform(-0.3, 0.3))
                
                data_points.append(DataPoint(
                    label=time_label,
                    value=round(float(value), 2),
                    series=series_label,
                    metadata={"time_index": t, "series_index": s, "synthetic": True}
                ))
        
        return data_points
    
    async def _generate_grouped_categorical(
        self,
        request: Any,
        config: SyntheticDataConfig,
        merged_config: Dict[str, Any] = None
    ) -> List[DataPoint]:
        """Generate grouped categorical data."""
        num_categories = getattr(config, 'num_categories', 6)
        num_groups = getattr(config, 'num_groups', 3)
        
        # Generate labels
        if hasattr(request, 'enhance_labels') and request.enhance_labels:
            category_labels = await self._generate_category_labels_llm(request, num_categories)
            group_labels = await self._generate_group_labels_llm(request, num_groups)
        else:
            category_labels = [f"Category_{chr(65+i)}" for i in range(num_categories)]
            group_labels = [f"Group_{i+1}" for i in range(num_groups)]
        
        # Generate values
        data_points = []
        for cat_label in category_labels:
            for group_label in group_labels:
                value = self.np_random.uniform(config.value_range[0], config.value_range[1])
                data_points.append(DataPoint(
                    label=cat_label,
                    value=round(float(value), 2),
                    category=group_label,
                    metadata={"group": group_label, "synthetic": True}
                ))
        
        return data_points
    
    async def _generate_grouped_distribution(
        self,
        request: Any,
        config: SyntheticDataConfig,
        merged_config: Dict[str, Any] = None
    ) -> List[DataPoint]:
        """Generate grouped distribution data for box/violin plots."""
        n_groups = getattr(config, 'n_groups', 4)
        n_per_group = getattr(config, 'n_per_group', 100)
        
        # Generate group labels
        if hasattr(request, 'enhance_labels') and request.enhance_labels:
            group_labels = await self._generate_group_labels_llm(request, n_groups)
        else:
            group_labels = [f"Group_{chr(65+i)}" for i in range(n_groups)]
        
        data_points = []
        for g, group_label in enumerate(group_labels):
            # Generate distribution for this group
            if config.distribution == "bimodal":
                # Bimodal for violin plots
                mode1 = 30 + g * 10
                mode2 = 60 + g * 10
                values1 = self.np_random.normal(mode1, 5, n_per_group // 2)
                values2 = self.np_random.normal(mode2, 5, n_per_group // 2)
                values = np.concatenate([values1, values2])
            else:
                # Normal distribution
                mean = 50 + g * 10
                values = self.np_random.normal(mean, 10, n_per_group)
            
            # Store summary statistics
            data_points.append(DataPoint(
                label=group_label,
                value=round(float(np.median(values)), 2),
                metadata={
                    "mean": round(float(np.mean(values)), 2),
                    "std": round(float(np.std(values)), 2),
                    "q1": round(float(np.percentile(values, 25)), 2),
                    "q3": round(float(np.percentile(values, 75)), 2),
                    "min": round(float(np.min(values)), 2),
                    "max": round(float(np.max(values)), 2),
                    "samples": n_per_group,
                    "synthetic": True
                }
            ))
        
        return data_points
    
    async def _generate_bubble(
        self,
        request: Any,
        config: SyntheticDataConfig,
        merged_config: Dict[str, Any] = None
    ) -> List[DataPoint]:
        """Generate bubble chart data (x, y, size)."""
        n_points = getattr(config, 'n_points', 15)
        
        # Generate labels
        if hasattr(request, 'enhance_labels') and request.enhance_labels:
            labels = await self._generate_entity_labels_llm(request, n_points)
        else:
            labels = [f"Entity_{chr(65+i)}" for i in range(n_points)]
        
        data_points = []
        for label in labels:
            x = self.np_random.uniform(0, 100)
            y = self.np_random.uniform(0, 100)
            size = self.np_random.uniform(100, 1000)
            
            data_points.append(DataPoint(
                label=label,
                value=round(float(y), 2),
                metadata={
                    "x": round(float(x), 2),
                    "y": round(float(y), 2),
                    "size": round(float(size), 2),
                    "synthetic": True
                }
            ))
        
        return data_points
    
    async def _generate_multivariate(
        self,
        request: Any,
        config: SyntheticDataConfig,
        merged_config: Dict[str, Any] = None
    ) -> List[DataPoint]:
        """Generate multivariate data for radar charts."""
        num_dimensions = getattr(config, 'num_dimensions', 6)
        
        # Generate dimension labels
        if hasattr(request, 'enhance_labels') and request.enhance_labels:
            labels = await self._generate_dimension_labels_llm(request, num_dimensions)
        else:
            labels = [f"Dimension_{i+1}" for i in range(num_dimensions)]
        
        data_points = []
        for label in labels:
            value = self.np_random.uniform(config.value_range[0], config.value_range[1])
            data_points.append(DataPoint(
                label=label,
                value=round(float(value), 2),
                metadata={"dimension": label, "synthetic": True}
            ))
        
        return data_points
    
    async def _generate_matrix(
        self,
        request: Any,
        config: SyntheticDataConfig,
        merged_config: Dict[str, Any] = None
    ) -> List[DataPoint]:
        """Generate matrix data for heatmaps."""
        shape = getattr(config, 'shape', [7, 7])
        rows, cols = shape if isinstance(shape, list) else (7, 7)
        
        # Generate labels
        if hasattr(request, 'enhance_labels') and request.enhance_labels:
            row_labels = await self._generate_row_labels_llm(request, rows)
            col_labels = await self._generate_column_labels_llm(request, cols)
        else:
            row_labels = [f"Row_{i+1}" for i in range(rows)]
            col_labels = [f"Col_{i+1}" for i in range(cols)]
        
        # Generate matrix values
        matrix = self.np_random.uniform(config.value_range[0], config.value_range[1], (rows, cols))
        
        data_points = []
        for i, row_label in enumerate(row_labels):
            for j, col_label in enumerate(col_labels):
                data_points.append(DataPoint(
                    label=f"{row_label}_{col_label}",
                    value=round(float(matrix[i, j]), 2),
                    metadata={"row": i, "col": j, "row_label": row_label, 
                             "col_label": col_label, "synthetic": True}
                ))
        
        return data_points
    
    async def _generate_waterfall(
        self,
        request: Any,
        config: SyntheticDataConfig,
        merged_config: Dict[str, Any] = None
    ) -> List[DataPoint]:
        """Generate waterfall chart data."""
        num_steps = getattr(config, 'num_steps', 6)
        
        # Generate step labels
        if hasattr(request, 'enhance_labels') and request.enhance_labels:
            labels = await self._generate_waterfall_labels_llm(request, num_steps)
        else:
            labels = ["Start", "Add1", "Add2", "Sub1", "Sub2", "End"]
        
        # Generate values
        start_value = 100
        values = [start_value]
        current = start_value
        
        for i in range(1, num_steps - 1):
            change = self.np_random.choice([-1, 1]) * self.np_random.uniform(10, 40)
            current += change
            values.append(change)
        
        values.append(current)  # End value
        
        data_points = []
        for label, value in zip(labels, values):
            data_points.append(DataPoint(
                label=label,
                value=round(float(value), 2),
                metadata={"type": "positive" if value >= 0 else "negative", "synthetic": True}
            ))
        
        return data_points
    
    async def _generate_funnel(
        self,
        request: Any,
        config: SyntheticDataConfig,
        merged_config: Dict[str, Any] = None
    ) -> List[DataPoint]:
        """Generate funnel chart data."""
        num_stages = getattr(config, 'num_stages', 5)
        
        # Generate stage labels
        if hasattr(request, 'enhance_labels') and request.enhance_labels:
            labels = await self._generate_funnel_labels_llm(request, num_stages)
        else:
            labels = ["Visitors", "Leads", "Qualified", "Opportunity", "Customers"]
        
        # Generate decreasing values
        start_value = 10000
        conversion_rates = getattr(config, 'conversion_rates', [1.0, 0.3, 0.1, 0.05, 0.02])
        
        data_points = []
        for i, (label, rate) in enumerate(zip(labels, conversion_rates[:num_stages])):
            value = start_value * rate
            data_points.append(DataPoint(
                label=label,
                value=round(float(value), 0),
                metadata={"conversion": rate * 100, "stage": i, "synthetic": True}
            ))
        
        return data_points
    
    async def _generate_gantt(
        self,
        request: Any,
        config: SyntheticDataConfig,
        merged_config: Dict[str, Any] = None
    ) -> List[DataPoint]:
        """Generate Gantt chart data."""
        num_tasks = getattr(config, 'num_tasks', 8)
        
        # Generate task labels
        if hasattr(request, 'enhance_labels') and request.enhance_labels:
            labels = await self._generate_task_labels_llm(request, num_tasks)
        else:
            labels = [f"Task_{i+1}" for i in range(num_tasks)]
        
        data_points = []
        start = 0
        for label in labels:
            duration = self.random_state.randint(1, 4)
            data_points.append(DataPoint(
                label=label,
                value=duration,
                metadata={"start": start, "end": start + duration, "synthetic": True}
            ))
            start += self.random_state.randint(0, 2)
        
        return data_points
    
    async def _generate_pareto(
        self,
        request: Any,
        config: SyntheticDataConfig,
        merged_config: Dict[str, Any] = None
    ) -> List[DataPoint]:
        """Generate Pareto chart data (80/20 distribution)."""
        num_categories = getattr(config, 'num_categories', 7)
        
        # Generate category labels
        if hasattr(request, 'enhance_labels') and request.enhance_labels:
            labels = await self._generate_pareto_labels_llm(request, num_categories)
        else:
            labels = [f"Cause_{i+1}" for i in range(num_categories)]
        
        # Generate Pareto distribution (exponential decay)
        values = sorted([self.np_random.exponential(100) for _ in range(num_categories)], 
                       reverse=True)
        
        # Normalize to reasonable range
        total = sum(values)
        values = [v / total * 1000 for v in values]
        
        # Calculate cumulative percentages
        cumulative = 0
        data_points = []
        for label, value in zip(labels, values):
            cumulative += value
            data_points.append(DataPoint(
                label=label,
                value=round(float(value), 2),
                metadata={
                    "percentage": round(value / sum(values) * 100, 1),
                    "cumulative": round(cumulative / sum(values) * 100, 1),
                    "synthetic": True
                }
            ))
        
        return data_points
    
    async def _generate_control(
        self,
        request: Any,
        config: SyntheticDataConfig,
        merged_config: Dict[str, Any] = None
    ) -> List[DataPoint]:
        """Generate control chart data."""
        n_points = getattr(config, 'n_points', 30)
        mean = (config.value_range[0] + config.value_range[1]) / 2
        std = (config.value_range[1] - config.value_range[0]) / 10
        
        # Generate process data
        values = self.np_random.normal(mean, std, n_points)
        
        # Add some out-of-control points
        if getattr(config, 'include_violations', True):
            violation_indices = self.np_random.choice(n_points, 2, replace=False)
            for idx in violation_indices:
                values[idx] = mean + self.np_random.choice([-1, 1]) * 3.5 * std
        
        # Generate labels
        if hasattr(request, 'enhance_labels') and request.enhance_labels:
            labels = await self._generate_sample_labels_llm(request, n_points)
        else:
            labels = [f"Sample_{i+1}" for i in range(n_points)]
        
        data_points = []
        for label, value in zip(labels, values):
            data_points.append(DataPoint(
                label=label,
                value=round(float(value), 2),
                metadata={
                    "ucl": round(mean + 3 * std, 2),
                    "lcl": round(mean - 3 * std, 2),
                    "mean": round(mean, 2),
                    "synthetic": True
                }
            ))
        
        return data_points
    
    async def _generate_error_bar(
        self,
        request: Any,
        config: SyntheticDataConfig,
        merged_config: Dict[str, Any] = None
    ) -> List[DataPoint]:
        """Generate error bar chart data."""
        n_conditions = getattr(config, 'n_conditions', 5)
        
        # Generate condition labels
        if hasattr(request, 'enhance_labels') and request.enhance_labels:
            labels = await self._generate_condition_labels_llm(request, n_conditions)
        else:
            labels = [f"Condition_{i+1}" for i in range(n_conditions)]
        
        data_points = []
        for i, label in enumerate(labels):
            mean = 50 + i * 10
            std_error = self.np_random.uniform(2, 5)
            
            data_points.append(DataPoint(
                label=label,
                value=round(float(mean), 2),
                metadata={"error": round(float(std_error), 2), "synthetic": True}
            ))
        
        return data_points
    
    async def _generate_dense_scatter(
        self,
        request: Any,
        config: SyntheticDataConfig,
        merged_config: Dict[str, Any] = None
    ) -> List[DataPoint]:
        """Generate dense scatter data for hexbin plots."""
        n_points = getattr(config, 'n_points', 10000)
        n_clusters = getattr(config, 'n_clusters', 3)
        
        # Generate cluster centers
        cluster_centers = [(self.np_random.uniform(100, 700), 
                           self.np_random.uniform(100, 700)) 
                          for _ in range(n_clusters)]
        
        points_per_cluster = n_points // n_clusters
        data_points = []
        
        for i, (cx, cy) in enumerate(cluster_centers):
            for j in range(points_per_cluster):
                x = self.np_random.normal(cx, 50)
                y = self.np_random.normal(cy, 50)
                
                data_points.append(DataPoint(
                    label=f"Point_{i*points_per_cluster+j}",
                    value=round(float(y), 2),
                    metadata={"x": round(float(x), 2), "y": round(float(y), 2), 
                             "cluster": i, "synthetic": True}
                ))
        
        return data_points
    
    # LLM Label Generation Methods
    
    async def _generate_time_labels_llm(self, request: Any, count: int) -> List[str]:
        """Generate time-based labels using LLM."""
        prompt = f"""
        Generate {count} time-based labels for a chart.
        Context: {request.content if hasattr(request, 'content') else 'Time series data'}
        
        Requirements:
        - Sequential time periods
        - Consistent format
        - Professional naming
        
        Return as JSON array of strings.
        Example: ["Jan 2024", "Feb 2024", "Mar 2024"]
        """
        
        try:
            result = await self.llm_agent.run(prompt)
            labels = json.loads(result.data)
            return labels[:count]
        except:
            # Fallback to default
            return [f"Period_{i+1}" for i in range(count)]
    
    async def _generate_category_labels_llm(self, request: Any, count: int) -> List[str]:
        """Generate category labels using LLM."""
        prompt = f"""
        Generate {count} category labels for a bar chart.
        Context: {request.content if hasattr(request, 'content') else 'Category comparison'}
        
        Requirements:
        - Clear, distinct categories
        - Industry-appropriate naming
        - Consistent style
        
        Return as JSON array of strings.
        Example: ["North America", "Europe", "Asia Pacific"]
        """
        
        try:
            result = await self.llm_agent.run(prompt)
            labels = json.loads(result.data)
            return labels[:count]
        except:
            return [f"Category_{chr(65+i)}" for i in range(count)]
    
    async def _generate_segment_labels_llm(self, request: Any, count: int) -> List[str]:
        """Generate segment labels for pie charts using LLM."""
        prompt = f"""
        Generate {count} segment labels for a pie chart.
        Context: {request.content if hasattr(request, 'content') else 'Market share distribution'}
        
        Requirements:
        - Represent parts of a whole
        - Professional terminology
        - Clear and concise
        
        Return as JSON array of strings.
        Example: ["Enterprise", "SMB", "Startup", "Individual", "Government"]
        """
        
        try:
            result = await self.llm_agent.run(prompt)
            labels = json.loads(result.data)
            return labels[:count]
        except:
            return [f"Segment_{chr(65+i)}" for i in range(count)]
    
    async def _generate_series_labels_llm(self, request: Any, count: int) -> List[str]:
        """Generate series labels for multi-series charts."""
        prompt = f"""
        Generate {count} series labels for a multi-series chart.
        Context: {request.content if hasattr(request, 'content') else 'Multiple data series'}
        
        Requirements:
        - Distinct series names
        - Related to the context
        - Short and clear
        
        Return as JSON array of strings.
        Example: ["Product A", "Product B", "Product C"]
        """
        
        try:
            result = await self.llm_agent.run(prompt)
            labels = json.loads(result.data)
            return labels[:count]
        except:
            return [f"Series_{chr(65+i)}" for i in range(count)]
    
    async def _generate_group_labels_llm(self, request: Any, count: int) -> List[str]:
        """Generate group labels for grouped charts."""
        prompt = f"""
        Generate {count} group labels for a grouped chart.
        Context: {request.content if hasattr(request, 'content') else 'Group comparison'}
        
        Requirements:
        - Distinct group names
        - Logical grouping
        - Professional naming
        
        Return as JSON array of strings.
        Example: ["Q1 2024", "Q2 2024", "Q3 2024", "Q4 2024"]
        """
        
        try:
            result = await self.llm_agent.run(prompt)
            labels = json.loads(result.data)
            return labels[:count]
        except:
            return [f"Group_{i+1}" for i in range(count)]
    
    async def _generate_dimension_labels_llm(self, request: Any, count: int) -> List[str]:
        """Generate dimension labels for radar charts."""
        prompt = f"""
        Generate {count} dimension labels for a radar chart.
        Context: {request.content if hasattr(request, 'content') else 'Multi-dimensional comparison'}
        
        Requirements:
        - Different aspects or metrics
        - Measurable dimensions
        - Clear and specific
        
        Return as JSON array of strings.
        Example: ["Performance", "Quality", "Cost", "Reliability", "Innovation", "Support"]
        """
        
        try:
            result = await self.llm_agent.run(prompt)
            labels = json.loads(result.data)
            return labels[:count]
        except:
            return [f"Dimension_{i+1}" for i in range(count)]
    
    async def _generate_entity_labels_llm(self, request: Any, count: int) -> List[str]:
        """Generate entity labels for bubble charts."""
        prompt = f"""
        Generate {count} entity labels for a bubble chart.
        Context: {request.content if hasattr(request, 'content') else 'Entity comparison'}
        
        Requirements:
        - Distinct entity names
        - Context-appropriate
        - Professional naming
        
        Return as JSON array of strings.
        Example: ["Company A", "Company B", "Company C"]
        """
        
        try:
            result = await self.llm_agent.run(prompt)
            labels = json.loads(result.data)
            return labels[:count]
        except:
            return [f"Entity_{chr(65+i)}" for i in range(count)]
    
    async def _generate_point_labels_llm(self, request: Any, count: int) -> List[str]:
        """Generate point labels for scatter plots."""
        # For scatter plots with many points, simple numbered labels are often best
        return [f"P{i+1}" for i in range(count)]
    
    async def _generate_row_labels_llm(self, request: Any, count: int) -> List[str]:
        """Generate row labels for heatmaps."""
        prompt = f"""
        Generate {count} row labels for a heatmap.
        Context: {request.content if hasattr(request, 'content') else 'Matrix data'}
        
        Requirements:
        - Row identifiers
        - Consistent format
        - Clear and concise
        
        Return as JSON array of strings.
        Example: ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        """
        
        try:
            result = await self.llm_agent.run(prompt)
            labels = json.loads(result.data)
            return labels[:count]
        except:
            return [f"Row_{i+1}" for i in range(count)]
    
    async def _generate_column_labels_llm(self, request: Any, count: int) -> List[str]:
        """Generate column labels for heatmaps."""
        prompt = f"""
        Generate {count} column labels for a heatmap.
        Context: {request.content if hasattr(request, 'content') else 'Matrix data'}
        
        Requirements:
        - Column identifiers
        - Consistent format
        - Clear and concise
        
        Return as JSON array of strings.
        Example: ["9AM", "10AM", "11AM", "12PM", "1PM", "2PM", "3PM"]
        """
        
        try:
            result = await self.llm_agent.run(prompt)
            labels = json.loads(result.data)
            return labels[:count]
        except:
            return [f"Col_{i+1}" for i in range(count)]
    
    async def _generate_waterfall_labels_llm(self, request: Any, count: int) -> List[str]:
        """Generate waterfall chart labels."""
        prompt = f"""
        Generate {count} labels for a waterfall chart showing incremental changes.
        Context: {request.content if hasattr(request, 'content') else 'Financial waterfall'}
        
        Requirements:
        - Start value, changes, end value
        - Clear cause-effect labels
        - Professional terminology
        
        Return as JSON array of strings.
        Example: ["Starting Revenue", "New Customers", "Upsells", "Churn", "Discounts", "Final Revenue"]
        """
        
        try:
            result = await self.llm_agent.run(prompt)
            labels = json.loads(result.data)
            return labels[:count]
        except:
            return ["Start"] + [f"Change_{i}" for i in range(1, count-1)] + ["End"]
    
    async def _generate_funnel_labels_llm(self, request: Any, count: int) -> List[str]:
        """Generate funnel chart labels."""
        prompt = f"""
        Generate {count} stage labels for a funnel chart.
        Context: {request.content if hasattr(request, 'content') else 'Sales funnel'}
        
        Requirements:
        - Sequential stages
        - Decreasing population
        - Clear progression
        
        Return as JSON array of strings.
        Example: ["Awareness", "Interest", "Consideration", "Intent", "Purchase"]
        """
        
        try:
            result = await self.llm_agent.run(prompt)
            labels = json.loads(result.data)
            return labels[:count]
        except:
            return [f"Stage_{i+1}" for i in range(count)]
    
    async def _generate_task_labels_llm(self, request: Any, count: int) -> List[str]:
        """Generate task labels for Gantt charts."""
        prompt = f"""
        Generate {count} task labels for a Gantt chart.
        Context: {request.content if hasattr(request, 'content') else 'Project timeline'}
        
        Requirements:
        - Project task names
        - Action-oriented
        - Clear and specific
        
        Return as JSON array of strings.
        Example: ["Planning", "Design", "Development", "Testing", "Deployment", "Review"]
        """
        
        try:
            result = await self.llm_agent.run(prompt)
            labels = json.loads(result.data)
            return labels[:count]
        except:
            return [f"Task_{i+1}" for i in range(count)]
    
    async def _generate_pareto_labels_llm(self, request: Any, count: int) -> List[str]:
        """Generate Pareto chart labels."""
        prompt = f"""
        Generate {count} cause/category labels for a Pareto chart (80/20 analysis).
        Context: {request.content if hasattr(request, 'content') else 'Root cause analysis'}
        
        Requirements:
        - Problem causes or categories
        - Ordered by importance
        - Clear and specific
        
        Return as JSON array of strings.
        Example: ["Equipment Failure", "Human Error", "Material Defect", "Process Issue", "Design Flaw", "Other"]
        """
        
        try:
            result = await self.llm_agent.run(prompt)
            labels = json.loads(result.data)
            return labels[:count]
        except:
            return [f"Cause_{i+1}" for i in range(count)]
    
    async def _generate_sample_labels_llm(self, request: Any, count: int) -> List[str]:
        """Generate sample labels for control charts."""
        # For control charts, simple sequential labels are usually best
        return [f"S{i+1}" for i in range(count)]
    
    async def _generate_condition_labels_llm(self, request: Any, count: int) -> List[str]:
        """Generate condition labels for error bar charts."""
        prompt = f"""
        Generate {count} experimental condition labels for an error bar chart.
        Context: {request.content if hasattr(request, 'content') else 'Experimental conditions'}
        
        Requirements:
        - Test conditions or treatments
        - Scientific/technical naming
        - Clear differentiation
        
        Return as JSON array of strings.
        Example: ["Control", "Treatment A", "Treatment B", "Combined", "Placebo"]
        """
        
        try:
            result = await self.llm_agent.run(prompt)
            labels = json.loads(result.data)
            return labels[:count]
        except:
            return [f"Condition_{i+1}" for i in range(count)]
    
    def _calculate_statistics(self, values: List[float]) -> DataStatistics:
        """Calculate statistics for a set of values."""
        if not values:
            return DataStatistics(
                min=0, max=0, mean=0, median=0, std=0, total=0, count=0
            )
        
        return DataStatistics(
            min=round(float(np.min(values)), 2),
            max=round(float(np.max(values)), 2),
            mean=round(float(np.mean(values)), 2),
            median=round(float(np.median(values)), 2),
            std=round(float(np.std(values)), 2),
            total=round(float(np.sum(values)), 2),
            count=len(values)
        )
    
    def format_data_for_chart(
        self,
        data_points: List[DataPoint],
        chart_type: ChartType
    ) -> ChartData:
        """Format data points for chart consumption and table display."""
        labels = []
        values = []
        series_data = {}
        categories = set()
        
        for dp in data_points:
            labels.append(dp.label)
            values.append(dp.value)
            
            if dp.series:
                if dp.series not in series_data:
                    series_data[dp.series] = []
                series_data[dp.series].append({"label": dp.label, "value": dp.value})
            
            if dp.category:
                categories.add(dp.category)
        
        # Format series data
        series_list = []
        if series_data:
            for series_name, series_values in series_data.items():
                series_list.append({
                    "name": series_name,
                    "data": series_values
                })
        
        # Calculate statistics
        statistics = self._calculate_statistics(values)
        
        # Create table-ready format
        table_data = []
        table_columns = []
        
        if series_data:
            # Multi-series data: create pivot table format
            table_columns = ["Label"] + list(series_data.keys())
            
            # Get unique labels
            unique_labels = []
            seen = set()
            for dp in data_points:
                if dp.label not in seen:
                    unique_labels.append(dp.label)
                    seen.add(dp.label)
            
            # Create rows with series as columns
            for label in unique_labels:
                row = {"Label": label}
                for series_name in series_data.keys():
                    # Find value for this label and series
                    series_value = next(
                        (dp.value for dp in data_points 
                         if dp.label == label and dp.series == series_name), 
                        None
                    )
                    row[series_name] = series_value
                table_data.append(row)
                
        elif categories:
            # Grouped data: include category column
            table_columns = ["Label", "Category", "Value"]
            
            for dp in data_points:
                row = {
                    "Label": dp.label,
                    "Category": dp.category if dp.category else "",
                    "Value": dp.value
                }
                table_data.append(row)
                
        else:
            # Simple data: basic label-value pairs
            table_columns = ["Label", "Value"]
            
            for dp in data_points:
                row = {
                    "Label": dp.label,
                    "Value": dp.value
                }
                
                # Add relevant metadata fields if present
                if dp.metadata:
                    for key, val in dp.metadata.items():
                        # Skip internal metadata
                        if key not in ["synthetic", "raw_value", "time_index", "series_index"]:
                            if key not in table_columns:
                                table_columns.append(key.replace("_", " ").title())
                            row[key.replace("_", " ").title()] = val
                            
                table_data.append(row)
        
        return ChartData(
            labels=labels,
            values=values,
            series=series_list if series_list else None,
            categories=list(categories) if categories else None,
            statistics=statistics,
            raw_data=data_points,
            table_data=table_data,
            table_columns=table_columns
        )