"""Hourly bars: ADX 21 above 26 with DI+ over DI- on volume above 1.8 x its 20-bar average goes long, with DI- over DI+ on such volume goes short; the opposite signal reverses.
Port of FMZ strategy #471664 "ADX-Average-Directional-Index-和交易量趋势动态跟踪策略-ADX-Average-Directional-Index-and-Volume-Dynamic-Trend-Tracking-Strategy" (ADX + Volume Strategy).

FMZ source id: 471664

Source
    https://www.fmz.com/strategy/471664 (PineScript v5, FMZ last modified 2024-11-12 11:00:17).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 94-132), ta.dmi(21, 21); ADX > 26; volume SMA 20 x 1.8
    longCondition = adx > 26 and diPlus > diMinus and volume > avgVolume * 1.8 -> entry Long
    shortCondition = adx > 26 and diMinus > diPlus and volume > avgVolume * 1.8 -> entry Short
    position_size > 0 and shortCondition -> close Long;  position_size < 0 and longCondition -> close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The closes only repeat what the opposite entry already does (it reverses), so the strategy is
      always in the market after its first signal. ta.dmi uses Wilder RMAs of the directional moves over
      the RMA of the true range, and 100 x RMA of |DI+ - DI-| / (DI+ + DI-, 1 when 0). REVERSAL INTENDED.
      No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, ADX trend strength with DI direction on high volume.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) against 1.8 x its SMA 20; exchange volume to be compared later (Austin, 2026-10-23).
Session open: none (24 h).
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_471664_adx21_di_volume_1_8x_1h_reversal"
FAMILY = "adx_trend"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "adx_len": [21, 14],
    "adx_min": [26.0, 20.0],
}
DEFAULT_PARAMS = {"adx_len": 21, "adx_min": 26.0, "vol_mult": 1.8}


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
    """Pine fixnan: a NaN takes the last non-NaN value (Pine's own indicator semantics)."""
    v = x.to_numpy(dtype=float).copy()
    last = np.nan
    for i in range(len(v)):
        if np.isnan(v[i]):
            v[i] = last
        else:
            last = v[i]
    return pd.Series(v, index=x.index)


def _dmi(h, lo, c, n, sm):
    up, dn = h.diff(), -lo.diff()
    pdm = up.where((up > dn) & (up > 0), 0.0).where(up.notna())
    mdm = dn.where((dn > up) & (dn > 0), 0.0).where(dn.notna())
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1).where(pc.notna())
    trur = _rma(tr, n)
    plus, minus = _fixnan(100 * _rma(pdm, n) / trur), _fixnan(100 * _rma(mdm, n) / trur)
    tot = plus + minus
    adx = 100 * _rma((plus - minus).abs() / tot.where(tot != 0, 1.0), sm)
    return plus, minus, adx


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c, v = bars_df["high"], bars_df["low"], bars_df["close"], bars_df["volume"]
    n = int(p["adx_len"])
    plus, minus, adx = _dmi(h, lo, c, n, n)
    vol_ok = v > v.rolling(20).mean() * float(p["vol_mult"])
    strong = adx > float(p["adx_min"])
    buy = strong & (plus > minus) & vol_ok
    sell = strong & (minus > plus) & vol_ok
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return buy.astype(bool), false, sell.astype(bool), false.copy()


def portfolio_kwargs(**params):
    return {}
