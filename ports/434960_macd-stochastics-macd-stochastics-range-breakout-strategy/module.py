"""Slow MACD side with stochastic crosses, broker days: with the MACD 180 / 390 above its EMA 135 signal, the stochastic %K
14 crossing above 30 goes long; with the MACD below its signal, %K crossing below 70 goes short (reversing); each trade
takes profit 3 % from the fill.
Port of FMZ strategy #434960 "MACD-Stochastics波段震荡突破策略MACD-Stochastics-Range-Breakout-Strategy" (macd stoch strategy).

FMZ source id: 434960

Source
    https://www.fmz.com/strategy/434960 (PineScript v5, FMZ last modified 2023-12-11 11:48:27).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 223-292), MACD 180 / 390 / 135 (EMA); stoch 14 / 1 / 3; long and short TP 3 %
    macd > signal and crossover(k, 30) -> entry long;  macd < signal and crossunder(k, 70) -> entry short
    position long -> exit(limit = avg (1 + 3 %));  short -> exit(limit = avg (1 - 3 %))

Interpretation choices (Pine rules in SURVEY_README.md)
    * The target uses the fill price: tp_stop 0.03 on both sides (no stop). Pine arms it from the
      bar after the fill (approximation stated). strategy.entry reverses: REVERSAL INTENDED. Stop
      module: portfolio_kwargs {} (driver D4). Stops on daily bars: mark coarse_bar_stop. Daily bars
      are broker days (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from
      the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; fixed-percent target.
    2 generic: PASS, MACD side and stochastic crosses.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_434960_slow_macd_stoch_cross_tp"
FAMILY = "stochastic_oscillator"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "k_len": [14, 7],
    "tp_pct": [0.03, 0.06],
}
DEFAULT_PARAMS = {"fast": 180, "slow": 390, "signal": 135, "k_len": 14, "k_smooth": 1, "tp_pct": 0.03}


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
    macd = c.ewm(span=int(p["fast"]), adjust=False).mean() - c.ewm(span=int(p["slow"]), adjust=False).mean()
    sig = macd.ewm(span=int(p["signal"]), adjust=False).mean()
    n = int(p["k_len"])
    ll, hh = lo.rolling(n).min(), h.rolling(n).max()
    k = (100 * (c - ll) / (hh - ll).replace(0.0, np.nan)).rolling(int(p["k_smooth"])).mean()
    le = ((macd > sig) & (k > 30) & (k.shift(1) <= 30)).astype(bool)
    se = ((macd < sig) & (k < 70) & (k.shift(1) >= 70)).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"tp_stop": float(p["tp_pct"])}


def portfolio_kwargs(**params):
    return {}
