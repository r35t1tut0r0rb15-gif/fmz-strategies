"""A "snake line" (average of an ADX-like value, stochastic RSI x 100 and CCI 14) crossing its 100-bar range levels,
always in the market, daily (broker-day) bars: the line crossing above 20 % of its 100-bar range goes long; crossing
below 80 % of the range goes short.
Port of FMZ strategy #483038 "多重技术指标动态交叉趋势识别策略-Dynamic-Multi-Indicator-Trend-Recognition-Strategy-with-Triple-Sync-Analysis" (Triple Sync Strategy).

FMZ source id: 483038

Source
    https://www.fmz.com/strategy/483038 (PineScript v6, FMZ last modified 2025-02-21 10:31:53).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 93-134), base period 14, dynamic lookback 100
    dmi+ = rma(max(change(high), 0), 14), dmi- = rma(max(-change(low), 0), 14), dx = |dmi+ - dmi-| / (sum) x 100,
    adx = rma(dx, 14); stochRsi = (rsi - lowest rsi 14) / (highest - lowest); cci = ta.cci(close, 14)
    snake = (adx + 100 stochRsi + cci) / 3; lower = min + 0.2 range, upper = min + 0.8 range over 100 bars
    long = crossover(snake, lower): close short, entry long; short = crossunder(snake, upper): mirrored

Interpretation choices (Pine rules in SURVEY_README.md)
    * The DMI is the source's own (no up / down move comparison), as written. ta.cci = (close - SMA) / (0.015 x mean
      absolute deviation).
    * close + entry is a reversal: only the entries are emitted (REVERSAL INTENDED); no exits, no stops.
    * Daily bars are broker days (17:00 America/New_York) stamped with their first minute (as #430984). FREQ = "1D"
      from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, oscillators and their own rolling range.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing in the source (strategy() defaults).
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_483038_snake_line_range_cross_reversal"
FAMILY = "oscillator_cross"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [14, 21],
    "dyn_len": [100, 50],
}
DEFAULT_PARAMS = {"length": 14, "dyn_len": 100}


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
    r = 100 - 100 / (1 + up / dn)
    r = r.where(up != 0, 0.0)
    return r.where(dn != 0, 100.0).where(up.notna() & dn.notna())


def _cci(c, n):
    sma = c.rolling(n).mean()
    mad = c.rolling(n).apply(lambda w: np.abs(w - w.mean()).mean(), raw=True)
    return (c - sma) / (0.015 * mad)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["length"])
    dp = _rma(h.diff().clip(lower=0), n)
    dm = _rma((-lo.diff()).clip(lower=0), n)
    adx = _rma((dp - dm).abs() / (dp + dm) * 100, n)
    rsi = _rsi(c, n)
    rl, rh = rsi.rolling(n).min(), rsi.rolling(n).max()
    srsi = (rsi - rl) / (rh - rl)
    snake = (adx + srsi * 100 + _cci(c, n)) / 3
    w = int(p["dyn_len"])
    sh, sl = snake.rolling(w).max(), snake.rolling(w).min()
    lower, upper = sl + (sh - sl) * 0.2, sl + (sh - sl) * 0.8
    long_e = ((snake > lower) & (snake.shift(1) <= lower.shift(1))).astype(bool)
    short_e = ((snake < upper) & (snake.shift(1) >= upper.shift(1))).astype(bool)
    long_e = (long_e & ~short_e).astype(bool)          # both on one bar: the later short entry wins
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def portfolio_kwargs(**params):
    return {}
