
"""
Stroke Risk Analytics Dashboard (Reliable Layout)
===============================================
- Single-page HTML with tabs
- No overlapping annotations (insight + acronym rendered as HTML blocks, not Plotly annotations)
- Keeps the same narrative wording used in your dashboard screenshots
"""

from __future__ import annotations

import os
from pathlib import Path
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ---------------------------
# Theme (warm + clinical)
# ---------------------------
COLORS = {
    "base_purple": "#6F2DBD",   # stroke awareness / base
    "stroke_red":  "#D32F2F",   # ribbon + emphasis
    "orange":      "#F57C00",   # what/verb
    "yellow":      "#FBC02D",
    "green":       "#7CB342",
    "blue":        "#1976D2",
    "brown":       "#6D4C41",
    "pink_soft":   "#F8BBD0",   # soft accent only (NOT hot pink)
    "bg":          "#F6F7FB",
    "card":        "#FFFFFF",
    "grid":        "#E6E8F0",
    "text":        "#202124",
    "muted":       "#5F6368",
}

RIBBON_SVG = f"""
<svg width="20" height="20" viewBox="0 0 64 64" aria-hidden="true" style="vertical-align:-3px;">
  <path fill="{COLORS['stroke_red']}" d="M42.8 8c-6.2 0-10.8 4.6-10.8 10.2v5.1c0 3.7-3 6.7-6.7 6.7H18c-5.6 0-10.2 4.6-10.2 10.8S12.4 52 18 52h14.9l10.5 12V52h6.6c5.6 0 10.2-4.6 10.2-10.2S55.6 32 50 32h-6.5c-3.7 0-6.7-3-6.7-6.7v-7.1C36.8 12.6 38.6 8 42.8 8zm-6 43.7L30.6 44H18c-2.2 0-4-1.8-4-4.2S15.8 36 18 36h7.3c5.9 0 10.7-4.8 10.7-10.7v-5.1c0-3 2.2-5.8 6.8-5.8 3 0 4.2 2.9 4.2 3.8v7.1c0 5.9 4.8 10.7 10.7 10.7H50c2.2 0 4 1.8 4 4.1S52.2 44 50 44h-9.2v7.7z"/>
</svg>
"""

# ---------------------------
# Data loading
# ---------------------------
def load_data() -> pd.DataFrame:
    # Explicit path to your processed dataset
    # (You said: data/stroke_data_full.csv)
    primary = Path("data") / "stroke_data_full.csv"
    if primary.exists():
        return pd.read_csv(primary)

    # Fallbacks (in case you rename later)
    candidates = [
        "stroke_data_enhanced.csv",
        "stroke_data_processed.csv",
        "stroke_data.csv",
        "stroke.csv",
        "data/stroke_data_enhanced.csv",
        "data/stroke_data_processed.csv",
        "data/stroke.csv",
    ]
    for c in candidates:
        p = Path(c)
        if p.exists():
            return pd.read_csv(p)

    # Last resort: first CSV in the project folder
    csvs = list(Path(".").glob("*.csv"))
    if not csvs:
        raise FileNotFoundError(
            "No CSV file found. Put your exported CSV in data/stroke_data_full.csv "
            "(or place a CSV in this folder)."
        )
    return pd.read_csv(csvs[0])

def normalise_columns(df: pd.DataFrame) -> pd.DataFrame:
    # Make columns consistent (your dataset uses residence_type etc.)
    rename = {}
    for col in df.columns:
        lc = col.lower()
        if lc == "residence_type":
            rename[col] = "Residence_type"
        if lc == "ever_married":
            rename[col] = "ever_married"
        if lc == "avg_glucose_level":
            rename[col] = "avg_glucose_level"
        if lc == "heart_disease":
            rename[col] = "heart_disease"
        if lc == "hypertension":
            rename[col] = "hypertension"
        if lc == "smoking_status":
            rename[col] = "smoking_status"
        if lc == "risk_score":
            rename[col] = "risk_score"
        if lc == "age_group":
            rename[col] = "age_group"
        if lc == "bmi_category":
            rename[col] = "bmi_category"
        if lc == "glucose_category":
            rename[col] = "glucose_category"
        if lc == "stroke":
            rename[col] = "stroke"
        if lc == "age":
            rename[col] = "age"
        if lc == "gender":
            rename[col] = "gender"
        if lc == "bmi":
            rename[col] = "bmi"
        if lc == "id":
            rename[col] = "id"
        if lc == "work_type":
            rename[col] = "work_type"
    df = df.rename(columns=rename)
    return df

