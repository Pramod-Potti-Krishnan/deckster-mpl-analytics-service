# Analytics Agent V2 - Technical Documentation

## Table of Contents
- [Overview](#overview)
- [Architecture](#architecture)
- [Core Components](#core-components)
- [Data Flow](#data-flow)
- [Supported Chart Types](#supported-chart-types)
- [API Reference](#api-reference)
- [Usage Examples](#usage-examples)
- [Configuration](#configuration)
- [Error Handling](#error-handling)
- [Performance Considerations](#performance-considerations)

## Overview

Analytics Agent V2 is a sophisticated AI-powered analytics generation system that creates data visualizations from natural language descriptions. It combines LLM intelligence with deterministic chart generation to produce high-quality, contextually appropriate visualizations.

### Key Features
- **23 Chart Types**: Comprehensive coverage from basic bar charts to complex statistical visualizations
- **AI-Powered Selection**: Intelligent chart type selection based on user intent and data characteristics
- **Synthetic Data Generation**: LLM-enhanced data generation when user data is not provided
- **Advanced Theming**: Smart color theming with gradient support and contrast optimization
- **Rate Limiting**: Built-in API rate management for production deployments
- **Multiple Execution Methods**: Python/MCP execution, Mermaid diagrams, and standalone code generation

### Version
- **Current Version**: 2.0
- **Author**: Analytics Agent System V2
- **Year**: 2024

## Architecture

### System Architecture
```
┌─────────────────────────────────────────────────┐
│                  User Request                    │
│            (Natural Language + Data)             │
└─────────────────────┬───────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────┐
│              AnalyticsAgentV2                   │
│           (Main Orchestrator)                   │
│  ┌──────────────────────────────────────────┐  │
│  │ • Request validation                      │  │
│  │ • Component coordination                  │  │
│  │ • Response formatting                     │  │
│  │ • Statistics tracking                     │  │
│  └──────────────────────────────────────────┘  │
└────────┬────────────┬────────────┬─────────────┘
         │            │            │
         ▼            ▼            ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│  Conductor   │ │ DataManager  │ │ PythonAgent  │
│              │ │              │ │              │
│ • Chart      │ │ • Data       │ │ • Code       │
│   selection  │ │   fetching   │ │   generation │
│ • LLM calls  │ │ • Synthetic  │ │ • Execution  │
│ • Playbook   │ │   generation │ │ • Rendering  │
└──────────────┘ └──────────────┘ └──────────────┘
         │            │            │
         ▼            ▼            ▼
┌─────────────────────────────────────────────────┐
│           Supporting Components                  │
│  ┌──────────────────────────────────────────┐  │
│  │ • ThemeEngine: Color and style management│  │
│  │ • RateLimiter: API call management       │  │
│  │ • MCPExecutor: Code execution engine     │  │
│  │ • FileUtils: Output persistence          │  │
│  └──────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
```

### Component Interaction Model
The system follows an orchestrator pattern where `AnalyticsAgentV2` coordinates between specialized components:

1. **Request Phase**: Validates and prepares the analytics request
2. **Selection Phase**: Conductor analyzes intent and selects optimal chart type
3. **Data Phase**: DataManager prepares or generates appropriate data
4. **Generation Phase**: PythonAgent creates and executes visualization code
5. **Response Phase**: Results are formatted and returned with metadata

## Core Components

### 1. AnalyticsAgentV2 (`analytics_agent_v2.py`)
**Purpose**: Main orchestrator that coordinates all components

**Key Responsibilities**:
- Request lifecycle management
- Component initialization and coordination
- Error handling and fallback strategies
- Statistics and performance tracking
- Response formatting

**Key Methods**:
```python
async def generate(request: AnalyticsRequest) -> AnalyticsResponse:
    """Main generation pipeline"""
    
async def create_analytics_v2(...) -> Dict[str, Any]:
    """Public API entry point"""
    
async def batch_create_analytics_v2(...) -> List[Dict[str, Any]]:
    """Batch processing support"""
```

### 2. AnalyticsConductor (`conductor.py`)
**Purpose**: Intelligent chart type selection using LLM and rules

**Features**:
- LLM-powered chart selection with Gemini 2.0 Flash
- Playbook-based rules for deterministic fallbacks
- Confidence scoring for selections
- Secondary chart recommendations

**Key Components**:
```python
class ChartSelection(BaseModel):
    primary_chart: str  # Selected chart type
    secondary_chart: Optional[str]  # Fallback option
    reasoning: str  # Why this chart was selected
    confidence: float  # 0-1 confidence score
```

### 3. DataManager (`data_manager.py`)
**Purpose**: Data preparation and synthetic generation

**Capabilities**:
- User data validation and normalization
- Synthetic data generation with LLM enhancement
- Statistical analysis and insights
- Multi-series data handling
- Time series generation

**Data Generation Patterns**:
- **Trend**: Linear/exponential growth patterns
- **Seasonal**: Cyclic patterns with noise
- **Random**: Statistical distributions
- **Mixed**: Combination of patterns

### 4. PythonChartAgent (`python_chart_agent.py`)
**Purpose**: Chart code generation and execution

**Features**:
- Fixed implementations for all 23 chart types
- Matplotlib-based rendering
- Theme application
- Base64 image encoding
- Error recovery mechanisms

**Chart Categories**:
- **Line & Trend**: line_chart, step_chart, area_chart, stacked_area_chart
- **Bar Charts**: bar_vertical, bar_horizontal, grouped_bar, stacked_bar
- **Distribution**: histogram, box_plot, violin_plot
- **Correlation**: scatter_plot, bubble_chart, hexbin
- **Composition**: pie_chart, waterfall, funnel
- **Comparison**: radar_chart, heatmap
- **Statistical**: error_bar, control_chart, pareto
- **Project**: gantt

### 5. ThemeEngine (`theme_engine.py`)
**Purpose**: Advanced theming and styling

**Features**:
- Color palette generation with gradients
- Smart text color contrast
- Theme style presets (modern, classic, minimal, dark, corporate)
- Matplotlib style injection
- Transparency and font management

### 6. RateLimiter (`rate_limiter.py`)
**Purpose**: API call management and throttling

**Capabilities**:
- Token bucket algorithm
- Exponential backoff retry logic
- Batch request handling
- Per-API configuration
- Statistics tracking

## Data Flow

### Standard Request Flow
```
1. User Request
   ├─ Content: "Show quarterly revenue growth"
   ├─ Data: Optional user data
   └─ Theme: Color preferences

2. Request Validation (AnalyticsAgentV2)
   ├─ Parse parameters
   ├─ Initialize request object
   └─ Set defaults

3. Chart Selection (Conductor)
   ├─ Analyze intent with LLM
   ├─ Match playbook rules
   └─ Return ChartPlan

4. Data Preparation (DataManager)
   ├─ Check for user data
   ├─ Generate synthetic if needed
   ├─ Enhance labels with LLM
   └─ Calculate statistics

5. Chart Generation (PythonAgent)
   ├─ Generate Python code
   ├─ Apply theme
   ├─ Execute with MCP/Local
   └─ Encode to base64

6. Response Assembly
   ├─ Chart image (base64)
   ├─ Structured data (JSON)
   ├─ Metadata
   └─ Insights
```

## Supported Chart Types

### Line and Trend Charts
| Type | Best For | Data Points |
|------|----------|-------------|
| `line_chart` | Time series, trends | 5-100 |
| `step_chart` | Discrete changes | 5-50 |
| `area_chart` | Volume over time | 5-100 |
| `stacked_area_chart` | Part-to-whole trends | 3-5 series |

### Bar Charts
| Type | Best For | Data Points |
|------|----------|-------------|
| `bar_chart_vertical` | Category comparison | 3-20 |
| `bar_chart_horizontal` | Long labels | 3-20 |
| `grouped_bar` | Multi-series comparison | 2-4 series |
| `stacked_bar` | Part-to-whole | 3-5 parts |

### Distribution Charts
| Type | Best For | Data Points |
|------|----------|-------------|
| `histogram` | Frequency distribution | 30+ |
| `box_plot` | Statistical summary | 5+ groups |
| `violin_plot` | Distribution shape | 3+ groups |

### Correlation Charts
| Type | Best For | Data Points |
|------|----------|-------------|
| `scatter_plot` | Correlation analysis | 20-500 |
| `bubble_chart` | 3D relationships | 10-100 |
| `hexbin` | Dense scatter data | 500+ |

### Composition Charts
| Type | Best For | Data Points |
|------|----------|-------------|
| `pie_chart` | Part-to-whole | 3-8 |
| `waterfall` | Incremental changes | 5-15 |
| `funnel` | Process stages | 3-7 |

### Comparison Charts
| Type | Best For | Data Points |
|------|----------|-------------|
| `radar_chart` | Multi-dimensional | 4-8 dimensions |
| `heatmap` | Matrix relationships | 5x5 to 20x20 |

### Statistical Charts
| Type | Best For | Data Points |
|------|----------|-------------|
| `error_bar` | Uncertainty ranges | 5-20 |
| `control_chart` | Process monitoring | 20+ |
| `pareto` | 80/20 analysis | 5-15 |

### Project Charts
| Type | Best For | Data Points |
|------|----------|-------------|
| `gantt` | Project timeline | 5-20 tasks |

## API Reference

### Main Entry Point
```python
async def create_analytics_v2(
    content: str,                           # Required: Chart description
    title: Optional[str] = None,           # Chart title
    data: Optional[List[Dict]] = None,     # User data
    use_synthetic_data: bool = True,       # Generate if no data
    theme: Optional[Dict] = None,          # Theme config
    chart_type: Optional[str] = None,      # Force chart type
    enhance_labels: bool = True,           # LLM enhancement
    mcp_tool=None,                          # MCP executor
    save_files: bool = False,              # Save outputs
    output_dir: str = "analytics_output"   # Output directory
) -> Dict[str, Any]
```

### Request Models
```python
class AnalyticsRequest(BaseModel):
    content: str                            # Chart description
    title: Optional[str]                    # Chart title
    data: Optional[List[Dict[str, Any]]]   # User data
    use_synthetic_data: bool = True        # Synthetic fallback
    theme: Optional[ThemeConfig]           # Theme settings
    chart_preference: Optional[ChartType]  # Preferred type
    output_format: Literal["png", "svg", "base64"] = "png"
    include_raw_data: bool = True         # Include JSON
    enhance_labels: bool = True           # LLM labels
```

### Response Structure
```python
{
    "success": true,
    "chart": "base64_encoded_image",
    "data": {
        "labels": ["Q1", "Q2", "Q3", "Q4"],
        "values": [45000, 52000, 48000, 61000],
        "series": null,
        "statistics": {
            "min": 45000,
            "max": 61000,
            "mean": 51500,
            "median": 50000,
            "std": 6557.4
        }
    },
    "metadata": {
        "chart_type": "bar_chart_vertical",
        "generation_method": "python_mcp",
        "data_source": "synthetic",
        "insights": [
            "Data range: 45000.0 to 61000.0",
            "Average value: 51500.0",
            "Increasing trend detected"
        ],
        "generation_time_ms": 1250.5,
        "data_points_count": 4,
        "llm_enhanced": true
    },
    "code": "# Generated Python code..."
}
```

## Usage Examples

### Basic Chart Generation
```python
import asyncio
from analytics_agent_v2 import create_analytics_v2

async def generate_simple_chart():
    result = await create_analytics_v2(
        content="Show monthly sales for 2024",
        title="2024 Sales Performance"
    )
    
    if result['success']:
        # Chart is in result['chart'] as base64
        print(f"Generated {result['metadata']['chart_type']}")
```

### With User Data
```python
async def generate_with_data():
    user_data = [
        {"label": "Product A", "value": 45},
        {"label": "Product B", "value": 78},
        {"label": "Product C", "value": 63},
        {"label": "Product D", "value": 91}
    ]
    
    result = await create_analytics_v2(
        content="Compare product performance",
        data=user_data,
        chart_type="bar_chart_horizontal"
    )
```

### Custom Theme
```python
async def generate_themed():
    theme = {
        "primary": "#FF6B6B",
        "secondary": "#4ECDC4",
        "tertiary": "#45B7D1",
        "style": "modern",
        "gradient": True
    }
    
    result = await create_analytics_v2(
        content="Customer satisfaction by department",
        theme=theme
    )
```

### Batch Processing
```python
async def generate_batch():
    requests = [
        {"content": "Q1 revenue", "chart_type": "pie_chart"},
        {"content": "Q2 revenue", "chart_type": "pie_chart"},
        {"content": "Q3 revenue", "chart_type": "pie_chart"}
    ]
    
    results = await batch_create_analytics_v2(
        requests=requests,
        batch_size=3,
        batch_delay=30.0
    )
```

## Configuration

### Environment Variables
```bash
# LLM Configuration
GOOGLE_API_KEY=your_gemini_api_key

# Rate Limiting
RATE_LIMIT_TOKENS=100
RATE_LIMIT_WINDOW=60

# Execution
ENABLE_MCP=true
MCP_TIMEOUT=30
```

### Theme Configuration
```python
class ThemeConfig(BaseModel):
    primary: str = "#1E40AF"      # Primary color
    secondary: str = "#10B981"    # Secondary color
    tertiary: str = "#F59E0B"     # Tertiary color
    style: ThemeStyle = "modern"  # Style preset
    gradient: bool = True         # Use gradients
    transparency: float = 0.8     # Alpha value
    font_family: str = "Arial"    # Font family
    font_size: int = 12          # Base font size
```

### Rate Limiter Configuration
```python
# API-specific limits
RATE_LIMITS = {
    "gemini": {
        "requests_per_minute": 60,
        "tokens_per_minute": 60000
    },
    "openai": {
        "requests_per_minute": 50,
        "tokens_per_minute": 40000
    }
}
```

## Error Handling

### Error Types
1. **ValidationError**: Invalid request parameters
2. **DataError**: Data parsing or generation failure
3. **GenerationError**: Chart creation failure
4. **ExecutionError**: Code execution failure
5. **RateLimitError**: API quota exceeded

### Fallback Strategies
```python
# Automatic fallbacks
1. Primary chart fails → Try secondary chart
2. LLM fails → Use playbook rules
3. Synthetic data fails → Use default data
4. Theme fails → Use default theme
5. Execution fails → Return code only
```

### Error Response
```python
{
    "success": false,
    "error": "Chart generation failed: Invalid data format",
    "metadata": {
        "chart_type": "fallback_type",
        "generation_method": "fallback",
        "attempted_methods": ["python_mcp", "mermaid"]
    }
}
```

## Performance Considerations

### Optimization Strategies
1. **Caching**: Results cached for identical requests
2. **Batch Processing**: Multiple charts in parallel
3. **Rate Limiting**: Prevent API throttling
4. **Code Generation**: Pre-compiled chart templates
5. **Data Limits**: Automatic sampling for large datasets

### Performance Metrics
- **Average Generation Time**: 1-3 seconds
- **LLM Call Time**: 500-1500ms
- **Code Execution Time**: 200-500ms
- **Image Encoding Time**: 50-100ms

### Scalability
- **Concurrent Requests**: Up to 10 per instance
- **Batch Size**: Optimal at 5-10 charts
- **Data Points**: Tested up to 10,000 points
- **Memory Usage**: ~100MB base + 10MB per chart

## Best Practices

### Request Optimization
1. Provide clear, specific descriptions
2. Include data when available
3. Specify chart type if known
4. Use appropriate data ranges

### Data Preparation
1. Validate data before submission
2. Use consistent formats
3. Limit to necessary points
4. Include meaningful labels

### Theme Selection
1. Choose contrasting colors
2. Consider accessibility
3. Match brand guidelines
4. Test on different backgrounds

### Error Recovery
1. Implement retry logic
2. Handle partial failures
3. Log errors for debugging
4. Provide user feedback

## Troubleshooting

### Common Issues

**Issue**: Chart type not appropriate
- **Solution**: Provide more specific description or force chart type

**Issue**: Synthetic data unrealistic
- **Solution**: Provide sample data or data ranges

**Issue**: Rate limit exceeded
- **Solution**: Implement batching with delays

**Issue**: Theme not applying
- **Solution**: Verify hex color format and values

**Issue**: Execution timeout
- **Solution**: Reduce data points or simplify chart

## Future Enhancements

### Planned Features
1. **Real-time Updates**: WebSocket support for live data
2. **Interactive Charts**: Plotly/D3.js integration
3. **Custom Templates**: User-defined chart types
4. **ML Insights**: Advanced pattern detection
5. **Export Formats**: PDF, SVG, HTML support

### API Evolution
- Version 2.1: WebSocket support
- Version 2.2: Interactive charts
- Version 3.0: Full microservice architecture

---

*Last Updated: January 2025*
*Version: 2.0*
*Status: Production Ready*