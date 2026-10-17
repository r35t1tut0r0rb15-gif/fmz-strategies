"""CCI 20 turns from under -150, long only, broker days: the CCI rising after a bar below -150, on a bar closing more than
0.25 % above its open, goes long; the CCI above +150 closes it, and so does a close 8 % below the fill price.
Port of FMZ strategy #432225 "CCI强势突破策略CCI-Strong-Breakthrough-Strategy" (CCI High Performance long only).

FMZ source id: 432225

Source
    https://www.fmz.com/strategy/432225 (PineScript v5, FMZ last modified 2023-11-15 16:52:06).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 222-262), CCI 20, bands -150 / +150, signal-bar filter 0.25 %, stop 8 %
    cci = (close - sma(close, 20)) / (0.015 x dev(close, 20))
    cci[1] < -150 and cci > cci[1] and close > open x (1 + 0.25 %) -> entry long
    cci > 150 -> close long;  close < avg price x (1 - 8 %) -> close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The 8 % stop is checked on the close (strategy.close): rule 3, a close-based exit signal from
      simulate(), not sl_stop. The fill price is the open of the bar after the entry signal; from
      that bar on, a close below it by 8 % closes the trade. ta.dev is the mean absolute deviation
      from the window's mean (current bar included).
    * A signal while long is an ignored add, and the closes act on the position held at the bar's
      start. The window() inputs (2016 to 2112) are the author's backtest range: dropped. Long only;
      Opposite entries cannot occur. Daily bars are broker days (17:00 America/New_York), stamped
      with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; close-checked stop.
    2 generic: PASS, CCI bands and percentages of the open / fill.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code; the close-checked stop quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only. Opposite entries cannot occur.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_432225_cci_turn_long"
FAMILY = "momentum_oscillator_turn"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [20, 14],
    "loss_pct": [8.0, 4.0],
}
DEFAULT_PARAMS = {"length": 20, "loss_pct": 8.0, "scart": 0.25, "upper": 150, "lower": -150}


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
    o, c = bars_df["open"], bars_df["close"]
    n = int(p["length"])
    ma = c.rolling(n).mean()
    dev = c.rolling(n).apply(lambda a: float(np.mean(np.abs(a - a.mean()))), raw=True)
    cci = (c - ma) / (0.015 * dev)
    le = ((cci.shift(1) < float(p["lower"])) & (cci > cci.shift(1))
          & (c > o * (1 + float(p["scart"]) / 100))).to_numpy()
    tgt_x = (cci > float(p["upper"])).to_numpy()
    ov, cv = o.to_numpy(dtype=float), c.to_numpy(dtype=float)
    lp = float(p["loss_pct"]) / 100
    m = len(cv)
    tgt = np.zeros(m, dtype=np.int8)
    pos, e_i = 0, -1
    for i in range(m):
        start = pos
        if start == 1 and (tgt_x[i] or cv[i] < ov[e_i] * (1 - lp)):   # in position from the fill bar e_i
            pos = 0
        if start == 0 and le[i]:
            pos, e_i = 1, i + 1
        tgt[i] = pos
    prev = np.concatenate(([0], tgt[:-1]))
    l_e = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    false = np.zeros(m, dtype=bool)
    return tuple(pd.Series(a, index=bars_df.index) for a in (l_e, lx, false, false.copy()))


def portfolio_kwargs(**params):
    return {}
