# Chart Types Guide - Analytics Microservice V2

## Overview

This guide provides detailed information about all 23 chart types available in the Analytics Microservice V2, including when to use each type, example requests, and expected outputs.

---

## Chart Categories

### 📈 Line and Trend Charts (4 types)
Best for showing changes over time and trends

### 📊 Bar Charts (4 types)
Best for comparing values across categories

### 📉 Distribution Charts (3 types)
Best for showing data distribution and statistical properties

### 🔵 Correlation Charts (3 types)
Best for showing relationships between variables

### 🥧 Composition Charts (3 types)
Best for showing part-to-whole relationships

### 🎯 Comparison Charts (2 types)
Best for multi-dimensional comparisons

### 📐 Statistical Charts (3 types)
Best for quality control and statistical analysis

### 📅 Project Charts (1 type)
Best for project management and timelines

---

## Line and Trend Charts

### 1. Line Chart (`line_chart`)

**Purpose**: Show trends and changes over continuous time periods

**Best For**:
- Stock prices over time
- Temperature changes
- Revenue trends
- User growth metrics

**Request Example**:
```json
{
    "payload": {
        "content": "Show monthly revenue trend for 2024",
        "chart_preference": "line_chart"
    }
}
```

**Characteristics**:
- X-axis: Time periods (temporal)
- Y-axis: Values (numerical)
- Smooth continuous lines
- Good for spotting trends

---

### 2. Step Chart (`step_chart`)

**Purpose**: Show discrete changes at specific points in time

**Best For**:
- Interest rate changes
- Price adjustments
- Status changes
- Threshold crossings

**Request Example**:
```json
{
    "payload": {
        "content": "Show interest rate changes throughout 2024",
        "chart_preference": "step_chart"
    }
}
```

**Characteristics**:
- X-axis: Time points (temporal)
- Y-axis: Values (numerical)
- Horizontal lines with vertical jumps
- Emphasizes discrete changes

---

### 3. Area Chart (`area_chart`)

**Purpose**: Show volume or magnitude changes over time

**Best For**:
- Cumulative values
- Volume trends
- Population growth
- Resource consumption

**Request Example**:
```json
{
    "payload": {
        "content": "Display cumulative sales volume by month",
        "chart_preference": "area_chart"
    }
}
```

**Characteristics**:
- X-axis: Time periods (temporal)
- Y-axis: Values (numerical)
- Filled area under the line
- Emphasizes magnitude

---

### 4. Stacked Area Chart (`stacked_area_chart`)

**Purpose**: Show how multiple series contribute to a total over time

**Best For**:
- Market share over time
- Budget allocation trends
- Component contributions
- Resource distribution

**Request Example**:
```json
{
    "payload": {
        "content": "Show revenue breakdown by product line over quarters",
        "chart_preference": "stacked_area_chart"
    }
}
```

**Characteristics**:
- X-axis: Time periods (temporal)
- Y-axis: Cumulative values (numerical)
- Multiple stacked areas
- Shows both total and composition

---

## Bar Charts

### 5. Vertical Bar Chart (`bar_chart_vertical`)

**Purpose**: Compare values across different categories

**Best For**:
- Sales by product
- Performance by department
- Votes by candidate
- Scores by team

**Request Example**:
```json
{
    "payload": {
        "content": "Compare sales across product categories",
        "chart_preference": "bar_chart_vertical"
    }
}
```

**Characteristics**:
- X-axis: Categories (categorical)
- Y-axis: Values (numerical)
- Vertical bars
- Easy comparison of heights

---

### 6. Horizontal Bar Chart (`bar_chart_horizontal`)

**Purpose**: Compare values when category names are long

**Best For**:
- Rankings
- Survey responses
- Long category names
- Top 10 lists

**Request Example**:
```json
{
    "payload": {
        "content": "Show top 10 countries by population",
        "chart_preference": "bar_chart_horizontal"
    }
}
```

