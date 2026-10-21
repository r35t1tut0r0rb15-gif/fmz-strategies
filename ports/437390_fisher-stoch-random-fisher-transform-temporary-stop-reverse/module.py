"""Inverse Fisher stochastic crossings with a tick trailing stop, broker days: the inverse-Fisher line of a 4-bar WMA of the 19-bar stochastic crossing over -0.62 goes long, crossing under 0.64 goes short,
reversing; each trade trails 20 ticks behind the best price once 245 ticks in profit (house trail).
Port of FMZ strategy #437390 "随机Fisher变换临时停止反转STOCH指标量化策略Random-Fisher-Transform-Temporary-Stop-Reverse-STOCH-Indicator-Quantitative-Strategy" (IFT Stochastic + Trailing Stop).

FMZ source id: 437390

Source
    https://www.fmz.com/strategy/437390 (PineScript v3, FMZ last modified 2024-01-02 11:14:12).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 159-193), stoch 19, smooth 4, levels 0.64 / -0.62; trailing stop on: activation 245, offset 20 (ticks)
    v2 = wma(0.1 (stoch(close, high, low, 19) - 50), 4);  INV = (exp(2 v2) - 1) / (exp(2 v2) + 1)
    buy = crossover(INV, -0.62) -> entry BUY;  sell = crossunder(INV, 0.64) -> entry SELL;  exit(trail_points = 245, trail_offset = 20) for both

Interpretation choices (Pine rules in SURVEY_README.md)
    * Criterion 2: on daily BTC (0.1 tick, ATR about 1000 USD near 40000) the trail activates after 245
      ticks (24.5 USD, about 0.0006 of the price) and trails 20 ticks (2 USD, about 0.002 ATR) behind the
      best price: the house trail {"type": "volatility", "atr_n": 14, "k": 0.002, "anchor": "high_low",
      "activate_after": 0.0006} (stated approximation, as #429564; mark trailing_stop). The entry calls are
      repeated in the script; one is ported. REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4).
      Stops on 1-day bars: mark coarse_bar_stop. The 100 % of equity size and commission are sizing. Daily
      bars are broker days (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the trail is a house trail (approximation stated).
    2 generic: ADAPT, tick trail -> ATR multiple and a fraction.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent-of-equity size, commission and the tick trail inputs stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: coarse_bar_stop, trailing_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_437390_inverse_fisher_stoch_trail"
FAMILY = "stochastic_oscillator"  # proposed 2026-10-21 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "stoch_len": [19, 14],
    "trail_k": [0.002, 1.0],
}
DEFAULT_PARAMS = {"stoch_len": 19, "trail_k": 0.002, "wma_len": 4, "ul": 0.64, "dl": -0.62, "atr_len": 14,
                  "trail_activate": 0.0006}


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


def _wma(x, n):
    w = np.arange(1, n + 1, dtype=float)
    return x.rolling(n).apply(lambda v: np.dot(v, w) / w.sum(), raw=True)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["stoch_len"])
    ll, hh = lo.rolling(n).min(), h.rolling(n).max()
    with np.errstate(divide="ignore", invalid="ignore"):
        st = 100.0 * (c - ll) / (hh - ll).where(hh > ll)
    v2 = _wma(0.1 * (st - 50), int(p["wma_len"]))
    e2 = np.exp(2 * v2)
    inv = (e2 - 1) / (e2 + 1)
    i1 = inv.shift(1)
    ul, dl = float(p["ul"]), float(p["dl"])
    buy = (inv > dl) & (i1 <= dl)
    sell = (inv < ul) & (i1 >= ul)
    false = pd.Series(False, index=bars_df.index)
    return buy, false, sell, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"trail": {"type": "volatility", "atr_n": int(p["atr_len"]), "k": float(p["trail_k"]),
                      "anchor": "high_low", "activate_after": float(p["trail_activate"])}}


def portfolio_kwargs(**params):
    return {}
