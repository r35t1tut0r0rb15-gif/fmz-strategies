"""Vortex crossings with a smoothed SMA filter, broker days: VI+ crossing over VI- (14) with the close above the SMA 5 of the SMA 9 goes long, VI+ crossing under VI- with the close below it short;
reversing.
Port of FMZ strategy #440831 "Spiral Cross Strategy with Moving Average Confirmation" (Vortex + Moving Average Strategy).

FMZ source id: 440831

Source
    https://www.fmz.com/strategy/440831 (PineScript v5, FMZ last modified 2024-02-02 14:50:08).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 143-185), Vortex 14; MA 9 on close, smoothing SMA 5; offset 0
    VIP = sum(|high - low[1]|, 14) / sum(atr(1), 14);  VIM = sum(|low - high[1]|, 14) / sum(atr(1), 14);  crossover(VIP, VIM) and close > sma(sma(close, 9), 5) -> entry Long;  crossunder and close below -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * atr(1) is the true range. strategy.entry reverses: REVERSAL INTENDED. No sizing code. Daily bars
      are broker days (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, Vortex crossings and a smoothed SMA.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_440831_vortex_cross_smoothed_sma_filter"
FAMILY = "directional_movement"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "period": [14, 21],
    "ma_len": [9, 20],
}
DEFAULT_PARAMS = {"period": 14, "ma_len": 9, "smooth": 5}


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
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["period"])
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    s_tr = tr.rolling(n).sum()
    vip = (h - lo.shift(1)).abs().rolling(n).sum() / s_tr
    vim = (lo - h.shift(1)).abs().rolling(n).sum() / s_tr
    sm = c.rolling(int(p["ma_len"])).mean().rolling(int(p["smooth"])).mean()
    up = (vip > vim) & (vip.shift(1) <= vim.shift(1)) & (c > sm)
    dn = (vip < vim) & (vip.shift(1) >= vim.shift(1)) & (c < sm)
    false = pd.Series(False, index=c.index)
    return up, false, dn, false.copy()


def portfolio_kwargs(**params):
    return {}
