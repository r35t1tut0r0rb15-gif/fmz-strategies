"""SuperTrend flip stop-and-reverse (ATR factor bands on HL2, ratcheting).
Port of FMZ strategy #200625 "SuperTrend-V1".

Source
    https://www.fmz.com/strategy/200625 (Python, author "homily", FMZ last modified
    2020-04-23 00:12:49). Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 36-123), Factor 3, Pd 7
    runs once per new 15-min bar on records[:-1] (completed bars only)
    tr = max(|H-L|, |H-prevC|, |L-prevC|); atr = tr.ewm(alpha=1/Pd, min_periods=Pd).mean()
    Up = hl2 - Factor*atr; Dn = hl2 + Factor*atr; (NaN -> 0)
    TrendUp[x]   = max(Up[x], TrendUp[x-1])   if close[x-1] > TrendUp[x-1]   else Up[x]
    TrendDown[x] = min(Dn[x], TrendDown[x-1]) if close[x-1] < TrendDown[x-1] else Dn[x]
    Trend[x] = 1 if close[x] > TrendDown[x-1] else (-1 if close[x] < TrendUp[x-1] else Trend[x-1])
    Trend[-1] == 1 and Trend[-2] == -1 -> close short, buy;  mirror -> close long, sell short

Interpretation choices
    * The bot already uses completed bars only: the signal on the last completed bar t is
      exactly the contract's signal bar. The recursion is computed once over the whole history
      (the bot recomputes it over FMZ's record window each bar; same values after warm-up).
    * pandas ewm with adjust=True (the source's default) for ATR; Up/Dn NaN set to 0 as in the
      source; no signal is emitted until ATR exists.
    * Close-and-open-opposite in one pass: REVERSAL INTENDED (portfolio_kwargs {}; the engine's
      default opposite-entry reversal applies). The 2x short volume is sizing.
    * FREQ = "15min" (code requests PERIOD_M15; header 15m).

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_200625_supertrend_reverse"
FAMILY = "supertrend"  # proposed 2026-10-07, user to confirm
FREQ = "15min"  # code requests PERIOD_M15
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "factor": [2.0, 3.0, 4.0],
    "pd": [7, 10, 14],
}
DEFAULT_PARAMS = {"factor": 3.0, "pd": 7}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    n = int(p["pd"])
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([(h - lo).abs(), (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    atr = tr.ewm(alpha=1.0 / n, min_periods=n).mean()
    hl2 = (h + lo) / 2
    up = (hl2 - p["factor"] * atr).fillna(0).to_numpy()
    dn = (hl2 + p["factor"] * atr).fillna(0).to_numpy()
    cl = c.to_numpy(dtype=float)
    valid = atr.notna().to_numpy()

    m = len(cl)
    t_up, t_dn, trend = np.zeros(m), np.zeros(m), np.ones(m, dtype=int)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    for x in range(m):
        if x == 0:
            t_up[0], t_dn[0] = up[0], dn[0]
            continue
        t_up[x] = max(up[x], t_up[x - 1]) if cl[x - 1] > t_up[x - 1] else up[x]
        t_dn[x] = min(dn[x], t_dn[x - 1]) if cl[x - 1] < t_dn[x - 1] else dn[x]
        trend[x] = 1 if cl[x] > t_dn[x - 1] else (-1 if cl[x] < t_up[x - 1] else trend[x - 1])
        if valid[x] and valid[x - 1]:
            le[x] = trend[x] == 1 and trend[x - 1] == -1
            se[x] = trend[x] == -1 and trend[x - 1] == 1

    idx = bars_df.index
    false = pd.Series(False, index=idx)
    return pd.Series(le, index=idx), false.copy(), pd.Series(se, index=idx), false.copy()


def portfolio_kwargs(**params):
    return {}
