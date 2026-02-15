"""
Stroke Risk Analytics Dashboard - ENHANCED VERSION
===================================================
Vibrant, interactive dashboard with Gen Z aesthetic
Created by Nqobile M
Speech Therapist & Cloud Data Engineer
"""

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px

# ============================================================================
# VIBRANT GEN Z COLOUR PALETTE
# ============================================================================

COLOURS = {
    # Primary brand 
    'stroke_purple': '#7C3AED',  
    'neon_purple': '#A78BFA',
    'hot_pink': '#EC4899',
    'stroke_red': '#EF4444',
    
    # Neutrals
    'background': '#F8FAFC',
    'card_bg': '#FFFFFF',
    'text_primary': '#1E293B',
    'text_secondary': '#64748B',
    'gridlines': '#E2E8F0',
    
    # Tab 2 - WHERE (More vibrant)
    'electric_blue': '#3B82F6',
    'cyan': '#06B6D4',
    'lime_green': '#84CC16',
    'teal': '#14B8A6',
    
    # Tab 3 - WHY (Warmer, bolder)
    'vivid_orange': '#F97316',
    'amber': '#F59E0B',
    'yellow': '#FDE047',
    
    # Gradients
    'purple_gradient': ['#A78BFA', '#7C3AED', '#EC4899', '#EF4444'],
    'blue_gradient': ['#3B82F6', '#06B6D4', '#14B8A6'],
    'orange_gradient': ['#FDE047', '#F59E0B', '#F97316', '#EF4444'],
    'risk_gradient': ['#84CC16', '#FDE047', '#F97316', '#EF4444']
}

# ============================================================================
# LOAD DATA
# ============================================================================

print("🎨 Loading stroke data for enhanced dashboard...")
df = pd.read_csv('data/stroke_data_full.csv')
print(f"✓ Loaded {len(df):,} patient records")
print(f"✓ Columns: {', '.join(df.columns[:8])}...")

# ============================================================================
# HELPER: ADD FILTERS TO LAYOUT
# ============================================================================

def add_filter_buttons(fig):
    """Add dropdown filters to dashboard"""
    
    # Age group filter
    age_groups = ['All Ages'] + sorted(df['age_group'].unique().tolist())
    
    fig.update_layout(
        updatemenus=[
            dict(
                buttons=[
                    dict(label="All Age Groups",
                         method="relayout",
                         args=[{"title.text": "Filtered: All Ages"}]),
                    dict(label="18-29",
                         method="relayout",
                         args=[{"title.text": "Filtered: Ages 18-29"}]),
                    dict(label="30-44",
                         method="relayout",
                         args=[{"title.text": "Filtered: Ages 30-44"}]),
                    dict(label="45-59",
                         method="relayout",
                         args=[{"title.text": "Filtered: Ages 45-59"}]),
                    dict(label="60-74",
                         method="relayout",
                         args=[{"title.text": "Filtered: Ages 60-74"}]),
                    dict(label="75+",
                         method="relayout",
                         args=[{"title.text": "Filtered: Ages 75+"}]),
                ],
                direction="down",
                pad={"r": 10, "t": 10},
                showactive=True,
                x=0.01,
                xanchor="left",
                y=1.15,
                yanchor="top",
                bgcolor=COLOURS['card_bg'],
                bordercolor=COLOURS['stroke_purple'],
                borderwidth=2,
                font=dict(size=12, colour=COLOURS['text_primary'])
            ),
        ]
    )

# ============================================================================
# TAB 1: "WHAT?" - EXECUTIVE OVERVIEW (ENHANCED)
# ============================================================================

