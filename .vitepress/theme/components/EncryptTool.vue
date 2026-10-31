<script setup>
import { ref } from 'vue'

const ENCRYPTED_FORMAT = 'open-bookmarks/encrypted/1.0'
const CIPHER = 'AES-256-GCM'
const KDF = 'PBKDF2-HMAC-SHA-256'
const ITERATIONS = 600000

const plainText = ref('')
const plainPassword = ref('')
const plainConfirm = ref('')
const showPlainPassword = ref(false)
const encryptedOutput = ref('')
const encryptError = ref('')
const encryptFileName = ref('')

const encryptedText = ref('')
const decryptPassword = ref('')
const showDecryptPassword = ref(false)
const plainOutput = ref('')
const decryptError = ref('')

function toHex(buffer) {
  return Array.from(new Uint8Array(buffer))
    .map((b) => b.toString(16).padStart(2, '0'))
    .join('')
}

function fromHex(hex) {
  if (typeof hex !== 'string' || hex.length % 2 !== 0 || !/^[0-9a-fA-F]+$/.test(hex)) {
    throw new Error('bad hex')
  }
  const bytes = new Uint8Array(hex.length / 2)
  for (let i = 0; i < bytes.length; i++) {
    bytes[i] = parseInt(hex.slice(i * 2, i * 2 + 2), 16)
  }
  return bytes
}

async function getKey(password, salt) {
  const keyMaterial = await crypto.subtle.importKey(
    'raw',
    new TextEncoder().encode(password),
    'PBKDF2',
    false,
    ['deriveKey']
  )
  return crypto.subtle.deriveKey(
    { name: 'PBKDF2', salt, iterations: ITERATIONS, hash: 'SHA-256' },
    keyMaterial,
    { name: 'AES-GCM', length: 256 },
    false,
    ['encrypt', 'decrypt']
  )
}

async function onEncrypt() {
  encryptError.value = ''
  encryptedOutput.value = ''
  let pack
  try {
    pack = JSON.parse(plainText.value)
  } catch {
    encryptError.value = 'That is not valid JSON.'
    return
  }
  if (!pack || typeof pack !== 'object' || Array.isArray(pack)) {
    encryptError.value = 'A plain pack must be a JSON object.'
    return
  }
  if (pack.format !== 'open-bookmarks/1.0') {
    encryptError.value = 'A plain pack must have format open-bookmarks/1.0.'
    return
  }
  if (typeof pack.title !== 'string' || pack.title.trim() === '') {
    encryptError.value = 'A plain pack must have a non-empty title.'
    return
  }
  if (!Array.isArray(pack.nodes)) {
    encryptError.value = 'A plain pack must have a nodes list.'
    return
  }
  if (!plainPassword.value) {
    encryptError.value = 'Enter a password.'
    return
  }
  if (plainPassword.value !== plainConfirm.value) {
    encryptError.value = 'The two passwords do not match.'
    return
  }
  try {
    const salt = crypto.getRandomValues(new Uint8Array(16))
    const iv = crypto.getRandomValues(new Uint8Array(12))
    const key = await getKey(plainPassword.value, salt)
    const ciphertext = await crypto.subtle.encrypt(
      { name: 'AES-GCM', iv },
      key,
      new TextEncoder().encode(JSON.stringify(pack))
    )
    const envelope = {
      format: ENCRYPTED_FORMAT,
      cipher: CIPHER,
      kdf: KDF,
      iterations: ITERATIONS,
      salt: toHex(salt),
      iv: toHex(iv),
      ciphertext: toHex(ciphertext),
    }
    encryptedOutput.value = JSON.stringify(envelope, null, 2)
    const slug = pack.title.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '') || 'pack'
    encryptFileName.value = slug + '-encrypted.json'
  } catch {
    encryptError.value = 'Encryption failed in this browser. Try a browser with Web Crypto support.'
  }
}

async function onDecrypt() {
  decryptError.value = ''
  plainOutput.value = ''
  let encrypted
  try {
    encrypted = JSON.parse(encryptedText.value)
  } catch {
    decryptError.value = 'That is not valid JSON.'
    return
  }
  if (!decryptPassword.value) {
    decryptError.value = 'Enter a password.'
    return
  }
  try {
    if (!encrypted || encrypted.format !== ENCRYPTED_FORMAT) {
      throw new Error('not encrypted')
    }
    if (encrypted.cipher && encrypted.cipher !== CIPHER) throw new Error('cipher')
    if (encrypted.kdf && encrypted.kdf !== KDF) throw new Error('kdf')
    const iterations = encrypted.iterations || ITERATIONS
    const salt = fromHex(encrypted.salt)
    const iv = fromHex(encrypted.iv)
    const ciphertext = fromHex(encrypted.ciphertext)
    if (salt.length !== 16 || iv.length !== 12 || ciphertext.length < 16) {
      throw new Error('length')
    }
    const keyMaterial = await crypto.subtle.importKey(
      'raw',
      new TextEncoder().encode(decryptPassword.value),
      'PBKDF2',
      false,
      ['deriveKey']
    )
    const key = await crypto.subtle.deriveKey(
      { name: 'PBKDF2', salt, iterations, hash: 'SHA-256' },
      keyMaterial,
      { name: 'AES-GCM', length: 256 },
      false,
      ['decrypt']
    )
    const plain = await crypto.subtle.decrypt({ name: 'AES-GCM', iv }, key, ciphertext)
    const pack = JSON.parse(new TextDecoder().decode(plain))
    plainOutput.value = JSON.stringify(pack, null, 2)
  } catch {
    decryptError.value = 'Decryption failed. Invalid password or corrupted payload'
  }
}

