#!/usr/bin/env node
/**
 * Build-time image fetcher for Séptima Ola React press kit.
 *
 * Downloads images from Google Drive CDN to public/images/ for local serving.
 * Run via: npm run fetch:images
 * Auto-runs before dev/build via predev/prebuild hooks.
 */

import { writeFile, mkdir, access } from 'node:fs/promises'
import { createWriteStream } from 'node:fs'
import { pipeline } from 'node:stream/promises'
import { fileURLToPath } from 'node:url'
import { dirname, join } from 'node:path'

const __filename = fileURLToPath(import.meta.url)
const __dirname = dirname(__filename)

const FORCE = process.argv.includes('--force')

const manifest = {
  members: [
    { slug: 'alfred', id: '1NLXEkoOz8CcVXXAFOMoCwttNoPVw7t35' },
    { slug: 'lemanu', id: '1vZxL4byBgKMExxKbakuZhEgQ2hsFDPVY' },
    { slug: 'levisax', id: '1kh42JDOOif795zfIgig1c3THcWXdvsYq' },
    { slug: 'rodrigo', id: '1EXP5Kh_RfxbQLrNVMUn7-Fygg1LrC7Xw' },
    { slug: 'sandy', id: '1EfbO0_BJL924CbnvjxfwbDaUj6Vo3uhp' },
    { slug: 'arthur', id: '10nWFvuwRtm_hR9LMtT5SmwRO5NCWey30' },
  ],
  gallery: [
    { slug: 'photo-1', id: '17NlhB47l-1RD9mlxM9hJpMwvSz1g8UEb' },
    { slug: 'photo-2', id: '1LmL-xTYYOU-jf1WVThT4N3Y9vLytwvWy' },
  ],
}

const BASE_DIR = join(__dirname, '..')
const IMAGES_DIR = join(BASE_DIR, 'public', 'images')

const MAX_RETRIES = 3
const RETRY_DELAYS = [1000, 2000, 4000]

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms))

const formatBytes = (bytes) => {
  if (bytes < 1024) return `${bytes}B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)}KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)}MB`
}

const exists = async (path) => {
  try {
    await access(path)
    return true
  } catch {
    return false
  }
}

const downloadWithRetry = async (url, destPath, required = true) => {
  const filename = destPath.split('/').pop()

  if (!FORCE && (await exists(destPath))) {
    console.log(`  ✓ ${filename} (cached)`)
    return { success: true, cached: true }
  }

  let lastError

  for (let attempt = 0; attempt < MAX_RETRIES; attempt++) {
    try {
      const response = await fetch(url, {
        headers: {
          'User-Agent': 'Mozilla/5.0 (compatible; SeptimaOla-Fetch/1.0)',
        },
      })

      if (!response.ok) {
        if (response.status === 429) {
          throw new Error('Rate limited (429)')
        }
        throw new Error(`HTTP ${response.status}`)
      }

      await mkdir(dirname(destPath), { recursive: true })

      const contentLength = parseInt(response.headers.get('content-length') || '0', 10)
      await pipeline(response.body, createWriteStream(destPath))

      const size = contentLength > 0 ? ` (${formatBytes(contentLength)})` : ''
      console.log(`  ↓ ${filename}${size}`)
      return { success: true, cached: false }
    } catch (err) {
      lastError = err
      const isRetryable =
        err.message.includes('429') ||
        err.message.includes('ETIMEDOUT') ||
        err.message.includes('ECONNRESET') ||
        err.message.includes('fetch failed')

      if (isRetryable && attempt < MAX_RETRIES - 1) {
        const delay = RETRY_DELAYS[attempt] || RETRY_DELAYS[RETRY_DELAYS.length - 1]
        console.log(`  ⏳ ${filename} (attempt ${attempt + 1} failed: ${err.message}, retrying in ${delay}ms)`)
        await sleep(delay)
      }
    }
  }

  console.log(`  ✗ ${filename} (failed after ${MAX_RETRIES} retries: ${lastError.message})`)
  return { success: false, error: lastError, required }
}

const main = async () => {
  console.log('📸 Fetching images from Google Drive...\n')

  let requiredFailed = 0
  let optionalFailed = 0

  console.log('Members (required):')
  for (const member of manifest.members) {
    const url = `https://lh3.googleusercontent.com/d/${member.id}=w800-h800-c`
    const destPath = join(IMAGES_DIR, 'members', `${member.slug}.jpg`)
    const result = await downloadWithRetry(url, destPath, true)
    if (!result.success) requiredFailed++
  }

  console.log('\nGallery (optional):')
  for (const photo of manifest.gallery) {
    const url = `https://lh3.googleusercontent.com/d/${photo.id}=w1600-h1200-c`
    const destPath = join(IMAGES_DIR, 'gallery', `${photo.slug}.jpg`)
    const result = await downloadWithRetry(url, destPath, false)
    if (!result.success) optionalFailed++
  }

  console.log('')

  if (requiredFailed > 0) {
    console.error(`❌ ${requiredFailed} required member image(s) failed to download`)
    process.exit(1)
  }

  if (optionalFailed > 0) {
    console.warn(`⚠️  ${optionalFailed} optional gallery image(s) failed (continuing anyway)`)
  }

  console.log('✅ Done\n')
}

main().catch((err) => {
  console.error('Fatal error:', err)
  process.exit(1)
})
