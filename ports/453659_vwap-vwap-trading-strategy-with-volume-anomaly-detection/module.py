"""Four-hour bars: four anchored VWAPs (from the first bar, from the latest year-to-date high, from the latest year-to-date low, and from the latest record volume bar above twice its 20-bar average); a bar that closes back above one of them after trading below it goes long, one that closes back under after trading above goes short (unless the open gapped across it); the last such call of the bar wins; RSI 14 over 70 closes a long, under 30 a short; reversing.
Port of FMZ strategy #453659 "VWAP交易策略与成交量异常监测VWAP-Trading-Strategy-with-Volume-Anomaly-Detection" (5 Anchored VWAP Strategy with Abnormally High Volume Candle).

FMZ source id: 453659

Source
    https://www.fmz.com/strategy/453659 (PineScript v5, FMZ last modified 2024-06-07 15:44:04).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 105-309), anchors: data start, YTD high, YTD low, abnormal volume (2 x SMA 20); RSI 14, 70 / 30
    vwap_open = cum(close x volume) / cum(volume) from the first bar;  vwap_high / vwap_low restart on bars with high == ytd_high / low == ytd_low;  vwap_high_volume restarts on a new record volume above 2 x avg
    not gap: close > vwap and low < vwap -> entry Long_*;  close < vwap and high > vwap -> entry Short_*  (8 calls);  long and rsi > 70 -> close all longs;  short and rsi < 30 -> close all shorts

Interpretation choices (Pine rules in SURVEY_README.md)
    * The first-bar VWAP never restarts and the record-volume level never decays, so both depend on
      where the data starts, as written (weird case, as #437032). Years and YTD resets are read in UTC.
      The VWAPs weigh the close. With several entry calls on one bar the last one decides the position
      (each ignores a position already on its side). The displaced levels only feed the debug plots. A
      close acts only on a position the bar's entries leave unchanged. REVERSAL INTENDED. No sizing code.
      FREQ = "4h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, wick and cross re-tests of four anchored VWAPs, RSI exits.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) as the weights of the four anchored VWAPs and in the record-volume anchor test; exchange volume to be compared later (Austin, 2026-10-23).
Session open: years in UTC (header exchange time) for the YTD anchors.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_453659_four_anchored_vwaps_retest_rsi_exit_4h_reversal"
FAMILY = "vwap_breakout"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "vol_thresh": [2.0, 3.0],
    "rsi_ob": [70.0, 80.0],
}
DEFAULT_PARAMS = {"vol_len": 20, "vol_thresh": 2.0, "rsi_len": 14, "rsi_ob": 70.0}


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


def _rsi(x, n):
    d = x.diff()
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    out = 100 - 100 / (1 + up / dn.where(dn != 0))
    return out.where(up != 0, 0.0).where(dn != 0, 100.0).where(up.notna() & dn.notna())


def _vwaps(bars_df, p):
    o, h, lo, c, v = (bars_df[k].to_numpy(dtype=float) for k in ("open", "high", "low", "close", "volume"))
    avg = bars_df["volume"].rolling(int(p["vol_len"])).mean().to_numpy()
    years = np.asarray(bars_df.index.year)
    m = len(c)
    out = np.full((4, m), np.nan)
    cv = np.zeros(4)
    cpv = np.zeros(4)
    ytd_h = ytd_l = np.nan
    rec_v = 0.0
    thr = float(p["vol_thresh"])
    for i in range(m):
        if i > 0 and years[i] != years[i - 1]:
            ytd_h, ytd_l = h[i], lo[i]
        ytd_h = h[i] if np.isnan(ytd_h) else max(ytd_h, h[i])
        ytd_l = lo[i] if np.isnan(ytd_l) else min(ytd_l, lo[i])
        if h[i] == ytd_h:
            cv[1] = cpv[1] = 0.0
        if lo[i] == ytd_l:
            cv[2] = cpv[2] = 0.0
        if v[i] > rec_v and v[i] > thr * avg[i]:
            rec_v = v[i]
            cv[3] = cpv[3] = 0.0
        cv += v[i]
        cpv += c[i] * v[i]
        for k in range(4):
            if cv[k] != 0:
                out[k, i] = cpv[k] / cv[k]
            elif i > 0:
                out[k, i] = out[k, i - 1]
    return out


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c = (bars_df[k].to_numpy(dtype=float) for k in ("open", "high", "low", "close"))
    vw = _vwaps(bars_df, p)
    rsi = _rsi(bars_df["close"], int(p["rsi_len"])).to_numpy()
    ob = float(p["rsi_ob"])
    m = len(c)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        final = 0
        for k in range(4):
            w = vw[k, i]
            if i == 0 or np.isnan(w):
                gap = False
            else:
                gap = ((o[i] > c[i - 1] and o[i] < w and c[i - 1] > w) or (o[i] < c[i - 1] and o[i] > w and c[i - 1] < w))
            if not gap:
                if c[i] > w and lo[i] < w:
                    final = 1
                if c[i] < w and h[i] > w:
                    final = -1
        new = pos
        if final == 1 and new != 1:
            new = 1
        elif final == -1 and new != -1:
            new = -1
        if new == pos:
            if pos == 1 and rsi[i] > ob:
                new = 0
            elif pos == -1 and rsi[i] < 100 - ob:
                new = 0
        if new != pos:
            if new == 1:
                le[i] = True
            elif new == -1:
                se[i] = True
            elif pos == 1:
                lx[i] = True
            else:
                sx[i] = True
            pos = new
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {}
