"""Candle reversal patterns (hammer, inverted hammer, engulfing, tweezers and their bearish mirrors) inside close-only Stochastic 14 extreme zones, 2-minute bars: a bullish pattern in the bearish zone goes long, a bearish pattern in the bullish zone goes short, each with a 1 ATR 14 stop and a 1.5 ATR target from the signal close; reversing.
Port of FMZ strategy #484582 "Automated Market Reversal Trading Strategy Based on Stochastic Indicator and Candlestick Patterns" (Bauhaus Reversal Master).

FMZ source id: 484582

Source
    https://www.fmz.com/strategy/484582 (PineScript v6, FMZ last modified 2025-03-03 10:03:52).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 189-276), ATR 14; target 1.5 ATR; stop 1 ATR; trend lookback 14; threshold 80; smoothing 20; all patterns on; 10 % of equity, commission 0.1 %; MPL 2.0 notice (tradingbauhaus)
    kTrend = stoch(close, close, close, 14);  smoothK moves 2 / 21 of the way to 100 when kTrend > 50, to 0 when < 50, else takes kTrend;  bullZone = both >= 80;  bearZone = both <= 20
    bullish = hammer / inverted hammer in bearZone, engulfing / tweezer bottom after a bearZone bar -> entry GoLong + exit(limit = close + 1.5 atr, stop = close - atr);  bearish mirrors -> entry GoShort + mirror

Interpretation choices (Pine rules in SURVEY_README.md)
    * As written, smoothK takes kTrend's na during the warm-up and then stays na (na plus anything is
      na) until a bar where kTrend is exactly 50 resets it; no zone, and so no trade, exists before that.
    * Wick and body shares divide by the bar range (na on a zero range, so the test fails). The doji and
      tweezer tests compare prices rounded to the tick; the stored data is already at the instrument's
      tick, so they compare the prices directly. The levels are fixed at the signal close and sent as
      fractions of the fill open (a level at or through it is marketable and closed one bar late, as
      #458256). A repeat signal while held re-sends the bracket; stops() keeps the first, so the repeat
      case is marked trailing_stop_pending (as #434428). An entry on the other side reverses (REVERSAL
      INTENDED); a short called on the same bar as a long wins (called later, as #437773). Stop module:
      portfolio_kwargs {} (driver D4). The 10 % of equity size is sizing; the commission is a cost (the
      house cost model applies). The MPL 2.0 notice is kept with the verbatim copy (ported, stated).
      FREQ = "2min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; ATR bracket as fractions of the fill.
    2 generic: PASS, candle reversals in Stochastic extreme zones.
    3 crypto-exchange-only: no (futures exchange pair in the header only).
    4 signals only: 10 % of equity stored, not ported.
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

NAME = "fmz_484582_candle_reversals_stoch_zone_atr_bracket_reversal"
FAMILY = "candle_pattern"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "2min"  # backtest header period: 2m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "thresh": [80.0, 70.0],
    "trend_len": [14, 20],
}
DEFAULT_PARAMS = {"thresh": 80.0, "trend_len": 14, "smooth_period": 20.0, "atr_len": 14, "profit_target": 1.5,
                  "stop_loss": 1.0}


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


def _signals(bars_df, p):
    o, h, lo, c = bars_df["open"], bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["trend_len"])
    rng = c.rolling(n).max() - c.rolling(n).min()
    kt = (100 * (c - c.rolling(n).min()) / rng.where(rng > 0)).to_numpy(dtype=float)
    al = 2 / (float(p["smooth_period"]) + 1)
    sk = np.zeros(len(kt))
    prev = 0.0
    for i in range(len(kt)):
        if kt[i] > 50:
            prev = prev + (100 - prev) * al          # na stays na
        elif kt[i] < 50:
            prev = prev + (0 - prev) * al
        else:
            prev = kt[i]                             # na kTrend (warm-up) or exactly 50
        sk[i] = prev
    kts, sks = pd.Series(kt, index=c.index), pd.Series(sk, index=c.index)
    th = float(p["thresh"])
    bull_z = (kts >= th) & (sks >= th)
    bear_z = (kts <= 100 - th) & (sks <= 100 - th)
    red, green = c < o, c > o
    top, bot = np.maximum(o, c), np.minimum(o, c)
    fr = (h - lo).where(h - lo > 0)
    body = top - bot
    up_p, dn_p, body_p = (h - top) / fr * 100, (bot - lo) / fr * 100, body / fr * 100
    doji = c == o
    hammer_shape = (dn_p > body_p * 2) & (body_p < 50) & (up_p < 2) & ~doji
    inv_shape = (up_p > body_p * 2) & (body_p < 50) & (dn_p < 2) & ~doji
    bull_eng = red.shift(1, fill_value=False) & green & (body > body.shift(1) / 2) & (o < c.shift(1)) & \
        (top > top.shift(1)) & bear_z.shift(1, fill_value=False)
    tw_bot = (lo == lo.shift(1)) & green & red.shift(1, fill_value=False) & bear_z.shift(1, fill_value=False)
    bear_eng = green.shift(1, fill_value=False) & red & (body > body.shift(1) / 2) & (o > c.shift(1)) & \
        (bot < bot.shift(1)) & bull_z.shift(1, fill_value=False)
    tw_top = (h == h.shift(1)) & red & green.shift(1, fill_value=False) & bull_z.shift(1, fill_value=False)
    le = ((hammer_shape | inv_shape) & bear_z) | bull_eng | tw_bot
    se = ((inv_shape | hammer_shape) & bull_z) | bear_eng | tw_top
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1, skipna=False)
    tr.iloc[0] = h.iloc[0] - lo.iloc[0]
    atr = _rma(tr, int(p["atr_len"]))
    a, b = atr * float(p["stop_loss"]), atr * float(p["profit_target"])
    lvl = {"l_sl": c - a, "l_tp": c + b, "s_sl": c + a, "s_tp": c - b}
    return le & ~se, se, lvl


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, lvl = _signals(bars_df, p)
    o = bars_df["open"]
    lf, sf = le.shift(1, fill_value=False), se.shift(1, fill_value=False)
    l_thr = (lvl["l_sl"].shift(1) >= o) | (lvl["l_tp"].shift(1) <= o)    # marketable at the fill
    s_thr = (lvl["s_sl"].shift(1) <= o) | (lvl["s_tp"].shift(1) >= o)
    return le, lf & l_thr & ~le & ~se, se, sf & s_thr & ~se & ~le


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, se, lvl = _signals(bars_df, p)
    o = bars_df["open"]
    lf = le.shift(1, fill_value=False)
    l_sl, l_tp = 1 - lvl["l_sl"].shift(1) / o, lvl["l_tp"].shift(1) / o - 1
    s_sl, s_tp = lvl["s_sl"].shift(1) / o - 1, 1 - lvl["s_tp"].shift(1) / o
    sl = l_sl.where(lf, s_sl)
    tp = l_tp.where(lf, s_tp)
    return {"sl_stop": sl.where(sl > 0), "tp_stop": tp.where(tp > 0)}


def portfolio_kwargs(**params):
    return {}
