"""A linear-regression channel (30, 2 sd) with move filters, 12-hour bars: after any close under the lower line, a 3-bar rise over 1.8 % (without a 120-bar rise over 5 %) goes long once per touch; after any close over the upper line, a 0.2 % fall from the previous 3-minute close goes short once per touch; body crossings of the lines close, with a 5 % / 10 % bracket from the entry price; reversing.
Port of FMZ strategy #482460 "Advanced Linear Regression Channel Trading Strategy with Dynamic Exit System" (STRATEGY WITH SL).

FMZ source id: 482460

Source
    https://www.fmz.com/strategy/482460 (PineScript v6, FMZ last modified 2025-02-18 15:18:08).
    Verbatim copy: original_source.md. Read 2026-10-22 (FMZ-C).

Original signal (original_source.md lines 101-236), linreg 30, x 2.0; move 1.8 % over 3 bars, large move 5 % over 120 bars; drop 0.2 % from request.security('3', close[1]); TP 10 %, SL 5 % of the avg price
    close < lower -> lower_crossed := true, move_after_cross := false;  close > upper -> upper_crossed := true, alert_sent := false
    lower_crossed and up 1.8 % and not move_after_cross and not large move -> entry Long (move_after_cross := true);  upper_crossed and drop 0.2 % and not alert_sent -> entry Short (alert_sent := true)
    body (open + close) / 2 -> ohlc4 crosses the lower line -> close Long;  crosses over the upper line -> close Short;  exit(limit = avg x 1.10, stop = avg x 0.95), mirror for shorts

Interpretation choices (Pine rules in SURVEY_README.md)
    * The flags are kept as written: lower_crossed and upper_crossed are never cleared, so after the first
      touch each side only needs its move filter and its own once-per-touch flag. The 3-minute request on
      a 12-hour chart is a lower time frame: it returns the chart bar's last block, here close[1] of that
      block, i.e. the close of the 3-minute block before the bar's last one, built from the minutes in
      precompute (as #477605). The "Heikin-Ashi" values are (open + close) / 2 and ohlc4 of the bar itself,
      as written. The entries come before the closes, so a close acts only on a position held into the bar
      and not reversed on it (as #441963), and a bar with both entries takes the short (the later call, as
      #437773): a loop that also follows the avg-price bracket on the bar's high / low (as #449508). The
      bracket is a scalar fraction active from the fill (as #440797). REVERSAL INTENDED. Stop module:
      portfolio_kwargs {} (driver D4). Stops on bars longer than 1 hour: mark coarse_bar_stop. No sizing
      code. FREQ = "12h" from the backtest header.

Admission criteria
    1 fits the interface: PASS, bar-close orders; lower-time-frame value from the bar's last block; avg-price bracket.
    2 generic: PASS, regression-channel touches with move filters and body-crossing exits.
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

NAME = "fmz_482460_linreg30_channel_touch_move_filter_body_exit_pct_bracket_reversal"
FAMILY = "mean_reversion_band"  # proposed 2026-10-22 (FMZ-C), user to confirm
FREQ = "12h"  # backtest header period: 12h
PERIODS_PER_YEAR_OVERRIDE = None
USES_STOPS = True

GRID = {
    "length": [30, 60],
    "mult": [2.0, 2.5],
}
DEFAULT_PARAMS = {"length": 30, "mult": 2.0, "move_pct": 1.8, "large_move_pct": 5.0, "large_bars": 120,
                  "drop_frac": 0.002, "tp_frac": 0.10, "sl_frac": 0.05}


def _resample(raw_1m_df, freq):
    ohlc = raw_1m_df[["open", "high", "low", "close"]]
    bars = ohlc.resample(freq, label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"})
    bars = bars.dropna(how="all")  # an empty period is not a bar; never forward-filled
    if bars.index.tz is None:
        raise ValueError("raw_1m_df must have a tz-aware UTC index")
    return bars


def precompute(raw_1m_df, symbol_key, **params):
    bars = _resample(raw_1m_df, FREQ)
    ltf = _resample(raw_1m_df, "3min")
    prev = ltf["close"].shift(1)                                   # close[1] in the 3-minute series
    last = prev.groupby(prev.index.floor(FREQ)).last()             # the chart bar's last block
    bars["ltf_prev_close"] = last.reindex(bars.index).to_numpy()
    return bars


def _linreg(x, n):
    """Pine ta.linreg(x, n, 0): the least-squares line over the last n values, at the last one."""
    v = x.to_numpy(dtype=float)
    m = len(v)
    out = np.full(m, np.nan)
    if m >= n:
        k = np.arange(n, dtype=float)
        sy = np.convolve(v, np.ones(n))[:m]                        # sum of the window
        sky = np.convolve(v, k)[:m]                                # sum of (age) x value
        sxy = (n - 1) * sy - sky                                   # x = n - 1 - age
        sx, sxx = k.sum(), (k * k).sum()
        b = (n * sxy - sx * sy) / (n * sxx - sx * sx)
        a = (sy - b * sx) / n
        out[n - 1:] = (a + b * (n - 1))[n - 1:]
    return pd.Series(out, index=x.index)


def simulate(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    o, h, lo, c = bars_df["open"], bars_df["high"], bars_df["low"], bars_df["close"]
    n = int(p["length"])
    reg = _linreg(c, n)
    sd = c.rolling(n).std(ddof=0)
    up_s, dn_s = reg + float(p["mult"]) * sd, reg - float(p["mult"]) * sd
    nb = int(p["large_bars"])
    is_up = ((c - c.shift(3)) / c.shift(3) * 100 > float(p["move_pct"])).to_numpy()
    large = ((c - c.shift(nb)) / c.shift(nb) * 100 > float(p["large_move_pct"])).to_numpy()
    p3 = bars_df["ltf_prev_close"]
    drop = ((c - p3) / p3 <= -float(p["drop_frac"])).to_numpy()
    ho, hc = (o + c) / 2, (o + h + lo + c) / 4
    ex_l = (((ho > dn_s) & (hc < dn_s)) | ((ho < dn_s) & (hc > dn_s))).to_numpy()
    ex_s = ((ho < up_s) & (hc > up_s)).to_numpy()
    below, above = (c < dn_s).to_numpy(), (c > up_s).to_numpy()
    ov, hv, lv = o.to_numpy(dtype=float), h.to_numpy(dtype=float), lo.to_numpy(dtype=float)
    sl, tp = float(p["sl_frac"]), float(p["tp_frac"])
    m = len(ov)
    le, lx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    se, sx = np.zeros(m, dtype=bool), np.zeros(m, dtype=bool)
    lcr = ucr = mac = sent = False
    pos, pend, ent = 0, 0, np.nan
    for i in range(m):
        if pend in (1, -1):                       # the order from the bar before fills at this open
            pos, ent = pend, ov[i]
        elif pend == 2:
            pos = 0
        pend = 0
        if pos == 1 and (lv[i] <= ent * (1 - sl) or hv[i] >= ent * (1 + tp)):
            pos = 0                               # the bracket closes the long on this bar
        elif pos == -1 and (hv[i] >= ent * (1 + sl) or lv[i] <= ent * (1 - tp)):
            pos = 0
        if below[i]:
            lcr, mac = True, False
        if above[i]:
            ucr, sent = True, False
        fl = lcr and is_up[i] and not mac and not large[i]
        fs = ucr and drop[i] and not sent
        if fl:
            mac = True
        if fs:
            sent = True
        new = 0
        if fl and pos != 1:
            new = 1
        if fs and pos != -1:
            new = -1                              # the later call wins a bar with both entries
        if new == 1:
            le[i], pend = True, 1
        elif new == -1:
            se[i], pend = True, -1
        elif pos == 1 and ex_l[i]:
            lx[i], pend = True, 2
        elif pos == -1 and ex_s[i]:
            sx[i], pend = True, 2
    idx = c.index
    return (pd.Series(le, index=idx), pd.Series(lx, index=idx),
            pd.Series(se, index=idx), pd.Series(sx, index=idx))


def stops(bars_df, **params):
    p = {**DEFAULT_PARAMS, **params}
    return {"sl_stop": float(p["sl_frac"]), "tp_stop": float(p["tp_frac"])}


def portfolio_kwargs(**params):
    return {}
