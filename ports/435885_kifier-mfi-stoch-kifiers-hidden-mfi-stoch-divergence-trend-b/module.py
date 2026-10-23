"""Hourly bars, long only: a stochastic 28 at or above 50 with the MFI 7 crossing over 50, the VWMA 50 above the SMA 50 with the close above it, OBV above its EMA 100 and a trending ATR regime goes long; so does a hidden bullish MFI divergence (higher price low and higher MFI low) in a ranging regime, for 5 bars, from flat; a 10 % target, and a close at or under the support level saved at the signal closes.
Port of FMZ strategy #435885 "Kifier隐藏式MFI-STOCH指标交易-趋势操盘策略Kifiers-Hidden-MFI-STOCH-Divergence-Trend-Breaker-Trading-Strategy" (Kifier's MFI/STOCH Hidden Divergence/Trend Beater).

FMZ source id: 435885

Source
    https://www.fmz.com/strategy/435885 (PineScript v4, FMZ last modified 2023-12-19 15:18:09).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 159-363), VWMA 50, SMA 50; stoch 28; MFI 7 (90 / 10); OBV EMA 100; ATR regime EMA 50 / 100 of atr(14) / close; price pivots 5 / 5, inaccuracy 5 %; MFI pivots 5 / 2; TP 10 %; support pivots 20 / 20, inaccuracy 3 %
    mfi_stoch_trend = stoch >= 50 and crossover(mfi, 50) and vwma > sma and close >= vwma and obv > ema(obv, 100) and not ranging -> entry Buy
    mfi_div = higher_low and higher_low_m and vwma > sma and close >= vwma and stoch >= 50 and ranging -> buy window 5 bars while flat -> entry Buy;  order_fired -> previousRes := _pL
    position_size > 0 -> exit("Buy", limit = avg x 1.10);  close <= previousRes -> exit("Buy", stop = previousRes)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The pivot bookkeeping runs as written, including its operator precedence: "a or b and pivot"
      updates the price lows whenever low x 1.05 is under the saved low, not only on pivots; the support
      _pL is set to the CURRENT bar's low when a 20 / 20 pivot low is confirmed or when the low drops 3 %
      under it. Pivots are strict. ta.mfi(close, 7) uses the close as source. The second strategy.exit
      reuses the id "Buy", so it replaces the target with a stop at the saved support; it is sent only
      when the close is already at or under that level, so it fills at the next open: ported as a close
      signal (and the target as a 10 % fraction of the fill, sent from the bar after the fill in the
      script). The target is followed in the signals to know when the position is flat. A stop call on a
      bar whose entry is still pending is not ported (approximation). The divergence window counter
      starts at 0, which would also buy on the first loaded bar; that start-up buy is not ported. The
      date range is off. Long only.
      95 % of equity is sizing. Stop module: portfolio_kwargs {} (driver D4). FREQ = "1h" from the backtest
      header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; percent target from the fill; support-break close.
    2 generic: PASS, MFI / stochastic trend and hidden-divergence entries.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: strategy(): 95 % of equity, margin_long / margin_short 100, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) in the VWMA 50, ta.mfi(close, 7) and the OBV trend; exchange volume to be compared later (Austin, 2026-10-23).
Session open: not used (date range off).
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_435885_mfi_stoch_trend_hidden_divergence_support_exit_long"
FAMILY = "mfi_divergence"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "tp": [0.10, 0.05],
    "mfi_len": [7, 14],
}
DEFAULT_PARAMS = {"vwma_len": 50, "sma_len": 50, "stoch_len": 28, "mfi_len": 7, "obv_len": 100, "atr_len": 100,
                  "div_price": 5, "inacc": 0.05, "mfi_left": 5, "mfi_right": 2, "tp": 0.10, "sup_inacc": 0.03}


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


def _mfi(src, vol, n):
    """Pine ta.mfi: money-flow ratio over n bars; 100 when the falling flow is 0, 0 when the rising is 0."""
    ch = src.diff()
    upper = (vol * src.where(~(ch <= 0), 0.0)).rolling(n).sum()
    lower = (vol * src.where(~(ch >= 0), 0.0)).rolling(n).sum()
    out = 100.0 - 100.0 / (1.0 + upper / lower.where(lower != 0))
    return out.where(upper != 0, 0.0).where(lower != 0, 100.0).where(upper.notna() & lower.notna())


def _pivot_hit(x, side, left, right):
    """pivothigh / pivotlow(x, left, right) found on this bar (strict), and the pivot value x[right]."""
    s = x if side > 0 else -x
    centre = s.shift(right)
    lft = s.shift(right + 1).rolling(left).max()
    rgt = s.rolling(right).max()
    return ((centre > lft) & (centre > rgt)).to_numpy(), x.shift(right).to_numpy(dtype=float)


def _signals(bars_df, p):
    o, h, lo, c, v = (bars_df[k] for k in ("open", "high", "low", "close", "volume"))
    hv, lv, cv = h.to_numpy(dtype=float), lo.to_numpy(dtype=float), c.to_numpy(dtype=float)
    m = len(cv)
    # support level _pL
    pl20, _ = _pivot_hit(lo, -1, 20, 20)
    sup = np.full(m, np.nan)
    q = np.nan
    si = float(p["sup_inacc"])
    for i in range(m):
        q_prev = q
        if pl20[i]:
            q = lv[i]
        if lv[i] + si * lv[i] < q_prev:
            q = lv[i]
        sup[i] = q
    # price higher lows (operator precedence as written)
    ph5, _ = _pivot_hit(h, 1, int(p["div_price"]), int(p["div_price"]))
    pl5, _ = _pivot_hit(lo, -1, int(p["div_price"]), int(p["div_price"]))
    ia = float(p["inacc"])
    p_h, p_l = 0.0, 0.0
    higher_low = np.zeros(m, dtype=bool)
    for i in range(m):
        prev_l = p_l
        if (hv[i] - hv[i] * ia) > p_h or ((hv[i] + hv[i] * ia) < p_h and ph5[i]):
            p_h = hv[i]
        if (lv[i] + lv[i] * ia) < p_l or ((lv[i] - lv[i] * ia) > p_l and pl5[i]):
            p_l = lv[i]
        if (ph5[i] or pl5[i]) and p_l > prev_l:
            higher_low[i] = True
    # MFI higher lows
    mfi = _mfi(c, v, int(p["mfi_len"]))
    ml_hit, ml_val = _pivot_hit(mfi, -1, int(p["mfi_left"]), int(p["mfi_right"]))
    m_l = 0.0
    higher_low_m = np.zeros(m, dtype=bool)
    for i in range(m):
        if ml_hit[i] and ml_val[i] != 0:
            prev = m_l
            m_l = ml_val[i]
            higher_low_m[i] = m_l > prev
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1).where(pc.notna())
    ar = _rma(tr, 14) / c
    na_ = int(p["atr_len"])
    ranging = (ar.ewm(span=na_ // 2, adjust=False).mean() < ar.ewm(span=na_, adjust=False).mean()).to_numpy()
    obv = (np.sign(c.diff()).fillna(0.0) * v).cumsum()
    long_trend = (obv > obv.ewm(span=int(p["obv_len"]), adjust=False).mean()).to_numpy() & ~ranging
    nv = int(p["vwma_len"])
    vs = v.rolling(nv).sum()
    vw = (c * v).rolling(nv).sum() / vs.where(vs != 0)
    sm = c.rolling(int(p["sma_len"])).mean()
    crossing_over = ((vw > sm) & (c >= vw)).to_numpy()
    ns = int(p["stoch_len"])
    ll, hh = lo.rolling(ns).min(), h.rolling(ns).max()
    st = (100 * (c - ll) / (hh - ll).where(hh != ll)).to_numpy()
    mfi_x = ((mfi > 50) & (mfi.shift(1) <= 50)).to_numpy()
    mst = (st >= 50) & mfi_x & crossing_over & long_trend & ~ranging
    mdiv = higher_low & higher_low_m & crossing_over & (st >= 50) & ranging
    return mst, mdiv, sup


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    mst, mdiv, sup = _signals(bars_df, p)
    ov, hv, cv = (bars_df[k].to_numpy(dtype=float) for k in ("open", "high", "close"))
    tp = float(p["tp"])
    m = len(cv)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, avg, pending, counter, prev_res = 0, np.nan, False, -1, 0.0
    for i in range(m):
        fresh = False
        if pending:
            avg, pending, fresh = ov[i], False, True          # the entry fills at this bar's open
        if pos == 1 and not fresh and hv[i] >= avg * (1 + tp):
            pos = 0                                            # the target, sent from the bar after the fill
        if mdiv[i]:
            counter = i + 5
        fired = mst[i] or (i <= counter and pos == 0)
        if fired and pos == 0 and i + 1 < m:
            le[i], pos, pending = True, 1, True
        if fired:
            prev_res = sup[i]
        if pos == 1 and not pending and cv[i] <= prev_res:
            lx[i], pos = True, 0
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"tp_stop": float(p["tp"])}


def portfolio_kwargs(**params):
    return {}
