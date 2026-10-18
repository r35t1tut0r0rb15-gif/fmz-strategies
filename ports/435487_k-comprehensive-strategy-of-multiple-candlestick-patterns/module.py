"""Candlestick pattern library, 1-hour bars: about 40 one- to five-candle patterns (trend from the SMA 50) set a bullish or bearish
direction, the last one that fires on a bar standing; a bullish direction goes long, a bearish one short (reversing); a long is also
closed on any close above its entry price or on a close 1.5 % under it (the short mirrors). The direction variable persists while
flat, as written.
Port of FMZ strategy #435487 "多种K线形态综合策略Comprehensive-Strategy-of-Multiple-Candlestick-Patterns" (All Candlestick Patterns Strategy).

FMZ source id: 435487

Source
    https://www.fmz.com/strategy/435487 (PineScript v4, FMZ last modified 2023-12-15 12:03:17).
    Verbatim copy: original_source.md. Read 2026-10-18 (FMZ-C).

Original signal (original_source.md lines 235-940), SMA 50 trend; pattern type Both; stop loss 1.5 %; the Doji, Long Shadow and Spinning Top options and On Neck set no direction
    _tradeDirection := "" when in a position; each enabled pattern block in file order sets "bullish" / "bearish" (Dark Cloud Cover sets "bullish", as written)
    entry("long", when = bullish);  close("long", when = bearish or (close < open and close < avg (1 - 0.015)) or close > avg);  entry("short", when = bearish);  close("short", when = bullish or (close > open and close > avg (1 + 0.015)) or close < avg)

Interpretation choices (Pine rules in SURVEY_README.md)
    * All pattern conditions are on the current and earlier bars (shifts only). The patterns with their
      default switches: On Neck (no direction), Rising / Falling Window, Falling / Rising Three Methods,
      Tweezer Top / Bottom, Dark Cloud Cover (sets bullish), Downside / Upside Tasuki Gap, Evening Doji
      Star, Doji Star bearish / bullish, Morning Doji Star, Piercing, Hammer, Hanging Man, Shooting
      Star, Inverted Hammer, Morning / Evening Star, Marubozu white / black, Doji (no direction),
      Gravestone / Dragonfly Doji, Harami Cross and Harami (both ways), Three White Soldiers, Three
      Black Crows, Engulfing, Abandoned Baby, Tri-Star, Kicking. Long / Upper Shadow and the two Spinning
      Tops are off by default and not ported.
    * The order loop follows the script: the position held at a bar's open decides whether the
      direction is reset; the four orders (entry long, close long, entry short, close short) are
      filled in that sequence at the next open, so a bullish bar on a short reverses it and the close
      rules can then close what was just opened. avg is the position's average price (the fill open).
      The direction that is set while a position is open and survives to a flat bar re-enters at once,
      as written. The "close above the entry price" exit makes trades last
      about one bar. The percent-of-equity size is sizing. REVERSAL INTENDED.
    * FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; exits on closes.
    2 generic: PASS, candle patterns and percent stops on closes.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the initial capital input stored.
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

NAME = "fmz_435487_candlestick_pattern_library"
FAMILY = "candle_pattern"  # proposed 2026-10-18 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "stop_loss": [0.015, 0.03],
    "sma_len": [50, 100],
}
DEFAULT_PARAMS = {"stop_loss": 0.015, "sma_len": 50, "body_len": 14}


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


def _patterns(bars_df, p):
    """The direction (+1 bullish, -1 bearish, 0 none) set on each bar: the last firing block in file order."""
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    with np.errstate(invalid="ignore", divide="ignore"):
        avg = c.rolling(int(p["sma_len"])).mean()
        dn_t, up_t = c < avg, c > avg
        body_hi, body_lo = np.maximum(c, o), np.minimum(c, o)
        body = body_hi - body_lo
        body_avg = body.ewm(span=int(p["body_len"]), adjust=False).mean()
        small, long_ = body < body_avg, body > body_avg
        up_sh, dn_sh = h - body_hi, body_lo - lo
        has_up, has_dn = up_sh > 5.0 / 100 * body, dn_sh > 5.0 / 100 * body
        white, black = o < c, o > c
        rng = h - lo
        body_mid = body / 2 + body_lo
        sh_eq = (up_sh == dn_sh) | (((up_sh - dn_sh).abs() / dn_sh * 100 < 100.0) & ((dn_sh - up_sh).abs() / up_sh * 100 < 100.0))
        doji_body = (rng > 0) & (body <= rng * 5.0 / 100)
        doji = doji_body & sh_eq
        hl2 = (h + lo) / 2

        def S(x, k):
            return x.shift(k, fill_value=False) if x.dtype == bool else x.shift(k)

        pats = []   # (flag, direction) in file order; a block with no direction is left out

        pats.append((S(up_t, 1) & (rng != 0) & (S(rng, 1) != 0) & (lo > S(h, 1)), 1))                        # Rising Window
        pats.append((S(dn_t, 1) & (rng != 0) & (S(rng, 1) != 0) & (h < S(lo, 1)), -1))                      # Falling Window
        pats.append((S(dn_t, 4) & S(long_, 4) & S(black, 4)
                     & S(small, 3) & S(white, 3) & (S(o, 3) > S(lo, 4)) & (S(c, 3) < S(h, 4))
                     & S(small, 2) & S(white, 2) & (S(o, 2) > S(lo, 4)) & (S(c, 2) < S(h, 4))
                     & S(small, 1) & S(white, 1) & (S(o, 1) > S(lo, 4)) & (S(c, 1) < S(h, 4))
                     & long_ & black & (c < S(c, 4)), -1))                                                  # Falling Three Methods
        pats.append((S(up_t, 4) & S(long_, 4) & S(white, 4)
                     & S(small, 3) & S(black, 3) & (S(o, 3) < S(h, 4)) & (S(c, 3) > S(lo, 4))
                     & S(small, 2) & S(black, 2) & (S(o, 2) < S(h, 4)) & (S(c, 2) > S(lo, 4))
                     & S(small, 1) & S(black, 1) & (S(o, 1) < S(h, 4)) & (S(c, 1) > S(lo, 4))
                     & long_ & white & (c > S(c, 4)), 1))                                                   # Rising Three Methods
        pats.append((S(up_t, 1) & (~doji_body | (has_up & has_dn)) & ((h - S(h, 1)).abs() <= body_avg * 0.05)
                     & S(white, 1) & black & S(long_, 1), -1))                                              # Tweezer Top
        pats.append((S(up_t, 1) & (~doji_body | (has_up & has_dn)) & ((lo - S(lo, 1)).abs() <= body_avg * 0.05)
                     & S(black, 1) & white & S(long_, 1), 1))                                               # Tweezer Bottom
        pats.append((S(up_t, 1) & S(white, 1) & S(long_, 1) & black & (o >= S(h, 1)) & (c < S(body_mid, 1))
                     & (c > S(o, 1)), 1))                                                                   # Dark Cloud Cover (sets bullish)
        pats.append((S(long_, 2) & S(small, 1) & dn_t & S(black, 2) & (S(body_hi, 1) < S(body_lo, 2)) & S(black, 1)
                     & white & (body_hi <= S(body_lo, 2)) & (body_hi >= S(body_hi, 1)), -1))                # Downside Tasuki Gap
        pats.append((S(long_, 2) & S(small, 1) & up_t & S(white, 2) & (S(body_lo, 1) > S(body_hi, 2)) & S(white, 1)
                     & black & (body_lo >= S(body_hi, 2)) & (body_lo <= S(body_lo, 1)), 1))                 # Upside Tasuki Gap
        pats.append((S(long_, 2) & S(doji_body, 1) & long_ & up_t & S(white, 2) & (S(body_lo, 1) > S(body_hi, 2)) & black
                     & (body_lo <= S(body_mid, 2)) & (body_lo > S(body_lo, 2)) & (S(body_lo, 1) > body_hi), -1))  # Evening Doji Star
        pats.append((up_t & S(white, 1) & S(long_, 1) & doji_body & (body_lo > S(body_hi, 1)), -1))        # Doji Star bearish
        pats.append((dn_t & S(black, 1) & S(long_, 1) & doji_body & (body_hi < S(body_lo, 1)), 1))         # Doji Star bullish
        pats.append((S(long_, 2) & S(doji_body, 1) & long_ & dn_t & S(black, 2) & (S(body_hi, 1) < S(body_lo, 2)) & white
                     & (body_hi >= S(body_mid, 2)) & (body_hi < S(body_hi, 2)) & (S(body_hi, 1) < body_lo), 1))  # Morning Doji Star
        pats.append((S(dn_t, 1) & S(black, 1) & S(long_, 1) & white & (o <= S(lo, 1)) & (c > S(body_mid, 1))
                     & (c < S(o, 1)), 1))                                                                   # Piercing
        hammer_shape = small & (body > 0) & (body_lo > hl2) & (dn_sh >= 2.0 * body) & ~has_up
        pats.append((hammer_shape & dn_t, 1))                                                               # Hammer
        pats.append((hammer_shape & up_t, -1))                                                              # Hanging Man
        star_shape = small & (body > 0) & (body_hi < hl2) & (up_sh >= 2.0 * body) & ~has_dn
        pats.append((star_shape & up_t, -1))                                                                # Shooting Star
        pats.append((star_shape & dn_t, 1))                                                                 # Inverted Hammer
        pats.append((S(long_, 2) & S(small, 1) & long_ & dn_t & S(black, 2) & (S(body_hi, 1) < S(body_lo, 2)) & white
                     & (body_hi >= S(body_mid, 2)) & (body_hi < S(body_hi, 2)) & (S(body_hi, 1) < body_lo), 1))  # Morning Star
        pats.append((S(long_, 2) & S(small, 1) & long_ & up_t & S(white, 2) & (S(body_lo, 1) > S(body_hi, 2)) & black
                     & (body_lo <= S(body_mid, 2)) & (body_lo > S(body_lo, 2)) & (S(body_lo, 1) > body_hi), -1))  # Evening Star
        maru = long_ & (up_sh <= 5.0 / 100 * body) & (dn_sh <= 5.0 / 100 * body)
        pats.append((white & maru, 1))                                                                      # Marubozu White
        pats.append((black & maru, -1))                                                                     # Marubozu Black
        pats.append((doji_body & (dn_sh <= body), -1))                                                      # Gravestone Doji
        pats.append((doji_body & (up_sh <= body), 1))                                                       # Dragonfly Doji
        inside = (h <= S(body_hi, 1)) & (lo >= S(body_lo, 1))
        pats.append((S(long_, 1) & S(black, 1) & S(dn_t, 1) & doji_body & inside, 1))                       # Harami Cross bullish
        pats.append((S(long_, 1) & S(white, 1) & S(up_t, 1) & doji_body & inside, -1))                      # Harami Cross bearish
        pats.append((S(long_, 1) & S(black, 1) & S(dn_t, 1) & white & small & inside, 1))                   # Harami bullish
        pats.append((S(long_, 1) & S(white, 1) & S(up_t, 1) & black & small & inside, -1))                  # Harami bearish
        nu = (rng * 5.0 / 100) > up_sh
        pats.append((long_ & S(long_, 1) & S(long_, 2) & white & S(white, 1) & S(white, 2)
                     & (c > S(c, 1)) & (S(c, 1) > S(c, 2)) & (o < S(c, 1)) & (o > S(o, 1)) & (S(o, 1) < S(c, 2))
                     & (S(o, 1) > S(o, 2)) & nu & S(nu, 1) & S(nu, 2), 1))                                  # Three White Soldiers
        nd = (rng * 5.0 / 100) > dn_sh
        pats.append((long_ & S(long_, 1) & S(long_, 2) & black & S(black, 1) & S(black, 2)
                     & (c < S(c, 1)) & (S(c, 1) < S(c, 2)) & (o > S(c, 1)) & (o < S(o, 1)) & (S(o, 1) > S(c, 2))
                     & (S(o, 1) < S(o, 2)) & nd & S(nd, 1) & S(nd, 2), -1))                                 # Three Black Crows
        pats.append((dn_t & white & long_ & S(black, 1) & S(small, 1) & (c >= S(o, 1)) & (o <= S(c, 1))
                     & ((c > S(o, 1)) | (o < S(c, 1))), 1))                                                 # Engulfing bullish
        pats.append((up_t & black & long_ & S(white, 1) & S(small, 1) & (c <= S(o, 1)) & (o >= S(c, 1))
                     & ((c < S(o, 1)) | (o > S(c, 1))), -1))                                                # Engulfing bearish
        pats.append((S(dn_t, 2) & S(black, 2) & S(doji_body, 1) & (S(lo, 2) > S(h, 1)) & white & (S(h, 1) < lo), 1))   # Abandoned Baby bullish
        pats.append((S(up_t, 2) & S(white, 2) & S(doji_body, 1) & (S(h, 2) < S(lo, 1)) & black & (S(lo, 1) > h), -1))  # Abandoned Baby bearish
        three = doji & S(doji, 1) & S(doji, 2)
        gap_up = S(body_hi, 1) < body_lo
        gap_dn = S(body_lo, 1) > body_hi
        pats.append((three & S(dn_t, 2) & S(gap_dn, 1) & gap_up, 1))                                        # Tri-Star bullish
        pats.append((three & S(up_t, 2) & S(gap_up, 1) & gap_dn, -1))                                       # Tri-Star bearish
        pats.append((S(maru & black, 1) & (maru & white) & (S(h, 1) < lo), 1))                              # Kicking bullish
        pats.append((S(maru & white, 1) & (maru & black) & (S(lo, 1) > h), -1))                             # Kicking bearish
    out = np.zeros(len(o), dtype=np.int8)
    for flag, d in pats:
        f = flag.fillna(False).to_numpy(dtype=bool)
        out = np.where(f, d, out).astype(np.int8)
    return out


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, c = bars_df["open"].to_numpy(dtype=float), bars_df["close"].to_numpy(dtype=float)
    setdir = _patterns(bars_df, p)
    sl = float(p["stop_loss"])
    m = len(c)
    held = np.zeros(m, dtype=np.int8)       # the position held during bar i (after the opening fills)
    pos, avg, d = 0, np.nan, 0
    e_l = c_l = e_s = c_s = False
    for i in range(m):
        if i > 0:                            # fills at this bar's open, in the script's call order
            if e_l and pos <= 0:
                pos, avg = 1, o[i]
            if c_l and pos == 1:
                pos, avg = 0, np.nan
            if e_s and pos >= 0:
                pos, avg = -1, o[i]
            if c_s and pos == -1:
                pos, avg = 0, np.nan
        held[i] = pos
        if pos != 0:
            d = 0
        if setdir[i] != 0:
            d = int(setdir[i])
        e_l, e_s = d == 1, d == -1
        c_l = (d == -1) or (c[i] < o[i] and c[i] < avg * (1 - sl)) or (c[i] > avg)
        c_s = (d == 1) or (c[i] > o[i] and c[i] > avg * (1 + sl)) or (c[i] < avg)
    nxt = np.concatenate((held[1:], held[-1:]))
    ix = bars_df.index
    return (pd.Series((nxt == 1) & (held != 1), index=ix), pd.Series((nxt == 0) & (held == 1), index=ix),
            pd.Series((nxt == -1) & (held != -1), index=ix), pd.Series((nxt == 0) & (held == -1), index=ix))


def portfolio_kwargs(**params):
    return {}
