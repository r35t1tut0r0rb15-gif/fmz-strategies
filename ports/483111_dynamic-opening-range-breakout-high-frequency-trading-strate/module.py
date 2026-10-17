"""New York 09:30-09:45 opening-range breakout, one trade a day before 12:00 on Tuesdays, Wednesdays and Fridays,
with the stop at the range midpoint and everything closed at 16:00 New York, 1-minute bars: after 09:45, a close above
the range high goes long (stop the high minus half the range); a close below the range low goes short.
Port of FMZ strategy #483111 "高频动态开盘区间突破交易策略-Dynamic-Opening-Range-Breakout-High-Frequency-Trading-Strategy" (ORB).

FMZ source id: 483111

Source
    https://www.fmz.com/strategy/483111 (PineScript v6, FMZ last modified 2025-02-21 14:02:59).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 107-185), trade days Tue / Wed / Fri
    09:30 NY: reset the range and the daily flag; 09:30 <= time < 09:45 NY: range high / low; 09:45: range set
    while set, hour < 12 NY and no trade today: close > orHigh and position <= 0 -> entry long +
    exit(stop = orHigh - 0.5 x range, limit = position_avg_price + 1.5 x range); short mirrored
    16:00 NY: close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * The target uses strategy.position_avg_price on the signal bar, where the position is flat (na): never set, as
      written (as #489056); stop only. The stop level becomes the signal bar's distance (close - stop) / close,
      shifted one bar inside stops() and re-based on the fill (house rule).
    * Clock rules (check 9 / C6): the range, the entry window and the close-out use America/New_York time (DST by the
      zone) of the bar's open; dayofweek(time) is the chart's time zone, UTC on the author's Binance chart (the same
      date as New York at 09:30-16:00). The 16:00 close_all is an exit signal on the 16:00 bar (next open).
    * One trade a day (the flag is set on the entry); the request.security of the 1-minute close is never used.
      Entries reverse only in principle (one trade a day, all closed at 16:00): REVERSAL INTENDED.
    * Stop module: portfolio_kwargs {} (D4). FREQ = "1min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; stop from the signal bar.
    2 generic: PASS, an opening range and a stop inside it (no fixed price levels).
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing in the source; the stop ported via stops() and quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: 09:30 America/New_York (DST by the zone): range 09:30-09:44, entries 09:45-11:59, close-out 16:00;
    trade days Tue / Wed / Fri by the UTC chart date.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_483111_ny_orb_midpoint_stop_1600_close"
FAMILY = "opening_range_breakout"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "stop_frac": [0.5, 1.0],
    "last_entry_hour": [12, 11],
}
DEFAULT_PARAMS = {"session_tz": "America/New_York", "stop_frac": 0.5, "last_entry_hour": 12,
                  "trade_days": "1,2,4"}


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


def _run(bars_df, p):
    h, lo, c = (bars_df[k].to_numpy(dtype=float) for k in ("high", "low", "close"))
    loc = bars_df.index.tz_convert(p["session_tz"])
    hh, mm = np.asarray(loc.hour), np.asarray(loc.minute)
    days = {int(d) for d in str(p["trade_days"]).split(",")}
    trade_day = np.isin(np.asarray(bars_df.index.tz_convert("UTC").weekday), list(days))
    m = len(c)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    dist = np.full(m, np.nan)
    or_h = or_l = np.nan
    est = taken = False
    pos = 0
    k = float(p["stop_frac"])
    for i in range(m):
        if hh[i] == 9 and mm[i] == 30:
            or_h = or_l = np.nan
            est = taken = False
        if trade_day[i]:
            if hh[i] == 9 and 30 <= mm[i] < 45:
                or_h = h[i] if np.isnan(or_h) else max(or_h, h[i])
                or_l = lo[i] if np.isnan(or_l) else min(or_l, lo[i])
            if hh[i] == 9 and mm[i] == 45 and not np.isnan(or_h) and not np.isnan(or_l):
                est = True
            if est and not np.isnan(or_h) and hh[i] < p["last_entry_hour"] and not taken and i + 1 < m:
                size = k * (or_h - or_l)
                if c[i] > or_h and pos <= 0:
                    le[i], pos, taken = True, 1, True
                    dist[i] = (c[i] - (or_h - size)) / c[i]
                elif c[i] < or_l and pos >= 0:
                    se[i], pos, taken = True, -1, True
                    dist[i] = ((or_l + size) - c[i]) / c[i]
        if hh[i] == 16 and mm[i] == 0:
            if pos == 1:
                lx[i] = True
            elif pos == -1:
                sx[i] = True
            pos = 0
    return le, lx, se, sx, dist


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    idx = bars_df.index
    return tuple(pd.Series(a, index=idx) for a in _run(bars_df, p)[:4])


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    dist = _run(bars_df, p)[4]
    return {"sl_stop": pd.Series(dist, index=bars_df.index).shift(1)}


def portfolio_kwargs(**params):
    return {}
