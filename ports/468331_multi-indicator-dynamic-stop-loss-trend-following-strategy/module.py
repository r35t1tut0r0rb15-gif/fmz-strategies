"""UT Bot trail crossings (key 2, ATR 1) confirmed by a rising Hull 31, 2-hour bars: the close crossing over the UT trail while over a rising Hull average goes long, crossing under it while under a falling Hull goes short; reversing.
Port of FMZ strategy #468331 "Multi Indicator Dynamic Stop Loss Trend Following Strategy" (SVMKR_UT_HMA_ORB_Strategy).

FMZ source id: 468331

Source
    https://www.fmz.com/strategy/468331 (PineScript v5, FMZ last modified 2024-09-26 16:03:18).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 140-190), UT Bot key 2, ATR 1 (the true range); Heikin Ashi source off; HMA 31 (WMA 16 / 31, WMA 6)
    close > trail and crossover(ema(close, 1), trail) and close > hull and hull > hull[1] -> entry Buy
    close < trail and crossover(trail, ema(close, 1)) and close < hull and hull < hull[1] -> entry Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * The UT Bot trail is the house reading (as #458056): ATR 1 is the plain true range. ema(src, 1) is
      the close itself. math.round(31 / 2) = 16 and math.round(sqrt(31)) = 6. The Heikin Ashi source is
      off by default. There is no exit: positions end at the opposite entry. REVERSAL INTENDED. No sizing
      code. FREQ = "2h" from the backtest header (UTC-aligned 2-hour bars).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, ATR-trail crossings with a Hull slope filter.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_468331_ut_bot_trail_cross_hull31_slope_reversal"
FAMILY = "atr_trailing_line"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "key": [2.0, 1.0],
    "atr_len": [1, 10],
    "hull_len": [31, 55],
}
DEFAULT_PARAMS = {"key": 2.0, "atr_len": 1, "hull_len": 31}


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


def _wma(x, n):
    n = int(n)
    out = pd.Series(0.0, index=x.index)
    for k in range(n):
        out = out + (n - k) * x.shift(k)
    return out / (n * (n + 1) / 2)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    nl = (float(p["key"]) * _atr(bars_df, p["atr_len"])).to_numpy()
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    line = np.full(m, np.nan)
    for i in range(m):
        prev = line[i - 1] if i > 0 and not np.isnan(line[i - 1]) else 0.0
        c1 = cv[i - 1] if i > 0 else np.nan
        if np.isnan(nl[i]):
            continue                          # math.max / min with an na ATR give na
        if cv[i] > prev and c1 > prev:
            line[i] = max(prev, cv[i] - nl[i])
        elif cv[i] < prev and c1 < prev:
            line[i] = min(prev, cv[i] + nl[i])
        else:
            line[i] = cv[i] - nl[i] if cv[i] > prev else cv[i] + nl[i]
    ln = pd.Series(line, index=c.index)
    n = int(p["hull_len"])
    hull = _wma(2 * _wma(c, int(np.floor(n / 2 + 0.5))) - _wma(c, n), int(np.floor(np.sqrt(n) + 0.5)))
    rising = hull > hull.shift(1)
    above = (c > ln) & (c.shift(1) <= ln.shift(1))
    below = (ln > c) & (ln.shift(1) <= c.shift(1))
    le = (c > ln) & above & (c > hull) & rising
    se = (c < ln) & below & (c < hull) & ~rising
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
