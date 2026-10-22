"""Breaks of a "pre-market" range and of a previous-day level, hourly bars, entries only from flat: the close crossing over the pre-market high or the previous-day high goes long, crossing under the pre-market low or the previous-day low goes short; the close crossing over (under) the last completed day's high (low) closes a long (short).
Port of FMZ strategy #477590 "Multi Period Price Level Breakout Trend Trading System Based on Key Price Levels" (HOD/LOD/PMH/PML/PDH/PDL Strategy by tradingbauhaus).

FMZ source id: 477590

Source
    https://www.fmz.com/strategy/477590 (PineScript v6, FMZ last modified 2025-01-06 16:06:30).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 105-186), daily high / low and their [1] / [0] requests; pre-market window 00:00-09:30 with hours before 09:30 or from 16:00; exchange-time hours
    dailyhigh = security("D", high);  high1 = security("D", high[1]);  high0 = security("D", high[0]);  hour 9 and minute > 30 or hour > 10 -> pdh := high1, else pdh := high0 (lows the same)
    first bar of the "0000-0930" session -> pm_high := high, pm_low := low;  in pre-market hours (before 09:30 or from 16:00) extend them by each bar's high / low
    (crossover(close, pm_high) or crossover(close, pdh)) and no open trade -> entry Long;  (crossunder(close, pm_low) or crossunder(close, pdl)) and no open trade -> entry Short
    long and crossover(close, dailyhigh) -> close Long;  short and crossunder(close, dailylow) -> close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * A version-6 security("D") without lookahead is read as the last completed broker day (as #440503):
      dailyhigh / high0 are the previous broker day's high, high1 the day before; on hourly bars minute
      is always 0, so the "previous day" level is high1 from 11:00 and high0 before, as written. The hours
      are the bar's open hour in UTC (exchange time), with no DST; the pre-market range restarts on the
      first bar from 00:00 (the session test) and grows on bars before 09:30 or from 16:00. Entries need
      no open trade at the bar's close; on a bar with both breaks from flat the later short call wins
      (#437773). A loop follows these states. Opposite entries cannot occur (entries only from flat). No
      sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; daily values from completed broker days.
    2 generic: PASS, pre-market and previous-day level breaks with day-high / low closes.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: pre-market window by UTC bar hour (00:00-09:30 plus 16:00 onward), fixed UTC, no DST; daily levels by broker day (17:00 America/New_York).
Opposite entries cannot occur (entries only from flat).

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_477590_premarket_prevday_level_break_dayhl_close_flat_only"
FAMILY = "support_resistance"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "pm_end_hour": [9, 7],
    "switch_hour": [10, 12],
}
DEFAULT_PARAMS = {"pm_end_hour": 9, "switch_hour": 10}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    day = broker_day(c.index)
    dh, dl = h.groupby(day).max(), lo.groupby(day).min()
    h0 = pd.Series(dh.shift(1).reindex(day).to_numpy(), index=c.index)    # last completed day
    l0 = pd.Series(dl.shift(1).reindex(day).to_numpy(), index=c.index)
    h1 = pd.Series(dh.shift(2).reindex(day).to_numpy(), index=c.index)
    l1 = pd.Series(dl.shift(2).reindex(day).to_numpy(), index=c.index)
    t = c.index.tz_convert("UTC")
    hr = pd.Series(t.hour, index=c.index)
    late = hr > int(p["switch_hour"])
    pdh, pdl = h1.where(late, h0), l1.where(late, l0)
    pm_hours = ((hr < int(p["pm_end_hour"])) | (hr >= 16) | (hr == int(p["pm_end_hour"]))).to_numpy()
    in_sess = ((hr < 9) | (hr == 9)).to_numpy()          # 00:00-09:30 holds the 00:00 ... 09:00 bars
    utc_day = t.normalize()
    hv, lv, cv = h.to_numpy(dtype=float), lo.to_numpy(dtype=float), c.to_numpy(dtype=float)
    m = len(cv)
    pmh, pml = np.full(m, np.nan), np.full(m, np.nan)
    ph = pl = np.nan
    for i in range(m):
        first = in_sess[i] and (i == 0 or not in_sess[i - 1] or utc_day[i - 1] < utc_day[i])
        if first and pm_hours[i]:
            ph, pl = hv[i], lv[i]
        if pm_hours[i] and hv[i] > ph:
            ph = hv[i]
        if pm_hours[i] and lv[i] < pl:
            pl = lv[i]
        pmh[i], pml[i] = ph, pl
    pmh_s, pml_s = pd.Series(pmh, index=c.index), pd.Series(pml, index=c.index)

    def xo(a, b):
        return (a > b) & (a.shift(1) <= b.shift(1))

    lc = (xo(c, pmh_s) | xo(c, pdh)).to_numpy()
    sc = (xo(pml_s, c) | xo(pdl, c)).to_numpy()
    xl = xo(c, h0).to_numpy()
    xs = xo(l0, c).to_numpy()
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, nxt = 0, 0
    for i in range(m):
        pos = nxt
        if pos == 0 and sc[i]:
            se[i], nxt = True, -1
        elif pos == 0 and lc[i]:
            le[i], nxt = True, 1
        if pos == 1 and xl[i]:
            lx[i], nxt = True, 0
        elif pos == -1 and xs[i]:
            sx[i], nxt = True, 0
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {}
