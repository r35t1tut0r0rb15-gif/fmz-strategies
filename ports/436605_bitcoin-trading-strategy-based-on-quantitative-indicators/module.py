"""Hourly bars, from flat: the close above a rising Hull MA 180 with a positive volume oscillator (EMA 5 vs 10 of volume) and the QQE-mod bars turning green (smoothed RSI 6 above 53 and above its Bollinger band) goes long; the mirror goes short; a stop at the 7-bar swing low / high distance and a 1.5 x target; reversing state.
Port of FMZ strategy #436605 "Bitcoin Trading Strategy Based on Quantitative Indicators" (Strategy Crypto (maxencetajet)).

FMZ source id: 436605

Source
    https://www.fmz.com/strategy/436605 (PineScript v5, FMZ last modified 2023-12-26 11:06:12).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 167-356), Hull Hma, length 60 x 3 = 180; QQE RSI 6 / smoothing 5 / factor 3, BB 50 x 0.35; QQE2 factor 1.61, threshold 3; volume oscillator 5 / 10; swing 7 / 7; risk / reward 1.5; slippage 25
    longcondition = close > HULL and HULL > HULL[2] and osc > 0 and Greenbar1 and Greenbar2 and not Greenbar1[1] and not Greenbar2[1];  Greenbar1 = RsiMa2 - 50 > 3, Greenbar2 = RsiMa - 50 > upper(BB of FastAtrRsiTL - 50)
    position_size == 0 and long -> risk_long = (close - lowest(low, 7)) / close, entry long;  exit(stop = avg x (1 - risk), limit = avg x (1 + 1.5 risk));  short mirror

Interpretation choices (Pine rules in SURVEY_README.md)
    * The second QQE uses the same RSI 6 / smoothing 5, so RsiMa2 = RsiMa; only its threshold test (+-3)
      is used. The QQE trend line follows the script's band recursion. The volume oscillator compares two
      volume EMAs. The risk is measured at the signal close and applied to the average price, so the stop
      and target are fractions of the fill: risk and 1.5 x risk (sent from the bar after the fill in the
      script). Entries need a flat position; the stop / target state is followed in the signals. REVERSAL
      INTENDED. The fixed 0.5 qty and the slippage are sizing and costs. Stop module: portfolio_kwargs {}
      (driver D4). FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; swing-distance bracket from the fill.
    2 generic: PASS, Hull trend with QQE-mod and volume-oscillator confirmation.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: qty = 0.5 fixed, slippage 25, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) in the volume oscillator 100 x (ema(v, 5) - ema(v, 10)) / ema(v, 10); exchange volume to be compared later (Austin, 2026-10-23).
Session open: not used (the 2022-05-01 start dropped).
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_436605_hull180_qqe_mod_volume_osc_swing_bracket_reversal"
FAMILY = "qqe"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "hull_len": [180, 100],
    "rr": [1.5, 2.0],
}
DEFAULT_PARAMS = {"hull_len": 180, "rr": 1.5, "rsi_len": 6, "sf": 5, "qqe": 3.0, "bb_len": 50, "bb_mult": 0.35,
                  "thresh2": 3.0, "swing": 7, "vol_short": 5, "vol_long": 10}


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


def _ema(x, n):
    return x.ewm(span=n, adjust=False).mean()


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


def _qqe_tl(rs_ma, dar):
    """The script's QQE band recursion: FastAtrRsiTL."""
    r, d = rs_ma.to_numpy(dtype=float), dar.to_numpy(dtype=float)
    m = len(r)
    tl = np.full(m, np.nan)
    lb, sb = np.full(m, np.nan), np.full(m, np.nan)

    def cross(a, b, a1, b1):
        return (a > b and a1 <= b1) or (a < b and a1 >= b1)

    tr_p = 1
    for i in range(m):
        nsb, nlb = r[i] + d[i], r[i] - d[i]
        r1 = r[i - 1] if i else np.nan
        lb1 = lb[i - 1] if i else np.nan
        sb1 = sb[i - 1] if i else np.nan
        lb2 = lb[i - 2] if i > 1 else np.nan
        sb2 = sb[i - 2] if i > 1 else np.nan
        lb[i] = max(lb1, nlb) if (r1 > lb1 and r[i] > lb1) else nlb
        sb[i] = min(sb1, nsb) if (r1 < sb1 and r[i] < sb1) else nsb
        if cross(r[i], sb1, r1, sb2):              # ta.cross(RSIndex, shortband[1])
            t = 1
        elif cross(lb1, r[i], lb2, r1):            # ta.cross(longband[1], RSIndex)
            t = -1
        else:
            t = tr_p
        tl[i] = lb[i] if t == 1 else sb[i]
        tr_p = t
    return tl


