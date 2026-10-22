"""SSL channel flips confirmed by Wave Trend crossings and the SSL Hybrid baseline, 1-hour bars: an SSL flip up with a Wave Trend cross up, the close above the HMA 60 Keltner baseline, a small candle
inside the Keltner channel and a target clear of the EMA 200 goes long, the mirror short; a 1.7 NNFX-ATR stop and a 2.5 R target from the entry; reversing.
Port of FMZ strategy #442097 "基于SSL通道和波浪趋势的量化交易策略SSL-Channel-and-Wave-Trend-Quantitative-Trading-Strategy" (SSL + Wave Trend Strategy).

FMZ source id: 442097

Source
    https://www.fmz.com/strategy/442097 (PineScript v5, FMZ last modified 2024-02-19 11:47:38).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 250-763), all entry conditions on; baseline HMA 60 (channel x 0.2 of EMA(TR, 60)); SSL 10; WT 10 / 21; KC EMA 20 x 1.5 ATR 10, wicks; candle height 1 %; EMA 200; stop 1.7 x ATR 14 (RMA); RR 2.5; risk 1 %
    goLong = close > HMA60 + 0.2 ema(tr, 60) and crossover(sslUp, sslDown) and crossover(wt1, wt2) and candle <= 1 % and inside KC and not (close < ema200 and tpTarget > ema200);  goShort mirrored
    openLong = goLong and not inLong -> entry Long;  openShort = goShort and not inShort -> entry Short;  on entry: loss / profit points = sl% / tp% of the close in ticks, sl% = 1.7 ATR / close, tp% = 2.5 sl%
    strategy.exit("TP/SL", profit = profitPoints, loss = lossPoints) every bar;  inLong / inShort cleared when the signal-close levels are touched

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is a percentage of the signal close converted to ticks and applied from the entry:
      sl = 1.7 ATR(14) / close (truncated to 5 decimals as written), tp = 2.5 sl, shifted one bar inside
      stops() and re-based on the fill. The script's inLong / inShort flags, which gate new entries, are
      ported as written (cleared when the bar touches the levels set from the signal close). A new entry on
      the other side reverses: REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4). The
      risk-based quantity is sizing. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry from signal-bar data.
    2 generic: PASS, SSL, Wave Trend, Keltner and EMA filters with an ATR bracket.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the 1 % risk quantity, capital and commission stored.
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

NAME = "fmz_442097_ssl_wavetrend_keltner_atr_bracket"
FAMILY = "multi_indicator_confluence"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sl_atr_mult": [1.7, 2.5],
    "risk_reward": [2.5, 1.5],
}
DEFAULT_PARAMS = {"sl_atr_mult": 1.7, "risk_reward": 2.5, "base_len": 60, "multy": 0.2, "ssl_len": 10,
                  "n1": 10, "n2": 21, "kc_len": 20, "kc_mult": 1.5, "kc_atr": 10, "candle_height": 1.0,
                  "ema_len": 200, "atr_len": 14}


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


def _wma(x, n):
    w = np.arange(1, n + 1, dtype=float)
    return x.rolling(n).apply(lambda a: np.dot(a, w) / w.sum(), raw=True)


def _hma(src, n):
    return _wma(2 * _wma(src, n // 2) - _wma(src, n), int(round(np.sqrt(n))))


def _sl_frac(bars_df, p):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    atr = np.trunc(_rma(tr, int(p["atr_len"])) * 1e5) / 1e5
    return atr * float(p["sl_atr_mult"]) / c


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c = bars_df["open"], bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr_na = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1).where(pc.notna())
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    bl = int(p["base_len"])
    kelt = _hma(c, bl)
    rng = tr_na.ewm(span=bl, adjust=False).mean()
    upk, lok = kelt + rng * float(p["multy"]), kelt - rng * float(p["multy"])
    sn = int(p["ssl_len"])
    smh, sml = h.rolling(sn).mean().to_numpy(), lo.rolling(sn).mean().to_numpy()
    cv = c.to_numpy(dtype=float)
    m = len(cv)
    hlv = np.full(m, np.nan)
    hv_ = np.nan
    for i in range(m):
        if cv[i] > smh[i]:
            hv_ = 1.0
        elif cv[i] < sml[i]:
            hv_ = -1.0
        hlv[i] = hv_
    neg = hlv < 0
    s_dn = pd.Series(np.where(neg, smh, sml), index=c.index)
    s_up = pd.Series(np.where(neg, sml, smh), index=c.index)
    ap = (h + lo + c) / 3
    esa = ap.ewm(span=int(p["n1"]), adjust=False).mean()
    dd = (ap - esa).abs().ewm(span=int(p["n1"]), adjust=False).mean()
    wt1 = ((ap - esa) / (0.015 * dd)).ewm(span=int(p["n2"]), adjust=False).mean()
    wt2 = wt1.rolling(4).mean()
    wt_up = (wt1 > wt2) & (wt1.shift(1) <= wt2.shift(1))
    wt_dn = (wt1 < wt2) & (wt1.shift(1) >= wt2.shift(1))
    kcm = c.ewm(span=int(p["kc_len"]), adjust=False).mean()
    katr = _rma(tr, int(p["kc_atr"]))
    ktop, kbot = kcm + float(p["kc_mult"]) * katr, kcm - float(p["kc_mult"]) * katr
    p_red = ((o - c) / c * 100).where(o > c, 0.0)
    p_green = ((c - o) / o * 100).where(o < c, 0.0)
    ch = float(p["candle_height"])
    candle_ok = (p_green <= ch) & (p_red <= ch)
    inside = (h < ktop) & (lo > kbot)
    ema = c.ewm(span=int(p["ema_len"]), adjust=False).mean()
    sl_s = _sl_frac(bars_df, p)
    tp_s = sl_s * float(p["risk_reward"])
    tp_target = c * (1 + tp_s.where(wt_up, -tp_s))
    bull_tp = ~((c < ema) & (tp_target > ema))
    bear_tp = ~((c > ema) & (tp_target < ema))
    go_l = ((c > upk) & (s_up > s_dn) & (s_up.shift(1) <= s_dn.shift(1)) & wt_up & candle_ok & inside & bull_tp).to_numpy()
    go_s = ((c < lok) & (s_dn > s_up) & (s_dn.shift(1) <= s_up.shift(1)) & wt_dn & candle_ok & inside & bear_tp).to_numpy()
    sl, tp = sl_s.to_numpy(), tp_s.to_numpy()
    ov, hv, lv = o.to_numpy(dtype=float), h.to_numpy(dtype=float), lo.to_numpy(dtype=float)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, entry_i, s_, t_ = 0, -1, np.nan, np.nan
    in_l = in_s = False
    sl_px = tp_px = 0.0
    for i in range(m):
        if pos != 0 and i >= entry_i:
            x = ov[entry_i]
            if pos == 1 and (lv[i] <= x * (1 - s_) or hv[i] >= x * (1 + t_)):
                pos = 0
            elif pos == -1 and (hv[i] >= x * (1 + s_) or lv[i] <= x * (1 - t_)):
                pos = 0
        in_trade = in_l or in_s
        open_l = go_l[i] and not in_l
        open_s = go_s[i] and not in_s
        ok = i + 1 < m and not np.isnan(sl[i])
        if open_l and ok:
            if pos != 1:
                le[i] = True
            pos, entry_i, s_, t_ = 1, i + 1, sl[i], tp[i]
            in_l, in_s = True, False
        if open_s and ok:
            if pos != -1:
                se[i] = True
                le[i] = False
            pos, entry_i, s_, t_ = -1, i + 1, sl[i], tp[i]
            in_s, in_l = True, False
        if (open_l or open_s) and ok:
            sgn = 1 if open_l else -1
            sl_px = cv[i] * (1 - sgn * sl[i])
            tp_px = cv[i] * (1 + sgn * tp[i])
        hit = (in_s and hv[i] >= sl_px) or (in_l and lv[i] <= sl_px) \
            or (in_l and hv[i] >= tp_px) or (in_s and lv[i] <= tp_px)
        if in_trade and hit:
            in_l = in_s = False
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, pd.Series(se, index=ix), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    sl = _sl_frac(bars_df, p)
    return {"sl_stop": sl.shift(1), "tp_stop": (sl * float(p["risk_reward"])).shift(1)}


def portfolio_kwargs(**params):
    return {}
