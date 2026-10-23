"""Hourly bars, long only: from flat, the VWMA 9 crossing over the VWMA 14 with the candle body above a VWMA-89 channel line, the line not falling more than 0.2 %, the 10-bar change above -2 %, dollar volume between its 15th and 95th 60-bar percentiles and a shifted DMI (ADX > 18, DI+ - |DI-| > 15) goes long with a stop 2 % under the previous high; it closes when the close drops under the line or after 66 bars.
Port of FMZ strategy #446985 "VWMA-ADX-基于动量与趋势的比特币多头策略-VWMA-ADX-Momentum-and-Trend-Based-Bitcoin-Long-Strategy" (Long BTC Strategy (Q_D_Nam_N_96)).

FMZ source id: 446985

Source
    https://www.fmz.com/strategy/446985 (PineScript v5, FMZ last modified 2024-04-03 17:47:49).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 97-218), VWMA 9 / 14; ma3 = (0.1 VWMA89(highest 89) + 0.9 VWMA89(lowest 89)) x 0.995; DMI 7 / 10 with +-11 shifts; volume quartile 60 bars 15 / 95; 60-minute settings: stop high[1] x 0.98, hold 66 bars, ROC 10
    longCondition = crossover(vwma9, vwma14) and (close > open ? close > ma3 : open > ma3) and ma3 change >= -0.2 % and roc(10) > -2 %;  cond1 = Volume_Quartile(volume x hlcc4);  cond2 = adx > 18 and plus - |minus| > 15
    longCondition and cond1 and cond2 and flat -> entry buy, exit(stop = high[1] x 0.98);  count > 66 or close < ma3 -> close('buy', immediately = true)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The 60-minute branch of each timeframe switch applies (n 0.995, ROC 10, stop x 0.98, hold 66). The
      DMI adds 11 to DI+ and subtracts 11 from DI-, and its ADX is a VWMA 10 of |DI+ - DI- - 11| / sum,
      as written (weird case). The stop is sent on the signal bar from the previous high: a fraction of
      the fill, exact (1e-6 floor); the signals follow it for the flat test. close(immediately = true)
      fills at the bar's close in Pine; the house fills at the next open. count is the bars held, from
      the fill bar. Percentiles by linear interpolation. Long only. 100 % of equity is sizing. Stop
      module: portfolio_kwargs {} (driver D4). FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; stop at the signal bar as a fraction of the fill.
    2 generic: PASS, VWMA crossings over a volume-weighted channel with volume and DMI filters.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: strategy(): 100 % of equity, capital 1000, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) in the VWMAs, the dollar-volume percentile band and the VWMA-smoothed ADX; exchange volume to be compared later (Austin, 2026-10-23).
Session open: none (24 h).
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_446985_vwma9_14_cross_vwma_channel_dmi_volume_band_1h_long_only"
FAMILY = "volume_weighted_ma"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "hold": [66, 33],
    "stop_k": [0.98, 0.95],
}
DEFAULT_PARAMS = {"hold": 66, "stop_k": 0.98, "n": 0.995, "p_roc": 10}


def _resample(raw_1m_df, freq):
    ohlcv = raw_1m_df[["open", "high", "low", "close", "volume"]]
    bars = ohlcv.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
    bars = bars.dropna(subset=["close"])  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


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


def _fixnan(x):
    """Pine fixnan: the last non-NaN value, NaN before the first."""
    v = x.to_numpy(dtype=float)
    idx = np.where(~np.isnan(v), np.arange(len(v)), 0)
    idx = np.maximum.accumulate(idx)
    return pd.Series(v[idx], index=x.index)


def _vwma(x, v, n):
    sv = v.rolling(n).mean()
    return (x * v).rolling(n).mean() / sv.where(sv != 0)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c, v = (bars_df[k] for k in ("open", "high", "low", "close", "volume"))
    dv = v * (h + lo + c + c) / 4
    q15, q95 = dv.rolling(60).quantile(0.15), dv.rolling(60).quantile(0.95)
    cond1 = (dv > q15) & (dv < q95)
    ma1, ma2 = _vwma(c, v, 9), _vwma(c, v, 14)
    ma3 = (0.1 * _vwma(c.rolling(89).max(), v, 89) + 0.9 * _vwma(c.rolling(89).min(), v, 89)) * float(p["n"])
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1).where(pc.notna())
    up, dn = h.diff(), -lo.diff()
    pdm = pd.Series(np.where((up > dn) & (up > 0), up, 0.0), index=c.index).where(up.notna())
    mdm = pd.Series(np.where((dn > up) & (dn > 0), dn, 0.0), index=c.index).where(dn.notna())
    trur = _rma(tr, 7)
    plus = _fixnan(100 * _rma(pdm, 7) / trur) + 11
    minus = _fixnan(100 * _rma(mdm, 7) / trur) - 11
    s = plus + minus
    adx = 100 * _vwma((plus - minus - 11).abs() / s.where(s != 0, 1.0), v, 10)
    cond2 = (adx > 18) & (plus - minus.abs() > 15)
    pr = int(p["p_roc"])
    body_ok = pd.Series(np.where(c > o, c > ma3, o > ma3), index=c.index)
    lc = ((ma1 > ma2) & (ma1.shift(1) <= ma2.shift(1)) & body_ok & ((ma3 - ma3.shift(1)) * 100 / ma3.shift(1) >= -0.2)
          & ((c - c.shift(pr)) * 100 / c.shift(pr) > -2.0) & cond1 & cond2).to_numpy()
    below = (c < ma3).to_numpy()
    stv = (h.shift(1) * float(p["stop_k"])).to_numpy()
    lv = lo.to_numpy(dtype=float)
    hold = int(p["hold"])
    m = len(lc)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, pend_in, pend_out, sl_px, count = 0, False, False, np.nan, 0
    for i in range(m):
        if pend_in:
            pos, pend_in, count = 1, False, 0
        if pend_out:
            pos, pend_out = 0, False
        if pos == 1 and lv[i] <= sl_px:                 # the stop ends the trade inside the bar
            pos = 0
        count = count + 1 if pos == 1 else 0
        if pos == 1:
            if (count > hold or below[i]) and i + 1 < m:
                lx[i], pend_out = True, True
        elif not pend_in and lc[i] and i + 1 < m:
            le[i], pend_in, sl_px = True, True, stv[i]
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, lx, se, sx = simulate(bars_df, **params)
    o, h = bars_df["open"], bars_df["high"]
    lf = le.shift(1, fill_value=False)
    sl_f = (1 - (h.shift(1) * float(p["stop_k"])).shift(1) / o).where(lf)
    return {"sl_stop": sl_f.clip(lower=1e-6)}


def portfolio_kwargs(**params):
    return {}
