"""WaveTrend level crosses with a Friday close-out, 1-minute bars: WT1 (channel 10, average 21) crossing above -30 goes long
and crossing under 70 goes short (each closing the other side); every position is closed on Friday between 13:00 and
14:00.
Port of FMZ strategy #433575 "Wave Trend Based Quantitative Trading Strategy" (WaveTrend strat).

FMZ source id: 433575

Source
    https://www.fmz.com/strategy/433575 (PineScript v4, FMZ last modified 2023-11-28 16:17:31).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 125-190), channel 10, average 21, overbought 70, oversold -30; long and short on; Friday 1300-1400 close-out
    esa = ema(hlc3, 10);  d = ema(|hlc3 - esa|, 10);  ci = (hlc3 - esa) / (0.015 d);  wt1 = ema(ci, 21)
    crossover(wt1, -30) -> entry long, crossunder(wt1, 70) -> close long;  crossunder(wt1, 70) -> entry short, crossover(wt1, -30) -> close short
    dayofweek == friday and time in 1300-1400 -> close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * Clock (C6): dayofweek and the session use the exchange time zone (UTC on the header's BTC_USDT);
      the script's USA-DST sessions are unused, so the grid also declares America/New_York (DST by the
      zone). A bar is in the window when it opens inside 13:00-14:00.
    * The close-out acts on the position held at the start of the bar; an entry on that bar still goes
      ahead (it fills at the next open). The crosses of one side are the entries of the other:
      REVERSAL INTENDED. FREQ = "1min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; a clock-time exit signal.
    2 generic: PASS, oscillator levels.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: Friday 13:00-14:00 close-out, in UTC (header) or America/New_York (grid), DST by the zone; no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_433575_wavetrend_friday_close"
FAMILY = "momentum_oscillator_turn"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "tz": ["UTC", "America/New_York"],
    "n1": [10, 20],
}
DEFAULT_PARAMS = {"tz": "UTC", "n1": 10, "n2": 21, "ob": 70.0, "os": -30.0}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    ap = (bars_df["high"] + bars_df["low"] + bars_df["close"]) / 3
    n1 = int(p["n1"])
    esa = ap.ewm(span=n1, adjust=False).mean()
    d = (ap - esa).abs().ewm(span=n1, adjust=False).mean()
    wt1 = ((ap - esa) / (0.015 * d)).ewm(span=int(p["n2"]), adjust=False).mean()
    ob, os_ = float(p["ob"]), float(p["os"])
    up = ((wt1 > os_) & (wt1.shift(1) <= os_)).to_numpy()
    dn = ((wt1 < ob) & (wt1.shift(1) >= ob)).to_numpy()
    loc = bars_df.index.tz_convert(str(p["tz"]))
    fri = np.asarray((loc.dayofweek == 4) & (loc.hour == 13))
    m = len(wt1)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if pos != 0 and fri[i]:
            pos = 0
        if up[i]:
            pos = 1
        elif dn[i]:
            pos = -1
        tgt[i] = pos
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    return (pd.Series((tgt == 1) & (prev != 1), index=ix), pd.Series((prev == 1) & (tgt == 0), index=ix),
            pd.Series((tgt == -1) & (prev != -1), index=ix), pd.Series((prev == -1) & (tgt == 0), index=ix))


def portfolio_kwargs(**params):
    return {}