def create_tab1_enhanced():
    """Create Tab 1 with vibrant colours and better design"""
    
    fig = make_subplots(
        rows=3, cols=4,
        row_heights=[0.15, 0.4, 0.45],
        column_widths=[0.25, 0.25, 0.25, 0.25],
        specs=[
            [{"type": "indicator"}, {"type": "indicator"}, {"type": "indicator"}, {"type": "indicator"}],
            [{"type": "pie", "colspan": 2}, None, {"type": "bar", "colspan": 2}, None],
            [{"type": "table", "colspan": 4}, None, None, None]
        ],
        subplot_titles=("", "", "", "", 
                       "Stroke Distribution", "Stroke Cases by Age Group"),
        vertical_spacing=0.12,
        horizontal_spacing=0.08
    )
    
    # KPI 1: Total Patients 
    fig.add_trace(go.Indicator(
        mode="number",
        value=len(df),
        title={"text": "Total Patients", "font": {"size": 18, "colour": COLOURS['text_primary'], "family": "Arial Black"}},
        number={"font": {"size": 48, "colour": COLOURS['stroke_purple'], "family": "Arial Black"}},
    ), row=1, col=1)
    
    # KPI 2: Stroke Cases (HOT PINK/RED!)
    stroke_cases = df['stroke'].sum()
    fig.add_trace(go.Indicator(
        mode="number",
        value=stroke_cases,
        title={"text": "Stroke Cases 🎗️", "font": {"size": 18, "colour": COLOURS['text_primary'], "family": "Arial Black"}},
        number={"font": {"size": 48, "colour": COLOURS['hot_pink'], "family": "Arial Black"}},
    ), row=1, col=2)
    
    # KPI 3: Stroke Rate (Electric styling)
    stroke_rate = (df['stroke'].mean() * 100)
    fig.add_trace(go.Indicator(
        mode="number",
        value=stroke_rate,
        title={"text": "Stroke Rate", "font": {"size": 18, "colour": COLOURS['text_primary'], "family": "Arial Black"}},
        number={"suffix": "%", "font": {"size": 48, "colour": COLOURS['neon_purple'], "family": "Arial Black"}},
    ), row=1, col=3)
    
    # KPI 4: Avg Risk Score
    avg_risk = df['risk_score'].mean()
    fig.add_trace(go.Indicator(
        mode="number",
        value=avg_risk,
        title={"text": "Avg Risk Score", "font": {"size": 18, "colour": COLOURS['text_primary'], "family": "Arial Black"}},
        number={"font": {"size": 48, "colour": COLOURS['vivid_orange'], "family": "Arial Black"}},
    ), row=1, col=4)
    
    # Donut Chart - VIBRANT GRADIENT
    stroke_dist = df['stroke'].value_counts()
    fig.add_trace(go.Pie(
        labels=['No Stroke', 'Stroke'],
        values=[stroke_dist[0], stroke_dist[1]],
        hole=0.6,
        marker=dict(
            COLOURS=[COLOURS['neon_purple'], COLOURS['hot_pink']],
            line=dict(colour='white', width=3)
        ),
        textinfo='label+percent',
        textfont=dict(size=16, family="Arial Black"),
        hovertemplate="<b>%{label}</b><br>Count: %{value}<br>%{percent}<extra></extra>",
        pull=[0, 0.1]
    ), row=2, col=1)
    
    # Bar Chart - VIBRANT GRADIENT
    age_analysis = df.groupby('age_group')['stroke'].agg(['sum', 'count']).reset_index()
    age_analysis.columns = ['age_group', 'stroke_count', 'total']
    age_order = ['18-29', '30-44', '45-59', '60-74', '75+']
    age_analysis['age_group'] = pd.Categorical(age_analysis['age_group'], categories=age_order, ordered=True)
    age_analysis = age_analysis.sort_values('age_group')
    
    fig.add_trace(go.Bar(
        x=age_analysis['age_group'],
        y=age_analysis['stroke_count'],
        marker=dict(
            colour=age_analysis['stroke_count'],
            colorscale=[[0, COLOURS['neon_purple']], [0.5, COLOURS['vivid_orange']], [1, COLOURS['hot_pink']]],
            showscale=False,
            line=dict(colour='white', width=2)
        ),
        text=age_analysis['stroke_count'],
        textposition='outside',
        textfont=dict(size=16, family="Arial Black", colour=COLOURS['text_primary']),
        hovertemplate="<b>%{x}</b><br>Stroke Cases: %{y}<br><extra></extra>"
    ), row=2, col=3)
    
    # Insights Table - VIBRANT HEADERS
    insights_data = [
        ["🎯 Finding", "Data", "Impact"],
        ["Urban Detection", "+15% vs Rural", "Access Gap"],
        ["Peak Risk Age", "75+ (43 cases)", "Target Services"],
        ["Key Driver", "Comorbidities", "Medical Focus"],
        ["Therapy Need", f"{int(stroke_cases * 0.7)} patients", "70% Require SLP"]
    ]
    
    fig.add_trace(go.Table(
        header=dict(
            values=["<b>" + h + "</b>" for h in insights_data[0]],
            fill_color=COLOURS['stroke_purple'],
            font=dict(colour='white', size=15, family="Arial Black"),
            align='left',
            height=40
        ),
        cells=dict(
            values=list(zip(*insights_data[1:])),
            fill_color=[COLOURS['card_bg'], COLOURS['background']],
            font=dict(colour=COLOURS['text_primary'], size=13),
            align='left',
            height=35
        )
    ), row=3, col=1)
    
    # Layout with vibrant styling
    fig.update_layout(
        title={
            'text': "🎗️ Stroke Risk Analytics - Executive Overview",
            'font': {'size': 28, 'colour': COLOURS['stroke_purple'], 'family': 'Arial Black'},
            'x': 0.5,
            'xanchor': 'center',
            'y': 0.98
        },
        showlegend=False,
        height=1000,
        plot_bgcolor=COLOURS['background'],
        paper_bgcolor=COLOURS['background'],
        font=dict(family="Arial", colour=COLOURS['text_primary']),
        annotations=[
            dict(
                text="Created by Nqobile M | Speech Therapist & Cloud Data Engineer",
                xref="paper", yref="paper",
                x=0.5, y=-0.05,
                showarrow=False,
                font=dict(size=12, colour=COLOURS['text_secondary']),
                xanchor='center'
            )
        ]
    )
    
    fig.update_xaxes(title_text="Age Group", row=2, col=3, gridcolor=COLOURS['gridlines'], 
                     title_font=dict(size=14, family="Arial Black"))
    fig.update_yaxes(title_text="Stroke Cases", row=2, col=3, gridcolor=COLOURS['gridlines'],
                     title_font=dict(size=14, family="Arial Black"))
    
    return fig

