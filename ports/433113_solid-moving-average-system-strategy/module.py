"""Stacked SMMA / EMA trend entries with a London holding window, 1-hour bars: with the close above the SMMAs 3 / 6 / 9
(hl2) and 50 and the EMA 200, all stacked in order, a long opens (the mirror opens a short) at any time of day; a
300-tick bracket becomes an ATR bracket; every position is closed outside 03:00-10:45.
Port of FMZ strategy #433113 "Solid Moving Average System Strategy" (Money maker EURUSD 15min).

FMZ source id: 433113

Source
    https://www.fmz.com/strategy/433113 (PineScript v4, FMZ last modified 2023-11-24 15:11:18).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 201-286), SMMA 3 / 6 / 9 (hl2), SMMA 50, EMA 200; session 0300-1045 (holding); TP / SL 300 ticks; time_cond true
    close above all and smma3 > smma6 > smma9 > smma50 > ema200 -> entry long ("long", 1);  mirror -> entry short
    exit(profit = 300, loss = 300) each;  not in 0300-1045 -> close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * Unlike #432890 (the same author's Koala script) the entries are not limited to a window here
      (time_cond is true; londonEntry is unused), so an entry outside 03:00-10:45 is closed again on the
      next bar by the close-out, as written: the close-out acts on the position held at the start of
      the bar; the bar that closes a long does not re-open it (the repeated entry is refused under
      pyramiding 1), but an opposite entry on that bar reverses. The entries are levels (a repeat
      while in the position is ignored), so after a stop or target the next qualifying bar re-enters.
    * Clock times (C6): Pine's time(period, session) uses the exchange time zone; on the header's
      BTC_USDT that is UTC; the grid also declares America/New_York (the script's "london" / EURUSD
      reading), DST by the zone. A bar belongs to the window when it opens inside it.
    * Criterion 2: the 300-tick target and stop become atr_k x Wilder ATR 14 of the signal bar as
      fractions of its close (as #432890), shifted one bar inside stops() and re-based on the fill.
    * strategy.entry reverses: REVERSAL INTENDED. The lot formula is sizing; the date inputs are unused.
      Stop module: portfolio_kwargs {} (driver D4). FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry; explicit time exits.
    2 generic: ADAPT, tick distances -> ATR fractions.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the risk-based lot stored in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: 03:00-10:45 holding window, in UTC (header) or America/New_York (grid), DST by the zone; no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_433113_smma_stack_london_close"
FAMILY = "ma_trend"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "tz": ["UTC", "America/New_York"],
    "atr_k": [0.15, 1.0],
}
DEFAULT_PARAMS = {"tz": "UTC", "atr_k": 0.15, "atr_len": 14, "hold_from": 180, "hold_to": 645}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _smma(x, n):
    v = x.to_numpy(dtype=float)
    sma = x.rolling(n).mean().to_numpy(dtype=float)
    out = np.full(len(v), np.nan)
    prev = np.nan
    for i in range(len(v)):
        prev = sma[i] if np.isnan(prev) else (prev * (n - 1) + v[i]) / n
        out[i] = prev
    return pd.Series(out, index=x.index)


def _signals(bars_df, p):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    hl2 = (h + lo) / 2
    s1, s2, s3 = _smma(hl2, 3), _smma(hl2, 6), _smma(hl2, 9)
    s4 = _smma(c, 50)
    e5 = c.ewm(span=200, adjust=False).mean()
    loc = bars_df.index.tz_convert(str(p["tz"]))
    mins = np.asarray(loc.hour * 60 + loc.minute)
    in_hold = (mins >= int(p["hold_from"])) & (mins < int(p["hold_to"]))
    lc = ((c > e5) & (c > s4) & (c > s3) & (c > s2) & (c > s1)
          & (s1 > s2) & (s2 > s3) & (s3 > s4) & (s4 > e5)).to_numpy()
    sc = ((c < e5) & (c < s4) & (c < s3) & (c < s2) & (c < s1)
          & (s1 < s2) & (s2 < s3) & (s3 < s4) & (s4 < e5)).to_numpy()
    m = len(c)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    lx, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        start = pos
        closing = start != 0 and not in_hold[i]
        if closing:
            pos = 0
        # level entries (a repeat while in the position is ignored by the engine); the bar that
        # closes a position does not re-enter it (pyramiding 1: the entry is refused, then close_all)
        if lc[i] and not (closing and start == 1):
            pos, le[i] = 1, True
        elif sc[i] and not (closing and start == -1):
            pos, se[i] = -1, True
        lx[i] = closing and start == 1 and pos == 0
        sx[i] = closing and start == -1 and pos == 0
    c1 = c.shift(1)
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1)
    af = tr.ewm(alpha=1 / int(p["atr_len"]), adjust=False).mean() / c
    return le, lx, se, sx, af


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, lx, se, sx, _ = _signals(bars_df, p)
    ix = bars_df.index
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), pd.Series(se, index=ix), pd.Series(sx, index=ix)


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    af = _signals(bars_df, p)[4]
    k = float(p["atr_k"])
    return {"sl_stop": (af * k).shift(1), "tp_stop": (af * k).shift(1)}


def portfolio_kwargs(**params):
    return {}
