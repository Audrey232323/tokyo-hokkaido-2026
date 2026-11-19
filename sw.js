/* trip26 offline service worker */
var V='trip26-ae3b16747b',IMG='trip26-img-v1';
var CORE=['./','./index.html','./fonts/huninn-0b0f67d4.woff2','./fonts/iansui-bc6c36b4.woff2','./manifest.webmanifest','./icon-192.png','./apple-touch-icon.png','./img/map/sapporo.webp','./img/map/haneda.webp',
 './img/cat/all.webp','./img/cat/hotel.webp','./img/cat/spot.webp','./img/cat/shop.webp','./img/cat/food.webp','./img/cat/conv.webp','./img/cat/trans.webp','./img/cat/wheel.webp'];
self.addEventListener('install',function(e){e.waitUntil(caches.open(V).then(function(c){return c.addAll(CORE);}).then(function(){return self.skipWaiting();}));});
self.addEventListener('activate',function(e){e.waitUntil(caches.keys().then(function(ks){return Promise.all(ks.filter(function(k){return k!==V&&k!==IMG&&k.indexOf('trip26')===0;}).map(function(k){return caches.delete(k);}));}).then(function(){return self.clients.claim();}));});
self.addEventListener('fetch',function(e){var r=e.request;if(r.method!=='GET')return;var u=new URL(r.url);if(u.origin!==location.origin)return;
 if(r.mode==='navigate'||u.pathname.endsWith('/index.html')||u.pathname.endsWith('/')){
  e.respondWith(fetch(r).then(function(res){var cp=res.clone();caches.open(V).then(function(c){c.put('./index.html',cp);});return res;}).catch(function(){return caches.match('./index.html',{ignoreSearch:true});}));return;}
 if(/\/img\/|\/fonts\/|\.png$|\.webmanifest$/.test(u.pathname)){
  e.respondWith(caches.match(r,{ignoreSearch:true}).then(function(hit){return hit||fetch(r).then(function(res){if(res.ok){var cp=res.clone();caches.open(IMG).then(function(c){c.put(r,cp);});}return res;});}));}
});
