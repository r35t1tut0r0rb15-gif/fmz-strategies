"""Rising ADX above both 50-day averages, broker days, long only: the ADX (14 / 14) rising with the close above the SMA 50 and the EMA 50 goes long; the ADX falling or the close under either average
closes.
Port of FMZ strategy #440314 "基于ADXMA和EMA的只做多趋势跟踪策略ADX-MA-and-EMA-Long-Only-Trend-Tracking-Strategy" (ADX_MA_EMA_Long_UpTrend).

FMZ source id: 440314

Source
    https://www.fmz.com/strategy/440314 (PineScript v4, FMZ last modified 2024-01-29 11:30:15).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 144-170), ADX smoothing 14, DI length 14; SMA 50, EMA 50
    sig = adx(14, 14);  longCondition = sig > sig[1] and close > sma50 and close > ema50 -> entry Long;  exitCondition = sig < sig[1] or close < sma50 or close < ema50 -> close Long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The DI lines are fixnan()-held as written; the ADX divides by 1 when the DI sum is 0. The entry and
      exit conditions cannot hold together. Long only. No sizing code. Daily bars are broker days (17:00
      America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, ADX slope and averages.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_440314_rising_adx_above_ma_ema_long"
FAMILY = "directional_movement"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ma_period": [50, 20],
    "adx_len": [14, 7],
}
DEFAULT_PARAMS = {"ma_period": 50, "adx_len": 14, "di_len": 14}


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


def _fixnan(x):
    """Pine fixnan: the last non-NaN value, NaN before the first."""
    v = x.to_numpy(dtype=float)
    idx = np.where(~np.isnan(v), np.arange(len(v)), 0)
    idx = np.maximum.accumulate(idx)
    return pd.Series(v[idx], index=x.index)


def _adx(bars_df, di_len, adx_len):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    up, dn = h.diff(), -lo.diff()
    pdm = up.where((up > dn) & (up > 0), 0.0).where(up.notna())
    mdm = dn.where((dn > up) & (dn > 0), 0.0).where(dn.notna())
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1).where(pc.notna())
    trr = _rma(tr, di_len)
    plus = _fixnan(100 * _rma(pdm, di_len) / trr)
    minus = _fixnan(100 * _rma(mdm, di_len) / trr)
    s = plus + minus
    return 100 * _rma((plus - minus).abs() / s.where(s != 0, 1.0), adx_len)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    sig = _adx(bars_df, int(p["di_len"]), int(p["adx_len"]))
    n = int(p["ma_period"])
    ma = c.rolling(n).mean()
    em = c.ewm(span=n, adjust=False).mean()
    le = (sig > sig.shift(1)) & (c > ma) & (c > em)
    lx = (sig < sig.shift(1)) | (c < ma) | (c < em)
    false = pd.Series(False, index=c.index)
    return le, lx & ~le, false, false.copy()


def portfolio_kwargs(**params):
    return {}
