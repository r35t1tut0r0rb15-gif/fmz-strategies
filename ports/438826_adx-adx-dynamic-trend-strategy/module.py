"""Rising ADX trend entries, 10-minute bars: the ADX 14 rising over 3 bars above 23 with DI+ over DI- and the close at or above the EMA 200 goes long, the DI- mirror at or under the EMA 200 goes short;
reversing; a falling ADX (against 3 bars back) closes either side.
Port of FMZ strategy #438826 "ADX动态平均趋势指标策略ADX-Dynamic-Trend-Strategy" (ADX | DMI Trend).

FMZ source id: 438826

Source
    https://www.fmz.com/strategy/438826 (PineScript v4, FMZ last modified 2024-01-15 15:32:45).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 186-240), ADX smoothing 14, DI 14; key level 23; slope lookback 3; MA filter EMA 200; dates from 2019; 100 % of equity, commission 0.04 %
    buy = adx - adx[3] > 0 and adx > 23 and di+ > di- and close >= ema 200 -> entry Long;  short = the same rising ADX with di+ < di- and close <= ema 200 -> entry Short;  adx - adx[3] < 0 -> close Long, close Short

Interpretation choices (Pine rules in SURVEY_README.md)
    * The DMI is Pine's built-in dmi(14, 14) (Wilder smoothing). The date window starts 2019 and never
      ends; it is treated as always true (as #436533). strategy.entry reverses: REVERSAL INTENDED. The
      size, capital and commission are sizing / costs. FREQ = "10min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, ADX slope and DI lines.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent-of-equity size, capital and commission stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: DG438826 (2 members, best partner #438952, Jaccard 1.000); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_438826_adx_slope_dmi_ema200"
FAMILY = "directional_movement"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "10min"  # backtest header period: 10m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "key_level": [23, 30],
    "ma_length": [200, 100],
}
DEFAULT_PARAMS = {"key_level": 23.0, "ma_length": 200, "adx_len": 14, "di_len": 14, "lookback": 3}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


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


def _dmi(h, lo, c, di_len, adx_len):
    up = h.diff()
    down = -lo.diff()
    plus_dm = pd.Series(np.where((up > down) & (up > 0), up, 0.0), index=h.index).where(up.notna())
    minus_dm = pd.Series(np.where((down > up) & (down > 0), down, 0.0), index=h.index).where(down.notna())
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    trr = _rma(tr, di_len)
    with np.errstate(divide="ignore", invalid="ignore"):
        plus = 100 * _rma(plus_dm, di_len) / trr
        minus = 100 * _rma(minus_dm, di_len) / trr
    s = plus + minus
    adx = 100 * _rma((plus - minus).abs() / s.where(s != 0, 1.0), adx_len)
    return plus, minus, adx


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    plus, minus, adx = _dmi(h, lo, c, int(p["di_len"]), int(p["adx_len"]))
    k = int(p["lookback"])
    slope = adx - adx.shift(k)
    ema = c.ewm(span=int(p["ma_length"]), adjust=False).mean()
    lvl = float(p["key_level"])
    buy = (slope > 0) & (adx > lvl) & (plus > minus) & (c >= ema)
    sell = (slope > 0) & (adx > lvl) & (plus < minus) & (c <= ema)
    cover = slope < 0
    return buy, cover & ~sell, sell, cover & ~buy


def portfolio_kwargs(**params):
    return {}
