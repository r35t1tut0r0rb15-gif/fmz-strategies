"""RSI against its SMA 50 with a CCI side, broker days: RSI 14 above its SMA 50 with the CCI 14 of hl2 above zero goes (or
stays) long; RSI under its SMA with the CCI under zero goes short (reversing); each signal also closes the other side.
Port of FMZ strategy #435245 "Moving Average Crossover and Reversal Indicator Combination Strategy" (MA RSI CCI).

FMZ source id: 435245

Source
    https://www.fmz.com/strategy/435245 (PineScript v4, FMZ last modified 2023-12-13 15:20:20).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 145-190), RSI 14, SMA 50 of RSI; CCI 14 on hl2; price filters computed but unused
    isCrossover = rsi > sma(rsi, 50) and cci(hl2, 14) > 0 -> entry long, close short;  isCrossunder = rsi < sma(rsi, 50) and cci < 0 -> entry short, close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The "price_up / price_down" filters only appear in commented-out orders: unused. The states
      hold until the opposite one. strategy.entry reverses: REVERSAL INTENDED. The fixed quantity 1 is
      sizing. Daily bars are broker days (17:00 America/New_York), stamped with their first minute.
      FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, RSI and CCI states.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the fixed quantity 1 stored.
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

NAME = "fmz_435245_rsi_sma_cci_side"
FAMILY = "rsi_oscillator"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rsi_ma": [50, 20],
    "cci_len": [14, 28],
}
DEFAULT_PARAMS = {"rsi_len": 14, "rsi_ma": 50, "cci_len": 14}


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
    ch = c.diff()
    n = int(p["rsi_len"])
    up = ch.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    dn = (-ch.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    rsi = (100 - 100 / (1 + up / dn)).where(dn != 0, 100.0).where(up.notna())
    rs = rsi.rolling(int(p["rsi_ma"])).mean()
    hl2 = (h + lo) / 2
    k = int(p["cci_len"])
    md = hl2.rolling(k).apply(lambda a: np.mean(np.abs(a - a.mean())), raw=True)
    cci = (hl2 - hl2.rolling(k).mean()) / (0.015 * md.replace(0.0, np.nan))
    lc, sc = ((rsi > rs) & (cci > 0)).to_numpy(), ((rsi < rs) & (cci < 0)).to_numpy()
    m = len(lc)
    tgt = np.zeros(m, dtype=np.int8)
    q = 0
    for i in range(m):
        if lc[i]:
            q = 1
        elif sc[i]:
            q = -1
        tgt[i] = q
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return (pd.Series((tgt == 1) & (prev != 1), index=ix), false,
            pd.Series((tgt == -1) & (prev != -1), index=ix), false.copy())


def portfolio_kwargs(**params):
    return {}
