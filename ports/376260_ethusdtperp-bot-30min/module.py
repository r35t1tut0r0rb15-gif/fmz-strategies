"""ADX (MASANAKAMURA 16 > 13.5) direction with an RSI 30 of hl2 band, relative volume over 1.2 x its SMA 31, a DEMA-smoothed Hull RSI momentum beyond +/- 5 and a smoothed-RSI oscillator signal sign, 30-minute bars: all bullish goes long, all bearish goes short, each with a 1.6 % target and 4.3 % stop from the entry; reversing.
Port of FMZ strategy #376260 "ETHUSDTPERP BOT 30min" (ETHUSDTPERP BOT 30min).

FMZ source id: 376260

Source
    https://www.fmz.com/strategy/376260 (PineScript v4, FMZ last modified 2022-08-02 23:47:12).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 45-186), ADX MASANAKAMURA 16 / 13.5; RSI 30 of hl2; volume SMA 31 x 1.2; momentum hma(rsi(ohlc4, 14), 23) - 50, DEMA 9 > 5; oscillator ema(ema(rsi(ohlc4, 11), 7), 5) vs SMA 9, signal SMA 10; TP 1.6 %, SL 4.3 % of the avg price
    Long = DI+ > DI- and ADX > 13.5 and rsi(hl2, 30) < 70 and volume > 1.2 sma(volume, 31) and dema(hma(rsi(ohlc4, 14), 23) - 50, 9) > 5 and sma(dosc, 10) > 0 -> entry L
    Short mirror (rsi > 30, momentum < -5, signal < 0) -> entry S;  exit(qty_percent 100, profit 1.6 %, loss 4.3 % of the avg price)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bar size is the one the title states (30min; the source has no backtest header). The momentum
      source is the default "Price" (ohlc4), so no VWAP is used. ta.hma is wma(2 wma(x, n / 2) - wma(x, n),
      floor(sqrt(n))) with n / 2 taken as an integer. The ADX is the MASANAKAMURA menu default (Wilder sums,
      SMA of DX). The exit has no from_entry, so it brackets both sides: a scalar fraction of the fill (as
      #440797). A bar with both sets takes the short (the later call). REVERSAL INTENDED. Stop module:
      portfolio_kwargs {} (driver D4). The 100 % of equity size, capital and commission are sizing /
      costs, not ported.

Admission criteria
    1 fits the interface: PASS, bar-close orders; percent bracket from the fill.
    2 generic: PASS, ADX direction with volume and RSI-momentum confirmation.
    3 crypto-exchange-only: no (no exchange header).
    4 signals only: 100 % of equity, capital 10000 and commission 0.075 % stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) in volume > 1.2 x sma(volume, 31); exchange volume to be compared later (Austin, 2026-10-23).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_376260_adx_mn16_volume_hull_rsi_momentum_dosc_pct_bracket_reversal"
FAMILY = "adx_trend"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "30min"  # the title's "30min" (no backtest header)
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "rvol_trigger": [1.2, 1.0],
    "th": [13.5, 20.0],
}
DEFAULT_PARAMS = {"rvol_trigger": 1.2, "th": 13.5, "adx_len": 16, "len_3": 30, "ma_length": 31, "rsi_len": 14,
                  "s_len": 23, "rsi_length": 11, "ema1": 7, "ema2": 5, "sma_len": 9, "signal_len": 10,
                  "tp": 0.016, "sl": 0.043}


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


def _rsi(c, n):
    d = c.diff()
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    return 100 - 100 / (1 + up / dn)


def _rsi_custom(x, n):
    """The source's rsi_3: down == 0 -> 100, up == 0 -> 0, else 100 - 100 / (1 + up / down)."""
    d = x.diff()
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    return (100 - 100 / (1 + up / dn)).where(up != 0, 0.0).where(dn != 0, 100.0).where(up.notna() & dn.notna())


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


def _adx_masanakamura(b, n):
    """The source's calcADX_Masanakamura: Wilder running sums with nz(), DX averaged by an SMA."""
    h, lo, c = (b[k].to_numpy(dtype=float) for k in ("high", "low", "close"))
    m = len(c)
    dip, dim = np.full(m, np.nan), np.full(m, np.nan)
    s_tr = s_p = s_m = 0.0
    for i in range(m):
        c1 = c[i - 1] if i else 0.0
        h1 = h[i - 1] if i else 0.0
        l1 = lo[i - 1] if i else 0.0
        tr = max(h[i] - lo[i], abs(h[i] - c1), abs(lo[i] - c1))
        dmp = max(h[i] - h1, 0.0) if h[i] - h1 > l1 - lo[i] else 0.0
        dmm = max(l1 - lo[i], 0.0) if l1 - lo[i] > h[i] - h1 else 0.0
        s_tr = s_tr - s_tr / n + tr
        s_p = s_p - s_p / n + dmp
        s_m = s_m - s_m / n + dmm
        if s_tr != 0:
            dip[i], dim[i] = s_p / s_tr * 100, s_m / s_tr * 100
    dip_s, dim_s = pd.Series(dip, index=b.index), pd.Series(dim, index=b.index)
    dx = (dip_s - dim_s).abs() / (dip_s + dim_s) * 100
    return dip_s, dim_s, dx.rolling(n).mean()


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c, v = (bars_df[k] for k in ("open", "high", "low", "close", "volume"))
    th = float(p["th"])
    dip, dim, adx = _adx_masanakamura(bars_df, int(p["adx_len"]))
    r3 = _rsi_custom((h + lo) / 2, int(p["len_3"]))
    vol_ok = v > float(p["rvol_trigger"]) * v.rolling(int(p["ma_length"])).mean()
    src = (o + h + lo + c) / 4
    r2 = _hma(_rsi(src, int(p["rsi_len"])), int(p["s_len"])) - 50
    e0 = r2.ewm(span=9, adjust=False).mean()
    dema1 = 2 * e0 - e0.ewm(span=9, adjust=False).mean()
    sr = _rsi(src, int(p["rsi_length"])).ewm(span=int(p["ema1"]), adjust=False).mean() \
        .ewm(span=int(p["ema2"]), adjust=False).mean()
    dosc = sr - sr.rolling(int(p["sma_len"])).mean()
    sig = dosc.rolling(int(p["signal_len"])).mean()
    le = (dip > dim) & (adx > th) & (r3 < 70) & vol_ok & (dema1 > 5) & (sig > 0)
    se = (dip < dim) & (adx > th) & (r3 > 30) & vol_ok & (dema1 < -5) & (sig < 0)
    false = pd.Series(False, index=c.index)
    return le & ~se, false, se, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["sl"]), "tp_stop": float(p["tp"])}


def portfolio_kwargs(**params):
    return {}
