"""Close crossings of the displaced Ichimoku span B, 1-hour bars: the close crossing over the 52-bar Donchian midpoint of 25 bars back goes long, crossing under goes short; each trade has a tick bracket
re-expressed as ATR multiples; reversing.
Port of FMZ strategy #439964 "Lagging Span 2 Line Tracking Trading Strategy" (TPS - FX Trade).

FMZ source id: 439964

Source
    https://www.fmz.com/strategy/439964 (PineScript v5, FMZ last modified 2024-01-25 13:00:51).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 143-174), span B 52, displacement 26; long-only off; long TP 10000 / SL 7500, short TP 20000 / SL 7500 (ticks)
    leadLine = donchian(52);  buycross = crossover(close, leadLine[25]) -> entry Long, exit(profit = 10000, loss = 7500);  sellcross = crossover(leadLine[25], close) -> entry Short, exit(profit = 20000, loss = 7500)

Interpretation choices (Pine rules in SURVEY_README.md)
    * Criterion 2: the brackets are tick distances from the fill; the port reads them as ATR(14)
      multiples of the signal bar: long target 3.33, short target 6.67, stop 2.5 for both (the reading:
      1000 / 2000 / 750 on BTC with 0.1 ticks against a 1-hour ATR near 300), shifted one bar inside
      stops() and re-based on the fill; a second grid value halves them. The span is taken 25 bars back
      (displacement - 1), past values only. strategy.entry reverses: REVERSAL INTENDED. Stop module:
      portfolio_kwargs {} (driver D4). No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry.
    2 generic: ADAPT, tick brackets -> ATR multiples.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the tick inputs stored.
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

NAME = "fmz_439964_span_b_displaced_cross_tick_bracket"
FAMILY = "ichimoku"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "k": [1.0, 0.5],
    "span_len": [52, 26],
}
DEFAULT_PARAMS = {"k": 1.0, "span_len": 52, "displacement": 26, "tp_long": 3.33, "tp_short": 6.67,
                  "sl_mult": 2.5, "atr_len": 14}


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


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def _cross(bars_df, p):
    c = bars_df["close"]
    n = int(p["span_len"])
    lead = ((bars_df["low"].rolling(n).min() + bars_df["high"].rolling(n).max()) / 2).shift(int(p["displacement"]) - 1)
    up = (c > lead) & (c.shift(1) <= lead.shift(1))
    dn = (lead > c) & (lead.shift(1) <= c.shift(1))
    return up, dn


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    up, dn = _cross(bars_df, p)
    false = pd.Series(False, index=bars_df.index)
    return up, false, dn & ~up, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    up, dn = _cross(bars_df, p)
    a = float(p["k"]) * _atr(bars_df, p["atr_len"]) / bars_df["close"]
    sl = (float(p["sl_mult"]) * a).where(up | dn)
    tp = (float(p["tp_long"]) * a).where(up, (float(p["tp_short"]) * a).where(dn))
    return {"sl_stop": sl.shift(1), "tp_stop": tp.shift(1)}


def portfolio_kwargs(**params):
    return {}
