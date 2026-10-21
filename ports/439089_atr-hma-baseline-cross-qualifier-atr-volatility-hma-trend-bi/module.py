"""Closes beyond an SMA 20 baseline by half an ATR with a Hull 50 bias, broker days: a close above the baseline by at least 0.5 ATR(14) and above the Hull MA, with the low 3 bars ago above the baseline, goes
long; the mirror (with the same low test) goes short; reversing. The bracket at the baseline +- 1 ATR is re-sent every bar and is not ported (pending).
Port of FMZ strategy #439089 "基于ATR波动性与HMA趋势偏差的双均线突破策略Baseline-Cross-Qualifier-ATR-Volatility-HMA-Trend-Bias-Mean-Reversion-Strategy" (Baseline Cross Qualifier Volatility Strategy with HMA Trend Bias).

FMZ source id: 439089

Source
    https://www.fmz.com/strategy/439089 (PineScript v5, FMZ last modified 2024-01-17 16:37:23).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 122-186), baseline SMA 20; qualifier on, 3 bars ago; ATR 14, range 1, qualifier 0.5; one take profit; HMA 50
    isLong = close > baseline and close - baseline >= 0.5 atr and close > hma 50;  isShort mirror;  pbcqValid = low[3] > baseline;  isLong and valid -> entry Long;  isShort and valid -> entry Short
    every bar: exit(Long, limit = baseline + atr, stop = baseline - atr), exit(Short, limit = baseline - atr, stop = baseline + atr)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The qualifier tests low[3] > baseline for both sides, as written. The bracket is re-sent on every
      bar from the current baseline and ATR, so its levels move after entry: stops() cannot express a
      level re-set every bar, so it is described and kept pending (as #437036, mark trailing_stop_pending).
      Positions end at the opposite entry until then. The Hull MA uses floor(n / 2) and round(sqrt(n)).
      strategy.entry reverses: REVERSAL INTENDED. No sizing code. Daily bars are broker days (17:00
      America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, baseline distance, Hull bias; per-bar bracket described (pending).
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_439089_baseline_qualifier_hma_bias"
FAMILY = "ma_trend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "baseline_len": [20, 50],
    "qualifier_mult": [0.5, 1.0],
}
DEFAULT_PARAMS = {"baseline_len": 20, "qualifier_mult": 0.5, "atr_len": 14, "hma_len": 50, "bars_ago": 3}


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


def _wma(x, n):
    w = np.arange(1, n + 1, dtype=float)
    return x.rolling(n).apply(lambda a: np.dot(a, w) / w.sum(), raw=True)


def _hma(x, n):
    return _wma(2 * _wma(x, n // 2) - _wma(x, n), int(np.floor(np.sqrt(n) + 0.5)))


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    base = c.rolling(int(p["baseline_len"])).mean()
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    atr = _rma(tr, int(p["atr_len"]))
    q = float(p["qualifier_mult"]) * atr
    hma = _hma(c, int(p["hma_len"]))
    valid = lo.shift(int(p["bars_ago"])) > base
    up = (c > base) & ((c - base) >= q) & (c > hma) & valid
    dn = (c < base) & ((base - c) >= q) & (c < hma) & valid
    false = pd.Series(False, index=c.index)
    return up, false, dn, false.copy()


def portfolio_kwargs(**params):
    return {}
