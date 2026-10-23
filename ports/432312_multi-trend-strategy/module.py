"""One-minute bars: the RSI 13 of the session VWAP rising under 20 with the RSI 13 of a linear regression 100 of hlc3 rising goes long, closed on the VWAP RSI crossing over 99.8; a peak of the RSI 23 of a VWMA 23 of a linear regression 23 above 95 goes short, closed when that RSI turns up; every position closes from 15:16 to 15:59 UTC; a 0.3 % (long) or 0.95 % (short) target; reversing.
Port of FMZ strategy #432312 "Multi Trend Strategy" (VWAP Candles Strategy (RolandoSantos)).

FMZ source id: 432312

Source
    https://www.fmz.com/strategy/432312 (PineScript v4, FMZ last modified 2023-11-16 11:20:10).
    Verbatim copy: original_source.md. Read 2026-10-23 (FMZ-C).

Original signal (original_source.md lines 209-516), RSI 13 of vwap(hlc3); RSI 13 of linreg(hlc3, 100); RSI 23 of vwma(linreg(close, 23), 23); TP long 0.3 %, short 0.95 %, qty 100 %; close_all hour 15, minute > 15
    long = vwaprsi > vwaprsi[1] and rsi > rsi[1] and vwaprsi < 20;  close_long = crossover(vwaprsi, 99.8);  short = rsiv > 95 and rsiv < rsiv[1] and rsiv[2] < rsiv[1];  close_short = rsiv > rsiv[1] and rsiv[2] > rsiv[1]
    long -> entry Long;  short -> entry Short;  close_long / close_short -> close;  hour(time) == 15 and minute(time) > 15 -> close_all;  position_size > 0 -> exit(qty_percent 100, limit = avg x 1.003), short limit avg x 0.9905

Interpretation choices (Pine rules in SURVEY_README.md)
    * Only the uncommented conditions trade; the Copp curve, QQE, LSMA, ADX, squeeze, coral trend and VWAP
      candles feed no order. vwap(hlc3) is the session VWAP, anchored at the broker-day start (as earlier
      ports). The close_all hour is read in the header exchange's time, UTC (as earlier ports): bars opening
      15:16 to 15:59 UTC. When both entries fire on one bar the later call (short) is taken; a close acts
      only on a position the bar's entries leave unchanged (call order). The targets are full exits
      (qty_percent 100) from the fill, longs 0.3 %, shorts 0.95 %; the script places them from the bar
      after the fill (position_size updates at that bar's close), the port from the fill minute (weird
      case, one minute). REVERSAL INTENDED. The 10000 cash size is sizing. Stop module: portfolio_kwargs {}
      (driver D4). FREQ = "1min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; side-specific percent targets from the fill.
    2 generic: PASS, VWAP RSI dips and regression RSI peaks with a daily cut-off.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: strategy(): cash 10000 per trade, capital 10000, not ported.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: used: the bars' volume column (broker tick volume of the cTrader M1 data, summed per bar) in the session VWAP of hlc3 (long side) and vwma(linreg(close, 23), 23) (short side); exchange volume to be compared later (Austin, 2026-10-23).
Session open: close_all on bars opening 15:16 to 15:59 UTC (header exchange time); VWAP anchored at the broker-day start.
REVERSAL INTENDED.

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_432312_vwap_rsi_dip_linreg_rsi_peak_1m_pct_target_reversal"
FAMILY = "rsi_threshold"  # proposed 2026-10-23 (FMZ-C), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "long_tp": [0.003, 0.006],
    "short_tp": [0.0095, 0.005],
}
DEFAULT_PARAMS = {"long_tp": 0.003, "short_tp": 0.0095, "rsi_len": 13, "lin_len": 100, "rsiv_len": 23}


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


def broker_day(index):
    """Broker day of each timestamp: the session ending 17:00 America/New_York, labelled by its
    end date (as worker A's ports). The desktop binds this name to registry_schema.broker_day."""
    ny = index.tz_convert("America/New_York")
    return (ny + pd.Timedelta(hours=7)).normalize().tz_localize(None)


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


def _linreg(x, n):
    """Pine linreg(x, n, 0): the least-squares line's value at the newest bar."""
    t = np.arange(n, dtype=float)
    tb = t.mean()
    w = 1.0 / n + (t - tb) * (n - 1 - tb) / ((t - tb) ** 2).sum()
    v = x.to_numpy(dtype=float)
    out = np.full(len(v), np.nan)
    if len(v) >= n:
        out[n - 1:] = np.lib.stride_tricks.sliding_window_view(v, n) @ w
    return pd.Series(out, index=x.index)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    h, lo, c, v = (bars_df[k] for k in ("high", "low", "close", "volume"))
    hlc3 = (h + lo + c) / 3
    day = broker_day(c.index)
    cv = v.groupby(day).cumsum()
    vwap = (hlc3 * v).groupby(day).cumsum() / cv.where(cv != 0)
    k = int(p["rsi_len"])
    vr = _rsi(vwap, k)
    r = _rsi(_linreg(hlc3, int(p["lin_len"])), k)
    nv = int(p["rsiv_len"])
    lr = _linreg(c, nv)
    vs = v.rolling(nv).sum()
    rv = _rsi((lr * v).rolling(nv).sum() / vs.where(vs != 0), nv)
    rv1, rv2 = rv.shift(1), rv.shift(2)
    long_c = ((vr > vr.shift(1)) & (r > r.shift(1)) & (vr < 20)).to_numpy()
    close_l = ((vr > 99.8) & (vr.shift(1) <= 99.8)).to_numpy()
    short_c = ((rv > 95) & (rv < rv1) & (rv2 < rv1)).to_numpy()
    close_s = ((rv > rv1) & (rv2 > rv1)).to_numpy()
    win = np.asarray((c.index.hour == 15) & (c.index.minute > 15))
    m = len(long_c)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos = 0
    for i in range(m):
        tgt = -1 if short_c[i] else (1 if long_c[i] else 0)
        if tgt != 0 and tgt != pos:
            if tgt == 1:
                le[i] = True
            else:
                se[i] = True
            pos = tgt
        elif pos == 1 and (close_l[i] or win[i]):
            lx[i], pos = True, 0
        elif pos == -1 and (close_s[i] or win[i]):
            sx[i], pos = True, 0
    ix = bars_df.index
    return (pd.Series(le, index=ix), pd.Series(lx, index=ix),
            pd.Series(se, index=ix), pd.Series(sx, index=ix))


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    le, lx, se, sx = simulate(bars_df, **params)
    short_fill = se.shift(1, fill_value=False).to_numpy()   # the entry fills on the bar after its signal
    tp = np.where(short_fill, float(p["short_tp"]), float(p["long_tp"]))
    return {"tp_stop": pd.Series(tp, index=bars_df.index)}


def portfolio_kwargs(**params):
    return {}