**Characteristics**:
- X-axis: Values (numerical)
- Y-axis: Categories (categorical)
- Horizontal bars
- Better for long labels

---

### 7. Grouped Bar Chart (`grouped_bar_chart`)

**Purpose**: Compare multiple series across categories

**Best For**:
- Year-over-year comparisons
- Multiple metrics by category
- A/B test results
- Regional comparisons

**Request Example**:
```json
{
    "payload": {
        "content": "Compare Q1 vs Q2 sales by product category",
        "chart_preference": "grouped_bar_chart"
    }
}
```

**Characteristics**:
- X-axis: Categories (categorical)
- Y-axis: Values (numerical)
- Multiple bars per category
- Side-by-side comparison

---

### 8. Stacked Bar Chart (`stacked_bar_chart`)

**Purpose**: Show composition within categories

**Best For**:
- Budget breakdowns
- Market composition
- Resource allocation
- Survey results by segment

**Request Example**:
```json
{
    "payload": {
        "content": "Show expense breakdown by department",
        "chart_preference": "stacked_bar_chart"
    }
}
```

**Characteristics**:
- X-axis: Categories (categorical)
- Y-axis: Cumulative values (numerical)
- Stacked segments in each bar
- Shows total and parts

---

## Distribution Charts

### 9. Histogram (`histogram`)

**Purpose**: Show frequency distribution of continuous data

**Best For**:
- Age distribution
- Score distribution
- Response times
- Price ranges

**Request Example**:
```json
{
    "payload": {
        "content": "Show distribution of customer ages",
        "chart_preference": "histogram"
    }
}
```

**Characteristics**:
- X-axis: Value ranges (numerical)
- Y-axis: Frequency (count)
- Bins of continuous data
- Shows data concentration

---

### 10. Box Plot (`box_plot`)

**Purpose**: Show statistical distribution and outliers

**Best For**:
- Comparing distributions
- Identifying outliers
- Statistical analysis
- Quality control

**Request Example**:
```json
{
    "payload": {
        "content": "Compare salary distributions across departments",
        "chart_preference": "box_plot"
    }
}
```

**Characteristics**:
- X-axis: Categories (categorical)
- Y-axis: Values (numerical)
- Shows median, quartiles, outliers
- Compact statistical summary

---

### 11. Violin Plot (`violin_plot`)

**Purpose**: Show distribution shape and density

**Best For**:
- Bimodal distributions
- Density comparison
- Advanced statistical analysis
- Research data

**Request Example**:
```json
{
    "payload": {
        "content": "Show distribution of test scores by class",
        "chart_preference": "violin_plot"
    }
}
```

**Characteristics**:
- X-axis: Categories (categorical)
- Y-axis: Values (numerical)
- Shows distribution shape
- Combines box plot with density

---

## Correlation Charts

### 12. Scatter Plot (`scatter_plot`)

**Purpose**: Show correlation between two variables

**Best For**:
- Price vs demand
- Height vs weight
- Study time vs scores
- Temperature vs sales

**Request Example**:
```json
{
    "payload": {
        "content": "Show correlation between advertising spend and sales",
        "chart_preference": "scatter_plot"
    }
}
```

**Characteristics**:
- X-axis: Variable 1 (numerical)
- Y-axis: Variable 2 (numerical)
- Individual data points
- Pattern reveals correlation

---

### 13. Bubble Chart (`bubble_chart`)

**Purpose**: Show three dimensions of data

**Best For**:
- Market analysis (price, volume, growth)
- Risk assessment
- Portfolio analysis
- Multi-factor comparison

**Request Example**:
```json
{
    "payload": {
        "content": "Compare products by price, sales volume, and profit margin",
        "chart_preference": "bubble_chart"
    }
}
```

**Characteristics**:
- X-axis: Variable 1 (numerical)
- Y-axis: Variable 2 (numerical)
- Bubble size: Variable 3
- Three dimensions in 2D space

