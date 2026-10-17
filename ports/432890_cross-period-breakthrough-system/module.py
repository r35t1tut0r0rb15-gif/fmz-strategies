"""Stacked SMMA / EMA trend entries in a morning window, 1-hour bars: with the close above the SMMAs 3 / 6 / 9 (hl2) and 50
and the EMA 200, all stacked in order, during 03:00-08:45 a long opens (the mirror opens a short); a 300-tick bracket
becomes an ATR bracket; every position is closed outside 03:00-10:45.
Port of FMZ strategy #432890 "Cross Period Breakthrough System" (Koala Script).

FMZ source id: 432890

Source
    https://www.fmz.com/strategy/432890 (PineScript v4, FMZ last modified 2023-11-22 15:22:49).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 192-296), SMMA 3 / 6 / 9 (hl2), SMMA 50, EMA 200; sessions 0300-0845 (entries) and 0300-1045; TP / SL 300 ticks
    close above all and smma3 > smma6 > smma9 > smma50 > ema200 and in 0300-0845 -> entry long ("long", 1)
    mirror -> entry short ("short", 0);  exit(profit = 300, loss = 300) each;  not in 0300-1045 -> close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * Clock times (check 9 / C6): Pine's time(period, session) uses the exchange time zone; on the
      header's BTC_USDT that is UTC (no DST). The script's "london" label suggests the FX exchange
      time (America/New_York, where 03:00 is the London open); the grid declares both zones, DST by
      the zone. A bar belongs to a window when it opens inside it.
    * Criterion 2: the 300-tick target and stop (30 USD on BTC_USDT, mintick 0.1, about 0.15 ATR on
      hourly BTC) become atr_k x Wilder ATR 14 of the signal bar as fractions of its close, shifted one
      bar inside stops() and re-based on the fill.
    * The close-out outside the window is an explicit exit signal. strategy.entry reverses (the two
      conditions exclude each other): REVERSAL INTENDED. The lot formula is sizing; the date inputs
      are dropped. Stop module: portfolio_kwargs {} (driver D4). FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry; explicit time exits.
    2 generic: ADAPT, tick distances -> ATR fractions.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the risk-based lot and the commission / slippage settings stored in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: 03:00-08:45 entries and 03:00-10:45 holding, in UTC (header) or America/New_York (grid), DST by the zone; no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_432890_koala_smma_stack_window"
FAMILY = "ma_trend"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "tz": ["UTC", "America/New_York"],
    "atr_k": [0.15, 1.0],
}
DEFAULT_PARAMS = {"tz": "UTC", "atr_k": 0.15, "atr_len": 14, "entry_from": 180, "entry_to": 525, "hold_to": 645}


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
    mins = pd.Series(loc.hour * 60 + loc.minute, index=c.index)
    in_entry = (mins >= int(p["entry_from"])) & (mins < int(p["entry_to"]))
    in_hold = (mins >= int(p["entry_from"])) & (mins < int(p["hold_to"]))
    le = ((c > e5) & (c > s4) & (c > s3) & (c > s2) & (c > s1) & in_entry
          & (s1 > s2) & (s2 > s3) & (s3 > s4) & (s4 > e5)).astype(bool)
    se = ((c < e5) & (c < s4) & (c < s3) & (c < s2) & (c < s1) & in_entry
          & (s1 < s2) & (s2 < s3) & (s3 < s4) & (s4 < e5)).astype(bool)
    out_ = (~in_hold).astype(bool)
    c1 = c.shift(1)
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1)
    af = tr.ewm(alpha=1 / int(p["atr_len"]), adjust=False).mean() / c
    return le, se, out_, af


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, out_, _ = _signals(bars_df, p)
    return le, out_.copy(), se, out_.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    af = _signals(bars_df, p)[3]
    k = float(p["atr_k"])
    return {"sl_stop": (af * k).shift(1), "tp_stop": (af * k).shift(1)}


def portfolio_kwargs(**params):
    return {}
