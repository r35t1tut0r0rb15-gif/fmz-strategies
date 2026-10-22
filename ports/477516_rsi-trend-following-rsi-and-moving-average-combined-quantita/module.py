"""Close on one side of the SMA 50 with RSI 14 past 55 / 45, broker days: above the SMA with RSI over 55 goes long, below with RSI under 45 goes short, each with a 1 % stop and 2 % target from the entry price; reversing.
Port of FMZ strategy #477516 "趋势跟踪型RSI与移动平均线组合量化交易策略-Trend-Following-RSI-and-Moving-Average-Combined-Quantitative-Trading-Strategy" (RSI + MA Trend Strategy (v6)).

FMZ source id: 477516

Source
    https://www.fmz.com/strategy/477516 (PineScript v6, FMZ last modified 2025-01-06 10:58:42).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 95-189), SMA 50; RSI 14, 55 / 45; stop 1 %, target 2 % of strategy.position_avg_price; qty 1, capital 50000
    close > sma50 and rsi > 55 -> entry RSI MA Long;  close < sma50 and rsi < 45 -> entry RSI MA Short;  in a position: exit(stop = avg x (1 -/+ 1 %), limit = avg x (1 +/- 2 %))

Interpretation choices (Pine rules in SURVEY_README.md)
    * The conditions are states, so an entry repeats on every bar they hold; it is ignored while that
      side is held and re-enters on the next such bar after a bracket exit. The bracket is sent from the
      position's average price while it is held: a scalar fraction of the entry fill, active from the
      fill (as #440797). REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4). Stops on daily
      bars: mark coarse_bar_stop. The fixed qty 1 and capital are sizing. Daily bars are broker days
      (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; avg-price bracket as fractions of the fill.
    2 generic: PASS, SMA side with RSI thresholds and a percent bracket.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: qty 1 and capital 50000 stored, not ported.
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

NAME = "fmz_477516_sma50_side_rsi55_45_pct_bracket_reversal"
FAMILY = "rsi_oscillator"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "ma_length": [50, 100],
    "tp_pct": [0.02, 0.04],
}
DEFAULT_PARAMS = {"ma_length": 50, "tp_pct": 0.02, "sl_pct": 0.01, "rsi_length": 14, "buy_level": 55, "sell_level": 45}


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


def _rma(x, n):
    """Wilder smoothing as Pine's rma: SMA seed over the first n valid values, then recursive."""
    v = x.to_numpy(dtype=float)
    out = np.full(v.shape, np.nan)
    valid = np.flatnonzero(~np.isnan(v))
    if len(valid) >= n:
        s = valid[0]
        out[s + n - 1] = v[s:s + n].mean()
        for i in range(s + n, len(v)):
            out[i] = (out[i - 1] * (n - 1) + v[i]) / n
    return pd.Series(out, index=x.index)


def _rsi(c, n):
    d = c.diff()
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    return 100 - 100 / (1 + up / dn)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    ma = c.rolling(int(p["ma_length"])).mean()
    r = _rsi(c, int(p["rsi_length"]))
    le = (c > ma) & (r > float(p["buy_level"]))
    se = (c < ma) & (r < float(p["sell_level"]))
    false = pd.Series(False, index=c.index)
    return le, false, se, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["sl_pct"]), "tp_stop": float(p["tp_pct"])}


def portfolio_kwargs(**params):
    return {}
