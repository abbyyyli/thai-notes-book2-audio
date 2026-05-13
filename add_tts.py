"""
add_tts.py
把 🔊 語音按鈕加進所有 thai-02-ch*.html 學習指南。
執行：python3 add_tts.py
輸出：每個檔案旁邊產生 *-audio.html（原檔不動）
"""

import glob, os, re

CSS_INJECT = """    .speak-btn {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      width: 22px;
      height: 22px;
      border-radius: 50%;
      border: .5px solid rgba(37,99,235,.3);
      background: var(--blue-soft);
      color: #1d4ed8;
      font-size: 11px;
      cursor: pointer;
      margin-left: 6px;
      vertical-align: middle;
      flex-shrink: 0;
      transition: all .15s ease;
      line-height: 1;
      padding: 0;
    }
    .speak-btn:hover {
      background: rgba(37,99,235,.22);
      transform: scale(1.12);
    }
    .speak-btn.speaking {
      background: var(--orange-soft);
      border-color: rgba(249,115,22,.4);
      color: #c2410c;
      animation: pulse .6s ease-in-out infinite alternate;
    }
    @keyframes pulse {
      from { transform: scale(1); }
      to   { transform: scale(1.18); }
    }
    div.thai {
      display: flex;
      align-items: center;
      flex-wrap: wrap;
      gap: 2px;
    }
    .thai-text { flex: 1; }

"""

JS_INJECT = """
// ── TTS ──────────────────────────────────────────────
let thaiVoice = null;
let activBtn  = null;

function loadVoices() {
  const voices = window.speechSynthesis.getVoices();
  thaiVoice = voices.find(v => v.lang === 'th-TH') ||
              voices.find(v => v.lang.startsWith('th')) ||
              null;
}
loadVoices();
if (speechSynthesis.onvoiceschanged !== undefined) {
  speechSynthesis.onvoiceschanged = loadVoices;
}

function speakThai(text, btn) {
  if (!window.speechSynthesis) {
    alert('此瀏覽器不支援語音合成。請用 Safari（macOS/iOS）或 Chrome。');
    return;
  }
  if (activBtn === btn && speechSynthesis.speaking) {
    speechSynthesis.cancel();
    btn.classList.remove('speaking');
    btn.textContent = '🔊';
    activBtn = null;
    return;
  }
  speechSynthesis.cancel();
  if (activBtn) {
    activBtn.classList.remove('speaking');
    activBtn.textContent = '🔊';
  }
  const utter = new SpeechSynthesisUtterance(text);
  utter.lang  = 'th-TH';
  utter.rate  = 0.85;
  utter.pitch = 1.0;
  if (thaiVoice) utter.voice = thaiVoice;
  utter.onstart = () => {
    btn.classList.add('speaking');
    btn.textContent = '⏸';
    activBtn = btn;
  };
  utter.onend = utter.onerror = () => {
    btn.classList.remove('speaking');
    btn.textContent = '🔊';
    activBtn = null;
  };
  speechSynthesis.speak(utter);
}

document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('div.thai').forEach(el => {
    const rawText = el.textContent.trim();
    if (!rawText) return;
    const span = document.createElement('span');
    span.className = 'thai-text';
    span.textContent = rawText;
    const btn = document.createElement('button');
    btn.className = 'speak-btn';
    btn.textContent = '🔊';
    btn.title = '唸出泰文';
    btn.setAttribute('aria-label', '播放發音');
    btn.addEventListener('click', e => {
      e.stopPropagation();
      speakThai(rawText, btn);
    });
    el.textContent = '';
    el.appendChild(span);
    el.appendChild(btn);
  });
});
"""

def process_file(src_path):
    with open(src_path, encoding='utf-8') as f:
        html = f.read()

    # Skip if already processed
    if 'speak-btn' in html:
        print(f"  ⏭  已處理過，跳過：{os.path.basename(src_path)}")
        return

    # 1. Inject CSS before first @media (max-width...) or before </style>
    if '@media (max-width' in html:
        html = html.replace('@media (max-width', CSS_INJECT + '@media (max-width', 1)
    else:
        html = html.replace('</style>', CSS_INJECT + '</style>', 1)

    # 2. Inject JS before </script> (last one)
    last_script_close = html.rfind('</script>')
    if last_script_close == -1:
        print(f"  ⚠️  找不到 </script>，跳過：{os.path.basename(src_path)}")
        return
    html = html[:last_script_close] + JS_INJECT + html[last_script_close:]

    # 3. Write output
    base, ext = os.path.splitext(src_path)
    out_path = base + '-audio' + ext
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"  ✅  {os.path.basename(out_path)}")

def main():
    # Match both original and merged files in current directory
    patterns = ['thai-02-ch*.html', 'thai-02-ch*-merged.html']
    files = []
    for pat in patterns:
        files += glob.glob(pat)

    # Deduplicate and exclude already-audio files
    files = sorted(set(f for f in files if '-audio' not in f))

    if not files:
        print("⚠️  找不到任何 thai-02-ch*.html 檔案。")
        print("   請把這個 script 放在跟 HTML 檔案同一個資料夾裡再執行。")
        return

    print(f"找到 {len(files)} 個檔案，開始處理...\n")
    for f in files:
        process_file(f)
    print(f"\n完成！所有 *-audio.html 已產生在同一資料夾。")

if __name__ == '__main__':
    main()
