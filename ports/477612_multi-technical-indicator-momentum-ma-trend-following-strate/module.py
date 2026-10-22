"""MACD (12 / 26 / 9) cross-ups with RSI 14 over 50 in an SMA 50 / 200 up-trend, 15-minute bars, long only: such a cross buys with a 1 % stop and a 2 % target from the signal close.
Port of FMZ strategy #477612 "Multi Technical Indicator Momentum MA Trend Following Strategy" (Saudi Market Buy-Only Strategy (Customizable)).

FMZ source id: 477612

Source
    https://www.fmz.com/strategy/477612 (PineScript v6, FMZ last modified 2025-01-06 16:56:14).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 95-152), MACD 12 / 26 / 9; RSI 14 over 50; SMA 50 > 200; stop 1 %, TP1 2 %, TP2 3 %; capital and risk inputs unused
    crossover(macd, signal) and rsi > 50 and sma50 > sma200 -> entry Buy + exit TP1(limit = close x 1.02, stop = close x 0.99) + exit TP2(limit = close x 1.03)

Interpretation choices (Pine rules in SURVEY_README.md)
    * Both exits close the whole position (no qty given), so TP1 or its stop acts first and TP2 never
      does. The bracket is sent on each signal bar from its close: the opening signal's levels are
      ported, sent as fractions of the fill open (a level at or through it is marketable and closed one
      bar late, as #458256); a later cross-up inside the trade re-sends it, which is not followed (as
      #434428, mark trailing_stop_pending). Long only. The capital and risk inputs are unused. FREQ =
      "15min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; signal-bar bracket as fractions of the fill.
    2 generic: PASS, MACD cross-ups with RSI and SMA trend filters.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the capital / risk inputs unused; the bracket fractions stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_477612_macd_crossup_rsi50_sma50_200_pct_bracket_long"
FAMILY = "macd"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "15min"  # backtest header period: 15m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "tp_pct": [0.02, 0.03],
    "sl_pct": [0.01, 0.005],
}
DEFAULT_PARAMS = {"tp_pct": 0.02, "sl_pct": 0.01, "rsi_length": 14}


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
    macd = c.ewm(span=12, adjust=False).mean() - c.ewm(span=26, adjust=False).mean()
    sig = macd.ewm(span=9, adjust=False).mean()
    r = _rsi(c, int(p["rsi_length"]))
    trend = c.rolling(50).mean() > c.rolling(200).mean()
    le = (macd > sig) & (macd.shift(1) <= sig.shift(1)) & (r > 50) & trend
    sp, tp = float(p["sl_pct"]), float(p["tp_pct"])
    return le, c * (1 - sp), c * (1 + tp)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, sl, tp = _signals(bars_df, p)
    o = bars_df["open"]
    lf = le.shift(1, fill_value=False)
    thr = (sl.shift(1) >= o) | (tp.shift(1) <= o)       # marketable at the fill
    false = pd.Series(False, index=le.index)
    return le, lf & thr & ~le, false, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, sl, tp = _signals(bars_df, p)
    o = bars_df["open"]
    sl_f = 1 - sl.shift(1) / o
    tp_f = tp.shift(1) / o - 1
    return {"sl_stop": sl_f.where(sl_f > 0), "tp_stop": tp_f.where(tp_f > 0)}


def portfolio_kwargs(**params):
    return {}
