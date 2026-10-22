"""Twenty candlestick patterns (doji star, grave and dragonfly dojis, hammer, hanging man, reversed hammer, falling star, absorptions, tweezers, three inside, three soldiers / crows, golden / death crosses, morning / evening stars) judged against an EMA 6, daily bars: bullish patterns go long, bearish ones short; reversing.
Port of FMZ strategy #471720 "Multi Level Moving Average with Candlestick Pattern Recognition Trading System" (hazed candles).

FMZ source id: 471720

Source
    https://www.fmz.com/strategy/471720 (PineScript v5, FMZ last modified 2024-11-12 16:39:22).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 131-361), EMA 6 trend; size ratios 10 / 9; SMA 50 / 200 crosses; every pattern switch on
    each bullish pattern -> entry "Buy <pattern>";  each bearish pattern -> entry "Sell <pattern>"  (twenty calls in a fixed order)

Interpretation choices (Pine rules in SURVEY_README.md)
    * All patterns are coded as written, including exact equality of prices (open == high, low ==
      close, matching lows / highs) and high_body_prop used as a truth value (non-zero). With the
      default pyramiding of 1 a further same-side entry does nothing; when patterns of both sides fire
      on one bar the later call in the source's order wins (#437773). There is no exit: positions end
      at the opposite entry. REVERSAL INTENDED. No sizing code. FREQ = "1D" from the backtest header
      (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, candlestick patterns against an EMA trend.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (2 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_471720_twenty_candle_patterns_ema6_reversal"
FAMILY = "candle_pattern"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ema_input": [6, 20],
}
DEFAULT_PARAMS = {"ema_input": 6}


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
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    e = c.ewm(span=int(p["ema_input"]), adjust=False).mean()
    o1, o2, o3 = o.shift(1), o.shift(2), o.shift(3)
    c1, c2, c3 = c.shift(1), c.shift(2), c.shift(3)
    h1, h2, l1, l2 = h.shift(1), h.shift(2), lo.shift(1), lo.shift(2)
    bar_size_h = h - c
    bar_size_l = (o - c).abs()
    body = h - lo
    low_prop, high_prop = c - lo, h - c
    low_half = (low_prop > body / 2.5) & (low_prop < body / 1.65)
    oc_eq = bar_size_l < body / 9
    star_up = (c <= e) & oc_eq & (high_prop != 0) & low_half
    star_dn = (c > e) & oc_eq & (high_prop != 0) & low_half
    grave = (c > e) & oc_eq & ((c - lo) < body / 9) & (high_prop > bar_size_l * 10)
    dragon = (c <= e) & oc_eq & ((h - c) < body / 9) & (low_prop > bar_size_l * 10)
    b_low, b_high = c - bar_size_h * 15, c - bar_size_h * 1.5
    t_low, t_high = o + bar_size_l * 1.5, o + bar_size_l * 15
    hammer = (e > c) & (o == h) & (lo > b_low) & (lo < b_high)
    hanging = (e < c) & (o == h) & (lo > b_low) & (lo < b_high)
    r_hammer = (e > o) & (lo == c) & (h > t_low) & (h < t_high)
    f_star = (e < c) & (lo == c) & (h > t_low) & (h < t_high)
    bar1, bar2 = (o1 - c1).abs(), (o2 - c2).abs()
    bar = (o - c).abs()
    big = bar > bar1 * 1.2
    abs_up = big & (o1 > c1) & (o1 != o) & (o3 > o2) & (o2 > o1) & (o1 > o) & (c > o)
    abs_dn = big & (o1 < c1) & (o1 != o) & (o3 < o2) & (o2 < o1) & (o1 < o) & (c < o)
    m_lows = (l1 == lo) | ((l2 == lo) & (o2 == o1))
    tw_up = (e > o) & m_lows & (o3 > o2) & (o2 > o1) & (o1 > o) & (lo != o) & (c1 != l1)
    m_highs = (h1 == h) | ((h2 == h) & (o2 == o1))
    tw_dn = (e <= o) & m_highs & (o3 < o2) & (o2 < o1) & (o1 < o) & (h != o) & (c1 != h1)
    mn0, mx0 = np.minimum(c, o), np.maximum(c, o)
    mn1, mx1 = np.minimum(c1, o1), np.maximum(c1, o1)
    mn2, mx2 = np.minimum(c2, o2), np.maximum(c2, o2)
    sized = (bar1 > bar2 * 0.4) & (bar1 < bar2 * 0.6) & (bar > bar1) & (bar + bar1 < bar2 * 2)
    ti_up = (mn2 == mn1) & sized & (c > o2)
    ti_dn = (mx2 == mx1) & sized & (c < o2)
    even = (bar > bar1 * 0.8) & (bar < bar1 * 1.2) & (bar > bar2 * 0.8) & (bar < bar2 * 1.2)
    soldiers = (e > o2) & even & (c > c1) & (c1 > c2) & (o2 < c2) & (o1 < c1)
    crows = (e < o2) & even & (c < c1) & (c1 < c2) & (o2 > c2) & (o1 > c1)
    m50, m200 = c.rolling(50).mean(), c.rolling(200).mean()
    cross = ((m50 > m200) & (m50.shift(1) <= m200.shift(1))) | ((m50 < m200) & (m50.shift(1) >= m200.shift(1)))
    golden, death = cross & (m50 > m200), cross & (m50 < m200)
    star_base = (bar > bar1) & (bar2 > bar1) & (bar > bar2 * 0.5) & (c2 != c1) & (o != c) & (o2 != c2)
    morning = (star_base & (mn2 > mn1) & (mn0 > mn1) & (e > c2) & (e > c1) & (c > c1) & (c3 > c2)
               & (c2 > c1) & (c > mx1))
    evening = (star_base & (mx2 < mx1) & (mx0 < mx1) & (e < c2) & (e < c1) & (c < c1) & (c3 < c2)
               & (c2 < c1) & (c < mn1))
    calls = [(star_up, 1), (star_dn, -1), (grave, -1), (dragon, 1), (hammer, 1), (hanging, -1),
             (r_hammer, 1), (f_star, -1), (abs_up, 1), (abs_dn, -1), (tw_up, 1), (tw_dn, -1),
             (ti_up, 1), (ti_dn, -1), (soldiers, 1), (crows, -1), (golden, 1), (death, -1),
             (morning, 1), (evening, -1)]
    d = np.zeros(len(c))
    for cond, side in calls:                    # the source's call order: the later call wins
        d = np.where(cond.to_numpy(), side, d)
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(d == 1, index=ix), false, pd.Series(d == -1, index=ix), false.copy()


def portfolio_kwargs(**params):
    return {}
