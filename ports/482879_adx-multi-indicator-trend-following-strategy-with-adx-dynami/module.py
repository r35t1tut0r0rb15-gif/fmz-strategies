"""RSI 14 leaving oversold (overbought) in an EMA 20 / 50 trend with ADX above 20, with a 1.5 ATR stop and a 2 R
target, 1-minute bars: in an up-trend, RSI crossing above 30 goes long; in a down-trend, RSI crossing below 70 goes
short.
Port of FMZ strategy #482879 "多指标综合趋势跟踪策略结合ADX动态交易系统-Multi-Indicator-Trend-Following-Strategy-with-ADX-Dynamic-Trading-System" (Enhanced GBP/USD Strategy with ADX).

FMZ source id: 482879

Source
    https://www.fmz.com/strategy/482879 (PineScript v5, FMZ last modified 2025-02-20 16:20:04).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 102-151), EMA 20 / 50, RSI 14 (70 / 30), ATR 14, ADX 14, RR 2, SL 1.5 ATR
    +DM = rma(max(high - high[1], 0)), -DM = rma(max(low[1] - low, 0)) (the source's own), adx = rma(dx, 14)
    buy = ema20 > ema50 and adx > 20 and crossover(rsi, 30); sell = ema20 < ema50 and adx > 20 and crossunder(rsi, 70)
    entry + exit(stop = close -+ 1.5 ATR, limit = close +- 3 ATR)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The ADX is the source's own (no up / down comparison), as written.
    * The bracket is fixed at the signal bar: 1.5 ATR / close and RR x that, shifted one bar inside stops() and re-based
      on the fill (house rule). A same-side signal while held re-places it: mark trailing_stop_pending.
    * Entries reverse (REVERSAL INTENDED). Stop module: portfolio_kwargs {} (D4). FREQ = "1min" from the backtest
      header ("GBP/USD" in the title is a label).

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket from the signal bar (re-placement marked).
    2 generic: PASS, moving averages, RSI, ADX and ATR multiples.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 1 % of equity quoted; the bracket ported via stops() and quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_482879_rsi_exit_extreme_ema_adx_atr_rr"
FAMILY = "mean_reversion"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sl_mult": [1.5, 2.5],
    "rr": [2.0, 3.0],
}
DEFAULT_PARAMS = {"fast": 20, "slow": 50, "rsi_len": 14, "atr_len": 14, "adx_len": 14, "sl_mult": 1.5, "rr": 2.0}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
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
    r = 100 - 100 / (1 + up / dn)
    r = r.where(up != 0, 0.0)
    return r.where(dn != 0, 100.0).where(up.notna() & dn.notna())


def _tr(bars_df):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]   # Pine's first true range is high - low
    return tr


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["adx_len"])
    trs = _rma(_tr(bars_df), n)
    pdi = _rma(h.diff().clip(lower=0), n) / trs * 100
    mdi = _rma((-lo.diff()).clip(lower=0), n) / trs * 100
    adx = _rma((pdi - mdi).abs() / (pdi + mdi) * 100, n)
    f = c.ewm(span=int(p["fast"]), adjust=False).mean()
    s = c.ewm(span=int(p["slow"]), adjust=False).mean()
    rsi = _rsi(c, int(p["rsi_len"]))
    up, dn = (f > s) & (adx > 20), (f < s) & (adx > 20)
    long_e = (up & (rsi > 30) & (rsi.shift(1) <= 30)).astype(bool)
    short_e = (dn & (rsi < 70) & (rsi.shift(1) >= 70)).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return long_e, false, short_e, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    sl = (p["sl_mult"] * _rma(_tr(bars_df), int(p["atr_len"])) / bars_df["close"]).shift(1)
    return {"sl_stop": sl, "tp_stop": p["rr"] * sl}


def portfolio_kwargs(**params):
    return {}
