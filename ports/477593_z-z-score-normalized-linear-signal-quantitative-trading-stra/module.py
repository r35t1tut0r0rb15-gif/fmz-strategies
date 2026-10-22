"""Z-score (14) of a blend of RSI 14 and the close, 15-minute bars: a score under -1.5 goes long, over 1.5 goes short, each with a 1 % stop and 2 % target from the signal close; reversing.
Port of FMZ strategy #477593 "基于Z分数标准化的线性信号量化交易策略-Z-Score-Normalized-Linear-Signal-Quantitative-Trading-Strategy" (Linear Signal-Based Strategy).

FMZ source id: 477593

Source
    https://www.fmz.com/strategy/477593 (PineScript v5, FMZ last modified 2025-01-06 16:14:07).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 81-132), lookback 14; alpha 0.5; take profit 0.02, stop 0.01 (used as fractions); threshold 1.5; qty 1
    sig = 0.5 rsi14 + 0.5 close;  z = (sig - sma(sig, 14)) / stdev(sig, 14);  z < -1.5 -> entry Long (qty 1) + exit(stop = close x 0.99, limit = close x 1.02);  z > 1.5 -> mirror Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The "percent" inputs are used as fractions (close x (1 + 0.02)), so the bracket is 2 % / 1 %, as
      written. It is sent on each signal bar from its close: the opening signal's levels are ported, sent
      as fractions of the fill open (a level at or through it is marketable and closed one bar late, as
      #458256); the score can stay beyond the threshold, and a repeat re-sends the bracket, which is not
      followed (as #434428, mark trailing_stop_pending). ta.stdev is the population deviation. REVERSAL
      INTENDED. Stop module: portfolio_kwargs {} (driver D4). The fixed qty 1 is sizing. FREQ = "15min"
      from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; signal-bar bracket as fractions of the fill.
    2 generic: PASS, blended RSI / price z-score extremes with a bracket.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: qty 1 stored, not ported.
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

NAME = "fmz_477593_rsi_close_blend_zscore14_pct_bracket_reversal"
FAMILY = "zscore_reversion"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "15min"  # backtest header period: 15m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "lookback": [14, 50],
    "threshold": [1.5, 2.0],
}
DEFAULT_PARAMS = {"lookback": 14, "threshold": 1.5, "alpha": 0.5, "tp_frac": 0.02, "sl_frac": 0.01}


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
    c = bars_df["close"]
    n = int(p["lookback"])
    a = float(p["alpha"])
    sig = a * _rsi(c, n) + (1 - a) * c
    z = (sig - sig.rolling(n).mean()) / sig.rolling(n).std(ddof=0)
    t = float(p["threshold"])
    le, se = z < -t, z > t
    sp, tp = float(p["sl_frac"]), float(p["tp_frac"])
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