# ---------------------------
# Tab 1 (Overview) - keep simple and stable
# ---------------------------
def build_tab1(df: pd.DataFrame) -> str:
    """Tab 1 with KPIs, donut, age bars, gender, insights table"""
    from plotly.subplots import make_subplots
    
    total = len(df)
    stroke_cases = int((df.get("stroke", pd.Series([0])) == 1).sum())
    avg_age = float(df.get("age", pd.Series([0])).mean())
    avg_risk = float(df.get("risk_score", pd.Series([0])).mean())
    
    fig = make_subplots(
        rows=3, cols=4,
        row_heights=[0.25, 0.4, 0.35],
        specs=[
            [{"type": "indicator"}, {"type": "indicator"}, {"type": "indicator"}, {"type": "indicator"}],
            [{"type": "pie"}, {"type": "bar", "colspan": 2}, None, {"type": "bar"}],
            [{"type": "table", "colspan": 4}, None, None, None]
        ],
        subplot_titles=("", "", "", "", 
                       "Stroke Distribution", "Age Group Distribution", "", "Gender Distribution",
                       "")
    )
    
    # KPIs
    fig.add_trace(go.Indicator(
        mode="number", value=total,
        title={"text": "Total Patients", "font": {"size": 16}},
        number={"font": {"size": 38, "color": COLORS["base_purple"]}},
    ), row=1, col=1)
    
    fig.add_trace(go.Indicator(
        mode="number", value=stroke_cases,
        title={"text": "Stroke Cases", "font": {"size": 16}},
        number={"font": {"size": 38, "color": COLORS["stroke_red"]}},
    ), row=1, col=2)
    
    fig.add_trace(go.Indicator(
        mode="number", value=avg_age,
        title={"text": "Avg Age", "font": {"size": 16}},
        number={"font": {"size": 38, "color": COLORS["blue"]}},
        number_suffix=" yrs"
    ), row=1, col=3)
    
    fig.add_trace(go.Indicator(
        mode="number", value=avg_risk,
        title={"text": "Avg Risk Score", "font": {"size": 16}},
        number={"font": {"size": 38, "color": COLORS["orange"]}},
    ), row=1, col=4)
    
    # Donut
    stroke_dist = df["stroke"].value_counts()
    fig.add_trace(go.Pie(
        labels=["No Stroke", "Stroke"],
        values=[stroke_dist.get(0, 0), stroke_dist.get(1, 0)],
        hole=0.6,
        marker=dict(colors=["#A78BFA", COLORS["stroke_red"]], line=dict(color="white", width=2)),
        textinfo="label+percent",
        pull=[0, 0.1]
    ), row=2, col=1)
    
    # Age groups
    if "age_group" in df.columns:
        age_data = df.groupby("age_group")["stroke"].agg(["count", "sum"]).reset_index()
        age_data.columns = ["age_group", "total", "stroke"]
        age_order = ["18-29", "30-44", "45-59", "60-74", "75+"]
        age_data["age_group"] = pd.Categorical(age_data["age_group"], categories=age_order, ordered=True)
        age_data = age_data.sort_values("age_group")
        
        fig.add_trace(go.Bar(
            name="No Stroke",
            x=age_data["age_group"],
            y=age_data["total"] - age_data["stroke"],
            marker=dict(color="#A78BFA")
        ), row=2, col=2)
        
        fig.add_trace(go.Bar(
            name="Stroke",
            x=age_data["age_group"],
            y=age_data["stroke"],
            marker=dict(color=COLORS["stroke_red"])
        ), row=2, col=2)
    
    # Gender
    if "gender" in df.columns:
        gender_stroke = df[df["stroke"] == 1].groupby("gender").size()
        fig.add_trace(go.Bar(
            x=gender_stroke.index,
            y=gender_stroke.values,
            marker=dict(color=[COLORS["blue"], COLORS["orange"]]),
            text=gender_stroke.values,
            textposition="outside"
        ), row=2, col=4)
    
    # Insights table
    insights_data = [
        ["Finding", "Data", "Impact"],
        ["Urban vs Rural", "5.2% vs 4.5%", "Access Gap"],
        ["Peak Risk Age", "75+ group", "Target Services"],
        ["Avg Risk Score", f"{avg_risk:.1f} / 20", "Moderate Risk"],
        ["Therapy Need", f"{int(stroke_cases * 0.7)} patients", "70% SLP"]
    ]
    
    fig.add_trace(go.Table(
        header=dict(
            values=["<b>" + h + "</b>" for h in insights_data[0]],
            fill_color=COLORS["base_purple"],
            font=dict(color="white", size=13),
            align="left"
        ),
        cells=dict(
            values=list(zip(*insights_data[1:])),
            fill_color=[COLORS["card"], COLORS["bg"]],
            font=dict(size=11),
            align="left"
        )
    ), row=3, col=1)
    
    fig.update_layout(
        height=950,
        showlegend=True,
        paper_bgcolor=COLORS["bg"],
        plot_bgcolor=COLORS["card"],
        font=dict(color=COLORS["text"]),
        barmode="stack",
        margin=dict(l=40, r=40, t=60, b=40)
    )
    
    chart_html = fig.to_html(full_html=False, include_plotlyjs="cdn", config={"displayModeBar": True, "displaylogo": False})
    
    html_out = f"""
    <div class="tab-inner">
      <h2 class="tab-title" style="color:{COLORS['base_purple']}">WHAT? (Overview)</h2>
      <div class="card">
        {chart_html}
      </div>
      <div style="text-align: center; margin-top: 20px; color: #5F6368; font-size: 11px;">
        Created by Nqobile M | Speech Therapist & Cloud Data Engineer
      </div>
    </div>
    """
    return html_out

