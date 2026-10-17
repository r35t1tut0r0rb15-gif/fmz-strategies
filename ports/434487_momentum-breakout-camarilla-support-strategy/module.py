"""Weekly Camarilla fades, 1-hour bars: a close at or under the last completed broker week's L3 less a seventh of the
L1-L2 gap goes long; a high at or above that week's H1 less the same amount goes short; the position reverses on the
opposite condition.
Port of FMZ strategy #434487 "Momentum Breakout Camarilla Support Strategy" (CamarillaStrategyVhaouri).

FMZ source id: 434487

Source
    https://www.fmz.com/strategy/434487 (PineScript v2, FMZ last modified 2023-12-06 18:09:06).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 121-177), weekly Camarilla from the previous week's high / low / close (h1 = C + 1.1 R / 12, l3 = C - 1.1 R / 4); EMA 8 unused
    men = (l1 - l2) / 7 (weekly, [1]);  close <= l3 and close <= l3 - men -> entry long ("Long12");  high >= h1 - men -> entry short
    exit("Exit Long", "Longl2") and exit("Exit Short", "Short") carry no price, so they do nothing

Interpretation choices (Pine rules in SURVEY_README.md)
    * security('W', x[1]) is the last completed week: the last completed broker week (broker days
      from Monday on, 17:00 America/New_York) built from the port's own bars, known from the next
      week's first bar. men = 1.1 R / 84 of that week.
    * The two strategy.exit calls have no level (and one names a misspelt entry): no exit. Both
      conditions on one bar end short (the short entry is issued last). strategy.entry reverses:
      REVERSAL INTENDED. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; weekly levels from completed broker weeks.
    2 generic: PASS, prior-week range levels.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND428790 (2 members, best partner #428790, Jaccard 0.789); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: weekly levels on broker weeks (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_434487_weekly_camarilla_fade"
FAMILY = "pivot_levels"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "men_div": [7, 3],
    "l_mult": [4.0, 6.0],
}
DEFAULT_PARAMS = {"men_div": 7, "l_mult": 4.0}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _prev_week(bars_df):
    """High, low and close of the last completed broker week, on every bar of the next one."""
    day = broker_day(bars_df.index)
    week = day - pd.to_timedelta(day.weekday, unit="D")
    g = pd.DataFrame({k: bars_df[k].to_numpy() for k in ("high", "low", "close")}, index=week)
    w = g.groupby(level=0).agg({"high": "max", "low": "min", "close": "last"}).shift(1)
    return tuple(w[k].reindex(week).to_numpy() for k in ("high", "low", "close"))


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    wh, wl, wc = _prev_week(bars_df)
    r = wh - wl
    h1 = wc + r * 1.1 / 12.0
    l1, l2 = wc - r * 1.1 / 12.0, wc - r * 1.1 / 6.0
    l3 = wc - r * 1.1 / float(p["l_mult"])
    men = (l1 - l2) / float(p["men_div"])
    cv, hv = bars_df["close"].to_numpy(dtype=float), bars_df["high"].to_numpy(dtype=float)
    with np.errstate(invalid="ignore"):
        lc = (cv <= l3) & (cv <= l3 - men)
        sc = hv >= h1 - men
    m = len(cv)
    tgt = np.zeros(m, dtype=np.int8)
    q = 0
    for i in range(m):
        if lc[i]:
            q = 1
        if sc[i]:
            q = -1
        tgt[i] = q
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return (pd.Series((tgt == 1) & (prev != 1), index=ix), false,
            pd.Series((tgt == -1) & (prev != -1), index=ix), false.copy())


def portfolio_kwargs(**params):
    return {}
