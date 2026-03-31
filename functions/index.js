/**
 * 望月リソルゴルフクラブ LP — フォームバックエンド
 * Cloud Functions (GCP) + SendGrid Web API v3
 *
 * デプロイ:
 *   gcloud functions deploy sendMail \
 *     --project servertest-337307 \
 *     --runtime nodejs20 \
 *     --trigger-http \
 *     --allow-unauthenticated \
 *     --region asia-northeast1 \
 *     --set-env-vars SENDGRID_API_KEY=YOUR_API_KEY_HERE \
 *     --entry-point sendMail
 */

const functions = require('@google-cloud/functions-framework');
const sgMail    = require('@sendgrid/mail');

functions.http('sendMail', async (req, res) => {
  // ---- CORS ----
  res.set('Access-Control-Allow-Origin', '*');
  res.set('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.set('Access-Control-Allow-Headers', 'Content-Type');
  if (req.method === 'OPTIONS') {
    return res.status(204).send('');
  }

  // POST以外は拒否
  if (req.method !== 'POST') {
    return res.status(405).json({ result: 'error', message: 'Method Not Allowed' });
  }

  // SendGrid APIキーを環境変数から取得（絶対に直書きしない）
  const apiKey = process.env.SENDGRID_API_KEY;
  if (!apiKey) {
    console.error('SENDGRID_API_KEY is not set');
    return res.status(500).json({ result: 'error', message: 'Server configuration error' });
  }
  sgMail.setApiKey(apiKey);

  const d = req.body;

  // 基本バリデーション
  if (!d.name_kanji || !d.email || !d.tel) {
    return res.status(400).json({ result: 'error', message: 'Required fields missing' });
  }

  // 送信先
  const ADMIN_EMAIL = 'mochizuki@resol-golf.jp';
  const FROM_EMAIL  = 'mochizuki@resol-golf.jp';

  // ---- フォーム内容をテキストに整形 ----
  const formBody = [
    `【お名前（漢字）】${d.name_kanji}`,
    `【お名前（カナ）】${d.name_kana || '未入力'}`,
    `【生年月日】${d.birthday || '未入力'}`,
    `【郵便番号】${d.zip || '未入力'}`,
    `【住所】${d.address || '未入力'}`,
    `【電話番号】${d.tel}`,
    `【メールアドレス】${d.email}`,
    `【お問い合わせ種別】${d.inquiry_type || '未選択'}`,
    `【視察プレー希望日（第1希望）】${d.trial_date1 || '未入力'}`,
    `【視察プレー希望日（第2希望）】${d.trial_date2 || '未入力'}`,
    `【ご希望時間】${d.trial_time || '未入力'}`,
    `【プレー人数】${d.play_count || '未入力'}`,
    `【同伴者お名前】${d.companion || '未入力'}`,
    `【会員権について】${d.membership_intent || '未選択'}`,
    `【お問い合わせ内容】\n${d.message || 'なし'}`,
  ].join('\n');

  // ---- ① 担当者への通知メール ----
  const adminMail = {
    to:      ADMIN_EMAIL,
    from:    FROM_EMAIL,
    subject: `【望月リソルGC LP】${d.inquiry_type || 'お問い合わせ'}｜${d.name_kanji} 様`,
    text: `望月リソルゴルフクラブ LP より新しいお問い合わせがありました。\n\n` +
          `━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n` +
          formBody + '\n' +
          `━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n` +
          `※このメールはLPフォームから自動送信されています。`,
  };

  // ---- ② ユーザーへの自動返信メール ----
  const userMail = {
    to:      d.email,
    from:    FROM_EMAIL,
    subject: '【望月リソルゴルフクラブ】お問い合わせを受け付けました',
    text: `${d.name_kanji} 様\n\n` +
          `この度は望月リソルゴルフクラブにお問い合わせいただき、\n` +
          `誠にありがとうございます。\n\n` +
          `以下の内容でお問い合わせを受け付けいたしました。\n` +
          `担当者より折り返しご連絡させていただきますので、\n` +
          `今しばらくお待ちくださいませ。\n\n` +
          `━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n` +
          formBody + '\n' +
          `━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n` +
          `━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n` +
          `望月リソルゴルフクラブ\n` +
          `〒384-2204 長野県佐久市協和3597-27\n` +
          `TEL: 0267-53-6006\n` +
          `Email: mochizuki@resol-golf.jp\n` +
          `━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n` +
          `※このメールは自動送信されています。\n` +
          `　このメールへの返信はお受けできませんのでご了承ください。`,
  };

  try {
    // 両方のメールを同時送信
    await Promise.all([
      sgMail.send(adminMail),
      sgMail.send(userMail),
    ]);

    console.log(`Mail sent successfully: ${d.name_kanji} (${d.email})`);
    return res.status(200).json({ result: 'success' });

  } catch (error) {
    console.error('SendGrid error:', error);
    if (error.response) {
      console.error('SendGrid response body:', error.response.body);
    }
    return res.status(500).json({ result: 'error', message: 'Failed to send email' });
  }
});
