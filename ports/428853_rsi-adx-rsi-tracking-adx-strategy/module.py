"""ADX + RSI trend entries, long only, broker days: a rising SMA 20 with a rising ADX and a non-extreme RSI 14
goes long; RSI 9 above 75 with the ADX rising by less than 0.2 closes it (two conditional stop orders of the
source are described, not emitted).
Port of FMZ strategy #428853 "RSI追踪ADX策略RSI-Tracking-ADX-Strategy" ([蘆田策略]ADX+RSI).

FMZ source id: 428853

Source
    https://www.fmz.com/strategy/428853 (PineScript v2, FMZ last modified 2023-10-10 10:32:48).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 243-292), ADX 14 / 14, RSI 14 and 9, SMA 20
    dADX = adx - adx[1]; up20 = sma(close,20) > sma(close,20)[1]
    (up20 and dADX > 0.2 and rsi14 < 85) or (up20 and 0 < dADX < 0.2 and rsi14 < 50) -> entry long
    rsi9 > 75 and 0 < dADX < 0.2 -> strategy.close_all()
    rsi9 > 75 and dADX > 0.2 -> exit(stop = position_avg_price + 4 x tr); sma20 falling -> exit(stop = sma20)

Interpretation choices (Pine rules in SURVEY_README.md)
    * ADX as the source's dirmov / adx functions (Wilder rma, fixnan on the DIs, sum 0 -> 1).
    * The two strategy.exit(stop=) orders set a stop level from the bar they are placed on (the
      average price + 4 x that bar's true range; the bar's SMA 20) and re-place it on every later bar
      that meets their condition: a stop level that moves after entry, which stops() cannot express
      (rule 2). Not emitted; mark trailing_stop_pending. Described exactly here and in PORT_NOTES.
    * Long only. Daily bars are broker days (17:00 America/New_York), stamped with their first minute.
      FREQ = "1D" from the backtest header (period 1d).

Admission criteria
    1 fits the interface: PASS, bar-close orders; the conditional stop orders are not emitted (rule 2).
    2 generic: PASS, ADX and RSI levels only.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code; the conditional stops are quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_428853_adx_rsi_trend_long"
FAMILY = "directional_movement"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "adx_step": [0.2, 0.5],
    "rsi_exit": [75, 70],
}
DEFAULT_PARAMS = {"adx_len": 14, "di_len": 14, "adx_step": 0.2, "rsi_exit": 75, "sma_length": 20}


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


def _rsi(x, n):
    d = x.diff()
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    r = 100 - 100 / (1 + up / dn)
    return r.where(dn != 0, 100.0).where(up.notna() & dn.notna())


def _fixnan(x):
    """Pine's fixnan: an na value is replaced by the last earlier non-na value of the indicator
    itself (no bar data is carried; past values only)."""
    v = x.to_numpy(dtype=float).copy()
    last = np.nan
    for i in range(len(v)):
        if np.isnan(v[i]):
            v[i] = last
        else:
            last = v[i]
    return pd.Series(v, index=x.index)


def _adx(bars_df, di_len, adx_len):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    up, down = h.diff(), -lo.diff()
    plus_dm = up.where((up > down) & (up > 0), 0.0).fillna(0.0)
    minus_dm = down.where((down > up) & (down > 0), 0.0).fillna(0.0)
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    trng = _rma(tr, di_len)
    plus = _fixnan(100 * _rma(plus_dm, di_len) / trng)
    minus = _fixnan(100 * _rma(minus_dm, di_len) / trng)
    s = plus + minus
    return 100 * _rma((plus - minus).abs() / s.where(s != 0, 1.0), adx_len)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    adx = _adx(bars_df, int(p["di_len"]), int(p["adx_len"]))
    dadx = adx - adx.shift(1)
    sma = c.rolling(int(p["sma_length"])).mean()
    up20 = sma > sma.shift(1)
    r14, r9 = _rsi(c, 14), _rsi(c, 9)
    st = p["adx_step"]
    long_e = ((up20 & (dadx > st) & (r14 < 85)) | (up20 & (dadx > 0) & (dadx < st) & (r14 < 50))).astype(bool)
    long_x = ((r9 > p["rsi_exit"]) & (dadx > 0) & (dadx < st)).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, long_x, false, false.copy()


def portfolio_kwargs(**params):
    return {}
