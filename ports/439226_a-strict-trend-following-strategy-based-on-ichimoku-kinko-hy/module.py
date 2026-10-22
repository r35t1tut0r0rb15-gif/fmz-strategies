"""Strict Ichimoku alignment, 30-minute bars: a cloud at least one ATR(20) wide, the base line above span A, conversion above base, the close above conversion and rising future spans, base and conversion lines
go long; the mirror goes short; the close crossing back through the base line closes; the span-A stop is re-sent every bar and is not ported.
Port of FMZ strategy #439226 "A Strict Trend Following Strategy Based on Ichimoku Kinko Hyo" (BadaBing Ichimoku).

FMZ source id: 439226

Source
    https://www.fmz.com/strategy/439226 (PineScript v3, FMZ last modified 2024-01-18 15:03:28).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 140-273), ATR 20; conversion 9, base 26, span B 52, displacement 26; min current cloud 1.0 ATR, min future 0 (unused); current span pointing checks off, the other checks on
    bing_long = current cloud width >= ATR and future cloud width >= ATR and base > span A and conversion > base and close > conversion and future spans, base and conversion rising;  bing_short mirror
    entry long when bing_long;  exit(stop = span_a);  close long when close < base;  entry short when bing_short;  exit(stop = span_a);  close short when close > base

Interpretation choices (Pine rules in SURVEY_README.md)
    * span A and span B are the future spans 26 bars back (past values only). The future-cloud test uses
      the current ATR width, as written (the "min future" input is never read). The closes and the entry
      act on the position held at the bar close; an opposite bing signal also meets the base-line close
      and the reversal stands (as #438020). The span-A stop is re-sent every bar at the current span A,
      a moving level the house trail cannot express: not ported, mark trailing_stop_pending. The bada
      flags only feed the plots. strategy.entry reverses: REVERSAL INTENDED. The size of 1 is sizing.
      FREQ = "30min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the per-bar stop pending.
    2 generic: PASS, Ichimoku lines and ATR widths.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the fixed size stored.
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

NAME = "fmz_439226_badabing_ichimoku_alignment"
FAMILY = "ichimoku"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "30min"  # backtest header period: 30m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "min_cloud_atr": [1.0, 0.5],
    "atr_period": [20, 14],
}
DEFAULT_PARAMS = {"min_cloud_atr": 1.0, "atr_period": 20, "conversion": 9, "base": 26, "span_b": 52,
                  "displacement": 26}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]

    def donch(n):
        return (lo.rolling(int(n)).min() + h.rolling(int(n)).max()) / 2

    conv, base = donch(p["conversion"]), donch(p["base"])
    fsa, fsb = (conv + base) / 2, donch(p["span_b"])
    d = int(p["displacement"])
    sa, sb = fsa.shift(d), fsb.shift(d)
    w = float(p["min_cloud_atr"]) * _atr(bars_df, p["atr_period"])
    bl = ((sa > sb + w) & (fsa > fsb + w) & (base > sa) & (conv > base) & (c > conv)
          & (fsa > fsa.shift(1)) & (fsb > fsb.shift(1)) & (base > base.shift(1)) & (conv > conv.shift(1))).to_numpy()
    bs = ((sa < sb - w) & (fsa < fsb - w) & (base < sa) & (conv < base) & (c < conv)
          & (fsa < fsa.shift(1)) & (fsb < fsb.shift(1)) & (base < base.shift(1)) & (conv < conv.shift(1))).to_numpy()
    xl, xs = (c < base).to_numpy(), (c > base).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        new = pos
        if pos == 1 and xl[i]:
            new = 0
        if pos == -1 and xs[i]:
            new = 0
        if bl[i] and pos != 1:
            new = 1
        elif bs[i] and pos != -1:
            new = -1
        pos = new
        tgt[i] = pos
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    return (pd.Series((tgt == 1) & (prev != 1), index=ix), pd.Series((prev == 1) & (tgt == 0), index=ix),
            pd.Series((tgt == -1) & (prev != -1), index=ix), pd.Series((prev == -1) & (tgt == 0), index=ix))


def portfolio_kwargs(**params):
    return {}
