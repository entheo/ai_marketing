<template>
  <div class="page-shell">
    <div class="page-container report-page">
      <div class="report-head">
        <div class="ui-eyebrow">梳理结果</div>

        <h1 class="ui-title">
          这是你当前阶段最接近自己的整理结果。
        </h1>

        <p class="ui-subtitle">
          它不是标签，也不是结论，而是你此刻最值得认真对待的一版理解。
        </p>
      </div>

      <div class="ui-card ui-report-box ui-report-box-lg report-main-card">
        {{ reportText }}
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'SelfValueReport',

  data() {
    return {
      reportText: '正在加载报告…'
    }
  },

  methods: {
    async fetchReport() {
      const reportId = this.$route.query.id

      if (!reportId) {
        this.reportText = this.$store.getters.self_value_report || '暂无报告内容'
        return
      }

      try {
        const response = await fetch(`http://127.0.0.1:8002/api/selfvalue/report/${reportId}/`)
        const data = await response.json()

        if (!response.ok) {
          throw new Error(data.error || '读取报告失败')
        }

        this.reportText = data.report_text || '暂无报告内容'
      } catch (error) {
        this.reportText = `读取报告失败：${error.message}`
      }
    }
  },

  mounted() {
    this.fetchReport()
  }
}
</script>

<style scoped>
.report-page {
  max-width: 820px;
}

.report-head {
  margin-bottom: 28px;
}

.report-main-card {
  padding: 28px;
}

@media (max-width: 768px) {
  .report-main-card {
    padding: 20px;
  }
}
</style>