def _signals(bars_df, p):
    h, lo, c, v = (bars_df[k] for k in ("high", "low", "close", "volume"))
    n = int(p["hull_len"])
    hull = _wma(2 * _wma(c, n // 2) - _wma(c, n), int(round(np.sqrt(n))))
    rs = _rsi(c, int(p["rsi_len"]))
    rs_ma = _ema(rs, int(p["sf"]))
    wp = int(p["rsi_len"]) * 2 - 1
    dar = _ema(_ema((rs_ma.shift(1) - rs_ma).abs(), wp), wp) * float(p["qqe"])
    tl = pd.Series(_qqe_tl(rs_ma, dar), index=c.index)
    nb = int(p["bb_len"])
    basis = (tl - 50).rolling(nb).mean()
    dev = float(p["bb_mult"]) * (tl - 50).rolling(nb).std(ddof=0)
    g1 = rs_ma - 50 > float(p["thresh2"])
    g2 = rs_ma - 50 > basis + dev
    r1 = rs_ma - 50 < -float(p["thresh2"])
    r2 = rs_ma - 50 < basis - dev
    es, el = _ema(v, int(p["vol_short"])), _ema(v, int(p["vol_long"]))
    osc = 100 * (es - el) / el.where(el != 0)
    h2 = hull.shift(2)
    long_c = (c > hull) & (hull > h2) & (osc > 0) & g1 & g2 & ~g1.shift(1, fill_value=False) & ~g2.shift(1, fill_value=False)
    short_c = (c < h2) & (hull < h2) & (osc > 0) & r1 & r2 & ~r1.shift(1, fill_value=False) & ~r2.shift(1, fill_value=False)
    sw = int(p["swing"])
    risk_l = (c - lo.rolling(sw).min()) / c
    risk_s = (h.rolling(sw).max() - c) / c
    return long_c.to_numpy(), short_c.to_numpy(), risk_l.to_numpy(), risk_s.to_numpy()


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    long_c, short_c, risk_l, risk_s = _signals(bars_df, p)
    ov, hv, lv = (bars_df[k].to_numpy(dtype=float) for k in ("open", "high", "low"))
    rr = float(p["rr"])
    m = len(ov)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, pend, avg, rk, fresh = 0, 0, np.nan, np.nan, False
    for i in range(m):
        fresh = False
        if pend != 0:
            pos, avg, pend, fresh = pend, ov[i], 0, True
        if pos == 1 and not fresh and (lv[i] <= avg * (1 - rk) or hv[i] >= avg * (1 + rr * rk)):
            pos = 0                                   # the bracket, sent from the bar after the fill
        elif pos == -1 and not fresh and (hv[i] >= avg * (1 + rk) or lv[i] <= avg * (1 - rr * rk)):
            pos = 0
        if pos == 0 and pend == 0 and i + 1 < m:
            if long_c[i]:
                le[i], pend, rk = True, 1, risk_l[i]
            elif short_c[i]:
                se[i], pend, rk = True, -1, risk_s[i]
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, pd.Series(se, index=ix), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    long_c, short_c, risk_l, risk_s = _signals(bars_df, p)
    le, lx, se, sx = simulate(bars_df, **params)
    rl = pd.Series(risk_l, index=bars_df.index).shift(1)
    rs_ = pd.Series(risk_s, index=bars_df.index).shift(1)
    short_fill = se.shift(1, fill_value=False)
    rk = rs_.where(short_fill, rl)                    # the risk measured at the signal close
    return {"sl_stop": rk.where(rk > 0), "tp_stop": (float(p["rr"]) * rk).where(rk > 0)}


def portfolio_kwargs(**params):
    return {}