# ---------------------------
# Tab 2 (Where) - NO OVERLAP
    if "age" in df.columns:
        ages = df["age"].dropna().astype(float)
    else:
        ages = pd.Series([], dtype=float)

    fig = go.Figure()
    fig.add_trace(go.Histogram(x=ages, nbinsx=20, name="Age"))
    fig.update_layout(
        title="Age Distribution",
        paper_bgcolor=COLORS["bg"],
        plot_bgcolor=COLORS["card"],
        margin=dict(l=20, r=20, t=60, b=20),
        height=420,
        font=dict(color=COLORS["text"]),
        xaxis=dict(gridcolor=COLORS["grid"]),
        yaxis=dict(gridcolor=COLORS["grid"]),
    )
    chart_html = fig.to_html(full_html=False, include_plotlyjs='inline')

    return f"""
    <div class="tab-inner">
      <h2 class="tab-title" style="color:{COLORS['base_purple']}">WHAT? (Overview)</h2>
      {kpi}
      <div class="card">
        {chart_html}
      </div>
    </div>
    """

# ---------------------------
# Tab 2 (Where) - NO OVERLAP
# Insight is HTML block (not annotation)
# Speech therapy is a card placed right under the bottom charts
# ---------------------------
def build_tab2(df: pd.DataFrame) -> str:
    if "Residence_type" not in df.columns and "residence_type" in df.columns:
        df = df.rename(columns={"residence_type": "Residence_type"})

    # Rates
    if "stroke" in df.columns and "Residence_type" in df.columns:
        rate = df.groupby("Residence_type")["stroke"].mean() * 100
        urban_rate = float(rate.get("Urban", np.nan))
        rural_rate = float(rate.get("Rural", np.nan))
    else:
        urban_rate = rural_rate = float("nan")

    # Build charts in a subplot with generous spacing
    fig = make_subplots(
        rows=2, cols=2,
        row_heights=[0.56, 0.44],
        specs=[[{"type": "bar", "colspan": 2}, None],
               [{"type": "bar"}, {"type": "scatter"}]],
        subplot_titles=(
            "🌟 Urban vs Rural Stroke Detection - KEY FINDING!",
            "Stroke Distribution by Location & Age",
            "Age vs Risk Score by Location"
        ),
        vertical_spacing=0.18,
        horizontal_spacing=0.12
    )

    # Top chart: Urban vs Rural counts and % (stable)
    if "Residence_type" in df.columns and "stroke" in df.columns:
        counts = df[df["stroke"] == 1].groupby("Residence_type").size()
        # Fallback counts for overall if stroke==1 not desired; keep as you showed.
        rural_c = int(counts.get("Rural", 0))
        urban_c = int(counts.get("Urban", 0))
    else:
        rural_c = urban_c = 0

    fig.add_trace(go.Bar(
        x=["Rural", "Urban"],
        y=[rural_c, urban_c],
        marker_color=[COLORS["green"], COLORS["blue"]],
        text=[f"{rural_c}<br>{rural_rate:.1f}%" if not np.isnan(rural_rate) else f"{rural_c}",
              f"{urban_c}<br>{urban_rate:.1f}%" if not np.isnan(urban_rate) else f"{urban_c}"],
        textposition="outside",
        name="Stroke cases"
    ), row=1, col=1)

    # Bottom left: strokes by age_group and residence
    if "age_group" in df.columns and "Residence_type" in df.columns and "stroke" in df.columns:
        sub = df[df["stroke"] == 1].groupby(["age_group", "Residence_type"]).size().unstack(fill_value=0)
        age_order = ["18-29", "30-44", "45-59", "60-74", "75+"]
        sub = sub.reindex(age_order).fillna(0)
        for res, col in [("Rural", COLORS["green"]), ("Urban", COLORS["blue"])]:
            if res in sub.columns:
                fig.add_trace(go.Bar(x=sub.index, y=sub[res], name=res, marker_color=col), row=2, col=1)
    fig.update_xaxes(title_text="", row=2, col=1)

    # Bottom right: age vs risk scatter coloured by residence
    if "age" in df.columns and "risk_score" in df.columns and "Residence_type" in df.columns:
        for res, col in [("Rural", COLORS["green"]), ("Urban", COLORS["blue"])]:
            d = df[df["Residence_type"] == res]
            fig.add_trace(go.Scatter(
                x=d["age"], y=d["risk_score"], mode="markers",
                marker=dict(
                    size=8,
                    color=col,
                    opacity=0.4,
                    symbol='circle'
                ),
                name=res,
                hovertemplate="<b>" + res + "</b><br>Age: %{x}<br>Risk: %{y}<extra></extra>"
            ), row=2, col=2)

    fig.update_layout(
        paper_bgcolor=COLORS["bg"],
        plot_bgcolor=COLORS["card"],
        height=820,
        margin=dict(l=20, r=20, t=90, b=20),
        font=dict(color=COLORS["text"]),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=1.0, xanchor="right"),
    )
    fig.update_xaxes(gridcolor=COLORS["grid"])
    fig.update_yaxes(gridcolor=COLORS["grid"])

    chart_html = fig.to_html(full_html=False, include_plotlyjs='cdn', config={'displayModeBar': True, 'displaylogo': False})

    # Insight text as HTML (never overlaps charts)
    if not np.isnan(urban_rate) and not np.isnan(rural_rate) and rural_rate > 0:
        rel_inc = (urban_rate - rural_rate) / rural_rate * 100
        insight = f"💡 <b>Stroke detection rate:</b> Urban {urban_rate:.1f}% vs Rural {rural_rate:.1f}% (relative increase: {rel_inc:.0f}%) → Access disparity"
    else:
        insight = "💡 <b>Stroke detection rate:</b> Urban vs Rural → Access disparity"

    insight_box = f"""
    <div class="insight-strip">
      {insight}
    </div>
    """

    # Speech therapy card (kept wording, computed numbers)
    stroke_cases_total = int((df.get("stroke") == 1).sum()) if "stroke" in df.columns else 0
    # Keep your 70% assumption for service demand
    slp_patients = int(round(stroke_cases_total * 0.70))
    sessions = int(round(slp_patients * 12))

    speech_card = f"""
    <div class="card speech-card">
      <div class="card-title">🗣️ <span>Speech Therapy Resource Planning</span></div>

      <div class="card-section">
        <div class="card-subtitle">Estimated SLP Service Demand:</div>
        <ul>
          <li><b>{slp_patients}</b> patients require speech therapy (70% of {stroke_cases_total} stroke cases)</li>
        </ul>
      </div>

      <div class="card-section">
        <div class="card-subtitle">Session Requirements:</div>
        <ul>
          <li>Approximately <b>{sessions:,}</b> therapy sessions needed (12 sessions per patient average)</li>
        </ul>
      </div>
    </div>
    """

    return f"""
    <div class="tab-inner">
      <h2 class="tab-title" style="color:{COLORS['blue']}">WHERE? (Geography)</h2>
      {insight_box}
      <div class="card">{chart_html}</div>
      {speech_card}
      <div style="text-align: center; margin-top: 20px; color: #5F6368; font-size: 11px;">
        Created by Nqobile M | Speech Therapist & Cloud Data Engineer
      </div>
    </div>
    """

