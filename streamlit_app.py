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

# Normalize `day` column to timezone-naive datetimes for Arrow compatibility
if "day" in df.columns:
    df["day"] = pd.to_datetime(df["day"], errors="coerce")
    # Remove timezone info if present
    try:
        if df["day"].dt.tz is not None:
            df["day"] = df["day"].dt.tz_convert(None)
    except Exception:
        pass
    try:
        df["day"] = df["day"].dt.tz_localize(None)
    except Exception:
        # If localization fails, ignore — the column is likely already tz-naive
        pass

st.subheader("Data preview")
# Create a display-safe copy for Streamlit to avoid Arrow serialization issues
df_display = df.head(n_rows).copy()
if "day" in df_display.columns:
    # Convert to string for safe display (preserves readability)
    try:
        df_display["day"] = df_display["day"].astype(str)
    except Exception:
        df_display["day"] = df_display["day"].apply(lambda x: str(x))
st.dataframe(df_display)

with st.expander("Diagnostics (data types and sample)"):
    st.write(df.dtypes)
    if "day" in df.columns:
        # show any rows where parsing previously failed (NaT)
        try:
            bad = df.loc[df["day"].isna()]
            if not bad.empty:
                st.warning("Some 'day' values could not be parsed.")
                st.info("Showing affected rows:")
                st.dataframe(bad.head(10))
            else:
                st.write("All 'day' values parsed successfully or are present.")
        except Exception:
            st.write("Could not evaluate 'day' diagnostics.")

with st.expander("Summary statistics"):
    st.write(df.describe(include="all"))

if show_chart:
    st.subheader("Time series")
    if "day" in df.columns:
        df_chart = df.set_index("day")[df.columns.drop("day")]
    else:
        df_chart = df
    # Convert index to string to avoid Arrow serialization issues
    try:
        df_chart = df_chart.copy()
        df_chart.index = df_chart.index.astype(str)
    except Exception:
        pass
    st.line_chart(df_chart)
