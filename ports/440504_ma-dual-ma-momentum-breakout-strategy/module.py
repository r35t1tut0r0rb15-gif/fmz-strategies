"""Converging MA with a QQE threshold, 1-hour bars: the EMA 5 of the RSI 14 first rising above 60 with the fast line above the converging MA goes long, first falling below 40 with it below goes short;
the smoothed RSI above 60 closes shorts, below 40 closes longs; a stop 0.3 ATR(14) beyond the signal bar's low / high.
Port of FMZ strategy #440504 "双MA动量突破策略Dual-MA-Momentum-Breakout-Strategy" (MAConverging + QQE Threshold Strategy).

FMZ source id: 440504

Source
    https://www.fmz.com/strategy/440504 (PineScript v5, FMZ last modified 2024-01-31 10:33:21).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 118-388), converging MA length 100, increment 10, fast 10; RSI 14, smoothing 5 (EMA), threshold 10; ATR 14 (RMA) x 0.3 on high / low
    alpha := cross(close, ma) ? 2 / 101 : close > ma and new 100-bar high ? alpha + 0.1 : close < ma and new low ? alpha + 0.1 : alpha;  ma := ma[1] + alpha[1] (close - ma[1]) (seeded by sma 100);  fma follows the close
    prebuy = ema(rsi, 5) - 50 > 10;  buy = prebuy and not prebuy[1] and fma > ma;  prebuy -> close Short;  buy and position <= 0 -> entry Long, long_sl = low - 0.3 atr;  strategy.exit(stop = long_sl);  shorts mirrored

Interpretation choices (Pine rules in SURVEY_README.md)
    * The cross test uses the converging MA before this bar's update, as written; the step can grow past
      1 between crosses, as written. The stop is set on the signal bar: sl_stop = (close - (low - 0.3
      ATR)) / close of the signal bar (shorts from the high), shifted one bar inside stops() and re-based
      on the fill. The QQE bands, crosses and plots do not feed the orders. A close acts only on the held
      position; an opposite entry after it stands. strategy.entry reverses: REVERSAL INTENDED. Stop
      module: portfolio_kwargs {} (driver D4). No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; stop fixed at entry.
    2 generic: PASS, adaptive average and smoothed RSI threshold.
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

NAME = "fmz_440504_converging_ma_qqe_threshold"
FAMILY = "multi_indicator_confluence"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "thresh": [10, 20],
    "atr_mult": [0.3, 1.0],
}
DEFAULT_PARAMS = {"thresh": 10, "atr_mult": 0.3, "length": 100, "incr": 10, "fast": 10, "rsi_len": 14,
                  "sf": 5, "atr_len": 14}


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


def _rsi(c, n):
    d = c.diff()
    up = _rma(d.clip(lower=0), n)
    dn = _rma((-d).clip(lower=0), n)
    with np.errstate(divide="ignore", invalid="ignore"):
        r = 100.0 - 100.0 / (1.0 + up / dn)
    r = r.where(up != 0, 0.0).where(dn != 0, 100.0)    # Pine: down == 0 -> 100, else up == 0 -> 0
    return r.where(up.notna() & dn.notna())


def _converging(bars_df, p):
    c = bars_df["close"]
    n = int(p["length"])
    upv = bars_df["high"].rolling(n).max().to_numpy()
    lwv = bars_df["low"].rolling(n).min().to_numpy()
    init = c.rolling(n).mean().to_numpy()
    cv = c.to_numpy(dtype=float)
    k, fast = 1.0 / float(p["incr"]), float(p["fast"])
    m = len(cv)
    ma_o, fma_o = np.full(m, np.nan), np.full(m, np.nan)
    ma, alpha = 0.0, 0.0                                  # var initial values
    fma = np.nan                                          # fma[1] is na on the first bar
    ma_hist = [np.nan]                                    # ma as passed to cross() on the previous bar
    alpha_p = np.nan
    ma_p = np.nan
    for i in range(m):
        ma_cur = ma                                       # ma before this bar's update
        a0, a1 = ma_cur, ma_hist[-1]
        cross = (i > 0 and ((cv[i] > a0 and cv[i - 1] <= a1) or (cv[i] < a0 and cv[i - 1] >= a1)))
        if cross:
            alpha = 2 / (n + 1)
        elif cv[i] > ma_cur and i > 0 and upv[i] > upv[i - 1]:
            alpha = alpha + k
        elif cv[i] < ma_cur and i > 0 and lwv[i] < lwv[i - 1]:
            alpha = alpha + k
        ma_hist.append(ma_cur)
        cand = ma_p + alpha_p * (cv[i] - ma_p)
        ma = init[i] if np.isnan(cand) else cand
        if cross:
            f = (cv[i] + fma) / 2
        elif cv[i] > ma:
            f = max(cv[i], fma) + (cv[i] - fma) / fast
        else:
            f = min(cv[i], fma) + (cv[i] - fma) / fast
        fma = cv[i] if np.isnan(f) else f
        ma_o[i], fma_o[i] = ma, fma
        ma_p, alpha_p = ma, alpha
    return pd.Series(ma_o, index=c.index), pd.Series(fma_o, index=c.index)


def _setup(bars_df, p):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    ma, fma = _converging(bars_df, p)
    rm = _rsi(c, int(p["rsi_len"])).ewm(span=int(p["sf"]), adjust=False).mean()
    t = float(p["thresh"])
    prebuy = (rm - 50) > t
    presell = (rm - 50) < -t
    buy = prebuy & ~prebuy.shift(1, fill_value=False) & (fma > ma)
    sell = presell & ~presell.shift(1, fill_value=False) & (fma < ma)
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    a = _rma(tr, int(p["atr_len"])) * float(p["atr_mult"])
    sl = ((c - (lo - a)) / c).where(buy, ((h + a - c) / c).where(sell))
    return prebuy.to_numpy(), presell.to_numpy(), buy.to_numpy(), sell.to_numpy(), sl


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    prebuy, presell, buy, sell, sl_s = _setup(bars_df, p)
    sl = sl_s.to_numpy()
    ov = bars_df["open"].to_numpy(dtype=float)
    hv, lv = bars_df["high"].to_numpy(dtype=float), bars_df["low"].to_numpy(dtype=float)
    m = len(ov)
    le, lx, se, sx = (np.zeros(m, dtype=bool) for _ in range(4))
    pos, entry_i, s_ = 0, -1, np.nan
    for i in range(m):
        if pos != 0 and i >= entry_i:
            x = ov[entry_i]
            if pos == 1 and lv[i] <= x * (1 - s_):
                pos = 0
            elif pos == -1 and hv[i] >= x * (1 + s_):
                pos = 0
        held = pos
        new = pos
        if prebuy[i] and held == -1:
            new = 0
        if buy[i] and held <= 0 and i + 1 < m and not np.isnan(sl[i]):
            new, entry_i, s_ = 1, i + 1, sl[i]
        if presell[i] and held == 1 and new == 1:
            new = 0
        if sell[i] and held >= 0 and i + 1 < m and not np.isnan(sl[i]):
            new, entry_i, s_ = -1, i + 1, sl[i]
        if new == 1 and held != 1:
            le[i] = True
        elif new == -1 and held != -1:
            se[i] = True
        elif new == 0 and held == 1:
            lx[i] = True
        elif new == 0 and held == -1:
            sx[i] = True
        pos = new
    ix = bars_df.index
    return tuple(pd.Series(a, index=ix) for a in (le, lx, se, sx))


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": _setup(bars_df, p)[4].shift(1)}


def portfolio_kwargs(**params):
    return {}
