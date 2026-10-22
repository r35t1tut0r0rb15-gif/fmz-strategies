"""EMA 50 / 100 crossings above (below) the Ichimoku cloud and the EMA 200 with RSI 14 and MACD agreeing, gated by daily RSI / MACD level crossings, 3-hour bars: the cross up with the last daily RSI cross under 30 or MACD cross under 0 goes long, the mirror goes short; reversing.
Port of FMZ strategy #478724 "Advanced Multi Indicator Multi Dimensional Trend Cross Quantitative Strategy" (Ichimoku + RSI + MACD + HTF Divergence + EMA Cross Strategy).

FMZ source id: 478724

Source
    https://www.fmz.com/strategy/478724 (PineScript v6, FMZ last modified 2025-01-17 16:00:03).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 81-188), Ichimoku 9 / 26 / 52 (undisplaced in the tests); RSI 14, 70 / 30; MACD 12 / 26 / 9; HTF "D" RSI and MACD level crossings; EMA 50 / 100 / 200
    htf_rsi = security("D", rsi), htf_macd = security("D", macd);  div := 1 when src crosses up through upper, -1 when it crosses down through lower (kept)
    long = close above both spans and rsi > 50 and macd > signal and (rsi_div == -1 or macd_div == -1) and close > ema200 and crossover(ema50, ema100) -> entry Long;  short mirror (div == 1) -> entry Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * A version-6 security("D") without lookahead is read as the last completed broker day (as #440503):
      the RSI 14 and MACD line of daily closes as of the previous broker day, built from the module's own
      bars. The divergence flags are kept states set by those daily series crossing their levels (the
      MACD at 0), sampled on the 3-hour bars as the script does. The spans are read undisplaced; the
      displacement only plots. REVERSAL INTENDED. No sizing code. FREQ = "3h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; daily values from completed broker days.
    2 generic: PASS, EMA crossings with cloud, RSI, MACD and daily-level filters.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: daily values by broker day (17:00 America/New_York, DST by the zone).
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_478724_ema50_100_cross_cloud_rsi_macd_daily_level_flags_reversal"
FAMILY = "ichimoku"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "3h"  # backtest header period: 3h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "ema_fast": [50, 20],
    "ema_slow": [100, 50],
}
DEFAULT_PARAMS = {"ema_fast": 50, "ema_slow": 100}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


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


def _macd_parts(c):
    m = c.ewm(span=12, adjust=False).mean() - c.ewm(span=26, adjust=False).mean()
    return m, m.ewm(span=9, adjust=False).mean()


def _level_flag(src, lower, upper):
    """var div: 1 when src crosses up to / through upper, -1 when down to / through lower, else kept."""
    v = src.to_numpy(dtype=float)
    out = np.full(len(v), np.nan)
    st = np.nan
    for i in range(1, len(v)):
        if v[i] >= upper and v[i - 1] < upper:
            st = 1.0
        elif v[i] <= lower and v[i - 1] > lower:
            st = -1.0
        out[i] = st
    return out


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]

    def don(n):
        return (h.rolling(n).max() + lo.rolling(n).min()) / 2

    span_a = (don(9) + don(26)) / 2
    span_b = don(52)
    r = _rsi(c, 14)
    macd, sig = _macd_parts(c)
    day = broker_day(c.index)
    dc = c.groupby(day).last()
    d_rsi = pd.Series(_rsi(dc, 14).shift(1).reindex(day).to_numpy(), index=c.index)   # last completed day
    d_macd = pd.Series(_macd_parts(dc)[0].shift(1).reindex(day).to_numpy(), index=c.index)
    rf = _level_flag(d_rsi, 30.0, 70.0)
    mf = _level_flag(d_macd, 0.0, 0.0)
    e200 = c.ewm(span=200, adjust=False).mean()
    a = c.ewm(span=int(p["ema_fast"]), adjust=False).mean()
    b = c.ewm(span=int(p["ema_slow"]), adjust=False).mean()
    up = (a > b) & (a.shift(1) <= b.shift(1))
    dn = (a < b) & (a.shift(1) >= b.shift(1))
    bull_f = pd.Series((rf == -1) | (mf == -1), index=c.index)
    bear_f = pd.Series((rf == 1) | (mf == 1), index=c.index)
    le = (c > span_a) & (c > span_b) & (r > 50) & (macd > sig) & bull_f & (c > e200) & up
    se = (c < span_a) & (c < span_b) & (r < 50) & (macd < sig) & bear_f & (c < e200) & dn
    false = pd.Series(False, index=c.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
