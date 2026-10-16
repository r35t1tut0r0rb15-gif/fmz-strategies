"""MACD / RSI extreme flag with a bracket and a trailing stop, hourly bars: when the "extreme" flag (deep
oversold or high overbought) turns on the strategy goes long, when it turns off it goes short; each trade
has a stop, a target and a trail.
Port of FMZ strategy #428795 "基于MACD和RSI的长短双向交易策略MACD-and-RSI-Based-Long-Short-Trading-Strategy" (Moriceau_Crypto_strategies_Long_short_indicator).

FMZ source id: 428795

Source
    https://www.fmz.com/strategy/428795 (PineScript v3, FMZ last modified 2023-10-09 15:33:17).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 146-227), MACD 12 / 26, RSI 14; TP 2500, SL 600, trail 300 / offset 50 ticks
    Achat = macd < -0.1 and rsi < 27 and ema12 < ema26; vente = macd > 0.125 and rsi > 81 and ema12 > ema26
    tradeDirection = vente ? (Achat ? false : true) : Achat     (= Achat or vente: they never coincide)
    turns true -> entry long; turns false -> entry short
    exit(profit = 2500, loss = 600, trail_points = 300, trail_offset = 50) per side

Interpretation choices (Pine rules in SURVEY_README.md)
    * tradeDirection is true on EITHER extreme, as written (a deep oversold bar and a high
      overbought bar both turn it on), so longs open when an extreme starts and shorts when it ends.
    * Criterion 2: the MACD thresholds -0.1 / 0.125 (price units) become macd_lo_atr / macd_hi_atr x
      Wilder ATR(14) (about 0.0007 / 0.0008 ATR on hourly BTC, practically sign tests); the ticks of
      the bracket become ATR multiples of the signal bar (shifted one bar inside stops(), re-based on
      the fill): 600 / 2500 ticks of 0.1 on hourly BTC are about 0.4 / 1.7 ATR (judgement before any
      backtest).
    * The trail is ported natively (mark trailing_stop): {"type": "volatility", "atr_n": 14, "k":
      0.035, "anchor": "high_low", "activate_after": 0.00115}. Stated approximations: Pine trails 50
      ticks behind the best price, here 0.035 x ATR(14) of the last completed bar; Pine activates
      after 300 ticks of profit, here after a 0.115 % gain (300 ticks of 0.1 at about 26,000).
    * strategy.close("TP 50% Sell") names no entry: inert. strategy.close("Vente") on exitShort is
      the same bar as the long entry, which reverses anyway. The date inputs are not used.
    * Stop module: portfolio_kwargs {} (driver D4); REVERSAL INTENDED. FREQ = "1h".

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry; the trail is a house trail (approximation stated).
    2 generic: ADAPT, price-unit thresholds and tick distances -> ATR multiples.
    3 crypto-exchange-only: no ("crypto" is in the name only; exchange pair in the header).
    4 signals only: the exits are ported via stops() and quoted in original_sizing.txt.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND427239 (2 members, best partner #427239, Jaccard 0.732); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: trailing_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_428795_macd_rsi_extreme_flag_bracket"
FAMILY = "macd_momentum"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sl_atr": [0.4, 1.0],
    "tp_atr": [1.7, 4.0],
}
DEFAULT_PARAMS = {"fast": 12, "slow": 26, "rsi_length": 14, "rsi_low": 27, "rsi_high": 81,
                  "macd_lo_atr": 0.0007, "macd_hi_atr": 0.0008, "sl_atr": 0.4, "tp_atr": 1.7,
                  "trail_k": 0.035, "trail_activate": 0.00115, "atr_length": 14}


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


def _rsi(x, n):
    d = x.diff()
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    r = 100 - 100 / (1 + up / dn)
    return r.where(dn != 0, 100.0).where(up.notna() & dn.notna())


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    return _rma(tr, n)


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    c = bars_df["close"]
    ef = c.ewm(span=int(p["fast"]), adjust=False).mean()
    es = c.ewm(span=int(p["slow"]), adjust=False).mean()
    macd = ef - es
    r = _rsi(c, int(p["rsi_length"]))
    atr = _atr(bars_df, int(p["atr_length"]))
    achat = (macd < -p["macd_lo_atr"] * atr) & (r < p["rsi_low"]) & (ef < es)
    vente = (macd > p["macd_hi_atr"] * atr) & (r > p["rsi_high"]) & (ef > es)
    td = (achat ^ vente).to_numpy()
    prev = np.concatenate(([False], td[:-1]))
    idx = bars_df.index
    long_e = pd.Series(td & ~prev, index=idx)
    short_e = pd.Series(prev & ~td, index=idx)
    false = pd.Series(False, index=idx)
    return long_e, false, short_e, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    frac = _atr(bars_df, int(p["atr_length"])) / bars_df["close"]
    return {"sl_stop": (p["sl_atr"] * frac).shift(1), "tp_stop": (p["tp_atr"] * frac).shift(1),
            "trail": {"type": "volatility", "atr_n": int(p["atr_length"]), "k": float(p["trail_k"]),
                      "anchor": "high_low", "activate_after": float(p["trail_activate"])}}


def portfolio_kwargs(**params):
    return {}
