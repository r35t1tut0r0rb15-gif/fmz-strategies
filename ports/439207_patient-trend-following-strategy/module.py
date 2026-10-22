"""CCI pullbacks in a Chandelier-style trend, 1-minute bars: from flat, with the EMA 21 above the EMA 55 and the ATR(55) x 5 trend up, a CCI 20 between -140 and -100 goes long with a stop at the trend's long
line and a 400-tick target (re-expressed as an ATR multiple); the mirror goes short.
Port of FMZ strategy #439207 "Patient Trend Following Strategy" (Patient Trendfollower (7) Strategy).

FMZ source id: 439207

Source
    https://www.fmz.com/strategy/439207 (PineScript v4, FMZ last modified 2024-01-18 12:40:11).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 169-316), EMA 21 / 55; CCI 20 levels 100 / 140 / 180; ATR 55 x 5 with wicks; spread 0.0002; level 1 only; static target 400 pips
    trend lines: longStop = hl2 - 5 atr(55) ratcheted while low[1] is above it, shortStop mirror with high[1];  dir flips on the high / low crossing the previous lines
    buy1 = ema 21 > ema 55 and dir 1 and -140 < cci <= -100 and no open trade -> entry Long1, exit(profit = 400 ticks, stop = longStop - spread of the signal bar);  sell1 mirror

Interpretation choices (Pine rules in SURVEY_README.md)
    * The stop is the trend's long line (short line) of the signal bar minus (plus) the spread: sl_stop
      = its distance from the signal close as a fraction, shifted one bar inside stops() and re-based on
      the fill. Criterion 2: the 400-tick target becomes k_tp x ATR(14) / close of the signal bar (1.0 is
      the reading: 40 on BTC with 0.1 ticks against a 1-minute ATR near 40; 3.0 a wider target), and the
      0.0002 spread a fraction of the close (5e-9 reads it on BTC near 42000). "Flat" follows the house
      bracket. Entries only from flat: Opposite entries cannot occur. Stop module: portfolio_kwargs {}
      (driver D4). The order size is sizing. FREQ = "1min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry.
    2 generic: ADAPT, tick target -> ATR multiple; price-unit spread -> fraction.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the capital / close order size and the pip inputs stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: ND429967 (2 members, best partner #429967, Jaccard 0.785); ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Opposite entries cannot occur (entries only from flat).

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_439207_patient_trendfollower_cci_pullback"
FAMILY = "trend_confluence"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "k_tp": [1.0, 3.0],
    "mult": [5.0, 3.0],
}
DEFAULT_PARAMS = {"k_tp": 1.0, "mult": 5.0, "ema_short": 21, "ema_long": 55, "cci_len": 20, "atr_len": 55,
                  "spread_frac": 5e-9, "tp_atr_len": 14}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


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


def _atr(bars_df, n):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - lo, (h - pc).abs(), (lo - pc).abs()], axis=1).max(axis=1)
    return _rma(tr, int(n))


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def _setup(bars_df, p):
    o, h, lo, c = (bars_df[k] for k in ("open", "high", "low", "close"))
    es = c.ewm(span=int(p["ema_short"]), adjust=False).mean()
    el = c.ewm(span=int(p["ema_long"]), adjust=False).mean()
    n = int(p["cci_len"])
    ma = c.rolling(n).mean()
    dev = c.rolling(n).apply(lambda a: np.mean(np.abs(a - a.mean())), raw=True)
    with np.errstate(divide="ignore", invalid="ignore"):
        cci = ((c - ma) / (0.015 * dev)).to_numpy()
    a = (float(p["mult"]) * _atr(bars_df, p["atr_len"])).to_numpy()
    hv, lv, cv = h.to_numpy(dtype=float), lo.to_numpy(dtype=float), c.to_numpy(dtype=float)
    hl2 = (hv + lv) / 2
    m = len(cv)
    ls, ss = np.full(m, np.nan), np.full(m, np.nan)
    d = np.ones(m)
    for i in range(m):
        l0, s0 = hl2[i] - a[i], hl2[i] + a[i]
        lp = ls[i - 1] if i > 0 and not np.isnan(ls[i - 1]) else l0           # nz(longStop[1], longStop)
        sp = ss[i - 1] if i > 0 and not np.isnan(ss[i - 1]) else s0
        l1 = lv[i - 1] if i > 0 else np.nan
        h1 = hv[i - 1] if i > 0 else np.nan
        ls[i] = max(l0, lp) if (l1 > lp and not np.isnan(l0)) else l0
        ss[i] = min(s0, sp) if (h1 < sp and not np.isnan(s0)) else s0
        prev = d[i - 1] if i > 0 else 1.0
        d[i] = 1.0 if (prev == -1 and hv[i] > sp) else (-1.0 if (prev == 1 and lv[i] < lp) else prev)
    spr = float(p["spread_frac"]) * cv
    up = (es > el).to_numpy() & (d == 1) & (cci <= -100) & (cci > -140)
    dn = (es < el).to_numpy() & (d == -1) & (cci >= 100) & (cci < 140)
    sl = np.where(up, (cv - (ls - spr)) / cv, np.where(dn, ((ss + spr) - cv) / cv, np.nan))
    sl = np.where(sl > 0, sl, np.nan)
    tpf = (float(p["k_tp"]) * _atr(bars_df, p["tp_atr_len"]) / c).to_numpy()
    return up & ~np.isnan(sl), dn & ~np.isnan(sl), sl, tpf


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    up, dn, sl, tpf = _setup(bars_df, p)
    ov = bars_df["open"].to_numpy(dtype=float)
    hv, lv = bars_df["high"].to_numpy(dtype=float), bars_df["low"].to_numpy(dtype=float)
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
        if pos == 0 and i + 1 < m and not np.isnan(tpf[i]):
            if up[i]:
                le[i], pos, entry_i, s_, t_ = True, 1, i + 1, sl[i], tpf[i]
            elif dn[i]:
                se[i], pos, entry_i, s_, t_ = True, -1, i + 1, sl[i], tpf[i]
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, pd.Series(se, index=ix), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    _, _, sl, tpf = _setup(bars_df, p)
    ix = bars_df.index
    return {"sl_stop": pd.Series(sl, index=ix).shift(1), "tp_stop": pd.Series(tpf, index=ix).shift(1)}


def portfolio_kwargs(**params):
    return {}
