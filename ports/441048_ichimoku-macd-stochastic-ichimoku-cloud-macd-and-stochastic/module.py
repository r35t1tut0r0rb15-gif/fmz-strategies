"""Ichimoku cloud, MACD, stochastic and SMA 100 confluence with an ATR bracket, 4-hour bars: the stochastic K (5, 3) crossing over 20 with MACD above zero and the close above the SMA 100 and both cloud
lines goes long, the mirror (K under 80) short; a 1 ATR(8) stop and a 1 ATR target from the entry; reversing.
Port of FMZ strategy #441048 "基于Ichimoku云图MACD和Stochastic的多时间框架趋势跟踪策略Ichimoku-Cloud-MACD-and-Stochastic-Based-Multi-Timeframe-Trend-Tracking-Strategy" (FXFUNDINGMATE TREND INDICATOR).

FMZ source id: 441048

Source
    https://www.fmz.com/strategy/441048 (PineScript v4, FMZ last modified 2024-02-05 10:30:45).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 167-269), Ichimoku 9 / 26 / 52, displacement 26; MACD 12 / 26 / 9 (EMAs); stochastic 5 / 3 / 3; ATR 8 (RMA), stop x 1, target x 1; SMA 100; both sides; date window 2020-2025
    leadLine1 = avg(conversion, base)[25], leadLine2 = donchian(52)[25];  longCond = crossover(k, 20) and macd > 0 and close > sma100 and close > leadLine1 and close > leadLine2;  shortCond mirrored with crossunder(k, 80)
    entry_price = position_avg_price (na on the flat signal bar), entry_atr = valuewhen(long or short, atr, 0);  every bar: strategy.exit(limit = entry_price +- 1 entry_atr, stop = entry_price -+ 1 entry_atr)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is fill +- 1 ATR(8) of the signal bar: sl_stop = tp_stop = ATR / close of the signal
      bar, shifted one bar inside stops() and re-based on the fill. The script's exit has na levels on the
      flat signal bar, so its bracket is first placed at the fill bar's close; the port's bracket is active
      from the fill bar (as #440797). A later signal while held moves the script's levels, which the port
      does not follow. The date window and the close_all after its end are dropped. strategy.entry
      reverses: REVERSAL INTENDED. Stop module: portfolio_kwargs {} (driver D4). Stops on 4-hour bars: mark
      coarse_bar_stop. No sizing code. FREQ = "4h" from the backtest header (bars on UTC multiples of 4
      hours).

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry from signal-bar data.
    2 generic: PASS, cloud, MACD, stochastic and SMA filters with ATR bracket.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
REVERSAL INTENDED.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_441048_ichimoku_macd_stoch_atr_bracket"
FAMILY = "ichimoku"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "4h"  # backtest header period: 4h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "sl_mult": [1.0, 2.0],
    "tp_mult": [1.0, 2.0],
}
DEFAULT_PARAMS = {"sl_mult": 1.0, "tp_mult": 1.0, "conv": 9, "base": 26, "span2": 52, "displacement": 26,
                  "fast": 12, "slow": 26, "signal": 9, "k_len": 5, "k_smooth": 3, "atr_len": 8, "sma_len": 100}


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


def _fractions(bars_df, p):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    a = _rma(tr, int(p["atr_len"])) / c
    return float(p["sl_mult"]) * a, float(p["tp_mult"]) * a


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]

    def don(n):
        return (lo.rolling(n).min() + h.rolling(n).max()) / 2

    d = int(p["displacement"]) - 1
    lead1 = ((don(int(p["conv"])) + don(int(p["base"]))) / 2).shift(d)
    lead2 = don(int(p["span2"])).shift(d)
    macd = c.ewm(span=int(p["fast"]), adjust=False).mean() - c.ewm(span=int(p["slow"]), adjust=False).mean()
    n = int(p["k_len"])
    ll, hh = lo.rolling(n).min(), h.rolling(n).max()
    with np.errstate(divide="ignore", invalid="ignore"):
        st = 100.0 * (c - ll) / (hh - ll).where(hh > ll)
    k = st.rolling(int(p["k_smooth"])).mean()
    sma = c.rolling(int(p["sma_len"])).mean()
    lsig = ((k > 20) & (k.shift(1) <= 20) & (macd > 0) & (c > sma) & (c > lead1) & (c > lead2)).to_numpy()
    ssig = ((k < 80) & (k.shift(1) >= 80) & (macd < 0) & (c < sma) & (c < lead1) & (c < lead2)).to_numpy()
    sl_s, tp_s = _fractions(bars_df, p)
    sl, tp = sl_s.to_numpy(), tp_s.to_numpy()
    ov = bars_df["open"].to_numpy(dtype=float)
    hv, lv = h.to_numpy(dtype=float), lo.to_numpy(dtype=float)
    m = len(ov)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, entry_i, s_, t_ = 0, -1, np.nan, np.nan
    for i in range(m):
        if pos != 0 and i >= entry_i:
            x = ov[entry_i]
            if pos == 1 and (lv[i] <= x * (1 - s_) or hv[i] >= x * (1 + t_)):
                pos = 0
            elif pos == -1 and (hv[i] >= x * (1 + s_) or lv[i] <= x * (1 - t_)):
                pos = 0
        if i + 1 < m and not np.isnan(sl[i]):
            if lsig[i] and pos != 1:
                le[i], pos, entry_i, s_, t_ = True, 1, i + 1, sl[i], tp[i]
            elif ssig[i] and pos != -1:
                se[i], pos, entry_i, s_, t_ = True, -1, i + 1, sl[i], tp[i]
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, pd.Series(se, index=ix), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    sl, tp = _fractions(bars_df, p)
    return {"sl_stop": sl.shift(1), "tp_stop": tp.shift(1)}


def portfolio_kwargs(**params):
    return {}
