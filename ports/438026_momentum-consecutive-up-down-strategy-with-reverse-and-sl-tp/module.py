"""Consecutive higher / lower closes, broker days: 3 higher closes in a row go long, 4 lower closes in a row go short (reversing); each trade has a stop 5 ATR 14 from the bar's ohlc4, a target 5 times the stop
distance, and a trailing stop that follows the high (the low for shorts).
Port of FMZ strategy #438026 "双向追Momentum止盈止损策略Consecutive-Up-Down-Strategy-with-Reverse-and-SL-TP-Extension" (Consecutive Up/Down Strategy with Reverse).

FMZ source id: 438026

Source
    https://www.fmz.com/strategy/438026 (PineScript v4, FMZ last modified 2024-01-08 11:58:21).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 162-278), direction all; bars up 3, bars down 4; stop type ATR (5 x ATR 14 from ohlc4), reward 5; trailing stop on; direct reverse on, reverse trades off
    BUY = ups >= 3 and bar_index > 40;  SELL = dns >= 4 and bar_index > 40 (ups / dns: consecutive closes above / below the previous close)
    SL = valuewhen(position changed, ohlc4 - 5 atr(14));  TP = avg + (avg - SL) x 5;  trailing: tstop = high - (avg - SL) - (fill-bar high - avg), never lowered;  exit(limit = TP, stop = tstop)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The script takes the ATR stop at the bar its position changes (the fill bar's close); the port
      takes it from the signal bar ((close - (ohlc4 - 5 ATR)) / close), shifted one bar inside stops()
      and re-based on the fill (as #434998): approximation stated. A signal whose stop is not beyond the
      close places no entry; the target is 5 times the stop fraction. The trailing stop keeps a fixed
      distance (fill-bar high - SL) under each new high; the port uses the house volatility trail
      (5 x ATR 14 under the best high, anchor high_low), which lets the distance follow the ATR: stated
      approximation (mark trailing_stop). The first 40 bars give no signal. strategy.entry reverses
      (direct reverse on): REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4). Stops on 1-day
      bars: mark coarse_bar_stop. The size, capital and commission are sizing / costs. Daily bars are
      broker days (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry; house trail.
    2 generic: PASS, close runs and ATR distances.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent-of-equity size, capital and commission stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND434998 (4 members, best partner #435256, Jaccard 0.783); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: coarse_bar_stop, trailing_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_438026_consecutive_closes_atr_trail"
FAMILY = "momentum_breakout"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "bars_up": [3, 2],
    "k_atr": [5.0, 3.0],
}
DEFAULT_PARAMS = {"bars_up": 3, "k_atr": 5.0, "bars_down": 4, "atr_len": 14, "rr": 5.0, "warmup": 40}


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


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    return _rma(tr, int(n))


def _setup(bars_df, p):
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    ups, dns = np.zeros(m), np.zeros(m)
    for i in range(1, m):
        ups[i] = ups[i - 1] + 1 if cv[i] > cv[i - 1] else 0.0
        dns[i] = dns[i - 1] + 1 if cv[i] < cv[i - 1] else 0.0
    late = np.arange(m) > int(p["warmup"])
    a = float(p["k_atr"]) * _atr(bars_df, p["atr_len"])
    ohlc4 = (o + h + lo + c) / 4.0
    sl_l = ((c - (ohlc4 - a)) / c).to_numpy()
    sl_s = (((ohlc4 + a) - c) / c).to_numpy()
    buy = (ups >= int(p["bars_up"])) & late & (sl_l > 0)
    sell = (dns >= int(p["bars_down"])) & late & (sl_s > 0)
    sl = np.where(buy, sl_l, np.where(sell, sl_s, np.nan))
    return buy, sell, sl


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    buy, sell, _ = _setup(bars_df, p)
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(buy, index=ix), false, pd.Series(sell, index=ix), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    _, _, sl = _setup(bars_df, p)
    s = pd.Series(sl, index=bars_df.index)
    return {"sl_stop": s.shift(1), "tp_stop": (float(p["rr"]) * s).shift(1),
            "trail": {"type": "volatility", "atr_n": int(p["atr_len"]), "k": float(p["k_atr"]),
                      "anchor": "high_low"}}


def portfolio_kwargs(**params):
    return {}
