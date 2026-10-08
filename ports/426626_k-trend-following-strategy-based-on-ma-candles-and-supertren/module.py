"""MA-candle SuperTrend, long only: a SuperTrend run on RMA(20) candles (ATR = RMA(30) of their
range); with it up, the close above its short stop and the close near the previous year's high
(or well above its low), go long; when it turns down, close.
Port of FMZ strategy #426626 "K Trend Following Strategy Based on MA Candles and Supertrend".

Source
    https://www.fmz.com/strategy/426626 (PineScript v4, FMZ last modified 2023-09-13 18:07:54).
    Verbatim copy: original_source.md. Read 2026-10-07.

Original signal (original_source.md lines 95-186), rma 20 candles, ATR rma 30 x 1, wicks on,
dThreshold 0.2, rThreshold 0.7, direction long
    oO / oC / oH / oL = rma(open / close / high / low, 20)
    atr = rma(max(oH, oC[1]) - min(oL, oC[1]), 30)
    longStop = oC - atr, ratcheted up while oL[1] > its previous value; shortStop mirrors on oH[1]
    dir: -1 -> 1 when oH > shortStop[1]; 1 -> -1 when oL < longStop[1]
    yh / yl = previous 12-month bar's high / low (security '12M', [1], lookahead on)
    long = close > shortStop and dir == 1 and (close > yh * 0.8 or close > yl * 1.7)
    long -> entry long;  dir == -1 -> close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The '12M' read with [1] and lookahead on is the completed previous year: here the high /
      low of the previous calendar year of broker-day dates. The first year in the data has no
      previous year (no entries); the second reads a partial first year (data-start
      dependence, decision owed).
    * strategy.risk.allow_entry_in(long): short entries only close longs, which the dir == -1
      close already does. Long only.
    * Daily bars are broker days (session ending 17:00 New York), stamped with the session start.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_426626_ma_candle_supertrend_long"
FAMILY = "supertrend"  # proposed 2026-10-07, user to confirm
FREQ = "1D"  # broker days (backtest period 1d)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "lookback": [10, 20, 30],
    "atr_length": [20, 30],
}
DEFAULT_PARAMS = {"lookback": 20, "atr_length": 30, "atr_mult": 1.0, "d_threshold": 0.2, "r_threshold": 0.7}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date. The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def _daily(raw_1m_df):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    if ohlc.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    bars = ohlc.groupby(broker_day(ohlc.index)).agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"}).dropna(how="all")
    start = (bars.index - pd.Timedelta(days=1) + pd.Timedelta(hours=17)).tz_localize("America/New_York")
    bars.index = start.tz_convert("UTC")  # each bar stamped with its session start
    return bars


def _rma(x, n):
    """Wilder smoothing as TA-Lib: SMA seed over the first n valid values, then recursive."""
    v = x.to_numpy(dtype=float)
    out = np.full(v.shape, np.nan)
    valid = np.flatnonzero(~np.isnan(v))
    if len(valid) >= n:
        s = valid[0]
        out[s + n - 1] = v[s:s + n].mean()
        for i in range(s + n, len(v)):
            out[i] = (out[i - 1] * (n - 1) + v[i]) / n
    return pd.Series(out, index=x.index)


def _prev_year(bars_df):
    """High / low of the previous calendar year of broker-day dates (NaN for the first year)."""
    year = pd.Series(broker_day(bars_df.index).year, index=bars_df.index)
    yh = bars_df["high"].groupby(year).max()
    yl = bars_df["low"].groupby(year).min()
    return (year - 1).map(yh), (year - 1).map(yl)


def precompute(raw_1m_df, symbol_key, **params):
    return _daily(raw_1m_df)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    n = int(p["lookback"])
    oc = _rma(bars_df["close"], n)
    oh = _rma(bars_df["high"], n)
    ol = _rma(bars_df["low"], n)
    oc1 = oc.shift(1)
    rng = pd.concat([oh, oc1], axis=1).max(axis=1, skipna=False) - pd.concat([ol, oc1], axis=1).min(axis=1, skipna=False)
    atr = (_rma(rng, int(p["atr_length"])) * p["atr_mult"]).to_numpy()
    ocv, ohv, olv = oc.to_numpy(), oh.to_numpy(), ol.to_numpy()
    m = len(ocv)
    ls_out, ss_out, dir_out = np.full(m, np.nan), np.full(m, np.nan), np.ones(m)
    ls_p = ss_p = np.nan
    d = 1
    for i in range(m):
        ls, ss = ocv[i] - atr[i], ocv[i] + atr[i]
        ls_prev = ls if np.isnan(ls_p) else ls_p
        ss_prev = ss if np.isnan(ss_p) else ss_p
        if i > 0 and olv[i - 1] > ls_prev:
            ls = max(ls, ls_prev)
        if i > 0 and ohv[i - 1] < ss_prev:
            ss = min(ss, ss_prev)
        if d == -1 and ohv[i] > ss_prev:
            d = 1
        elif d == 1 and olv[i] < ls_prev:
            d = -1
        ls_out[i], ss_out[i], dir_out[i] = ls, ss, d
        ls_p, ss_p = ls, ss
    c = bars_df["close"]
    yh, yl = _prev_year(bars_df)
    near_high = (c > yh * (1 - p["d_threshold"])) | (c > yl * (1 + p["r_threshold"]))
    up = pd.Series(dir_out == 1, index=bars_df.index)
    le = (c > pd.Series(ss_out, index=bars_df.index)) & up & near_high
    lx = ~up
    false = pd.Series(False, index=bars_df.index)
    return le, lx, false, false.copy()


def portfolio_kwargs(**params):
    return {}
