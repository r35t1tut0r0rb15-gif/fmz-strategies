"""RSI 14 extremes at the Bollinger 20 / 2 bands, 3-hour bars: RSI under 30 with the close at or under the lower band goes long with a stop at the 5-bar low and a 2 R target; RSI over 70 at or over the upper band goes short with the mirror; reversing.
Port of FMZ strategy #477609 "Dual Technical Indicator Momentum Reversal Trading Strategy with Risk Management System" (RSI + Bollinger Bands with 1:2 Risk/Reward).

FMZ source id: 477609

Source
    https://www.fmz.com/strategy/477609 (PineScript v5, FMZ last modified 2025-01-06 16:45:01).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 79-147), RSI 14, 30 / 70; BB 20 / 2; swing 5; R:R 2 (the target hard-codes 2)
    rsi < 30 and close <= lower -> entry Buy + exit(limit = close + 2 (close - lowest(low, 5)), stop = lowest(low, 5));  rsi > 70 and close >= upper -> entry Sell + exit(mirror with highest(high, 5))

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is sent on each signal bar from its close and 5-bar swing: the opening signal's levels
      are ported, sent as fractions of the fill open (a level at or through it is marketable and closed
      one bar late, as #458256); the extremes can repeat inside a trade and re-send it, which is not
      followed (as #434428, mark trailing_stop_pending). The target uses 2 as written (the R:R input is
      unused). REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4). Stops on bars longer than
      1 hour: mark coarse_bar_stop. No sizing code. FREQ = "3h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; signal-bar swing bracket as fractions of the fill.
    2 generic: PASS, RSI / Bollinger extremes with a swing stop and 2 R target.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code; the R:R input unused.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: coarse_bar_stop, trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_477609_rsi14_bb20_extreme_swing5_stop_2r_reversal"
FAMILY = "bollinger_reversion"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "3h"  # backtest header period: 3h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "swing": [5, 10],
    "rr": [2.0, 1.0],
}
DEFAULT_PARAMS = {"swing": 5, "rr": 2.0, "rsi_length": 14, "bb_length": 20}


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


def _rsi(c, n):
    d = c.diff()
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    return 100 - 100 / (1 + up / dn)


def _signals(bars_df, p):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    r = _rsi(c, int(p["rsi_length"]))
    n = int(p["bb_length"])
    basis = c.rolling(n).mean()
    dev = 2 * c.rolling(n).std(ddof=0)
    le = (r < 30) & (c <= basis - dev)
    se = (r > 70) & (c >= basis + dev)
    k = int(p["swing"])
    swl, swh = lo.rolling(k).min(), h.rolling(k).max()
    rr = float(p["rr"])
    lvl = {"l_sl": swl, "l_tp": c + rr * (c - swl), "s_sl": swh, "s_tp": c - rr * (swh - c)}
    return le, se, lvl


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, lvl = _signals(bars_df, p)
    o = bars_df["open"]
    lf = le.shift(1, fill_value=False)
    sf = se.shift(1, fill_value=False)
    l_thr = (lvl["l_sl"].shift(1) >= o) | (lvl["l_tp"].shift(1) <= o)    # marketable at the fill
    s_thr = (lvl["s_sl"].shift(1) <= o) | (lvl["s_tp"].shift(1) >= o)
    return le, lf & l_thr & ~se & ~le, se, sf & s_thr & ~le & ~se


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, lvl = _signals(bars_df, p)
    o = bars_df["open"]
    lf = le.shift(1, fill_value=False)
    sl_f = (1 - lvl["l_sl"].shift(1) / o).where(lf, lvl["s_sl"].shift(1) / o - 1)
    tp_f = (lvl["l_tp"].shift(1) / o - 1).where(lf, 1 - lvl["s_tp"].shift(1) / o)
    return {"sl_stop": sl_f.where(sl_f > 0), "tp_stop": tp_f.where(tp_f > 0)}


def portfolio_kwargs(**params):
    return {}
