"""Donovan Wall's range filter on closes, broker days: the filter steps when the close moves more than a smoothed 2.618 x average change away; a close above a rising filter goes long, below a falling one goes
short, each only after the other side was last signalled; reversing.
Port of FMZ strategy #439838 "This strategy is a bidirectional adaptive range filtering momentum tracking strategy" (Range Filter [DW] & Labels).

FMZ source id: 439838

Source
    https://www.fmz.com/strategy/439838 (PineScript v4, FMZ last modified 2024-01-24 11:32:23).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 148-306), type 1; close source; range 2.618 x average change (14), smoothed EMA 27; filter changes averaged over 2
    r = ema27(2.618 x ema14(|close - close[1]|));  filt1 steps to close - r / close + r when the close leaves the band;  filt = EMA(2) of filt1 sampled on its changes
    fdir = filt rising / falling (held);  longCond = close > filt and close != close[1] and fdir == 1;  shortCond mirror;  CondIni = last side;  enter only when CondIni[1] is the other side;  closes on the opposite signal

Interpretation choices (Pine rules in SURVEY_README.md)
    * The conditional EMAs seed with their first defined value; the averaged filter is undefined until
      the stepped filter first changes. The written close tests reduce to close != close[1]. CondIni
      starts undefined, so the first trade waits for one side to be seen first. The opposite signal's
      close and entry share a bar and the reversal stands. strategy.entry reverses: REVERSAL INTENDED. No
      sizing code. Daily bars are broker days (17:00 America/New_York), stamped with their first minute.
      FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, range filter on closes.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: DG439838 (2 members, best partner #441059, Jaccard 0.921); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_439838_dw_range_filter_close_flip"
FAMILY = "trend_filter"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rng_qty": [2.618, 1.5],
    "rng_per": [14, 28],
}
DEFAULT_PARAMS = {"rng_qty": 2.618, "rng_per": 14, "smooth_per": 27, "av_samples": 2}


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
    c = bars_df["close"]
    ac = c.diff().abs().ewm(span=int(p["rng_per"]), adjust=False).mean()
    r = (float(p["rng_qty"]) * ac).ewm(span=int(p["smooth_per"]), adjust=False).mean().to_numpy()
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    f1 = np.full(m, np.nan)
    prev = cv[0] if m else np.nan
    for i in range(m):
        cur = prev
        if cv[i] - r[i] > prev:
            cur = cv[i] - r[i]
        if cv[i] + r[i] < prev:
            cur = cv[i] + r[i]
        f1[i] = cur
        prev = cur
    a = 2 / (int(p["av_samples"]) + 1)
    filt = np.full(m, np.nan)
    e = np.nan
    for i in range(1, m):
        if f1[i] != f1[i - 1]:
            e = f1[i] if np.isnan(e) else (f1[i] - e) * a + e
        filt[i] = e
    fd = np.zeros(m)
    d = 0.0
    for i in range(1, m):
        if filt[i] > filt[i - 1]:
            d = 1.0
        elif filt[i] < filt[i - 1]:
            d = -1.0
        fd[i] = d
    moved = np.concatenate(([False], cv[1:] != cv[:-1]))
    lc = (cv > filt) & moved & (fd == 1)
    sc = (cv < filt) & moved & (fd == -1)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    ci = np.nan
    for i in range(m):
        if lc[i] and ci == -1:
            le[i] = True
        elif sc[i] and ci == 1:
            se[i] = True
        if lc[i]:
            ci = 1
        elif sc[i]:
            ci = -1
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, pd.Series(se, index=ix), false.copy()


def portfolio_kwargs(**params):
    return {}
