"""RSI 20 with the rate of change of a retro-weighted MA 20, broker days: the RSI at or above 60 with the MA down at least
1 % over 20 bars goes long; the RSI at or below 40 with the MA up at least 1 % goes short; a 3 ATR stop from the signal
close and a 3 % trail that starts once the trade is well in profit (house stop and trail).
Port of FMZ strategy #432330 "RSI趋势跟踪策略RSI-Trend-Following-Strategy" (RSI + MA BACKTESTING).

FMZ source id: 432330

Source
    https://www.fmz.com/strategy/432330 (PineScript v5, FMZ last modified 2023-11-16 15:33:40).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 154-336), RSI 20, RWMA 20, ROC thresholds -1 / +1, ATR 20, stop 3 ATR, trail activation 4 ATR, trail 3 %
    rwma(x, 20) = sum(x[i] x w_i) / sum(w_i), w = 100 / (4 + 16 x 1.3) for i <= 3, 1.3 times that after; roc = (ma / ma[20] - 1) x 100
    rsi >= 60 and roc <= -1 and not long -> entry long, exit(stop = close - 3 atr, trail_price = close + 4 atr, trail_offset = 3 % of it)
    rsi <= 40 and roc >= 1 and not short -> entry short, mirror

Interpretation choices (Pine rules in SURVEY_README.md)
    * The stop is 3 ATR(20) from the signal close: sl_atr x ATR / close of the signal bar, shifted one
      bar inside stops() and re-based on the fill. The trail is ported natively (mark trailing_stop):
      {"type": "percent", "pct": 0.03, "anchor": "high_low", "activate_after": a}. Stated
      approximations: Pine starts trailing once the price reaches close + 4 ATR (about 12 % on daily
      BTC) and trails 3 % of that activation price; here it starts after a gain of a (0.12 in the
      grid with 0.06) and trails 3 % of the best price.
    * The script's long / short flags and its drawn stop only mirror the orders (not long = not
      already in a long). The fixed-ratio money management is sizing (criterion 4). inRange is
      always true. The ROC thresholds (-1 long, +1 short) are used as written.
    * strategy.entry reverses: REVERSAL INTENDED. Daily bars are broker days (17:00 America/New_York),
      stamped with their first minute; stops on daily bars: mark coarse_bar_stop. Stop module:
      portfolio_kwargs {} (driver D4). FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; stop fixed at entry; the trail is a house trail (approximation stated).
    2 generic: PASS, RSI levels, MA rate of change, ATR stop and percentage trail.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the fixed-ratio order amounts and the commission stored in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: DG432330 (2 members, best partner #436501, Jaccard 0.910); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: trailing_stop, coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_432330_rsi_rwma_roc_trail"
FAMILY = "rsi_oscillator"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "activate": [0.12, 0.06],
    "sl_atr": [3.0, 1.5],
}
DEFAULT_PARAMS = {"rsi_len": 20, "ma_len": 20, "rsi_long": 60, "rsi_short": 40, "roc_long": -1.0, "roc_short": 1.0,
                  "atr_len": 20, "sl_atr": 3.0, "trail_pct": 0.03, "activate": 0.12}


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


def _rwma(x, n):
    """The source's retro-weighted MA: the 4 newest values weigh 1 / 1.3 of the older ones."""
    wx = 100 / (4 + (n - 4) * 1.30)
    w = np.array([wx * 1.30 if lag > 3 else wx for lag in range(n - 1, -1, -1)])   # oldest ... newest
    v = x.to_numpy(dtype=float)
    out = np.full(len(v), np.nan)
    if len(v) >= n:
        win = np.lib.stride_tricks.sliding_window_view(v, n)
        out[n - 1:] = win @ w / w.sum()
    return pd.Series(out, index=x.index)


def _rsi(x, n):
    d = x.diff()
    up = d.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    dn = (-d.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    return 100 - 100 / (1 + up / dn)


def _atr_frac(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    c1 = c.shift(1)
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1)
    return tr.ewm(alpha=1 / n, adjust=False).mean() / c


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    r = _rsi(c, int(p["rsi_len"]))
    n = int(p["ma_len"])
    ma = _rwma(c, n)
    roc = (ma / ma.shift(n) - 1) * 100
    le = ((r >= float(p["rsi_long"])) & (roc <= float(p["roc_long"]))).astype(bool)
    se = ((r <= float(p["rsi_short"])) & (roc >= float(p["roc_short"]))).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    af = _atr_frac(bars_df, int(p["atr_len"]))
    return {"sl_stop": (af * float(p["sl_atr"])).shift(1),
            "trail": {"type": "percent", "pct": float(p["trail_pct"]), "anchor": "high_low",
                      "activate_after": float(p["activate"])}}


def portfolio_kwargs(**params):
    return {}
