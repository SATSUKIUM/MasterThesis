(() => {
  'use strict';
  const select = document.getElementById('figure-font');
  const reset = document.getElementById('font-reset');
  const status = document.getElementById('font-status');
  const choices = JSON.parse(document.getElementById('font-choices').textContent);
  const initialFont = select.value;
  let revision = 0;
  async function applyFont() {
    const current = ++revision;
    const font = choices.find(choice => choice.id === select.value);
    if (!font) return;
    status.textContent = `${font.label}を読み込み中…`;
    try {
      await Promise.all([
        document.fonts.load(`400 20px "${font.family}"`),
        document.fonts.load(`700 20px "${font.family}"`),
        document.fonts.load(`italic 400 20px "${font.family}"`),
        document.fonts.load(`italic 700 20px "${font.family}"`)
      ]);
      if (current !== revision) return;
      document.documentElement.style.setProperty('--figure-font', `"${font.family}", sans-serif`);
      status.textContent = `${font.label}（通常体・太字・斜体）`;
    } catch (error) {
      if (current === revision) status.textContent = `${font.label}の読込みに失敗しました`;
    }
  }
  select.addEventListener('change', applyFont);
  reset.addEventListener('click', () => {
    select.value = initialFont;
    applyFont();
  });
  applyFont();
})();
