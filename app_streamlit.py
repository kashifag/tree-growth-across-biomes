import os
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import statsmodels.formula.api as smf
import statsmodels.api as sm

st.set_page_config(page_title="Tree Growth Across Biomes — Dynamic", layout="wide")

DATA_PATH = "data/trees_biomes.csv"

def simulate_data():
    rng = np.random.default_rng(42)
    biomes = ["Tropical Rainforest", "Temperate Forest", "Boreal Forest", "Savanna", "Mediterranean"]
    n_per_biome = [300, 260, 240, 220, 200]
    biome_intercepts = { "Tropical Rainforest": 5.0, "Temperate Forest": 4.2, "Boreal Forest": 3.8, "Savanna": 4.0, "Mediterranean": 4.4 }
    biome_slopes     = { "Tropical Rainforest": 0.65, "Temperate Forest": 0.60, "Boreal Forest": 0.55, "Savanna": 0.58, "Mediterranean": 0.62 }

    rows, tree_id = [], 1
    for b in biomes:
        biome_intercepts[b] += rng.normal(0, 0.2)
        biome_slopes[b]     += rng.normal(0, 0.05)

    for b, n in zip(biomes, n_per_biome):
        diameter_cm = rng.lognormal(mean=3.2, sigma=0.35, size=n)
        log_d = np.log(diameter_cm)
        height_m = (biome_intercepts[b] + biome_slopes[b]*log_d + rng.normal(0, 0.5, size=n))
        height_m = np.clip(height_m, 2.0, 70.0)
        for i in range(n):
            rows.append({"tree_id": tree_id, "biome": b, "diameter_cm": float(diameter_cm[i]), "height_m": float(height_m[i])})
            tree_id += 1
    df = pd.DataFrame(rows)
    os.makedirs("data", exist_ok=True)
    df.to_csv(DATA_PATH, index=False)

@st.cache_data
def load_data():
    if not os.path.exists(DATA_PATH):
        simulate_data()
    return pd.read_csv(DATA_PATH)

df = load_data()
df["log_diameter"] = np.log(df["diameter_cm"])

st.title("🌳 Tree Growth Across Biomes — Dynamic")
st.write("Toggle between **No pooling**, **Partial pooling (mixed-effects)**, and **Complete pooling** to see shrinkage.")

with st.sidebar:
    pooling = st.radio("Pooling mode:", ["No pooling (per biome OLS)", "Partial pooling (mixed-effects)", "Complete pooling (pooled OLS)"], index=1)
    biomes  = sorted(df["biome"].unique())
    highlight = st.multiselect("Highlight biome(s):", biomes, default=biomes[:2])
    show_points = st.checkbox("Show raw points", value=True)
    alpha = st.slider("Point opacity", 0.1, 1.0, 0.35, 0.05)

fig = px.scatter(df, x="diameter_cm", y="height_m", color="biome", opacity=alpha if show_points else 0.0,
                 hover_data=["biome","diameter_cm","height_m"])
fig.update_traces(marker=dict(size=6))
fig.update_layout(height=650, legend_title_text="Biome")

if pooling == "Complete pooling (pooled OLS)":
    model = smf.ols("height_m ~ np.log(diameter_cm)", data=df).fit()
    xs = np.linspace(df["diameter_cm"].min(), df["diameter_cm"].max(), 200)
    ys = model.params["Intercept"] + model.params["np.log(diameter_cm)"] * np.log(xs)
    fig.add_trace(go.Scatter(x=xs, y=ys, mode="lines", line=dict(width=4), name="Pooled fit (global)"))
    st.caption(f"**Pooled OLS** R² = {model.rsquared:.3f}")

elif pooling == "No pooling (per biome OLS)":
    for b in df["biome"].unique():
        sub = df[df["biome"] == b]
        m = smf.ols("height_m ~ np.log(diameter_cm)", data=sub).fit()
        xs = np.linspace(sub["diameter_cm"].min(), sub["diameter_cm"].max(), 100)
        ys = m.params["Intercept"] + m.params["np.log(diameter_cm)"] * np.log(xs)
        fig.add_trace(go.Scatter(x=xs, y=ys, mode="lines", name=f"{b} fit"))
    st.caption("**No pooling**: separate OLS per biome.")

else:
    md = sm.MixedLM.from_formula("height_m ~ np.log(diameter_cm)", groups="biome",
                                 re_formula="~np.log(diameter_cm)", data=df)
    mdf = md.fit()
    b0 = mdf.fe_params["Intercept"]
    b1 = mdf.fe_params["np.log(diameter_cm)"]
    xs_global = np.linspace(df["diameter_cm"].min(), df["diameter_cm"].max(), 200)
    ys_global = b0 + b1 * np.log(xs_global)
    fig.add_trace(go.Scatter(x=xs_global, y=ys_global, mode="lines", line=dict(width=4),
                             name="Mixed-effects: population mean"))
    for b in df["biome"].unique():
        re = mdf.random_effects[b]
        b0_g = b0 + re.get("Intercept", 0.0)
        b1_g = b1 + re.get("np.log(diameter_cm)", 0.0)
        sub = df[df["biome"] == b]
        xs = np.linspace(sub["diameter_cm"].min(), sub["diameter_cm"].max(), 100)
        ys = b0_g + b1_g * np.log(xs)
        fig.add_trace(go.Scatter(x=xs, y=ys, mode="lines", name=f"{b} (BLUP)"))
    st.caption("**Partial pooling**: MixedLM with random intercepts & slopes per biome.")

if highlight:
    for trace in fig.data:
        if any(h in trace.name for h in highlight):
            trace.update(line=dict(width=5))

fig.update_xaxes(title="Diameter (cm)")
fig.update_yaxes(title="Height (m)")
st.plotly_chart(fig, use_container_width=True)
