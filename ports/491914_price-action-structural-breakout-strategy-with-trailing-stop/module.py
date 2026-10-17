"""Break of structure at a pivot zone with a candle, RSI and CCI filter and an ATR trail, 2-minute bars: the close
crossing above the last confirmed swing high while near the last swing low, on a bullish candle shape, with the close
above the EMA 20 or EMA 200, RSI > 50 and CCI > 0, goes long; the mirror goes short; exits by a trailing stop only.
Port of FMZ strategy #491914 "价格行为结构突破-跟踪止损策略-Price-Action-Structural-Breakout-Strategy-with-Trailing-Stop" (SMC + EMA + Candles + RSI/CCI + BOS + Trailing).

FMZ source id: 491914

Source
    https://www.fmz.com/strategy/491914 (PineScript v6, FMZ last modified 2025-04-24 18:25:06).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C laptop lane).

Original signal (original_source.md lines 100-164), EMA 20 / 200, RSI 14, CCI 20, ATR 14, pivots 10 / 10
    supply = the last pivothigh(high, 10, 10); demand = the last pivotlow(low, 10, 10)
    bos_long = crossover(close, supply); near_demand = demand x 0.98 <= close <= demand x 1.01
    bull_candle = engulfing or "pinbar" (upper wick > 2 x lower wick) or marubozu (wicks < 0.1 ATR) or doji
    long = (close > ema20 or close > ema200) and near_demand and bull_candle and bos_long and rsi > 50 and cci > 0
    short = the mirror (near_supply = supply x 0.99 <= close <= supply x 1.02, crossunder(close, demand), ...)
    on entry: exit(trail_points = ATR x 1.0, trail_offset = ATR x 0.5), no other exit

Interpretation choices (Pine rules in SURVEY_README.md)
    * pivothigh / pivotlow(10, 10): the high (low) 10 bars back strictly above (below) the 10 before and the 10
      after (ties are not pivots), known 10 bars later; the zone keeps its last value. The crosses compare with the
      zone's value on the previous bar, as Pine's crossover.
    * The candle shapes as written (the "bull pinbar" is a long UPPER wick; a doji counts for both sides).
      CCI = (close - SMA 20) / (0.015 x mean absolute deviation over 20).
    * The trail: trail_points / trail_offset take TICKS, but the author passes ATR price distances; read as the
      author evidently meant (as #427592): price distances. Ported natively (mark trailing_stop): {"type":
      "volatility", "atr_n": 14, "k": 0.5, "anchor": "high_low", "activate_after": 0.0015}. Stated approximations:
      Pine fixes both distances at the entry bar's ATR, the house trail uses the ATR of the last completed bar; the
      1-ATR activation becomes a 0.15 % gain (about one 2-minute ATR on the author's DOGE_USDT; judgement before any
      backtest).
    * Entries reverse (REVERSAL INTENDED); on the rare bar with both signals the short (written last) wins.
    * Stop module: portfolio_kwargs {} (driver D4). FREQ = "2min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; pivots confirmed after their right bars; the trail is a house trail (approximations stated).
    2 generic: PASS, percentage proximity bands, ATR-scaled candle tests, oscillators.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 10 % of equity quoted; the trail ported via stops() and quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: trailing_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_491914_smc_bos_candles_atr_trail"
FAMILY = "price_action_breakout"  # proposed 2026-10-17 (FMZ-C laptop lane), user to confirm
FREQ = "2min"  # backtest header period: 2m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "trail_k": [0.5, 1.0],
    "trail_activate": [0.0015, 0.003],
}
DEFAULT_PARAMS = {"pivot": 10, "rsi_len": 14, "cci_len": 20, "atr_len": 14, "trail_k": 0.5,
                  "trail_activate": 0.0015}


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


def _rsi(c, n):
    d = c.diff()
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    r = 100 - 100 / (1 + up / dn)
    r = r.where(up != 0, 0.0)
    return r.where(dn != 0, 100.0).where(up.notna() & dn.notna())


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]   # Pine's first true range is high - low
    return _rma(tr, n)


def _cci(c, n):
    sma = c.rolling(n).mean()
    mad = c.rolling(n).apply(lambda w: np.abs(w - w.mean()).mean(), raw=True)
    return (c - sma) / (0.015 * mad)


def _last_pivot(x, n, high):
    """The value of the last confirmed pivot (strict, n left / n right bars), held until the next one."""
    m = len(x)
    out = np.full(m, np.nan)
    cur = np.nan
    for t in range(m):
        j = t - n
        if j - n >= 0:
            v = x[j]
            left, right = x[j - n:j], x[j + 1:t + 1]
            if not (np.isnan(v) or np.isnan(left).any() or np.isnan(right).any()):
                if (high and v > left.max() and v > right.max()) or (not high and v < left.min() and v < right.min()):
                    cur = v
        out[t] = cur
    return out


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c = (bars_df[x] for x in ("open", "high", "low", "close"))
    idx = bars_df.index
    ema20, ema200 = c.ewm(span=20, adjust=False).mean(), c.ewm(span=200, adjust=False).mean()
    rsi, cci = _rsi(c, int(p["rsi_len"])), _cci(c, int(p["cci_len"]))
    atr = _atr(bars_df, int(p["atr_len"]))
    top, bot = np.maximum(o, c), np.minimum(o, c)
    bull_engulf = (c.shift(1) < o.shift(1)) & (c > o) & (c > o.shift(1)) & (o <= c.shift(1))
    bear_engulf = (c.shift(1) > o.shift(1)) & (c < o) & (c < o.shift(1)) & (o >= c.shift(1))
    bull_pin = (h - top) > 2 * (bot - lo)
    bear_pin = (bot - lo) > 2 * (h - top)
    doji = (c - o).abs() <= (h - lo) * 0.1
    bull_maru = (c > o) & (h - c < atr * 0.1) & (o - lo < atr * 0.1)
    bear_maru = (o > c) & (h - o < atr * 0.1) & (c - lo < atr * 0.1)
    bull_candle = bull_engulf | bull_pin | bull_maru | doji
    bear_candle = bear_engulf | bear_pin | bear_maru | doji
    n = int(p["pivot"])
    supply = pd.Series(_last_pivot(h.to_numpy(dtype=float), n, True), index=idx)
    demand = pd.Series(_last_pivot(lo.to_numpy(dtype=float), n, False), index=idx)
    bos_long = (c > supply) & (c.shift(1) <= supply.shift(1))
    bos_short = (c < demand) & (c.shift(1) >= demand.shift(1))
    near_demand = (c >= demand * 0.98) & (c <= demand * 1.01)
    near_supply = (c <= supply * 1.02) & (c >= supply * 0.99)
    long_c = ((c > ema20) | (c > ema200)) & near_demand & bull_candle & bos_long & (rsi > 50) & (cci > 0)
    short_c = ((c < ema20) | (c < ema200)) & near_supply & bear_candle & bos_short & (rsi < 50) & (cci < 0)
    long_c, short_c = long_c.fillna(False).astype(bool), short_c.fillna(False).astype(bool)
    false = pd.Series(False, index=idx)
    return (long_c & ~short_c).astype(bool), false, short_c, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"trail": {"type": "volatility", "atr_n": int(p["atr_len"]), "k": float(p["trail_k"]),
                      "anchor": "high_low", "activate_after": float(p["trail_activate"])}}


def portfolio_kwargs(**params):
    return {}
