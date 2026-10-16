"""Early-European-morning breakout, hourly bars: in the 03:00-04:00 UTC bar, the close (or high) crossing above
the SMA 2 with the previous close above the EMA 200 goes long, the mirror goes short; positions close once
a bar starts outside 03:00-09:45 UTC; each trade has a stop.
Port of FMZ strategy #428812 "Breakout Day Trading Strategy" (2 ma breakout).

FMZ source id: 428812

Source
    https://www.fmz.com/strategy/428812 (PineScript v4, FMZ last modified 2023-10-09 16:56:21).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 260-321), SMA 2, EMA 200, stop 66 ticks, windows "0300-0400" (entries) and "0300-0945" (holding)
    longC = time in "0300-0400" and (crossover(close, sma2) or crossover(high, sma2)) and close[1] > ema200
    shortC = time in "0300-0400" and (crossunder(close, sma2) or crossunder(low, sma2)) and close[1] < ema200
    close long / short when not time in "0300-0945"; exit(loss = 66) per side

Interpretation choices (Pine rules in SURVEY_README.md)
    * The session strings are read in the chart's exchange time, taken as UTC (FMZ crypto data; as the
      earlier FMZ-C ports, e.g. #428000): a bar is "in" a session when its open time is inside it. The
      closes outside the holding window are explicit exit signals (time exits from simulate()).
    * Criterion 2: the 66-tick stop becomes sl_atr x Wilder ATR(14) of the signal bar (shifted one bar
      inside stops(), re-based on the fill): 6.6 USD on hourly BTC is about 0.05 ATR.
    * The session-colour inputs, the hiHighs / loLows block (local values never used) and the 60-minute
      securities (plots commented out) do nothing. The risk-% size is sizing. The date window is dropped.
    * strategy.entry reverses (both sides only in one bar a day). Stop module: portfolio_kwargs {} (driver
      D4); REVERSAL INTENDED. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; stop fixed at entry; clock-time exits as signals.
    2 generic: ADAPT, the tick stop -> an ATR multiple.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the commented-out strategy(), the risk-% size and the stop quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: entries only in the bar opening 03:00-04:00 UTC, exits once a bar opens outside 03:00-09:45 UTC (UTC, no DST; not a venue open).
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_428812_morning_sma2_breakout"
FAMILY = "momentum_breakout"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sl_atr": [0.05, 0.5],
    "trend_length": [200, 100],
}
DEFAULT_PARAMS = {"length": 2, "trend_length": 200, "sl_atr": 0.05, "atr_length": 14,
                  "entry_start": 180, "entry_end": 240, "hold_start": 180, "hold_end": 585}


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


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    idx = bars_df.index.tz_convert("UTC")
    mins = pd.Series(idx.hour * 60 + idx.minute, index=bars_df.index)
    in_entry = (mins >= p["entry_start"]) & (mins < p["entry_end"])
    in_hold = (mins >= p["hold_start"]) & (mins < p["hold_end"])
    out = c.rolling(int(p["length"])).mean()
    outa = c.ewm(span=int(p["trend_length"]), adjust=False).mean()
    xo = lambda a, b: (a > b) & (a.shift(1) <= b.shift(1))  # noqa: E731
    xu = lambda a, b: (a < b) & (a.shift(1) >= b.shift(1))  # noqa: E731
    long_e = (in_entry & (xo(c, out) | xo(h, out)) & (c.shift(1) > outa)).astype(bool)
    short_e = (in_entry & (xu(c, out) | xu(lo, out)) & (c.shift(1) < outa) & ~long_e).astype(bool)
    exit_ = (~in_hold).astype(bool)
    return long_e, exit_, short_e, exit_.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    frac = _rma(tr, int(p["atr_length"])) / c
    return {"sl_stop": (p["sl_atr"] * frac).shift(1)}


def portfolio_kwargs(**params):
    return {}
