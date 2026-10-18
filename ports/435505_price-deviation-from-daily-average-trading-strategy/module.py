"""Ichimoku cloud trades with two entry types per side, broker days: a bullish stack (Tenkan over Kijun, positive 30-bar momentum, close
over the displaced cloud) opens "Long" and a bullish re-entry from under the cloud floor opens "Long e2e"; each closes by its own
rules; the bearish mirror opens "Short" / "Short e2e" (an opposite entry reverses). One trade per direction at a time.
Port of FMZ strategy #435505 "Price Deviation from Daily Average Trading Strategy" (Ichimoku Cloud).

FMZ source id: 435505

Source
    https://www.fmz.com/strategy/435505 (PineScript v5, FMZ last modified 2023-12-15 15:44:18).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 169-232), conversion 20, base 60, span B 120, displacement 30; long, short and e2e entries on
    tenkan, kijun = Donchian midpoints; ss_high / ss_low = max / min of the two spans 29 bars back;  bullish = tenkan > kijun and mom(close, 30) > 0 and close > ss_high;  bullishe2e = previous_close < ss_low[1] and close > ss_low
    entry "Long" (bullish), close "Long" (tenkan < kijun or previous_close > ss_high[1] and close < ss_high);  entry "Long e2e" (bullishe2e), close "Long e2e" (cross of close and ss_high, or close < ss_low);  shorts mirror

Interpretation choices (Pine rules in SURVEY_README.md)
    * strategy.close(id) closes only the trade with that id; the two long ids share the single
      long slot (pyramiding 1 lets one trade per direction stand), so a second long entry while one
      is open does nothing; an opposite entry reverses whatever is open. The orders are filled in
      the script's call order at the next open. The cloud is displaced 29 bars back: only past values
      are read. cross() is a crossing in either direction. The Chikou span is not used. REVERSAL
      INTENDED. Daily bars are broker days (17:00 America/New_York), stamped with their first minute.
      FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, cloud and line rules.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
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

NAME = "fmz_435505_ichimoku_two_entry_types"
FAMILY = "ichimoku"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "conversion": [20, 9],
    "base": [60, 26],
}
DEFAULT_PARAMS = {"conversion": 20, "base": 60, "span_b": 120, "displacement": 30}


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


def _cross(a, b):
    up = (a > b) & (a.shift(1) <= b.shift(1))
    dn = (a < b) & (a.shift(1) >= b.shift(1))
    return (up | dn).fillna(False).to_numpy()


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]

    def donchian(n):
        return (lo.rolling(n).min() + h.rolling(n).max()) / 2

    tenkan, kijun = donchian(int(p["conversion"])), donchian(int(p["base"]))
    span_a = (tenkan + kijun) / 2
    span_b = donchian(int(p["span_b"]))
    k = int(p["displacement"]) - 1
    ss_high = np.maximum(span_a.shift(k), span_b.shift(k))
    ss_low = np.minimum(span_a.shift(k), span_b.shift(k))
    prev_c = c.shift(1)
    mom = c - c.shift(int(p["displacement"]))
    bullish = ((tenkan > kijun) & (mom > 0) & (c > ss_high)).fillna(False).to_numpy()
    bearish = ((tenkan < kijun) & (mom < 0) & (c < ss_low)).fillna(False).to_numpy()
    bull_e2e = ((prev_c < ss_low.shift(1)) & (c > ss_low)).fillna(False).to_numpy()
    bear_e2e = ((prev_c > ss_high.shift(1)) & (c < ss_high)).fillna(False).to_numpy()
    tk_bear = (tenkan < kijun).fillna(False).to_numpy()
    tk_bull = (tenkan > kijun).fillna(False).to_numpy()
    enters_top = ((prev_c > ss_high.shift(1)) & (c < ss_high)).fillna(False).to_numpy()
    enters_bottom = ((prev_c < ss_low.shift(1)) & (c > ss_low)).fillna(False).to_numpy()
    touch_top, touch_bottom = _cross(c, ss_high), _cross(c, ss_low)
    below = (c < ss_low).fillna(False).to_numpy()
    above = (c > ss_high).fillna(False).to_numpy()
    m = len(bullish)
    held = np.zeros(m, dtype=np.int8)
    pos = 0                                    # 0 flat, 1 "Long", 2 "Long e2e", -1 "Short", -2 "Short e2e"
    pend = None
    for i in range(m):
        if i > 0 and pend is not None:
            e1, c1, e2, c2, e3, c3, e4, c4 = pend
            if e1 and pos <= 0:
                pos = 1
            if c1 and pos == 1:
                pos = 0
            if e2 and pos <= 0:
                pos = 2
            if c2 and pos == 2:
                pos = 0
            if e3 and pos >= 0:
                pos = -1
            if c3 and pos == -1:
                pos = 0
            if e4 and pos >= 0:
                pos = -2
            if c4 and pos == -2:
                pos = 0
        held[i] = 1 if pos > 0 else (-1 if pos < 0 else 0)
        pend = (bullish[i], tk_bear[i] or enters_top[i], bull_e2e[i], touch_top[i] or below[i],
                bearish[i], tk_bull[i] or enters_bottom[i], bear_e2e[i], touch_bottom[i] or above[i])
    nxt = np.concatenate((held[1:], held[-1:]))
    ix = bars_df.index
    return (pd.Series((nxt == 1) & (held != 1), index=ix), pd.Series((nxt == 0) & (held == 1), index=ix),
            pd.Series((nxt == -1) & (held != -1), index=ix), pd.Series((nxt == 0) & (held == -1), index=ix))


def portfolio_kwargs(**params):
    return {}
