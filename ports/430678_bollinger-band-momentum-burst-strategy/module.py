"""Bollinger expansion with a 4-hour EMA trend (kasaism), 1-hour bars: when the 20-bar band has been wider than the 40-bar
band (now or 14 bars ago), a bar opening under and closing over the 20-bar basis in a 4-hour up-trend goes long (mirror
short); a 3 ATR stop and a 1.5 R target, set from the close of the first bar in the position, are checked on bar
extremes and close at the next open.
Port of FMZ strategy #430678 "Bollinger Band Momentum Burst Strategy" ([EURUSD60] BB Expansion Strategy).

FMZ source id: 430678

Source
    https://www.fmz.com/strategy/430678 (PineScript v4, FMZ last modified 2023-10-31 15:54:41).
    Verbatim copy: original_source.md. Read 2026-10-16 (FMZ-C).

Original signal (original_source.md lines 170-319), large BB 40, small BB 20, 2 sd, valid length 14; 4h EMA 14 / smooth 3; ATR 14 x 3, R:R 1.5
    bbTrade = lrgUpper < smlUpper and lrgLower > smlLower; isBbEntry = bbTrade or bbTrade[14]
    isBbLong = isBbEntry and open < smlBasis and close > smlBasis (short mirrored)
    base = security("240", ema(close, 14)); sig = security("240", ema(base, 3)); trend up when base >= sig
    isBbLong and up -> entry long;  isBbShort and down -> entry short
    in a position: SL = close - 3 atr(14), TP = close + 1.5 x 3 atr, taken on its first bar and kept
    low <= SL or high >= TP -> strategy.close (long; short mirrored)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The BB resolutions are "" (the chart). The for loop overwrites isBbEntry on every pass, so only
      bbTrade or bbTrade[validLen] remains, as written.
    * The 4-hour EMAs use completed 4-hour bars (lookahead off, index 0 on history): built from the
      1-hour bars, each 4-hour value is used from the last 1-hour bar of its block (which closes with
      it) on.
    * Default risk rule "ATR": the levels are set from the close of the first bar in the position (the
      fill bar) and tested on bar extremes with strategy.close (a market exit at the next open):
      exit signals, not stop orders. Criterion 2: round(level, 3) is a price-unit grid (3 decimals,
      10 pips on EUR/USD): not ported.
    * An opposite entry reverses the position (the close by id then has nothing left to close).
      The strategy() line is commented out in the corpus copy: orders read as written (as #429505).
      REVERSAL INTENDED. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; close-checked exits; completed higher-timeframe values.
    2 generic: ADAPT, the 3-decimal rounding of the levels dropped.
    3 crypto-exchange-only: no ("EURUSD" in the title only; exchange pair in the header).
    4 signals only: the risk-rule options quoted in original_sizing.txt.
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

NAME = "fmz_430678_bb_expansion_4h_trend"
FAMILY = "volatility_squeeze"  # proposed 2026-10-16 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
HTF = "4h"  # the source's EMA trend timeframe (240)

GRID = {
    "atr_multi": [3.0, 2.0],
    "rr": [1.5, 2.0],
}
DEFAULT_PARAMS = {"large_len": 40, "small_len": 20, "multi": 2.0, "valid_len": 14, "ema_len": 14, "smooth": 3,
                  "atr_multi": 3.0, "rr": 1.5}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _atr(bars, n):
    c1 = bars["close"].shift(1)
    tr = pd.concat([bars["high"] - bars["low"], (bars["high"] - c1).abs(), (bars["low"] - c1).abs()],
                   axis=1).max(axis=1)
    return tr.ewm(alpha=1 / n, adjust=False).mean()


def _htf_trend(bars_df, p):
    """+1 / -1 / 0 from completed 4-hour bars, each used from the last 1-hour bar of its block on."""
    c4 = bars_df["close"].resample(HTF, label="left", closed="left").last().dropna()
    base = c4.ewm(span=int(p["ema_len"]), adjust=False).mean()
    sig = base.ewm(span=int(p["smooth"]), adjust=False).mean()
    trend = np.where(base < sig, -1, 1).astype(float)
    avail = (c4.index + pd.Timedelta(HTF) - pd.Timedelta(FREQ)).asi8
    t = bars_df.index.asi8
    k = np.searchsorted(avail, t, side="right") - 1
    out = np.where(k >= 0, trend[np.clip(k, 0, None)], 0.0)
    return out


def _emit(tgt, index):
    prev = np.concatenate(([0], tgt[:-1]))
    le = (tgt == 1) & (prev != 1)
    lx = (prev == 1) & (tgt == 0)
    se = (tgt == -1) & (prev != -1)
    sx = (prev == -1) & (tgt == 0)
    return tuple(pd.Series(a, index=index) for a in (le, lx, se, sx))


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    L, S, mu = int(p["large_len"]), int(p["small_len"]), float(p["multi"])
    lb, ld = c.rolling(L).mean(), mu * c.rolling(L).std(ddof=0)
    sb, sd = c.rolling(S).mean(), mu * c.rolling(S).std(ddof=0)
    bbt = ((lb + ld) < (sb + sd)) & ((lb - ld) > (sb - sd))
    entry_ok = bbt | bbt.shift(int(p["valid_len"]), fill_value=False)
    is_long = (entry_ok & (o < sb) & (c > sb)).to_numpy()
    is_short = (entry_ok & (o > sb) & (c < sb)).to_numpy()
    trend = _htf_trend(bars_df, p)
    go_long = is_long & (trend == 1)
    go_short = is_short & (trend == -1)
    atr = (_atr(bars_df, 14) * float(p["atr_multi"])).to_numpy()
    rr = float(p["rr"])
    cv, hv, lv = c.to_numpy(dtype=float), h.to_numpy(dtype=float), lo.to_numpy(dtype=float)
    m = len(cv)
    tgt = np.zeros(m, dtype=np.int8)
    pos = 0
    sl_l = tp_l = sl_s = tp_s = np.nan
    for i in range(m):
        start = pos
        if start == 1:
            if np.isnan(sl_l):
                sl_l, tp_l = cv[i] - atr[i], cv[i] + atr[i] * rr
        else:
            sl_l = tp_l = np.nan
        if start == -1:
            if np.isnan(sl_s):
                sl_s, tp_s = cv[i] + atr[i], cv[i] - atr[i] * rr
        else:
            sl_s = tp_s = np.nan
        new = start
        if go_long[i]:
            new = 1
        if go_short[i]:
            new = -1
        if start == 1 and new == 1 and (lv[i] <= sl_l or hv[i] >= tp_l):
            new = 0
        if start == -1 and new == -1 and (hv[i] >= sl_s or lv[i] <= tp_s):
            new = 0
        pos = new
        tgt[i] = pos
    return _emit(tgt, bars_df.index)


def portfolio_kwargs(**params):
    return {}
