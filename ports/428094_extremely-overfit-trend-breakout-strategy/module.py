"""EMA 6 price channels widened by a 50-bar volatility term, a Hull 4 and filters on trend, volume, rate of change and OBV correlation, broker days, entered only when flat: in a calm market (or any market without the dynamic trend test) a Hull dip under the fast channel's top with the fast channel's bottom under the slow channel's bottom goes long and the mirror goes short; a Hull peak beyond the channels closes, with a stop of 3 % x (1 + 11 x the 360-bar price sd / price) from the entry.
Port of FMZ strategy #428094 "Extremely Overfit Trend Breakout Strategy" (Extremely Overfit).

FMZ source id: 428094

Source
    https://www.fmz.com/strategy/428094 (PineScript v4, FMZ last modified 2023-09-28 15:54:32).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 199-434), channels EMA 6 (margin 3.2 / 1000) and EMA(EMA 6) (1.5 / 2000) + vol 1.92 x sd(50) / sqrt(50); Hull 4; restrictiveness -40; trend 360 / 720; volume EMA 14 cutoff 3.8 %; ROC 80 EMA 30 < 5.6; OBV correlation 10 > 0.89; stop 3 % flexed
    dynamicTrendDetected = abs(1.4 sd(close, 360) / close x 100) < 3.8 + 1.5 (close - close[720]) / close
    detected: not short and trendUp and close < close[1] and TpeakLow and volume EMA falling and ROC ok and OBV corr > 0.89 -> entry Long (mirror Short);  else: not short and TpeakLow and OBV ok -> entry Long (mirror)
    long and peakHigh -> close Long;  short and peakLow -> close Short;  exit(stop = avg x (1 - stopLossMod / 100))

Interpretation choices (Pine rules in SURVEY_README.md)
    * TpeakLow tests the Hull against the fast channel's TOP, as written. Entries need no opposite position
      (a long while long is ignored), so they come only from flat; "flat" follows the house bracket (the
      loop marks the trade closed when its stop is reached). The stop percent is re-sent every bar with the
      current 360-bar sd; the port fixes it at the signal bar as a fraction of the fill (mark
      trailing_stop_pending). conservativeClose is false, so the closes are the peak tests. ta.rising-type
      helpers are not used. Stop module: portfolio_kwargs {} (driver D4). Stops on 1-day bars: mark
      coarse_bar_stop. The 100 % of equity size and commission are sizing / costs. Daily bars are broker
      days (17:00 America/New_York), stamped with their first minute. FREQ = "1D" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; volatility-flexed percent stop.
    2 generic: PASS, channel peak / dip entries with trend, volume, ROC and OBV filters.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 100 % of equity, commission 0.16 %, pyramiding 1 stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) in the falling volume-EMA test and the OBV correlation; exchange volume to be compared later (Austin, 2026-10-23).
Session open: broker day (17:00 America/New_York, DST by the zone); no venue-open rule.
Opposite entries cannot occur (entries only from flat).

Marks: trailing_stop_pending, coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_428094_ema_channel_hull_peaks_trend_volume_obv_filters_flex_stop_flat_only"
FAMILY = "channel_breakout"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1D"  # backtest header period: 1d (broker days)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "restrictiveness": [-40.0, 0.0],
    "stop_loss": [3.0, 5.0],
}
DEFAULT_PARAMS = {"restrictiveness": -40.0, "stop_loss": 3.0, "fast_len": 6, "fast_margin": 3.2, "slow_len": 6,
                  "slow_margin": 1.5, "hma_len": 4}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


def precompute(raw_1m_df, symbol_key, **params):
    df = raw_1m_df[["open", "high", "low", "close", "volume"]].dropna(subset=["close"])
    if df.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    lab = broker_day(df.index)
    bars = df.groupby(lab).agg({"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
    first = pd.Series(df.index, index=df.index).groupby(lab).first()
    bars.index = pd.DatetimeIndex(first.loc[bars.index].values)   # each bar stamped with its first minute
    if bars.index.tz is None:
        bars.index = bars.index.tz_localize("UTC")
    return bars


def _wma(x, n):
    """Pine ta.wma over each n-bar window (NaN when the window holds a NaN)."""
    v = x.to_numpy(dtype=float)
    out = np.full(len(v), np.nan)
    if len(v) >= n:
        w = np.arange(1, n + 1, dtype=float)              # newest bar weighted n
        out[n - 1:] = np.lib.stride_tricks.sliding_window_view(v, n) @ w / w.sum()
    return pd.Series(out, index=x.index)


def _hma(x, n):
    return _wma(2 * _wma(x, n // 2) - _wma(x, n), int(np.floor(np.sqrt(n))))


def _parts(bars_df, p):
    o, c, v = bars_df["open"], bars_df["close"], bars_df["volume"]
    rs = float(p["restrictiveness"])
    rv = c.rolling(50).std(ddof=0) / np.sqrt(50) * (3.2 * (1 + rs / 100))
    fc = c.ewm(span=int(p["fast_len"]), adjust=False).mean()
    fub = fc * (1 + float(p["fast_margin"]) / 1000) + rv
    flb = fc * (1 - float(p["fast_margin"]) / 1000) - rv
    sn = int(p["slow_len"])
    sc = c.ewm(span=sn, adjust=False).mean().ewm(span=sn, adjust=False).mean()
    sub = sc * (1 + float(p["slow_margin"]) / 2000) + rv
    slb = sc * (1 - float(p["slow_margin"]) / 2000) - rv
    fh = _hma(c, int(p["hma_len"]))
    cbull, cbear = c > c.shift(1), c < c.shift(1)
    tv = (c - c.shift(360)) / c
    t_up, t_dn = tv > 0, tv < 0
    peak_high = (fh > fub) & (flb > sub)
    peak_low = (fh < flb) & (fub < slb)
    tpk_high = (fh > fub) & (fub > sub)
    tpk_low = (fh < fub) & (flb < slb)                    # the fast channel's top, as written
    vma = v.ewm(span=14, adjust=False).mean()
    vol_dec = vma < (vma.shift(1) * (1 - 3.8 / 100)).ewm(span=5, adjust=False).mean()
    trendiness = c.rolling(360).std(ddof=0) / c * (1 - rs / 100)
    lt = (c - c.shift(720)) / c
    dyn = (trendiness * 100).abs() < (3.8 + lt * 1.5)
    roc = 100 * (c - c.shift(80)) / c.shift(80)
    roc_ok = roc.ewm(span=30, adjust=False).mean().abs() < 5.6
    obv = (np.sign(c.diff()) * v).fillna(0.0).cumsum()
    obv_ok = c.rolling(10).corr(obv) > 0.89
    lc = (dyn & t_up & cbear & tpk_low & vol_dec & roc_ok & obv_ok) | (~dyn & tpk_low & obv_ok)
    scond = (dyn & t_dn & cbull & tpk_high & vol_dec & roc_ok & obv_ok) | (~dyn & tpk_high & obv_ok)
    dev = c.rolling(360).std(ddof=0) * (1 + 50 / 5)
    slm = float(p["stop_loss"]) * (1 + dev / c) / 100
    return lc.to_numpy(), scond.to_numpy(), peak_high.to_numpy(), peak_low.to_numpy(), slm


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    lc, scond, ph, pl, slm = _parts(bars_df, p)
    o, h, lo = (bars_df[k].to_numpy(dtype=float) for k in ("open", "high", "low"))
    k = slm.to_numpy(dtype=float)
    m = len(o)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    pos, fill, kk = 0, np.nan, np.nan
    for i in range(m):
        if pos == 1 and lo[i] <= fill * (1 - kk):
            pos = 0
        elif pos == -1 and h[i] >= fill * (1 + kk):
            pos = 0
        old = pos
        tgt = old
        if lc[i] and old != -1:
            tgt = 1
        if scond[i] and old != 1:
            tgt = -1
        if tgt == old == 1 and ph[i]:
            tgt = 0
        elif tgt == old == -1 and pl[i]:
            tgt = 0
        if tgt != old and tgt != 0 and i + 1 < m:
            fill, kk = o[i + 1], k[i]
            if tgt == 1:
                le[i] = True
            else:
                se[i] = True
        elif tgt == 0 and old == 1:
            lx[i] = True
        elif tgt == 0 and old == -1:
            sx[i] = True
        pos = tgt if (tgt == 0 or tgt != old and i + 1 < m) else old
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    slm = _parts(bars_df, p)[4]
    sl_f = slm.shift(1)                                # the stop percent of the signal bar
    return {"sl_stop": sl_f.where(sl_f > 0)}


def portfolio_kwargs(**params):
    return {}
