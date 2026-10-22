"""SMA 50 / 200 crossings with a close and RSI filter, 1-hour bars, with a percent bracket: a cross up with the close above the SMA 50 and the RSI 14 under 70 goes long, a cross down with the close under it
and the RSI over 30 goes short; stop 2 %, target 4 %; reversing.
Port of FMZ strategy #445817 "基于MA和RSI的趋势跟踪摆动策略MA-and-RSI-based-Trend-Following-Swing-Trading-Strategy" (Swing Trading Strategy (MA and RSI)).

FMZ source id: 445817

Source
    https://www.fmz.com/strategy/445817 (PineScript v5, FMZ last modified 2024-03-22 14:31:57).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 143-190), SMA 50 / 200; RSI 14, levels 70 / 30; stop 2 %, risk / reward 2
    crossover(sma50, sma200) and close > sma50 and rsi < 70 -> entry Long, exit(stop = close x 0.98, limit = close x 1.04);  short mirrored

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is a fixed percentage of the signal close, so it is ported as fractions of the fill:
      sl_stop 0.02, tp_stop 0.04 (as #437751). A repeated signal inside the trade re-issues the levels
      from that bar's close: not expressible (mark trailing_stop_pending); the opening levels are kept.
      strategy.entry reverses: REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4). No
      sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry (re-sent levels marked).
    2 generic: PASS, SMA crossings with close and RSI filters, percent bracket.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_445817_sma50_200_cross_rsi_filter_pct_bracket_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sl": [0.02, 0.01],
    "rr": [2.0, 3.0],
}
DEFAULT_PARAMS = {"sl": 0.02, "rr": 2.0, "fast": 50, "slow": 200, "rsi_len": 14, "ob": 70.0, "os": 30.0}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    f = c.rolling(int(p["fast"])).mean()
    s = c.rolling(int(p["slow"])).mean()
    r = _rsi(c, int(p["rsi_len"]))
    f1, s1 = f.shift(1), s.shift(1)
    le = (f > s) & (f1 <= s1) & (c > f) & (r < float(p["ob"]))
    se = (f < s) & (f1 >= s1) & (c < f) & (r > float(p["os"]))
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    sl = float(p["sl"])
    return {"sl_stop": sl, "tp_stop": sl * float(p["rr"])}


def portfolio_kwargs(**params):
    return {}
