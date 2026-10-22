"""Bollinger 20 / 2.5 and RSI 14 extremes, daily bars: an RSI under 25 with the close at or under the lower band goes long, an RSI over 75 with the close at or over the upper band goes short; reversing. The 5 % target re-sent every bar from the latest close is not ported (pending).
Port of FMZ strategy #473153 "基于布林带和RSI的动态成本平均策略系统-Dynamic-Cost-Averaging-Strategy-System-Based-on-Bollinger-Bands-and-RSI" (BB RSI Combined DCA Strategy).

FMZ source id: 473153

Source
    https://www.fmz.com/strategy/473153 (PineScript v5, FMZ last modified 2024-11-27 16:37:12).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 131-227), BB 20, 2.5 sd; RSI 14, 25 / 75; target 5 % of the current close; "DCA" size 1 % of equity (unused); profit and 3-month labels
    rsi < 25 and close <= lower -> entry DCA Buy;  rsi > 75 and close >= upper -> entry DCA Sell
    long: exit(limit = close x 1.05);  short: exit(limit = close x 0.95)  (every bar)

Interpretation choices (Pine rules in SURVEY_README.md)
    * Despite the "DCA" name the entries use the default pyramiding of 1, so nothing is added while
      held, and the size input is never used. The target is re-sent on every bar from that bar's close,
      so its level moves after entry: stops() cannot express a level re-set every bar, so it is kept
      pending (as #438034, mark trailing_stop_pending); positions end at the opposite entry until then.
      The profit and market-change labels are drawing only. REVERSAL INTENDED. No sizing code. FREQ =
      "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, band and RSI extremes; per-bar target described (pending).
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the unused percent-of-equity size stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_473153_bb20_2p5_rsi25_75_extremes_reversal"
FAMILY = "bollinger_reversion"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "length": [20, 50],
    "mult": [2.5, 2.0],
}
DEFAULT_PARAMS = {"length": 20, "mult": 2.5, "rsi_len": 14}


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
    n = int(p["length"])
    basis = c.rolling(n).mean()
    dev = float(p["mult"]) * c.rolling(n).std(ddof=0)
    r = _rsi(c, int(p["rsi_len"]))
    le = (r < 25) & (c <= basis - dev)
    se = (r > 75) & (c >= basis + dev)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
