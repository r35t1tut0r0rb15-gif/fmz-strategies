"""Ichimoku signals with counters, broker days, long only: a close crossing the Kijun (SMA of hl2, 26) while the Kijun moves
(new 6-bar high or low) together with the close above both cloud lines, or a close crossing above the close 26 bars ago
within 8 bars of the last bearish condition, goes long; the bearish mirror closes it.
Port of FMZ strategy #434984 "Ichimoku Trend Following Strategy" (My Ichimoku Strat).

FMZ source id: 434984

Source
    https://www.fmz.com/strategy/434984 (PineScript v3, FMZ last modified 2023-12-11 15:00:29).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 144-220), Kijun / Tenkan / Senkou B as SMAs of hl2 (26 / 9 / 52); Kijun lag 6; dates 2017-9999
    buy2 = crossover(close, kijun) and (rising(kijun, 6) or falling(kijun, 6));  buy3 = close above both spans;  buy1 = crossover(close, close[26])
    buyCount: 1 on buy2 or buy3, +1 while positive, -1 on sell2 or sell3;  sellCount mirror
    buy = buy2 and buy3 or (buy1 and sellCount <= 8) -> entry long;  sell = sell2 and sell3 or (sell1 and buyCount <= 8) -> close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * rising / falling(x, 6) mean x above (below) all of its previous 6 values. The lines are the
      current SMAs (the offsets only shift the plots). The date window is the author's: dropped.
      Long only; an entry while long is ignored. Daily bars are broker days (17:00
      America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, Ichimoku lines and counters.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the strategy() 100 % of equity and capital stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND434984 (2 members, best partner #435948, Jaccard 0.687); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_434984_ichimoku_counters_long"
FAMILY = "ichimoku"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "kijun_lag": [6, 3],
    "count_max": [8, 4],
}
DEFAULT_PARAMS = {"kijun_lag": 6, "count_max": 8}


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
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    hl2 = (h + lo) / 2
    kij, ten, ssb = hl2.rolling(26).mean(), hl2.rolling(9).mean(), hl2.rolling(52).mean()
    ssa = (kij + ten) / 2
    lag = int(p["kijun_lag"])
    mv = (kij > kij.shift(1).rolling(lag).max()) | (kij < kij.shift(1).rolling(lag).min())
    b2 = ((c > kij) & (c.shift(1) <= kij.shift(1)) & mv).to_numpy()
    s2 = ((c < kij) & (c.shift(1) >= kij.shift(1)) & mv).to_numpy()
    b3 = ((c > ssa) & (c > ssb)).to_numpy()
    s3 = ((c < ssa) & (c < ssb)).to_numpy()
    c26 = c.shift(26)
    b1 = ((c > c26) & (c.shift(1) <= c26.shift(1))).to_numpy()
    s1 = ((c < c26) & (c.shift(1) >= c26.shift(1))).to_numpy()
    m, cm = len(c), int(p["count_max"])
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    bc = sc = -1
    pos = 0
    for i in range(m):
        if b2[i] or b3[i]:
            bc = 1
        if bc > 0:
            bc += 1
        if s2[i] or s3[i]:
            bc = -1
        if s2[i] or s3[i]:
            sc = 1
        if sc > 0:
            sc += 1
        if b2[i] or b3[i]:
            sc = -1
        sell = (s2[i] and s3[i]) or (s1[i] and bc <= cm)
        buy = (b2[i] and b3[i]) or (b1[i] and sc <= cm)
        if pos == 1 and sell:              # the close acts on the open long (a buy while long is ignored)
            lx[i], pos = True, 0
        elif pos == 0 and buy:             # flat: the entry fills; the same-bar close finds no position
            le[i], pos = True, 1
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def portfolio_kwargs(**params):
    return {}
