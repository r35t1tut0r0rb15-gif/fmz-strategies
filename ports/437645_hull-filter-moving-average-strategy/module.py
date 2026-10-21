"""Hull-average turns in the direction of a slow Hull trend, 1-hour bars: the HMA 50 turning up while the HMA 200 rises goes long, turning down while it falls goes short, reversing; each trade has an ATR
bracket written in ticks (stop 100 x 2 ATR, target 100 x 3 ATR) re-expressed as ATR multiples.
Port of FMZ strategy #437645 "Hull Filter Moving Average Strategy" (Hull Filtered Strategy).

FMZ source id: 437645

Source
    https://www.fmz.com/strategy/437645 (PineScript v4, FMZ last modified 2024-01-04 15:16:34).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 143-213), signal HMA 50, filter HMA 200, direction all, stop factor 2, take-profit factor 3, ATR 14; date window 2010-2030
    trend = sign of the HMA 200 change;  signal = sign of the HMA 50 change;  signal == 1 and signal[1] != 1 and trend == 1 -> entry HMA_LNG, exit(profit = 100 x 3 atr, loss = 100 x 2 atr);  short mirror

Interpretation choices (Pine rules in SURVEY_README.md)
    * Criterion 2: profit / loss are TICK counts of 100 x factor x ATR, which equal factor x ATR only at a
      0.01 tick; on BTC's 0.1 tick they are 10 x larger. The port uses sl_stop = k_sl x ATR(14) / close and
      tp_stop = 1.5 x sl_stop (3 / 2) of the signal bar, shifted one bar inside stops() and re-based on the
      fill: 20 is the reading on BTC, 2 the evident intent. The hma is Pine's built-in (integer n / 2,
      rounded sqrt). The date window covers everything: dropped. REVERSAL INTENDED. Stop module:
      portfolio_kwargs {} (driver D4). The 10 % of equity size is sizing. FREQ = "1h" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry.
    2 generic: ADAPT, tick-scaled ATR bracket -> ATR multiples.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent-of-equity size and the factor inputs stored.
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

NAME = "fmz_437645_hull_turn_hull_trend_bracket"
FAMILY = "trend_filter"  # proposed 2026-10-21 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "k_sl": [20.0, 2.0],
    "signal_period": [50, 30],
}
DEFAULT_PARAMS = {"k_sl": 20.0, "signal_period": 50, "filter_period": 200, "atr_len": 14, "tp_ratio": 1.5}


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


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    return _rma(tr, int(n))


def _wma(x, n):
    w = np.arange(1, n + 1, dtype=float)
    return x.rolling(n).apply(lambda v: np.dot(v, w) / w.sum(), raw=True)


def _hma(src, n):
    return _wma(2 * _wma(src, n // 2) - _wma(src, n), int(round(np.sqrt(n))))


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    hs, hf = _hma(c, int(p["signal_period"])), _hma(c, int(p["filter_period"]))
    trend = np.sign(hf.diff()).fillna(0.0)
    sig = np.sign(hs.diff()).fillna(0.0)
    up = (sig == 1) & (sig.shift(1) != 1) & (trend == 1)
    dn = (sig == -1) & (sig.shift(1) != -1) & (trend == -1)
    false = pd.Series(False, index=bars_df.index)
    return up, false, dn, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    f = float(p["k_sl"]) * _atr(bars_df, p["atr_len"]) / bars_df["close"]
    return {"sl_stop": f.shift(1), "tp_stop": (float(p["tp_ratio"]) * f).shift(1)}


def portfolio_kwargs(**params):
    return {}