---

### 14. Hexbin Chart (`hexbin`)

**Purpose**: Show density in large scatter plot data

**Best For**:
- Large datasets
- Density visualization
- Geographic data
- Heatmap alternative

**Request Example**:
```json
{
    "payload": {
        "content": "Show density of customer locations",
        "chart_preference": "hexbin"
    }
}
```

**Characteristics**:
- X-axis: Variable 1 (numerical)
- Y-axis: Variable 2 (numerical)
- Hexagonal bins
- Color indicates density

---

## Composition Charts

### 15. Pie Chart (`pie_chart`)

**Purpose**: Show proportions of a whole

**Best For**:
- Market share
- Budget allocation
- Survey results
- Category distribution

**Request Example**:
```json
{
    "payload": {
        "content": "Show market share distribution",
        "chart_preference": "pie_chart"
    }
}
```

**Characteristics**:
- Categories as slices
- Values as percentages
- Best for 2-7 categories
- Shows part-to-whole

---

### 16. Waterfall Chart (`waterfall`)

**Purpose**: Show cumulative effect of sequential changes

**Best For**:
- Profit bridges
- Budget changes
- Inventory flow
- Year-over-year changes

**Request Example**:
```json
{
    "payload": {
        "content": "Show how revenue changed from Q1 to Q4",
        "chart_preference": "waterfall"
    }
}
```

**Characteristics**:
- X-axis: Stages (categorical)
- Y-axis: Cumulative value (numerical)
- Positive and negative changes
- Running total visualization

---

### 17. Funnel Chart (`funnel`)

**Purpose**: Show progressive reduction through stages

**Best For**:
- Sales pipeline
- Conversion rates
- User journey
- Process efficiency

**Request Example**:
```json
{
    "payload": {
        "content": "Show customer conversion funnel from visit to purchase",
        "chart_preference": "funnel"
    }
}
```

**Characteristics**:
- Stages from top to bottom
- Width represents volume
- Shows drop-off rates
- Process flow visualization

---

## Comparison Charts

### 18. Radar Chart (`radar_chart`)

**Purpose**: Compare multiple dimensions simultaneously

**Best For**:
- Performance metrics
- Feature comparison
- Skill assessment
- Product profiles

**Request Example**:
```json
{
    "payload": {
        "content": "Compare employee skills across different dimensions",
        "chart_preference": "radar_chart"
    }
}
```

**Characteristics**:
- Multiple axes from center
- Polygonal shape
- Multiple series overlay
- Multi-dimensional comparison

---

### 19. Heatmap (`heatmap`)

**Purpose**: Show intensity across two dimensions

**Best For**:
- Correlation matrices
- Activity patterns
- Geographic data
- Time-based patterns

**Request Example**:
```json
{
    "payload": {
        "content": "Show website traffic by hour and day of week",
        "chart_preference": "heatmap"
    }
}
```

**Characteristics**:
- X-axis: Category 1 (categorical)
- Y-axis: Category 2 (categorical)
- Color: Intensity value
- Matrix visualization

---

## Statistical Charts

### 20. Error Bar Chart (`error_bar_chart`)

**Purpose**: Show confidence intervals and variability

**Best For**:
- Scientific data
- Survey results with margins
- Experimental results
- Quality measurements

**Request Example**:
```json
{
    "payload": {
        "content": "Show experimental results with confidence intervals",
        "chart_preference": "error_bar_chart"
    }
}
```

**Characteristics**:
- X-axis: Conditions (categorical)
- Y-axis: Measurements (numerical)
- Error bars show variability
- Statistical confidence display

---

### 21. Control Chart (`control_chart`)

**Purpose**: Monitor process stability over time

**Best For**:
- Quality control
- Manufacturing processes
- Service metrics
- Performance monitoring

**Request Example**:
```json
{
    "payload": {
        "content": "Monitor production quality over time",
        "chart_preference": "control_chart"
    }
}
```

