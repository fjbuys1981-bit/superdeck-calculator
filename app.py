import base64
import io
import json
from datetime import datetime

import pandas as pd
import plotly.graph_objects as go
import streamlit as st


# ==========================================================
# PRESTON HIRE NZ
# SUPERDECK LOAD CALCULATOR MVP+
# ==========================================================

st.set_page_config(
    page_title="Preston Hire - SuperDeck Calculator",
    page_icon="PH",
    layout="wide",
)


# ==========================================================
# BRANDING
# ==========================================================

PH_YELLOW = "#F5D800"
PH_BLACK = "#1A1A1A"
PH_RED = "#E8400C"
PH_GREEN = "#27AE60"
PH_ORANGE = "#F39C12"
PH_WHITE = "#FFFFFF"
PH_STEEL = "#EEF1F3"
PH_MUTED = "#6B7280"
PH_LINE = "#D8DEE4"


# ==========================================================
# PLATFORM DATABASE
# ==========================================================

ALL_SPECS = {
    "SuperDeck 2.2": {
        "4 Prop": {
            4500: {"swl": 5000, "RA": 9.2, "RB": 6.2, "RC": -0.4, "defl_wheel": 5, "defl_free": 27},
            4750: {"swl": 4000, "RA": 9.3, "RB": 6.6, "RC": -0.3, "defl_wheel": 6, "defl_free": 27},
            5000: {"swl": 3200, "RA": 9.8, "RB": 7.4, "RC": -0.1, "defl_wheel": 7, "defl_free": 27},
            5250: {"swl": 2500, "RA": 10.7, "RB": 8.4, "RC": -0.1, "defl_wheel": 8, "defl_free": 28},
        },
        "2 Prop": {
            4500: {"swl": 5000, "RA": 5.5, "RB": None, "RC": 2.1, "defl_wheel": 9, "defl_free": 41},
            4750: {"swl": 4000, "RA": 5.0, "RB": None, "RC": 2.1, "defl_wheel": 10, "defl_free": 41},
            5000: {"swl": 3200, "RA": 4.6, "RB": None, "RC": 2.1, "defl_wheel": 11, "defl_free": 40},
            5250: {"swl": 2500, "RA": 4.2, "RB": None, "RC": 2.1, "defl_wheel": 12, "defl_free": 40},
        },
        "Boltdown": {
            4500: {"swl": 5000, "RA": 9.4, "RB": 6.5, "RC": -0.5, "defl_wheel": 8, "defl_free": 38},
            4750: {"swl": 4000, "RA": 9.6, "RB": 6.9, "RC": -0.5, "defl_wheel": 9, "defl_free": 37},
            5000: {"swl": 3200, "RA": 10.1, "RB": 7.7, "RC": -0.1, "defl_wheel": 10, "defl_free": 37},
            5250: {"swl": 2500, "RA": 11.1, "RB": 8.7, "RC": -0.2, "defl_wheel": 11, "defl_free": 37},
        },
    },
    "SuperDeck 3.2": {
        "4 Prop": {
            4500: {"swl": 5000, "RA": 9.9, "RB": 6.6, "RC": -0.4, "defl_wheel": 5, "defl_free": 29},
            4750: {"swl": 4000, "RA": 10.1, "RB": 7.2, "RC": -0.3, "defl_wheel": 6, "defl_free": 29},
            5000: {"swl": 3200, "RA": 10.8, "RB": 8.1, "RC": -0.1, "defl_wheel": 7, "defl_free": 30},
            5250: {"swl": 2500, "RA": 12.0, "RB": 9.5, "RC": -0.1, "defl_wheel": 9, "defl_free": 31},
        },
        "2 Prop": {
            4500: {"swl": 5000, "RA": 5.9, "RB": None, "RC": 2.2, "defl_wheel": 10, "defl_free": 44},
            4750: {"swl": 4000, "RA": 5.4, "RB": None, "RC": 2.2, "defl_wheel": 11, "defl_free": 44},
            5000: {"swl": 3200, "RA": 5.1, "RB": None, "RC": 2.3, "defl_wheel": 13, "defl_free": 45},
            5250: {"swl": 2500, "RA": 4.8, "RB": None, "RC": 2.3, "defl_wheel": 14, "defl_free": 45},
        }
    },
    "SuperDeck 4.2": {
        "4 Prop": {
            4500: {"swl": 5000, "RA": 10.6, "RB": 7.0, "RC": -0.4, "defl_wheel": 6, "defl_free": 32},
            4750: {"swl": 4000, "RA": 10.9, "RB": 7.8, "RC": -0.3, "defl_wheel": 7, "defl_free": 32},
            5000: {"swl": 3200, "RA": 11.8, "RB": 8.9, "RC": -0.1, "defl_wheel": 8, "defl_free": 33},
            5250: {"swl": 2500, "RA": 13.3, "RB": 10.5, "RC": 0.1, "defl_wheel": 10, "defl_free": 35},
        },
        "2 Prop": {
            4500: {"swl": 5000, "RA": 6.3, "RB": None, "RC": 2.4, "defl_wheel": 10, "defl_free": 47},
            4750: {"swl": 4000, "RA": 5.9, "RB": None, "RC": 2.4, "defl_wheel": 12, "defl_free": 48},
            5000: {"swl": 3200, "RA": 5.6, "RB": None, "RC": 2.5, "defl_wheel": 14, "defl_free": 49},
            5250: {"swl": 2500, "RA": 5.3, "RB": None, "RC": 2.6, "defl_wheel": 15, "defl_free": 50},
        }
    },
}


