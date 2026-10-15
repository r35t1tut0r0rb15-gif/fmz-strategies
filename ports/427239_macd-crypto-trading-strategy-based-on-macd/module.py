"""EMA 12 / 26 direction with a fixed bracket: the fast EMA crossing above the slow one goes long, crossing
below goes short (each closes the other side); a stop-loss and a take-profit fixed at entry (the
source's 1,500 / 20,000 ticks, re-expressed as ATR multiples).
Port of FMZ strategy #427239 "Crypto Trading Strategy Based on MACD".

FMZ source id: 427239

Source
    https://www.fmz.com/strategy/427239 (PineScript v3, FMZ last modified 2023-09-19 11:21:42).
    Verbatim copy: original_source.md. Read 2026-10-15 (FMZ-C).

Original signal (original_source.md lines 176-260), invert off, TP 20000 ticks, SL 1500 ticks,
trail points 100, trail offset 0
    tradeDirection = ema(close, 12) >= ema(close, 26)
    turns true -> entry long (close short); turns false -> entry short (close long)
    exit(profit = 20000, loss = 1500, trail_points = 100, trail_offset = na) per side

Interpretation choices (Pine rules in SURVEY_README.md)
    * dataS / dataB (MACD and RSI extremes) only colour bars; they never reach an order.
    * Criterion 2: profit / loss in ticks are instrument-specific; they become sl_atr / tp_atr x
      Wilder ATR(14) of the signal bar, as fractions of the close, shifted one bar inside stops()
      (known at the fill bar's open) and re-based on the fill price.
    * The trailing part never acts: trail_offset is na (input 0 -> na), and a Pine trailing stop
      needs an offset. No trail is ported (no mark).
    * The date window (2017-01-01 to 2019-02-10) is the author's backtest window: dropped.
    * Stop module: portfolio_kwargs {} (driver D4); one-bar reversals: REVERSAL INTENDED.
    * FREQ = "10min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the bracket is fixed at entry.
    2 generic: ADAPT, tick distances -> ATR multiples.
    3 crypto-exchange-only: no ("crypto" is in the name only; exchange pair in the header).
    4 signals only: the bracket is ported via stops() and quoted in original_sizing.txt.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: ND427239 (with #428795, Jaccard 0.732); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_427239_ema_direction_bracket"
FAMILY = "macd_momentum"  # proposed 2026-10-15 (FMZ-C), user to confirm
FREQ = "10min"  # backtest header period: 10m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sl_atr": [4.0, 2.0],
    "tp_atr": [50.0, 10.0],
    "slow": [26, 50],
}
DEFAULT_PARAMS = {"fast": 12, "slow": 26, "sl_atr": 4.0, "tp_atr": 50.0, "atr_length": 14}


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


def _atr(bars, n):
    pc = bars["close"].shift(1)
    tr = pd.concat([bars["high"] - bars["low"], (bars["high"] - pc).abs(), (bars["low"] - pc).abs()],
                   axis=1).max(axis=1, skipna=False)
    return _rma(tr, n)


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    d = (c.ewm(span=int(p["fast"]), adjust=False).mean()
         >= c.ewm(span=int(p["slow"]), adjust=False).mean())
    d1 = d.shift(1, fill_value=False)
    up = (d & ~d1).astype(bool)
    dn = (d1 & ~d).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    # the close of the other side and the new entry fall on the same bar: an opposite entry reverses
    return up, false.copy(), dn, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    frac = _atr(bars_df, int(p["atr_length"])) / bars_df["close"]
    return {"sl_stop": (p["sl_atr"] * frac).shift(1), "tp_stop": (p["tp_atr"] * frac).shift(1)}


def portfolio_kwargs(**params):
    return {}
