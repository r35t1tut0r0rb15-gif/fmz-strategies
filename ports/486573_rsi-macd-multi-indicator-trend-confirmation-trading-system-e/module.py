"""EMA 50 reclaims in a stacked EMA 50 / 100 / 200 trend with RSI and MACD filters, always in, broker days: the close
crossing above EMA 50 with EMA 50 > 100 > 200, RSI 14 between 50 and 70 and MACD above its signal goes long; the
mirror goes short; the opposite signal reverses.
Port of FMZ strategy #486573 "多指标趋势确认交易系统-均线融合RSI背离MACD信号策略-Multi-Indicator-Trend-Confirmation-Trading-System-EMA-Confluence-with-RSI-Divergence-and-MACD-Signal-Strategy" (Multi-Indikator Handelsstrategie).

FMZ source id: 486573

Source
    https://www.fmz.com/strategy/486573 (PineScript v5, FMZ last modified 2025-03-14 09:52:05).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 204-246), EMA 50 / 100 / 200, RSI 14 (30 / 70), MACD 12 / 26 / 9
    long = crossover(close, ema50) and ema50 > ema100 > ema200 and 50 < rsi < 70 and macd > signal
    short = crossunder(close, ema50) and ema50 < ema100 < ema200 and 30 < rsi < 50 and macd < signal
    entry long / entry short (no other exit)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The Bollinger bands are computed but unused. Entries reverse (REVERSAL INTENDED).
    * Near-duplicate group DG486573: this id is the group's port candidate; its partner #489201 (Jaccard 1.000) is
      marked DUPLICATE in screening and not ported.
    * Daily bars are broker days (17:00 America/New_York), stamped with their first minute; FREQ = "1D" from the
      backtest header. No stops.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, EMAs and oscillators.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: DG486573 with #489201 (Jaccard 1.000, DUPLICATE); this member ported.
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_486573_ema_stack_reclaim_rsi_macd"
FAMILY = "ma_trend_filter"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "len1": [50, 20],
    "rsi_ob": [70, 80],
}
DEFAULT_PARAMS = {"len1": 50, "len2": 100, "len3": 200, "rsi_len": 14, "rsi_ob": 70, "rsi_os": 30}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    e1, e2, e3 = (c.ewm(span=int(p[k]), adjust=False).mean() for k in ("len1", "len2", "len3"))
    rsi = _rsi(c, int(p["rsi_len"]))
    macd = c.ewm(span=12, adjust=False).mean() - c.ewm(span=26, adjust=False).mean()
    sig = macd.ewm(span=9, adjust=False).mean()
    x_up = (c > e1) & (c.shift(1) <= e1.shift(1))
    x_dn = (c < e1) & (c.shift(1) >= e1.shift(1))
    long_e = (x_up & (e1 > e2) & (e2 > e3) & (rsi > 50) & (rsi < p["rsi_ob"]) & (macd > sig)).astype(bool)
    short_e = (x_dn & (e1 < e2) & (e2 < e3) & (rsi < 50) & (rsi > p["rsi_os"]) & (macd < sig)).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def portfolio_kwargs(**params):
    return {}
