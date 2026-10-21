"""AlexInc's meaningful-bar counter-moves, 30-minute bars: after three meaningful down bars (or one down bar whose body is over 3x the largest of the last three), with a real body, buy (from flat, or reversing a
short that is in profit); the mirror sells; an up bar with a body over half the 6-bar average closes a long, a down bar closes a short.
Port of FMZ strategy #437548 "AlexIncs Bar v12 Breakout Accumulation Strategy Based on Meaningful Bar Filtering" (AlexInc Bar 1.2).

FMZ source id: 437548

Source
    https://www.fmz.com/strategy/437548 (PineScript v2, FMZ last modified 2024-01-03 16:30:16).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 160-299), body multiplier 3, meaningful divider 3, take-profit bars 6 (unused); martingale off; SMA filter off; long and short on
    meaningful bar = body > sma(body, 6) / 3;  counts of consecutive meaningful bullish / bearish bars;  up1 = bearish count >= 3 and (flat or close < avg price) and body > sma(body, 6) / 5;  up2 = down bar and body > 3 x max3[1] and the same tests
    up -> close_all if short, entry Long;  dn mirror;  exit = (long and up bar or short and down bar) and body > sma(body, 6) / 2 -> close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * "close < firstbullishopen or 1" is always true, as written. The position tests use the average
      entry price (the fill, one entry). Orders follow the script's call order: the close_all and entry of
      each side, then the exit, which only closes the position open at the bar's close and left unchanged
      by the entries. The predicted-profit and bar-count lines place no orders; martingale and the SMA
      filter are off. REVERSAL INTENDED. The lot and martingale are sizing. FREQ = "30min" from the
      backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, body ratios and counts.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the lot, capital % and martingale stored.
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

NAME = "fmz_437548_alexinc_meaningful_bars"
FAMILY = "reversal_pattern"  # proposed 2026-10-21 (FMZ-C), user to confirm
FREQ = "30min"  # backtest header period: 30m
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "body_mult": [3.0, 2.0],
    "meanful_div": [3.0, 2.0],
}
DEFAULT_PARAMS = {"body_mult": 3.0, "meanful_div": 3.0, "abody_len": 6}


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, c = bars_df["open"], bars_df["close"]
    body = (c - o).abs()
    ab = body.rolling(int(p["abody_len"])).mean().to_numpy()
    b = body.to_numpy(dtype=float)
    ov, cv = o.to_numpy(dtype=float), c.to_numpy(dtype=float)
    m = len(cv)
    bar = np.where(cv > ov, 1, np.where(cv < ov, -1, 0))
    max3 = np.zeros(m)
    with np.errstate(invalid="ignore"):
        for i in range(m):
            b0, b1, b2 = b[i], (b[i - 1] if i >= 1 else np.nan), (b[i - 2] if i >= 2 else np.nan)
            if b0 >= b1 and b0 >= b2:
                max3[i] = b0
            elif b1 >= b0 and b1 >= b2:
                max3[i] = b1
            elif b2 >= b0 and b2 >= b1:
                max3[i] = b2
    prevmax3 = np.concatenate(([0.0], max3[:-1]))
    bm, md = float(p["body_mult"]), float(p["meanful_div"])
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    bull = bear = 0
    pos, entry_i = 0, -1
    with np.errstate(invalid="ignore"):
        for i in range(m):
            if b[i] > ab[i] / md:
                if bar[i] == 1:
                    bull, bear = bull + 1, 0
                elif bar[i] == -1:
                    bear, bull = bear + 1, 0
            avg = ov[entry_i] if pos != 0 else np.nan
            real = b[i] > ab[i] / 5
            lpos = pos == 0 or (pos != 0 and cv[i] < avg)
            spos = pos == 0 or (pos != 0 and cv[i] > avg)
            up = real and lpos and (bear >= 3 or (bar[i] == -1 and b[i] > prevmax3[i] * bm))
            dn = real and spos and (bull >= 3 or (bar[i] == 1 and b[i] > prevmax3[i] * bm))
            ex = ((pos > 0 and bar[i] == 1) or (pos < 0 and bar[i] == -1)) and b[i] > ab[i] / 2
            s, changed = pos, False
            if up:
                if s < 0:
                    s = 0
                if s != 1:
                    s, changed = 1, True
            if dn:
                if s > 0:
                    s = 0
                if s != -1:
                    s, changed = -1, True
            if ex and not changed:
                s = 0
            if s == 1 and pos != 1:
                le[i] = True
            elif s == -1 and pos != -1:
                se[i] = True
            elif s == 0 and pos == 1:
                lx[i] = True
            elif s == 0 and pos == -1:
                sx[i] = True
            if s != 0 and s != pos:
                entry_i = i + 1 if i + 1 < m else i
            pos = s
    ix = bars_df.index
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), pd.Series(se, index=ix), pd.Series(sx, index=ix)


def portfolio_kwargs(**params):
    return {}
