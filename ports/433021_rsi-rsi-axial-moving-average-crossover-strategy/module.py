"""RSI crossing its own average, broker days, long only: the RSI 14 crossing above its SMA 14 goes long, crossing below
closes it.
Port of FMZ strategy #433021 "RSI轴向均线交叉策略RSI-Axial-Moving-Average-Crossover-Strategy" (rsisma).

FMZ source id: 433021

Source
    https://www.fmz.com/strategy/433021 (PineScript v5, FMZ last modified 2023-11-23 16:45:55).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 142-170), RSI 14 (close), MA type SMA, MA length 14
    rsi = 100 - 100 / (1 + rma(up, 14) / rma(down, 14));  rsiMA = sma(rsi, 14)
    crossover(rsi, rsiMA) -> entry long;  crossunder(rsi, rsiMA) -> close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The Bollinger option only changes the plot. Long only; Opposite entries cannot occur. Daily bars
      are broker days (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, an oscillator against its own average.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only. Opposite entries cannot occur.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_433021_rsi_sma_cross"
FAMILY = "rsi_oscillator"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rsi_len": [14, 7],
    "ma_len": [14, 28],
}
DEFAULT_PARAMS = {"rsi_len": 14, "ma_len": 14}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def precompute(raw_1m_df, symbol_key, **params):
    df = raw_1m_df[["open", "high", "low", "close"]].dropna(how="all")
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    lab = broker_day(df.index)
    bars = df.groupby(lab).agg({"open": "first", "high": "max", "low": "min", "close": "last"})
    first = pd.Series(df.index, index=df.index).groupby(lab).first()
    bars.index = pd.DatetimeIndex(first.loc[bars.index].values)   # each bar stamped with its first minute
    if bars.index.tz is None:
        bars.index = bars.index.tz_localize("UTC")
    return bars


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    ch = c.diff()
    n = int(p["rsi_len"])
    up = ch.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    dn = (-ch.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    rsi = (100 - 100 / (1 + up / dn)).where(up != 0, 0.0).where(dn != 0, 100.0).where(up.notna())
    ma = rsi.rolling(int(p["ma_len"])).mean()
    le = ((rsi > ma) & (rsi.shift(1) <= ma.shift(1))).astype(bool)
    lx = ((rsi < ma) & (rsi.shift(1) >= ma.shift(1))).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return le, lx, false, false.copy()


def portfolio_kwargs(**params):
    return {}
