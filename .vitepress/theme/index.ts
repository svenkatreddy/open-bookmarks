import DefaultTheme from 'vitepress/theme'
import EncryptTool from './components/EncryptTool.vue'

export default {
  extends: DefaultTheme,
  enhanceApp({ app }) {
    app.component('EncryptTool', EncryptTool)
  },
}
