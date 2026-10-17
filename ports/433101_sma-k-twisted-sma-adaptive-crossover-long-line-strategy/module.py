"""Stacked SMA 4 / 9 / 18 longs above the SMA 100, broker days, long only: with SMA 4 > SMA 9 > SMA 18, the close above
the SMA 100 and a self-powered adaptive average that is not flat (it moved by 0.1 % or more since the previous bar), a
long opens; SMA 4 < SMA 9 < SMA 18 closes it.
Port of FMZ strategy #433101 "三重SMA自适应K线交叉长线策略Twisted-SMA-Adaptive-Crossover-Long-Line-Strategy" (twisted SMA strategy [4h]).

FMZ source id: 433101

Source
    https://www.fmz.com/strategy/433101 (PineScript v5, FMZ last modified 2023-11-24 14:26:37).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 180-221), SMA 4 / 9 / 18, main SMA 100, adaptive length 25, self powered on
    er = |change(close, 25)| / sum(|change(close)|, 25);  per = er ^ (1 / er);  a = per close + (1 - per) nz(a[1], close)
    a_f = 0.999 < a / a[1] < 1.001;  long_cond = sma4 > sma9 > sma18 and sma100 < close and not a_f -> entry long
    sma4 < sma9 < sma18 -> close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * The adaptive average is transcribed as written (an efficiency ratio raised to its own inverse);
      when the ratio is undefined (no movement) the weight is undefined and the next bar restarts from
      the close (nz). The title's "4h" is not the header's period: FREQ = "1D" from the backtest header.
    * Long only; Opposite entries cannot occur. Daily bars are broker days (17:00 America/New_York),
      stamped with their first minute.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, average order and an efficiency ratio.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the strategy() 100 % of equity and the commission stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND433101 (2 members, best partner #436491, Jaccard 0.715); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only. Opposite entries cannot occur.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_433101_twisted_sma_adaptive_long"
FAMILY = "ma_trend"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "main_len": [100, 50],
    "ad_len": [25, 50],
}
DEFAULT_PARAMS = {"len1": 4, "len2": 9, "len3": 18, "main_len": 100, "ad_len": 25}


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
    c = bars_df["close"]
    s1, s2, s3 = (c.rolling(int(p[k])).mean() for k in ("len1", "len2", "len3"))
    sm = c.rolling(int(p["main_len"])).mean()
    n = int(p["ad_len"])
    with np.errstate(invalid="ignore", divide="ignore"):
        er = (c.diff(n).abs() / c.diff().abs().rolling(n).sum()).to_numpy()
        per = np.power(er, 1 / er)
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    a = np.full(m, np.nan)
    for i in range(m):
        prev_a = a[i - 1] if i > 0 and not np.isnan(a[i - 1]) else cv[i]
        a[i] = per[i] * cv[i] + (1 - per[i]) * prev_a
    a1 = np.concatenate(([np.nan], a[:-1]))
    with np.errstate(invalid="ignore", divide="ignore"):
        flat = (a / a1 > 0.999) & (a / a1 < 1.001)
    long_ma = ((s1 > s2) & (s2 > s3)).to_numpy()
    short_ma = ((s1 < s2) & (s2 < s3)).to_numpy()
    ent = long_ma & (sm < c).to_numpy() & ~flat
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if pos == 0 and ent[i]:
            pos = 1
        elif pos == 1 and short_ma[i]:
            pos = 0
        tgt[i] = pos
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return (pd.Series((tgt == 1) & (prev == 0), index=ix), pd.Series((prev == 1) & (tgt == 0), index=ix),
            false, false.copy())


def portfolio_kwargs(**params):
    return {}
