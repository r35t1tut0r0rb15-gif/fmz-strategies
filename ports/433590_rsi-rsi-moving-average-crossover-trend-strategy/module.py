"""RSI average crosses above a short EMA, broker days, long only: while the EMA 12 of the RSI 16 is above the SMA 29 of the
RSI and the close is above its EMA 8 the strategy goes long; the RSI EMA falling under the RSI SMA closes it.
Port of FMZ strategy #433590 "RSI均线交叉趋势策略RSI-Moving-Average-Crossover-Trend-Strategy" (Sv3nla RSI EMA SMA Strat).

FMZ source id: 433590

Source
    https://www.fmz.com/strategy/433590 (PineScript v4, FMZ last modified 2023-11-28 17:03:56).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 137-160), RSI 16, RSI EMA 12, RSI SMA 29, price EMA 8
    entry long when ema(rsi, 12) > sma(rsi, 29) and close > ema(close, 8);  close when ema(rsi, 12) < sma(rsi, 29)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The entry is a level (re-fired while it holds, ignored while long). Long only; Opposite entries
      cannot occur. The date window is always true. Daily bars are broker days (17:00
      America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, RSI averages and a price EMA.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the strategy() 100 % of equity stored.
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

NAME = "fmz_433590_rsi_ema_sma_long"
FAMILY = "rsi_oscillator"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rsi_len": [16, 8],
    "price_ema": [8, 21],
}
DEFAULT_PARAMS = {"rsi_len": 16, "rsi_ema": 12, "rsi_sma": 29, "price_ema": 8}


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
    ch = c.diff()
    n = int(p["rsi_len"])
    up = ch.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    dn = (-ch.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    r = (100 - 100 / (1 + up / dn)).where(up != 0, 0.0).where(dn != 0, 100.0).where(up.notna())
    re = r.ewm(span=int(p["rsi_ema"]), adjust=False).mean()
    rs = r.rolling(int(p["rsi_sma"])).mean()
    pe = c.ewm(span=int(p["price_ema"]), adjust=False).mean()
    ent = ((re > rs) & (c > pe)).to_numpy()
    ex = (re < rs).to_numpy()
    m = len(c)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    for i in range(m):
        if pos == 0 and ent[i]:
            pos = 1
        elif pos == 1 and ex[i]:
            pos = 0
        tgt[i] = pos
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return (pd.Series((tgt == 1) & (prev == 0), index=ix), pd.Series((prev == 1) & (tgt == 0), index=ix),
            false, false.copy())


def portfolio_kwargs(**params):
    return {}
