"""Three-minute bars: with the Coral Trend line (smoothing 25, constant 0.4) rising, a bar fully above it since the last cross above, and a pullback close below it while the line stayed rising, the close crossing back above it with ADX / DI confirmation (DI+ over DI-, ADX 14 above 20 and rising) goes long; the bearish mirror goes short; each with a stop at the 5-bar low / high of the signal bar and a target 1.5 times that distance; reversing.
Port of FMZ strategy #440971 "基于回测试区间Coral-Trend指标的瑞波策略Coral-Trend-Pullback-Strategy" (Coral Trend Pullback Strategy (TradeIQ) (kevinmck100)).

FMZ source id: 440971

Source
    https://www.fmz.com/strategy/440971 (PineScript v5, FMZ last modified 2024-02-04 12:18:03).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 246-601), Coral Trend 25 / 0.4; confirmation ADX and DI (length 14, mid line 20); stop = 5-bar local low / high; R:R 1.5; 1 % portfolio risk sizing
    goLong = isCoralBullish and prePullbackBullBreakout and isPullbackValid and entryBreakout and longTradeConfirmed;  openLong = goLong and not inLong -> entry Long
    lossPoints = round(slPercent / 100 x close / mintick) (slPercent from close - lowest(5));  profitPoints = 1.5 x;  exit("TP/SL", profit = profitPoints, loss = lossPoints) every bar

Interpretation choices (Pine rules in SURVEY_README.md)
    * The Coral Trend is LazyBear's six-stage smoothing (each stage seeded from 0 by nz, as written). The
      bracket distances are fixed on the signal bar from that bar's close: stop close - lowest(low, 5)
      (highest(high, 5) - close for a short) and target 1.5 times it, in ticks from the entry price;
      ported as fractions of the fill (distance / open of the fill bar), exact; a zero distance leaves no
      bracket. The script's own inLong / inShort flags (which gate new entries) are cleared when its
      signal-close levels are hit, as written; a new signal in the same direction while the position is
      still open (after those flags cleared) re-sends new points, which the port does not follow. ADX and
      DI as the script's own Wilder sums (nz(close[1]) on the first bar). The HawkEye volume
      confirmation is not the default: volume is not used. REVERSAL INTENDED. The 1 % risk sizing is
      sizing. Stop module: portfolio_kwargs {} (driver D4). FREQ = "3min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; swing-based bracket from the signal bar as fractions of the fill.
    2 generic: PASS, Coral Trend pullback re-entries confirmed by ADX / DI.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: qty = equity x 1 % / stop % / close, commission 0.02 %, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: none (24 h).
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_440971_coral_trend_pullback_adx_di_swing_bracket_3m_reversal"
FAMILY = "trend_pullback"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "3min"  # backtest header period: 3m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "ct_sm": [25, 50],
    "risk_reward": [1.5, 2.0],
}
DEFAULT_PARAMS = {"ct_sm": 25, "ct_cd": 0.4, "adx_len": 14, "mid_line": 20, "lookback": 5, "risk_reward": 1.5}


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


def _coral(c, sm, cd):
    di = (sm - 1.0) / 2.0 + 1.0
    c1 = 2 / (di + 1.0)
    c2 = 1 - c1
    c3 = 3.0 * (cd * cd + cd * cd * cd)
    c4 = -3.0 * (2.0 * cd * cd + cd + cd * cd * cd)
    c5 = 3.0 * cd + 1.0 + cd * cd * cd + 3.0 * cd * cd
    src = c.to_numpy(dtype=float)
    m = len(src)
    st = np.zeros(6)
    out = np.full(m, np.nan)
    for i in range(m):
        x = src[i]
        for k in range(6):
            st[k] = c1 * x + c2 * st[k]
            x = st[k]
        out[i] = -cd * cd * cd * st[5] + c3 * st[4] + c4 * st[3] + c5 * st[2]
    return pd.Series(out, index=c.index)


def _since(cond):
    """ta.barssince: bars since cond was last true (NaN before the first)."""
    v = np.asarray(cond, dtype=bool)
    out = np.full(len(v), np.nan)
    last = -1
    for i in range(len(v)):
        if v[i]:
            last = i
        if last >= 0:
            out[i] = i - last
    return out


def _adx_di(h, lo, c, n):
    hv, lv, cv = (x.to_numpy(dtype=float) for x in (h, lo, c))
    m = len(cv)
    pdi, mdi = np.full(m, np.nan), np.full(m, np.nan)
    s_tr = s_p = s_m = 0.0
    for i in range(m):
        pc = cv[i - 1] if i > 0 else 0.0
        ph = hv[i - 1] if i > 0 else 0.0
        pl = lv[i - 1] if i > 0 else 0.0
        tr = max(max(hv[i] - lv[i], abs(hv[i] - pc)), abs(lv[i] - pc))
        dp = max(hv[i] - ph, 0.0) if hv[i] - ph > pl - lv[i] else 0.0
        dm = max(pl - lv[i], 0.0) if pl - lv[i] > hv[i] - ph else 0.0
        s_tr = s_tr - s_tr / n + tr
        s_p = s_p - s_p / n + dp
        s_m = s_m - s_m / n + dm
        if s_tr != 0:
            pdi[i], mdi[i] = s_p / s_tr * 100, s_m / s_tr * 100
    p_, m_ = pd.Series(pdi, index=c.index), pd.Series(mdi, index=c.index)
    s = p_ + m_
    dx = (p_ - m_).abs() / s.where(s != 0) * 100
    return dx.rolling(n).mean(), p_, m_


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    bfr = _coral(c, int(p["ct_sm"]), float(p["ct_cd"]))
    pb = bfr.shift(1).fillna(0.0)
    bull, bear = (bfr > pb).to_numpy(), (bfr < pb).to_numpy()
    x_up = ((c > bfr) & (c.shift(1) <= bfr.shift(1))).to_numpy()
    x_dn = ((c < bfr) & (c.shift(1) >= bfr.shift(1))).to_numpy()
    s_bull_bo = _since(x_up)
    s_bear_bo = _since(x_dn)
    above = _since(((lo > bfr) & (h > bfr)).to_numpy())
    below = _since(((lo < bfr) & (h < bfr)).to_numpy())
    pre_bull = above < np.concatenate(([np.nan], s_bull_bo[:-1]))
    pre_bear = below < np.concatenate(([np.nan], s_bear_bo[:-1]))
    pull_start = np.where(bull, s_bear_bo, np.where(bear, s_bull_bo, np.nan))
    flip_up = ((bfr > pb) & (bfr.shift(1) <= pb.shift(1))).to_numpy()
    flip_dn = ((bfr < pb) & (bfr.shift(1) >= pb.shift(1))).to_numpy()
    flip = np.where(bull, _since(flip_up), np.where(bear, _since(flip_dn), np.nan))
    valid = pull_start < flip
    brk = (bull & x_up) | (bear & x_dn)
    adx, pdi, mdi = _adx_di(h, lo, c, int(p["adx_len"]))
    adx_ok = ((adx > float(p["mid_line"])) & (adx > adx.shift(1))).to_numpy()
    l_conf = (pdi > mdi).to_numpy() & adx_ok
    s_conf = (mdi > pdi).to_numpy() & adx_ok
    go_l = bull & pre_bull & valid & brk & l_conf
    go_s = bear & pre_bear & valid & brk & s_conf
    lb = int(p["lookback"])
    ll, hh = lo.rolling(lb).min().to_numpy(), h.rolling(lb).max().to_numpy()
    hv, lv, cv = h.to_numpy(dtype=float), lo.to_numpy(dtype=float), c.to_numpy(dtype=float)
    rr = float(p["risk_reward"])
    m = len(cv)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    in_l = in_s = False
    sl_px = tp_px = 0.0
    for i in range(m):
        in_trade = in_l or in_s
        open_l = go_l[i] and not in_l
        open_s = go_s[i] and not in_s
        if open_l:
            le[i], in_l, in_s = True, True, False
        if open_s:
            se[i], in_s, in_l = True, True, False
        if open_l or open_s:
            dist = (cv[i] - ll[i]) if bull[i] else (hh[i] - cv[i])
            sign = 1 if open_l else -1
            sl_px, tp_px = cv[i] - sign * dist, cv[i] + sign * dist * rr
        sl_hit = (in_s and hv[i] >= sl_px) or (in_l and lv[i] <= sl_px)
        tp_hit = (in_l and hv[i] >= tp_px) or (in_s and lv[i] <= tp_px)
        if in_trade and (sl_hit or tp_hit):
            in_l = in_s = False
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, pd.Series(se, index=ix), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, lx, se, sx = simulate(bars_df, **params)
    h, lo, c, o = bars_df["high"], bars_df["low"], bars_df["close"], bars_df["open"]
    lb = int(p["lookback"])
    bfr = _coral(c, int(p["ct_sm"]), float(p["ct_cd"]))
    bull = bfr > bfr.shift(1).fillna(0.0)
    dist = ((c - lo.rolling(lb).min()).where(bull, h.rolling(lb).max() - c)).shift(1) / o
    filled = le.shift(1, fill_value=False) | se.shift(1, fill_value=False)
    sl_f = dist.where(filled & (dist > 0))
    return {"sl_stop": sl_f, "tp_stop": float(p["risk_reward"]) * sl_f}


def portfolio_kwargs(**params):
    return {}