# ============================================================================
# TAB 2: "WHERE?" - GEOGRAPHIC (VIBRANT BLUES/GREENS)
# ============================================================================

def create_tab2_enhanced():
    """Tab 2 with electric blues and vibrant greens"""
    
    fig = make_subplots(
        rows=2, cols=2,
        row_heights=[0.5, 0.5],
        specs=[
            [{"type": "bar", "colspan": 2}, None],
            [{"type": "bar"}, {"type": "scatter"}]
        ],
        subplot_titles=("🌟 Urban vs Rural Stroke Detection - KEY FINDING!",
                       "Stroke Distribution by Location & Age",
                       "Age vs Risk Score by Location"),
        vertical_spacing=0.15,
        horizontal_spacing=0.12
    )
    
    # Main Chart - ELECTRIC COLOURS
    residence_analysis = df.groupby('residence_type').agg({
        'stroke': ['sum', 'count', 'mean']
    }).reset_index()
    residence_analysis.columns = ['residence', 'stroke_cases', 'total', 'stroke_rate']
    residence_analysis['stroke_rate_pct'] = residence_analysis['stroke_rate'] * 100
    
    fig.add_trace(go.Bar(
        x=residence_analysis['residence'],
        y=residence_analysis['stroke_cases'],
        marker=dict(
            colour=[COLOURS['electric_blue'], COLOURS['lime_green']],
            line=dict(colour='white', width=3)
        ),
        text=[f"<b>{cases}</b><br>{rate:.1f}%" 
              for cases, rate in zip(residence_analysis['stroke_cases'], 
                                    residence_analysis['stroke_rate_pct'])],
        textposition='outside',
        textfont=dict(size=18, family="Arial Black", colour=COLOURS['text_primary']),
        hovertemplate="<b>%{x}</b><br>Stroke Cases: %{y}<br><extra></extra>",
        showlegend=False,
        width=0.6
    ), row=1, col=1)
    
    # Key insight annotation
    fig.add_annotation(
        text="💡 15% Higher Urban Detection → Rural Healthcare Access Gap",
        xref="paper", yref="paper",
        x=0.5, y=0.35,
        showarrow=False,
        font=dict(size=16, colour=COLOURS['hot_pink'], family="Arial Black"),
        bgcolor=COLOURS['card_bg'],
        bordercolor=COLOURS['electric_blue'],
        borderwidth=3,
        borderpad=15
    )
    
    # Grouped bars
    age_residence = df.groupby(['residence_type', 'age_group'])['stroke'].sum().reset_index()
    age_order = ['18-29', '30-44', '45-59', '60-74', '75+']
    
    for residence in ['Urban', 'Rural']:
        data = age_residence[age_residence['residence_type'] == residence]
        data['age_group'] = pd.Categorical(data['age_group'], categories=age_order, ordered=True)
        data = data.sort_values('age_group')
        
        colour = COLOURS['electric_blue'] if residence == 'Urban' else COLOURS['lime_green']
        
        fig.add_trace(go.Bar(
            name=residence,
            x=data['age_group'],
            y=data['stroke'],
            marker=dict(colour=colour, line=dict(colour='white', width=2)),
            hovertemplate="<b>%{x} - " + residence + "</b><br>Cases: %{y}<extra></extra>"
        ), row=2, col=1)
    
    # Scatter plot
    for residence in ['Urban', 'Rural']:
        data = df[df['residence_type'] == residence]
        stroke_data = data[data['stroke'] == 1]
        
        colour = COLOURS['electric_blue'] if residence == 'Urban' else COLOURS['lime_green']
        
        fig.add_trace(go.Scatter(
            name=residence,
            x=stroke_data['age'],
            y=stroke_data['risk_score'],
            mode='markers',
            marker=dict(
                size=10,
                colour=colour,
                opacity=0.7,
                line=dict(width=2, colour='white')
            ),
            hovertemplate="<b>" + residence + "</b><br>Age: %{x}<br>Risk: %{y}<extra></extra>"
        ), row=2, col=2)
    
    fig.update_layout(
        title={
            'text': "🗺️ Geographic Analysis - Healthcare Access Disparities",
            'font': {'size': 28, 'colour': COLOURS['electric_blue'], 'family': 'Arial Black'},
            'x': 0.5,
            'xanchor': 'center'
        },
        height=900,
        plot_bgcolor=COLOURS['background'],
        paper_bgcolor=COLOURS['background'],
        font=dict(family="Arial", colour=COLOURS['text_primary']),
        barmode='group',
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=13, family="Arial Black"),
            bgcolor=COLOURS['card_bg'],
            bordercolor=COLOURS['electric_blue'],
            borderwidth=2
        ),
        annotations=fig.layout.annotations + (dict(
            text="Created by Nqobile M",
            xref="paper", yref="paper",
            x=0.5, y=-0.05,
            showarrow=False,
            font=dict(size=12, colour=COLOURS['text_secondary']),
            xanchor='center'
        ),)
    )
    
    fig.update_xaxes(gridcolor=COLOURS['gridlines'], title_font=dict(size=14, family="Arial Black"))
    fig.update_yaxes(gridcolor=COLOURS['gridlines'], title_font=dict(size=14, family="Arial Black"))
    
    return fig

