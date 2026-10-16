"""BEST trailing profit, 2-day bars: SMA 20 crossing above SMA 50 goes long, crossing below goes short.
Once price has reached 3 % beyond the signal close, a long is closed when the bar's high pushes above
the running "high + 1 %" ratchet (a short when the low breaks the "low - 1 %" ratchet).
Port of FMZ strategy #428583 "Best Trailing Take Profit Strategy" (Daveatt).

FMZ source id: 428583

Source
    https://www.fmz.com/strategy/428583 (PineScript v4, FMZ last modified 2023-10-07 10:28:54).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 170-370), SMA 20 / 50, trail 1 %, trigger 3 %
    crossover(sma20, sma50) -> entry long; crossunder -> entry short; buy_trend = barssince(sell) > barssince(buy)
    trigger = signal close x (1 +- 3 %); hitL := buy_trend and high >= trigger ? true : hitL[1] (reset on a trend change)
    longTrail = buy_trend ? max(high x 1.01, longTrail[1]) : 0; close long on crossover(high, longTrail[1]) and hitL
    shorts mirror (low x 0.99, min, 999999 when not in a sell trend)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The "trailing take profit" is a close signal on the bar's range (strategy.close: filled at the
      next open), as written; it fires when a high clears the previous ratchet.
    * barssince is na before the first event (both trends false until both crosses happened).
    * The strategy() lines are commented out: Pine defaults. REVERSAL INTENDED.
    * 2-day bars are blocks of broker days counted from 1970-01-01 (as worker A's 2-day ports),
      stamped with the session start. FREQ = "2D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, MA lengths and percentages.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the commented strategy() settings stored in original_sizing.txt.
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

NAME = "fmz_428583_best_trailing_profit_2d"
FAMILY = "ma_cross"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "2D"  # backtest header period: 2d (blocks of broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "trail_pct": [1.0, 2.0],
    "trigger_pct": [3.0, 5.0],
}
DEFAULT_PARAMS = {"fast": 20, "slow": 50, "trail_pct": 1.0, "trigger_pct": 3.0}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date. The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def _daily(raw_1m_df):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    if ohlc.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    bars = ohlc.groupby(broker_day(ohlc.index)).agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"}).dropna(how="all")
    start = (bars.index - pd.Timedelta(days=1) + pd.Timedelta(hours=17)).tz_localize("America/New_York")
    bars.index = start.tz_convert("UTC")  # each bar stamped with its session start
    return bars


def _multiday(raw_1m_df, weekly=False, days=1):
    """Multi-day bars built from broker days: calendar weeks (Monday-Sunday) of the broker-day
    dates when weekly, else blocks of `days` broker-day dates counted from 1970-01-01. Each bar
    is stamped with the session start of its first broker day."""
    daily = _daily(raw_1m_df)
    day = broker_day(daily.index)
    if weekly:
        key = np.asarray(day - pd.to_timedelta(day.weekday, unit="D"))
    else:
        key = np.asarray((day - pd.Timestamp("1970-01-01")).days // days)
    grouped = daily.assign(_key=key, _start=daily.index).groupby("_key", sort=True)
    bars = grouped.agg(open=("open", "first"), high=("high", "max"), low=("low", "min"),
                       close=("close", "last"), _start=("_start", "first"))
    return bars.set_index("_start").rename_axis(None)[["open", "high", "low", "close"]]


def _barssince(cond):
    out = np.full(len(cond), np.nan)
    last = -1
    for i, v in enumerate(cond):
        if v:
            last = i
        if last >= 0:
            out[i] = i - last
    return out


def _emit(tgt, index):
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=index) for a in (le, lx, se, sx))


def precompute(raw_1m_df, symbol_key, **params):
    return _multiday(raw_1m_df, days=2)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    f, s = c.rolling(int(p["fast"])).mean(), c.rolling(int(p["slow"])).mean()
    el = ((f > s) & (f.shift(1) <= s.shift(1))).to_numpy()
    es = ((f < s) & (f.shift(1) >= s.shift(1))).to_numpy()
    sb, ss = _barssince(el), _barssince(es)
    with np.errstate(invalid="ignore"):
        bt = ss > sb
        st = ss < sb
    hv, lv, cv = h.to_numpy(dtype=float), lo.to_numpy(dtype=float), c.to_numpy(dtype=float)
    tp, trig = p["trail_pct"] / 100, p["trigger_pct"] / 100
    m = len(cv)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    entry_px = np.nan
    hit_l = hit_s = False
    lt1 = lt2 = 0.0                       # longTrail[1], longTrail[2]
    st1 = st2 = 999999.0
    h1 = l1 = np.nan
    for i in range(m):
        if el[i] or es[i]:
            entry_px = cv[i]
        trigger = entry_px * (1 + trig) if bt[i] else entry_px * (1 - trig)
        if bt[i] and hv[i] >= trigger:
            hit_l = True
        if st[i] and lv[i] <= trigger:
            hit_s = True
        lt = max(hv[i] * (1 + tp), lt1) if bt[i] else 0.0
        sht = min(lv[i] * (1 - tp), st1) if st[i] else 999999.0
        close_l = bt[i] and hv[i] > lt1 and h1 <= lt2 and hit_l
        close_s = st[i] and lv[i] < st1 and l1 >= st2 and hit_s
        if el[i]:
            pos = 1
        elif es[i]:
            pos = -1
        elif pos == 1 and close_l:
            pos = 0
        elif pos == -1 and close_s:
            pos = 0
        tgt[i] = pos
        change = i > 0 and ((bt[i] and st[i - 1]) or (st[i] and bt[i - 1]))
        if change:
            hit_l = hit_s = False
        lt2, lt1, st2, st1 = lt1, lt, st1, sht
        h1, l1 = hv[i], lv[i]
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
