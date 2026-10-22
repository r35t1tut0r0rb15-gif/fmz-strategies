"""Bollinger 20 / 2 band crossings confirmed by the RSI 14, daily bars: the close crossing under the lower band with the RSI under 30 goes long, crossing over the upper band with the RSI over 70 goes short; reversing. The 2 % / 4 % bracket is re-sent every bar from the latest close and is not ported (pending).
Port of FMZ strategy #458171 "布林带RSI中性市场量化交易策略Bollinger-Bands-RSI-Neutral-Market-Quantitative-Trading-Strategy" (Neutral Market Strategy with Bollinger Bands and RSI).

FMZ source id: 458171

Source
    https://www.fmz.com/strategy/458171 (PineScript v5, FMZ last modified 2024-07-30 15:47:49).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 194-242), BB 20, 2 sd; RSI 14, levels 30 / 70; stop 2 %, target 4 % of the current close
    crossunder(close, lowerBB) and rsi < 30 -> entry Buy;  crossover(close, upperBB) and rsi > 70 -> entry Sell;  every bar: exit(Buy / Sell, limit = close x (1 +- 0.04), stop = close x (1 -+ 0.02))

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is re-sent on every bar from that bar's close, so its levels move after entry: stops()
      cannot express a level re-set every bar, so it is described here and kept pending (as #438034,
      mark trailing_stop_pending). Positions end at the opposite entry until then. REVERSAL INTENDED. No
      sizing code. FREQ = "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, band crossings with RSI confirmation; per-bar bracket described (pending).
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent bracket inputs stored.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_458171_bb20_band_cross_rsi_confirm_reversal"
FAMILY = "bollinger_reversion"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "bb_len": [20, 50],
    "bb_mult": [2.0, 1.5],
    "rsi_len": [14, 7],
}
DEFAULT_PARAMS = {"bb_len": 20, "bb_mult": 2.0, "rsi_len": 14}


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
    n, k = int(p["bb_len"]), float(p["bb_mult"])
    basis = c.rolling(n).mean()
    dev = k * c.rolling(n).std(ddof=0)
    lower, upper = basis - dev, basis + dev
    r = _rsi(c, int(p["rsi_len"]))
    le = (c < lower) & (c.shift(1) >= lower.shift(1)) & (r < 30)
    se = (c > upper) & (c.shift(1) <= upper.shift(1)) & (r > 70)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
