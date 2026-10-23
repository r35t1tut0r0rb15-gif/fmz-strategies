"""Hourly bars: the EMA 20 crossing over the EMA 50 with the script's ADX 14 over 15, RSI 14 over 45 and the close above the session VWAP goes long, the mirror short; a stop 1.5 ATR 14 beyond each bar's close, re-sent every bar, is followed in the signals; reversing.
Port of FMZ strategy #488862 "多指标融合期权销售策略趋势确认与ATR动态止损优化Multi-Indicator-Fusion-Options-Selling-Strategy-Trend-Confirmation-with-ATR-Dynamic-Stop-Loss-Optimization" (Improved Option Selling Strategy).

FMZ source id: 488862

Source
    https://www.fmz.com/strategy/488862 (PineScript v5, FMZ last modified 2025-03-31 13:10:34).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 179-225), EMA 20 / 50; manual ADX 14 (RMA of high - low as the range); RSI 14 (45 / 55); session VWAP; ATR 14 x 1.5
    buyCondition = crossover(ema20, ema50) and adx > 15 and rsi > 45 and close > vwap -> entry BullPutSpread;  sellCondition mirrored (rsi < 55, close < vwap) -> entry BearCallSpread
    every bar: exit("BullPutSpreadExit", from_entry = "BullPutSpread", stop = close - 1.5 atr);  exit("BearCallSpreadExit", ..., stop = close + 1.5 atr)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The script's ADX divides the RMA of the directional moves by the RMA of high - low (not the true
      range). The stops are re-sent every bar from that bar's close (including the signal bar, for the
      pending entry), so they move both ways; the signals follow them: a bar that reaches the previous
      bar's level closes the trade at the next open (mark trailing_stop_pending). ta.vwap(close)
      restarts each session: the house session is the broker day (17:00 America/New_York). The option
      names are labels only. REVERSAL INTENDED. No sizing code. FREQ = "1h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; per-bar re-sent stop followed in the signals.
    2 generic: PASS, EMA crossings with ADX, RSI and VWAP filters.
    3 crypto-exchange-only: no (exchange pair in the header only (option spreads named in the ids)).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) as the session-VWAP weights; exchange volume to be compared later (Austin, 2026-10-23).
Session open: broker day (17:00 America/New_York, DST by the zone) for the VWAP reset; no venue-open rule.
REVERSAL INTENDED.

Marks: trailing_stop_pending
"""
import numpy as np
import pandas as pd

NAME = "fmz_488862_ema20_50_cross_adx_rsi_vwap_rolling_atr_stop_1h_reversal"
FAMILY = "ma_cross"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1h"  # backtest header period: 1h
PERIODS_PER_YEAR_OVERRIDE = None

GRID = {
    "atr_mult": [1.5, 2.5],
    "adx_min": [15.0, 25.0],
}
DEFAULT_PARAMS = {"atr_mult": 1.5, "adx_min": 15.0}


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


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


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c, v = bars_df["high"], bars_df["low"], bars_df["close"], bars_df["volume"]
    e20, e50 = c.ewm(span=20, adjust=False).mean(), c.ewm(span=50, adjust=False).mean()
    day = broker_day(bars_df.index)
    vw = (c * v).groupby(day).cumsum() / v.groupby(day).cumsum()
    r = _rsi(c, 14)
    pc = c.shift(1)
    atr = _rma(pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1), 14)
    up, dn = h.diff(), -lo.diff()
    pdm = up.where((up > dn) & (up > 0), 0.0).where(up.notna())
    mdm = dn.where((dn > up) & (dn > 0), 0.0).where(dn.notna())
    rr = _rma(h - lo, 14)
    pdi, mdi = 100 * _rma(pdm, 14) / rr, 100 * _rma(mdm, 14) / rr
    adx = _rma(100 * (pdi - mdi).abs() / (pdi + mdi), 14)
    strong = adx > float(p["adx_min"])
    buy = ((e20 > e50) & (e20.shift(1) <= e50.shift(1)) & strong & (r > 45) & (c > vw)).to_numpy()
    sell = ((e20 < e50) & (e20.shift(1) >= e50.shift(1)) & strong & (r < 55) & (c < vw)).to_numpy()
    d = float(p["atr_mult"]) * atr
    l_st, s_st = (c - d).to_numpy(dtype=float), (c + d).to_numpy(dtype=float)
    hn, ln = h.to_numpy(dtype=float), lo.to_numpy(dtype=float)
    m = len(buy)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    vpos, pine = 0, 0
    for i in range(m):
        held = pine
        if i > 0 and held == 1 and ln[i] <= l_st[i - 1]:
            held = 0                       # the stop sent at the previous close is touched
        elif i > 0 and held == -1 and hn[i] >= s_st[i - 1]:
            held = 0
        new = held
        if buy[i]:
            new = 1
        if sell[i]:
            new = -1
        pine = new
        if new != vpos and i + 1 < m:
            if new == 1:
                le[i] = True
            elif new == -1:
                se[i] = True
            elif vpos == 1:
                lx[i] = True
            else:
                sx[i] = True
            vpos = new
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def portfolio_kwargs(**params):
    return {}
