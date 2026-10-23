"""Elder force-index pullbacks (Wilder 15 of change x volume against its trend Wilder 120) with ADX 20 and an EMA 50 high / low channel, hourly bars: a negative but rising short force in a positive long force with the open under the EMA of highs (and the Wilder 10 of hlc3 at or above the EMA of lows) goes long, the mirror goes short, each with a target 4 ATR 14 beyond and a stop 8 ATR 14 behind the signal bar's high / low; reversing.
Port of FMZ strategy #427279 "基于ADX-EFI指标的趋势回调策略ADX-EFI-50-Moving-Average-Channel-Pullback-Strategy" (adx efi 50 ema channel, trend pullback).

FMZ source id: 427279

Source
    https://www.fmz.com/strategy/427279 (PineScript v5, FMZ last modified 2023-09-19 17:10:51).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 159-230), EFI rma 15 / 120 of change(close) x volume; DMI 20 / 20, ADX >= 20; EMA 50 of high / low; rma(hlc3, 10); ATR 14 x 4 / 8; strategy() commented out
    buy = efi2 > 0 and efi < 0 and efi[1] < efi and adx >= 20 and open < ema(high, 50);  sell mirror (open > ema(low, 50))
    buy: entry buy when rma(hlc3, 10) >= ema(low, 50), exit(limit = high + 4 atr, stop = low - 8 atr);  sell: entry sell when rma(hlc3, 10) <= ema(high, 50), exit(limit = low - 4 atr, stop = high + 8 atr)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The exit levels are prices fixed on the signal bar; the port gives them as fractions of the fill. A
      later signal bar re-sends them at new levels while the position is open (the house bracket keeps the
      first: mark trailing_stop_pending). strategy.close("close") names an id that is never entered, so it
      never acts. The Bollinger, SAR, MACD, RSI, stochastic and WMA lines only feed plots or comments.
      REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4). strategy() is commented out (no
      sizing). FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; ATR bracket from the signal bar.
    2 generic: PASS, force-index pullbacks in an ADX trend.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the commented strategy() (margin 100, capital 100000) stored, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) in both force indexes rma(change(close) x volume); exchange volume to be compared later (Austin, 2026-10-23).
Session open: not used.
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_427279_efi15_120_pullback_adx20_ema50_channel_atr_bracket_reversal"
FAMILY = "force_index"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "efi_fast": [15, 8],
    "adx_min": [20.0, 25.0],
}
DEFAULT_PARAMS = {"efi_fast": 15, "adx_min": 20.0, "efi_slow": 120, "atr_len": 14, "tp_atr": 4.0, "sl_atr": 8.0}


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


def _adx(b, n, nsig):
    h, lo, c = b["high"], b["low"], b["close"]
    up, dn = h.diff(), -lo.diff()
    pdm = up.where((up > dn) & (up > 0), 0.0).where(up.notna())
    mdm = dn.where((dn > up) & (dn > 0), 0.0).where(dn.notna())
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1).where(pc.notna())
    trr = _rma(tr, n)
    plus = _fixnan(100 * _rma(pdm, n) / trr)
    minus = _fixnan(100 * _rma(mdm, n) / trr)
    s = plus + minus
    return 100 * _rma((plus - minus).abs() / s.where(s != 0, 1.0), nsig)


def _signals(bars_df, p):
    o, h, lo, c, v = (bars_df[k] for k in ("open", "high", "low", "close", "volume"))
    force = c.diff() * v
    efi, efi2 = _rma(force, int(p["efi_fast"])), _rma(force, int(p["efi_slow"]))
    adx = _adx(bars_df, 20, 20)
    ehi, elo = h.ewm(span=50, adjust=False).mean(), lo.ewm(span=50, adjust=False).mean()
    e34 = _rma((h + lo + c) / 3, 10)
    am = float(p["adx_min"])
    buy = (efi2 > 0) & (efi < 0) & (efi.shift(1) < efi) & (adx >= am) & (o < ehi)
    sell = (efi2 < 0) & (efi > 0) & (efi.shift(1) > efi) & (adx >= am) & (o > elo)
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)   # first bar: high - low
    atr = _rma(tr, int(p["atr_len"]))
    return buy & (e34 >= elo), sell & (e34 <= ehi), atr


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, _ = _signals(bars_df, p)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se & ~le, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, atr = _signals(bars_df, p)
    o, h, lo = bars_df["open"], bars_df["high"], bars_df["low"]
    a1, h1, l1 = atr.shift(1), h.shift(1), lo.shift(1)
    kt, ks = float(p["tp_atr"]), float(p["sl_atr"])
    lf, sf = le.shift(1, fill_value=False), (se & ~le).shift(1, fill_value=False)
    sl_l, tp_l = 1 - (l1 - ks * a1) / o, (h1 + kt * a1) / o - 1
    sl_s, tp_s = (h1 + ks * a1) / o - 1, 1 - (l1 - kt * a1) / o
    sl_f = sl_l.where(lf, sl_s.where(sf))
    tp_f = tp_l.where(lf, tp_s.where(sf))
    return {"sl_stop": sl_f.where(sl_f > 0), "tp_stop": tp_f.where(tp_f > 0)}


def portfolio_kwargs(**params):
    return {}