**Characteristics**:
- X-axis: Time/samples (temporal)
- Y-axis: Measurements (numerical)
- Control limits (UCL/LCL)
- Process stability tracking

---

### 22. Pareto Chart (`pareto`)

**Purpose**: Show most significant factors (80/20 rule)

**Best For**:
- Problem prioritization
- Defect analysis
- Cost drivers
- Customer complaints

**Request Example**:
```json
{
    "payload": {
        "content": "Show main causes of customer complaints",
        "chart_preference": "pareto"
    }
}
```

**Characteristics**:
- X-axis: Causes (categorical)
- Y-axis: Frequency (count)
- Bars in descending order
- Cumulative line overlay

---

## Project Charts

### 23. Gantt Chart (`gantt`)

**Purpose**: Show project timeline and dependencies

**Best For**:
- Project schedules
- Resource planning
- Task dependencies
- Timeline visualization

**Request Example**:
```json
{
    "payload": {
        "content": "Show project timeline with all tasks",
        "chart_preference": "gantt"
    }
}
```

**Characteristics**:
- X-axis: Timeline (temporal)
- Y-axis: Tasks (categorical)
- Horizontal bars for duration
- Dependencies and milestones

---

## Chart Selection Guide

### By Data Type

**Categorical vs Numerical**:
- Use bar charts, pie charts

**Time Series**:
- Use line charts, area charts

**Distribution**:
- Use histograms, box plots

**Correlation**:
- Use scatter plots, bubble charts

**Composition**:
- Use pie charts, stacked charts

### By Purpose

**Comparison**:
- Bar charts for categories
- Line charts for trends
- Radar charts for multiple dimensions

**Distribution**:
- Histogram for frequency
- Box plot for statistics
- Violin plot for shape

**Relationship**:
- Scatter plot for correlation
- Bubble chart for 3D data
- Heatmap for matrix data

**Composition**:
- Pie chart for proportions
- Stacked bar for parts
- Waterfall for changes

**Process**:
- Funnel for stages
- Gantt for timeline
- Control chart for monitoring

---

## Best Practices

### Do's ✅
1. **Match chart to data type** - Categorical, numerical, temporal
2. **Consider audience** - Technical vs general
3. **Limit data points** - Keep it readable
4. **Use appropriate scale** - Linear vs logarithmic
5. **Include context** - Titles, labels, units

### Don'ts ❌
1. **Don't use pie charts** for more than 7 categories
2. **Don't use 3D effects** unnecessarily
3. **Don't overcrowd** the visualization
4. **Don't mix chart types** inappropriately
5. **Don't ignore color blindness** considerations

---

## Examples by Industry

### Finance
- Line charts for stock prices
- Waterfall for P&L analysis
- Heatmap for correlation matrix
- Control charts for risk monitoring

### Sales & Marketing
- Bar charts for product comparison
- Funnel for conversion tracking
- Pie chart for market share
- Scatter plot for price optimization

### Manufacturing
- Control charts for quality
- Pareto for defect analysis
- Gantt for production planning
- Histogram for measurements

### Healthcare
- Box plots for patient data
- Line charts for vital signs
- Heatmap for symptom patterns
- Error bars for clinical trials

### Education
- Histogram for grade distribution
- Radar chart for skill assessment
- Bar chart for performance comparison
- Scatter plot for correlation studies

---

## Advanced Features

### Multi-Series Support
Charts that support multiple data series:
- Line chart
- Area chart (stacked)
- Bar chart (grouped/stacked)
- Scatter plot

### Statistical Enhancement
Charts with statistical features:
- Box plot (quartiles, outliers)
- Violin plot (density)
- Error bar (confidence intervals)
- Control chart (control limits)

### Time Intelligence
Charts optimized for time data:
- Line chart
- Step chart
- Area chart
- Control chart

---

*For implementation details, see the [API Documentation](./WEBSOCKET_API_DOCUMENTATION.md)*