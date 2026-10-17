"""Tenkan / Kijun crosses with an ADX filter, 1-hour bars: the Tenkan 18 crossing above the Kijun 58 with the ADX 14 above
12 goes long, the cross down with the same filter goes short (reversing).
Port of FMZ strategy #434704 "基于一小时TENKAN-KIJUN交叉的ADX趋势跟踪策略ADX-Based-One-Hour-TENKAN-KIJUN-Cross-Trend-Tracking-Strategy" (Odin's Kraken (TK Cross Strategy)).

FMZ source id: 434704

Source
    https://www.fmz.com/strategy/434704 (PineScript v2, FMZ last modified 2023-12-08 15:37:00).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 181-256), Tenkan 18, Kijun 58; ADX 14 / 14 with the code's level 12 (the threshold input 20 is unused); date filter off
    crossover(tenkan, kijun) and adx > 12 -> entry long;  crossunder(tenkan, kijun) and adx > 12 -> entry short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The ADX is Pine's: rma-smoothed DI (fixnan) and an rma of the DI spread over its sum. The
      code compares with 12, not the threshold input: as written. time_cond is always true.
      strategy.entry reverses: REVERSAL INTENDED. The 100 % of equity is sizing. FREQ = "1h" from
      the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, Donchian-midline crosses and an ADX level.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the strategy() 100 % of equity stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_434704_tk_cross_adx"
FAMILY = "ichimoku"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "tenkan": [18, 9],
    "adx_min": [12, 25],
}
DEFAULT_PARAMS = {"tenkan": 18, "kijun": 58, "adx_len": 14, "di_len": 14, "adx_min": 12}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _fixnan(v, index):
    """Pine fixnan: a NaN (or inf) takes the last valid value before it (past values only)."""
    out = np.array(v, dtype=float)
    last = np.nan
    for i in range(len(out)):
        if np.isfinite(out[i]):
            last = out[i]
        else:
            out[i] = last
    return pd.Series(out, index=index)


def _adx(h, lo, c, di_len, adx_len):
    up, dn = h.diff(), -lo.diff()
    c1 = c.shift(1)
    tr = pd.concat([h - lo, (h - c1).abs(), (lo - c1).abs()], axis=1).max(axis=1)
    tr.iloc[0] = np.nan
    rma = lambda x, n: x.ewm(alpha=1 / n, adjust=False).mean()  # noqa: E731
    trur = rma(tr, di_len)
    pdm = pd.Series(np.where((up > dn) & (up > 0), up, 0.0), index=c.index).where(up.notna())
    ndm = pd.Series(np.where((dn > up) & (dn > 0), dn, 0.0), index=c.index).where(dn.notna())
    plus = _fixnan((100 * rma(pdm, di_len) / trur).to_numpy(), c.index)
    minus = _fixnan((100 * rma(ndm, di_len) / trur).to_numpy(), c.index)
    s = plus + minus
    return 100 * rma((plus - minus).abs() / s.where(s != 0, 1.0), adx_len)


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    don = lambda n: (lo.rolling(n).min() + h.rolling(n).max()) / 2  # noqa: E731
    t, k = don(int(p["tenkan"])), don(int(p["kijun"]))
    adx = _adx(h, lo, c, int(p["di_len"]), int(p["adx_len"]))
    ok = adx > float(p["adx_min"])
    le = ((t > k) & (t.shift(1) <= k.shift(1)) & ok).astype(bool)
    se = ((t < k) & (t.shift(1) >= k.shift(1)) & ok).astype(bool)
    false = pd.Series(False, index=bars_df.index)
    return le, false, se, false.copy()


def portfolio_kwargs(**params):
    return {}
