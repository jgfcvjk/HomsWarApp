"""تجهيز مشروع APK للعبة حرب حمص (يعمل داخل GitHub Actions)
   python3 prepare_app.py web      ← ينسخ اللعبة ويحمّل المكتبات لتعمل بدون إنترنت
   python3 prepare_app.py android  ← يجعل التطبيق أفقياً وبملء الشاشة وشاشة مضاءة دائماً """
import os, re, sys, urllib.request

LIBS = {
    'https://unpkg.com/peerjs@1.5.4/dist/peerjs.min.js': 'peerjs.min.js',
    'https://cdn.jsdelivr.net/npm/three@0.147.0/build/three.min.js': 'three.min.js',
    'https://cdn.jsdelivr.net/npm/mqtt@5.10.1/dist/mqtt.min.js': 'mqtt.min.js',
}

def web():
    os.makedirs('www/lib', exist_ok=True)
    # ملف اللعبة: أي ملف html في المستودع (يُفضَّل غير index.html إن وُجد أكثر من واحد) */
    htmls = sorted(f for f in os.listdir('.') if f.lower().endswith('.html'))
    others = [f for f in htmls if f != 'index.html']
    src = (others or htmls)[-1]
    print('game file:', src)
    s = open(src, encoding='utf-8').read()
    for url, name in LIBS.items():
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            data = urllib.request.urlopen(req, timeout=60).read()
            if len(data) < 10000:
                raise ValueError('ملف صغير جداً')
            open('www/lib/' + name, 'wb').write(data)
            s = s.replace(url, 'lib/' + name)
            print('bundled', name, len(data))
        except Exception as e:
            print('skip (يبقى من الإنترنت):', url, e)
    open('www/index.html', 'w', encoding='utf-8').write(s)

MAIN_ACTIVITY = '''package com.homswar.game;

import android.os.Bundle;
import android.view.View;
import android.view.WindowManager;
import com.getcapacitor.BridgeActivity;

public class MainActivity extends BridgeActivity {
    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
        hideBars();
    }
    @Override
    public void onWindowFocusChanged(boolean hasFocus) {
        super.onWindowFocusChanged(hasFocus);
        if (hasFocus) hideBars();
    }
    private void hideBars() {
        getWindow().getDecorView().setSystemUiVisibility(
            View.SYSTEM_UI_FLAG_LAYOUT_STABLE
            | View.SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION
            | View.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN
            | View.SYSTEM_UI_FLAG_HIDE_NAVIGATION
            | View.SYSTEM_UI_FLAG_FULLSCREEN
            | View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY);
    }
}
'''

def android():
    man = 'android/app/src/main/AndroidManifest.xml'
    m = open(man, encoding='utf-8').read()
    if 'screenOrientation' not in m:
        m = m.replace('<activity', '<activity android:screenOrientation="sensorLandscape"', 1)
    open(man, 'w', encoding='utf-8').write(m)

    st = 'android/app/src/main/res/values/styles.xml'
    t = open(st, encoding='utf-8').read()
    add = ('<item name="android:windowFullscreen">true</item>'
           '<item name="android:windowLayoutInDisplayCutoutMode">shortEdges</item>')
    t = re.sub(r'(<style name="AppTheme\.NoActionBar"[^>]*>)', lambda g: g.group(1) + add, t, count=1)
    open(st, 'w', encoding='utf-8').write(t)

    d = 'android/app/src/main/java/com/homswar/game'
    os.makedirs(d, exist_ok=True)
    open(d + '/MainActivity.java', 'w', encoding='utf-8').write(MAIN_ACTIVITY)
    print('android patched')

if __name__ == '__main__':
    {'web': web, 'android': android}[sys.argv[1]]()