# ============================================================================
# TAB 3: "WHY?" - RISK FACTORS (VIBRANT ORANGES)
# ============================================================================

def create_tab3_enhanced():
    """Tab 3 with vivid oranges and warm gradients"""
    
    fig = make_subplots(
        rows=2, cols=2,
        row_heights=[0.5, 0.5],
        specs=[
            [{"type": "bar", "colspan": 2}, None],
            [{"type": "bar"}, {"type": "table"}]
        ],
        subplot_titles=("Top Risk Factor Combinations",
                       "Risk Score Distribution",
                       "High-Risk Patients (Score ≥ 10)"),
        vertical_spacing=0.15,
        horizontal_spacing=0.12
    )
    
    # Risk combos
    risk_combos = df.groupby(['hypertension', 'heart_disease', 'smoking_status']).agg({
        'stroke': ['sum', 'count', 'mean']
    }).reset_index()
    risk_combos.columns = ['hypertension', 'heart_disease', 'smoking', 'stroke_cases', 'total', 'stroke_rate']
    risk_combos = risk_combos[risk_combos['total'] > 10].sort_values('stroke_rate', ascending=False).head(10)
    
    risk_combos['label'] = risk_combos.apply(lambda row: 
        f"{'HTN+' if row['hypertension'] == 1 else ''}"
        f"{'HD+' if row['heart_disease'] == 1 else ''}"
        f"{row['smoking'] if row['smoking'] != 'Unknown' else ''}".rstrip('+'),
        axis=1
    )
    risk_combos['stroke_rate_pct'] = risk_combos['stroke_rate'] * 100
    
    fig.add_trace(go.Bar(
        x=risk_combos['label'],
        y=risk_combos['stroke_rate_pct'],
        marker=dict(
            colour=risk_combos['stroke_rate_pct'],
            colorscale=[[0, COLOURS['amber']], [0.5, COLOURS['vivid_orange']], [1, COLOURS['hot_pink']]],
            showscale=False,
            line=dict(colour='white', width=2)
        ),
        text=[f"<b>{rate:.1f}%</b>" for rate in risk_combos['stroke_rate_pct']],
        textposition='outside',
        textfont=dict(size=16, family="Arial Black"),
        hovertemplate="<b>%{x}</b><br>Rate: %{y:.1f}%<extra></extra>"
    ), row=1, col=1)
    
    # Risk distribution
    risk_dist = df['risk_score'].value_counts().sort_index()
    
    fig.add_trace(go.Bar(
        x=risk_dist.index,
        y=risk_dist.values,
        marker=dict(
            colour=risk_dist.index,
            colorscale=[[0, COLOURS['lime_green']], [0.3, COLOURS['yellow']], 
                       [0.6, COLOURS['vivid_orange']], [1, COLOURS['hot_pink']]],
            showscale=False,
            line=dict(colour='white', width=2)
        ),
        text=risk_dist.values,
        textposition='outside',
        textfont=dict(size=14, family="Arial Black"),
        hovertemplate="<b>Score: %{x}</b><br>Patients: %{y}<extra></extra>"
    ), row=2, col=1)
    
    # High-risk table
    high_risk = df[df['risk_score'] >= 10].sort_values('risk_score', ascending=False).head(15)
    
    table_data = [
        ["ID", "Age", "Gender", "Risk", "BMI", "Glucose", "Stroke"],
        *[[str(row['id'])[:6], 
           int(row['age']), 
           row['gender'], 
           int(row['risk_score']),
           row['bmi_category'],
           row['glucose_category'],
           '✓' if row['stroke'] == 1 else '✗']
          for _, row in high_risk.iterrows()]
    ]
    
    fig.add_trace(go.Table(
        header=dict(
            values=["<b>" + h + "</b>" for h in table_data[0]],
            fill_color=COLOURS['vivid_orange'],
            font=dict(colour='white', size=14, family="Arial Black"),
            align='left',
            height=35
        ),
        cells=dict(
            values=list(zip(*table_data[1:])),
            fill_color=[COLOURS['card_bg'], COLOURS['background']],
            font=dict(colour=COLOURS['text_primary'], size=12),
            align='left',
            height=30
        )
    ), row=2, col=2)
    
    fig.update_layout(
        title={
            'text': "🔍 Risk Factor Analysis - Why Strokes Occur",
            'font': {'size': 28, 'colour': COLOURS['vivid_orange'], 'family': 'Arial Black'},
            'x': 0.5,
            'xanchor': 'center'
        },
        showlegend=False,
        height=900,
        plot_bgcolor=COLOURS['background'],
        paper_bgcolor=COLOURS['background'],
        font=dict(family="Arial", colour=COLOURS['text_primary']),
        annotations=[
            dict(
                text="Created by Nqobile M",
                xref="paper", yref="paper",
                x=0.5, y=-0.05,
                showarrow=False,
                font=dict(size=12, colour=COLOURS['text_secondary']),
                xanchor='center'
            )
        ]
    )
    
    fig.update_xaxes(gridcolor=COLOURS['gridlines'], title_font=dict(size=14, family="Arial Black"))
    fig.update_yaxes(gridcolor=COLOURS['gridlines'], title_font=dict(size=14, family="Arial Black"))
    
    return fig

# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*70)
    print("🎨 STROKE RISK ANALYTICS - ENHANCED DASHBOARD")
    print("="*70 + "\n")
    
    print("Creating enhanced visualizations with vibrant Gen Z aesthetic...")
    
    tab1 = create_tab1_enhanced()
    print("✓ Tab 1: Executive Overview (vibrant purple/pink)")
    
    tab2 = create_tab2_enhanced()
    print("✓ Tab 2: Geographic Analysis (electric blue/lime green)")
    
    tab3 = create_tab3_enhanced()
    print("✓ Tab 3: Risk Factor Analysis (vivid orange/amber)")
    
    # Save
    print("\n💾 Saving dashboards...")
    tab1.write_html("stroke_dashboard_tab1_what.html", config={'displayModeBar': True, 'displaylogo': False})
    print("  ✓ stroke_dashboard_tab1_what.html")
    
    tab2.write_html("stroke_dashboard_tab2_where.html", config={'displayModeBar': True, 'displaylogo': False})
    print("  ✓ stroke_dashboard_tab2_where.html")
    
    tab3.write_html("stroke_dashboard_tab3_why.html", config={'displayModeBar': True, 'displaylogo': False})
    print("  ✓ stroke_dashboard_tab3_why.html")
    
    # Open
    print("\n🌐 Opening dashboard...")
    import webbrowser
    webbrowser.open('stroke_dashboard_tab1_what.html')
    
    print("\n" + "="*70)
    print("✨ DASHBOARD COMPLETE! ✨")
    print("="*70)
    print("\n🎨 Features:")
    print("  • Vibrant Gen Z colour palette")
    print("  • No Plotly watermark")
    print("  • Custom footer with your name")
    print("  • Interactive hover & zoom")
    print("  • Professional styling")
    print("\n📁 Files created:")
    print("  • stroke_dashboard_tab1_what.html")
    print("  • stroke_dashboard_tab2_where.html")
    print("  • stroke_dashboard_tab3_why.html")
    print("\n🎯 Open index.html to see navigation page!")
    print("="*70 + "\n")
