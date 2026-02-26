"""Clinical charts and graphs for MCP-UI rendering.

Generates interactive Chart.js visualizations for clinical data including:
- Lab result trends
- Vital signs over time
- Medication timelines
- Visit frequency
"""

import json
from typing import Any


class ClinicalChartBuilder:
    """Builds Chart.js visualizations for clinical data.

    All charts are rendered as HTML with embedded Chart.js that MCP-UI
    clients can display interactively.
    """

    # Chart color palette - accessible and clinical-appropriate
    CHART_COLORS = {
        "primary": "rgb(37, 99, 235)",
        "primary_bg": "rgba(37, 99, 235, 0.1)",
        "success": "rgb(16, 185, 129)",
        "success_bg": "rgba(16, 185, 129, 0.1)",
        "warning": "rgb(245, 158, 11)",
        "warning_bg": "rgba(245, 158, 11, 0.1)",
        "danger": "rgb(220, 38, 38)",
        "danger_bg": "rgba(220, 38, 38, 0.1)",
        "purple": "rgb(139, 92, 246)",
        "purple_bg": "rgba(139, 92, 246, 0.1)",
        "gray": "rgb(107, 114, 128)",
        "gray_bg": "rgba(107, 114, 128, 0.1)",
    }

    @classmethod
    def build_lab_trend_chart(
        cls,
        test_name: str,
        values: list[dict],
        normal_range: tuple[float, float] | None = None,
    ) -> str:
        """Build a line chart showing lab result trends over time.

        Args:
            test_name: Name of the lab test
            values: List of dicts with 'date', 'value' keys
            normal_range: Optional (min, max) tuple for reference line

        Returns:
            HTML with Chart.js visualization
        """
        if not values:
            return '<p style="color: #64748b; text-align: center;">No data available</p>'

        # Prepare data
        labels = [v.get("date", "")[:10] for v in values]
        data_points = [float(v.get("value", 0)) for v in values]

        # Determine if any values are abnormal
        abnormal_points = []
        if normal_range:
            low, high = normal_range
            for val in data_points:
                abnormal_points.append(val < low or val > high)
        else:
            abnormal_points = [False] * len(data_points)

        # Point colors based on abnormality
        point_colors = [
            cls.CHART_COLORS["danger"] if abn else cls.CHART_COLORS["primary"]
            for abn in abnormal_points
        ]

        chart_id = f"lab_chart_{hash(test_name) % 10000}"

        datasets = [
            {
                "label": test_name,
                "data": data_points,
                "borderColor": cls.CHART_COLORS["primary"],
                "backgroundColor": cls.CHART_COLORS["primary_bg"],
                "pointBackgroundColor": point_colors,
                "pointBorderColor": point_colors,
                "pointRadius": 6,
                "fill": True,
                "tension": 0.3,
            }
        ]

        # Add normal range band if provided
        annotations = {}
        if normal_range:
            annotations = {
                "normalRange": {
                    "type": "box",
                    "yMin": normal_range[0],
                    "yMax": normal_range[1],
                    "backgroundColor": "rgba(16, 185, 129, 0.1)",
                    "borderColor": "rgba(16, 185, 129, 0.3)",
                    "borderWidth": 1,
                    "label": {
                        "content": "Normal Range",
                        "enabled": True,
                        "position": "end",
                    },
                }
            }

        return cls._build_chart_html(
            chart_id=chart_id,
            chart_type="line",
            labels=labels,
            datasets=datasets,
            title=f"{test_name} Trend",
            y_axis_label=values[0].get("unit", "") if values else "",
            annotations=annotations,
        )

    @classmethod
    def build_vitals_dashboard(cls, vitals: list[dict]) -> str:
        """Build a multi-chart dashboard for vital signs.

        Args:
            vitals: List of vital sign records with date and measurements

        Returns:
            HTML with multiple Chart.js visualizations
        """
        if not vitals:
            return '<p style="color: #64748b; text-align: center;">No vitals data</p>'

        # Group vitals by type
        bp_data = []
        hr_data = []
        temp_data = []
        weight_data = []

        for v in vitals:
            date = v.get("date", "")[:10]
            if v.get("systolic") and v.get("diastolic"):
                bp_data.append(
                    {
                        "date": date,
                        "systolic": v["systolic"],
                        "diastolic": v["diastolic"],
                    }
                )
            if v.get("heart_rate"):
                hr_data.append({"date": date, "value": v["heart_rate"]})
            if v.get("temperature"):
                temp_data.append({"date": date, "value": v["temperature"]})
            if v.get("weight"):
                weight_data.append({"date": date, "value": v["weight"]})

        charts = []

        # Blood Pressure Chart (dual line)
        if bp_data:
            charts.append(cls._build_bp_chart(bp_data))

        # Heart Rate Chart
        if hr_data:
            charts.append(
                cls.build_lab_trend_chart(
                    "Heart Rate (bpm)",
                    hr_data,
                    normal_range=(60, 100),
                )
            )

        # Weight Trend
        if weight_data:
            charts.append(cls.build_lab_trend_chart("Weight (lbs)", weight_data))

        chart_items = "".join(f'<div class="chart-container">{chart}</div>' for chart in charts)
        return f"""
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
                    gap: 1rem;">
            {chart_items}
        </div>
        """

    @classmethod
    def _build_bp_chart(cls, bp_data: list[dict]) -> str:
        """Build blood pressure chart with systolic/diastolic lines."""
        chart_id = f"bp_chart_{hash(str(bp_data)) % 10000}"
        labels = [d["date"] for d in bp_data]

        datasets = [
            {
                "label": "Systolic",
                "data": [d["systolic"] for d in bp_data],
                "borderColor": cls.CHART_COLORS["danger"],
                "backgroundColor": cls.CHART_COLORS["danger_bg"],
                "pointRadius": 5,
                "tension": 0.3,
            },
            {
                "label": "Diastolic",
                "data": [d["diastolic"] for d in bp_data],
                "borderColor": cls.CHART_COLORS["primary"],
                "backgroundColor": cls.CHART_COLORS["primary_bg"],
                "pointRadius": 5,
                "tension": 0.3,
            },
        ]

        # Normal range annotations
        annotations = {
            "systolicHigh": {
                "type": "line",
                "yMin": 140,
                "yMax": 140,
                "borderColor": "rgba(220, 38, 38, 0.5)",
                "borderWidth": 2,
                "borderDash": [5, 5],
            },
            "diastolicHigh": {
                "type": "line",
                "yMin": 90,
                "yMax": 90,
                "borderColor": "rgba(37, 99, 235, 0.5)",
                "borderWidth": 2,
                "borderDash": [5, 5],
            },
        }

        return cls._build_chart_html(
            chart_id=chart_id,
            chart_type="line",
            labels=labels,
            datasets=datasets,
            title="Blood Pressure Trend",
            y_axis_label="mmHg",
            annotations=annotations,
        )

    @classmethod
    def build_medication_timeline(cls, medications: list[dict]) -> str:
        """Build a horizontal timeline of medication history.

        Args:
            medications: List of medication records with start/end dates

        Returns:
            HTML with medication timeline visualization
        """
        if not medications:
            return '<p style="color: #64748b; text-align: center;">No medications</p>'

        chart_id = f"med_timeline_{hash(str(medications)) % 10000}"

        # Build timeline data
        labels = [m.get("name", "Unknown")[:30] for m in medications]
        start_dates = []
        durations = []

        from datetime import datetime

        now = datetime.now()

        for med in medications:
            start = med.get("start_date", "")
            end = med.get("end_date", "")

            try:
                start_dt = datetime.strptime(start[:10], "%Y-%m-%d") if start else now
                end_dt = datetime.strptime(end[:10], "%Y-%m-%d") if end else now
                days_from_start = (now - start_dt).days
                duration = (end_dt - start_dt).days if end else (now - start_dt).days
                start_dates.append(-days_from_start)  # Negative for past
                durations.append(max(duration, 30))  # Min 30 days for visibility
            except ValueError:
                start_dates.append(0)
                durations.append(30)

        datasets = [
            {
                "label": "Duration (days)",
                "data": durations,
                "backgroundColor": [
                    cls.CHART_COLORS["primary"],
                    cls.CHART_COLORS["success"],
                    cls.CHART_COLORS["purple"],
                    cls.CHART_COLORS["warning"],
                    cls.CHART_COLORS["gray"],
                ]
                * (len(medications) // 5 + 1),
                "borderRadius": 4,
            }
        ]

        return cls._build_chart_html(
            chart_id=chart_id,
            chart_type="bar",
            labels=labels,
            datasets=datasets,
            title="Active Medications",
            x_axis_label="Days on medication",
            options_override={
                "indexAxis": "y",
                "scales": {
                    "x": {"title": {"display": True, "text": "Days"}},
                },
            },
        )

    @classmethod
    def build_visit_frequency_chart(cls, visits: list[dict]) -> str:
        """Build a bar chart showing visit frequency by month.

        Args:
            visits: List of appointment records with dates

        Returns:
            HTML with visit frequency chart
        """
        if not visits:
            return '<p style="color: #64748b; text-align: center;">No visits</p>'

        # Count visits by month
        from collections import defaultdict

        monthly_counts = defaultdict(int)

        for v in visits:
            date = v.get("date", "") or v.get("scheduled_time", "")
            if date:
                month_key = date[:7]  # YYYY-MM
                monthly_counts[month_key] += 1

        # Sort by date
        sorted_months = sorted(monthly_counts.keys())
        labels = sorted_months
        data = [monthly_counts[m] for m in sorted_months]

        chart_id = f"visits_chart_{hash(str(visits)) % 10000}"

        datasets = [
            {
                "label": "Visits",
                "data": data,
                "backgroundColor": cls.CHART_COLORS["primary_bg"],
                "borderColor": cls.CHART_COLORS["primary"],
                "borderWidth": 2,
                "borderRadius": 4,
            }
        ]

        return cls._build_chart_html(
            chart_id=chart_id,
            chart_type="bar",
            labels=labels,
            datasets=datasets,
            title="Visit Frequency",
            y_axis_label="Number of Visits",
        )

    @classmethod
    def build_problem_distribution_chart(cls, problems: list[dict]) -> str:
        """Build a doughnut chart showing problem categories.

        Args:
            problems: List of problem records

        Returns:
            HTML with problem distribution chart
        """
        if not problems:
            return ""

        # Categorize problems (simplified categorization)
        categories = {
            "Cardiovascular": 0,
            "Endocrine": 0,
            "Respiratory": 0,
            "Musculoskeletal": 0,
            "Mental Health": 0,
            "Other": 0,
        }

        cardio_terms = ["heart", "hypertension", "cardio", "blood pressure", "cholesterol"]
        endo_terms = ["diabetes", "thyroid", "obesity", "metabolic"]
        resp_terms = ["asthma", "copd", "respiratory", "lung", "breathing"]
        msk_terms = ["arthritis", "pain", "back", "joint", "osteo"]
        mh_terms = ["anxiety", "depression", "mental", "psychiatric", "bipolar"]

        for p in problems:
            name = (p.get("name") or "").lower()
            if any(t in name for t in cardio_terms):
                categories["Cardiovascular"] += 1
            elif any(t in name for t in endo_terms):
                categories["Endocrine"] += 1
            elif any(t in name for t in resp_terms):
                categories["Respiratory"] += 1
            elif any(t in name for t in msk_terms):
                categories["Musculoskeletal"] += 1
            elif any(t in name for t in mh_terms):
                categories["Mental Health"] += 1
            else:
                categories["Other"] += 1

        # Filter out zero categories
        labels = [k for k, v in categories.items() if v > 0]
        data = [v for v in categories.values() if v > 0]

        if not data:
            return ""

        chart_id = f"problems_chart_{hash(str(problems)) % 10000}"

        colors = [
            cls.CHART_COLORS["danger"],
            cls.CHART_COLORS["warning"],
            cls.CHART_COLORS["primary"],
            cls.CHART_COLORS["purple"],
            cls.CHART_COLORS["success"],
            cls.CHART_COLORS["gray"],
        ]

        datasets = [
            {
                "data": data,
                "backgroundColor": colors[: len(data)],
                "borderWidth": 2,
                "borderColor": "#ffffff",
            }
        ]

        return cls._build_chart_html(
            chart_id=chart_id,
            chart_type="doughnut",
            labels=labels,
            datasets=datasets,
            title="Problem Categories",
            options_override={
                "plugins": {
                    "legend": {"position": "right"},
                },
            },
        )

    @classmethod
    def _build_chart_html(
        cls,
        chart_id: str,
        chart_type: str,
        labels: list,
        datasets: list[dict],
        title: str = "",
        y_axis_label: str = "",
        x_axis_label: str = "",
        annotations: dict | None = None,
        options_override: dict | None = None,
    ) -> str:
        """Build complete HTML for a Chart.js chart.

        Args:
            chart_id: Unique ID for the canvas element
            chart_type: Chart.js chart type (line, bar, doughnut, etc.)
            labels: X-axis labels
            datasets: Chart.js dataset configurations
            title: Chart title
            y_axis_label: Y-axis label
            x_axis_label: X-axis label
            annotations: Chart.js annotation plugin config
            options_override: Override default options

        Returns:
            Complete HTML string with Chart.js
        """
        # Build options
        options: dict[str, Any] = {
            "responsive": True,
            "maintainAspectRatio": False,
            "plugins": {
                "title": {
                    "display": bool(title),
                    "text": title,
                    "font": {"size": 14, "weight": "bold"},
                },
                "legend": {
                    "display": len(datasets) > 1,
                },
            },
            "scales": {},
        }

        # Add axis labels for line/bar charts
        if chart_type in ("line", "bar"):
            options["scales"]["y"] = {
                "beginAtZero": False,
                "title": {
                    "display": bool(y_axis_label),
                    "text": y_axis_label,
                },
            }
            options["scales"]["x"] = {
                "title": {
                    "display": bool(x_axis_label),
                    "text": x_axis_label,
                },
            }

        # Add annotations if provided
        if annotations:
            options["plugins"]["annotation"] = {"annotations": annotations}

        # Apply overrides
        if options_override:
            cls._deep_merge(options, options_override)

        config = {
            "type": chart_type,
            "data": {
                "labels": labels,
                "datasets": datasets,
            },
            "options": options,
        }

        config_json = json.dumps(config)

        return f"""
        <div style="height: 300px; position: relative;">
            <canvas id="{chart_id}"></canvas>
        </div>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-annotation"></script>
        <script>
            (function() {{
                const ctx = document.getElementById('{chart_id}');
                if (ctx) {{
                    new Chart(ctx, {config_json});
                }}
            }})();
        </script>
        """

    @staticmethod
    def _deep_merge(base: dict, override: dict) -> dict:
        """Deep merge override into base dict."""
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                ClinicalChartBuilder._deep_merge(base[key], value)
            else:
                base[key] = value
        return base
