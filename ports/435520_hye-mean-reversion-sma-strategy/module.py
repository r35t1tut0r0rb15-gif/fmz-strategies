"""Two-offset mean reversion, broker days: the SMA 2 crossing under a level 3 % under the SMA 5, with the RSI 2 average under 30, goes
long (closed when the SMA 2 crosses back over the SMA 5); the short side (crossing over a level 3 % over the SMA 5 with the RSI
average over 70, closed when the SMA 2 crosses under the SMA 5) is off by default.
Port of FMZ strategy #435520 "HYE Mean Reversion SMA Strategy" (HYE Mean Reversion SMA).

FMZ source id: 435520

Source
    https://www.fmz.com/strategy/435520 (PineScript v4, FMZ last modified 2023-12-15 16:51:23).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 190-239), SMA 2 / 5, 3 % offsets, RSI 2 with an EMA 5, levels 30 / 70; direction Long Only
    rsiEMA = ema(rsi(close, 2), 5);  buyMA = 0.97 sma(close, 5);  sellMA = 1.03 sma(close, 5)
    crossunder(sma(close, 2), buyMA) and rsiEMA < 30 -> entry long;  crossover(sma2, sma5) -> close long;  crossover(sma2, sellMA) and rsiEMA > 70 -> entry short (Both only);  crossunder(sma2, sma5) -> close short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The trade direction input (Long Only by default) is in the grid with "Both"; the date range
      inputs are the author's window (always true): dropped. Opposite entries reverse when both sides
      are on: REVERSAL INTENDED for "Both". Daily bars are broker days (17:00 America/New_York),
      stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, average offsets and an RSI filter.
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

NAME = "fmz_435520_hye_two_offset_mean_reversion"
FAMILY = "mean_reversion"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "direction": ["Long Only", "Both"],
    "pct_below": [3, 5],
}
DEFAULT_PARAMS = {"direction": "Long Only", "pct_below": 3, "pct_above": 3, "small": 2, "big": 5,
                  "rsi_len": 2, "rsi_buy": 30, "rsi_sell": 70}


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
    r = int(p["rsi_len"])
    ch = c.diff()
    up_ = ch.clip(lower=0).ewm(alpha=1 / r, adjust=False).mean()
    dn_ = (-ch.clip(upper=0)).ewm(alpha=1 / r, adjust=False).mean()
    rsi = (100 - 100 / (1 + up_ / dn_)).where(dn_ != 0, 100.0).where(up_.notna())
    rsi_ema = rsi.ewm(span=5, adjust=False).mean()
    small, big = c.rolling(int(p["small"])).mean(), c.rolling(int(p["big"])).mean()
    buy_ma = (100 - float(p["pct_below"])) / 100 * big
    sell_ma = (100 + float(p["pct_above"])) / 100 * big
    le = ((small < buy_ma) & (small.shift(1) >= buy_ma.shift(1)) & (rsi_ema < float(p["rsi_buy"]))).fillna(False)
    lx = ((small > big) & (small.shift(1) <= big.shift(1))).fillna(False)
    se = ((small > sell_ma) & (small.shift(1) <= sell_ma.shift(1)) & (rsi_ema > float(p["rsi_sell"]))).fillna(False)
    sx = ((small < big) & (small.shift(1) >= big.shift(1))).fillna(False)
    if p["direction"] == "Long Only":
        se = se & False
    return le.astype(bool), lx.astype(bool), se.astype(bool), sx.astype(bool)


def portfolio_kwargs(**params):
    return {}
