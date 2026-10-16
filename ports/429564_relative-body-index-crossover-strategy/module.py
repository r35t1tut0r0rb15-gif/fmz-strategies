"""Relative body index crosses, broker days: the RBI (EMA 5 of the 5-bar sum of body / range) crossing above its
EMA 5 signal while below zero goes long, crossing below it while above zero goes short; each trade has a small
stop and a tight trailing take-profit.
Port of FMZ strategy #429564 "Relative Body Index Crossover Strategy" (RBI Backtest /w TSSL).

FMZ source id: 429564

Source
    https://www.fmz.com/strategy/429564 (PineScript v3, FMZ last modified 2023-10-18 11:16:53).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 196-249), RBI 5 / signal 5, thresholds 0, stop 300 ticks, trail 120 points / offset 1
    yn = ema(sum((close - open) / (high - low), 5), 5); sig = ema(yn, 5)
    crossover(yn, sig) and yn < 0 -> entry long; crossover(sig, yn) and yn > 0 -> entry short
    exit("Exit", loss = 300, trail_points = 120, trail_offset = 1) for any entry; exit("Exit", when = ...) with no levels

Interpretation choices (Pine rules in SURVEY_README.md)
    * Criterion 2: on daily BTC (0.1 tick, ATR about 1000 USD) the 300-tick stop is about 0.03 ATR, the
      trail activates after 120 ticks (12 USD, about 0.0005 of the price) and trails 1 tick behind the best
      price (about 0.0001 ATR). Ported: sl_atr x Wilder ATR(14) of the signal bar (shifted, re-based) and the
      house trail {"type": "volatility", "atr_n": 14, "k": 0.0001, "anchor": "high_low", "activate_after":
      0.0005} (stated approximation of the tick offsets; mark trailing_stop).
    * The exit calls with only `when` place no order. The binary RBI option is off. The date window is
      dropped (startTimeOk is true).
    * strategy.entry reverses. Stop module: portfolio_kwargs {} (driver D4); REVERSAL INTENDED. Stops on
      1-day bars: mark coarse_bar_stop. Daily bars are broker days (17:00 America/New_York), stamped with
      their first minute. FREQ = "1D" from the backtest header (period 1d).

Admission criteria
    1 fits the interface: PASS, bar-close orders; stop fixed at entry; the trail is a house trail (approximation stated).
    2 generic: ADAPT, tick distances -> ATR multiples / a fraction.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the strategy() 100 % of equity and slippage stored; the exits quoted in original_sizing.txt.
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

NAME = "fmz_429564_relative_body_index"
FAMILY = "candle_pattern"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "par1": [5, 10],
    "sl_atr": [0.03, 1.0],
}
DEFAULT_PARAMS = {"par1": 5, "par2": 5, "thr_long": 0.0, "thr_short": 0.0, "sl_atr": 0.03, "trail_k": 0.0001,
                  "trail_activate": 0.0005, "atr_length": 14}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    t = int(p["par1"])
    s = (c - o) / (h - lo).replace(0.0, np.nan)
    yn = s.rolling(t).sum().ewm(span=t, adjust=False).mean()
    sig = yn.ewm(span=int(p["par2"]), adjust=False).mean()
    long_e = ((yn > sig) & (yn.shift(1) <= sig.shift(1)) & (yn < p["thr_long"])).astype(bool)
    short_e = ((sig > yn) & (sig.shift(1) <= yn.shift(1)) & (yn > p["thr_short"])).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    frac = _rma(tr, int(p["atr_length"])) / c
    return {"sl_stop": (p["sl_atr"] * frac).shift(1),
            "trail": {"type": "volatility", "atr_n": int(p["atr_length"]), "k": float(p["trail_k"]),
                      "anchor": "high_low", "activate_after": float(p["trail_activate"])}}


def portfolio_kwargs(**params):
    return {}
