"""EMA 12 / 26 crossings with RSI 14 on the 50 side, hourly bars: the cross up with RSI over 50 goes long, the cross down under 50 goes short, each with a 1 % stop and 2 % target from the signal close; any opposite crossing closes; reversing.
Port of FMZ strategy #478742 "动态均线系统结合RSI动量指标的日内交易优化策略-Dynamic-EMA-System-Combined-with-RSI-Momentum-Indicator-for-Optimized-Intraday-Trading-Strategy" (Estrategia Intradía - Cruce EMA + RSI - Optimizado).

FMZ source id: 478742

Source
    https://www.fmz.com/strategy/478742 (PineScript v5, FMZ last modified 2025-01-17 16:27:55).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 97-156), EMA 12 / 26; RSI 14; stop 1 %, target 2 %; qty 20 / close
    crossover(ema12, ema26) and rsi > 50 -> entry Long (qty 20 / close) + exit(stop = close x 0.99, limit = close x 1.02);  long and crossunder -> close Long;  mirror for shorts

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is sent once, on the signal bar, from its close: sent as fractions of the fill open (a
      level at or through it is marketable and closed one bar late, as #458256); the crossings alternate,
      so no repeat re-sends it. A close acts only on the held position and leaves a same-bar reversal
      standing (as #441963). REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4). The 20 / close
      qty is sizing. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; signal-bar bracket as fractions of the fill.
    2 generic: PASS, EMA crossings with an RSI filter, a percent bracket and crossing exits.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: qty 20 / close stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_478742_ema12_26_cross_rsi50_pct_bracket_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "fast": [12, 5],
    "slow": [26, 50],
}
DEFAULT_PARAMS = {"fast": 12, "slow": 26, "rsi_length": 14, "sl_pct": 0.01, "tp_pct": 0.02}


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
    f = c.ewm(span=int(p["fast"]), adjust=False).mean()
    s = c.ewm(span=int(p["slow"]), adjust=False).mean()
    r = _rsi(c, int(p["rsi_length"]))
    up = (f > s) & (f.shift(1) <= s.shift(1))
    dn = (f < s) & (f.shift(1) >= s.shift(1))
    le, se = up & (r > 50), dn & (r < 50)
    sp, tp = float(p["sl_pct"]), float(p["tp_pct"])
    lvl = {"l_sl": c * (1 - sp), "l_tp": c * (1 + tp), "s_sl": c * (1 + sp), "s_tp": c * (1 - tp)}
    return le, se, up, dn, lvl


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, up, dn, lvl = _signals(bars_df, p)
    o = bars_df["open"]
    lf = le.shift(1, fill_value=False)
    sf = se.shift(1, fill_value=False)
    l_thr = (lvl["l_sl"].shift(1) >= o) | (lvl["l_tp"].shift(1) <= o)    # marketable at the fill
    s_thr = (lvl["s_sl"].shift(1) <= o) | (lvl["s_tp"].shift(1) >= o)
    lx = ((lf & l_thr) | dn) & ~se
    sx = ((sf & s_thr) | up) & ~le
    return le, lx, se, sx


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, up, dn, lvl = _signals(bars_df, p)
    o = bars_df["open"]
    lf = le.shift(1, fill_value=False)
    sl_f = (1 - lvl["l_sl"].shift(1) / o).where(lf, lvl["s_sl"].shift(1) / o - 1)
    tp_f = (lvl["l_tp"].shift(1) / o - 1).where(lf, 1 - lvl["s_tp"].shift(1) / o)
    return {"sl_stop": sl_f.where(sl_f > 0), "tp_stop": tp_f.where(tp_f > 0)}


def portfolio_kwargs(**params):
    return {}
