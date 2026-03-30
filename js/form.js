/* =========================================
   望月リソルゴルフクラブ LP
   form.js - フォームバリデーション & SendGrid送信
   Cloud Functions (GCP: servertest-337307) 経由
   v1.1
   ========================================= */

(function () {
  'use strict';

  /* ---- Cloud Functions エンドポイント（デプロイ後に差し替え） ---- */
  var CF_URL = 'https://asia-northeast1-servertest-337307.cloudfunctions.net/sendMail';

  var form      = document.getElementById('contact-form');
  var submitBtn = document.getElementById('submit-btn');
  var submitTxt = document.getElementById('submit-text');
  var errorBox  = document.getElementById('form-error');
  var thanks    = document.getElementById('thanks-message');

  if (!form) return;

  /* ---- Validation helpers ---- */
  function isEmail(v) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v);
  }
  function isTel(v) {
    return /^[\d\-+()\s]{7,20}$/.test(v);
  }

  function setError(field) {
    field.classList.add('error');
    field.setAttribute('aria-invalid', 'true');
  }
  function clearError(field) {
    field.classList.remove('error');
    field.removeAttribute('aria-invalid');
  }

  function showError(msg) {
    errorBox.textContent = msg;
    errorBox.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  }
  function hideError() {
    errorBox.textContent = '';
  }

  /* ---- Live validation (on blur) ---- */
  form.querySelectorAll('input, select, textarea').forEach(function (field) {
    field.addEventListener('blur', function () {
      if (field.required && !field.value.trim()) {
        setError(field);
      } else if (field.type === 'email' && field.value && !isEmail(field.value)) {
        setError(field);
      } else if (field.type === 'tel' && field.value && !isTel(field.value)) {
        setError(field);
      } else {
        clearError(field);
      }
    });
    field.addEventListener('input', function () {
      if (field.value.trim()) clearError(field);
    });
  });

  /* ---- Full validation ---- */
  function validate() {
    var errors = [];
    var firstErr = null;

    // Required fields
    form.querySelectorAll('[required]').forEach(function (field) {
      // ラジオボタンはグループ単位でチェック（後で個別処理）
      if (field.type === 'radio') return;
      if (!field.value.trim()) {
        setError(field);
        if (!firstErr) firstErr = field;
        var label = field.closest('.form-group')
          ? field.closest('.form-group').querySelector('label')
          : null;
        errors.push(label ? label.textContent.replace('必須', '').trim() : field.name);
      } else {
        clearError(field);
      }
    });

    // Required radio groups
    var requiredRadios = ['gender'];
    requiredRadios.forEach(function (name) {
      var radios = form.querySelectorAll('input[name="' + name + '"]');
      var checked = form.querySelector('input[name="' + name + '"]:checked');
      if (!checked) {
        radios.forEach(function (r) { r.classList.add('error'); });
        var group = radios[0] ? radios[0].closest('.form-group') : null;
        var label = group ? group.querySelector('label') : null;
        errors.push(label ? label.textContent.replace('必須', '').trim() : name);
        if (!firstErr && radios[0]) firstErr = radios[0];
      } else {
        radios.forEach(function (r) { r.classList.remove('error'); });
      }
    });

    // Email format
    var emailField = document.getElementById('email');
    if (emailField && emailField.value && !isEmail(emailField.value)) {
      setError(emailField);
      errors.push('メールアドレスの形式が正しくありません');
      if (!firstErr) firstErr = emailField;
    }

    // Tel format
    var telField = document.getElementById('tel');
    if (telField && telField.value && !isTel(telField.value)) {
      setError(telField);
      errors.push('電話番号の形式が正しくありません');
      if (!firstErr) firstErr = telField;
    }

    if (errors.length) {
      showError('以下の項目を確認してください：' + errors.slice(0, 3).join('、') + (errors.length > 3 ? ' 他' : ''));
      if (firstErr) firstErr.focus();
      return false;
    }
    return true;
  }

  /* ---- Build form data object ---- */
  function buildPayload() {
    var f = form;
    var birthY = document.getElementById('birth_y').value;
    var birthM = document.getElementById('birth_m').value;
    var birthD = document.getElementById('birth_d').value;

    var genderChecked = f.querySelector('input[name="gender"]:checked');

    return {
      name_kanji:        (f.name_sei.value + ' ' + f.name_mei.value).trim(),
      name_kana:         (f.kana_sei.value + ' ' + f.kana_mei.value).trim(),
      gender:            genderChecked ? genderChecked.value : '',
      birthday:          birthY && birthM && birthD
                           ? birthY + '年' + birthM + '月' + birthD + '日'
                           : '',
      zip:               f.zip.value,
      address:           f.address.value,
      tel:               f.tel.value,
      email:             f.email.value,
      inquiry_type:      f.inquiry_type.value,
      trial_date1:       f.trial_date1.value,
      trial_date2:       f.trial_date2.value,
      trial_time:        f.trial_time.value,
      play_count:        f.play_count.value,
      companion:         f.companion.value,
      membership_intent: f.membership_intent ? f.membership_intent.value : '',
      message:           f.message.value
    };
  }

  /* ---- Submit handler ---- */
  form.addEventListener('submit', async function (e) {
    e.preventDefault();
    hideError();

    if (!validate()) return;

    submitBtn.disabled = true;
    submitTxt.textContent = '送信中...';

    var payload = buildPayload();

    try {
      var res = await fetch(CF_URL, {
        method:  'POST',
        headers: { 'Content-Type': 'application/json' },
        body:    JSON.stringify(payload)
      });

      if (!res.ok) throw new Error('server error: ' + res.status);

      // Success
      form.style.display   = 'none';
      thanks.style.display = 'block';
      thanks.scrollIntoView({ behavior: 'smooth', block: 'center' });

    } catch (err) {
      console.error('Form submit error:', err);
      showError(
        '送信に失敗しました。お手数ですが、お電話にてお問い合わせください。\nTEL: 0267-53-6006'
      );
      submitBtn.disabled    = false;
      submitTxt.textContent = '送信する';
    }
  });

})();
