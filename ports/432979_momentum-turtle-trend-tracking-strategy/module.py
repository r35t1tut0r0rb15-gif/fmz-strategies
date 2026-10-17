"""Daily Heikin Ashi colour with a rate-of-change filter, 1-hour bars: while the last completed broker day's Heikin Ashi
candle is green and the EMA 15 of the 30-bar rate of change is beyond +/- 3.5 %, the strategy is long (red: short),
reversing on the opposite condition; each position carries a 2 % stop from the entry price (the 5000 % target never
fills).
Port of FMZ strategy #432979 "Momentum Turtle Trend Tracking Strategy" (Heiken Ashi BF).

FMZ source id: 432979

Source
    https://www.fmz.com/strategy/432979 (PineScript v4, FMZ last modified 2023-11-23 11:53:27).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 149-213), HA daily open / close, ROC 30, pcntChange 7, stop 2 %, target 5000 %
    long = haOpen < haClose and |ema(roc(close, 30), 15)| > 7 / 2;  short = haOpen > haClose and the same filter
    strategy.entry L when long;  strategy.entry S when short;  exit(stop = avg (1 -/+ 2 %), limit = avg (1 +/- 5000 %))

Interpretation choices (Pine rules in SURVEY_README.md)
    * security(heikinashi, 'D', ...) without lookahead is read as the last completed daily bar
      (SURVEY_README: higher timeframes from completed higher bars), built from the port's own bars on
      broker days (17:00 America/New_York): HA close = ohlc4, HA open = the average of the previous HA
      open and close (seeded with (open + close) / 2).
    * long and short are levels: the entries fire on every bar they hold, and a repeated entry in the
      same direction is ignored (pyramiding 1), so after a stop the next bar with the condition
      re-enters, as in the source. The stop is sl_stop 0.02 of the fill; the source arms it from the
      bar after the signal (barssince > 0), and vbt does not test stops on the entry bar either. The
      target (50 x the price) is dropped as unreachable.
    * strategy.entry reverses: REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4). The
      date window is always true. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; daily values from completed broker days; fixed-percent stop.
    2 generic: PASS, candle colour and a percent rate of change.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the strategy() 100 % of equity and the commission stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND430880 (3 members, best partner #430880, Jaccard 0.698); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: daily values on broker days (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_432979_daily_ha_roc_filter"
FAMILY = "heikin_ashi_trend"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "roc_len": [30, 60],
    "sl_pct": [0.02, 0.04],
}
DEFAULT_PARAMS = {"roc_len": 30, "pcnt_change": 7.0, "sl_pct": 0.02}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _daily_ha(bars_df):
    """Heikin Ashi open and close of the last completed broker day, on every bar of the next one."""
    day = broker_day(bars_df.index)
    g = pd.DataFrame({k: bars_df[k].to_numpy() for k in ("open", "high", "low", "close")}, index=day)
    d = g.groupby(level=0).agg({"open": "first", "high": "max", "low": "min", "close": "last"})
    ha_c = ((d["open"] + d["high"] + d["low"] + d["close"]) / 4).to_numpy()
    ov, cv = d["open"].to_numpy(), d["close"].to_numpy()
    ha_o = np.empty(len(d))
    for j in range(len(d)):
        ha_o[j] = (ov[j] + cv[j]) / 2 if j == 0 else (ha_o[j - 1] + ha_c[j - 1]) / 2
    ho = pd.Series(ha_o, index=d.index).shift(1).reindex(day).to_numpy()
    hc = pd.Series(ha_c, index=d.index).shift(1).reindex(day).to_numpy()
    return pd.Series(ho, index=bars_df.index), pd.Series(hc, index=bars_df.index)


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    n = int(p["roc_len"])
    roc = 100 * (c - c.shift(n)) / c.shift(n)
    emaroc = roc.ewm(span=n / 2, adjust=False).mean()
    half = float(p["pcnt_change"]) / 2
    moving = (emaroc > half) | (emaroc < -half)
    ho, hc = _daily_ha(bars_df)
    le = ((ho < hc) & moving).astype(bool)
    se = ((ho > hc) & moving).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["sl_pct"])}


def portfolio_kwargs(**params):
    return {}
