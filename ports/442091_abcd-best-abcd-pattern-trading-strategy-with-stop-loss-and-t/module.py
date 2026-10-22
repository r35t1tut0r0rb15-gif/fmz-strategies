"""ABCD harmonic patterns on a fractal zigzag with triggered trailing exits, 1-hour bars: a fresh bullish ABCD (BC 0.382-0.886 of AB, CD 1.13-2.618 of BC, D under C) goes long, a bearish one short; once the
price has run 2 % (3 %) from the signal close, a 3 % trail on lows (1 % trail on highs) closes the position when crossed; reversing.
Port of FMZ strategy #442091 "基于ABCD形态且带止损追踪和止盈追踪的全新量化交易策略Best-ABCD-Pattern-Trading-Strategy-with-Stop-Loss-and-Take-Profit-Tracking" (BEST ABCD Strategy (Trailing)).

FMZ source id: 442091

Source
    https://www.fmz.com/strategy/442091 (PineScript v4, FMZ last modified 2024-02-19 11:25:29).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 159-450), Bill Williams filter off (BW fractals used); stop trail 3 % after a 2 % trigger; profit trail 1 % after a 3 % trigger
    fractal tops / bottoms (5 bars, BW form) -> zigzag (alternating);  x a b c d = the last five zigzag points;  bull = abc in [0.382, 0.886] and bcd in [1.13, 2.618] and d < c (fresh);  bear: d > c
    buy_trend = barssince(isShort) > barssince(isLong);  triggers hit when high >= entry 1.02 (stop) / 1.03 (profit) in the trend (mirrored for shorts), reset on a trend change
    longStop = max(low 0.97, longStop[1]) in a buy trend;  close Long on crossunder(low, longStop[1]) after the trigger, or crossover(high, longTrailTP[1]) after the profit trigger (longTrailTP = max(high 1.01, ..))

Interpretation choices (Pine rules in SURVEY_README.md)
    * Ported as written: the zigzag, pattern ratios, the trend state from the latest signals and the
      trailing levels with their triggers (all on bar data, the closes sent at the next open). entry_price
      is the latest signal close. A close acts only on the held position; a close written after a reversing
      entry leaves the reversal standing (as #438020). REVERSAL INTENDED. No sizing code. FREQ = "1h" from
      the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders.
    2 generic: PASS, fractal zigzag ABCD and bar-tested trailing levels.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
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

NAME = "fmz_442091_abcd_zigzag_triggered_trailing_exits"
FAMILY = "reversal_pattern"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "stop_trail": [0.03, 0.05],
    "tp_trigger": [0.03, 0.05],
}
DEFAULT_PARAMS = {"stop_trail": 0.03, "tp_trigger": 0.03, "sl_trigger": 0.02, "profit_trail": 0.01}


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


def _barssince(flag):
    out = np.full(len(flag), np.nan)
    k = -1
    for i, f in enumerate(flag):
        if f:
            k = 0
        elif k >= 0:
            k += 1
        if k >= 0:
            out[i] = k
    return out


def _signals(bars_df):
    h, lo = bars_df["high"], bars_df["low"]
    hs = [h.shift(k) for k in range(5)]
    ls = [lo.shift(k) for k in range(5)]
    top = ((hs[4] < hs[2]) & (hs[3] <= hs[2]) & (hs[2] >= hs[1]) & (hs[2] > hs[0])).to_numpy()
    bot = ((ls[4] > ls[2]) & (ls[3] >= ls[2]) & (ls[2] <= ls[1]) & (ls[2] < ls[0])).to_numpy()
    tc, bc = _barssince(top), _barssince(bot)
    h2, l2 = hs[2].to_numpy(), ls[2].to_numpy()
    m = len(top)
    pts = []
    bull = np.zeros(m, dtype=bool)
    bear = np.zeros(m, dtype=bool)
    for i in range(m):
        z = np.nan
        if i > 0:
            if top[i] and tc[i - 1] > bc[i - 1]:
                z = h2[i]
            elif bot[i] and tc[i - 1] < bc[i - 1]:
                z = l2[i]
        if not np.isnan(z) and z != 0:
            pts.append(z)
        if len(pts) >= 5:
            x, a, b, c, d = pts[-5:]
            with np.errstate(divide="ignore", invalid="ignore"):
                abc = abs(b - c) / abs(a - b) if a != b else np.nan
                bcd = abs(c - d) / abs(b - c) if b != c else np.nan
            ok = (0.382 <= abc <= 0.886) and (1.13 <= bcd <= 2.618)
            bull[i] = ok and d < c
            bear[i] = ok and d > c
    is_long = bull & ~np.concatenate(([False], bull[:-1]))
    is_short = bear & ~np.concatenate(([False], bear[:-1]))
    return is_long, is_short


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    is_long, is_short = _signals(bars_df)
    hv = bars_df["high"].to_numpy(dtype=float)
    lv = bars_df["low"].to_numpy(dtype=float)
    cv = bars_df["close"].to_numpy(dtype=float)
    up_n, dn_n = _barssince(is_long), _barssince(is_short)
    st, slt = float(p["stop_trail"]), float(p["sl_trigger"])
    pt, tpt = float(p["profit_trail"]), float(p["tp_trigger"])
    m = len(cv)
    tgt = np.zeros(m, dtype=np.int8)
    held = 0
    lep = sep = np.nan
    slL = slS = tpL = tpS = False
    lsp1, lsp2, ssp1, ssp2 = 0.0, 0.0, 999999.0, 999999.0
    ltp1, ltp2, stp1, stp2 = 0.0, 0.0, 999999.0, 999999.0
    bt_prev = st_prev = False
    for i in range(m):
        if is_long[i]:
            lep = cv[i]
        if is_short[i]:
            sep = cv[i]
        bt = dn_n[i] > up_n[i]
        sl_t = dn_n[i] < up_n[i]
        ep = lep if bt else sep
        trig = ep * (1 + slt) if bt else ep * (1 - slt)
        slL = True if (bt and hv[i] >= trig) else slL
        slS = True if (sl_t and lv[i] <= trig) else slS
        lsp = max(lv[i] * (1 - st), lsp1) if bt else 0.0
        ssp = min(hv[i] * (1 + st), ssp1) if sl_t else 999999.0
        lo1 = lv[i - 1] if i > 0 else np.nan
        hi1 = hv[i - 1] if i > 0 else np.nan
        c_lsl = bt and lv[i] < lsp1 and lo1 >= lsp2 and slL
        c_ssl = sl_t and hv[i] > ssp1 and hi1 <= ssp2 and slS
        ttrig = ep * (1 + tpt) if bt else ep * (1 - tpt)
        tpL = True if (bt and hv[i] >= ttrig) else tpL
        tpS = True if (sl_t and lv[i] <= ttrig) else tpS
        ltp = max(hv[i] * (1 + pt), ltp1) if bt else 0.0
        stp = min(lv[i] * (1 - pt), stp1) if sl_t else 999999.0
        c_ltp = bt and hv[i] > ltp1 and hi1 <= ltp2 and tpL
        c_stp = sl_t and lv[i] < stp1 and lo1 >= stp2 and tpS
        new = held
        if is_long[i] and new != 1:
            new = 1
        if (c_ltp or c_lsl) and held == 1 and new == 1:
            new = 0
        if is_short[i] and new != -1:
            new = -1
        if (c_stp or c_ssl) and held == -1 and new == -1:
            new = 0
        tgt[i] = new
        held = new
        if (bt and st_prev) or (sl_t and bt_prev):
            slL = slS = tpL = tpS = False
        lsp2, lsp1, ssp2, ssp1 = lsp1, lsp, ssp1, ssp
        ltp2, ltp1, stp2, stp1 = ltp1, ltp, stp1, stp
        bt_prev, st_prev = bt, sl_t
    prev = np.concatenate(([0], tgt[:-1]))
    ix = bars_df.index
    le = pd.Series((tgt == 1) & (prev != 1), index=ix)
    lx = pd.Series((prev == 1) & (tgt == 0), index=ix)
    se = pd.Series((tgt == -1) & (prev != -1), index=ix)
    sx = pd.Series((prev == -1) & (tgt == 0), index=ix)
    return le, lx, se, sx


def portfolio_kwargs(**params):
    return {}
