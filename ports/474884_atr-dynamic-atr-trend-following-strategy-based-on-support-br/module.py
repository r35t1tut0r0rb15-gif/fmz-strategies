"""EMA 50 / 200 trend outside consolidation, daily bars: while the 20-bar range is at least 2 ATR and EMA 50 is over EMA 200 it goes long, under it goes short; reversing. The 2 ATR / 6 ATR bracket re-sent every bar from that bar's close is not ported (pending).
Port of FMZ strategy #474884 "基于支撑位突破的动态ATR趋势跟踪策略-Dynamic-ATR-Trend-Following-Strategy-Based-on-Support-Breakout" (Smart Money Concept Strategy).

FMZ source id: 474884

Source
    https://www.fmz.com/strategy/474884 (PineScript v5, FMZ last modified 2024-12-12 17:26:00).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 99-175), EMA 50 / 200; ATR 14; consolidation = 20-bar range under 2 ATR; stop 2 ATR, target 6 ATR from the current close; risk-based lot size
    not consolidating: bull -> entry Buy (lot), exit(stop = close - 2 atr, limit = close + 6 atr);  bear -> entry Sell, exit(stop = close + 2 atr, limit = close - 6 atr)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The entries and the bracket are re-sent on every non-consolidating bar from that bar's close, so
      the levels move after entry: a level re-set every bar is not ported (as #438034, mark
      trailing_stop_pending). Positions end at the opposite entry until then. The order-block and
      imbalance helpers feed only commented drawings. The risk-based size is not ported. REVERSAL
      INTENDED. FREQ = "1D" from the backtest header (broker days).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMA trend states with a consolidation filter; per-bar bracket described (pending).
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: risk-based lot size stored, not ported.
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

NAME = "fmz_474884_ema50_200_trend_outside_consolidation_reversal_bracket_pending"
FAMILY = "ma_trend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ema_short": [50, 20],
    "ema_long": [200, 100],
}
DEFAULT_PARAMS = {"ema_short": 50, "ema_long": 200, "atr_len": 14}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    atr = _atr(bars_df, p["atr_len"])
    consol = (h.rolling(20).max() - lo.rolling(20).min()) / atr < 2
    a = c.ewm(span=int(p["ema_short"]), adjust=False).mean()
    b = c.ewm(span=int(p["ema_long"]), adjust=False).mean()
    free = ~consol & atr.notna()
    le = free & (a > b)
    se = free & (a < b)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
