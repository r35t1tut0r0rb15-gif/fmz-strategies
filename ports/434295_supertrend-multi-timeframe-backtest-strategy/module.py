"""Built-in Supertrend 3 / 5 side, 45-minute bars: a close above the Supertrend line goes long, a close below it goes short;
the position is held otherwise and reverses on the opposite side.
Port of FMZ strategy #434295 "SuperTrend Multi Timeframe Backtest Strategy" (SupterTrend).

FMZ source id: 434295

Source
    https://www.fmz.com/strategy/434295 (PineScript v4, FMZ last modified 2023-12-05 10:59:54).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 130-161), factor 3, ATR 5; intraday square-off off
    [superTrend, dir] = supertrend(3, 5);  close > superTrend -> entry long;  close < superTrend -> entry short
    intrady and minute >= 45 and hour >= 14 -> close "buy" and "sell"

Interpretation choices (Pine rules in SURVEY_README.md)
    * Pine's built-in supertrend: hl2 -/+ factor x ATR (Wilder), each band ratcheted unless the
      previous close broke it, direction set against the previous line; the line is the lower band in
      an uptrend, the upper band otherwise.
    * The intraday square-off is off by default (and names an entry id "buy" that does not exist):
      dropped. strategy.entry reverses: REVERSAL INTENDED. The 300 % of equity is sizing. FREQ =
      "45min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, ATR bands.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the strategy() 300 % of equity stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used (the off-by-default 14:45 square-off is dropped).
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_434295_supertrend_3_5_side"
FAMILY = "supertrend"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "45min"  # backtest header period: 45m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "mult": [3.0, 2.0],
    "atr_len": [5, 10],
}
DEFAULT_PARAMS = {"mult": 3.0, "atr_len": 5}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _supertrend(h, lo, c, factor, n):
    """Pine's built-in supertrend(factor, atrPeriod): the line and the direction (-1 up, 1 down)."""
    c1 = c.shift(1)
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1)
    tr.iloc[0] = np.nan
    atr = tr.ewm(alpha=1 / n, adjust=False).mean().to_numpy()
    hl2 = ((h + lo) / 2).to_numpy(dtype=float)
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    lb, ub, st = np.full(m, np.nan), np.full(m, np.nan), np.full(m, np.nan)
    dr = np.ones(m)
    for i in range(m):
        lo_b, up_b = hl2[i] - factor * atr[i], hl2[i] + factor * atr[i]
        pl = lb[i - 1] if i > 0 and not np.isnan(lb[i - 1]) else 0.0
        pu = ub[i - 1] if i > 0 and not np.isnan(ub[i - 1]) else 0.0
        cp = cv[i - 1] if i > 0 else np.nan
        lb[i] = lo_b if (lo_b > pl or cp < pl) else pl
        ub[i] = up_b if (up_b < pu or cp > pu) else pu
        if np.isnan(atr[i]):
            lb[i], ub[i] = np.nan, np.nan
        if i == 0 or np.isnan(atr[i - 1]):
            dr[i] = 1
        elif st[i - 1] == ub[i - 1]:
            dr[i] = -1 if cv[i] > ub[i] else 1
        else:
            dr[i] = 1 if cv[i] < lb[i] else -1
        st[i] = lb[i] if dr[i] == -1 else ub[i]
    return st, dr


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    st, _ = _supertrend(h, lo, c, float(p["mult"]), int(p["atr_len"]))
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if cv[i] > st[i]:
            pos = 1
        elif cv[i] < st[i]:
            pos = -1
        tgt[i] = pos
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return (pd.Series((tgt == 1) & (prev != 1), index=ix), false,
            pd.Series((tgt == -1) & (prev != -1), index=ix), false.copy())


def portfolio_kwargs(**params):
    return {}