# ==========================================================
# HELPERS
# ==========================================================

def get_status(utilisation):
    if utilisation < 80:
        return "PASS", PH_GREEN
    if utilisation <= 100:
        return "WARNING", PH_ORANGE
    return "OVERLOADED", PH_RED


def format_tonnes(value):
    return "N/A" if value is None else f"{value:.1f} t"


def format_kg(value):
    return "TBC" if value is None else f"{value:.0f} kg"


def format_mm(value):
    return "TBC" if value is None else f"{value} mm"


def format_percent(value):
    return "TBC" if value is None else f"{value:.1f}%"


def build_summary(model, method, outboard, spec, workers, worker_mass, material_load, custom_load):
    worker_weight = workers * worker_mass
    total_load = worker_weight + material_load + custom_load
    if spec["swl"] is None:
        utilisation = None
        status, status_color = "DATA REQUIRED", PH_MUTED
    else:
        utilisation = (total_load / spec["swl"]) * 100
        status, status_color = get_status(utilisation)

    return {
        "model": model,
        "method": method,
        "outboard": outboard,
        "workers": workers,
        "worker_mass": worker_mass,
        "worker_weight": worker_weight,
        "material_load": material_load,
        "custom_load": custom_load,
        "total_load": total_load,
        "swl": spec["swl"],
        "utilisation": utilisation,
        "status": status,
        "status_color": status_color,
    }


