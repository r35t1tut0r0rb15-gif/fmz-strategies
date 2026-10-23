"""Two-hour bars: MACD 8 / 13 / 5 above its signal, OBV above its EMA 55, EMA 8 of hlc3 above the EMA 100, the parabolic SAR (0.09 / 0.2 / 0.2) under the low and hl2 above the previous high, with the ADX 5 above 30 and above its EMA 3 and a rising market-facilitation bar on rising volume within the last 4 bars, goes long; the mirror goes short; each with a 100-tick target and a 75-tick stop; reversing.
Port of FMZ strategy #440435 "Scalping Strategy Based on Market Liquidity and Trend" (scalping with market facilitation (trent777brown)).

FMZ source id: 440435

Source
    https://www.fmz.com/strategy/440435 (PineScript v5, FMZ last modified 2024-01-30 15:36:33).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 179-296), MFI0 = range / volume; DMI 5 / 5, ADX > 30; MACD 8 / 13 / 5; OBV EMA 55; EMA 8 (hlc3) / EMA 100; SAR 0.09 / 0.2 / 0.2; profit 100 / loss 75 ticks
    long = macdl > sigl and obv > ema(obv, 55) and ema8 > ema55 and psar < low and hl2 > high[1];  longtrig2 = adx > 30 and adx > ema(adx, 3) and barssince(mfigreen) <= 4
    if long: entry long (qty 1) when longtrig2, exit(profit = 100, loss = 75);  if short: entry short when shorttrig2, exit(profit = 100, loss = 75)

Interpretation choices (Pine rules in SURVEY_README.md)
    * profit / loss are ticks from the entry price: on the header's BTC_USDT (0.1 tick, about 42000 USD
      in the 2023-12 window) 10 / 7.5 USD, ported as fractions of the fill 2.381e-4 / 1.786e-4 (as
      #437390); the bracket is fixed at the fill, exactly as written. "ema55" is an EMA 100, as written.
      The market-facilitation index is range / volume; mfigreen = it and the volume both rose. The bar
      control classes (b11 .. b12) feed nothing. REVERSAL INTENDED. qty 1 is sizing. Stop module:
      portfolio_kwargs {} (driver D4). Stops on 2-hour bars: mark coarse_bar_stop. FREQ = "2h" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; fixed tick bracket from the fill.
    2 generic: PASS, trend-agreement entries timed by ADX and market-facilitation volume.
    3 crypto-exchange-only: no (exchange pair in the header only; tick distances converted at the source's BTC price).
    4 signals only: entry qty 1 unit, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) in the OBV, the market-facilitation index range / volume and the rising-volume test; exchange volume to be compared later (Austin, 2026-10-23).
Session open: none (24 h).
REVERSAL INTENDED.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_440435_macd_obv_ema_sar_adx_mfi_tick_bracket_2h_reversal"
FAMILY = "multi_indicator_confluence"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "adx_min": [30.0, 25.0],
    "obv_len": [55, 21],
}
DEFAULT_PARAMS = {"adx_min": 30.0, "obv_len": 55, "tp": 2.381e-04, "sl": 1.786e-04}


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


def _sar(hv, lv, cv, start, inc, mx):
    """Pine's ta.sar as documented (pine_sar)."""
    m = len(cv)
    out = np.full(m, np.nan)
    res = mm = acc = np.nan
    below = None
    for i in range(1, m):
        first = False
        if i == 1:
            if cv[1] > cv[0]:
                below, mm, res = True, hv[1], lv[0]
            else:
                below, mm, res = False, lv[1], hv[0]
            first, acc = True, start
        res = res + acc * (mm - res)
        if below:
            if res > lv[i]:
                first, below = True, False
                res, mm, acc = max(hv[i], mm), lv[i], start
        else:
            if res < hv[i]:
                first, below = True, True
                res, mm, acc = min(lv[i], mm), hv[i], start
        if not first:
            if below:
                if hv[i] > mm:
                    mm, acc = hv[i], min(acc + inc, mx)
            else:
                if lv[i] < mm:
                    mm, acc = lv[i], min(acc + inc, mx)
        if below:
            res = min(res, lv[i - 1])
            if i > 1:
                res = min(res, lv[i - 2])
        else:
            res = max(res, hv[i - 1])
            if i > 1:
                res = max(res, hv[i - 2])
        out[i] = res
    return out


def _adx(h, lo, c, di_len, smooth):
    """ta.dmi(diLength, adxSmoothing)[2]."""
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1).where(pc.notna())
    up, dn = h.diff(), -lo.diff()
    pdm = pd.Series(np.where((up > dn) & (up > 0), up, 0.0), index=h.index).where(up.notna())
    mdm = pd.Series(np.where((dn > up) & (dn > 0), dn, 0.0), index=h.index).where(dn.notna())
    atr = _rma(tr, di_len)
    plus, minus = 100 * _rma(pdm, di_len) / atr, 100 * _rma(mdm, di_len) / atr
    s = plus + minus
    return 100 * _rma((plus - minus).abs() / s.where(s != 0, 1.0), smooth)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c, v = (bars_df[k] for k in ("high", "low", "close", "volume"))
    mfi0 = (h - lo) / v.where(v != 0)
    green = ((mfi0 > mfi0.shift(1)) & (v > v.shift(1))).to_numpy()
    m = len(green)
    since = np.full(m, np.inf)
    last = -1
    for i in range(m):
        if green[i]:
            last = i
        if last >= 0:
            since[i] = i - last
    recent = pd.Series(since <= 4, index=c.index)
    adx = _adx(h, lo, c, 5, 5)
    trig = (adx > float(p["adx_min"])) & (adx > adx.ewm(span=3, adjust=False).mean()) & recent
    hlc3, hl2 = (h + lo + c) / 3, (h + lo) / 2
    macd = c.ewm(span=8, adjust=False).mean() - c.ewm(span=13, adjust=False).mean()
    sig = macd.ewm(span=5, adjust=False).mean()
    d = c.diff()
    obv = pd.Series(np.where(d > 0, v, np.where(d < 0, -v, 0.0)), index=c.index).cumsum()
    obv_ma = obv.ewm(span=int(p["obv_len"]), adjust=False).mean()
    e8 = hlc3.ewm(span=8, adjust=False).mean()
    e100 = c.ewm(span=100, adjust=False).mean()
    psar = pd.Series(_sar(h.to_numpy(dtype=float), lo.to_numpy(dtype=float), c.to_numpy(dtype=float), 0.09, 0.2, 0.2),
                     index=c.index)
    long_ = (macd > sig) & (obv > obv_ma) & (e8 > e100) & (psar < lo) & (hl2 > h.shift(1))
    short_ = (macd < sig) & (obv < obv_ma) & (e8 < e100) & (psar > h) & (hl2 < lo.shift(1))
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return (long_ & trig).astype(bool), false, (short_ & trig).astype(bool), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["sl"]), "tp_stop": float(p["tp"])}


def portfolio_kwargs(**params):
    return {}