function onPlainFile(event) {
  const file = event.target.files && event.target.files[0]
  if (!file) return
  file.text().then((text) => {
    plainText.value = text
  })
}

function onEncryptedFile(event) {
  const file = event.target.files && event.target.files[0]
  if (!file) return
  file.text().then((text) => {
    encryptedText.value = text
  })
}

function download(text, filename) {
  const blob = new Blob([text], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  link.click()
  URL.revokeObjectURL(url)
}

async function copyText(text) {
  try {
    await navigator.clipboard.writeText(text)
  } catch {
    // Clipboard needs a secure context. The output box below is still selectable.
  }
}
</script>

<template>
  <div class="encrypt-tool">
    <h2>Encrypt a plain pack</h2>
    <p>
      <label for="plain-file">Plain pack file, or paste below</label>
      <input id="plain-file" type="file" accept=".json,application/json" @change="onPlainFile" />
    </p>
    <p>
      <label for="plain-text">Plain pack JSON</label>
      <textarea id="plain-text" v-model="plainText" rows="10" placeholder='{"format": "open-bookmarks/1.0", "title": "My pack", "nodes": []}'></textarea>
    </p>
    <p>
      <label for="plain-password">Password</label>
      <input id="plain-password" v-model="plainPassword" :type="showPlainPassword ? 'text' : 'password'" autocomplete="new-password" />
      <label><input type="checkbox" v-model="showPlainPassword" /> Show password</label>
    </p>
    <p>
      <label for="plain-confirm">Password again</label>
      <input id="plain-confirm" v-model="plainConfirm" :type="showPlainPassword ? 'text' : 'password'" autocomplete="new-password" />
    </p>
    <p><button type="button" @click="onEncrypt">Encrypt this pack</button></p>
    <p v-if="encryptError" class="error">{{ encryptError }}</p>
    <div v-if="encryptedOutput">
      <label for="encrypted-output">Encrypted pack</label>
      <textarea id="encrypted-output" :value="encryptedOutput" rows="10" readonly></textarea>
      <p>
        <button type="button" @click="copyText(encryptedOutput)">Copy encrypted pack</button>
        <button type="button" @click="download(encryptedOutput, encryptFileName)">Download encrypted pack</button>
      </p>
    </div>

    <h2>Decrypt an encrypted pack, to check it</h2>
    <p>
      <label for="encrypted-file">Encrypted pack file, or paste below</label>
      <input id="encrypted-file" type="file" accept=".json,application/json" @change="onEncryptedFile" />
    </p>
    <p>
      <label for="encrypted-text">Encrypted pack JSON</label>
      <textarea id="encrypted-text" v-model="encryptedText" rows="10" placeholder='{"format": "open-bookmarks/encrypted/1.0", "salt": "...", "iv": "...", "ciphertext": "..."}'></textarea>
    </p>
    <p>
      <label for="decrypt-password">Password</label>
      <input id="decrypt-password" v-model="decryptPassword" :type="showDecryptPassword ? 'text' : 'password'" autocomplete="current-password" />
      <label><input type="checkbox" v-model="showDecryptPassword" /> Show password</label>
    </p>
    <p><button type="button" @click="onDecrypt">Decrypt this pack</button></p>
    <p v-if="decryptError" class="error">{{ decryptError }}</p>
    <div v-if="plainOutput">
      <label for="plain-output">Decrypted plain pack</label>
      <textarea id="plain-output" :value="plainOutput" rows="10" readonly></textarea>
      <p>
        <button type="button" @click="copyText(plainOutput)">Copy plain pack</button>
        <button type="button" @click="download(plainOutput, 'pack-decrypted.json')">Download plain pack</button>
      </p>
    </div>
  </div>
</template>

<style scoped>
.encrypt-tool label {
  display: block;
  font-weight: 600;
  margin: 12px 0 4px;
}
.encrypt-tool textarea,
.encrypt-tool input[type="text"],
.encrypt-tool input[type="password"] {
  width: 100%;
  box-sizing: border-box;
  padding: 8px;
  border: 1px solid var(--vp-c-divider, #ccc);
  border-radius: 6px;
  font-family: monospace;
}
.encrypt-tool button {
  padding: 8px 14px;
  margin-right: 8px;
  border: 1px solid var(--vp-c-divider, #ccc);
  border-radius: 6px;
  background: var(--vp-c-brand-soft, #eee);
  cursor: pointer;
}
.encrypt-tool .error {
  color: #b00020;
  font-weight: 600;
}
</style>