def make_platform_figure(model, method, outboard, summary, spec):
    deck_lengths = {"SuperDeck 2.2": 2200, "SuperDeck 3.2": 3200, "SuperDeck 4.2": 4200}
    deck_length = deck_lengths[model]
    total_length = outboard + deck_length
    scale = 100 / total_length
    slab_x = outboard * scale
    deck_end_x = 100
    load_zone_start = slab_x + (deck_end_x - slab_x) * 0.18
    load_zone_end = slab_x + (deck_end_x - slab_x) * 0.82

    fig = go.Figure()

    fig.add_shape(type="rect", x0=0, y0=0, x1=slab_x, y1=18, fillcolor="#CDD3DA", line=dict(color="#A5AFBA", width=1))
    fig.add_shape(type="rect", x0=slab_x, y0=6, x1=deck_end_x, y1=13, fillcolor=PH_YELLOW, line=dict(color=PH_BLACK, width=2))
    fig.add_shape(type="rect", x0=load_zone_start, y0=7.2, x1=load_zone_end, y1=11.8, fillcolor=summary["status_color"], opacity=0.22, line=dict(color=summary["status_color"], width=2))
    fig.add_shape(type="line", x0=slab_x, y0=-1, x1=slab_x, y1=21, line=dict(color=PH_RED, width=3))

    prop_xs = [slab_x + 8, slab_x + 26, slab_x + 52, slab_x + 76]
    if method == "2 Prop":
        prop_xs = [slab_x + 15, slab_x + 67]
    elif method == "Boltdown":
        prop_xs = [slab_x + 8, slab_x + 25, slab_x + 50, slab_x + 74]

    for i, x in enumerate(prop_xs, start=1):
        if x >= deck_end_x:
            continue
        fig.add_shape(type="line", x0=x, y0=6, x1=x, y1=0.5, line=dict(color=PH_BLACK, width=4))
        fig.add_shape(type="circle", x0=x - 1.4, y0=-0.9, x1=x + 1.4, y1=1.9, fillcolor=PH_BLACK, line=dict(color=PH_BLACK))
        fig.add_annotation(x=x, y=-2.4, text=f"P{i}", showarrow=False, font=dict(size=11, color=PH_BLACK))

    if method == "Boltdown":
        bolt_xs = [slab_x + 4, slab_x + 12]
        for x in bolt_xs:
            fig.add_shape(type="circle", x0=x - 1.0, y0=8.4, x1=x + 1.0, y1=10.4, fillcolor=PH_BLACK, line=dict(color=PH_BLACK))

    fig.add_annotation(x=slab_x / 2, y=20, text="Slab / building edge", showarrow=False, font=dict(size=12, color=PH_BLACK))
    fig.add_annotation(x=(slab_x + deck_end_x) / 2, y=16, text=f"{model} | {method}", showarrow=False, font=dict(size=15, color=PH_BLACK))
    fig.add_annotation(x=(load_zone_start + load_zone_end) / 2, y=10, text=f"{summary['total_load']:.0f} kg applied", showarrow=False, font=dict(size=13, color=PH_BLACK))
    fig.add_annotation(x=slab_x + 5, y=3.2, text=f"Outboard {outboard} mm", showarrow=False, xanchor="left", font=dict(size=12, color=PH_BLACK))

    reaction_text = f"RA {format_tonnes(spec['RA'])} | RB {format_tonnes(spec['RB'])} | RC {format_tonnes(spec['RC'])}"
    fig.add_annotation(x=70, y=2.5, text=reaction_text, showarrow=False, font=dict(size=12, color=PH_MUTED))

    fig.update_xaxes(range=[-2, 103], visible=False)
    fig.update_yaxes(range=[-4, 22], visible=False)
    fig.update_layout(height=360, margin=dict(l=8, r=8, t=10, b=8), paper_bgcolor=PH_WHITE, plot_bgcolor=PH_WHITE)
    return fig


def create_project_payload(summary, spec):
    return {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "platform": {
            "model": summary["model"],
            "method": summary["method"],
            "outboard_mm": summary["outboard"],
        },
        "loads": {
            "workers": summary["workers"],
            "worker_mass_kg": summary["worker_mass"],
            "worker_load_kg": summary["worker_weight"],
            "material_load_kg": summary["material_load"],
            "additional_load_kg": summary["custom_load"],
            "total_load_kg": summary["total_load"],
        },
        "result": {
            "swl_kg": summary["swl"],
            "utilisation_percent": None if summary["utilisation"] is None else round(summary["utilisation"], 1),
            "status": summary["status"],
        },
        "engineering_outputs": {
            "RA_t": spec["RA"],
            "RB_t": spec["RB"],
            "RC_t": spec["RC"],
            "deflection_outer_wheel_mm": spec["defl_wheel"],
            "deflection_free_end_mm": spec["defl_free"],
        },
    }


