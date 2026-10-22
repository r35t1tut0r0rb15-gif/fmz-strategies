"""RSI 14 window divergences, 10-minute bars: a lower 14-bar close low with a higher 14-bar RSI low, above the 50-bar close support, goes long; the mirror under resistance goes short; each with a 1 % stop and 2 % target from the signal close; reversing.
Port of FMZ strategy #475635 "多周期RSI背离与支撑阻力组合量化策略-Multi-Period-RSI-Divergence-with-Support-Resistance-Quantitative-Trading-Strategy" (Агрессивная стратегия с дивергенциями по RSI и уровнями поддержки/сопротивления).

FMZ source id: 475635

Source
    https://www.fmz.com/strategy/475635 (PineScript v6, FMZ last modified 2024-12-20 17:01:44).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 98-155), RSI 14; support / resistance 50 (closes); stop 1 %, target 2 %
    lowest(close, 14) < its prior and lowest(rsi, 14) > its prior and close > lowest(close, 50) -> entry Long, exit(stop = close x 0.99, limit = close x 1.02);  mirror -> entry Short, exit(stop = close x 1.01, limit = close x 0.98)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is sent on each signal bar from its close: the opening signal's levels are ported,
      sent as fractions of the fill open (a level at or through it is marketable and closed one bar
      late, as #458256); a repeat signal inside a trade re-sends it and is not followed (as #434428,
      mark trailing_stop_pending). REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4). No
      sizing code. FREQ = "10min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; signal-bar bracket as fractions of the fill.
    2 generic: PASS, window RSI divergences with support / resistance filters and a bracket.
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

NAME = "fmz_475635_rsi14_window_divergence_sr50_pct_bracket_reversal"
FAMILY = "rsi_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "10min"  # backtest header period: 10m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "rsi_length": [14, 7],
    "sr_length": [50, 100],
}
DEFAULT_PARAMS = {"rsi_length": 14, "sr_length": 50, "sl_pct": 0.01, "tp_pct": 0.02}


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
    n = int(p["rsi_length"])
    r = _rsi(c, n)
    pl, ph = c.rolling(n).min(), c.rolling(n).max()
    rl, rh = r.rolling(n).min(), r.rolling(n).max()
    k = int(p["sr_length"])
    sup, res = c.rolling(k).min(), c.rolling(k).max()
    le = (pl < pl.shift(1)) & (rl > rl.shift(1)) & (c > sup)
    se = (ph > ph.shift(1)) & (rh < rh.shift(1)) & (c < res)
    sp, tp = float(p["sl_pct"]), float(p["tp_pct"])
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
