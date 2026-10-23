"""Hourly bars: the EMA 6 of a volume-squared OBV (signed volume x volume / ATR 3, accumulated) crossing over its EMA 24 goes long, crossing under goes short; a 3 % stop from the entry; reversing.
Port of FMZ strategy #442252 "基于OBV指标的趋势跟踪策略OBV-EMA-Crossover-Trend-Following-Strategy" (OBV EMA X BF).

FMZ source id: 442252

Source
    https://www.fmz.com/strategy/442252 (PineScript v4, FMZ last modified 2024-02-20 15:35:08).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 160-234), ATR 3, mult 1 (unused); EMA 24 / 6; stop 3 %; target 5000 % (unused)
    obv = cum(change(close) > 0 ? volume x (volume / atr(3)) : change < 0 ? -volume x (volume / atr) : 0);  long = crossover(ema(obv, 6), ema(obv, 24)) -> entry L;  short = crossunder -> entry S
    exit(L SL, stop = avg x 0.97, when = since_longEntry > 0);  exit(S SL, stop = avg x 1.03, when = since_shortEntry > 0)

Interpretation choices (Pine rules in SURVEY_README.md)
    * Each step of the "OBV" is volume squared over the 3-bar ATR, signed by the close change (weird
      case). The stops are fixed at 3 % of the average (fill) price; their "in signal" gate follows the
      same crossings, and Pine sends them from the bar after the signal, the port arms them at the fill
      (as #438772). The take-profit levels are computed but never sent. REVERSAL INTENDED. 100 % of equity
      is sizing. Stop module: portfolio_kwargs {} (driver D4). FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; fixed 3 % stop from the fill.
    2 generic: PASS, fast / slow EMA crossings of a volume-weighted OBV.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: strategy(): 100 % of equity, capital 10000, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar), squared over the ATR 3, in the OBV; exchange volume to be compared later (Austin, 2026-10-23).
Session open: none (24 h).
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_442252_volume_sq_obv_ema6_24_cross_3pct_stop_1h_reversal"
FAMILY = "obv"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "fast": [6, 12],
    "slow": [24, 50],
}
DEFAULT_PARAMS = {"atr_len": 3, "fast": 6, "slow": 24, "sl": 0.03}


def _resample(raw_1m_df, freq):
    ohlcv = raw_1m_df[["open", "high", "low", "close", "volume"]]
    bars = ohlcv.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
    bars = bars.dropna(subset=["close"])  # an empty period is not a bar; never forward-filled
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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c, v = (bars_df[k] for k in ("high", "low", "close", "volume"))
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1).where(pc.notna())
    atr = _rma(tr, int(p["atr_len"]))
    step = v * (v / atr.where(atr != 0))
    d = c.diff()
    obv = pd.Series(np.where(d > 0, step, np.where(d < 0, -step, 0.0)), index=c.index).fillna(0.0).cumsum()
    e_s = obv.ewm(span=int(p["slow"]), adjust=False).mean()
    e_f = obv.ewm(span=int(p["fast"]), adjust=False).mean()
    up = (e_f > e_s) & (e_f.shift(1) <= e_s.shift(1))
    dn = (e_f < e_s) & (e_f.shift(1) >= e_s.shift(1))
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return up.astype(bool), false, dn.astype(bool), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["sl"])}


def portfolio_kwargs(**params):
    return {}