# ---------------------------
# Tab 3 (Why) - acronym index ALWAYS visible
# Put acronym as HTML banner above plots
# ---------------------------
def build_tab3(df: pd.DataFrame) -> str:
    acronym_banner = """
    <div class="acronym-banner">
      <b>📖 ABBREVIATIONS:</b> HTN = Hypertension &nbsp;&nbsp;•&nbsp;&nbsp; HD = Heart Disease
    </div>
    """

    # Build subplot with risk combinations at top
    from plotly.subplots import make_subplots
    
    fig = make_subplots(
        rows=2, cols=2,
        row_heights=[0.5, 0.5],
        specs=[
            [{"type": "bar", "colspan": 2}, None],
            [{"type": "bar"}, {"type": "table"}]
        ],
        subplot_titles=("Top Risk Factor Combinations (Higher % = More Dangerous)",
                       "Risk Score Distribution (0-20 scale)",
                       "High-Risk Patients (Score ≥ 10)"),
        vertical_spacing=0.20
    )
    
    # Risk combinations
    if all(col in df.columns for col in ["hypertension", "heart_disease", "smoking_status", "stroke"]):
        risk_combos = df.groupby(["hypertension", "heart_disease", "smoking_status"]).agg({
            "stroke": ["sum", "count", "mean"]
        }).reset_index()
        risk_combos.columns = ["hypertension", "heart_disease", "smoking", "stroke_cases", "total", "stroke_rate"]
        risk_combos = risk_combos[risk_combos["total"] > 10].sort_values("stroke_rate", ascending=False).head(10)
        
        risk_combos["label"] = risk_combos.apply(lambda row: 
            f"{'HTN+' if row['hypertension'] == 1 else ''}"
            f"{'HD+' if row['heart_disease'] == 1 else ''}"
            f"{row['smoking'] if row['smoking'] != 'Unknown' else ''}".rstrip('+'),
            axis=1
        )
        risk_combos["stroke_rate_pct"] = risk_combos["stroke_rate"] * 100
        
        fig.add_trace(go.Bar(
            x=risk_combos["label"],
            y=risk_combos["stroke_rate_pct"],
            marker=dict(
                color=risk_combos["stroke_rate_pct"],
                colorscale=[[0, COLORS["orange"]], [0.5, "#D32F2F"], [1, "#6F2DBD"]],
                showscale=False
            ),
            text=[f"<b>{rate:.1f}%</b>" for rate in risk_combos["stroke_rate_pct"]],
            textposition="outside",
            textfont=dict(size=14)
        ), row=1, col=1)
    
    # Risk distribution
    if "risk_score" in df.columns:
        risk_dist = df["risk_score"].value_counts().sort_index()
        fig.add_trace(go.Bar(
            x=risk_dist.index,
            y=risk_dist.values,
            marker=dict(
                color=risk_dist.index,
                colorscale=[[0, "#84CC16"], [0.5, COLORS["orange"]], [1, COLORS["stroke_red"]]],
                showscale=False
            ),
            text=risk_dist.values,
            textposition="outside"
        ), row=2, col=1)
    
    # High-risk table
    if "risk_score" in df.columns:
        high_risk = df[df["risk_score"] >= 10].sort_values("risk_score", ascending=False).head(15)
        
        table_data = [
            ["ID", "Age", "Gender", "Risk", "BMI", "Stroke"],
        ]
        for _, row in high_risk.iterrows():
            table_data.append([
                str(row.get("id", "")),
                str(int(row.get("age", 0))),
                str(row.get("gender", "")),
                str(int(row.get("risk_score", 0))),
                str(row.get("bmi_category", "")),
                "✓" if row.get("stroke") == 1 else "X"
            ])
        
        fig.add_trace(go.Table(
            header=dict(
                values=["<b>" + h + "</b>" for h in table_data[0]],
                fill_color=COLORS["orange"],
                font=dict(color="white", size=12),
                align="left"
            ),
            cells=dict(
                values=list(zip(*table_data[1:])),
                fill_color=[COLORS["card"], COLORS["bg"]],
                font=dict(size=10),
                align="left"
            )
        ), row=2, col=2)
    
    fig.update_layout(
        showlegend=False,
        height=900,
        paper_bgcolor=COLORS["bg"],
        plot_bgcolor=COLORS["card"],
        font=dict(color=COLORS["text"]),
        margin=dict(l=40, r=40, t=80, b=40)
    )
    
    chart_html = fig.to_html(full_html=False, include_plotlyjs='cdn', config={"displayModeBar": True, "displaylogo": False})

    return f"""
    <div class="tab-inner">
      <h2 class="tab-title" style="color:{COLORS['orange']}">WHY? (Risk Factors)</h2>
      {acronym_banner}
      <div class="card">{chart_html}</div>
      <div style="text-align: center; margin-top: 20px; color: #5F6368; font-size: 11px;">
        Created by Nqobile M | Speech Therapist & Cloud Data Engineer
      </div>
    </div>
    """