def create_report_html(summary, spec, load_df, engineering_df):
    generated = datetime.now().strftime("%d %b %Y %H:%M")
    status_color = summary["status_color"]
    load_rows = "".join(f"<tr><td>{row.Item}</td><td>{row.Value}</td></tr>" for row in load_df.itertuples())
    engineering_rows = "".join(f"<tr><td>{row.Output}</td><td>{row.Value}</td></tr>" for row in engineering_df.itertuples())
    return f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>SuperDeck Load Report</title>
  <style>
    body {{ font-family: Arial, sans-serif; color: #1A1A1A; margin: 32px; }}
    .brand {{ background: #1A1A1A; color: #F5D800; padding: 20px; }}
    .status {{ background: {status_color}; color: white; padding: 16px; margin: 20px 0; }}
    table {{ width: 100%; border-collapse: collapse; margin: 16px 0 28px; }}
    th, td {{ border-bottom: 1px solid #D8DEE4; padding: 10px; text-align: left; }}
    th {{ background: #EEF1F3; }}
    .small {{ color: #6B7280; font-size: 12px; }}
  </style>
</head>
<body>
  <div class="brand">
    <h1>PRESTON HIRE NZ</h1>
    <h2>SuperDeck Load Calculator Report</h2>
  </div>
  <p class="small">Generated: {generated}</p>
  <h2>{summary["model"]} | {summary["method"]} | {summary["outboard"]} mm outboard</h2>
  <div class="status">
    <h2>Status: {summary["status"]}</h2>
    <h1>{format_percent(summary["utilisation"])} utilisation</h1>
  </div>
  <h3>Load Summary</h3>
  <table><tr><th>Item</th><th>Value</th></tr>{load_rows}</table>
  <h3>Engineering Outputs</h3>
  <table><tr><th>Output</th><th>Value</th></tr>{engineering_rows}</table>
  <p class="small">This MVP report is generated from the current calculator inputs and the embedded reference table. Final temporary works decisions should be reviewed by a suitably qualified engineer.</p>
</body>
</html>"""


def escape_pdf_text(value):
    return str(value).replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def create_pdf_report_bytes(summary, spec, load_df, engineering_df):
    lines = [
        "PRESTON HIRE NZ",
        "SuperDeck Load Calculator Report",
        f"Generated: {datetime.now().strftime('%d %b %Y %H:%M')}",
        "",
        f"Platform: {summary['model']} | {summary['method']} | {summary['outboard']} mm outboard",
        f"Status: {summary['status']}",
        f"Utilisation: {format_percent(summary['utilisation'])}",
        "",
        "Load Summary",
    ]
    lines.extend(f"{row.Item}: {row.Value}" for row in load_df.itertuples())
    lines.extend(["", "Engineering Outputs"])
    lines.extend(f"{row.Output}: {row.Value}" for row in engineering_df.itertuples())
    lines.extend(
        [
            "",
            "Engineering note: This MVP report is generated from the embedded reference table.",
            "Temporary works decisions should be reviewed by a suitably qualified engineer.",
        ]
    )

    content = ["BT", "/F1 18 Tf", "72 770 Td", f"({escape_pdf_text(lines[0])}) Tj"]
    content.extend(["/F1 11 Tf", "0 -24 Td"])
    for line in lines[1:]:
        safe_line = escape_pdf_text(line)
        content.append(f"({safe_line}) Tj")
        content.append("0 -16 Td")
    content.append("ET")
    stream = "\n".join(content).encode("latin-1", errors="replace")

    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        b"<< /Length " + str(len(stream)).encode("ascii") + b" >>\nstream\n" + stream + b"\nendstream",
    ]

    pdf = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for index, obj in enumerate(objects, start=1):
        offsets.append(len(pdf))
        pdf.extend(f"{index} 0 obj\n".encode("ascii"))
        pdf.extend(obj)
        pdf.extend(b"\nendobj\n")

    xref_start = len(pdf)
    pdf.extend(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
    pdf.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        pdf.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
    pdf.extend(
        f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref_start}\n%%EOF\n".encode("ascii")
    )
    return bytes(pdf)


def download_link_bytes(data, label, file_name, mime):
    st.download_button(label=label, data=data, file_name=file_name, mime=mime, use_container_width=True)


# ==========================================================
# STYLE
# ==========================================================

st.markdown(
    f"""
    <style>
    .stApp {{
        background: {PH_STEEL};
    }}
    [data-testid="stSidebar"] {{
        background: {PH_BLACK};
    }}
    [data-testid="stSidebar"] * {{
        color: {PH_WHITE};
    }}
    [data-testid="stSidebar"] input,
    [data-testid="stSidebar"] [data-baseweb="select"] *,
    [data-testid="stSidebar"] [data-baseweb="input"] * {{
        color: {PH_BLACK};
    }}
    [data-testid="stSidebar"] svg {{
        color: {PH_BLACK};
        fill: {PH_BLACK};
    }}
    .ph-hero {{
        background: {PH_BLACK};
        padding: 24px 28px;
        border-radius: 8px;
        border-left: 10px solid {PH_YELLOW};
    }}
    .ph-hero h1 {{
        color: {PH_YELLOW};
        margin: 0;
        font-size: 2rem;
        letter-spacing: 0;
    }}
    .ph-hero h3 {{
        color: white;
        margin: 6px 0 0;
        font-weight: 500;
    }}
    .metric-card {{
        background: white;
        border: 1px solid {PH_LINE};
        border-radius: 8px;
        padding: 16px;
        min-height: 116px;
    }}
    .metric-card .label {{
        color: {PH_MUTED};
        font-size: 0.84rem;
        margin-bottom: 6px;
    }}
    .metric-card .value {{
        color: {PH_BLACK};
        font-size: 1.8rem;
        font-weight: 700;
        line-height: 1.1;
    }}
    .status-banner {{
        padding: 18px 22px;
        border-radius: 8px;
        color: white;
    }}
    .status-banner h2, .status-banner h1 {{
        margin: 0;
    }}
    .status-banner h1 {{
        margin-top: 4px;
    }}
    .section-title {{
        color: {PH_BLACK};
        font-weight: 700;
        margin: 8px 0 2px;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)


# ==========================================================
# HEADER
# ==========================================================

st.markdown(
    """
    <div class="ph-hero">
        <h1>PRESTON HIRE NZ</h1>
        <h3>SuperDeck&reg; Load Calculator</h3>
    </div>
    """,
    unsafe_allow_html=True,
)


# ==========================================================
# SIDEBAR INPUTS
# ==========================================================

st.sidebar.header("Platform Selection")

model = st.sidebar.selectbox("Platform Model", list(ALL_SPECS.keys()))
method = st.sidebar.selectbox("Install Method", list(ALL_SPECS[model].keys()))
outboard = st.sidebar.selectbox("Outboard Distance (mm)", list(ALL_SPECS[model][method].keys()))
spec = ALL_SPECS[model][method][outboard]

st.sidebar.header("Loads")

workers = st.sidebar.number_input("Number of Workers", min_value=0, max_value=20, value=2)
worker_mass = st.sidebar.number_input("Worker Allowance per Person (kg)", min_value=60, max_value=150, value=100, step=5)
material_load = st.sidebar.number_input("Material Load (kg)", min_value=0, max_value=10000, value=1000, step=50)
custom_load = st.sidebar.number_input("Additional Load (kg)", min_value=0, max_value=10000, value=0, step=50)

st.sidebar.markdown("---")
st.sidebar.caption("Status thresholds: PASS < 80%, WARNING 80-100%, OVERLOADED > 100%.")


# ==========================================================
# CALCULATIONS
# ==========================================================

summary = build_summary(model, method, outboard, spec, workers, worker_mass, material_load, custom_load)
remaining_capacity = None if summary["swl"] is None else summary["swl"] - summary["total_load"]
required_reduction = 0 if remaining_capacity is None else abs(min(remaining_capacity, 0))

load_df = pd.DataFrame(
    {
        "Item": ["Workers", "Worker Allowance", "Material Load", "Additional Load", "Total Applied Load", "SWL"],
        "Value": [
            f"{summary['worker_weight']:.0f} kg",
            f"{worker_mass:.0f} kg/person",
            f"{material_load:.0f} kg",
            f"{custom_load:.0f} kg",
            f"{summary['total_load']:.0f} kg",
            format_kg(summary["swl"]),
        ],
    }
)

engineering_df = pd.DataFrame(
    {
        "Output": ["RA Reaction", "RB Reaction", "RC Reaction", "Deflection Outer Wheel", "Deflection Free End"],
        "Value": [
            format_tonnes(spec["RA"]),
            format_tonnes(spec["RB"]),
            format_tonnes(spec["RC"]),
            format_mm(spec["defl_wheel"]),
            format_mm(spec["defl_free"]),
        ],
    }
)


# ==========================================================
# STATUS + DASHBOARD
# ==========================================================

st.write("")
st.markdown(
    f"""
    <div class="status-banner" style="background:{summary['status_color']};">
        <h2>STATUS: {summary['status']}</h2>
        <h1>{format_percent(summary['utilisation'])} Utilisation</h1>
    </div>
    """,
    unsafe_allow_html=True,
)

m1, m2, m3, m4 = st.columns(4)
with m1:
    st.markdown(f"""<div class="metric-card"><div class="label">Applied Load</div><div class="value">{summary['total_load']:.0f} kg</div></div>""", unsafe_allow_html=True)
with m2:
    st.markdown(f"""<div class="metric-card"><div class="label">Rated SWL</div><div class="value">{format_kg(summary['swl'])}</div></div>""", unsafe_allow_html=True)
with m3:
    if remaining_capacity is None:
        capacity_text = "TBC"
    else:
        capacity_text = f"{remaining_capacity:.0f} kg" if remaining_capacity >= 0 else f"-{required_reduction:.0f} kg"
    st.markdown(f"""<div class="metric-card"><div class="label">Remaining Capacity</div><div class="value">{capacity_text}</div></div>""", unsafe_allow_html=True)
with m4:
    st.markdown(f"""<div class="metric-card"><div class="label">Free End Deflection</div><div class="value">{format_mm(spec['defl_free'])}</div></div>""", unsafe_allow_html=True)

if summary["status"] == "DATA REQUIRED":
    st.info("This platform system is available, but the SWL, reaction, and deflection values still need to be entered before utilisation can be calculated.")
elif summary["status"] == "OVERLOADED":
    st.error(f"Reduce the applied load by at least {required_reduction:.0f} kg or select a higher-capacity configuration.")
elif summary["status"] == "WARNING":
    st.warning("The platform is within SWL but above the 80% planning threshold. Review load assumptions before issue.")
else:
    st.success("The current load is below the planning threshold.")

tab_dashboard, tab_visual, tab_export, tab_notes = st.tabs(["Dashboard", "Diagram", "Export", "Roadmap"])

with tab_dashboard:
    left, right = st.columns(2)
    with left:
        st.markdown('<h3 class="section-title">Load Summary</h3>', unsafe_allow_html=True)
        st.dataframe(load_df, use_container_width=True, hide_index=True)
    with right:
        st.markdown('<h3 class="section-title">Engineering Outputs</h3>', unsafe_allow_html=True)
        st.dataframe(engineering_df, use_container_width=True, hide_index=True)

    st.markdown('<h3 class="section-title">Platform Utilisation</h3>', unsafe_allow_html=True)
    if summary["swl"] is None:
        st.info("Utilisation chart will appear once the SWL value is added for this 2 Prop configuration.")
    else:
        fig = go.Figure()
        fig.add_trace(
            go.Bar(
                x=["Applied Load", "SWL"],
                y=[summary["total_load"], summary["swl"]],
                text=[f"{summary['total_load']:.0f} kg", f"{summary['swl']:.0f} kg"],
                textposition="outside",
                marker_color=[summary["status_color"], PH_YELLOW],
            )
        )
        fig.add_hline(y=summary["swl"] * 0.8, line_dash="dash", line_color=PH_ORANGE, annotation_text="80% planning threshold")
        fig.update_layout(
            plot_bgcolor=PH_BLACK,
            paper_bgcolor=PH_BLACK,
            font=dict(color="white"),
            height=430,
            margin=dict(l=10, r=10, t=24, b=20),
            yaxis_title="Load (kg)",
        )
        st.plotly_chart(fig, use_container_width=True)

with tab_visual:
    st.markdown('<h3 class="section-title">Platform Diagram</h3>', unsafe_allow_html=True)
    st.plotly_chart(make_platform_figure(model, method, outboard, summary, spec), use_container_width=True)

    zones = pd.DataFrame(
        {
            "Zone": ["Slab side", "Deck load zone", "Free end"],
            "Purpose": ["Reference edge and support interface", "Indicative evenly distributed load area", "Outboard end and deflection reference"],
            "Live Value": [f"{outboard} mm outboard", f"{summary['total_load']:.0f} kg total load", f"{format_mm(spec['defl_free'])} deflection"],
        }
    )
    st.dataframe(zones, use_container_width=True, hide_index=True)

with tab_export:
    st.markdown('<h3 class="section-title">Save and Export</h3>', unsafe_allow_html=True)
    payload = create_project_payload(summary, spec)
    report_html = create_report_html(summary, spec, load_df, engineering_df)
    report_pdf = create_pdf_report_bytes(summary, spec, load_df, engineering_df)
    csv_buffer = io.StringIO()
    pd.concat(
        [
            load_df.rename(columns={"Item": "Metric"}),
            engineering_df.rename(columns={"Output": "Metric"}),
        ],
        ignore_index=True,
    ).to_csv(csv_buffer, index=False)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        download_link_bytes(
            json.dumps(payload, indent=2).encode("utf-8"),
            "Download Project JSON",
            "superdeck-project.json",
            "application/json",
        )
    with c2:
        download_link_bytes(csv_buffer.getvalue().encode("utf-8"), "Download Calculation CSV", "superdeck-calculation.csv", "text/csv")
    with c3:
        download_link_bytes(report_html.encode("utf-8"), "Download HTML Report", "superdeck-report.html", "text/html")
    with c4:
        download_link_bytes(report_pdf, "Download PDF Report", "superdeck-report.pdf", "application/pdf")

    encoded_html = base64.b64encode(report_html.encode("utf-8")).decode("ascii")
    st.markdown(
        f'<a href="data:text/html;base64,{encoded_html}" download="superdeck-report.html">Openable report file is ready for browser print-to-PDF.</a>',
        unsafe_allow_html=True,
    )

    with st.expander("Project Data Preview"):
        st.json(payload)

with tab_notes:
    st.markdown('<h3 class="section-title">Temporary Works Checks</h3>', unsafe_allow_html=True)
    st.write(
        "This app validates selected embedded SuperDeck table values against live load inputs. "
        "It does not replace a formal temporary works design review, slab check, or site-specific method statement."
    )
    st.markdown('<h3 class="section-title">Future Development Roadmap</h3>', unsafe_allow_html=True)
    st.write(
        """
        - Native PDF export with branded report template
        - Saved project database and customer records
        - QR code sharing for site teams
        - Hoist, spider crane, slab load, and ground bearing modules
        - Temporary works report bundle
        - Customer portal and AI configuration recommendations
        """
    )


# ==========================================================
# FOOTER
# ==========================================================

st.write("")
st.markdown(
    f"""
    <div style="background:{PH_BLACK};padding:15px;border-radius:8px;">
        <p style="color:{PH_YELLOW};margin:0;">Preston Hire NZ | SuperDeck Engineering Suite MVP</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.sidebar.markdown("---")
st.sidebar.markdown("### Deployment")
st.sidebar.code("streamlit run app.py")
