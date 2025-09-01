"""
Theme Engine V2
===============

Advanced theme management with color mixing, gradients, and chart-specific styling.
Supports primary/secondary/tertiary colors with automatic palette generation.

Author: Analytics Agent System V2
Date: 2024
Version: 2.0
"""

import colorsys
from typing import List, Dict, Any, Tuple, Optional
import logging
from .models import ThemeConfig, ChartType

logger = logging.getLogger(__name__)


class ThemeEngine:
    """Advanced theme engine for chart styling."""
    
    def __init__(self, theme_config: Optional[ThemeConfig] = None):
        """Initialize theme engine with configuration."""
        self.config = theme_config or ThemeConfig()
        self.palette = self._generate_palette()
        self.styles = self._load_styles()
    
    def _hex_to_rgb(self, hex_color: str) -> Tuple[int, int, int]:
        """Convert hex color to RGB tuple."""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def _rgb_to_hex(self, rgb: Tuple[int, int, int]) -> str:
        """Convert RGB tuple to hex color."""
        return '#{:02x}{:02x}{:02x}'.format(*rgb)
    
    def _lighten(self, hex_color: str, amount: float = 0.2) -> str:
        """Lighten a color by specified amount (0-1)."""
        rgb = self._hex_to_rgb(hex_color)
        h, l, s = colorsys.rgb_to_hls(*[x/255.0 for x in rgb])
        l = min(1.0, l + amount)
        rgb = colorsys.hls_to_rgb(h, l, s)
        return self._rgb_to_hex(tuple(int(x * 255) for x in rgb))
    
    def _darken(self, hex_color: str, amount: float = 0.2) -> str:
        """Darken a color by specified amount (0-1)."""
        rgb = self._hex_to_rgb(hex_color)
        h, l, s = colorsys.rgb_to_hls(*[x/255.0 for x in rgb])
        l = max(0.0, l - amount)
        rgb = colorsys.hls_to_rgb(h, l, s)
        return self._rgb_to_hex(tuple(int(x * 255) for x in rgb))
    
    def _mix_colors(self, color1: str, color2: str, ratio: float = 0.5) -> str:
        """Mix two colors with given ratio (0=color1, 1=color2)."""
        rgb1 = self._hex_to_rgb(color1)
        rgb2 = self._hex_to_rgb(color2)
        mixed = tuple(int(c1 * (1 - ratio) + c2 * ratio) for c1, c2 in zip(rgb1, rgb2))
        return self._rgb_to_hex(mixed)
    
    def _generate_shades(self, base_color: str, count: int = 3) -> List[str]:
        """Generate shades of a color."""
        shades = []
        for i in range(1, count + 1):
            amount = i * 0.15  # 15%, 30%, 45%
            shades.append(self._lighten(base_color, amount))
            shades.append(self._darken(base_color, amount))
        return shades
    
    def _generate_complementary(self, hex_color: str) -> List[str]:
        """Generate complementary colors."""
        rgb = self._hex_to_rgb(hex_color)
        h, l, s = colorsys.rgb_to_hls(*[x/255.0 for x in rgb])
        
        # Complementary (opposite on color wheel)
        comp_h = (h + 0.5) % 1.0
        comp_rgb = colorsys.hls_to_rgb(comp_h, l, s)
        complementary = self._rgb_to_hex(tuple(int(x * 255) for x in comp_rgb))
        
        # Analogous (adjacent on color wheel)
        analog1_h = (h + 0.083) % 1.0  # +30 degrees
        analog2_h = (h - 0.083) % 1.0  # -30 degrees
        analog1_rgb = colorsys.hls_to_rgb(analog1_h, l, s)
        analog2_rgb = colorsys.hls_to_rgb(analog2_h, l, s)
        
        return [
            complementary,
            self._rgb_to_hex(tuple(int(x * 255) for x in analog1_rgb)),
            self._rgb_to_hex(tuple(int(x * 255) for x in analog2_rgb))
        ]
    
    def _generate_palette(self) -> List[str]:
        """Generate extended color palette from base colors."""
        palette = [self.config.primary, self.config.secondary, self.config.tertiary]
        
        # Add mixed colors
        palette.append(self._mix_colors(self.config.primary, self.config.secondary))
        palette.append(self._mix_colors(self.config.secondary, self.config.tertiary))
        palette.append(self._mix_colors(self.config.primary, self.config.tertiary))
        
        # Add shades of primary and secondary
        palette.extend(self._generate_shades(self.config.primary, 2))
        palette.extend(self._generate_shades(self.config.secondary, 2))
        
        # Add complementary colors
        palette.extend(self._generate_complementary(self.config.primary))
        
        # Ensure unique colors
        seen = set()
        unique_palette = []
        for color in palette:
            if color not in seen:
                seen.add(color)
                unique_palette.append(color)
        
        return unique_palette
    
    def _create_gradient(self, start_color: str, end_color: str, steps: int = 10) -> List[str]:
        """Create gradient between two colors."""
        gradient = []
        for i in range(steps):
            ratio = i / (steps - 1) if steps > 1 else 0
            gradient.append(self._mix_colors(start_color, end_color, ratio))
        return gradient
    
    def _create_colormap(self, start_color: str, end_color: str, mid_color: Optional[str] = None) -> str:
        """Create matplotlib colormap name or custom colormap."""
        # For simplicity, return a standard colormap that matches the theme
        if mid_color:
            # Three-color diverging colormap
            return 'RdYlBu_r'  # Red-Yellow-Blue reversed
        else:
            # Two-color sequential colormap
            if 'blue' in start_color.lower() or self.config.primary == start_color:
                return 'Blues'
            elif 'green' in start_color.lower() or self.config.secondary == start_color:
                return 'Greens'
            elif 'orange' in start_color.lower() or self.config.tertiary == start_color:
                return 'Oranges'
            else:
                return 'viridis'
    
    def _load_styles(self) -> Dict[str, Dict[str, Any]]:
        """Load matplotlib style configurations."""
        styles = {
            "modern": {
                "figure.facecolor": "white",
                "axes.facecolor": "#FAFAFA",
                "axes.edgecolor": "#CCCCCC",
                "axes.linewidth": 1.0,
                "axes.grid": True,
                "grid.alpha": 0.3,
                "grid.color": "#E0E0E0",
                "font.family": "sans-serif",
                "font.size": self.config.font_size
            },
            "minimal": {
                "figure.facecolor": "white",
                "axes.facecolor": "white",
                "axes.edgecolor": "#333333",
                "axes.linewidth": 0.8,
                "axes.grid": False,
                "font.family": "sans-serif",
                "font.size": self.config.font_size
            },
            "dark": {
                "figure.facecolor": "#1A1A1A",
                "axes.facecolor": "#2A2A2A",
                "axes.edgecolor": "#555555",
                "axes.linewidth": 1.0,
                "axes.grid": True,
                "grid.alpha": 0.2,
                "grid.color": "#444444",
                "font.family": "sans-serif",
                "font.size": self.config.font_size,
                "text.color": "#E0E0E0",
                "axes.labelcolor": "#E0E0E0",
                "xtick.color": "#E0E0E0",
                "ytick.color": "#E0E0E0"
            },
            "corporate": {
                "figure.facecolor": "white",
                "axes.facecolor": "white",
                "axes.edgecolor": "#4A5568",
                "axes.linewidth": 1.5,
                "axes.grid": True,
                "grid.alpha": 0.1,
                "grid.color": "#CBD5E0",
                "font.family": "serif",
                "font.size": self.config.font_size
            },
            "classic": {
                "figure.facecolor": "#F5F5DC",
                "axes.facecolor": "#FFFEF0",
                "axes.edgecolor": "#8B4513",
                "axes.linewidth": 2.0,
                "axes.grid": True,
                "grid.alpha": 0.4,
                "grid.color": "#D2B48C",
                "font.family": "serif",
                "font.size": self.config.font_size
            }
        }
        return styles
    
    def get_style_dict(self) -> Dict[str, Any]:
        """Get matplotlib style dictionary for current theme."""
        return self.styles.get(self.config.style.value, self.styles["modern"])
    
    def apply_to_chart(self, chart_type: ChartType) -> Dict[str, Any]:
        """Get theme configuration for specific chart type."""
        
        # Base configuration
        config = {
            "colors": self.palette,
            "primary": self.config.primary,
            "secondary": self.config.secondary,
            "tertiary": self.config.tertiary,
            "style": self.get_style_dict(),
            "transparency": self.config.transparency
        }
        
        # Chart-specific configurations
        if chart_type in [ChartType.LINE_CHART, ChartType.STEP_CHART]:
            config.update({
                "line_colors": self.palette[:5],
                "line_width": 2.0,
                "marker_size": 6,
                "grid_color": self._lighten(self.config.tertiary, 0.4)
            })
        
        elif chart_type in [ChartType.BAR_VERTICAL, ChartType.BAR_HORIZONTAL]:
            if self.config.gradient:
                config["colors"] = self._create_gradient(
                    self.config.primary, self.config.secondary, 
                    steps=10
                )
            else:
                config["colors"] = [self.config.primary]
            config["edge_color"] = self._darken(self.config.primary, 0.2)
            config["edge_width"] = 1.0
        
        elif chart_type == ChartType.STACKED_AREA_CHART:
            config.update({
                "colors": self.palette[:6],
                "alpha": 0.7,
                "edge_color": None
            })
        
        elif chart_type == ChartType.PIE_CHART:
            config.update({
                "colors": self.palette,
                "explode_color": self.config.tertiary,
                "edge_color": "white",
                "edge_width": 2,
                "start_angle": 90
            })
        
        elif chart_type == ChartType.HEATMAP:
            config.update({
                "colormap": self._create_colormap(
                    self.config.primary, 
                    self.config.tertiary,
                    self.config.secondary
                ),
                "bad_color": "#CCCCCC",
                "under_color": self._lighten(self.config.primary, 0.5),
                "over_color": self._darken(self.config.tertiary, 0.3)
            })
        
        elif chart_type == ChartType.SCATTER_PLOT:
            config.update({
                "colors": self.palette[:10],
                "marker_size": 50,
                "alpha": 0.6,
                "edge_color": self._darken(self.config.primary, 0.3),
                "edge_width": 0.5
            })
        
        elif chart_type == ChartType.VIOLIN_PLOT:
            config.update({
                "body_colors": [self.config.primary, self.config.secondary] * 4,
                "edge_color": self._darken(self.config.primary, 0.2),
                "median_color": self.config.tertiary,
                "alpha": 0.7
            })
        
        elif chart_type == ChartType.RADAR_CHART:
            config.update({
                "line_colors": [self.config.primary, self.config.secondary, self.config.tertiary],
                "fill_alpha": 0.25,
                "line_width": 2,
                "marker_size": 6,
                "grid_color": self._lighten(self.config.tertiary, 0.3)
            })
        
        elif chart_type == ChartType.WATERFALL:
            config.update({
                "positive_color": self.config.secondary,  # Green for positive
                "negative_color": self.config.tertiary,   # Orange/red for negative
                "total_color": self.config.primary,       # Blue for totals
                "connector_color": "#666666",
                "alpha": 0.8
            })
        
        elif chart_type == ChartType.FUNNEL:
            if self.config.gradient:
                config["colors"] = self._create_gradient(
                    self.config.primary, 
                    self.config.tertiary,
                    steps=7
                )
            else:
                config["colors"] = self.palette[:7]
            config["edge_color"] = "white"
            config["edge_width"] = 2
        
        elif chart_type in [ChartType.GROUPED_BAR, ChartType.STACKED_BAR]:
            config.update({
                "group_colors": self.palette[:4],
                "edge_color": self._darken(self.config.primary, 0.1),
                "alpha": 0.9
            })
        
        elif chart_type == ChartType.BOX_PLOT:
            config.update({
                "box_colors": self.palette[:6],
                "whisker_color": self._darken(self.config.primary, 0.2),
                "median_color": self.config.tertiary,
                "outlier_color": self.config.tertiary,
                "alpha": 0.7
            })
        
        elif chart_type == ChartType.HISTOGRAM:
            config.update({
                "color": self.config.primary,
                "edge_color": self._darken(self.config.primary, 0.2),
                "alpha": 0.7,
                "bins": 30
            })
        
        elif chart_type == ChartType.CONTROL_CHART:
            config.update({
                "data_color": self.config.primary,
                "mean_color": self.config.secondary,
                "limit_color": self.config.tertiary,
                "violation_color": "#FF0000",
                "line_width": 1.5,
                "marker_size": 6
            })
        
        elif chart_type == ChartType.PARETO:
            config.update({
                "bar_colors": self._create_gradient(
                    self.config.primary,
                    self._lighten(self.config.primary, 0.3),
                    steps=10
                ),
                "line_color": self.config.tertiary,
                "cumulative_alpha": 1.0,
                "bar_alpha": 0.8
            })
        
        elif chart_type == ChartType.GANTT:
            config.update({
                "task_colors": self.palette[:10],
                "dependency_color": "#666666",
                "today_line_color": self.config.tertiary,
                "alpha": 0.8
            })
        
        elif chart_type == ChartType.BUBBLE_CHART:
            config.update({
                "bubble_colors": self.palette,
                "edge_color": self._darken(self.config.primary, 0.2),
                "alpha": 0.6,
                "size_scale": 1.0
            })
        
        elif chart_type == ChartType.ERROR_BAR:
            config.update({
                "marker_color": self.config.primary,
                "error_color": self.config.tertiary,
                "cap_size": 5,
                "line_width": 1.5,
                "marker_size": 8
            })
        
        elif chart_type == ChartType.HEXBIN:
            config.update({
                "colormap": self._create_colormap(
                    self._lighten(self.config.primary, 0.5),
                    self.config.tertiary
                ),
                "gridsize": 30,
                "mincnt": 1,
                "alpha": 0.8
            })
        
        return config
    
    def get_color_for_value(self, value: float, min_val: float, max_val: float) -> str:
        """Get color based on value within range."""
        if max_val == min_val:
            return self.config.primary
        
        ratio = (value - min_val) / (max_val - min_val)
        
        if ratio < 0.33:
            return self._mix_colors(self.config.tertiary, self.config.secondary, ratio * 3)
        elif ratio < 0.67:
            return self._mix_colors(self.config.secondary, self.config.primary, (ratio - 0.33) * 3)
        else:
            return self._mix_colors(self.config.primary, self._darken(self.config.primary, 0.2), (ratio - 0.67) * 3)
    
    def get_categorical_colors(self, n_categories: int) -> List[str]:
        """Get colors for categorical data."""
        if n_categories <= len(self.palette):
            return self.palette[:n_categories]
        
        # Generate additional colors if needed
        colors = list(self.palette)
        while len(colors) < n_categories:
            # Mix existing colors to create new ones
            idx1 = len(colors) % len(self.palette)
            idx2 = (len(colors) + 1) % len(self.palette)
            new_color = self._mix_colors(self.palette[idx1], self.palette[idx2])
            colors.append(new_color)
        
        return colors[:n_categories]
    
    def apply_theme_to_code(self, python_code: str, chart_type: ChartType) -> str:
        """Apply theme to Python matplotlib code."""
        theme_config = self.apply_to_chart(chart_type)
        style_dict = self.get_style_dict()
        
        # Create theme setup code
        theme_setup = f"""
# Apply theme
import matplotlib.pyplot as plt
import matplotlib as mpl

# Set style parameters
style_params = {style_dict}
for key, value in style_params.items():
    mpl.rcParams[key] = value

# Theme colors
theme_colors = {theme_config['colors']}
primary_color = '{theme_config['primary']}'
secondary_color = '{theme_config['secondary']}'
tertiary_color = '{theme_config['tertiary']}'
"""
        
        # Insert theme setup at the beginning of the code
        import_end = python_code.find('\n\n')
        if import_end > 0:
            return python_code[:import_end] + '\n' + theme_setup + python_code[import_end:]
        else:
            return theme_setup + '\n' + python_code