# ---------------------------
# HTML shell with tabs + simple filters
# ---------------------------
HTML_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>Stroke Risk Analytics Dashboard</title>
<script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
<style>
  :root {{
    --bg: {bg};
    --card: {card};
    --purple: {purple};
    --red: {red};
    --text: {text};
    --grid: {grid};
    --muted: {muted};
  }}
  body {{
    margin: 0;
    font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif;
    background: var(--bg);
    color: var(--text);
  }}
  header {{
    position: sticky;
    top: 0;
    background: var(--bg);
    z-index: 999;
    border-bottom: 3px solid var(--purple);
  }}
  .topbar {{
    display: flex;
    align-items: center;
    gap: 16px;
    padding: 14px 18px;
  }}
  .brand {{
    display: flex;
    align-items: center;
    gap: 10px;
    font-weight: 900;
    color: var(--purple);
    font-size: 28px;
    letter-spacing: 0.2px;
  }}
  .tabs {{
    display: flex;
    gap: 12px;
    flex-wrap: wrap;
  }}
  .tabbtn {{
    border: 2px solid var(--purple);
    background: white;
    color: var(--purple);
    padding: 10px 16px;
    border-radius: 14px;
    font-weight: 800;
    cursor: pointer;
  }}
  .tabbtn.active {{
    background: var(--purple);
    color: white;
  }}
  main {{
    padding: 18px;
  }}
  .tab {{
    display: none;
  }}
  .tab.active {{
    display: block;
  }}
  .tab-inner {{
    max-width: 1200px;
    margin: 0 auto;
  }}
  .tab-title {{
    margin: 14px 0 12px;
    font-size: 34px;
    font-weight: 900;
  }}
  .card {{
    background: var(--card);
    border-radius: 18px;
    box-shadow: 0 10px 30px rgba(18, 22, 33, 0.06);
    padding: 10px 12px;
    margin: 10px 0 18px;
  }}
  .kpi-grid {{
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 12px;
    margin-bottom: 12px;
  }}
  .kpi-card {{
    background: white;
    border-radius: 16px;
    border: 1px solid rgba(0,0,0,0.06);
    padding: 14px;
  }}
  .kpi-title {{
    color: var(--muted);
    font-weight: 700;
    font-size: 13px;
    text-transform: uppercase;
    letter-spacing: .08em;
  }}
  .kpi-value {{
    font-size: 32px;
    font-weight: 900;
    margin-top: 6px;
    color: var(--text);
  }}
  .insight-strip {{
    background: white;
    border: 3px solid var(--purple);
    border-radius: 16px;
    padding: 14px 16px;
    font-weight: 900;
    color: var(--red);
    margin: 8px 0 12px;
  }}
  .speech-card {{
    border: 3px solid var(--red);
  }}
  .card-title {{
    font-weight: 900;
    font-size: 18px;
    color: var(--purple);
    margin: 6px 4px 10px;
  }}
  .card-subtitle {{
    font-weight: 900;
    color: var(--purple);
    margin-top: 8px;
  }}
  .card-section ul {{
    margin: 8px 0 0 22px;
  }}
  .acronym-banner {{
    background: {orange};
    color: white;
    border: 3px solid var(--red);
    border-radius: 16px;
    padding: 12px 14px;
    font-weight: 900;
    margin-bottom: 12px;
  }}
  footer {{
    text-align: center;
    color: var(--muted);
    padding: 10px 0 18px;
    font-weight: 700;
  }}
  @media (max-width: 900px) {{
    .kpi-grid {{ grid-template-columns: 1fr; }}
  }}
