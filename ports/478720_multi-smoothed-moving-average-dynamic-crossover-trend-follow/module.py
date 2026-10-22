"""Crossings of a triple-smoothed EMA 7 and its EMA 12 signal, hourly bars, with EMA 200, RSI 14 and ATR filters: the smoothed line crossing over the signal above the EMA 200 with RSI over 50 and ATR above its SMA 14 goes long, the mirror goes short, each with a 1.5 ATR stop and 2 ATR target from the signal close; reversing.
Port of FMZ strategy #478720 "Multi Smoothed Moving Average Dynamic Crossover Trend Following Strategy with Multiple Confirmations" (Optimized Triple Smoothed MA Crossover Strategy).

FMZ source id: 478720

Source
    https://www.fmz.com/strategy/478720 (PineScript v6, FMZ last modified 2025-01-17 15:53:16).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 89-181), triple EMA 7, signal EMA 12; EMA 200, RSI 14 / 50, ATR 14 vs SMA 14 (all filters on); SL 1.5 ATR, TP 2 ATR; 200 % of equity
    tsma = ema(ema(ema(close, 7), 7), 7);  sig = ema(tsma, 12);  crossunder(sig, tsma) and close > ema200 and rsi > 50 and atr > sma(atr, 14) -> entry Long + exit(stop = close - 1.5 atr, limit = close + 2 atr);  crossover(sig, tsma) and mirror -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is sent on each signal bar from its close and ATR: the opening signal's levels are
      ported, sent as fractions of the fill open (a level at or through it is marketable and closed one
      bar late, as #458256); a later bullish crossing inside a long (after a bearish one that did not pass
      the filters) re-sends it, which is not followed (as #434428, mark trailing_stop_pending). REVERSAL
      INTENDED. Stop module: portfolio_kwargs {} (driver D4). The 200 % of equity size is sizing. FREQ =
      "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; signal-bar ATR bracket as fractions of the fill.
    2 generic: PASS, triple-smoothed MA crossings with trend, momentum and volatility filters.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 200 % of equity stored, not ported.
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

NAME = "fmz_478720_triple_ema7_signal12_cross_filters_atr_bracket_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "slength": [7, 14],
    "siglen": [12, 24],
}
DEFAULT_PARAMS = {"slength": 7, "siglen": 12, "sl_mult": 1.5, "tp_mult": 2.0}


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


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    return _rma(tr, int(n))


def _ema(x, n):
    return x.ewm(span=int(n), adjust=False).mean()


def _signals(bars_df, p):
    c = bars_df["close"]
    n = int(p["slength"])
    ts = _ema(_ema(_ema(c, n), n), n)
    sig = _ema(ts, p["siglen"])
    bull = (ts > sig) & (ts.shift(1) <= sig.shift(1))
    bear = (ts < sig) & (ts.shift(1) >= sig.shift(1))
    t200 = _ema(c, 200)
    r = _rsi(c, 14)
    atr = _atr(bars_df, 14)
    vol_ok = atr > atr.rolling(14).mean()
    le = bull & (c > t200) & (r > 50) & vol_ok
    se = bear & (c < t200) & (r < 50) & vol_ok
    sl, tp = float(p["sl_mult"]) * atr, float(p["tp_mult"]) * atr
    lvl = {"l_sl": c - sl, "l_tp": c + tp, "s_sl": c + sl, "s_tp": c - tp}
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
