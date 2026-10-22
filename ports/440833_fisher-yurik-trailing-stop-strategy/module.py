"""Fisher (Yurik) rises, broker days, long only: the Fisher transform (period 2) above zero and rising goes long; a trailing exit that activates about 7 % above the signal close and trails almost nothing
behind the best price closes.
Port of FMZ strategy #440833 "Fisher Yurik Trailing Stop Strategy" (FY Strategy).

FMZ source id: 440833

Source
    https://www.fmz.com/strategy/440833 (PineScript v5, FMZ last modified 2024-02-02 14:57:33).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 132-179), period 2; profit level 1.05; after the signal 1.02; trail offset 0.08 (ticks); dates from 2021 (window is true)
    Value = 0.66 ((hl2 - lowest(low, 2)) / (highest(high, 2) - lowest(low, 2)) - 0.5) + 0.67 Value[1] (clamped);  Fish = 0.5 ln((1 + Value) / (1 - Value)) + 0.5 Fish[1]
    ExtBuffer1 (Fish >= 0) rising -> entry Buy, entryPrice = close x 1.02, stopPrice = close x 1.05;  strategy.exit(when = close >= entryPrice x 1.05 or close < stopPrice, trail_price = entryPrice x 1.05, trail_offset = 0.08)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The exit is sent on almost every bar (its stopPrice test sits 5 % above the signal close) and
      trails 0.08 ticks (about 2e-7 of the price on BTC) once the price reaches 1.02 x 1.05 = 1.071 x the
      latest signal close. The port uses the house trail {"type": "percent", "pct": 2e-7, "anchor":
      "high_low", "activate_after": 0.071} from the fill (stated approximation, as #437390; mark
      trailing_stop); later signals that move the activation level are not followed. Long only. Stop
      module: portfolio_kwargs {} (driver D4). Stops on 1-day bars: mark coarse_bar_stop. No sizing code.
      Daily bars are broker days (17:00 America/New_York), stamped with their first minute. FREQ = "1D"
      from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the trail is a house trail (approximation stated).
    2 generic: ADAPT, tick trail -> house trail.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only.

Marks: trailing_stop, coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_440833_fisher_yurik_rise_trail_exit"
FAMILY = "momentum_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "period": [2, 10],
    "activate": [0.071, 0.03],
}
DEFAULT_PARAMS = {"period": 2, "activate": 0.071, "trail_pct": 2e-7}


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


def _fisher(bars_df, n):
    h, lo = bars_df["high"], bars_df["low"]
    price = ((h + lo) / 2).to_numpy(dtype=float)
    mx, mn = h.rolling(n).max().to_numpy(), lo.rolling(n).min().to_numpy()
    m = len(price)
    fish = np.full(m, np.nan)
    v_p = f_p = np.nan
    for i in range(m):
        rng = mx[i] - mn[i]
        raw = 0.33 * 2 * ((price[i] - mn[i]) / rng - 0.5) if rng > 0 else np.nan
        v = raw + 0.67 * (0.0 if np.isnan(v_p) else v_p)
        if not np.isnan(v):
            v = max(min(v, 0.999), -0.999)
        f = 0.5 * np.log((1 + v) / (1 - v)) + 0.5 * (0.0 if np.isnan(f_p) else f_p) if not np.isnan(v) else np.nan
        fish[i] = f
        v_p, f_p = v, f
    return pd.Series(fish, index=bars_df.index)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    f = _fisher(bars_df, int(p["period"]))
    b1 = f.where(f >= 0)
    buy = b1 > b1.shift(1)
    false = pd.Series(False, index=bars_df.index)
    return buy, false, false.copy(), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"trail": {"type": "percent", "pct": float(p["trail_pct"]), "anchor": "high_low",
                      "activate_after": float(p["activate"])}}


def portfolio_kwargs(**params):
    return {}
