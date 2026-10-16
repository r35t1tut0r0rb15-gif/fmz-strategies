"""SuperTrend (1 x ATR 1) flips with a "main" SuperTrend on the chart's own 2-hour bars (so the two are
the same line): a flip up goes long, a flip down goes short, with a take-profit and a stop-loss fixed
at entry.
Port of FMZ strategy #427591 "Dual-Timeframe Supertrend Tracking Strategy".

FMZ source id: 427591

Source
    https://www.fmz.com/strategy/427591 (PineScript v3, FMZ last modified 2023-09-22 14:27:52).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 211-268), main timeframe "120", factor 1, ATR 1, TP 500, SL 400 ticks
    SuperTrend lines and Trend on the chart; MTrend the same on security(ticker, "120", ...)
    Trend flips up and MTrend == 1 -> entry long; flips down and MTrend == -1 -> entry short
    exit(profit = 500, loss = 400) ticks per side

Interpretation choices (Pine rules in SURVEY_README.md)
    * The chart is 2-hour bars (header) and the main timeframe is "120" (2 hours): the main trend is
      the chart's own trend, so MTrend == Trend; the filter is always true at a flip.
    * Criterion 2: the tick distances become tp_atr / sl_atr x Wilder ATR(14) of the signal bar (as
      fractions of its close, shifted one bar inside stops(), re-based on the fill). On the source's
      2-hour BTC bars with a 0.1 tick, 50 / 40 USD is about 0.3 ATR (judgement before any backtest).
    * Stop module: portfolio_kwargs {} (driver D4); an opposite flip reverses: REVERSAL INTENDED.
    * Stops on 2-hour bars: mark coarse_bar_stop. FREQ = "2h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry.
    2 generic: ADAPT, tick distances -> ATR multiples.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the bracket is ported via stops() and quoted in original_sizing.txt.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: ND427591 (3 members, best partner #433448, Jaccard 0.705); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_427591_supertrend_flip_bracket"
FAMILY = "supertrend"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "factor": [1, 3],
    "tp_atr": [0.3, 1.0],
    "sl_atr": [0.25, 1.0],
}
DEFAULT_PARAMS = {"factor": 1, "pd": 1, "tp_atr": 0.3, "sl_atr": 0.25, "atr_length": 14}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
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


def _tr(bars):
    pc = bars["close"].shift(1)
    return pd.concat([bars["high"] - bars["low"], (bars["high"] - pc).abs(), (bars["low"] - pc).abs()],
                     axis=1).max(axis=1, skipna=False)


def _trend(bars, factor, n):
    hl2 = ((bars["high"] + bars["low"]) / 2).to_numpy()
    a = _rma(_tr(bars), n).to_numpy()
    c = bars["close"].to_numpy(dtype=float)
    m = len(c)
    tu, td = np.zeros(m), np.zeros(m)
    tr_ = np.ones(m, dtype=np.int8)
    for i in range(m):
        up_b, dn_b = hl2[i] - factor * a[i], hl2[i] + factor * a[i]
        tu1 = tu[i - 1] if i else 0.0
        td1 = td[i - 1] if i else 0.0
        c1 = c[i - 1] if i else np.nan
        tu[i] = max(up_b, tu1) if c1 > tu1 else up_b
        td[i] = min(dn_b, td1) if c1 < td1 else dn_b
        t = tr_[i - 1] if i else 1
        if c[i] > td1:
            t = 1
        elif c[i] < tu1:
            t = -1
        tr_[i] = t
    return tr_


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    t = _trend(bars_df, float(p["factor"]), int(p["pd"]))
    t1 = np.concatenate(([1], t[:-1]))
    idx = bars_df.index
    up = pd.Series((t == 1) & (t1 == -1), index=idx)     # MTrend == Trend on the chart's own period
    dn = pd.Series((t == -1) & (t1 == 1), index=idx)
    false = pd.Series(False, index=idx)
    return up, false.copy(), dn, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    frac = _rma(_tr(bars_df), int(p["atr_length"])) / bars_df["close"]
    return {"sl_stop": (p["sl_atr"] * frac).shift(1), "tp_stop": (p["tp_atr"] * frac).shift(1)}


def portfolio_kwargs(**params):
    return {}
