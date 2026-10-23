"""2-hour bars: a bullish engulfing candle (or a hammer at the 10-bar low in an EMA 20 > 50 uptrend) above the 14-bar low, on a volume spike (1.5 x and the previous bar 1.2 x the 20-bar average) with ADX 14 over 20, goes long with a 2 ATR stop and 3 ATR target from the signal close; the bearish mirror goes short; reversing.
Port of FMZ strategy #488018 "Multi Factor Trend Price Action Strategy with Dynamic Risk Management System" (Prism Confluence System).

FMZ source id: 488018

Source
    https://www.fmz.com/strategy/488018 (PineScript v6, FMZ last modified 2025-03-24 14:11:32).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 291-403), EMA 20 / 50; S/R 14; engulfing / hammer / inverted hammer; "FVG" low[10] > high[1] < low; volume SMA 20 x 1.5 / 1.2; DMI 14, ADX > 20; ATR 14 x 2 / 3
    weakBuy = (engulfingBull or hammer) and close > lowest(low, 14) and volumeSpike and adx > 20;  strongBuy = fvgBull and barssince(fvgBull) <= 5 and engulfingBull and trendBullish and volumeSpike and adx > 20
    strongBuy or weakBuy -> entry Long, exit(stop = close - 2 atr, limit = close + 3 atr);  sells mirrored -> entry Short, exit(stop = close + 2 atr, limit = close - 3 atr)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The strong signals are subsets of the weak ones (an engulfing candle on the same volume and ADX
      tests), so the weak set-ups decide. The bracket is sent on signal bars as levels from that close:
      ported as fractions of the fill, exact (1e-6 floor); repeats while in the trade re-send it (not
      followed: trailing_stop_pending). The engulfing test needs a body larger than the previous one. The
      header names BNB_USDT; the rules are generic. REVERSAL INTENDED. No sizing code. Stop module:
      portfolio_kwargs {} (driver D4). Stops on 2-hour bars: coarse_bar_stop. FREQ = "2h" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; ATR bracket at the signal close as fractions of the fill.
    2 generic: PASS, engulfing / hammer set-ups on volume spikes in trending markets.
    3 crypto-exchange-only: no (exchange pair in the header only (BNB_USDT)).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) against 1.5 x (and the previous bar 1.2 x) its SMA 20; exchange volume to be compared later (Austin, 2026-10-23).
Session open: none (24 h).
REVERSAL INTENDED.

Marks: coarse_bar_stop, trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_488018_prism_engulf_hammer_volume_adx_atr_bracket_2h_reversal"
FAMILY = "candlestick_pattern"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "2h"  # backtest header period: 2h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sl_atr": [2.0, 1.5],
    "tp_atr": [3.0, 4.0],
}
DEFAULT_PARAMS = {"sl_atr": 2.0, "tp_atr": 3.0}


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


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    return _rma(pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1), n)


def _recent(flag, k):
    """ta.barssince(flag) <= k (the current bar counts as 0; never true -> na -> false)."""
    f = np.asarray(flag)
    out = np.zeros(len(f), dtype=bool)
    last = -10**9
    for i in range(len(f)):
        if f[i]:
            last = i
        out[i] = i - last <= k
    return out


def simulate(bars_df, **params):
    o, h, lo, c, v = (bars_df[k] for k in ("open", "high", "low", "close", "volume"))
    e20, e50 = c.ewm(span=20, adjust=False).mean(), c.ewm(span=50, adjust=False).mean()
    bull_t, bear_t = e20 > e50, e20 < e50
    o1, c1 = o.shift(1), c.shift(1)
    eng_b = (c > o) & (c1 < o1) & (c > o1) & (o < c1) & ((c - o) > (o1 - c1))
    eng_s = (c < o) & (c1 > o1) & (c < o1) & (o > c1) & ((o - c) > (c1 - o1))
    rng = h - lo
    hamm = (lo == lo.rolling(10).min()) & (c > o) & ((c - lo) > rng * 0.6) & bull_t
    ihamm = (h == h.rolling(10).max()) & (c < o) & ((h - c) > rng * 0.6) & bear_t
    fvg_b = (lo.shift(10) > h.shift(1)) & (h.shift(1) < lo)
    fvg_s = (h.shift(10) < lo.shift(1)) & (lo.shift(1) > h)
    vma = v.rolling(20).mean()
    spike = (v > vma * 1.5) & (v.shift(1) > vma.shift(1) * 1.2)
    _, _, adx = _dmi(h, lo, c, 14, 14)
    trending = adx > 20
    strong_b = fvg_b & pd.Series(_recent(fvg_b.to_numpy(), 5), index=c.index) & eng_b & bull_t & spike & trending
    weak_b = (eng_b | hamm) & (c > lo.rolling(14).min()) & spike & trending
    strong_s = fvg_s & pd.Series(_recent(fvg_s.to_numpy(), 5), index=c.index) & eng_s & bear_t & spike & trending
    weak_s = (eng_s | ihamm) & (c < h.rolling(14).max()) & spike & trending
    sell = strong_s | weak_s
    buy = (strong_b | weak_b) & ~sell        # the later short call wins on a two-sided bar
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return buy.astype(bool), false, sell.astype(bool), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, lx, se, sx = simulate(bars_df, **params)
    o, c = bars_df["open"], bars_df["close"]
    atr = _atr(bars_df, 14)
    sl_d, tp_d = float(p["sl_atr"]) * atr, float(p["tp_atr"]) * atr
    lf, sf = le.shift(1, fill_value=False), se.shift(1, fill_value=False)
    sl_f = (pd.Series(np.nan, index=o.index).mask(lf, 1 - (c - sl_d).shift(1) / o)
            .mask(sf, (c + sl_d).shift(1) / o - 1))
    tp_f = (pd.Series(np.nan, index=o.index).mask(lf, (c + tp_d).shift(1) / o - 1)
            .mask(sf, 1 - (c - tp_d).shift(1) / o))
    return {"sl_stop": sl_f.clip(lower=1e-6), "tp_stop": tp_f.clip(lower=1e-6)}


def portfolio_kwargs(**params):
    return {}
