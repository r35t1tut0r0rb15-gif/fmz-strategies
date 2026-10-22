"""PSAR / EMA 30 crossing set-ups inside a 09:15-15:15 UTC session, 1-hour bars: after a PSAR cross under the EMA, the first green candle marks a low, and a close crossing back under that low buys from flat; the mirror (a red candle's high after a cross over, a close crossing over it) sells short from flat; a 16 % stop and 32 % target from the fill; everything is closed on the first bar outside the session.
Port of FMZ strategy #452692 "基于PSAR与EMA的量化策略-PSAR-and-EMA-Based-Quantitative-Trading-Strategy" (aj sir second project (PSAR and EMA)).

FMZ source id: 452692

Source
    https://www.fmz.com/strategy/452692 (PineScript v5, FMZ last modified 2024-05-28 11:00:40).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 94-252), PSAR 0.02 / 0.02 / 0.2; EMA 30; session 0915-1515; stop 16 %, target 32 % of the fill (targets 1 / 2 plotted only)
    flags: crossunder(psar, ema) not on a PSAR flip -> down flag; first green candle under it -> igc; crossover -> up flag; first red candle -> irc
    igc low / irc high by valuewhen;  crossunder(close, igc low) with the igc low valid, flat, in session -> entry buy;  crossover(close, irc high) valid, flat, in session -> entry short
    exit(stop = fill x 0.84, limit = fill x 1.32) / exit(stop = fill x 1.16, limit = fill x 0.68);  outside the session -> close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * The flag chain (crodownflag, igcflag, croupflag, ircflag, the 'there' guards and the valid-low
      / valid-high switches) is followed bar by bar as written. The fill price is the open of the bar
      after the signal (the source's valuewhen on buy1 / short1 with a flat previous bar), so the
      bracket is fixed fractions of the fill, ported active from the fill bar (#440797). Entries need
      a flat position on the signal bar, so the loop follows the bracket on each bar's high / low.
      The session is read on the bar's UTC open (as #435514): a bar opening 09:15 to 15:14 UTC is in
      it (on 1-hour bars: 10:00 to 15:00); every bar outside it closes all. Opposite entries cannot
      occur (entries only from flat). Stop module: portfolio_kwargs {} (driver D4). The margin
      settings are sizing. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; the fill-price bracket as fixed fractions; the flag chain in a loop.
    2 generic: PASS, PSAR / EMA set-up candles with level re-crosses.
    3 crypto-exchange-only: no (spot pair in the header only (the source sends shorts as written)).
    4 signals only: the margin settings stored.
    5 ranges declared: GRID below (8 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: 0915-1515 on the UTC bar open; close_all outside.
Opposite entries cannot occur (entries only from flat).

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_452692_psar_ema30_setup_candle_level_session_bracket"
FAMILY = "parabolic_sar"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "ema_len": [30, 50],
    "sl_pct": [0.16, 0.08],
    "tp_pct": [0.32, 0.16],
}
DEFAULT_PARAMS = {"ema_len": 30, "sl_pct": 0.16, "tp_pct": 0.32, "sar_start": 0.02, "sar_inc": 0.02,
                  "sar_max": 0.2, "sess_start": 555, "sess_end": 915}


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


def _sar(h, lo, c, start, inc, mx):
    """Pine's sar reference block: the SAR value per bar (nan on the first bar)."""
    n = len(c)
    out = np.full(n, np.nan)
    result = max_min = acc = np.nan
    below = False
    for i in range(1, n):
        first = False
        if i == 1:
            if c[1] > c[0]:
                below, max_min, result = True, h[1], lo[0]
            else:
                below, max_min, result = False, lo[1], h[0]
            first, acc = True, start
        result = result + acc * (max_min - result)
        if below:
            if result > lo[i]:
                first, below = True, False
                result, max_min, acc = max(h[i], max_min), lo[i], start
        else:
            if result < h[i]:
                first, below = True, True
                result, max_min, acc = min(lo[i], max_min), h[i], start
        if not first:
            if below:
                if h[i] > max_min:
                    max_min, acc = h[i], min(acc + inc, mx)
            else:
                if lo[i] < max_min:
                    max_min, acc = lo[i], min(acc + inc, mx)
        if below:
            result = min(result, lo[i - 1])
            if i > 1:
                result = min(result, lo[i - 2])
        else:
            result = max(result, h[i - 1])
            if i > 1:
                result = max(result, h[i - 2])
        out[i] = result
    return out


