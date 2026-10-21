"""Uptrend MACD pullback buys with an ATR structure bracket, 1-hour bars, long only: with the close above the 1-hour EMA 70 of hl2 and that EMA under the 15-minute EMA 68, a DEMA-MACD crossing under its signal
while the slow stochastic is under 30 buys from flat; the stop sits 4.3 ATR 9 under the 18-bar low, the target 5.5 ATR 24 over the 12-bar high.
Port of FMZ strategy #437507 "基于多时框架移动平均线和MACD-的长空开仓策略Long-and-Short-Opening-Strategy-Based-on-Multi-Timeframe-Moving-Average-and-MACD" (LONG).

FMZ source id: 437507

Source
    https://www.fmz.com/strategy/437507 (PineScript v4, FMZ last modified 2024-01-03 12:15:46).
    Verbatim copy: original_source.md. Read 2026-10-21 (FMZ-C).

Original signal (original_source.md lines 205-428), MTF EMA 60 / 70 and 15 / 68 of hl2; MACD (DEMA) 13 / 18 / 24, limit 180; stochastic 10 / 1 / 3 under 30; ATR stop 18-bar low - 4.3 ATR 9; ATR target 12-bar high + 5.5 ATR 24; date window true
    uptrend = close > mtf1 and mtf1 < mtf2;  LongBuy = uptrend and stoch d < 30 and crossunder(macd, signal) and signal < 180 and macd < 180
    GOLONG = LongBuy and FLAT -> entry, exit(limit = highest(high, 12) + 5.5 atr(24), stop = lowest(low, 18) - 4.3 atr(9));  the % stop / % target / MTF-cross exits are off or can never fire

Interpretation choices (Pine rules in SURVEY_README.md)
    * The 60-minute request is the 1-hour chart itself; the 15-minute EMA 68 is a lower time frame read as
      the hour's LAST 15-minute bar (as #436765), built from 15-minute bars of hl2. Criterion 2: the MACD
      limit 180 is in price units; the port tests macd / close and signal / close against a fraction
      (0.0043 reads 180 on BTC near 42000; 1.0 switches it off). The bracket is placed once, at the signal
      bar, from that bar's levels: distances from the signal close (sl_stop / tp_stop), shifted one bar
      inside stops() and re-based on the fill. The percent target is avg x (-1 + 5.3 %), a negative price
      that no close can cross under: dead code, as the off switches. "Flat" follows the house bracket. Long
      only (opposite entries cannot occur). Stop module: portfolio_kwargs {} (driver D4). The 100 % of
      equity size, commission and slippage are sizing. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry.
    2 generic: ADAPT, price-unit MACD limit -> fraction of the close; ATR structure bracket.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent-of-equity size, commission, slippage and the exit inputs stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Long only.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_437507_mtf_ema_macd_pullback_long"
FAMILY = "trend_confluence"  # proposed 2026-10-21 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "macd_limit_frac": [0.0043, 1.0],
    "stop_mult": [4.3, 3.0],
}
DEFAULT_PARAMS = {"macd_limit_frac": 0.0043, "stop_mult": 4.3, "len1": 70, "len2": 68, "ltf_minutes": 15,
                  "fast": 13, "slow": 18, "signal": 24, "k_len": 10, "k_smooth": 3, "stoch_limit": 30.0,
                  "stop_lookback": 18, "stop_atr": 9, "tp_lookback": 12, "tp_atr": 24, "tp_mult": 5.5}


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


def precompute(raw_1m_df, symbol_key, **params):
    p = {**DEFAULT_PARAMS, **params}
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    if ohlc.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    bars = ohlc.resample(FREQ, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"}).dropna(how="all")
    b15 = ohlc.resample(f"{int(p['ltf_minutes'])}min", label="left", closed="left").agg(
        {"high": "max", "low": "min"}).dropna(how="all")
    e15 = ((b15["high"] + b15["low"]) / 2).ewm(span=int(p["len2"]), adjust=False).mean()
    hour = e15.index.floor(FREQ)
    last = e15[~pd.Index(hour).duplicated(keep="last")]   # the hour's last 15-minute bar
    last.index = hour[~pd.Index(hour).duplicated(keep="last")]
    bars["mtf2"] = last.reindex(bars.index)
    return bars


def _dema(x, n):
    e = x.ewm(span=n, adjust=False).mean()
    return 2 * e - e.ewm(span=n, adjust=False).mean()


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    return _rma(tr, int(n))


def _setup(bars_df, p):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    src = (h + lo) / 2
    mtf1 = src.ewm(span=int(p["len1"]), adjust=False).mean()
    mtf2 = bars_df["mtf2"]
    uptrend = (c > mtf1) & (mtf1 < mtf2)
    macd = _dema(c, int(p["fast"])) - _dema(c, int(p["slow"]))
    sig = _dema(macd, int(p["signal"]))
    xdn = (macd < sig) & (macd.shift(1) >= sig.shift(1))
    lim = float(p["macd_limit_frac"])
    n = int(p["k_len"])
    ll, hh = lo.rolling(n).min(), h.rolling(n).max()
    with np.errstate(divide="ignore", invalid="ignore"):
        st = 100.0 * (c - ll) / (hh - ll).where(hh > ll)
    d = st.rolling(int(p["k_smooth"])).mean()
    buy = uptrend & (d < float(p["stoch_limit"])) & xdn & (sig / c < lim) & (macd / c < lim)
    stop_lv = lo.rolling(int(p["stop_lookback"])).min() - _atr(bars_df, p["stop_atr"]) * float(p["stop_mult"])
    tp_lv = h.rolling(int(p["tp_lookback"])).max() + _atr(bars_df, p["tp_atr"]) * float(p["tp_mult"])
    sl = ((c - stop_lv) / c).where(buy)
    tp = ((tp_lv - c) / c).where(buy)
    return buy, sl.where(sl > 0), tp.where(tp > 0)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    buy, sl, tp = _setup(bars_df, p)
    ov, hv, lv = (bars_df[k].to_numpy(dtype=float) for k in ("open", "high", "low"))
    bv, slv, tpv = buy.to_numpy(), sl.to_numpy(), tp.to_numpy()
    m = len(ov)
    le = np.zeros(m, dtype=bool)
    pos, entry_i, f_sl, f_tp = 0, -1, np.nan, np.nan
    for i in range(m):
        if pos == 1 and i >= entry_i:                    # house bracket from the fill price
            e = ov[entry_i]
            if lv[i] <= e * (1 - f_sl) or hv[i] >= e * (1 + f_tp):
                pos = 0
        if pos == 0 and bv[i] and i + 1 < m and not np.isnan(slv[i]) and not np.isnan(tpv[i]):
            le[i] = True
            pos, entry_i, f_sl, f_tp = 1, i + 1, slv[i], tpv[i]
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, false.copy(), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    _, sl, tp = _setup(bars_df, p)
    return {"sl_stop": sl.shift(1), "tp_stop": tp.shift(1)}


def portfolio_kwargs(**params):
    return {}