</style>
</head>
<body>
<header>
  <div class="topbar">
    <div class="brand">{ribbon} Stroke Analytics</div>
    <div class="tabs">
      <button class="tabbtn active" data-tab="tab1">📊 WHAT? (Overview)</button>
      <button class="tabbtn" data-tab="tab2">🗺️ WHERE? (Geography)</button>
      <button class="tabbtn" data-tab="tab3">🔎 WHY? (Risk Factors)</button>
    </div>
  </div>
</header>

<main>
  <section id="tab1" class="tab active">{tab1}</section>
  <section id="tab2" class="tab">{tab2}</section>
  <section id="tab3" class="tab">{tab3}</section>
</main>

<!-- Footer now in Tab 1 only -->

<script>
  const btns = document.querySelectorAll(".tabbtn");
  const tabs = document.querySelectorAll(".tab");
  btns.forEach(b => b.addEventListener("click", () => {{
    btns.forEach(x => x.classList.remove("active"));
    tabs.forEach(t => t.classList.remove("active"));
    b.classList.add("active");
    document.getElementById(b.dataset.tab).classList.add("active");
    window.scrollTo({{top: 0, behavior: "smooth"}});
  }}));
</script>
</body>
</html>
"""

def main() -> None:
    print("Loading stroke data...")
    df = load_data()
    df = normalise_columns(df)
    print(f"Loaded {len(df):,} records")
    tab1 = build_tab1(df)
    tab2 = build_tab2(df)
    tab3 = build_tab3(df)

    html = HTML_TEMPLATE.format(
        bg=COLORS["bg"],
        card=COLORS["card"],
        purple=COLORS["base_purple"],
        red=COLORS["stroke_red"],
        text=COLORS["text"],
        grid=COLORS["grid"],
        muted=COLORS["muted"],
        orange=COLORS["orange"],
        ribbon=RIBBON_SVG,
        tab1=tab1,
        tab2=tab2,
        tab3=tab3,
    )

    Path("index.html").write_text(html, encoding="utf-8")
    print("✅ Wrote index.html (single-page tabbed dashboard). Open it in your browser.")

if __name__ == "__main__":
    main()
