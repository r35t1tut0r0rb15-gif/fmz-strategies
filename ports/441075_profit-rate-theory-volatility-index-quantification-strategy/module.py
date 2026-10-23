"""Three-hour bars: the TradingView technical rating (the average of the moving-average rating over 12 SMA / EMA, Hull 9, VWMA 20 and Ichimoku, and the oscillator rating over RSI, stochastic, CCI, ADX, AO, momentum, MACD, stochastic RSI, Williams %R, bull / bear power and the ultimate oscillator) above 0.5 goes long, below -0.5 goes short; a 3 ATR 14 stop from the entry; reversing.
Port of FMZ strategy #441075 "Profit rate theory volatility index quantification strategy" (Ratings (TradingView technical ratings)).

FMZ source id: 441075

Source
    https://www.fmz.com/strategy/441075 (PineScript v4, FMZ last modified 2024-02-05 13:54:34).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 142-424), rating on All; strong bound 0.5; exit loss 3 x ATR 14, trail points 5 x ATR, trail offset 2 x ATR (ticks); chart timeframe
    [ratingTotal, ratingOther, ratingMA, ...] = security(tickerid, "", calcRatingAll());  tradeSignal = ratingTotal
    tradeSignal > 0.5 -> entry long;  tradeSignal < -0.5 -> entry short;  exit("sl/tp", loss = 3 x atr(14) / mintick, trail_points = 5 x atr / mintick, trail_offset = 2 x atr / mintick)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The rating is TradingView's own recipe as written: each MA votes +1 / -1 / 0 by its side of the
      close, Ichimoku (undisplaced lines) by its full pattern; each oscillator votes by its rule; a vote
      counts only when its inputs exist; the MA and oscillator ratings are averaged, then the two. v4
      integer division: the UO weights are 28 / 7 = 4 and 28 / 14 = 2, Hull 9 uses wma(4). The security()
      call is on the chart's timeframe. The exit is re-sent every bar with the current ATR: the 3 ATR stop
      is fixed at the signal bar (3 x ATR[signal] / fill, mark trailing_stop_pending) and the ATR trail
      (5 ATR activation, 2 ATR offset) is not followed (same mark). REVERSAL INTENDED. 100 % of equity and
      the commission are sizing and costs. Stop module: portfolio_kwargs {} (driver D4). Stops on 3-hour
      bars: mark coarse_bar_stop. The entries repeat on every bar beyond the bound, so a position
      stopped out re-enters on the next such bar. FREQ = "3h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; ATR stop from the signal bar as a fraction of the fill.
    2 generic: PASS, TradingView technical-rating thresholds.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: strategy(): 100 % of equity, commission 0.1 %, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) in the VWMA 20 vote of the MA rating; exchange volume to be compared later (Austin, 2026-10-23).
Session open: none (24 h).
REVERSAL INTENDED.

Marks: coarse_bar_stop, trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_441075_tradingview_technical_rating_atr_stop_3h_reversal"
FAMILY = "indicator_vote"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "3h"  # backtest header period: 3h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "bound": [0.5, 0.3],
    "sl_atr": [3.0, 2.0],
}
DEFAULT_PARAMS = {"bound": 0.5, "sl_atr": 3.0, "atr_len": 14}


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


def _rsi(x, n):
    d = x.diff()
    up, dn = _rma(d.clip(lower=0), n), _rma((-d).clip(lower=0), n)
    out = 100 - 100 / (1 + up / dn.where(dn != 0))
    return out.where(up != 0, 0.0).where(dn != 0, 100.0).where(up.notna() & dn.notna())


def _wma(x, n):
    w = np.arange(1, n + 1, dtype=float)
    v = x.to_numpy(dtype=float)
    out = np.full(len(v), np.nan)
    if len(v) >= n:
        out[n - 1:] = np.lib.stride_tricks.sliding_window_view(v, n) @ w / w.sum()
    return pd.Series(out, index=x.index)


def _tr(h, lo, c):
    pc = c.shift(1)
    return pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1).where(pc.notna())


def _stoch(x, hi, lo, n):
    hh, ll = hi.rolling(n).max(), lo.rolling(n).min()
    return 100 * (x - ll) / (hh - ll).where(hh != ll)


def _vote(buy, sell, ok):
    return pd.Series(np.where(buy, 1.0, np.where(sell, -1.0, 0.0)), index=buy.index).where(ok)


def _rating(bars_df):
    h, lo, c, v = (bars_df[k] for k in ("high", "low", "close", "volume"))
    ma_votes = []
    for n in (10, 20, 30, 50, 100, 200):
        for ma in (c.rolling(n).mean(), c.ewm(span=n, adjust=False).mean()):
            ma_votes.append(pd.Series(np.where(ma < c, 1.0, np.where(ma > c, -1.0, 0.0)), index=c.index).where(ma.notna()))
    hma = _wma(2 * _wma(c, 4) - _wma(c, 9), 3)
    sv = v.rolling(20).mean()
    vwma = (c * v).rolling(20).mean() / sv.where(sv != 0)
    for ma in (hma, vwma):
        ma_votes.append(pd.Series(np.where(ma < c, 1.0, np.where(ma > c, -1.0, 0.0)), index=c.index).where(ma.notna()))

    def don(n):
        return (lo.rolling(n).min() + h.rolling(n).max()) / 2

    conv, base, lead2 = don(9), don(26), don(52)
    lead1 = (conv + base) / 2
    ic_ok = lead1.notna() & lead2.notna() & base.notna() & conv.notna() & c.shift(1).notna()
    c1 = c.shift(1)
    ma_votes.append(_vote((lead1 > lead2) & (c > lead1) & (c < base) & (c1 < conv) & (c > conv),
                          (lead2 > lead1) & (c < lead2) & (c > base) & (c1 > conv) & (c < conv), ic_ok))
    mv = pd.concat(ma_votes, axis=1)
    rating_ma = mv.sum(axis=1, min_count=1) / mv.notna().sum(axis=1).where(mv.notna().sum(axis=1) > 0)

    o_votes = []
    rsi = _rsi(c, 14)
    o_votes.append(_vote((rsi < 30) & (rsi.shift(1) < rsi), (rsi > 70) & (rsi.shift(1) > rsi), rsi.notna() & rsi.shift(1).notna()))
    k = _stoch(c, h, lo, 14).rolling(3).mean()
    d = k.rolling(3).mean()
    ok = k.notna() & d.notna() & k.shift(1).notna() & d.shift(1).notna()
    o_votes.append(_vote((k < 20) & (d < 20) & (k > d) & (k.shift(1) < d.shift(1)),
                         (k > 80) & (d > 80) & (k < d) & (k.shift(1) > d.shift(1)), ok))
    tp = c
    sma20 = tp.rolling(20).mean()
    mad = pd.Series(np.nan, index=c.index)
    if len(tp) >= 20:
        win = np.lib.stride_tricks.sliding_window_view(tp.to_numpy(dtype=float), 20)
        mad.iloc[19:] = np.abs(win - win.mean(axis=1, keepdims=True)).mean(axis=1)
    cci = (tp - sma20) / (0.015 * mad).where(mad != 0)
    o_votes.append(_vote((cci < -100) & (cci > cci.shift(1)), (cci > 100) & (cci < cci.shift(1)), cci.notna() & cci.shift(1).notna()))
    tr = _tr(h, lo, c)
    upm, dnm = h.diff(), -lo.diff()
    pdm = pd.Series(np.where((upm > dnm) & (upm > 0), upm, 0.0), index=c.index).where(upm.notna())
    mdm = pd.Series(np.where((dnm > upm) & (dnm > 0), dnm, 0.0), index=c.index).where(dnm.notna())
    atr14 = _rma(tr, 14)
    plus, minus = 100 * _rma(pdm, 14) / atr14, 100 * _rma(mdm, 14) / atr14
    ssum = plus + minus
    adx = 100 * _rma((plus - minus).abs() / ssum.where(ssum != 0, 1.0), 14)
    ok = adx.notna() & plus.notna() & minus.notna() & plus.shift(1).notna() & minus.shift(1).notna()
    o_votes.append(_vote((adx > 20) & (plus.shift(1) < minus.shift(1)) & (plus > minus),
                         (adx > 20) & (plus.shift(1) > minus.shift(1)) & (plus < minus), ok))
    hl2 = (h + lo) / 2
    ao = hl2.rolling(5).mean() - hl2.rolling(34).mean()
    a1, a2 = ao.shift(1), ao.shift(2)
    o_votes.append(_vote(((ao > 0) & (a1 <= 0)) | ((ao > 0) & (a1 > 0) & (ao > a1) & (a2 > a1)),
                         ((ao < 0) & (a1 >= 0)) | ((ao < 0) & (a1 < 0) & (ao < a1) & (a2 < a1)), ao.notna() & a1.notna()))
    mom = c - c.shift(10)
    o_votes.append(_vote(mom > mom.shift(1), mom < mom.shift(1), mom.notna() & mom.shift(1).notna()))
    macd = c.ewm(span=12, adjust=False).mean() - c.ewm(span=26, adjust=False).mean()
    sig = macd.ewm(span=9, adjust=False).mean()
    o_votes.append(_vote(macd > sig, macd < sig, macd.notna() & sig.notna()))
    e50 = c.ewm(span=50, adjust=False).mean()
    down, up = c < e50, c > e50
    r1 = _rsi(c, 14)
    sk = _stoch(r1, r1, r1, 14).rolling(3).mean()
    sd = sk.rolling(3).mean()
    ok = sk.notna() & sd.notna() & sk.shift(1).notna() & sd.shift(1).notna()
    o_votes.append(_vote(down & (sk < 20) & (sd < 20) & (sk > sd) & (sk.shift(1) < sd.shift(1)),
                         up & (sk > 80) & (sd > 80) & (sk < sd) & (sk.shift(1) > sd.shift(1)), ok))
    hh14, ll14 = h.rolling(14).max(), lo.rolling(14).min()
    wr = 100 * (c - hh14) / (hh14 - ll14).where(hh14 != ll14)
    o_votes.append(_vote((wr < -80) & (wr > wr.shift(1)), (wr > -20) & (wr < wr.shift(1)), wr.notna() & wr.shift(1).notna()))
    e13 = c.ewm(span=13, adjust=False).mean()
    bull_p, bear_p = h - e13, lo - e13
    o_votes.append(_vote(up & (bear_p < 0) & (bear_p > bear_p.shift(1)), down & (bull_p > 0) & (bull_p < bull_p.shift(1)),
                         bear_p.shift(1).notna() & bull_p.shift(1).notna()))
    tl = c.shift(1).where(c.shift(1) < lo, lo)
    bp = c - tl
    v1, v2, v3 = tr.rolling(7).sum(), tr.rolling(14).sum(), tr.rolling(28).sum()
    v4, v5, v6 = bp.rolling(7).sum(), bp.rolling(14).sum(), bp.rolling(28).sum()
    uo_ok = (v1 != 0) & (v2 != 0) & (v3 != 0)
    uo = ((v4 / v1 * 4 + v5 / v2 * 2 + v6 / v3) / 7 * 100).where(uo_ok)
    o_votes.append(_vote(uo > 70, uo < 30, uo.notna()))
    ov = pd.concat(o_votes, axis=1)
    cnt = ov.notna().sum(axis=1)
    rating_o = ov.sum(axis=1, min_count=1) / cnt.where(cnt > 0)
    both = pd.concat([rating_ma, rating_o], axis=1)
    bc = both.notna().sum(axis=1)
    return both.sum(axis=1, min_count=1) / bc.where(bc > 0)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    r = _rating(bars_df)
    b = float(p["bound"])
    lg, sh = r > b, r < -b                              # repeated every bar: re-enters after a stop, as Pine
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return lg.astype(bool), false, sh.astype(bool), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c, o = bars_df["high"], bars_df["low"], bars_df["close"], bars_df["open"]
    atr = _rma(_tr(h, lo, c), int(p["atr_len"]))
    return {"sl_stop": (float(p["sl_atr"]) * atr).shift(1) / o}


def portfolio_kwargs(**params):
    return {}
