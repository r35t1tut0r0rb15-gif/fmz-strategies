"""UT Bot trailing-line crosses filtered by an EMA 26 / 50 spread, broker days: a close crossing above the UT Bot line
(3 x ATR 10) with the spread rising and under 25 price units goes long; a close crossing below it with the spread falling
and above 75 goes short (reversing). The spread levels are re-expressed as ATR multiples.
Port of FMZ strategy #434687 "Trend and Moving Average Crossover Based Multi Functional Algorithmic Trading Strategy" (OB+LQ+UTSTC+SMA+EMA-NORA-MIP21-Jashore-Bangladesh-OneMinuteTF).

FMZ source id: 434687

Source
    https://www.fmz.com/strategy/434687 (PineScript v4, FMZ last modified 2023-12-08 12:14:50).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 162-256), UT Bot key 3, ATR 10; "STC" = EMA 26 - EMA 50 with levels 25 / 75; order-block / liquidity lines, SMAs and EMA 5 plotted only
    trail = close > trail[1] and close[1] > trail[1] ? max(trail[1], close - 3 atr) : close < trail[1] and close[1] < trail[1] ? min(trail[1], close + 3 atr) : close > trail[1] ? close - 3 atr : close + 3 atr
    crossover(close, trail) and stc < 25 and stc > stc[1] -> entry long;  crossunder(close, trail) and stc > 75 and stc < stc[1] -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The UT Bot line is the strategy's signal line on closes (not a broker stop). The order-block
      and liquidity signals are plotted only (never traded).
    * Criterion 2: "STC" here is an EMA spread in price units compared with 25 and 75. On daily BTC
      those are about 0.025 and 0.075 x the daily Wilder ATR 10 in 2023; the port compares the spread
      with those ATR multiples.
    * strategy.entry reverses: REVERSAL INTENDED. Daily bars are broker days (17:00
      America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: ADAPT, price-unit spread levels -> ATR multiples.
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

NAME = "fmz_434687_ut_bot_ema_spread"
FAMILY = "volatility_stop_cross"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "key": [3.0, 1.5],
    "lvl_scale": [1.0, 20.0],
}
DEFAULT_PARAMS = {"key": 3.0, "atr_len": 10, "fast": 26, "slow": 50, "lo_atr": 0.025, "hi_atr": 0.075,
                  "lvl_scale": 1.0}


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
    c1 = c.shift(1)
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1)
    tr.iloc[0] = np.nan
    atr = tr.ewm(alpha=1 / int(p["atr_len"]), adjust=False).mean().to_numpy()
    nl = float(p["key"]) * atr
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    ts = np.full(m, np.nan)
    for i in range(m):
        t1 = ts[i - 1] if i > 0 and not np.isnan(ts[i - 1]) else 0.0     # nz(trail[1], 0)
        cp = cv[i - 1] if i > 0 else np.nan
        if cv[i] > t1 and cp > t1:
            ts[i] = max(t1, cv[i] - nl[i])
        elif cv[i] < t1 and cp < t1:
            ts[i] = min(t1, cv[i] + nl[i])
        else:
            ts[i] = cv[i] - nl[i] if cv[i] > t1 else cv[i] + nl[i]
    ts1 = np.concatenate(([np.nan], ts[:-1]))
    stc = (c.ewm(span=int(p["fast"]), adjust=False).mean() - c.ewm(span=int(p["slow"]), adjust=False).mean())
    sv, s1 = stc.to_numpy(), stc.shift(1).to_numpy()
    sc_ = float(p["lvl_scale"])
    lo_l, hi_l = float(p["lo_atr"]) * sc_ * atr, float(p["hi_atr"]) * sc_ * atr
    c1v = np.concatenate(([np.nan], cv[:-1]))
    with np.errstate(invalid="ignore"):
        le = (cv > ts) & (c1v <= ts1) & (sv < lo_l) & (sv > s1)
        se = (cv < ts) & (c1v >= ts1) & (sv > hi_l) & (sv < s1)
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, pd.Series(se, index=ix), false.copy()


def portfolio_kwargs(**params):
    return {}
