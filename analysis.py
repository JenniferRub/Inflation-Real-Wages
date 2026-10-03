"""How has inflation affected real wage growth in the U.S. over the last 20 years?

Data (FRED, monthly, seasonally adjusted):
  CPIAUCSL      - Consumer Price Index for All Urban Consumers
  CES0500000003 - Average Hourly Earnings of All Employees, Total Private
"""

from io import StringIO
from pathlib import Path
from urllib.request import urlopen

import matplotlib.pyplot as plt
import pandas as pd
from scipy import stats

DATA_DIR = Path("data")
FIG_DIR = Path("figures")
FRED_URL = "https://fred.stlouisfed.org/graph/fredgraph.csv?id={}"
SERIES = {"CPIAUCSL": "cpi", "CES0500000003": "wage"}

BLUE = "#2a78d6"
ORANGE = "#eb6834"
INK = "#0b0b0b"
INK_2 = "#52514e"
GRID = "#e4e3df"


def download(series_id):
    """Download a FRED series and cache the raw CSV in data/."""
    path = DATA_DIR / f"{series_id}.csv"
    if not path.exists():
        with urlopen(FRED_URL.format(series_id)) as resp:
            path.write_text(resp.read().decode())
    df = pd.read_csv(path)
    df.columns = ["date", SERIES[series_id]]
    df["date"] = pd.to_datetime(df["date"])
    df[SERIES[series_id]] = pd.to_numeric(df[SERIES[series_id]], errors="coerce")
    return df.set_index("date")


def build_dataset():
    df = download("CPIAUCSL").join(download("CES0500000003"), how="inner").dropna()

    # Real wage in constant dollars of the latest month's prices
    df["real_wage"] = df["wage"] * df["cpi"].iloc[-1] / df["cpi"]

    # Year-over-year percent changes
    df["inflation"] = df["cpi"].pct_change(12) * 100
    df["nominal_wage_growth"] = df["wage"].pct_change(12) * 100
    df["real_wage_growth"] = df["real_wage"].pct_change(12) * 100

    df = df.dropna()
    # Keep the last 20 years
    df = df[df.index >= df.index[-1] - pd.DateOffset(years=20)]
    return df


def style_axes(ax):
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(GRID)
    ax.tick_params(colors=INK_2, labelsize=9)
    ax.grid(axis="y", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)


def line_chart(df):
    fig, ax = plt.subplots(figsize=(10, 5.2))
    ax.axhline(0, color=INK_2, linewidth=0.8)
    ax.plot(df.index, df["inflation"], color=BLUE, linewidth=2, label="Inflation (CPI)")
    ax.plot(df.index, df["real_wage_growth"], color=ORANGE, linewidth=2,
            label="Real wage growth")

    # Direct labels at the end of each line
    last = df.index[-1]
    for col, color, name in [("inflation", BLUE, "Inflation"),
                             ("real_wage_growth", ORANGE, "Real wage growth")]:
        ax.annotate(f"{name}  {df[col].iloc[-1]:.1f}%", (last, df[col].iloc[-1]),
                    xytext=(6, 0), textcoords="offset points", va="center",
                    fontsize=9, color=INK)

    style_axes(ax)
    ax.set_ylabel("Year-over-year change (%)", color=INK_2, fontsize=10)
    ax.set_title("Inflation vs. real wage growth in the U.S.", loc="left",
                 fontsize=14, color=INK, fontweight="bold", pad=24)
    ax.text(0, 1.02, f"Monthly, {df.index[0]:%b %Y} – {df.index[-1]:%b %Y}. "
            "Source: FRED (CPIAUCSL, CES0500000003)",
            transform=ax.transAxes, fontsize=9, color=INK_2)
    ax.legend(frameon=False, loc="upper left", fontsize=9)
    ax.margins(x=0.01)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "line_inflation_real_wages.png", dpi=200,
                facecolor="white")
    plt.close(fig)


def scatter_plot(df, reg):
    fig, ax = plt.subplots(figsize=(7.5, 6))
    ax.axhline(0, color=INK_2, linewidth=0.8)
    ax.scatter(df["inflation"], df["real_wage_growth"], s=22, color=BLUE,
               alpha=0.7, edgecolor="white", linewidth=0.6, label="Month")

    x = pd.Series([df["inflation"].min(), df["inflation"].max()])
    ax.plot(x, reg.intercept + reg.slope * x, color=ORANGE, linewidth=2,
            label=f"OLS fit: y = {reg.intercept:.2f} {'−' if reg.slope < 0 else '+'} "
                  f"{abs(reg.slope):.2f}x  "
                  f"(R² = {reg.rvalue**2:.2f})")

    style_axes(ax)
    ax.grid(axis="x", color=GRID, linewidth=0.8)
    ax.set_xlabel("Inflation, YoY (%)", color=INK_2, fontsize=10)
    ax.set_ylabel("Real wage growth, YoY (%)", color=INK_2, fontsize=10)
    ax.set_title("Higher inflation, lower real wage growth?", loc="left",
                 fontsize=14, color=INK, fontweight="bold", pad=24)
    ax.text(0, 1.02, "Each dot is one month. Source: FRED",
            transform=ax.transAxes, fontsize=9, color=INK_2)
    ax.legend(frameon=False, loc="upper right", fontsize=9)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "scatter_inflation_real_wages.png", dpi=200,
                facecolor="white")
    plt.close(fig)


def main():
    DATA_DIR.mkdir(exist_ok=True)
    FIG_DIR.mkdir(exist_ok=True)

    df = build_dataset()
    df.to_csv(DATA_DIR / "cleaned_data.csv")

    reg = stats.linregress(df["inflation"], df["real_wage_growth"])

    # Robustness check: exclude 2020-2021, when pandemic job losses among
    # low-wage workers mechanically inflated average hourly earnings.
    no_covid = df[(df.index < "2020-01-01") | (df.index >= "2022-01-01")]
    reg_nc = stats.linregress(no_covid["inflation"], no_covid["real_wage_growth"])

    line_chart(df)
    scatter_plot(df, reg)

    print(f"Sample: {df.index[0]:%Y-%m} to {df.index[-1]:%Y-%m} ({len(df)} months)")
    print(f"Mean inflation:          {df['inflation'].mean():.2f}%")
    print(f"Mean real wage growth:   {df['real_wage_growth'].mean():.2f}%")
    print(f"Correlation:             {reg.rvalue:.3f}")
    print("\nRegression: real_wage_growth = a + b * inflation")
    print(f"  intercept a = {reg.intercept:.3f}")
    print(f"  slope     b = {reg.slope:.3f}  (SE {reg.stderr:.3f}, p = {reg.pvalue:.2g})")
    print(f"  R^2         = {reg.rvalue**2:.3f}")
    print("\nExcluding 2020-2021:")
    print(f"  slope b = {reg_nc.slope:.3f}  (SE {reg_nc.stderr:.3f}, "
          f"p = {reg_nc.pvalue:.2g}), R^2 = {reg_nc.rvalue**2:.3f}, n = {len(no_covid)}")

    years = df.resample("YE").mean()
    print("\nAnnual averages (%):")
    print(years[["inflation", "nominal_wage_growth", "real_wage_growth"]]
          .round(2).set_index(years.index.year).to_string())


if __name__ == "__main__":
    main()
