"""
Analytics Playbook V2
=====================

Complete specifications for all 23 chart types with enhanced configuration.
Includes when_to_use rules, data requirements, theme support, and synthetic data features.

Author: Analytics Agent System V2
Date: 2024
Version: 2.0
"""

from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)


ANALYTICS_PLAYBOOK_V2 = {
    "version": "2.0",
    "default_library": "matplotlib",
    "charts": {
        # ============== TREND CHARTS ==============
        "line_chart": {
            "name": "Line Chart",
            "category": "trend",
            "renderer": "matplotlib",
            "when_to_use": [
                "Trend over time or ordered x-axis",
                "Multiple series comparison (up to 5)",
                "Show patterns, seasonality, anomalies",
                "Continuous data progression"
            ],
            "data_requirements": [
                {"role": "x", "type": "time|ordered_category", "required": True},
                {"role": "y", "type": "numeric", "required": True},
                {"role": "series", "type": "category", "required": False, "max": 5}
            ],
            "theme_config": {
                "supports_gradient": False,
                "color_application": "per_series",
                "uses_primary": True,
                "uses_secondary": True,
                "uses_tertiary": True
            },
            "synthetic_features": {
                "rows": 100,
                "num_series": 1,
                "pattern": "linear_trend|seasonal",
                "noise_level": 0.1,
                "anomalies": {"count": 3, "magnitude": 2.0}
            },
            "plotting_api": {
                "function": "ax.plot",
                "params": ["x", "y", "label", "color", "linewidth", "marker"]
            }
        },
        
        "step_chart": {
            "name": "Step Chart",
            "category": "trend",
            "renderer": "matplotlib",
            "when_to_use": [
                "Discrete state changes",
                "Inventory levels over time",
                "Price tiers or rate changes",
                "Values that change at specific points"
            ],
            "data_requirements": [
                {"role": "x", "type": "time|ordered_category", "required": True},
                {"role": "y", "type": "numeric", "required": True}
            ],
            "theme_config": {
                "supports_gradient": False,
                "color_application": "single",
                "uses_primary": True
            },
            "synthetic_features": {
                "rows": 60,
                "pattern": "piecewise_constant",
                "num_steps": 6,
                "noise_level": 0.0
            },
            "plotting_api": {
                "function": "ax.step",
                "params": ["x", "y", "where", "color", "linewidth"]
            }
        },
        
        "area_chart": {
            "name": "Area Chart",
            "category": "trend",
            "renderer": "matplotlib",
            "when_to_use": [
                "Emphasize magnitude over time",
                "Show volume or accumulation",
                "Single series with filled area",
                "Highlight total area under curve"
            ],
            "data_requirements": [
                {"role": "x", "type": "time|ordered_category", "required": True},
                {"role": "y", "type": "numeric", "required": True}
            ],
            "theme_config": {
                "supports_gradient": True,
                "color_application": "gradient",
                "uses_primary": True,
                "uses_secondary": True
            },
            "synthetic_features": {
                "rows": 100,
                "pattern": "cumulative",
                "noise_level": 0.05
            },
            "plotting_api": {
                "function": "ax.fill_between",
                "params": ["x", "y", "alpha", "color"]
            }
        },
        
        "stacked_area_chart": {
            "name": "Stacked Area Chart",
            "category": "trend",
            "renderer": "matplotlib",
            "when_to_use": [
                "Show composition over time",
                "Multiple series that sum to total",
                "Part-to-whole relationships changing over time",
                "Cumulative contributions"
            ],
            "data_requirements": [
                {"role": "x", "type": "time|ordered_category", "required": True},
                {"role": "y", "type": "numeric", "required": True},
                {"role": "series", "type": "category", "required": True, "min": 2, "max": 6}
            ],
            "theme_config": {
                "supports_gradient": False,
                "color_application": "per_series",
                "uses_primary": True,
                "uses_secondary": True,
                "uses_tertiary": True
            },
            "synthetic_features": {
                "rows": 50,
                "num_series": 4,
                "pattern": "cumulative",
                "noise_level": 0.05
            },
            "plotting_api": {
                "function": "ax.stackplot",
                "params": ["x", "y_arrays", "labels", "colors", "alpha"]
            }
        },
        
        # ============== BAR CHARTS ==============
        "bar_chart_vertical": {
            "name": "Vertical Bar Chart",
            "category": "comparison",
            "renderer": "matplotlib",
            "when_to_use": [
                "Compare discrete categories",
                "Show ranking or ordering",
                "Display counts or totals",
                "Categories on x-axis"
            ],
            "data_requirements": [
                {"role": "categories", "type": "category", "required": True},
                {"role": "values", "type": "numeric", "required": True}
            ],
            "theme_config": {
                "supports_gradient": True,
                "color_application": "gradient|single",
                "uses_primary": True,
                "uses_secondary": True
            },
            "synthetic_features": {
                "num_categories": 8,
                "value_range": [50, 200],
                "distribution": "uniform"
            },
            "plotting_api": {
                "function": "ax.bar",
                "params": ["x", "height", "color", "edgecolor", "width"]
            }
        },
        
        "bar_chart_horizontal": {
            "name": "Horizontal Bar Chart",
            "category": "comparison",
            "renderer": "matplotlib",
            "when_to_use": [
                "Long category names",
                "Rankings or ratings",
                "When reading left-to-right is natural",
                "Space constraints favor horizontal layout"
            ],
            "data_requirements": [
                {"role": "categories", "type": "category", "required": True},
                {"role": "values", "type": "numeric", "required": True}
            ],
            "theme_config": {
                "supports_gradient": True,
                "color_application": "gradient|single",
                "uses_primary": True,
                "uses_secondary": True
            },
            "synthetic_features": {
                "num_categories": 10,
                "value_range": [0, 100],
                "distribution": "normal"
            },
            "plotting_api": {
                "function": "ax.barh",
                "params": ["y", "width", "color", "edgecolor", "height"]
            }
        },
        
        "grouped_bar_chart": {
            "name": "Grouped Bar Chart",
            "category": "comparison",
            "renderer": "matplotlib",
            "when_to_use": [
                "Compare multiple series across categories",
                "Side-by-side comparison",
                "Show relationships between groups",
                "2-3 series optimal"
            ],
            "data_requirements": [
                {"role": "categories", "type": "category", "required": True},
                {"role": "values", "type": "numeric", "required": True},
                {"role": "groups", "type": "category", "required": True, "min": 2, "max": 4}
            ],
            "theme_config": {
                "supports_gradient": False,
                "color_application": "per_group",
                "uses_primary": True,
                "uses_secondary": True,
                "uses_tertiary": True
            },
            "synthetic_features": {
                "num_categories": 6,
                "num_groups": 3,
                "value_range": [30, 150]
            },
            "plotting_api": {
                "function": "ax.bar",
                "params": ["x", "height", "width", "label", "color"]
            }
        },
        
        "stacked_bar_chart": {
            "name": "Stacked Bar Chart",
            "category": "composition",
            "renderer": "matplotlib",
            "when_to_use": [
                "Show composition within categories",
                "Part-to-whole for each category",
                "Compare totals and components",
                "Space-efficient for multiple series"
            ],
            "data_requirements": [
                {"role": "categories", "type": "category", "required": True},
                {"role": "values", "type": "numeric", "required": True},
                {"role": "stacks", "type": "category", "required": True, "min": 2, "max": 6}
            ],
            "theme_config": {
                "supports_gradient": False,
                "color_application": "per_stack",
                "uses_primary": True,
                "uses_secondary": True,
                "uses_tertiary": True
            },
            "synthetic_features": {
                "num_categories": 6,
                "num_stacks": 4,
                "value_range": [10, 50]
            },
            "plotting_api": {
                "function": "ax.bar",
                "params": ["x", "height", "bottom", "label", "color"]
            }
        },
        
        # ============== DISTRIBUTION CHARTS ==============
        "histogram": {
            "name": "Histogram",
            "category": "distribution",
            "renderer": "matplotlib",
            "when_to_use": [
                "Show frequency distribution",
                "Analyze data spread",
                "Identify patterns in continuous data",
                "Find outliers or clusters"
            ],
            "data_requirements": [
                {"role": "values", "type": "numeric", "required": True, "min_points": 30}
            ],
            "theme_config": {
                "supports_gradient": True,
                "color_application": "single",
                "uses_primary": True
            },
            "synthetic_features": {
                "n": 1000,
                "distribution": "normal|bimodal|lognormal",
                "bins": 30
            },
            "plotting_api": {
                "function": "ax.hist",
                "params": ["x", "bins", "color", "edgecolor", "alpha"]
            }
        },
        
        "box_plot": {
            "name": "Box Plot",
            "category": "distribution",
            "renderer": "matplotlib",
            "when_to_use": [
                "Compare distributions across groups",
                "Show quartiles and outliers",
                "Statistical summary visualization",
                "Identify data spread and skewness"
            ],
            "data_requirements": [
                {"role": "values", "type": "numeric", "required": True},
                {"role": "groups", "type": "category", "required": False}
            ],
            "theme_config": {
                "supports_gradient": False,
                "color_application": "per_group",
                "uses_primary": True,
                "uses_secondary": True
            },
            "synthetic_features": {
                "n_groups": 4,
                "n_per_group": 100,
                "include_outliers": True
            },
            "plotting_api": {
                "function": "ax.boxplot",
                "params": ["x", "positions", "widths", "patch_artist", "boxprops"]
            }
        },
        
        "violin_plot": {
            "name": "Violin Plot",
            "category": "distribution",
            "renderer": "matplotlib",
            "when_to_use": [
                "Show distribution shape",
                "Compare distributions with density",
                "Combine box plot with kernel density",
                "Identify multimodal distributions"
            ],
            "data_requirements": [
                {"role": "values", "type": "numeric", "required": True},
                {"role": "groups", "type": "category", "required": False}
            ],
            "theme_config": {
                "supports_gradient": False,
                "color_application": "per_group",
                "uses_primary": True,
                "uses_secondary": True,
                "uses_tertiary": True
            },
            "synthetic_features": {
                "n_groups": 4,
                "n_per_group": 100,
                "distribution": "bimodal"
            },
            "plotting_api": {
                "function": "ax.violinplot",
                "params": ["dataset", "positions", "widths", "showmeans", "showmedians"]
            }
        },
        
        # ============== CORRELATION CHARTS ==============
        "scatter_plot": {
            "name": "Scatter Plot",
            "category": "correlation",
            "renderer": "matplotlib",
            "when_to_use": [
                "Show relationship between two variables",
                "Identify correlations",
                "Find clusters or patterns",
                "Detect outliers"
            ],
            "data_requirements": [
                {"role": "x", "type": "numeric", "required": True},
                {"role": "y", "type": "numeric", "required": True},
                {"role": "color", "type": "category|numeric", "required": False}
            ],
            "theme_config": {
                "supports_gradient": True,
                "color_application": "by_value|single",
                "uses_primary": True,
                "uses_secondary": True
            },
            "synthetic_features": {
                "n_points": 100,
                "correlation": 0.7,
                "noise_level": 0.2
            },
            "plotting_api": {
                "function": "ax.scatter",
                "params": ["x", "y", "c", "s", "alpha", "cmap"]
            }
        },
        
        "bubble_chart": {
            "name": "Bubble Chart",
            "category": "correlation",
            "renderer": "matplotlib",
            "when_to_use": [
                "Three-dimensional data visualization",
                "Size represents third variable",
                "Compare multiple entities",
                "Show market positioning"
            ],
            "data_requirements": [
                {"role": "x", "type": "numeric", "required": True},
                {"role": "y", "type": "numeric", "required": True},
                {"role": "size", "type": "numeric", "required": True},
                {"role": "color", "type": "category", "required": False}
            ],
            "theme_config": {
                "supports_gradient": True,
                "color_application": "by_category",
                "uses_primary": True,
                "uses_secondary": True,
                "uses_tertiary": True
            },
            "synthetic_features": {
                "n_points": 15,
                "size_range": [100, 1000]
            },
            "plotting_api": {
                "function": "ax.scatter",
                "params": ["x", "y", "s", "c", "alpha", "edgecolors"]
            }
        },
        
        "hexbin": {
            "name": "Hexbin Plot",
            "category": "correlation",
            "renderer": "matplotlib",
            "when_to_use": [
                "Dense scatter data",
                "Show density patterns",
                "Large datasets (1000+ points)",
                "Heatmap-like correlation"
            ],
            "data_requirements": [
                {"role": "x", "type": "numeric", "required": True},
                {"role": "y", "type": "numeric", "required": True}
            ],
            "theme_config": {
                "supports_gradient": True,
                "color_application": "density_map",
                "uses_primary": True,
                "uses_tertiary": True
            },
            "synthetic_features": {
                "n_points": 10000,
                "n_clusters": 3
            },
            "plotting_api": {
                "function": "ax.hexbin",
                "params": ["x", "y", "gridsize", "cmap", "mincnt"]
            }
        },
        
        # ============== COMPOSITION CHARTS ==============
        "pie_chart": {
            "name": "Pie Chart",
            "category": "composition",
            "renderer": "mermaid",
            "when_to_use": [
                "Show parts of a whole",
                "Percentage breakdown",
                "5-7 categories optimal",
                "Sum equals 100%"
            ],
            "data_requirements": [
                {"role": "categories", "type": "category", "required": True},
                {"role": "values", "type": "numeric", "required": True, "constraint": "positive"}
            ],
            "theme_config": {
                "supports_gradient": False,
                "color_application": "per_slice",
                "uses_primary": True,
                "uses_secondary": True,
                "uses_tertiary": True
            },
            "synthetic_features": {
                "num_segments": 5,
                "ensure_sum_100": True
            },
            "plotting_api": {
                "function": "ax.pie",
                "params": ["x", "labels", "colors", "autopct", "startangle"]
            }
        },
        
        "waterfall": {
            "name": "Waterfall Chart",
            "category": "composition",
            "renderer": "matplotlib",
            "when_to_use": [
                "Show incremental changes",
                "Bridge between start and end values",
                "Profit/loss analysis",
                "Cumulative effect of sequential values"
            ],
            "data_requirements": [
                {"role": "categories", "type": "category", "required": True},
                {"role": "values", "type": "numeric", "required": True},
                {"role": "type", "type": "category", "values": ["increase", "decrease", "total"]}
            ],
            "theme_config": {
                "supports_gradient": False,
                "color_application": "by_value_sign",
                "uses_primary": True,
                "uses_secondary": True,
                "uses_tertiary": True
            },
            "synthetic_features": {
                "num_steps": 6,
                "include_total": True
            },
            "plotting_api": {
                "function": "custom_waterfall",
                "params": ["categories", "values", "colors"]
            }
        },
        
        "funnel": {
            "name": "Funnel Chart",
            "category": "composition",
            "renderer": "matplotlib",
            "when_to_use": [
                "Show process stages",
                "Conversion rates",
                "Sales pipeline",
                "Sequential reduction"
            ],
            "data_requirements": [
                {"role": "stages", "type": "category", "required": True},
                {"role": "values", "type": "numeric", "required": True, "constraint": "decreasing"}
            ],
            "theme_config": {
                "supports_gradient": True,
                "color_application": "gradient",
                "uses_primary": True,
                "uses_secondary": True
            },
            "synthetic_features": {
                "num_stages": 5,
                "conversion_rates": [1.0, 0.3, 0.1, 0.05, 0.02]
            },
            "plotting_api": {
                "function": "custom_funnel",
                "params": ["stages", "values", "colors"]
            }
        },
        
        # ============== COMPARISON CHARTS ==============
        "radar_chart": {
            "name": "Radar Chart",
            "category": "comparison",
            "renderer": "matplotlib",
            "when_to_use": [
                "Multi-dimensional comparison",
                "Performance across metrics",
                "Strengths and weaknesses",
                "3-8 dimensions optimal"
            ],
            "data_requirements": [
                {"role": "dimensions", "type": "category", "required": True, "min": 3, "max": 8},
                {"role": "values", "type": "numeric", "required": True},
                {"role": "series", "type": "category", "required": False, "max": 3}
            ],
            "theme_config": {
                "supports_gradient": False,
                "color_application": "per_series",
                "uses_primary": True,
                "uses_secondary": True,
                "uses_tertiary": True
            },
            "synthetic_features": {
                "num_dimensions": 6,
                "num_series": 2,
                "value_range": [0, 100]
            },
            "plotting_api": {
                "function": "ax.plot",
                "params": ["angles", "values", "color", "linewidth", "marker"]
            }
        },
        
        "heatmap": {
            "name": "Heatmap",
            "category": "comparison",
            "renderer": "matplotlib",
            "when_to_use": [
                "Matrix data visualization",
                "Correlation matrices",
                "Time vs category patterns",
                "Intensity representation"
            ],
            "data_requirements": [
                {"role": "rows", "type": "category", "required": True},
                {"role": "columns", "type": "category", "required": True},
                {"role": "values", "type": "numeric", "required": True}
            ],
            "theme_config": {
                "supports_gradient": True,
                "color_application": "colormap",
                "uses_primary": True,
                "uses_tertiary": True
            },
            "synthetic_features": {
                "shape": [7, 7],
                "value_range": [-1, 1]
            },
            "plotting_api": {
                "function": "ax.imshow",
                "params": ["data", "cmap", "aspect", "interpolation"]
            }
        },
        
        # ============== STATISTICAL CHARTS ==============
        "error_bar_chart": {
            "name": "Error Bar Chart",
            "category": "statistical",
            "renderer": "matplotlib",
            "when_to_use": [
                "Show measurement uncertainty",
                "Confidence intervals",
                "Scientific data",
                "Statistical significance"
            ],
            "data_requirements": [
                {"role": "x", "type": "category|numeric", "required": True},
                {"role": "y", "type": "numeric", "required": True},
                {"role": "error", "type": "numeric", "required": True}
            ],
            "theme_config": {
                "supports_gradient": False,
                "color_application": "single",
                "uses_primary": True
            },
            "synthetic_features": {
                "n_conditions": 5,
                "error_type": "std|sem|ci95"
            },
            "plotting_api": {
                "function": "ax.errorbar",
                "params": ["x", "y", "yerr", "fmt", "color", "capsize"]
            }
        },
        
        "control_chart": {
            "name": "Control Chart",
            "category": "statistical",
            "renderer": "matplotlib",
            "when_to_use": [
                "Process monitoring",
                "Quality control",
                "Identify out-of-control points",
                "Show control limits"
            ],
            "data_requirements": [
                {"role": "x", "type": "time|ordered", "required": True},
                {"role": "y", "type": "numeric", "required": True},
                {"role": "limits", "type": "numeric", "required": True}
            ],
            "theme_config": {
                "supports_gradient": False,
                "color_application": "by_status",
                "uses_primary": True,
                "uses_secondary": True,
                "uses_tertiary": True
            },
            "synthetic_features": {
                "n_points": 30,
                "include_violations": True
            },
            "plotting_api": {
                "function": "ax.plot",
                "params": ["x", "y", "color", "marker", "linestyle"]
            }
        },
        
        "pareto": {
            "name": "Pareto Chart",
            "category": "statistical",
            "renderer": "matplotlib",
            "when_to_use": [
                "80/20 analysis",
                "Prioritize issues",
                "Cumulative impact",
                "Root cause analysis"
            ],
            "data_requirements": [
                {"role": "categories", "type": "category", "required": True},
                {"role": "values", "type": "numeric", "required": True}
            ],
            "theme_config": {
                "supports_gradient": True,
                "color_application": "dual_axis",
                "uses_primary": True,
                "uses_secondary": True
            },
            "synthetic_features": {
                "num_categories": 7,
                "pareto_distribution": True
            },
            "plotting_api": {
                "function": "ax.bar+ax.plot",
                "params": ["x", "height", "cumulative_line"]
            }
        },
        
        # ============== PROJECT CHARTS ==============
        "gantt": {
            "name": "Gantt Chart",
            "category": "project",
            "renderer": "matplotlib",
            "when_to_use": [
                "Project timeline",
                "Task scheduling",
                "Resource planning",
                "Dependencies visualization"
            ],
            "data_requirements": [
                {"role": "tasks", "type": "category", "required": True},
                {"role": "start", "type": "time", "required": True},
                {"role": "duration", "type": "numeric", "required": True},
                {"role": "dependencies", "type": "category", "required": False}
            ],
            "theme_config": {
                "supports_gradient": False,
                "color_application": "by_status",
                "uses_primary": True,
                "uses_secondary": True,
                "uses_tertiary": True
            },
            "synthetic_features": {
                "num_tasks": 8,
                "include_dependencies": True
            },
            "plotting_api": {
                "function": "ax.barh",
                "params": ["y", "width", "left", "color", "edgecolor"]
            }
        }
    }
}


