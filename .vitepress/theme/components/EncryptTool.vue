<script setup>
import { ref } from 'vue'
import { encryptPack, decryptPack } from '../../../lib/js/encrypt.mjs'
import { validatePack } from '../../../lib/js/open-bookmarks.mjs'

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
const encryptBusy = ref(false)
const decryptBusy = ref(false)
let encryptRequestId = 0
let decryptRequestId = 0

async function onEncrypt() {
  const requestId = ++encryptRequestId
  encryptBusy.value = true
  encryptError.value = ''
  encryptedOutput.value = ''
  let pack
  try {
    pack = JSON.parse(plainText.value)
  } catch {
    encryptError.value = 'That is not valid JSON.'
    encryptBusy.value = false
    return
  }
  const validationErrors = validatePack(pack)
  if (validationErrors.length) {
    encryptError.value = 'Pack is not valid: ' + validationErrors.join('; ')
    encryptBusy.value = false
    return
  }
  if (!plainPassword.value) {
    encryptError.value = 'Enter a password.'
    encryptBusy.value = false
    return
  }
  if (plainPassword.value !== plainConfirm.value) {
    encryptError.value = 'The two passwords do not match.'
    encryptBusy.value = false
    return
  }
  try {
    const envelope = await encryptPack(pack, plainPassword.value)
    if (requestId !== encryptRequestId) return
    encryptedOutput.value = JSON.stringify(envelope, null, 2)
    const slug = pack.title.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '') || 'pack'
    encryptFileName.value = slug + '-encrypted.json'
  } catch {
    if (requestId !== encryptRequestId) return
    encryptError.value = 'Encryption failed in this browser. Try a browser with Web Crypto support.'
  } finally {
    if (requestId === encryptRequestId) encryptBusy.value = false
  }
}

async function onDecrypt() {
  const requestId = ++decryptRequestId
  decryptBusy.value = true
  decryptError.value = ''
  plainOutput.value = ''
  let encrypted
  try {
    encrypted = JSON.parse(encryptedText.value)
  } catch {
    decryptError.value = 'That is not valid JSON.'
    decryptBusy.value = false
    return
  }
  if (!decryptPassword.value) {
    decryptError.value = 'Enter a password.'
    decryptBusy.value = false
    return
  }
  try {
    const pack = await decryptPack(encrypted, decryptPassword.value)
    const validationErrors = validatePack(pack)
    if (validationErrors.length) {
      if (requestId !== decryptRequestId) return
      decryptError.value = 'Decrypted pack is not a valid plain pack: ' + validationErrors.join('; ')
      return
    }
    if (requestId !== decryptRequestId) return
    plainOutput.value = JSON.stringify(pack, null, 2)
  } catch (error) {
    if (requestId !== decryptRequestId) return
    decryptError.value = error && error.message ? error.message : 'Decryption failed. Invalid password or corrupted payload'
  } finally {
    if (requestId === decryptRequestId) decryptBusy.value = false
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
    <p><button type="button" @click="onEncrypt" :disabled="encryptBusy">Encrypt this pack</button></p>
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
    <p><button type="button" @click="onDecrypt" :disabled="decryptBusy">Decrypt this pack</button></p>
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
