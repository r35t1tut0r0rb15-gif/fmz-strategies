"""EMA 6 / 20 crosses on the LSMA 333 side with RSI 14 beyond 50, reversing, with a 1 % stop and a 2 % target from the
signal close, daily bars.
Port of FMZ strategy #482500 "多重指标交叉动态自适应趋势跟踪交易策略Multi-Indicator-Cross-Adaptive-Trend-Following-Trading-Strategy" (EMA 6-20 + LSMA 333 + RSI 50 Filtreli Al-Sat Stratejisi).

FMZ source id: 482500

Source
    https://www.fmz.com/strategy/482500 (PineScript v6, FMZ last modified 2025-02-18 17:17:25).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 116-152), EMA 6 / 20, LSMA 333 (linreg), RSI 14, SL 1 %, TP 2 %
    crossover(ema6, ema20) and close > lsma and rsi > 50 -> entry long with exit(stop = close x 0.99,
    limit = close x 1.02); crossunder and close < lsma and rsi < 50 -> short mirrored

Interpretation choices (Pine rules in SURVEY_README.md)
    * LSMA = ta.linreg(close, 333, 0): the least-squares line's value at the current bar over the last 333 closes.
    * The bracket is placed with the entry from the signal close, re-based on the fill (house rule).
    * Entries reverse (REVERSAL INTENDED). Stop module: portfolio_kwargs {} (D4). Daily bars are broker days
      (17:00 America/New_York), stamped with their first minute; FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders and a bracket set at entry.
    2 generic: PASS, EMAs, a regression line, RSI and percentage distances.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: default quantity; the bracket via stops(), quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
REVERSAL INTENDED.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_482500_ema6_20_cross_lsma333_rsi50_pct_bracket"
FAMILY = "trend_following"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "lsma_len": [333, 200],
    "tp_pct": [2.0, 4.0],
}
DEFAULT_PARAMS = {"fast": 6, "slow": 20, "lsma_len": 333, "rsi_len": 14, "sl_pct": 1.0, "tp_pct": 2.0}


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


def _linreg(c, n):
    """ta.linreg(src, n, 0): the least-squares line over the last n values, evaluated at the current bar."""
    x = np.arange(n, dtype=float)
    xm = x.mean()
    sxx = ((x - xm) ** 2).sum()

    def end_value(w):
        ym = w.mean()
        slope = ((x - xm) * (w - ym)).sum() / sxx
        return ym + slope * (n - 1 - xm)

    return c.rolling(n).apply(end_value, raw=True)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    f = c.ewm(span=int(p["fast"]), adjust=False).mean()
    s = c.ewm(span=int(p["slow"]), adjust=False).mean()
    lsma = _linreg(c, int(p["lsma_len"]))
    rsi = _rsi(c, int(p["rsi_len"]))
    long_e = ((f > s) & (f.shift(1) <= s.shift(1)) & (c > lsma) & (rsi > 50)).astype(bool)
    short_e = ((f < s) & (f.shift(1) >= s.shift(1)) & (c < lsma) & (rsi < 50)).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": p["sl_pct"] / 100, "tp_stop": p["tp_pct"] / 100}


def portfolio_kwargs(**params):
    return {}
