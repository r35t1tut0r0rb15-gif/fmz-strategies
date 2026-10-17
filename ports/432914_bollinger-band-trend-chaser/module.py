"""Narrow-band trend chaser, long only, broker days: the close above the 0.382-sigma band (SMA 20) of five bars ago and the
close five bars ago above the band of six bars ago, with the close at or above the previous SMA 200, a WMA-smoothed TSI
above its WMA 52 signal and the ADX 13 between 20 and 100, goes long; the TSI crossing under its signal closes it.
Port of FMZ strategy #432914 "Bollinger Band Trend Chaser" (ADX_TSI_Bol Band Trend Chaser (Trend Chaser)).

FMZ source id: 432914

Source
    https://www.fmz.com/strategy/432914 (PineScript v4, FMZ last modified 2023-11-22 16:51:27).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 154-246), BB 20 x 0.382, SMA 200, TSI 25 / 13 (WMA) with WMA 52, ADX 13 / 13, key level 20
    close > upper[5] and close[5] > upper[6] and close >= sma200[1] and tsi > wma(tsi, 52) and 20 < adx < 100 -> entry long
    crossunder(tsi, wma(tsi, 52)) -> close long

Interpretation choices (Pine rules in SURVEY_README.md)
    * The band test is coded as written (the current close against the band of five bars ago, the
      close of five bars ago against the band of six bars ago), not "five closes above". The TSI
      double smoothing uses WMAs; the ADX is Wilder's with fixnan as a running value. The back-test
      range (2010 to 2030) is dropped. Long only; Opposite entries cannot occur. Daily bars are broker
      days (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, bands, an SMA, a TSI and the ADX.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 10 % of equity and the commission stored in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Long only. Opposite entries cannot occur.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_432914_band_tsi_adx_trend_chaser"
FAMILY = "multi_indicator_confluence"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "mult": [0.382, 1.0],
    "ma_len": [200, 100],
}
DEFAULT_PARAMS = {"bb_len": 20, "mult": 0.382, "ma_len": 200, "ts_long": 25, "ts_short": 13, "ts_sig": 52,
                  "adx_len": 13, "di_len": 13, "key": 20}


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


def _wma(x, n):
    v = x.to_numpy(dtype=float)
    out = np.full(len(v), np.nan)
    if len(v) >= n:
        w = np.arange(1, n + 1, dtype=float)
        out[n - 1:] = np.lib.stride_tricks.sliding_window_view(v, n) @ w / w.sum()
    return pd.Series(out, index=x.index)


def _keep_last(v):
    out = np.full(len(v), np.nan)
    last = np.nan
    for i, x in enumerate(v):
        if not np.isnan(x):
            last = x
        out[i] = last
    return out


def _adx(h, lo, c, di_len, adx_len):
    up, dn = h.diff(), -lo.diff()
    c1 = c.shift(1)
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1)
    trur = tr.ewm(alpha=1 / di_len, adjust=False).mean()
    dmp = pd.Series(np.where((up > dn) & (up > 0), up, 0.0), index=h.index).where(up.notna())
    dmm = pd.Series(np.where((dn > up) & (dn > 0), dn, 0.0), index=h.index).where(dn.notna())
    plus = _keep_last((100 * dmp.ewm(alpha=1 / di_len, adjust=False).mean() / trur).to_numpy(dtype=float))
    minus = _keep_last((100 * dmm.ewm(alpha=1 / di_len, adjust=False).mean() / trur).to_numpy(dtype=float))
    s = plus + minus
    ratio = pd.Series(np.abs(plus - minus) / np.where(s == 0, 1.0, s), index=h.index)
    return 100 * ratio.ewm(alpha=1 / adx_len, adjust=False).mean()


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["bb_len"])
    upper = c.rolling(n).mean() + float(p["mult"]) * c.rolling(n).std(ddof=0)
    ma = c.rolling(int(p["ma_len"])).mean()
    pc = c.diff()
    ds = lambda x: _wma(_wma(x, int(p["ts_long"])), int(p["ts_short"]))  # noqa: E731
    tsi = 100 * ds(pc) / ds(pc.abs())
    sig = _wma(tsi, int(p["ts_sig"]))
    adx = _adx(h, lo, c, int(p["di_len"]), int(p["adx_len"]))
    buy = ((c > upper.shift(5)) & (c.shift(5) > upper.shift(6)) & (c >= ma.shift(1)) & (tsi > sig)
           & (adx > float(p["key"])) & (adx < 100)).astype(bool)
    close_l = ((tsi < sig) & (tsi.shift(1) >= sig.shift(1))).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return buy, close_l, false, false.copy()


def portfolio_kwargs(**params):
    return {}
