export function escapeHtml(text = '') {
  return String(text)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;')
}

function renderInline(text = '') {
  let html = escapeHtml(text)

  // **加粗**
  html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')

  return html
}

function isBulletLine(line) {
  return /^\s*-\s+/.test(line)
}

function isOrderedLine(line) {
  return /^\s*\d+\.\s+/.test(line)
}

function stripBullet(line) {
  return line.replace(/^\s*-\s+/, '').trim()
}

function stripOrdered(line) {
  return line.replace(/^\s*\d+\.\s+/, '').trim()
}

export function renderLightMarkdown(content = '') {
  const source = String(content || '').replace(/\r\n/g, '\n').trim()
  if (!source) return ''

  const lines = source.split('\n')
  const blocks = []

  let i = 0
  while (i < lines.length) {
    const line = lines[i].trim()

    if (!line) {
      i += 1
      continue
    }

    // 无序列表
    if (isBulletLine(lines[i])) {
      const items = []
      while (i < lines.length && isBulletLine(lines[i])) {
        items.push(`<li>${renderInline(stripBullet(lines[i]))}</li>`)
        i += 1
      }
      blocks.push(`<ul>${items.join('')}</ul>`)
      continue
    }

    // 有序列表
    if (isOrderedLine(lines[i])) {
      const items = []
      while (i < lines.length && isOrderedLine(lines[i])) {
        items.push(`<li>${renderInline(stripOrdered(lines[i]))}</li>`)
        i += 1
      }
      blocks.push(`<ol>${items.join('')}</ol>`)
      continue
    }

    // 普通段落：收集到空行或列表前为止
    const paragraphLines = []
    while (
      i < lines.length &&
      lines[i].trim() &&
      !isBulletLine(lines[i]) &&
      !isOrderedLine(lines[i])
    ) {
      paragraphLines.push(lines[i].trim())
      i += 1
    }

    const paragraphText = paragraphLines.join('<br>')
    blocks.push(`<p>${renderInline(paragraphText)}</p>`)
  }

  return blocks.join('')
}
