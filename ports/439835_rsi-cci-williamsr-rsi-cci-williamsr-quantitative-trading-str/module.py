"""Triple oscillator extremes with a percent bracket, 1-minute bars: from flat, RSI 14 under 25, CCI 20 under -130 and Williams %R 14 under -85 go long with a 1.2 % target and a 0.45 % stop; the mirrored
extremes go short.
Port of FMZ strategy #439835 "RSI-CCI-WilliamsR-量化交易策略RSI-CCI-WilliamsR-Quantitative-Trading-Strategy" (RSI CCI Williams %R Strategy with TP and SL).

FMZ source id: 439835

Source
    https://www.fmz.com/strategy/439835 (PineScript v5, FMZ last modified 2024-01-24 11:18:08).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 154-201), RSI 14 (25 / 75), CCI 20 (-130 / 130), Williams %R 14 (-85 / -15); take profit 1.2 %, stop 0.45 %
    long = rsi < 25 and cci < -130 and willR < -85 and flat -> entry Long, exit(limit = close x 1.012, stop = close x 0.9955);  short mirror (rsi > 75, cci > 130, willR > -15)

Interpretation choices (Pine rules in SURVEY_README.md)
    * The bracket is set from the signal close and sent once; the port reads it as fixed fractions of
      the entry fill (1.2 % / 0.45 %, as #437751). "Flat" follows the house bracket loop. Entries only
      from flat: Opposite entries cannot occur. Stop module: portfolio_kwargs {} (driver D4). No sizing
      code. FREQ = "1min" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; bracket fixed at entry.
    2 generic: PASS, oscillator extremes and a percent bracket.
    3 crypto-exchange-only: no (exchange pair in the header only).
    4 signals only: the percent inputs stored.
    5 ranges declared: GRID below (4 trials), before any backtest.
    6 near-duplicates: no DG / ND group; ported (rule 7).
    7 FMZ performance claims: ignored.
Volume: not used (check 8).
Session open: not used.
Opposite entries cannot occur (entries only from flat).

Marks: none
"""
import numpy as np
import pandas as pd

NAME = "fmz_439835_rsi_cci_willr_extremes_bracket"
FAMILY = "multi_indicator_confluence"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "1min"  # backtest header period: 1m
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "tp": [0.012, 0.006],
    "sl": [0.0045, 0.009],
}
DEFAULT_PARAMS = {"tp": 0.012, "sl": 0.0045, "rsi_period": 14, "cci_period": 20, "will_period": 14,
                  "rsi_os": 25, "rsi_ob": 75, "cci_os": -130, "cci_ob": 130, "will_os": -85, "will_ob": -15}


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


def _rsi(c, n):
    d = c.diff()
    up = _rma(d.clip(lower=0), n)
    dn = _rma((-d).clip(lower=0), n)
    with np.errstate(divide="ignore", invalid="ignore"):
        r = 100.0 - 100.0 / (1.0 + up / dn)
    r = r.where(up != 0, 0.0).where(dn != 0, 100.0)    # Pine: down == 0 -> 100, else up == 0 -> 0
    return r.where(up.notna() & dn.notna())


def precompute(raw_1m_df, symbol_key, **params):
    return _resample(raw_1m_df, FREQ)


def _setup(bars_df, p):
    h, lo, c = bars_df["high"], bars_df["low"], bars_df["close"]
    r = _rsi(c, int(p["rsi_period"]))
    n = int(p["cci_period"])
    ma = c.rolling(n).mean()
    dev = c.rolling(n).apply(lambda a: np.mean(np.abs(a - a.mean())), raw=True)
    with np.errstate(divide="ignore", invalid="ignore"):
        cci = (c - ma) / (0.015 * dev)
    k = int(p["will_period"])
    hh, ll = h.rolling(k).max(), lo.rolling(k).min()
    with np.errstate(divide="ignore", invalid="ignore"):
        wr = (hh - c) / (hh - ll) * -100
    up = (r < float(p["rsi_os"])) & (cci < float(p["cci_os"])) & (wr < float(p["will_os"]))
    dn = (r > float(p["rsi_ob"])) & (cci > float(p["cci_ob"])) & (wr > float(p["will_ob"]))
    return up.to_numpy(), dn.to_numpy()


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    up, dn = _setup(bars_df, p)
    ov = bars_df["open"].to_numpy(dtype=float)
    hv, lv = bars_df["high"].to_numpy(dtype=float), bars_df["low"].to_numpy(dtype=float)
    sl, tp = float(p["sl"]), float(p["tp"])
    m = len(ov)
    le, se = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    pos, entry_i = 0, -1
    for i in range(m):
        if pos != 0 and i >= entry_i:
            x = ov[entry_i]
            if pos == 1 and (lv[i] <= x * (1 - sl) or hv[i] >= x * (1 + tp)):
                pos = 0
            elif pos == -1 and (hv[i] >= x * (1 + sl) or lv[i] <= x * (1 - tp)):
                pos = 0
        if pos == 0 and i + 1 < m:
            if up[i]:
                le[i], pos, entry_i = True, 1, i + 1
            elif dn[i]:
                se[i], pos, entry_i = True, -1, i + 1
    ix = bars_df.index
    false = pd.Series(False, index=ix)
    return pd.Series(le, index=ix), false, pd.Series(se, index=ix), false.copy()


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["sl"]), "tp_stop": float(p["tp"])}


def portfolio_kwargs(**params):
    return {}
