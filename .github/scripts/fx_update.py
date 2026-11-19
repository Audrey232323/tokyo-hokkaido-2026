#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""JPY->TWD rate: fetch from free no-key APIs, render the static FX block, update rates.json.
Used by build.py at build time and by the daily GitHub Action (.github/scripts/fx_update.py)."""
import json, re, sys, os, datetime, urllib.request
TZ=datetime.timezone(datetime.timedelta(hours=8))
SOURCES=[
 ('ExchangeRate-API','https://open.er-api.com/v6/latest/JPY'),
 ('currency-api','https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@latest/v1/currencies/jpy.json'),
 ('currency-api','https://latest.currency-api.pages.dev/v1/currencies/jpy.json'),
]
def _get(u):
    r=urllib.request.Request(u,headers={'User-Agent':'trip-fx/1.0'})
    return json.load(urllib.request.urlopen(r,timeout=15))
def fetch():
    """-> dict(r=float, t=ISO time (+08:00), s=source) or None"""
    for name,u in SOURCES:
        try:
            j=_get(u)
            if 'rates' in j:
                r=float(j['rates']['TWD']); ts=datetime.datetime.fromtimestamp(int(j['time_last_update_unix']),TZ)
            else:
                r=float(j['jpy']['twd']); ts=datetime.datetime.strptime(j['date'],'%Y-%m-%d').replace(hour=8,tzinfo=TZ)
            if 0.1<r<0.5: return {'r':round(r,6),'t':ts.isoformat(timespec='minutes'),'s':name,'fetched':datetime.datetime.now(TZ).isoformat(timespec='minutes')}
        except Exception as e:
            print('fx source failed',name,e,file=sys.stderr)
    return None
def disp(t):
    d=datetime.datetime.fromisoformat(t); return d.astimezone(TZ).strftime('%Y/%m/%d %H:%M')
YEN=(100,500,1000,3000,5000,10000,30000)
def block(fx):
    r=fx['r']
    tbl=''.join('<tr><td>¥%s</td><td>約 NT$%s</td></tr>'%(format(y,','),format(round(y*r),',')) for y in YEN)
    return ('<!--FX--><div class="fxr" id="fxbox" data-r="%s" data-t="%s" data-s="%s">'
            '<p class="fxnow">1 日圓 ≈ <b id="fxv">%.4f</b> 台幣</p>'
            '<p class="fine" id="fxrate">匯率更新：%s（%s）・每天自動更新</p>'
            '<button type="button" class="fxre jsonly" id="fxre">🔄 更新匯率</button></div>'
            '<details class="fxt"><summary>常用金額速查表</summary><table class="tb" id="fxtb">%s</table></details><!--/FX-->'
            )%(r,fx['t'],fx['s'],r,disp(fx['t'])[:10] if fx['s']=='currency-api' else disp(fx['t']),fx['s'],tbl)
def apply(htmltext,fx):
    return re.sub(r'<!--FX-->.*?<!--/FX-->',lambda m:block(fx),htmltext,flags=re.S)
def main(root='.'):
    fx=fetch()
    if not fx: print('no rate; keep old'); return 0
    p=os.path.join(root,'rates.json')
    old={}
    try: old=json.load(open(p))
    except Exception: pass
    if old.get('JPY_TWD')==fx['r'] and old.get('updated')==fx['t']: print('unchanged'); return 0
    json.dump({'base':'JPY','JPY_TWD':fx['r'],'updated':fx['t'],'source':fx['s'],'fetched':fx['fetched']},open(p,'w'),ensure_ascii=False,indent=1)
    ip=os.path.join(root,'index.html')
    if os.path.exists(ip):
        h=open(ip,encoding='utf-8').read(); n=apply(h,fx)
        if n!=h: open(ip,'w',encoding='utf-8').write(n)
    print('updated',fx); return 0
if __name__=='__main__': sys.exit(main(sys.argv[1] if len(sys.argv)>1 else '.'))
