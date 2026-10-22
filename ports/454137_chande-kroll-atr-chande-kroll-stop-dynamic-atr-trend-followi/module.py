"""Chande Kroll stop lines (21-bar extremes -+ 3 ATR 10), daily bars, long only: the close crossing over the low stop line while over the SMA 21 buys; a close under the high stop line sells.
Port of FMZ strategy #454137 "Chande-Kroll止损动态ATR趋势跟踪策略-Chande-Kroll-Stop-Dynamic-ATR-Trend-Following-Strategy" (Chande Kroll Stop Strategy).

FMZ source id: 454137

Source
    https://www.fmz.com/strategy/454137 (PineScript v5, FMZ last modified 2024-06-14 15:15:43).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 90-142), stop length 21; ATR 10 x 3; SMA 21; quantity riskMultiplier 5 / lowest(close, 1560) x 1000 x equity / capital; commission 0.01 %, slippage 3
    crossover(close, lowest(low, 21) + 3 atr) and close > sma21 -> entry Long (qty by the risk formula);  close < highest(high, 21) - 3 atr -> close Long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The exit is a state; on the signal bar it can hold too, and the close then finds no trade yet
      (followed in a loop), while a held long meeting both is closed. The quantity formula is sizing
      (stored). Long only. FREQ = "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, Chande Kroll stop-line crossings.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the risk-formula quantity, commission and slippage stored.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_454137_chande_kroll_low_stop_cross_long"
FAMILY = "volatility_stop_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "stop_len": [21, 10],
    "atr_mult": [3.0, 2.0],
    "sma_len": [21, 50],
}
DEFAULT_PARAMS = {"stop_len": 21, "atr_mult": 3.0, "sma_len": 21, "atr_len": 10}


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


def _rma(x, n):
    """Wilder smoothing as Pine's rma: SMA seed over the first n valid values, then recursive."""
    v = x.to_numpy(dtype=float)
    out = np.full(v.shape, np.nan)
    valid = np.flatnonzero(~np.isnan(v))
    if len(valid) >= n:
        s = valid[0]
        out[s + n - 1] = v[s:s + n].mean()
        for i in range(s + n, len(v)):
            out[i] = (out[i - 1] * (n - 1) + v[i]) / n
    return pd.Series(out, index=x.index)


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    return _rma(tr, int(n))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["stop_len"])
    atr = _atr(bars_df, p["atr_len"]) * float(p["atr_mult"])
    hs = h.rolling(n).max() - atr
    ls = lo.rolling(n).min() + atr
    sma = c.rolling(int(p["sma_len"])).mean()
    go = ((c > ls) & (c.shift(1) <= ls.shift(1)) & (c > sma)).to_numpy()
    out = (c < hs).to_numpy()
    m = len(c)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, pend = 0, 0
    for i in range(m):
        if pend == 1:
            pos = 1
        elif pend == 2:
            pos = 0
        pend = 0
        if go[i] and pos == 0:
            le[i], pend = True, 1
        if out[i] and pos == 1:
            lx[i], pend = True, 2
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
