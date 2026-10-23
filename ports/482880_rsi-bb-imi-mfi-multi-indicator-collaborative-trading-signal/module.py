"""Hourly bars: RSI 14 under 30 with the close under the lower Bollinger band (20, 2), the intraday momentum index 14 under 30 and MFI 14 under 20 goes long; RSI over 70 with the close above the band BASIS (the script's "bbUpper"), IMI over 70 and MFI over 80 goes short; the opposite signal reverses.
Port of FMZ strategy #482880 "RSI BB IMI MFI Multi Indicator Collaborative Trading Signal Generation Strategy RSI BB IMI MFI" (Clear Buy/Sell Signals with RSI, Bollinger Bands, IMI, and MFI).

FMZ source id: 482880

Source
    https://www.fmz.com/strategy/482880 (PineScript v5, FMZ last modified 2025-02-20 16:23:35).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 122-167), RSI 14; BB 20 x 2 (destructured as [bbUpper, bbMiddle, bbLower] = [basis, upper, lower]); IMI 14; MFI 14 of hlc3
    [bbUpper, bbMiddle, bbLower] = ta.bb(close, 20, 2)  (ta.bb returns middle, upper, lower)
    buyCondition = rsi < 30 and close < bbLower and imi < 30 and mfi < 20 (or the stricter strong buy) -> entry Buy
    sellCondition = rsi > 70 and close > bbUpper and imi > 70 and mfi > 80 (or the stricter strong sell) -> entry Sell

Interpretation choices (Pine rules in SURVEY_README.md)
    * ta.bb returns [middle, upper, lower], so the script's "bbUpper" is the basis and its "bbLower" the
      real lower band: the sell needs a close above the basis only (weird case). The strong signals are
      subsets of the plain ones. ta.mfi(hlc3, 14) sums volume x hlc3 over up / down hlc3 changes; its
      division by zero is na. IMI = sum of up bodies / sum of all bodies over 14 bars. Entries only; an
      opposite entry reverses. REVERSAL INTENDED. No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, four-oscillator oversold / overbought agreement.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) in the MFI 14; exchange volume to be compared later (Austin, 2026-10-23).
Session open: none (24 h).
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_482880_rsi_bb_imi_mfi_extreme_agreement_1h_reversal"
FAMILY = "oscillator_agreement"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "rsi_lo": [30.0, 35.0],
    "mfi_lo": [20.0, 30.0],
}
DEFAULT_PARAMS = {"rsi_lo": 30.0, "mfi_lo": 20.0, "imi_lo": 30.0}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c, v = (bars_df[k] for k in ("open", "high", "low", "close", "volume"))
    r = _rsi(c, 14)
    basis, dev = c.rolling(20).mean(), 2.0 * c.rolling(20).std(ddof=0)
    lower = basis - dev
    up_b = (c - o).where(c > o, 0.0).rolling(14).sum()
    dn_b = (o - c).where(c < o, 0.0).rolling(14).sum()
    imi = up_b / (up_b + dn_b).where((up_b + dn_b) != 0) * 100
    src = (h + lo + c) / 3
    chg = src.diff()
    pos_f = (v * src.where(~(chg <= 0), 0.0)).rolling(14).sum()
    neg_f = (v * src.where(~(chg >= 0), 0.0)).rolling(14).sum()
    mfi = 100.0 - 100.0 / (1.0 + pos_f / neg_f.where(neg_f != 0))
    rl, ml, il = float(p["rsi_lo"]), float(p["mfi_lo"]), float(p["imi_lo"])
    buy = (r < rl) & (c < lower) & (imi < il) & (mfi < ml)
    sell = (r > 100 - rl) & (c > basis) & (imi > 100 - il) & (mfi > 100 - ml)   # "bbUpper" is the basis
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return buy.astype(bool), false, sell.astype(bool), false.copy()


def portfolio_kwargs(**params):
    return {}
