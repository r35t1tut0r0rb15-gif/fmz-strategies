"""BEST trailing stop on 2-day bars: SMA 15 crossing above SMA 45 goes long, crossing below goes short;
once the trade has reached 2 % beyond the signal close, a 3 % ratchet line (on lows for longs, highs
for shorts) is armed, and a bar crossing it closes the position.
Port of FMZ strategy #427513 "Best Trailing Stop Strategy".

FMZ source id: 427513

Source
    https://www.fmz.com/strategy/427513 (PineScript v4, FMZ last modified 2023-09-21 20:58:22).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 182-330), SMA 15 / 45, trail 3 %, trigger 2 %
    buy_trend = barssince(short cross) > barssince(long cross) (sell_trend mirrors)
    entry_price = valuewhen(any cross, close, 0); trigger = entry x (1 +- 2 %)
    long trigger hit (sticky until a trend change) when buy_trend and high >= trigger
    longStop = buy_trend ? max(low x (1 - 3 %), longStop[1]) : 0   (short: min(high x 1.03, ...) : 999999)
    close long when buy_trend and crossunder(low, longStop[1]) and the trigger was hit (short mirrors)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The strategy() line is commented out (with calc_on_every_tick / calc_on_order_fills in it):
      Pine defaults apply, bar-close evaluation.
    * The trail is tested on each completed bar's low / high and the exit is a strategy.close (next
      open): a close-based exit signal (rule 2 second half), no stop order and no mark; the line
      ratchets on lows, which the house trail (best price) could not express anyway.
    * 2-day bars are built from broker days in fixed blocks of two broker-day dates counted from
      1970-01-01, as worker A's #426995 (block phase: decision owed).
    * strategy.entry reverses: REVERSAL INTENDED.
    * FREQ = "2D" from the backtest header (period 2d).

Admission criteria
    1 fits the interface: PASS, bar-close orders and bar-close exit tests.
    2 generic: PASS, MA lengths and percent distances (a trail as a fraction of price).
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: fixed qty / capital settings stored in original_sizing.txt.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_427513_best_trailing_stop_2d"
FAMILY = "ma_trend"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "2D"  # backtest header period: 2d (blocks of broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "trail_pct": [3.0, 6.0],
    "trigger_pct": [2.0, 4.0],
    "slow": [45, 30],
}
DEFAULT_PARAMS = {"fast": 15, "slow": 45, "trail_pct": 3.0, "trigger_pct": 2.0}


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


def _multiday(raw_1m_df, days):
    """Blocks of `days` broker-day dates counted from 1970-01-01 (as worker A's #426995), each stamped
    with the session start of its first broker day."""
    daily = _daily(raw_1m_df)
    day = broker_day(daily.index)
    key = np.asarray((day - pd.Timestamp("1970-01-01")).days // days)
    grouped = daily.assign(_key=key, _start=daily.index).groupby("_key", sort=True)
    bars = grouped.agg(open=("open", "first"), high=("high", "max"), low=("low", "min"),
                       close=("close", "last"), _start=("_start", "first"))
    return bars.set_index("_start").rename_axis(None)[["open", "high", "low", "close"]]


def _barssince(cond):
    out = np.full(len(cond), np.nan)
    last = -1
    for i, f in enumerate(cond):
        if f:
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
    c = bars_df["close"]
    f, s = c.rolling(int(p["fast"])).mean(), c.rolling(int(p["slow"])).mean()
    up = ((f > s) & (f.shift(1) <= s.shift(1))).to_numpy()
    dn = ((f < s) & (f.shift(1) >= s.shift(1))).to_numpy()
    sb, ss = _barssince(up), _barssince(dn)
    with np.errstate(invalid="ignore"):
        buy, sell = ss > sb, ss < sb
    hv, lv, cv = (bars_df[k].to_numpy(dtype=float) for k in ("high", "low", "close"))
    trail, trig = p["trail_pct"] / 100, p["trigger_pct"] / 100
    m = len(cv)
    tgt = np.zeros(m, dtype=np.int8)
    pos, entry_px = 0, np.nan
    hit_l = hit_s = False
    ls = np.zeros(m)
    shs = np.full(m, 999999.0)
    for i in range(m):
        if up[i] or dn[i]:
            entry_px = cv[i]
        trigger = entry_px * (1 + trig) if buy[i] else entry_px * (1 - trig)
        if buy[i] and hv[i] >= trigger:
            hit_l = True
        if sell[i] and lv[i] <= trigger:
            hit_s = True
        ls[i] = max(lv[i] * (1 - trail), ls[i - 1] if i else 0.0) if buy[i] else 0.0
        shs[i] = min(hv[i] * (1 + trail), shs[i - 1] if i else 999999.0) if sell[i] else 999999.0
        x_l = i >= 2 and lv[i] < ls[i - 1] and lv[i - 1] >= ls[i - 2]
        x_s = i >= 2 and hv[i] > shs[i - 1] and hv[i - 1] <= shs[i - 2]
        close_l = buy[i] and x_l and hit_l
        close_s = sell[i] and x_s and hit_s
        if up[i] and pos != 1:
            pos = 1
        elif dn[i] and pos != -1:
            pos = -1
        elif pos == 1 and close_l:
            pos = 0
        elif pos == -1 and close_s:
            pos = 0
        tgt[i] = pos
        if i and ((buy[i] and sell[i - 1]) or (sell[i] and buy[i - 1])):   # change_trend resets the triggers
            hit_l = hit_s = False
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
