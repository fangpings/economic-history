import { readFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import { defineConfig } from 'vitepress'

const curriculum = JSON.parse(readFileSync(fileURLToPath(new URL('../../curriculum.json', import.meta.url)), 'utf8'))

// Use word segmentation for Chinese phrases and preserve English tickers/acronyms.
// The function is serialized by VitePress and runs in both indexing and querying.
function tokenize(text: string) {
  return Array.from(new Intl.Segmenter('zh-CN', { granularity: 'word' }).segment(text))
    .filter(part => part.isWordLike)
    .map(part => part.segment)
}

export default defineConfig({
  base: '/economic-history/',
  lang: 'zh-CN',
  title: '战后经济与金融史',
  description: '从布雷顿森林到2024年 · 国际与中国双线 · 六十章教材',
  rewrites: { 'README.md': 'index.md' },
  markdown: {
    config(md) {
      const renderLink = md.renderer.rules.link_open
      md.renderer.rules.link_open = (tokens, index, options, env, self) => {
        const href = tokens[index].attrGet('href')
        if (href === './README.html' || href === 'README.html' || href === 'README.md') {
          tokens[index].attrSet('href', './')
        }
        return renderLink ? renderLink(tokens, index, options, env, self) : self.renderToken(tokens, index, options)
      }
    }
  },
  themeConfig: {
    siteTitle: '战后经济与金融史',
    nav: [
      { text: '全书目录', link: '/' },
      { text: '开始阅读', link: '/01-interwar-origins' },
      { text: 'GitHub', link: 'https://github.com/fangpings/economic-history' }
    ],
    sidebar: [
      { text: '阅读入口', items: [{ text: '全书目录', link: '/' }] },
      ...curriculum.parts.map((part: { number: number; title: string }) => ({
        text: `第${part.number}篇 · ${part.title}`,
        collapsed: true,
        items: curriculum.chapters.filter((c: { part: number }) => c.part === part.number)
          .map((c: { number: number; title: string; file: string }) => ({
            text: `${String(c.number).padStart(2, '0')} ${c.title}`,
            link: `/${c.file.replace(/\.md$/, '')}`
          }))
      }))
    ],
    outline: { level: [2, 3], label: '本页目录' },
    docFooter: { prev: '上一节', next: '下一节' },
    sidebarMenuLabel: '章节目录',
    darkModeSwitchLabel: '切换外观',
    lightModeSwitchTitle: '切换为浅色',
    darkModeSwitchTitle: '切换为深色',
    returnToTopLabel: '回到顶部',
    search: {
      provider: 'local',
      options: {
        miniSearch: { options: { tokenize } },
        translations: {
          button: { buttonText: '搜索教材', buttonAriaLabel: '搜索教材' },
          modal: {
            displayDetails: '显示详情',
            resetButtonTitle: '清除搜索',
            backButtonTitle: '返回',
            noResultsText: '没有找到相关内容',
            footer: { selectText: '选择', navigateText: '切换', closeText: '关闭' }
          }
        }
      }
    }
  }
})
