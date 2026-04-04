document.addEventListener('DOMContentLoaded', () => {
  const form = document.querySelector('form');
  const textarea = document.querySelector('textarea');

  if (textarea) {
    textarea.addEventListener('input', () => {
      textarea.dataset.length = String(textarea.value.length);
    });
  }

  if (form) {
    form.addEventListener('submit', () => {
      const button = form.querySelector('button[type="submit"]');
      if (button) {
        button.disabled = true;
        button.textContent = 'Analyzing...';
      }
    });
  }
});
