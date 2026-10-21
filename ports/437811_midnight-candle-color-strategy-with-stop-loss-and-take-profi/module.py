"""Pre-midnight candle colour, 3-minute bars: on the bar opening 01:00 at a fixed UTC-5 (06:00 UTC), a long if the bar before the 00:00 bar (opening 04:57 UTC) closed above its open, else a short; each with a
fixed tick bracket re-expressed as ATR multiples; reversing.
Port of FMZ strategy #437811 "Midnight Candle Color Strategy with Stop Loss and Take Profit" (12AM +1H SL/TP Strat).

FMZ source id: 437811

Source
    https://www.fmz.com/strategy/437811 (PineScript v4, FMZ last modified 2024-01-05 16:37:35).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 104-130), nyHour = (hour - 5) % 24 (fixed UTC-5, no DST); long target 57 ticks, stop 200 ticks; short target 50 ticks, stop 200 ticks
    midnight bar (nyHour 0, minute 0): colour := close[1] > open[1] ? green : red;  1 AM bar: green -> entry Long, exit(limit = close + 57 ticks, stop = close - 200 ticks);  red -> entry Short, exit(limit = close - 50 ticks, stop = close + 200 ticks)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The script's hour is the exchange time zone, UTC (as #435514), shifted by a fixed -5 hours with no
      DST, as written ("assuming UTC-5"): the midnight bar opens 05:00 UTC, the 1 AM bar 06:00 UTC (Pine's
      % keeps the sign, so hours 0-4 UTC never match). The colour is the bar before the midnight bar (close[1]
      against open[1]); a flat bar counts red; the colour stays from the last midnight bar seen.
    * Criterion 2: the tick bracket is re-expressed as sl_stop = k_atr x ATR(14) / close of the signal
      bar, shifted one bar inside stops() and re-based on the fill, with targets 57 / 200 (long) and
      50 / 200 (short) of it; 0.57 is the reading (200 ticks of 0.1 = 20 on BTC against a 3-minute ATR
      near 35), 2.0 a wider stop. A same-side signal while a trade is still open would re-place its bracket
      in the original; not modelled (rare: the bracket is reached within hours). REVERSAL INTENDED. Stop
      module: portfolio_kwargs {} (driver D4). No sizing code. FREQ = "3min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry.
    2 generic: ADAPT, tick bracket -> ATR multiples.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the tick bracket stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: fixed UTC-5 clock on UTC bar stamps (no DST, as written).
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_437811_premidnight_candle_colour_bracket"
FAMILY = "calendar_seasonal"  # proposed 2026-10-21 (FMZ-C), user to confirm
FREQ = "3min"  # backtest header period: 3m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "k_atr": [0.57, 2.0],
    "atr_len": [14, 50],
}
DEFAULT_PARAMS = {"k_atr": 0.57, "atr_len": 14, "long_tp_ratio": 0.285, "short_tp_ratio": 0.25,
                  "midnight_hour_utc": 5, "entry_hour_utc": 6}


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


def _signals(bars_df, p):
    o, c = bars_df["open"], bars_df["close"]
    ix = bars_df.index.tz_convert("UTC")
    mid = ((ix.hour == int(p["midnight_hour_utc"])) & (ix.minute == 0))
    one = ((ix.hour == int(p["entry_hour_utc"])) & (ix.minute == 0))
    up_prev = (c.shift(1) > o.shift(1)).to_numpy()
    m = len(c)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    colour = 0                                           # na until the first midnight bar
    for i in range(m):
        if mid[i]:
            colour = 1 if up_prev[i] else -1
        if one[i]:
            le[i] = colour == 1
            se[i] = colour == -1
    return pd.Series(le, index=bars_df.index), pd.Series(se, index=bars_df.index)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se = _signals(bars_df, p)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, _ = _signals(bars_df, p)
    f = float(p["k_atr"]) * _atr(bars_df, p["atr_len"]) / bars_df["close"]
    ratio = pd.Series(np.where(le.to_numpy(), float(p["long_tp_ratio"]), float(p["short_tp_ratio"])),
                      index=bars_df.index)
    return {"sl_stop": f.shift(1), "tp_stop": (ratio * f).shift(1)}


def portfolio_kwargs(**params):
    return {}
