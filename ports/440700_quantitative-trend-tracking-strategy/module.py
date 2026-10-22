"""Band dips in trend, 5-hour bars, long only, 09:30-15:00 UTC: a low under the lower Bollinger band (3, 4.989 on highs) with RSI 16 above 39.2, ADX above 14, the close above the next Heikin-Ashi
open and the MACD (on highs) above its signal goes long, with a stop and target from the signal bar; outside the session everything closes.
Port of FMZ strategy #440700 "Quantitative Trend Tracking Strategy" (Bollinger Band + RSI + ADX + MACD).

FMZ source id: 440700

Source
    https://www.fmz.com/strategy/440700 (PineScript v4, FMZ last modified 2024-02-01 11:42:22).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 165-284), session 0930-1500; BB on high 3 / 4.989; RSI 16 > 39.2; ADX 14 > 14; MACD on high 12 / 20 / SMA 15
    long = low < lower and rsi > 39.2 and adx > 14 and close > (haOpen + haClose) / 2 and in session and macd > signal -> entry
    stop = (close - max(low x 0.9978, close x 0.9968)) / mintick;  target = (max(upper, close x 1.0075) - close) / mintick;  strategy.exit(profit = target, loss = stop);  not in session -> close_all

Interpretation choices (Pine rules in SURVEY_README.md)
    * The session is read on the UTC bar open (5-hour bars counted from the data's first day). The
      Heikin-Ashi values come from the chart's own bars. The ADX is the script's own Wilder sums with
      nz() starts and an SMA of DX. The bracket distances are in ticks from the entry, re-sized every bar
      from that bar's close, low and band; the port fixes them at the signal bar as fractions of its
      close, shifted one bar inside stops() and re-based on the fill (the later re-sizing is not
      followed). Long only. Stop module: portfolio_kwargs {} (driver D4). Stops on 5-hour bars: mark
      coarse_bar_stop. No sizing code. FREQ = "5h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry from signal-bar data.
    2 generic: PASS, Bollinger dip, RSI, ADX, Heikin-Ashi and MACD.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: no sizing code.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: entries on bars opening 09:30-15:00 UTC; close_all on the other bars (bar open time).
Long only.

Marks: coarse_bar_stop
"""
import numpy as np
import pandas as pd

NAME = "fmz_440700_bb_rsi_adx_macd_session_long"
FAMILY = "multi_indicator_confluence"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "5h"  # backtest header period: 5h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "mult": [4.989, 3.0],
    "rsi_comp": [39.2, 50.0],
}
DEFAULT_PARAMS = {"mult": 4.989, "rsi_comp": 39.2, "bb_len": 3, "rsi_len": 16, "adx_len": 14, "adx_comp": 14,
                  "fast": 12, "slow": 20, "signal": 15, "sess_start_min": 570, "sess_end_min": 900}


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


def _adx(bars_df, n):
    """The script's ADX: Wilder running sums with nz() starts, then an SMA of DX."""
    h, lo, c = (bars_df[k].to_numpy(dtype=float) for k in ("high", "low", "close"))
    m = len(c)
    dx = np.full(m, np.nan)
    s_tr = s_p = s_m = 0.0
    for i in range(m):
        pc = c[i - 1] if i > 0 else 0.0
        ph = h[i - 1] if i > 0 else 0.0
        pl = lo[i - 1] if i > 0 else 0.0
        tr = max(max(h[i] - lo[i], abs(h[i] - pc)), abs(lo[i] - pc))
        dmp = max(h[i] - ph, 0.0) if (h[i] - ph) > (pl - lo[i]) else 0.0
        dmm = max(pl - lo[i], 0.0) if (pl - lo[i]) > (h[i] - ph) else 0.0
        s_tr = s_tr - s_tr / n + tr
        s_p = s_p - s_p / n + dmp
        s_m = s_m - s_m / n + dmm
        if s_tr > 0:
            dip, dim = s_p / s_tr * 100, s_m / s_tr * 100
            if dip + dim > 0:
                dx[i] = abs(dip - dim) / (dip + dim) * 100
    return pd.Series(dx, index=bars_df.index).rolling(n).mean()


def _setup(bars_df, p):
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    n = int(p["bb_len"])
    basis = h.rolling(n).mean()
    dev = float(p["mult"]) * h.rolling(n).std(ddof=0)
    upper, lower = basis + dev, basis - dev
    r = _rsi(c, int(p["rsi_len"]))
    adx = _adx(bars_df, int(p["adx_len"]))
    hac = (o + h + lo + c) / 4
    hao_v = np.full(len(c), np.nan)
    ov, hcv = o.to_numpy(dtype=float), hac.to_numpy(dtype=float)
    for i in range(len(c)):
        hao_v[i] = (ov[i] + c.iloc[i]) / 2 if i == 0 else (hao_v[i - 1] + hcv[i - 1]) / 2
    nxt = (pd.Series(hao_v, index=c.index) + hac) / 2
    macd = h.ewm(span=int(p["fast"]), adjust=False).mean() - h.ewm(span=int(p["slow"]), adjust=False).mean()
    sig = macd.rolling(int(p["signal"])).mean()
    ix = bars_df.index.tz_convert("UTC")
    mins = ix.hour * 60 + ix.minute
    sess = pd.Series((mins >= int(p["sess_start_min"])) & (mins < int(p["sess_end_min"])), index=c.index)
    lsig = (lo < lower) & (r > float(p["rsi_comp"])) & (adx > float(p["adx_comp"])) & (c > nxt) & sess & (macd > sig)
    sl = (c - np.maximum(lo * (1 - 0.0022), c * (1 - 0.0032))) / c
    tp = (np.maximum(upper, c * 1.0075) - c) / c
    ok = lsig & (sl > 0) & (tp > 0)
    return ok.to_numpy(), (~sess).to_numpy(), sl.where(ok), tp.where(ok)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    sig, out, sl_s, tp_s = _setup(bars_df, p)
    sl, tp = sl_s.to_numpy(), tp_s.to_numpy()
    ov = bars_df["open"].to_numpy(dtype=float)
    hv, lv = bars_df["high"].to_numpy(dtype=float), bars_df["low"].to_numpy(dtype=float)
    m = len(ov)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, entry_i, s_, t_ = 0, -1, np.nan, np.nan
    for i in range(m):
        if pos == 1 and i >= entry_i:
            x = ov[entry_i]
            if lv[i] <= x * (1 - s_) or hv[i] >= x * (1 + t_):
                pos = 0
        if pos == 1 and out[i] and i >= entry_i:
            lx[i], pos = True, 0
        elif pos == 0 and sig[i] and i + 1 < m:
            le[i], pos, entry_i, s_, t_ = True, 1, i + 1, sl[i], tp[i]
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), pd.Series(lx, index=ix), false, false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    _, _, sl, tp = _setup(bars_df, p)
    return {"sl_stop": sl.shift(1), "tp_stop": tp.shift(1)}


def portfolio_kwargs(**params):
    return {}