def get_chart_spec(chart_type: str) -> Optional[Dict[str, Any]]:
    """Get specification for a specific chart type."""
    return ANALYTICS_PLAYBOOK_V2["charts"].get(chart_type)


def get_charts_by_category(category: str) -> List[str]:
    """Get all charts in a specific category."""
    charts = []
    for chart_type, spec in ANALYTICS_PLAYBOOK_V2["charts"].items():
        if spec.get("category") == category:
            charts.append(chart_type)
    return charts


def get_chart_when_to_use(chart_type: str) -> List[str]:
    """Get when_to_use rules for a chart type."""
    spec = get_chart_spec(chart_type)
    return spec.get("when_to_use", []) if spec else []


def get_chart_theme_config(chart_type: str) -> Dict[str, Any]:
    """Get theme configuration for a chart type."""
    spec = get_chart_spec(chart_type)
    return spec.get("theme_config", {}) if spec else {}


def get_chart_synthetic_features(chart_type: str) -> Dict[str, Any]:
    """Get synthetic data features for a chart type."""
    spec = get_chart_spec(chart_type)
    return spec.get("synthetic_features", {}) if spec else {}


def find_charts_for_intent(intent: str) -> List[str]:
    """Find charts matching a specific intent or use case."""
    matching_charts = []
    intent_lower = intent.lower()
    
    for chart_type, spec in ANALYTICS_PLAYBOOK_V2["charts"].items():
        when_to_use = spec.get("when_to_use", [])
        for rule in when_to_use:
            if intent_lower in rule.lower():
                matching_charts.append(chart_type)
                break
    
    return matching_charts


def get_all_chart_types() -> List[str]:
    """Get list of all supported chart types."""
    return list(ANALYTICS_PLAYBOOK_V2["charts"].keys())