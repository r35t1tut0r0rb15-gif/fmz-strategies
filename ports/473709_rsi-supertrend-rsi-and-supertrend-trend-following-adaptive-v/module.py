"""Supertrend (2.76, ATR 12) flips with an RSI 12 filter, 3-day bars: the flip to an up-trend with RSI under 70 goes long, the flip to a down-trend with RSI over 30 goes short; reversing. The ATR bracket re-sent every bar from that bar's close is not ported (pending).
Port of FMZ strategy #473709 "RSI与Supertrend趋势跟踪型自适应波动策略-RSI-and-Supertrend-Trend-Following-Adaptive-Volatility-Strategy" (ETH Signal 15m).

FMZ source id: 473709

Source
    https://www.fmz.com/strategy/473709 (PineScript v5, FMZ last modified 2024-12-02 16:41:30).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 107-139), supertrend factor 2.76, ATR 12; RSI 12, 70 / 30; exits close -/+ 4 ATR and +/- 2 (2.237) ATR every bar
    change(direction) < 0 and rsi < 70 -> entry Long;  change(direction) > 0 and rsi > 30 -> entry Short;  every bar: exit(Long, stop = close - 4 atr, limit = close + 2 atr), exit(Short, stop = close + 4 atr, limit = close - 2.237 atr)

Interpretation choices (Pine rules in SURVEY_README.md)
    * Pine's supertrend direction -1 is the up-trend, so a fall in direction is the flip up. The exits
      are re-sent on every bar from that bar's close and ATR, so the levels move after entry: a level
      re-set every bar is not ported (as #438034, mark trailing_stop_pending). Positions end at the
      opposite entry until then. The date window is always true. REVERSAL INTENDED. No sizing code.
      FREQ = "3D" from the backtest header (blocks of 3 broker days, as #429148; the title's "15m" is
      not the header).

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, supertrend flips with an RSI filter; per-bar bracket described (pending).
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the ATR bracket stored.
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

NAME = "fmz_473709_supertrend_2p76_atr12_flip_rsi_filter_reversal"
FAMILY = "supertrend"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "3D"  # backtest header period: 3d (blocks of 3 broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "factor": [2.76, 4.0],
    "atr_period": [12, 24],
}
DEFAULT_PARAMS = {"factor": 2.76, "atr_period": 12, "rsi_len": 12, "days": 3}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def _multiday(raw_1m_df, days):
    """Blocks of `days` broker days counted from 1970-01-01, each stamped with its first minute."""
    df = raw_1m_df[["open", "high", "low", "close"]].dropna(how="all")
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    key = np.asarray((broker_day(df.index) - pd.Timestamp("1970-01-01")).days // days)
    bars = df.groupby(key).agg({"open": "first", "high": "max", "low": "min", "close": "last"})
    first = pd.Series(df.index, index=df.index).groupby(key).first()
    bars.index = pd.DatetimeIndex(first.loc[bars.index].values)
    if bars.index.tz is None:
        bars.index = bars.index.tz_localize("UTC")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    p = {**DEFAULT_PARAMS, **params}
    return _multiday(raw_1m_df, int(p["days"]))


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


def _supertrend(bars_df, factor, period):
    """ta.supertrend (Pine reference implementation): returns (line, direction), -1 = up-trend."""
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    atr = _rma(tr, period).to_numpy()
    src = ((h + lo) / 2).to_numpy()
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    lower, upper = np.full(m, np.nan), np.full(m, np.nan)
    line, direc = np.full(m, np.nan), np.full(m, np.nan)
    for i in range(m):
        lb, ub = src[i] - factor * atr[i], src[i] + factor * atr[i]
        plb = lower[i - 1] if i >= 1 and not np.isnan(lower[i - 1]) else 0.0
        pub = upper[i - 1] if i >= 1 and not np.isnan(upper[i - 1]) else 0.0
        c1 = cv[i - 1] if i >= 1 else np.nan
        lower[i] = lb if (lb > plb or c1 < plb) else plb
        upper[i] = ub if (ub < pub or c1 > pub) else pub
        if i == 0 or np.isnan(atr[i - 1]):
            d = 1
        elif line[i - 1] == pub:
            d = -1 if cv[i] > upper[i] else 1
        else:
            d = 1 if cv[i] < lower[i] else -1
        direc[i] = d
        line[i] = lower[i] if d == -1 else upper[i]
    return pd.Series(line, index=bars_df.index), pd.Series(direc, index=bars_df.index)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    _, d = _supertrend(bars_df, float(p["factor"]), int(p["atr_period"]))
    r = _rsi(bars_df["close"], int(p["rsi_len"]))
    ch = d.diff()
    le = (ch < 0) & (r < 70)
    se = (ch > 0) & (r > 30)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
