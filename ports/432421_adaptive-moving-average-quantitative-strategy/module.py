"""Self-adjusting SMA trend turns, broker days: an SMA whose length steps by one bar each bar (shorter when no wick touched it
in the last 20 bars or the close sits against its slope, longer when a body crossed it, else the length with the most
wick touches) is smoothed by an EMA 3; the close above a rising line after a falling one goes long, the mirror short.
Port of FMZ strategy #432421 "Adaptive Moving Average Quantitative Strategy" (Automatic Moving Average).

FMZ source id: 432421

Source
    https://www.fmz.com/strategy/432421 (PineScript v5, FMZ last modified 2023-11-17 17:14:36).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 174-267), start length 20, sensitivity 20, smoothing 3, length kept within 2-200
    cma = sma(close, len[1]) (and len[1] +- 1); d = wick touches of each in the last 20 bars, d_b = body touches
    len = no wick touch or close against the slope ? len - 1 : any body touch ? len + 1 : the length (of the three) with most wick touches
    scma = ema(cma, 3); close > scma and scma rising and scma[1] falling -> entry long;  mirror -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * Coded as written: the length is a state carried from bar to bar; each touch count reads the
      touch flags of the past 20 bars as they were computed on those bars; the SMA is undefined
      (and counts no touch) while fewer bars than its length exist, so the length first shrinks, as in
      the source.
    * The start-year input (2020) is the author's window: dropped. strategy.entry reverses: REVERSAL
      INTENDED. Daily bars are broker days (17:00 America/New_York), stamped with their first minute.
      FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, touches of an adaptive SMA and its slope.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 10,000 USD cash per trade stored in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_432421_adaptive_touch_sma_turn"
FAMILY = "ma_trend"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "lookback": [20, 10],
    "smoothing": [3, 6],
}
DEFAULT_PARAMS = {"start": 20, "lookback": 20, "smoothing": 3}


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


def _adaptive_sma(o, h, lo, c, start, lookback):
    m = len(c)
    csum = np.concatenate(([0.0], np.cumsum(c)))
    avg = lambda t, n: (csum[t + 1] - csum[t + 1 - n]) / n if n >= 1 and t + 1 - n >= 0 else np.nan  # noqa: E731
    bull = c > o

    def wick(t, x):
        if np.isnan(x):
            return False
        if bull[t]:
            return (c[t] <= x <= h[t]) or (lo[t] <= x <= o[t])
        return (o[t] <= x <= h[t]) or (lo[t] <= x <= c[t])

    def body(t, x):
        if np.isnan(x):
            return False
        return (o[t] < x < c[t]) if bull[t] else (c[t] < x < o[t])

    flags = np.zeros((m, 6), dtype=np.int64)      # wick 0 / +1 / -1, body 0 / +1 / -1
    cum = np.zeros((m + 1, 6), dtype=np.int64)
    cma = np.full(m, np.nan)
    mal = start
    for t in range(m):
        prev = mal
        x0, xp, xm = avg(t, prev), avg(t, prev + 1), avg(t, prev - 1)
        cma[t] = x0
        flags[t] = (wick(t, x0), wick(t, xp), wick(t, xm), body(t, x0), body(t, xp), body(t, xm))
        cum[t + 1] = cum[t] + flags[t]
        tc = cum[t + 1] - cum[max(t + 1 - lookback, 0)]
        d, dp, dm, db, dpb, dmb = (int(v) for v in tc)
        any_body = db > 0 or dpb > 0 or dmb > 0
        no_wick = d <= 0 and dp <= 0 and dm <= 0
        if d >= dp and d >= dm:
            wmax = prev
        elif dp >= d and dp >= dm:
            wmax = prev + 1
        else:
            wmax = prev - 1
        c1 = cma[t - 1] if t >= 1 else np.nan
        up, dn = x0 > c1, x0 < c1
        against = (up and c[t] < x0) or (dn and c[t] > x0)
        new = prev - 1 if (no_wick or against) else (prev + 1 if any_body else wmax)
        mal = 2 if new < 2 else (200 if new > 200 else new)
    return cma


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c = (bars_df[k].to_numpy(dtype=float) for k in ("open", "high", "low", "close"))
    cma = pd.Series(_adaptive_sma(o, h, lo, c, int(p["start"]), int(p["lookback"])), index=bars_df.index)
    s = cma.ewm(span=int(p["smoothing"]), adjust=False).mean()
    cs = bars_df["close"]
    upt, dnt = s > s.shift(1), s < s.shift(1)
    up_ing = (cs > s) & upt
    dn_ing = (cs < s) & dnt
    le = (up_ing & dnt.shift(1, fill_value=False)).to_numpy()
    se = (dn_ing & upt.shift(1, fill_value=False)).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if le[i]:
            pos = 1
        if se[i]:
            pos = -1
        tgt[i] = pos
    prev = np.concatenate(([0], tgt[:-1]))
    l_e = (tgt == 1) & (prev != 1)
    s_e = (tgt == -1) & (prev != -1)
    false = np.zeros(m, dtype=bool)
    return tuple(pd.Series(a, index=bars_df.index) for a in (l_e, false, s_e, false.copy()))


def portfolio_kwargs(**params):
    return {}