def _levels(bars_df, p):
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    ps = pd.Series(_sar(h.to_numpy(dtype=float), lo.to_numpy(dtype=float), c.to_numpy(dtype=float),
                        float(p["sar_start"]), float(p["sar_inc"]), float(p["sar_max"])), index=c.index)
    ema = c.ewm(span=int(p["ema_len"]), adjust=False).mean()
    cdown = ((ps < ema) & (ps.shift(1) >= ema.shift(1))).to_numpy()
    cup = ((ps > ema) & (ps.shift(1) <= ema.shift(1))).to_numpy()
    flip_up = ((ps < c) & (ps.shift(1) > c.shift(1))).to_numpy()
    flip_dn = ((ps > c) & (ps.shift(1) < c.shift(1))).to_numpy()
    green, red = (c > o).to_numpy(), (c < o).to_numpy()
    hv, lv = h.to_numpy(dtype=float), lo.to_numpy(dtype=float)
    m = len(c)
    igc_low, irc_high = np.full(m, np.nan), np.full(m, np.nan)
    v_igc_a, v_irc_a = np.zeros(m, dtype=int), np.zeros(m, dtype=int)
    cd = igc = cu = irc = irc_th = igc_th = v_irc = v_igc = 0
    p_igc_c1 = p_irc_c1 = p_irc_c = False
    lo_v = hi_v = np.nan
    for i in range(m):
        if cdown[i] and cd == 0 and not flip_up[i]:
            cd = 1
        elif cdown[i] and cd == 1:
            cd = 0
        prev_igc = igc
        if cd == 1 and green[i] and igc == 0:
            igc = 1
        elif cdown[i] and igc == 1:
            igc = 0
        if cup[i] and cu == 0 and not flip_dn[i]:
            cu = 1
        elif cdown[i] and cu == 1:
            cu = 0
        prev_irc = irc
        if cu == 1 and red[i] and irc == 0:
            irc = 1
        elif cup[i] and cu == 1:
            irc = 0
        igc_c1 = (igc == 1 and prev_igc == 0) or (cdown[i] and not flip_up[i] and green[i])
        irc_c1 = (irc == 1 and prev_irc == 0) or (cup[i] and not flip_dn[i] and red[i])
        if p_irc_c1 and irc_th == 0:
            irc_th = 1
        elif cdown[i] and irc_th == 1:
            irc_th = 0
        irc_c = irc_c1 and irc_th == 0
        if p_igc_c1 and igc_th == 0:
            igc_th = 1
        elif cup[i] and igc_th == 1:
            igc_th = 0
        igc_c = igc_c1 and igc_th == 0
        if p_irc_c and v_irc == 0:
            v_irc = 1
        elif igc_c and v_irc == 1:
            v_irc = 0
        if igc_c and v_igc == 0:
            v_igc = 1
        elif irc_c and v_igc == 1:
            v_igc = 0
        if igc_c:
            lo_v = lv[i]
        if irc_c:
            hi_v = hv[i]
        igc_low[i], irc_high[i], v_igc_a[i], v_irc_a[i] = lo_v, hi_v, v_igc, v_irc
        p_igc_c1, p_irc_c1, p_irc_c = igc_c1, irc_c1, irc_c
    gl, rh = pd.Series(igc_low, index=c.index), pd.Series(irc_high, index=c.index)
    buy = ((c < gl) & (c.shift(1) >= gl.shift(1))).to_numpy() & (v_igc_a == 1)
    short = ((c > rh) & (c.shift(1) <= rh.shift(1))).to_numpy() & (v_irc_a == 1)
    return buy, short


def _run(bars_df, p):
    buy, short = _levels(bars_df, p)
    ix = bars_df.index
    tod = (ix.hour * 60 + ix.minute).to_numpy()
    st = (tod >= int(p["sess_start"])) & (tod < int(p["sess_end"]))
    sl, tp = float(p["sl_pct"]), float(p["tp_pct"])
    ov = bars_df["open"].to_numpy(dtype=float)
    hv, lv = bars_df["high"].to_numpy(dtype=float), bars_df["low"].to_numpy(dtype=float)
    m = len(ov)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    pos, pend, avg = 0, 0, np.nan
    for i in range(m):
        if pend in (1, -1):
            pos, avg = pend, ov[i]
        elif pend == 2:
            pos = 0
        pend = 0
        if pos == 1 and (lv[i] <= avg * (1 - sl) or hv[i] >= avg * (1 + tp)):
            pos = 0
        elif pos == -1 and (hv[i] >= avg * (1 + sl) or lv[i] <= avg * (1 - tp)):
            pos = 0
        if st[i]:
            if pos == 0 and short[i]:
                se[i], pend = True, -1           # the later call wins a same-bar tie
            elif pos == 0 and buy[i]:
                le[i], pend = True, 1
        elif pos == 1:
            lx[i], pend = True, 2                # close_all outside the session
        elif pos == -1:
            sx[i], pend = True, 2
    return le, lx, se, sx


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    ix = bars_df.index
    return tuple(pd.Series(a, index=ix) for a in _run(bars_df, p))


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["sl_pct"]), "tp_stop": float(p["tp_pct"])}


def portfolio_kwargs(**params):
    return {}
