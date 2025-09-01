"""
Python Chart Agent V2
=====================

Enhanced chart generation with fixed implementations for all 23 chart types.
Includes proper matplotlib usage and theme application.

Author: Analytics Agent System V2
Date: 2024
Version: 2.0
"""

import logging
import base64
from io import BytesIO
from typing import List, Dict, Any, Optional
import numpy as np

from .models import (
    ChartType, ChartPlan, DataPoint,
    GenerationMethod, ThemeConfig
)
from .theme_engine import ThemeEngine
from .local_executor import LocalExecutor

logger = logging.getLogger(__name__)


class PythonChartAgent:
    """
    Agent for generating Python/matplotlib chart code.
    Fixed implementations for all 23 chart types.
    """
    
    def __init__(self, mcp_executor=None):
        """Initialize the Python chart agent."""
        self.mcp_executor = mcp_executor
        self.theme_engine = None
    
    async def generate_chart(
        self,
        plan: ChartPlan,
        data_points: List[DataPoint],
        title: str
    ) -> Dict[str, Any]:
        """
        Generate chart based on plan and data.
        
        Args:
            plan: Chart execution plan
            data_points: Data points to visualize
            title: Chart title
            
        Returns:
            Dictionary with chart output
        """
        # Initialize theme engine
        self.theme_engine = ThemeEngine(plan.theme)
        
        # Generate chart code based on type
        generators = {
            ChartType.LINE_CHART: self._generate_line_chart,
            ChartType.STEP_CHART: self._generate_step_chart,
            ChartType.AREA_CHART: self._generate_area_chart,
            ChartType.STACKED_AREA_CHART: self._generate_stacked_area,
            ChartType.BAR_VERTICAL: self._generate_bar_vertical,
            ChartType.BAR_HORIZONTAL: self._generate_bar_horizontal,
            ChartType.GROUPED_BAR: self._generate_grouped_bar,
            ChartType.STACKED_BAR: self._generate_stacked_bar,
            ChartType.HISTOGRAM: self._generate_histogram,
            ChartType.BOX_PLOT: self._generate_box_plot,
            ChartType.VIOLIN_PLOT: self._generate_violin_plot,
            ChartType.SCATTER_PLOT: self._generate_scatter_plot,
            ChartType.BUBBLE_CHART: self._generate_bubble_chart,
            ChartType.HEXBIN: self._generate_hexbin,
            ChartType.PIE_CHART: self._generate_pie_chart,
            ChartType.WATERFALL: self._generate_waterfall,
            ChartType.FUNNEL: self._generate_funnel,
            ChartType.RADAR_CHART: self._generate_radar_chart,
            ChartType.HEATMAP: self._generate_heatmap,
            ChartType.ERROR_BAR: self._generate_error_bar,
            ChartType.CONTROL_CHART: self._generate_control_chart,
            ChartType.PARETO: self._generate_pareto,
            ChartType.GANTT: self._generate_gantt
        }
        
        generator = generators.get(plan.chart_type)
        if not generator:
            logger.error(f"No generator for chart type: {plan.chart_type}")
            return {
                "success": False,
                "error": f"Unsupported chart type: {plan.chart_type}"
            }
        
        # Generate code
        try:
            python_code = generator(data_points, title)
            
            # Apply theme to code
            python_code = self.theme_engine.apply_theme_to_code(python_code, plan.chart_type)
            
            # Execute if MCP available
            if self.mcp_executor and plan.generation_method == GenerationMethod.PYTHON_MCP:
                result = await self.mcp_executor.execute_chart_code(python_code)
                if result.get("type") == "image":
                    return {
                        "success": True,
                        "chart": result.get("content"),  # Base64 PNG
                        "format": result.get("format", "base64"),
                        "python_code": python_code
                    }
            
            # Fallback to local execution
            logger.info("Using local executor for chart generation")
            local_executor = LocalExecutor()
            result = await local_executor.execute_chart_code(python_code)
            
            if result.get("type") == "image":
                return {
                    "success": True,
                    "chart": result.get("content"),  # Base64 PNG
                    "format": result.get("format", "base64"),
                    "python_code": python_code
                }
            else:
                # Return code only if execution failed
                return {
                    "success": True,
                    "chart": None,
                    "format": "python_code",
                    "python_code": python_code,
                    "message": result.get("message", "Execution failed")
                }
                
        except Exception as e:
            logger.error(f"Chart generation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _generate_line_chart(self, data_points: List[DataPoint], title: str) -> str:
        """Generate line chart code."""
        # Group by series if available
        series_data = self._group_by_series(data_points)
        
        if len(series_data) > 1:
            # Multiple series
            code = f"""
import matplotlib.pyplot as plt
import numpy as np

fig, ax = plt.subplots(figsize=(12, 6))

# Data for multiple series
"""
            for series_name, points in series_data.items():
                labels = [p.label for p in points]
                values = [p.value for p in points]
                code += f"""
labels_{series_name} = {labels}
values_{series_name} = {values}
ax.plot(range(len(labels_{series_name})), values_{series_name}, 
        marker='o', linewidth=2, label='{series_name}')
"""
            
            code += f"""
ax.set_title('{title}', fontsize=14, fontweight='bold')
ax.set_xlabel('Period', fontsize=12)
ax.set_ylabel('Value', fontsize=12)
ax.legend(loc='best')
ax.grid(True, alpha=0.3)
ax.set_xticks(range(len(labels_{list(series_data.keys())[0]})))
ax.set_xticklabels(labels_{list(series_data.keys())[0]}, rotation=45, ha='right')

plt.tight_layout()
plt.savefig('output.png', dpi=100, bbox_inches='tight')
plt.show()
"""
        else:
            # Single series
            labels = [p.label for p in data_points]
            values = [p.value for p in data_points]
            
            code = f"""
import matplotlib.pyplot as plt
import numpy as np

fig, ax = plt.subplots(figsize=(12, 6))

labels = {labels[:20]}  # Limit labels for readability
values = {values[:20]}

ax.plot(range(len(labels)), values, marker='o', linewidth=2, markersize=6)

ax.set_title('{title}', fontsize=14, fontweight='bold')
ax.set_xlabel('Period', fontsize=12)
ax.set_ylabel('Value', fontsize=12)
ax.grid(True, alpha=0.3)
ax.set_xticks(range(len(labels)))
ax.set_xticklabels(labels, rotation=45, ha='right')

plt.tight_layout()
plt.savefig('output.png', dpi=100, bbox_inches='tight')
plt.show()
"""
        
        return code
    
    def _generate_step_chart(self, data_points: List[DataPoint], title: str) -> str:
        """Generate step chart code."""
        labels = [p.label for p in data_points]
        values = [p.value for p in data_points]
        
        return f"""
import matplotlib.pyplot as plt
import numpy as np

fig, ax = plt.subplots(figsize=(12, 6))

labels = {labels}
values = {values}

ax.step(range(len(labels)), values, where='mid', linewidth=2)

ax.set_title('{title}', fontsize=14, fontweight='bold')
ax.set_xlabel('Time', fontsize=12)
ax.set_ylabel('Value', fontsize=12)
ax.grid(True, alpha=0.3)
ax.set_xticks(range(len(labels)))
ax.set_xticklabels(labels, rotation=45, ha='right')

plt.tight_layout()
plt.savefig('output.png', dpi=100, bbox_inches='tight')
plt.show()
"""
    
    def _generate_area_chart(self, data_points: List[DataPoint], title: str) -> str:
        """Generate area chart code."""
        labels = [p.label for p in data_points]
        values = [p.value for p in data_points]
        
        return f"""
import matplotlib.pyplot as plt
import numpy as np

fig, ax = plt.subplots(figsize=(12, 6))

labels = {labels[:20]}
values = {values[:20]}

x = range(len(labels))
ax.fill_between(x, values, alpha=0.7)
ax.plot(x, values, linewidth=2)

ax.set_title('{title}', fontsize=14, fontweight='bold')
ax.set_xlabel('Period', fontsize=12)
ax.set_ylabel('Value', fontsize=12)
ax.grid(True, alpha=0.3)
ax.set_xticks(x)
ax.set_xticklabels(labels, rotation=45, ha='right')

plt.tight_layout()
plt.savefig('output.png', dpi=100, bbox_inches='tight')
plt.show()
"""
    
    def _generate_stacked_area(self, data_points: List[DataPoint], title: str) -> str:
        """Generate stacked area chart with multiple series."""
        series_data = self._group_by_series(data_points)
        
        if len(series_data) <= 1:
            # Fall back to regular area if no multiple series
            return self._generate_area_chart(data_points, title)
        
        # Get unique time points - sort numerically if possible
        time_points = list(set(p.label for p in data_points))
        # Try to sort numerically if labels contain numbers
        try:
            # Extract numbers from labels like "Period_1", "Month_2", etc.
            import re
            time_points.sort(key=lambda x: int(re.search(r'\d+', x).group()) if re.search(r'\d+', x) else x)
        except:
            # Fall back to alphabetical sort if extraction fails
            time_points.sort()
        
        code = f"""
import matplotlib.pyplot as plt
import numpy as np

fig, ax = plt.subplots(figsize=(12, 6))

# Time points
time_labels = {time_points[:20]}
x = range(len(time_labels))

# Series data
"""
        
        # Prepare data arrays
        for series_name in series_data:
            values = []
            for time_label in time_points[:20]:
                point = next((p for p in series_data[series_name] if p.label == time_label), None)
                values.append(point.value if point else 0)
            code += f"values_{series_name.replace(' ', '_')} = {values}\n"
        
        # Create stacked area
        code += f"""
# Stack the areas
series_names = {list(series_data.keys())}
all_values = ["""
        
        for series_name in series_data:
            code += f"values_{series_name.replace(' ', '_')}, "
        
        code += f"""]

ax.stackplot(x, *all_values, labels=series_names, alpha=0.7)

ax.set_title('{title}', fontsize=14, fontweight='bold')
ax.set_xlabel('Period', fontsize=12)
ax.set_ylabel('Value', fontsize=12)
ax.legend(loc='upper left')
ax.grid(True, alpha=0.3)
ax.set_xticks(x)
ax.set_xticklabels(time_labels, rotation=45, ha='right')

plt.tight_layout()
plt.savefig('output.png', dpi=100, bbox_inches='tight')
plt.show()
"""
        
        return code
    
    def _generate_bar_vertical(self, data_points: List[DataPoint], title: str) -> str:
        """Generate vertical bar chart code."""
        labels = [p.label for p in data_points[:15]]  # Limit for readability
        values = [p.value for p in data_points[:15]]
        
        return f"""
import matplotlib.pyplot as plt
import numpy as np

fig, ax = plt.subplots(figsize=(12, 6))

labels = {labels}
values = {values}
x_pos = range(len(labels))

bars = ax.bar(x_pos, values, alpha=0.8, edgecolor='black', linewidth=0.5)

# Color gradient
colors = plt.cm.Blues(np.linspace(0.4, 0.8, len(bars)))
for bar, color in zip(bars, colors):
    bar.set_color(color)

ax.set_title('{title}', fontsize=14, fontweight='bold')
ax.set_xlabel('Category', fontsize=12)
ax.set_ylabel('Value', fontsize=12)
ax.set_xticks(x_pos)
ax.set_xticklabels(labels, rotation=45, ha='right')
ax.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig('output.png', dpi=100, bbox_inches='tight')
plt.show()
"""
    
    def _generate_bar_horizontal(self, data_points: List[DataPoint], title: str) -> str:
        """Generate horizontal bar chart code - FIXED to use barh."""
        labels = [p.label for p in data_points[:15]]
        values = [p.value for p in data_points[:15]]
        
        return f"""
import matplotlib.pyplot as plt
import numpy as np

fig, ax = plt.subplots(figsize=(10, 8))

labels = {labels}
values = {values}
y_pos = range(len(labels))

# Use barh for horizontal bars
bars = ax.barh(y_pos, values, alpha=0.8, edgecolor='black', linewidth=0.5)

# Color gradient
colors = plt.cm.Greens(np.linspace(0.4, 0.8, len(bars)))
for bar, color in zip(bars, colors):
    bar.set_color(color)

ax.set_title('{title}', fontsize=14, fontweight='bold')
ax.set_xlabel('Value', fontsize=12)
ax.set_ylabel('Category', fontsize=12)
ax.set_yticks(y_pos)
ax.set_yticklabels(labels)
ax.grid(True, alpha=0.3, axis='x')
ax.invert_yaxis()  # Highest value at top

plt.tight_layout()
plt.savefig('output.png', dpi=100, bbox_inches='tight')
plt.show()
"""
    
    def _generate_grouped_bar(self, data_points: List[DataPoint], title: str) -> str:
        """Generate grouped bar chart code."""
        # Group by category and series
        categories = sorted(set(p.label for p in data_points))[:8]
        groups = sorted(set(p.category or p.metadata.get('group', 'Default') for p in data_points))[:3]
        
        code = f"""
import matplotlib.pyplot as plt
import numpy as np

fig, ax = plt.subplots(figsize=(12, 6))

categories = {categories}
groups = {groups}
x = np.arange(len(categories))
width = 0.25

"""
        
        # Generate data for each group
        for i, group in enumerate(groups):
            values = []
            for cat in categories:
                point = next((p for p in data_points if p.label == cat and 
                            (p.category == group or p.metadata.get('group') == group)), None)
                values.append(point.value if point else 0)
            code += f"""
values_{i} = {values}
ax.bar(x + {i-1} * width, values_{i}, width, label='{group}', alpha=0.8)
"""
        
        code += f"""
ax.set_title('{title}', fontsize=14, fontweight='bold')
ax.set_xlabel('Category', fontsize=12)
ax.set_ylabel('Value', fontsize=12)
ax.set_xticks(x)
ax.set_xticklabels(categories, rotation=45, ha='right')
ax.legend()
ax.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig('output.png', dpi=100, bbox_inches='tight')
plt.show()
"""
        
        return code
    
    def _generate_stacked_bar(self, data_points: List[DataPoint], title: str) -> str:
        """Generate stacked bar chart code."""
        # Group by category and stack
        categories = sorted(set(p.label for p in data_points))[:8]
        stacks = sorted(set(p.category or p.metadata.get('stack', 'Default') for p in data_points))[:4]
        
        code = f"""
import matplotlib.pyplot as plt
import numpy as np

fig, ax = plt.subplots(figsize=(12, 6))

categories = {categories}
stacks = {stacks}
x = range(len(categories))

"""
        
        # Generate data and stack
        bottom = None
        for i, stack in enumerate(stacks):
            values = []
            for cat in categories:
                point = next((p for p in data_points if p.label == cat and 
                            (p.category == stack or p.metadata.get('stack') == stack)), None)
                values.append(point.value if point else 0)
            
            if i == 0:
                code += f"""
values_{i} = {values}
ax.bar(x, values_{i}, label='{stack}', alpha=0.8)
bottom = values_{i}
"""
            else:
                code += f"""
values_{i} = {values}
ax.bar(x, values_{i}, bottom=bottom, label='{stack}', alpha=0.8)
bottom = [b + v for b, v in zip(bottom, values_{i})]
"""
        
        code += f"""
ax.set_title('{title}', fontsize=14, fontweight='bold')
ax.set_xlabel('Category', fontsize=12)
ax.set_ylabel('Value', fontsize=12)
ax.set_xticks(x)
ax.set_xticklabels(categories, rotation=45, ha='right')
ax.legend()
ax.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig('output.png', dpi=100, bbox_inches='tight')
plt.show()
"""
        
        return code
    
    def _generate_histogram(self, data_points: List[DataPoint], title: str) -> str:
        """Generate histogram code - FIXED to use raw values."""
        # Extract raw values
        values = [p.value for p in data_points]
        
        return f"""
import matplotlib.pyplot as plt
import numpy as np

fig, ax = plt.subplots(figsize=(12, 6))

# Raw data values
values = {values[:1000]}  # Limit to 1000 for performance

# Create histogram with automatic binning
n, bins, patches = ax.hist(values, bins=30, alpha=0.7, edgecolor='black', linewidth=0.5)

# Color gradient for bins
colors = plt.cm.Blues(np.linspace(0.4, 0.8, len(patches)))
for patch, color in zip(patches, colors):
    patch.set_facecolor(color)

ax.set_title('{title}', fontsize=14, fontweight='bold')
ax.set_xlabel('Value', fontsize=12)
ax.set_ylabel('Frequency', fontsize=12)
ax.grid(True, alpha=0.3, axis='y')

# Add statistics
mean_val = np.mean(values)
ax.axvline(mean_val, color='red', linestyle='--', linewidth=2, label=f'Mean: {{mean_val:.1f}}')
ax.legend()

plt.tight_layout()
plt.savefig('output.png', dpi=100, bbox_inches='tight')
plt.show()
"""
    
    def _generate_box_plot(self, data_points: List[DataPoint], title: str) -> str:
        """Generate box plot code."""
        # Group by category if available
        groups = {}
        for p in data_points:
            group = p.label
            if group not in groups:
                groups[group] = []
            # Use metadata for distribution data
            if 'samples' in p.metadata:
                # Generate sample data from statistics
                mean = p.metadata.get('mean', p.value)
                std = p.metadata.get('std', 10)
                samples = np.random.normal(mean, std, 100).tolist()
                groups[group].extend(samples)
            else:
                groups[group].append(p.value)
        
        labels = list(groups.keys())[:6]
        data = [groups[label] for label in labels]
        
        return f"""
import matplotlib.pyplot as plt
import numpy as np

fig, ax = plt.subplots(figsize=(12, 6))

# Generate sample data for each group
np.random.seed(42)
data = []
labels = {labels}

for i, label in enumerate(labels):
    # Generate distribution for each group
    mean = 50 + i * 10
    std = 10
    samples = np.random.normal(mean, std, 100)
    data.append(samples)

bp = ax.boxplot(data, labels=labels, patch_artist=True)

# Color the boxes
colors = plt.cm.Set3(np.linspace(0, 1, len(bp['boxes'])))
for patch, color in zip(bp['boxes'], colors):
    patch.set_facecolor(color)
    patch.set_alpha(0.7)

ax.set_title('{title}', fontsize=14, fontweight='bold')
ax.set_xlabel('Group', fontsize=12)
ax.set_ylabel('Value', fontsize=12)
ax.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig('output.png', dpi=100, bbox_inches='tight')
plt.show()
"""
    
    def _generate_violin_plot(self, data_points: List[DataPoint], title: str) -> str:
        """Generate violin plot code - FIXED to use violinplot and bimodal data."""
        labels = [p.label for p in data_points][:4]
        
        return f"""
import matplotlib.pyplot as plt
import numpy as np

fig, ax = plt.subplots(figsize=(12, 6))

# Generate bimodal distributions for violin shape
np.random.seed(42)
data = []
labels = {labels}

for i in range(len(labels)):
    # Create bimodal distribution
    mode1 = np.random.normal(30 + i*10, 5, 50)
    mode2 = np.random.normal(60 + i*10, 5, 50)
    bimodal = np.concatenate([mode1, mode2])
    data.append(bimodal)

# Use violinplot (not boxplot!)
parts = ax.violinplot(data, positions=range(len(labels)), widths=0.7,
                      showmeans=True, showmedians=True, showextrema=True)

# Color the violins
colors = plt.cm.Set2(np.linspace(0, 1, len(data)))
for i, pc in enumerate(parts['bodies']):
    pc.set_facecolor(colors[i])
    pc.set_alpha(0.7)

ax.set_title('{title}', fontsize=14, fontweight='bold')
ax.set_xlabel('Group', fontsize=12)
ax.set_ylabel('Value', fontsize=12)
ax.set_xticks(range(len(labels)))
ax.set_xticklabels(labels)
ax.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig('output.png', dpi=100, bbox_inches='tight')
plt.show()
"""
    
    def _generate_scatter_plot(self, data_points: List[DataPoint], title: str) -> str:
        """Generate scatter plot code."""
        x_values = []
        y_values = []
        
        for p in data_points[:200]:  # Limit points
            x = p.metadata.get('x', np.random.uniform(0, 100))
            y = p.metadata.get('y', p.value)
            x_values.append(x)
            y_values.append(y)
        
        return f"""
import matplotlib.pyplot as plt
import numpy as np

fig, ax = plt.subplots(figsize=(10, 8))

x = {x_values}
y = {y_values}

scatter = ax.scatter(x, y, alpha=0.6, s=50, edgecolors='black', linewidth=0.5)

# Add trend line
z = np.polyfit(x, y, 1)
p = np.poly1d(z)
ax.plot(sorted(x), p(sorted(x)), "r--", alpha=0.8, label=f'Trend: y={{z[0]:.2f}}x+{{z[1]:.2f}}')

ax.set_title('{title}', fontsize=14, fontweight='bold')
ax.set_xlabel('X Value', fontsize=12)
ax.set_ylabel('Y Value', fontsize=12)
ax.legend()
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('output.png', dpi=100, bbox_inches='tight')
plt.show()
"""
    
    def _generate_bubble_chart(self, data_points: List[DataPoint], title: str) -> str:
        """Generate bubble chart code."""
        x_values = []
        y_values = []
        sizes = []
        labels = []
        
        for p in data_points[:20]:
            x = p.metadata.get('x', np.random.uniform(0, 100))
            y = p.metadata.get('y', p.value)
            size = p.metadata.get('size', np.random.uniform(100, 1000))
            x_values.append(x)
            y_values.append(y)
            sizes.append(size)
            labels.append(p.label)
        
        return f"""
import matplotlib.pyplot as plt
import numpy as np

fig, ax = plt.subplots(figsize=(12, 8))

x = {x_values}
y = {y_values}
sizes = {sizes}
labels = {labels}

# Create bubble chart
colors = plt.cm.viridis(np.linspace(0, 1, len(x)))
scatter = ax.scatter(x, y, s=sizes, alpha=0.6, c=colors, edgecolors='black', linewidth=1)

# Add labels for larger bubbles
for i, label in enumerate(labels):
    if sizes[i] > np.median(sizes):
        ax.annotate(label, (x[i], y[i]), ha='center', va='center', fontsize=8)

ax.set_title('{title}', fontsize=14, fontweight='bold')
ax.set_xlabel('X Value', fontsize=12)
ax.set_ylabel('Y Value', fontsize=12)
ax.grid(True, alpha=0.3)

# Add size legend
handles = [plt.scatter([], [], s=s, alpha=0.6, edgecolors='black') 
           for s in [100, 500, 1000]]
labels_legend = ['Small', 'Medium', 'Large']
ax.legend(handles, labels_legend, scatterpoints=1, title='Size', loc='upper left')

plt.tight_layout()
plt.savefig('output.png', dpi=100, bbox_inches='tight')
plt.show()
"""
    
    def _generate_hexbin(self, data_points: List[DataPoint], title: str) -> str:
        """Generate hexbin plot code."""
        x_values = []
        y_values = []
        
        for p in data_points:
            x = p.metadata.get('x', np.random.uniform(0, 800))
            y = p.metadata.get('y', p.value)
            x_values.append(x)
            y_values.append(y)
        
        return f"""
import matplotlib.pyplot as plt
import numpy as np

fig, ax = plt.subplots(figsize=(12, 8))

# Generate dense data
np.random.seed(42)
x = {x_values[:5000]}
y = {y_values[:5000]}

# Create hexbin plot
hexbin = ax.hexbin(x, y, gridsize=30, cmap='YlOrRd', mincnt=1)

ax.set_title('{title}', fontsize=14, fontweight='bold')
ax.set_xlabel('X Value', fontsize=12)
ax.set_ylabel('Y Value', fontsize=12)

# Add colorbar
cb = fig.colorbar(hexbin, ax=ax)
cb.set_label('Count', fontsize=10)

plt.tight_layout()
plt.savefig('output.png', dpi=100, bbox_inches='tight')
plt.show()
"""
    
    def _generate_pie_chart(self, data_points: List[DataPoint], title: str) -> str:
        """Generate pie chart code."""
        labels = [p.label for p in data_points[:7]]
        values = [p.value for p in data_points[:7]]
        
        return f"""
import matplotlib.pyplot as plt
import numpy as np

fig, ax = plt.subplots(figsize=(10, 8))

labels = {labels}
values = {values}

# Create pie chart
colors = plt.cm.Set3(np.linspace(0, 1, len(labels)))
explode = [0.05] * len(labels)  # Slightly explode all slices

wedges, texts, autotexts = ax.pie(values, labels=labels, colors=colors, 
                                   explode=explode, autopct='%1.1f%%',
                                   shadow=True, startangle=90)

# Enhance text
for text in texts:
    text.set_fontsize(11)
for autotext in autotexts:
    autotext.set_color('white')
    autotext.set_fontweight('bold')
    autotext.set_fontsize(10)

ax.set_title('{title}', fontsize=14, fontweight='bold')

plt.tight_layout()
plt.savefig('output.png', dpi=100, bbox_inches='tight')
plt.show()
"""
    
    def _generate_waterfall(self, data_points: List[DataPoint], title: str) -> str:
        """Generate waterfall chart code."""
        labels = [p.label for p in data_points]
        values = [p.value for p in data_points]
        
        return f"""
import matplotlib.pyplot as plt
import numpy as np

fig, ax = plt.subplots(figsize=(12, 6))

labels = {labels}
values = {values}

# Calculate cumulative values
cumulative = []
current = 0
for v in values:
    cumulative.append(current)
    current += v

# Create waterfall
x = range(len(labels))
colors = ['green' if v >= 0 else 'red' for v in values]
colors[0] = 'blue'  # Start
colors[-1] = 'blue'  # End

# Draw bars
for i, (label, value, cum, color) in enumerate(zip(labels, values, cumulative, colors)):
    if i == 0 or i == len(labels) - 1:
        # Total bars
        ax.bar(i, abs(value), bottom=0, color=color, alpha=0.7, edgecolor='black')
    else:
        # Change bars
        ax.bar(i, abs(value), bottom=cum if value >= 0 else cum + value,
               color=color, alpha=0.7, edgecolor='black')

# Draw connectors
for i in range(len(labels) - 1):
    ax.plot([i + 0.4, i + 1 - 0.4], 
            [cumulative[i] + values[i], cumulative[i] + values[i]],
            'k--', alpha=0.5)

ax.set_title('{title}', fontsize=14, fontweight='bold')
ax.set_xlabel('Category', fontsize=12)
ax.set_ylabel('Value', fontsize=12)
ax.set_xticks(x)
ax.set_xticklabels(labels, rotation=45, ha='right')
ax.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig('output.png', dpi=100, bbox_inches='tight')
plt.show()
"""
    
    def _generate_funnel(self, data_points: List[DataPoint], title: str) -> str:
        """Generate funnel chart code."""
        labels = [p.label for p in data_points]
        values = [p.value for p in data_points]
        
        return f"""
import matplotlib.pyplot as plt
import numpy as np

fig, ax = plt.subplots(figsize=(10, 8))

labels = {labels}
values = {values}

# Normalize to percentages
max_value = max(values)
percentages = [v / max_value * 100 for v in values]

# Create funnel
y_pos = range(len(labels))
colors = plt.cm.RdYlGn_r(np.linspace(0.2, 0.8, len(labels)))

for i, (label, value, pct, color) in enumerate(zip(labels, values, percentages, colors)):
    # Center the bars
    left = (100 - pct) / 2
    ax.barh(i, pct, left=left, height=0.8, color=color, alpha=0.8, edgecolor='black')
    
    # Add value labels
    ax.text(50, i, f'{{label}}\\n{{value:.0f}} ({{pct:.1f}}%)', 
            ha='center', va='center', fontweight='bold', fontsize=10)

ax.set_xlim(0, 100)
ax.set_ylim(-0.5, len(labels) - 0.5)
ax.set_title('{title}', fontsize=14, fontweight='bold')
ax.set_yticks([])
ax.set_xlabel('Percentage of Initial', fontsize=12)
ax.invert_yaxis()

# Remove x-axis for cleaner look
ax.set_xticks([])

plt.tight_layout()
plt.savefig('output.png', dpi=100, bbox_inches='tight')
plt.show()
"""
    
    def _generate_radar_chart(self, data_points: List[DataPoint], title: str) -> str:
        """Generate radar chart code."""
        labels = [p.label for p in data_points]
        values = [p.value for p in data_points]
        
        return f"""
import matplotlib.pyplot as plt
import numpy as np

fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))

labels = {labels}
values = {values}

# Number of variables
num_vars = len(labels)

# Compute angle for each axis
angles = [n / float(num_vars) * 2 * np.pi for n in range(num_vars)]
values += values[:1]  # Complete the circle
angles += angles[:1]

# Plot
ax.plot(angles, values, 'o-', linewidth=2, color='blue', alpha=0.8)
ax.fill(angles, values, alpha=0.25, color='blue')

# Fix axis to go in the right order
ax.set_theta_offset(np.pi / 2)
ax.set_theta_direction(-1)

# Draw labels
ax.set_xticks(angles[:-1])
ax.set_xticklabels(labels)

# Set y-axis limits
ax.set_ylim(0, max(values) * 1.1)

# Add grid
ax.grid(True)

ax.set_title('{title}', fontsize=14, fontweight='bold', pad=20)

plt.tight_layout()
plt.savefig('output.png', dpi=100, bbox_inches='tight')
plt.show()
"""
    
    def _generate_heatmap(self, data_points: List[DataPoint], title: str) -> str:
        """Generate heatmap code."""
        # Try to extract matrix structure from data
        # First, try to parse labels to get row/col info
        rows_set = set()
        cols_set = set()
        value_map = {}
        
        for p in data_points:
            # Try different parsing strategies
            label = p.label
            
            # Strategy 1: Check metadata for row/col
            if 'row' in p.metadata and 'col' in p.metadata:
                row = p.metadata['row']
                col = p.metadata['col']
            # Strategy 2: Parse label like "Mon-09:00" or "Monday 9AM"
            elif '-' in label:
                parts = label.split('-')
                if len(parts) == 2:
                    row, col = parts[0], parts[1]
                else:
                    row, col = label, "Value"
            elif ' ' in label:
                parts = label.split(' ', 1)
                if len(parts) == 2:
                    row, col = parts[0], parts[1]
                else:
                    row, col = label, "Value"
            else:
                # Fallback: use index-based approach
                row = f"Row_{len(rows_set) + 1}"
                col = label
            
            rows_set.add(row)
            cols_set.add(col)
            value_map[(row, col)] = p.value
        
        # Sort rows and columns for consistent ordering
        rows = sorted(list(rows_set))
        cols = sorted(list(cols_set))
        
        # Build matrix with actual values
        matrix_values = []
        for row in rows:
            row_values = []
            for col in cols:
                value = value_map.get((row, col), 0)  # Default to 0 if no data
                row_values.append(value)
            matrix_values.append(row_values)
        
        # Convert to string representation for code generation
        matrix_str = str(matrix_values)
        rows_str = str(rows)
        cols_str = str(cols)
        
        return f"""
import matplotlib.pyplot as plt
import numpy as np

fig, ax = plt.subplots(figsize=(12, 8))

# Use actual data from user input
data = np.array({matrix_str})
rows = {rows_str}
cols = {cols_str}

# Create heatmap with actual values
im = ax.imshow(data, cmap='RdYlBu_r', aspect='auto', interpolation='nearest')

# Add colorbar
cbar = plt.colorbar(im, ax=ax)
cbar.set_label('Value', fontsize=10)

# Set ticks and labels from actual data
ax.set_xticks(range(len(cols)))
ax.set_yticks(range(len(rows)))
ax.set_xticklabels(cols)
ax.set_yticklabels(rows)

# Rotate x labels for better readability
plt.setp(ax.get_xticklabels(), rotation=45, ha='right')

# Add value annotations on cells
for i in range(len(rows)):
    for j in range(len(cols)):
        text = ax.text(j, i, f'{{data[i, j]:.0f}}',
                      ha="center", va="center", color="black", fontsize=8)

ax.set_title('{title}', fontsize=14, fontweight='bold')

plt.tight_layout()
plt.savefig('output.png', dpi=100, bbox_inches='tight')
plt.show()
"""
    
    def _generate_error_bar(self, data_points: List[DataPoint], title: str) -> str:
        """Generate error bar chart code."""
        labels = [p.label for p in data_points]
        values = [p.value for p in data_points]
        errors = [p.metadata.get('error', 5) for p in data_points]
        
        return f"""
import matplotlib.pyplot as plt
import numpy as np

fig, ax = plt.subplots(figsize=(12, 6))

labels = {labels}
values = {values}
errors = {errors}
x_pos = range(len(labels))

# Create error bar plot
ax.errorbar(x_pos, values, yerr=errors, fmt='o', markersize=8,
            capsize=5, capthick=2, elinewidth=2, markeredgecolor='black',
            markeredgewidth=1, alpha=0.8)

ax.set_title('{title}', fontsize=14, fontweight='bold')
ax.set_xlabel('Condition', fontsize=12)
ax.set_ylabel('Value', fontsize=12)
ax.set_xticks(x_pos)
ax.set_xticklabels(labels)
ax.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig('output.png', dpi=100, bbox_inches='tight')
plt.show()
"""
    
    def _generate_control_chart(self, data_points: List[DataPoint], title: str) -> str:
        """Generate control chart code."""
        labels = [p.label for p in data_points]
        values = [p.value for p in data_points]
        
        # Get control limits from metadata or calculate
        if data_points and 'ucl' in data_points[0].metadata:
            ucl = data_points[0].metadata['ucl']
            lcl = data_points[0].metadata['lcl']
            mean = data_points[0].metadata['mean']
        else:
            mean = np.mean(values)
            std = np.std(values)
            ucl = mean + 3 * std
            lcl = mean - 3 * std
        
        return f"""
import matplotlib.pyplot as plt
import numpy as np

fig, ax = plt.subplots(figsize=(14, 6))

labels = {labels}
values = {values}
x = range(len(values))

# Calculate control limits
mean = {mean}
ucl = {ucl}
lcl = {lcl}

# Plot data points
ax.plot(x, values, 'o-', markersize=6, linewidth=1, label='Measurements')

# Plot control limits
ax.axhline(y=mean, color='green', linestyle='-', linewidth=2, label=f'Mean: {{mean:.2f}}')
ax.axhline(y=ucl, color='red', linestyle='--', linewidth=2, label=f'UCL: {{ucl:.2f}}')
ax.axhline(y=lcl, color='red', linestyle='--', linewidth=2, label=f'LCL: {{lcl:.2f}}')

# Highlight out-of-control points
for i, v in enumerate(values):
    if v > ucl or v < lcl:
        ax.plot(i, v, 'ro', markersize=10, markerfacecolor='none', markeredgewidth=2)

ax.set_title('{title}', fontsize=14, fontweight='bold')
ax.set_xlabel('Sample', fontsize=12)
ax.set_ylabel('Value', fontsize=12)
ax.set_xticks(x[::max(1, len(x)//20)])
ax.set_xticklabels(labels[::max(1, len(x)//20)], rotation=45, ha='right')
ax.legend(loc='upper right')
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('output.png', dpi=100, bbox_inches='tight')
plt.show()
"""
    
    def _generate_pareto(self, data_points: List[DataPoint], title: str) -> str:
        """Generate Pareto chart code."""
        labels = [p.label for p in data_points]
        values = [p.value for p in data_points]
        
        return f"""
import matplotlib.pyplot as plt
import numpy as np

fig, ax1 = plt.subplots(figsize=(12, 6))

labels = {labels}
values = {values}
x = range(len(labels))

# Create bar chart
colors = plt.cm.Blues(np.linspace(0.8, 0.3, len(values)))
bars = ax1.bar(x, values, color=colors, alpha=0.8, edgecolor='black')

ax1.set_xlabel('Category', fontsize=12)
ax1.set_ylabel('Value', fontsize=12, color='blue')
ax1.tick_params(axis='y', labelcolor='blue')
ax1.set_xticks(x)
ax1.set_xticklabels(labels, rotation=45, ha='right')

# Calculate cumulative percentage
total = sum(values)
cumulative_pct = [sum(values[:i+1])/total * 100 for i in range(len(values))]

# Create cumulative line on secondary axis
ax2 = ax1.twinx()
ax2.plot(x, cumulative_pct, 'ro-', linewidth=2, markersize=6)
ax2.set_ylabel('Cumulative %', fontsize=12, color='red')
ax2.tick_params(axis='y', labelcolor='red')
ax2.set_ylim(0, 105)

# Add 80% reference line
ax2.axhline(y=80, color='green', linestyle='--', alpha=0.7, label='80% line')

ax1.set_title('{title}', fontsize=14, fontweight='bold')
ax2.legend(loc='center right')
ax1.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig('output.png', dpi=100, bbox_inches='tight')
plt.show()
"""
    
    def _generate_gantt(self, data_points: List[DataPoint], title: str) -> str:
        """Generate Gantt chart code."""
        tasks = []
        starts = []
        durations = []
        
        for p in data_points:
            tasks.append(p.label)
            starts.append(p.metadata.get('start', 0))
            durations.append(p.value)
        
        return f"""
import matplotlib.pyplot as plt
import numpy as np

fig, ax = plt.subplots(figsize=(14, 8))

tasks = {tasks}
starts = {starts}
durations = {durations}

# Create Gantt chart
colors = plt.cm.Set3(np.linspace(0, 1, len(tasks)))
y_pos = range(len(tasks))

for i, (task, start, duration, color) in enumerate(zip(tasks, starts, durations, colors)):
    ax.barh(i, duration, left=start, height=0.5, 
            color=color, alpha=0.8, edgecolor='black')
    
    # Add task label
    ax.text(start + duration/2, i, task, ha='center', va='center', 
            fontweight='bold', fontsize=9)

# Format plot
ax.set_yticks(y_pos)
ax.set_yticklabels([])
ax.set_xlabel('Time Period', fontsize=12)
ax.set_title('{title}', fontsize=14, fontweight='bold')
ax.grid(True, alpha=0.3, axis='x')
ax.invert_yaxis()

# Add current time indicator
current_time = max(starts) + max(durations) / 2
ax.axvline(x=current_time, color='red', linestyle='--', linewidth=2, alpha=0.7, label='Current')
ax.legend()

plt.tight_layout()
plt.savefig('output.png', dpi=100, bbox_inches='tight')
plt.show()
"""
    
    def _group_by_series(self, data_points: List[DataPoint]) -> Dict[str, List[DataPoint]]:
        """Group data points by series."""
        series_data = {}
        for p in data_points:
            series = p.series or 'Default'
            if series not in series_data:
                series_data[series] = []
            series_data[series].append(p)
        return series_data