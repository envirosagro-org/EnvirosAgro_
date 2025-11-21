import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="EnvirosAgro Demo", page_icon="🎈", layout="wide")
st.title("🎈 EnvirosAgro Demo App")

with st.sidebar:
    st.header("Controls")
    dataset = st.selectbox("Choose dataset", ["Sample crops", "Random"], index=0)
    n_rows = st.slider("Rows to show", 5, 100, 20)
    show_chart = st.checkbox("Show chart", value=True)
    upload = st.file_uploader("Upload CSV", type=["csv"])

st.write("Let's start building! For help and inspiration, head over to [docs.streamlit.io](https://docs.streamlit.io/).")


def get_sample_data(n=20):
    df = pd.DataFrame({
        "day": pd.date_range("2025-01-01", periods=n, freq="D"),
        "soil_moisture": np.random.uniform(10, 40, size=n).round(2),
        "temperature": np.random.uniform(15, 35, size=n).round(1),
        "yield_estimate": np.random.uniform(0.5, 3.0, size=n).round(2),
    })
    return df


if upload is not None:
    df = pd.read_csv(upload)
    st.success("Loaded uploaded CSV")
else:
    if dataset == "Sample crops":
        df = get_sample_data(n_rows)
    else:
        df = pd.DataFrame(np.random.randn(n_rows, 3), columns=["A", "B", "C"])

st.subheader("Data preview")
st.dataframe(df.head(n_rows))

with st.expander("Summary statistics"):
    st.write(df.describe(include='all'))

if show_chart:
    st.subheader("Time series")
    if "day" in df.columns:
        df_chart = df.set_index("day")[df.columns.drop("day")]
    else:
        df_chart = df
    st.line_chart(df_chart)
