"""Joint RSI 14 / CCI 20 extremes, 5-minute bars: RSI under 20 with CCI under -200 goes long, RSI over 80 with CCI over 200 goes short, each with a 1 % stop and 2 % target from the signal close; reversing.
Port of FMZ strategy #477535 "Dynamic Dual Technical Indicator Oversold Overbought Confirmation Trading Strategy" (RSI & CCI Strategy).

FMZ source id: 477535

Source
    https://www.fmz.com/strategy/477535 (PineScript v6, FMZ last modified 2025-01-06 11:54:50).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 119-184), RSI 14, 80 / 20; CCI 20, 200 / -200; stop 1 %, risk-reward 2
    rsi < 20 and cci < -200 -> sl := close x 0.99, tp := close + 2 (close - sl), entry Long + exit(limit = tp, stop = sl);  rsi > 80 and cci > 200 -> mirror for Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is sent on each signal bar from its close: the opening signal's levels are ported,
      sent as fractions of the fill open (a level at or through it is marketable and closed one bar
      late, as #458256); the extremes can repeat inside a trade, and a repeat re-sends the bracket, which
      is not followed (as #434428, mark trailing_stop_pending). REVERSAL INTENDED. Stop module:
      portfolio_kwargs {} (driver D4). No sizing code. FREQ = "5min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; signal-bar bracket as fractions of the fill.
    2 generic: PASS, RSI / CCI joint extremes with a bracket.
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

NAME = "fmz_477535_rsi14_cci20_joint_extreme_pct_bracket_reversal"
FAMILY = "rsi_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "5min"  # backtest header period: 5m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "cci_level": [200, 150],
    "rr": [2.0, 1.0],
}
DEFAULT_PARAMS = {"cci_level": 200, "rr": 2.0, "rsi_length": 14, "cci_length": 20, "sl_pct": 0.01}


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


def _cci(x, n):
    """ta.cci: (x - SMA) / (0.015 x mean absolute deviation), on sliding windows (5-minute bars)."""
    v = x.to_numpy(dtype=float)
    md = np.full(v.shape, np.nan)
    if len(v) >= n:
        w = np.lib.stride_tricks.sliding_window_view(v, n)
        md[n - 1:] = np.abs(w - w.mean(axis=1, keepdims=True)).mean(axis=1)
    ma = x.rolling(n).mean()
    return (x - ma) / (0.015 * pd.Series(md, index=x.index).replace(0.0, np.nan))


def _signals(bars_df, p):
    c = bars_df["close"]
    r = _rsi(c, int(p["rsi_length"]))
    cc = _cci(c, int(p["cci_length"]))
    lvl_c = float(p["cci_level"])
    le = (r < 20) & (cc < -lvl_c)
    se = (r > 80) & (cc > lvl_c)
    sp = float(p["sl_pct"])
    tp = sp * float(p["rr"])
    lvl = {"l_sl": c * (1 - sp), "l_tp": c * (1 + tp), "s_sl": c * (1 + sp), "s_tp": c * (1 - tp)}
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
