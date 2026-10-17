"""RSI 14 extremes with a cooldown after a loss, 3-minute bars: RSI at or under 20 goes long, at or over 80 goes short, each
with a 1 % target and a 3 % stop from the signal close; RSI reaching 70 (30 for shorts) or a close 1 % in profit closes
the position, and a losing trade blocks new entries for 24 bars.
Port of FMZ strategy #431668 "RSI策略的回测与优化Backtesting-and-Optimization-of-RSI-Strategy" (rsi超买超卖_回测用).

FMZ source id: 431668

Source
    https://www.fmz.com/strategy/431668 (PineScript v5, FMZ last modified 2023-11-10 11:59:40).
    Verbatim copy: original_source.md. Read 2026-10-17 (FMZ-C).

Original signal (original_source.md lines 175-266), RSI 14, trigger 20 / 80, RSI exits 70 / 30, stop 3 %, target 1 %, cooldown 24 bars
    rsi <= 20 and not stopTrade -> entry long (openPrice = close when flat); exit(limit = openPrice x 1.01, stop = openPrice x 0.97)
    rsi >= 80 and not stopTrade -> entry short (mirror)
    long and rsi >= 70 -> close_all;  long and (close - avg) / avg >= 1 % -> close_all  (mirror short)
    the bar of a losing exit -> stopTrade; stopTrade counts 24 bars, then trading resumes

Interpretation choices (Pine rules in SURVEY_README.md)
    * The state is ported line for line: the bracket levels come from openPrice (the signal close of
      the entry taken from flat; a reversal keeps the old openPrice, as written), as fractions of the
      entry fill (the open after the signal, known at that open); a level already passed at that open
      exits at once. "Flat", the exit prices and the losing-trade test follow the house bracket and
      the close_all fills (the next open) on bars; a stop and a target both reachable in one bar take
      the stop first.
    * A close_all written before an entry leaves the entry standing. Entries reverse: REVERSAL
      INTENDED. Stop module: portfolio_kwargs {} (driver D4). FREQ = "3min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry.
    2 generic: PASS, RSI levels, percentage exits and a bar-count cooldown.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: 50000 USDT per order stored in original_sizing.txt.
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

NAME = "fmz_431668_rsi_extremes_loss_cooldown"
FAMILY = "rsi_oscillator"  # proposed 2026-10-17 (FMZ-C), user to confirm
FREQ = "3min"  # backtest header period: 3m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "rsi_line": [20, 30],
    "cooldown": [24, 8],
}
DEFAULT_PARAMS = {"rsi_len": 14, "rsi_line": 20, "stop_top": 70, "stop_bottom": 30, "sl": 0.03, "tp": 0.01,
                  "cooldown": 24}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def _rsi(c, n):
    ch = c.diff()
    up = ch.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    dn = (-ch.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    rsi = 100 - 100 / (1 + up / dn)
    rsi = rsi.where(up != 0, 0.0)
    return rsi.where(dn != 0, 100.0).where(ch.notna())


def _run(bars_df, p):
    ov, hv, lv, cv = (bars_df[k].to_numpy(dtype=float) for k in ("open", "high", "low", "close"))
    r = _rsi(bars_df["close"], int(p["rsi_len"])).to_numpy()
    m = len(cv)
    rl = float(p["rsi_line"])
    sl, tp, cd = float(p["sl"]), float(p["tp"]), int(p["cooldown"])
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    sl_lvl, tp_lvl = np.full(m, np.nan), np.full(m, np.nan)
    pos, e_i, ep, open_px = 0, -1, np.nan, 0.0
    pend_close, pend_loss, stop_trade, failed = False, False, False, 0
    for i in range(m):
        exit_px = np.nan
        if pos != 0 and i >= e_i:
            if pend_close:                                   # the close_all of the last bar, at this open
                exit_px, pend_close = ov[i], False
            else:
                lo_lvl = open_px * (1 - sl) if pos == 1 else open_px * (1 - tp)
                hi_lvl = open_px * (1 + tp) if pos == 1 else open_px * (1 + sl)
                if pos == 1 and lv[i] <= lo_lvl:
                    exit_px = min(ov[i], lo_lvl)
                elif pos == 1 and hv[i] >= hi_lvl:
                    exit_px = max(ov[i], hi_lvl)
                elif pos == -1 and hv[i] >= hi_lvl:
                    exit_px = max(ov[i], hi_lvl)
                elif pos == -1 and lv[i] <= lo_lvl:
                    exit_px = min(ov[i], lo_lvl)
            if not np.isnan(exit_px):
                loss = (exit_px - ep) * pos < 0
                pos = 0
            else:
                loss = False
        else:
            loss = False
        if pend_loss:                                        # the reversed position's exit at this open
            loss, pend_loss = True, False
        if stop_trade:
            failed += 1
            if failed == cd:
                failed, stop_trade = 0, False
        cur = pos if (pos == 0 or i >= e_i) else 0
        close_now = False
        if cur > 0 and (r[i] >= float(p["stop_top"]) or (cv[i] - ep) / ep >= tp):
            close_now = True
        if cur < 0 and (r[i] <= float(p["stop_bottom"]) or (ep - cv[i]) / cv[i] >= tp):
            close_now = True
        if loss:
            stop_trade = True
        new = 0
        if r[i] <= rl and not stop_trade:
            new = 1
        elif r[i] >= 100 - rl and not stop_trade:
            new = -1
        if new != 0 and new != pos:
            if cur == 0:
                open_px = cv[i]
            if new == 1:
                le[i] = True
            else:
                se[i] = True
            if cur != 0 and i + 1 < m:
                pend_loss = (ov[i + 1] - ep) * cur < 0
            pos, e_i, pend_close = new, i + 1, False
            ep = ov[i + 1] if i + 1 < m else np.nan
            sl_lvl[i] = open_px * (1 - sl) if new == 1 else open_px * (1 + sl)
            tp_lvl[i] = open_px * (1 + tp) if new == 1 else open_px * (1 - tp)
        elif close_now and new != pos:                       # a same-side entry re-opens after the close_all
            if pos == 1:
                lx[i] = True
            else:
                sx[i] = True
            pend_close = True
    return le, lx, se, sx, sl_lvl, tp_lvl


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    idx = bars_df.index
    return tuple(pd.Series(a, index=idx) for a in _run(bars_df, p)[:4])


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, _, se, _, sl_lvl, tp_lvl = _run(bars_df, p)
    idx = bars_df.index
    o = bars_df["open"]
    side = pd.Series(np.where(le, 1.0, np.where(se, -1.0, np.nan)), index=idx).shift(1)
    s = pd.Series(sl_lvl, index=idx).shift(1)
    t = pd.Series(tp_lvl, index=idx).shift(1)
    return {"sl_stop": ((o - s) / o * side).clip(lower=1e-9), "tp_stop": ((t - o) / o * side).clip(lower=1e-9)}


def portfolio_kwargs(**params):
    return {}
