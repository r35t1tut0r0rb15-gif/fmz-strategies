"""Stochastic K / D crossings under the lower band, daily bars, long only: %K(14) crossing over its SMA 3 with the close under the lower band (14, 2) goes long; the close crossing under the basis, or a close
over the upper band, closes.
Port of FMZ strategy #444025 "布林带与随机指标KD交叉策略Bollinger-Bands-and-Stochastic-KD-Crossover-Strategy" (Bollinger Bands and KD Strategy with Take Profit).

FMZ source id: 444025

Source
    https://www.fmz.com/strategy/444025 (PineScript v5, FMZ last modified 2024-03-08 16:49:06).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 150-192), BB 14 / 2; stochastic 14, D 3
    close < lower and crossover(k, d) -> entry Buy;  crossunder(close, basis) or close > upper -> close Buy

Interpretation choices (Pine rules in SURVEY_README.md)
    * Pine's stdev is the population deviation. Long only. No sizing code. FREQ = "1D" from the
      backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, stochastic crossings at the lower band.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_444025_lower_band_stoch_cross_long"
FAMILY = "bollinger_reversion"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [14, 20],
    "kd_length": [14, 9],
}
DEFAULT_PARAMS = {"length": 14, "kd_length": 14, "mult": 2.0, "kd_smooth": 3}


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
    n = int(p["length"])
    basis = c.rolling(n).mean()
    dev = float(p["mult"]) * c.rolling(n).std(ddof=0)
    kn = int(p["kd_length"])
    ll, hh = lo.rolling(kn).min(), h.rolling(kn).max()
    k = 100.0 * (c - ll) / (hh - ll).where(hh > ll)
    d = k.rolling(int(p["kd_smooth"])).mean()
    go = ((c < basis - dev) & (k > d) & (k.shift(1) <= d.shift(1))).to_numpy()
    out = (((c < basis) & (c.shift(1) >= basis.shift(1))) | (c > basis + dev)).to_numpy()
    m = len(c)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    held = False
    for i in range(m):
        if go[i] and not held:
            le[i] = True                     # a same-bar close acts only on a held long
        elif out[i] and held:
            lx[i] = True
        held = (held and not lx[i]) or le[i]
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
