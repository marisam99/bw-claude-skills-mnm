# Bellwether Data Visualization Reference

## Core Principles

Bellwether data visualizations should be clear, purposeful, and restrained. The
goal is to communicate insight, not to display visual complexity. Every element
on a chart should earn its place.

The four pillars:
- **Text** — Every chart needs a headline that states the finding, not just a
  description of what is shown.
- **Arrangement** — Layout and composition should guide the reader's eye to the
  key insight first.
- **Color** — Use color deliberately to direct attention, not decorate.
- **Lines and details** — Reduce visual noise: fewer gridlines, fewer borders,
  fewer tick marks.

---

## Chart Color Sequence

Assign colors to data series in this order. Never skip ahead or rearrange.

| Series | Color | Hex |
|---|---|---|
| 1 | Plum | `#6D1E4A` |
| 2 | Teal | `#007786` |
| 3 | Light Gray | `#BEC6CE` |
| 4 | Navy | `#212B46` |
| 5 | Cream | `#F0DEC1` |
| 6 | Deep Green | `#0D525A` |
| 7 | Peach | `#FFA497` |
| 8 | Yellow | `#FFC762` |
| 9 | Lavender | `#CAD3FB` |

Most charts need only 2–4 colors. If a visualization requires more than 6
distinct series, reconsider whether it should be split into multiple charts.

### Callout / Emphasis Colors

Do not use series colors for highlights. Reserve these for annotating a key
data point or drawing attention to a critical finding:

- **Yellow** `#FFC762` — primary callout, key data point
- **Orange** `#FFB653` — secondary callout, supporting emphasis

---

## Headlines and Annotations

**Lead with the finding.** Every chart title should be a declarative statement
of the key takeaway, placed in the upper-left. Avoid descriptive titles like
"Student Performance Over Time" — instead write "Proficiency rates rose 12
points after program implementation."

**Annotate directly.** Label data series and data points on the chart wherever
possible instead of relying on a legend. Direct labels reduce cognitive load
and are more accessible.

**Use callout boxes** (with Yellow or Cream fill) to highlight a single
statistic or annotation that deserves emphasis.

**Source lines** go in the lower-left in Avenir Next LT Pro Regular 9pt, Gray
(`#5A6675`). Format: *Source: [Organization, Year].*

---

## Visual Simplicity Rules

### Gridlines
- Use light horizontal gridlines only (Gray `#BEC6CE` at 50% opacity or lighter).
- Remove vertical gridlines entirely.
- Remove the chart border/box.

### Axes
- Label the Y-axis clearly with units. If the unit is obvious from context
  (e.g., "%" in a percentage chart), the axis label can be omitted.
- Remove tick marks from both axes.
- Axis text: Avenir Next LT Pro Regular, 9–10pt, Gray (`#5A6675`).

### Legends
- Only use a legend when direct labeling is genuinely impractical (e.g., a
  complex line chart with 5+ overlapping series). Place legends below the chart,
  not to the right.

### Backgrounds
- White or Cream (`#F0DEC1`) chart backgrounds only.
- Do not use patterned fills, gradient backgrounds, or drop shadows on chart elements.

### 3D Effects
- Never use 3D chart types. They distort data and reduce readability.

---

## Chart Type Guidance

| Goal | Preferred chart type |
|---|---|
| Compare categories | Horizontal bar chart |
| Show change over time | Line chart |
| Show composition (parts of a whole) | Stacked bar or waffle chart |
| Show distribution | Dot plot or histogram |
| Compare two variables | Scatter plot |
| Show a single summary stat | Bold callout number (not a chart) |

Avoid pie charts for more than 2–3 slices. Avoid donut charts.

---

## Tables in Documents

Tables follow the same visual restraint principles:

- **Header row**: Dark fill, white text, Avenir Next LT Pro Medium 12-14pt.
- **Alternating rows**: white and a very light tint of a brand color (e.g.,
  Teal at 10–15% opacity, or Light Gray `#BEC6CE` at 20%).
- **Borders**: light Gray (`#BEC6CE`) horizontal rules only — no vertical
  borders within the table.
- **Text alignment**: left-align text columns, right-align numeric columns.
- **Totals / summary rows**: Avenir Next LT Pro Medium, with a slightly darker
  background or a top border in Gray.

---

## Accessibility

- Ensure sufficient contrast between text and background. For small text (under
  14pt), target a contrast ratio of at least 4.5:1.
- Do not rely on color alone to convey meaning — use direct labels, patterns,
  or text annotations as supplements.
- Test charts in grayscale to confirm that series remain distinguishable without
  color. The Bellwether sequence is designed to vary in luminosity as well as
  hue, which helps here.

---

## Writing Style in Charts

Bellwether follows AP Style with these exceptions and notes for data contexts:

- Spell out numbers one through nine; use numerals for 10 and above.
- Use "%" not "percent" in chart labels and axes.
- Use an en dash (–) not a hyphen for ranges: "2019–2023."
- Capitalize the first word of a chart headline; otherwise sentence case.
- Avoid jargon in chart titles — write for a policy-literate but general audience.
