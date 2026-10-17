"""Closes crossing above a 50-bar Kaufman adaptive average with MACD (26 / 52 / 18) above its signal go long, closed
at the bearish mirror, with a 3 ATR stop and target, long only, daily bars.
Port of FMZ strategy #482779 "基于KAMA与MACD的自适应趋势跟踪量化交易策略-Adaptive-Trend-Following-Strategy-Based-on-KAMA-and-MACD-Integration" (4-Hour KAMA Strategy).

FMZ source id: 482779

Source
    https://www.fmz.com/strategy/482779 (PineScript v5, FMZ last modified 2025-02-20 15:01:37).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 108-141), KAMA 50 (fast 3, slow 30), ATR 14 x 3, MACD 26 / 52 / 18
    ER = |close - close[50]| / sum(|close - close[1]|, 50); sc = (ER (2/4 - 2/31) + 2/31)^2
    kama = na(kama[1]) ? close : kama[1] + sc (close - kama[1])
    crossover(close, kama) and macd > signal -> entry long; crossunder(close, kama) and macd < signal -> close long
    every bar: exit(stop = close - 3 ATR, limit = close + 3 ATR)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The KAMA recursion is kept as written, including its warm-up (na and close alternate until the efficiency
      ratio exists).
    * The bracket is re-issued every bar from the current close and ATR (a moving level): fixed at the entry as
      3 ATR / close of the signal bar, shifted one bar inside stops() and re-based on the fill; mark
      trailing_stop_pending.
    * Entries and closes cannot fall on one bar; a close while flat does nothing. Long only. Stop module:
      portfolio_kwargs {} (D4). Daily bars are broker days (17:00 America/New_York), stamped with their first
      minute; FREQ = "1D" from the backtest header (the title's "4-Hour" is not the backtest period).

Admission criteria
    1 fits the interface: PASS, bar-close orders; the moving bracket fixed at entry (marked).
    2 generic: PASS, an adaptive average, MACD and ATR multiples.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 10 % of equity; the bracket via stops(), quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Opposite entries cannot occur (long only).

Marks: coarse_bar_stop, trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_482779_kama_cross_macd_atr_bracket_long"
FAMILY = "trend_following"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "ama_len": [50, 20],
    "atr_mult": [3.0, 2.0],
}
DEFAULT_PARAMS = {"ama_len": 50, "fast": 3, "slow": 30, "atr_len": 14, "atr_mult": 3.0}


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
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]   # Pine's first true range is high - low
    return _rma(tr, n)


def _kama(c, n, fast, slow):
    er = ((c - c.shift(n)).abs() / c.diff().abs().rolling(n).sum()).to_numpy()
    f, s = 2 / (fast + 1), 2 / (slow + 1)
    sc = (er * (f - s) + s) ** 2
    v = c.to_numpy(dtype=float)
    out = np.full(len(v), np.nan)
    for i in range(len(v)):
        prev = out[i - 1] if i > 0 else np.nan
        out[i] = v[i] if np.isnan(prev) else prev + sc[i] * (v[i] - prev)
    return pd.Series(out, index=c.index)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    kama = _kama(c, int(p["ama_len"]), int(p["fast"]), int(p["slow"]))
    macd = c.ewm(span=26, adjust=False).mean() - c.ewm(span=52, adjust=False).mean()
    sig = macd.ewm(span=18, adjust=False).mean()
    long_e = ((c > kama) & (c.shift(1) <= kama.shift(1)) & (macd > sig)).astype(bool)
    long_x = ((c < kama) & (c.shift(1) >= kama.shift(1)) & (macd < sig)).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, long_x, false, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    sl = (p["atr_mult"] * _atr(bars_df, int(p["atr_len"])) / bars_df["close"]).shift(1)
    return {"sl_stop": sl, "tp_stop": sl}


def portfolio_kwargs(**params):
    return {}
