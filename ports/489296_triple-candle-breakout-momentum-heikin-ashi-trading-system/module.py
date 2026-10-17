"""Heikin-Ashi colour-change breakouts, broker days: after three red Heikin-Ashi candles and a green one, a next bar
whose high breaks that green candle's high goes long; the long closes when the low breaks the low of the first red
Heikin-Ashi candle after the breakout; shorts mirrored (three greens, a red, its low broken).
Port of FMZ strategy #489296 "三次蜡烛突破动量平滑平均交易策略-Triple-Candle-Breakout-Momentum-Heikin-Ashi-Trading-System" (Heikin-Ashu Strategy).

FMZ source id: 489296

Source
    https://www.fmz.com/strategy/489296 (PineScript v6, FMZ last modified 2025-04-03 11:17:32).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 265-322), no inputs
    HA close = (o + h + l + c) / 4; HA open = (HA open[1] + HA close[1]) / 2 ((o + c) / 2 first); HA high / low incl. o / c
    setup = red[3] red[2] red[1] green -> level = HA high (else nz(level), i.e. 0 before the first setup)
    long_breakout = HA high[1] == level and high > level
    first_red_low = na on a breakout, else the HA low of the first red HA candle after it (kept)
    long_exit = long_active and low < first_red_low;  shorts mirrored with three greens and a red
    breakout -> entry long; long_exit -> close long; short breakout -> entry short; short exit -> close short

Interpretation choices (Pine rules in SURVEY_README.md)
    * nz() makes each stored level 0 before its first setup, so no breakout can happen before then, as written.
    * The script's long_active / short_active flags are kept apart from the position; a close acts on the position
      held at the bar's start (written after the entry; as #430850). Entries reverse (REVERSAL INTENDED).
    * Criterion 5: the source has no inputs; the number of opposite candles before the setup is the declared variant
      (3, as written, or 2).
    * Daily bars are broker days (17:00 America/New_York), stamped with their first minute; FREQ = "1D" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders (breaks checked on the completed bar, filled next open).
    2 generic: PASS, candle levels only.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (2 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_489296_heikin_ashi_colour_change_breakout"
FAMILY = "heikin_ashi_trend"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "n_opposite": [3, 2],
}
DEFAULT_PARAMS = {"n_opposite": 3}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def precompute(raw_1m_df, symbol_key, **params):
    df = raw_1m_df[["open", "high", "low", "close"]].dropna(how="all")
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    lab = broker_day(df.index)
    bars = df.groupby(lab).agg({"open": "first", "high": "max", "low": "min", "close": "last"})
    first = pd.Series(df.index, index=df.index).groupby(lab).first()
    bars.index = pd.DatetimeIndex(first.loc[bars.index].values)   # each bar stamped with its first minute
    if bars.index.tz is None:
        bars.index = bars.index.tz_localize("UTC")
    return bars


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c = (bars_df[k].to_numpy(dtype=float) for k in ("open", "high", "low", "close"))
    m = len(c)
    hc = (o + h + lo + c) / 4
    ho = np.empty(m)
    for i in range(m):
        ho[i] = (o[i] + c[i]) / 2 if i == 0 else (ho[i - 1] + hc[i - 1]) / 2
    hh, hl = np.maximum(h, np.maximum(ho, hc)), np.minimum(lo, np.minimum(ho, hc))
    red, green = hc < ho, hc > ho
    k = int(p["n_opposite"])
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    g_level = r_level = 0.0              # nz(level) before the first setup
    red_low = green_high = np.nan
    long_on = short_on = False
    for i in range(m):
        if i >= k and all(red[i - j] for j in range(1, k + 1)) and green[i]:
            g_level = hh[i]
        lb = i >= 1 and hh[i - 1] == g_level and h[i] > g_level
        if lb:
            red_low = np.nan
        elif red[i] and np.isnan(red_low):
            red_low = hl[i]
        long_on = True if lb else long_on
        lx = long_on and not np.isnan(red_low) and lo[i] < red_low
        if lx:
            long_on = False
        if i >= k and all(green[i - j] for j in range(1, k + 1)) and red[i]:
            r_level = hl[i]
        sb = i >= 1 and hl[i - 1] == r_level and lo[i] < r_level
        if sb:
            green_high = np.nan
        elif green[i] and np.isnan(green_high):
            green_high = hh[i]
        short_on = True if sb else short_on
        sx = short_on and not np.isnan(green_high) and h[i] > green_high
        if sx:
            short_on = False
        start = pos
        if lb:
            pos = 1
        if lx and start == 1 and pos == 1:
            pos = 0
        if sb:
            pos = -1
        if sx and start == -1 and pos == -1:
            pos = 0
        tgt[i] = pos
    prev = np.concatenate(([0], tgt[:-1]))
    idx = bars_df.index
    return (pd.Series((tgt == 1) & (prev != 1), index=idx), pd.Series((prev == 1) & (tgt == 0), index=idx),
            pd.Series((tgt == -1) & (prev != -1), index=idx), pd.Series((prev == -1) & (tgt == 0), index=idx))


def portfolio_kwargs(**params):
    return {}
