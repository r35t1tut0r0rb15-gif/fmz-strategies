"""New York 09:30-09:45 opening-range breakouts on Tuesdays, Wednesdays and Fridays, 1-minute bars: one trade a day before 12:00 New York, a close over the range high goes long and a close under the range low goes short, the stop half a range inside the broken edge and the target 1.5 ranges from the fill; everything closes at 16:00 New York.
Port of FMZ strategy #483111 "Dynamic Opening Range Breakout High Frequency Trading Strategy" (ORB).

FMZ source id: 483111

Source
    https://www.fmz.com/strategy/483111 (PineScript v6, FMZ last modified 2025-02-21 14:02:59).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 104-185), opening range 09:30-09:44 America/New_York; stop 0.5 range; target 3 x stop; days Tue / Wed / Fri; close-all 16:00; MPL 2.0 notice (UKFLIPS69)
    09:30 NY -> reset range and the day's flag;  trading day and 09:30 <= t < 09:45 -> orHigh / orLow accumulate;  09:45 -> range established
    established and hour < 12 and no trade today: close > orHigh and position <= 0 -> entry ORB Long + exit(stop = orHigh - 0.5 range, limit = avg + 1.5 range);  close < orLow -> entry ORB Short + mirror;  trade flag set
    16:00 NY -> close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * The range times use America/New_York (DST by the zone), as written; dayofweek(time) reads the
      chart exchange's zone, UTC for the header's Binance pair, so the weekday is the bar's UTC weekday.
      The one-trade-a-day flag also stops a second entry, so the position gates never bind after it.
    * The stop level is fixed at the signal bar and sent as a fraction of the fill open (a level at or
      through it is marketable and closed one bar late, as #458256); the target's average price is na on
      the flat signal bar and is ported from the fill, active from the fill bar (as #440797). The 16:00
      close-all is an exit signal on the 16:00 bar. An entry on the other side would reverse (REVERSAL
      INTENDED; one trade a day makes it rare). Stop module: portfolio_kwargs {} (driver D4). No sizing
      code. The MPL 2.0 notice is kept with the verbatim copy (ported, stated). FREQ = "1min" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; range stop and target as fractions of the fill.
    2 generic: PASS, New York opening-range breakouts.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: 09:30-09:45 America/New_York opening range (DST by the zone); entries before 12:00 New York; close-all at 16:00 New York; Tue / Wed / Fri by the UTC weekday.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_483111_ny_0930_0945_orb_half_range_stop_1_5_range_target"
FAMILY = "opening_range"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True
SESSION_TZ = "America/New_York"   # the range, noon and 16:00 times, as written
DAY_TZ = "UTC"                    # dayofweek(time) reads the chart exchange's zone (Binance: UTC)

GRID = {
    "stop_frac": [0.5, 0.25],
    "target_mult": [3.0, 2.0],
}
DEFAULT_PARAMS = {"stop_frac": 0.5, "target_mult": 3.0, "days": "1,2,4"}


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


def _plan(bars_df, p):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    ny = bars_df.index.tz_convert(SESSION_TZ)
    hr, mn = np.asarray(ny.hour), np.asarray(ny.minute)
    wd = np.asarray(bars_df.index.tz_convert(DAY_TZ).weekday)
    days = {int(x) for x in str(p["days"]).split(",")}
    hv, lv, cv = (x.to_numpy(dtype=float) for x in (h, lo, c))
    m = len(cv)
    le, se, xa = (np.zeros(m, dtype=bool) for _ in range(3))
    l_sl, s_sl, tgt = np.full(m, np.nan), np.full(m, np.nan), np.full(m, np.nan)
    orh = orl = np.nan
    est = taken = False
    sf, tm = float(p["stop_frac"]), float(p["target_mult"])
    for i in range(m):
        if hr[i] == 9 and mn[i] == 30:
            orh = orl = np.nan
            est = taken = False
        if wd[i] in days:
            if hr[i] == 9 and 30 <= mn[i] < 45:
                orh = hv[i] if np.isnan(orh) else max(orh, hv[i])
                orl = lv[i] if np.isnan(orl) else min(orl, lv[i])
            if hr[i] == 9 and mn[i] == 45 and not np.isnan(orh) and not np.isnan(orl):
                est = True
            if est and not np.isnan(orh) and not np.isnan(orl) and hr[i] < 12 and not taken:
                stop = sf * (orh - orl)
                if cv[i] > orh:
                    le[i], l_sl[i], tgt[i], taken = True, orh - stop, tm * stop, True
                if cv[i] < orl:
                    se[i], s_sl[i], tgt[i], taken = True, orl + stop, tm * stop, True
        if hr[i] == 16 and mn[i] == 0:
            xa[i] = True
    idx = c.index
    S = lambda a: pd.Series(a, index=idx)  # noqa: E731
    return S(le), S(se), S(xa), S(l_sl), S(s_sl), S(tgt)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, xa, l_sl, s_sl, _ = _plan(bars_df, p)
    o = bars_df["open"]
    lf, sf = le.shift(1, fill_value=False), se.shift(1, fill_value=False)
    lx = (lf & (l_sl.shift(1) >= o)) | xa      # marketable stop at the fill: closed one bar late
    sx = (sf & (s_sl.shift(1) <= o)) | xa
    return le, lx & ~le & ~se, se, sx & ~se & ~le


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, _, l_sl, s_sl, tgt = _plan(bars_df, p)
    o = bars_df["open"]
    lf = le.shift(1, fill_value=False)
    sl = (1 - l_sl.shift(1) / o).where(lf, s_sl.shift(1) / o - 1)
    tp = tgt.shift(1) / o
    return {"sl_stop": sl.where(sl > 0), "tp_stop": tp.where(tp > 0)}


def portfolio_kwargs(**params):
    return {}
