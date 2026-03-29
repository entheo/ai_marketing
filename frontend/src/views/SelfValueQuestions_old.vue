<template>
  <div class="questions-page" :class="{ 'questions-page--thinking': isQuestionBusy }">
    <div class="questions-page-bg questions-bg-a"></div>
    <div class="questions-page-bg questions-bg-b"></div>

    <div class="questions-shell">
      <div class="questions-container">
        <section v-if="interactionMode === 'ask'" class="questions-main">
          <div class="question-stage">
            <div class="question-title-wrap" :class="{ 'question-title-wrap--thinking': isQuestionBusy }">
              <h1 class="questions-title" :class="questionVisualSizeClass">
                <template v-if="requestingQuestion && !hasAnyStreamedQuestion">
                  <span class="gray">思考…</span><span class="thinking-caret"></span>
                </template>

                <template v-else-if="hasAnyStreamedQuestion">
                  <span>{{ streamedQuestionStableText }}</span>
                  <span
                    v-if="streamedQuestionPendingChar"
                    class="stream-char"
                  >{{ streamedQuestionPendingChar }}</span>
                  <span class="thinking-caret"></span>
                </template>

                <template v-else>
                  {{ currentQuestion || '' }}
                </template>
              </h1>

              <p v-if="!loading" class="questions-hint">
                {{ questionHintText }}
              </p>
            </div>

            <div v-if="loading" class="questions-status">
              正在请求问题……
            </div>
          </div>

          <div class="answer-stage">
            <div
              class="question-answer-area"
              :class="{ 'question-answer-area--thinking': isAnswerDimmed }"
            >
              <div
                v-if="questionType === 'text'"
                class="question-breath-wrap question-input-wrap"
              >
                <textarea
                  v-model="answerText"
                  class="question-textarea"
                  placeholder="在这里慢慢写下你的想法。"
                  :disabled="isQuestionBusy || !answerRevealReady"
                ></textarea>
              </div>

              <div
                v-else-if="questionType === 'single_choice'"
                class="question-breath-wrap question-options-wrap"
              >
                <div class="question-options">
                  <label
                    v-for="(option, index) in questionOptions"
                    :key="index"
                    class="question-option"
                    :class="{ 'question-option--active': selectedOption === option }"
                  >
                    <input
                      v-model="selectedOption"
                      type="radio"
                      name="question-option"
                      :value="option"
                      :disabled="isQuestionBusy || !answerRevealReady"
                    />
                    <span>{{ option }}</span>
                  </label>
                </div>
              </div>
            </div>
          </div>
        </section>

        <div
          v-if="interactionMode === 'ask' && showSummarizeButton"
          class="question-side-link-row question-side-link-row--intro"
        >
          <button
            class="question-side-link"
            type="button"
            :disabled="isQuestionBusy || !answerRevealReady"
            @click="summarizeNow"
          >
            <span class="question-side-link__icon" aria-hidden="true">
              <svg viewBox="0 0 20 20" fill="none">
                <path
                  d="M6 4.5h5.8L15 7.7V15a1 1 0 0 1-1 1H6a1 1 0 0 1-1-1v-9.5a1 1 0 0 1 1-1Z"
                  stroke="currentColor"
                  stroke-width="1.4"
                  stroke-linejoin="round"
                />
                <path
                  d="M11.8 4.5v2.2a1 1 0 0 0 1 1H15"
                  stroke="currentColor"
                  stroke-width="1.4"
                  stroke-linejoin="round"
                />
                <path
                  d="M7.5 10h5M7.5 12.8h4"
                  stroke="currentColor"
                  stroke-width="1.4"
                  stroke-linecap="round"
                />
              </svg>
            </span>
            <span class="question-side-link__text">暂时聊到这里，总结一下</span>
          </button>
        </div>

        <section
          v-else-if="interactionMode === 'stage_transition'"
          class="questions-main questions-main--transition"
        >
          <div class="transition-stage">
            <div class="report-hero">
              <h1 class="questions-title questions-title--medium report-title">
                根据当前的对话，整理出此时你的理解。
              </h1>

              <p class="questions-hint report-hint">
                这不是结束，是先把已经浮出来的东西看清楚
              </p>
            </div>
          </div>

          <div class="transition-panel-wrap">
            <div class="transition-panel">
              正在整理,请稍等…<span class="thinking-caret"></span>
            </div>
          </div>
        </section>

        <section v-else-if="interactionMode === 'draft_report'" class="report-page">
          <div class="report-topline">
            <div class="questions-kicker questions-kicker--soft">''</div>
          </div>

          <div class="report-hero">
            <h1 class="questions-title questions-title--medium report-title">
              目前的阶段性发现
            </h1>
            
            <!--
            <p class="report-subtitle">
              可以随时继续深入，也可以先留在这里
            </p>
            -->

          </div>

          <div class="report-stack">
            <section class="report-card report-card--primary">
              <div class="report-card-head">
                <div class="report-card-kicker">- 当前理解 -</div>
              </div>
              
              <div class="report-card-body report-main-content">
                <LightMarkdownBlock :content="draftReportMain" />
              </div>

            </section>

            <section v-if="draftReportNextAction" class="report-card report-card--secondary">
              <div class="report-card-head">
                <div class="report-card-kicker">- 下一步建议 -</div>
              </div>
              <div class="report-card-body report-next-content">
                <LightMarkdownBlock :content="draftReportNextAction"/>
              </div>
            </section>
          </div>

          <div class="questions-actions questions-actions--draft report-actions">
            <button
              class="question-btn question-btn--ghost"
              type="button"
              :disabled="isQuestionBusy"
              @click="continueDeeper"
            >
              继续深入
            </button>
            <button
              class="question-btn question-btn--solid"
              type="button"
              :disabled="isQuestionBusy"
              @click="acceptDraftReport"
            >
              {{ isQuestionBusy ? '正在整理…' : '保留这一版' }}
            </button>
          </div>
        </section>

        <div v-if="errorMessage" class="questions-error">
          {{ errorMessage }}
        </div>

        <div
          v-if="interactionMode === 'ask'"
          class="questions-actions"
          :class="{ 'questions-actions--thinking': isAnswerDimmed }"
        >
          <button
            class="question-btn question-btn--ghost"
            type="button"
            :disabled="isQuestionBusy || !answerRevealReady"
            @click="goBack"
          >
            返回上一页
          </button>

          <button
            class="question-btn question-btn--solid"
            type="button"
            :disabled="isQuestionBusy || !answerRevealReady"
            @click="goNext"
          >
            {{ requestingQuestion ? '正在整理…' : '下一步' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import LightMarkdownBlock from '@/components/LightMarkdownBlock.vue'

export default {
  name: 'SelfValueQuestions',

  data() {
    return {
      loading: true,
      errorMessage: '',
      currentQuestion: '',
      currentQuestionLengthHint: 'medium',
      questionType: 'text',
      questionOptions: [],
      answerText: '',
      selectedOption: '',
      qaHistory: [],
      round: 1,
      interactionMode: 'ask',
      draftReport: '',
      draftReportMain: '',
      draftReportNextAction: '',
      questionRenderKey: 0,

      canSummarize: false,

      lockedStreamingLengthHint: '',

      requestingQuestion: false,
      playingQuestion: false,
      savingDraftReport: false,
      requestingSummary: false,

      answerRevealReady: false,
      answerRevealTimer: null,

      rawAskBuffer: '',
      targetQuestionText: '',
      targetQuestionLengthHint: 'medium',
      askStreamComplete: false,
      streamedQuestionStableText: '',
      streamedQuestionPendingChar: '',
      playbackRafId: null,
      playbackLastTs: 0,
      playbackAccumulator: 0
    }
  },
  components:{
      LightMarkdownBlock
      },

  computed: {
    prefetchedFirstQuestion() {
      return this.$store.state.first_question_data
    },

    prefetchedFirstQuestionReady() {
      return this.$store.state.first_question_ready
    },

    isQuestionBusy() {
      return (
        this.requestingQuestion ||
        this.playingQuestion ||
        this.savingDraftReport ||
        this.requestingSummary
      )
    },

    isAnswerDimmed() {
      return this.isQuestionBusy || !this.answerRevealReady
    },

    hasAnyStreamedQuestion() {
      return !!(this.streamedQuestionStableText || this.streamedQuestionPendingChar)
    },

    activeQuestionText() {
      if (this.hasAnyStreamedQuestion) {
        return this.targetQuestionText || (this.streamedQuestionStableText + this.streamedQuestionPendingChar)
      }
      return this.currentQuestion || ''
    },

    activeQuestionLengthHint() {
      if (this.lockedStreamingLengthHint) {
        return this.lockedStreamingLengthHint
      }
      return this.currentQuestionLengthHint || this.inferQuestionLengthHint(this.activeQuestionText)
    },

    questionVisualSizeClass() {
      const hint = this.activeQuestionLengthHint
      if (hint === 'long') return 'questions-title--long'
      if (hint === 'short') return 'questions-title--short'
      return 'questions-title--medium'
    },

    questionHintText() {
      if (this.isQuestionBusy) {
        return ''
      }
      return '从你此刻最有感觉，最舒服的地方开始就可以'
    },

    showSummarizeButton() {
      return (
        this.interactionMode === 'ask' &&
        this.answerRevealReady &&
        !this.isQuestionBusy &&
        this.round >= 4 &&
        this.canSummarize
      )
    }
  },

  methods: {
    inferQuestionLengthHint(text) {
      const len = String(text || '').trim().length
      if (len <= 20) return 'short'
      if (len <= 30) return 'medium'
      return 'long'
    },

    clearAnswerRevealTimer() {
      if (this.answerRevealTimer) {
        clearTimeout(this.answerRevealTimer)
        this.answerRevealTimer = null
      }
    },

    delayAnswerReveal() {
      this.clearAnswerRevealTimer()
      this.answerRevealReady = false
      this.answerRevealTimer = setTimeout(() => {
        this.answerRevealReady = true
        this.answerRevealTimer = null
      }, 220)
    },

    bindQuestionMeta(data, fallbackQuestion = '') {
      const finalQuestion = data.question || fallbackQuestion || ''
      this.currentQuestion = finalQuestion
      this.currentQuestionLengthHint =
        data.question_length_hint || this.inferQuestionLengthHint(finalQuestion)

      const nextType = this.normalizeQuestionType(data.question_type)
      const nextOptions = Array.isArray(data.options) ? data.options : []

      this.answerText = ''
      this.selectedOption = ''

      this.questionType = nextType
      this.questionOptions = nextOptions
      this.canSummarize = !!data.can_summarize
      this.questionRenderKey += 1
    },

    applyFirstQuestion(data) {
      this.loading = false
      this.errorMessage = ''
      this.interactionMode = 'ask'

      const firstQuestion = data.question || '未返回问题内容'
      this.bindQuestionMeta(data, firstQuestion)

      this.playLocalQuestion(
        firstQuestion,
        data.question_length_hint || this.inferQuestionLengthHint(firstQuestion)
      )
    },

    playLocalQuestion(questionText, lengthHint = '') {
      this.resetAskStreamingState()
      this.answerRevealReady = false
      this.requestingQuestion = false
      this.playingQuestion = true
      this.targetQuestionText = questionText || ''
      this.targetQuestionLengthHint = lengthHint || this.inferQuestionLengthHint(questionText)
      this.lockedStreamingLengthHint = this.targetQuestionLengthHint || 'medium'
      this.askStreamComplete = true
      this.ensurePlaybackRunning()
    },

    goBack() {
      if (this.isQuestionBusy || !this.answerRevealReady) return
      this.$router.back()
    },

    normalizeQuestionType(questionType) {
      return questionType === 'single_choice' ? 'single_choice' : 'text'
    },

    getCurrentAnswer() {
      return this.questionType === 'single_choice'
        ? this.selectedOption
        : this.answerText.trim()
    },

    validateCurrentAnswer(answer) {
      if (this.questionType === 'single_choice') {
        return !!answer
      }
      return !!String(answer || '').trim()
    },

    extractQuestionFromBuffer(raw) {
      const marker = '"question"'
      const markerIndex = raw.indexOf(marker)
      if (markerIndex === -1) return ''

      const colonIndex = raw.indexOf(':', markerIndex)
      if (colonIndex === -1) return ''

      const firstQuoteIndex = raw.indexOf('"', colonIndex)
      if (firstQuoteIndex === -1) return ''

      let result = ''
      let escaped = false

      for (let i = firstQuoteIndex + 1; i < raw.length; i += 1) {
        const ch = raw[i]

        if (escaped) {
          if (ch === 'n') result += '\n'
          else if (ch === 't') result += '\t'
          else if (ch === 'r') result += '\r'
          else result += ch
          escaped = false
          continue
        }

        if (ch === '\\') {
          escaped = true
          continue
        }

        if (ch === '"') {
          return result
        }

        result += ch
      }

      return result
    },

    getBuiltLength() {
      return this.streamedQuestionStableText.length + this.streamedQuestionPendingChar.length
    },

    getNextChunkSize(currentChar) {
      if (/[，。！？；：,.!?;:]/.test(currentChar)) return 1
      return 2
    },

    getStepDelay(chunkText) {
      return /[，。！？；：,.!?;:]/.test(chunkText) ? 190 : 85
    },

    promotePendingChar() {
      if (this.streamedQuestionPendingChar) {
        this.streamedQuestionStableText += this.streamedQuestionPendingChar
        this.streamedQuestionPendingChar = ''
      }
    },

    takeNextChunk(text, startIndex) {
      const rest = text.slice(startIndex)
      if (!rest) return ''
      const firstChar = rest[0]
      const size = this.getNextChunkSize(firstChar)
      return rest.slice(0, size)
    },

    tickQuestionPlayback(timestamp) {
      if (!this.playbackLastTs) {
        this.playbackLastTs = timestamp
      }

      const delta = timestamp - this.playbackLastTs
      this.playbackLastTs = timestamp
      this.playbackAccumulator += delta

      let builtLength = this.getBuiltLength()

      while (builtLength < this.targetQuestionText.length) {
        const nextChunk = this.takeNextChunk(this.targetQuestionText, builtLength)
        if (!nextChunk) break

        const neededDelay = this.getStepDelay(nextChunk)
        if (this.playbackAccumulator < neededDelay) break

        this.playbackAccumulator -= neededDelay
        this.promotePendingChar()
        this.streamedQuestionPendingChar = nextChunk
        builtLength = this.getBuiltLength()

        if (/[，。！？；：,.!?;:]$/.test(nextChunk)) break
      }

      if (this.getBuiltLength() < this.targetQuestionText.length || !this.askStreamComplete) {
        this.playbackRafId = window.requestAnimationFrame(this.tickQuestionPlayback)
        return
      }

      this.finishAskStreaming()
    },

    ensurePlaybackRunning() {
      if (this.playbackRafId) return
      this.playbackRafId = window.requestAnimationFrame(this.tickQuestionPlayback)
    },

    finishAskStreaming() {
      if (this.playbackRafId) {
        window.cancelAnimationFrame(this.playbackRafId)
        this.playbackRafId = null
      }

      this.promotePendingChar()
      this.playbackLastTs = 0
      this.playbackAccumulator = 0
      this.requestingQuestion = false
      this.playingQuestion = false
      this.rawAskBuffer = ''
      this.targetQuestionText = ''
      this.targetQuestionLengthHint = 'medium'
      this.askStreamComplete = false
      this.streamedQuestionStableText = ''
      this.streamedQuestionPendingChar = ''

      this.delayAnswerReveal()
    },

    resetAskStreamingState() {
      if (this.playbackRafId) {
        window.cancelAnimationFrame(this.playbackRafId)
        this.playbackRafId = null
      }

      this.lockedStreamingLengthHint = ''
      this.rawAskBuffer = ''
      this.targetQuestionText = ''
      this.targetQuestionLengthHint = 'medium'
      this.askStreamComplete = false
      this.streamedQuestionStableText = ''
      this.streamedQuestionPendingChar = ''
      this.playbackLastTs = 0
      this.playbackAccumulator = 0
      this.playingQuestion = false
      this.clearAnswerRevealTimer()
    },

    applyAskResult(data) {
      const finalQuestion =
        data.question ||
        this.targetQuestionText ||
        (this.streamedQuestionStableText + this.streamedQuestionPendingChar) ||
        '未返回问题内容'

      this.interactionMode = 'ask'
      this.bindQuestionMeta(data, finalQuestion)
      this.round += 1

      this.targetQuestionText = finalQuestion
      this.targetQuestionLengthHint =
        data.question_length_hint || this.inferQuestionLengthHint(finalQuestion)

      if (!this.lockedStreamingLengthHint) {
        this.lockedStreamingLengthHint = this.targetQuestionLengthHint || 'medium'
      }

      this.currentQuestionLengthHint = this.lockedStreamingLengthHint
      this.askStreamComplete = true
      this.playingQuestion = true
      this.answerRevealReady = false
      this.ensurePlaybackRunning()
    },

    splitDraftReport(data) {
      const summaryText = String(data.summary || '').trim()
      const reportText = String(data.report || '').trim()
      const nextActionText = String(data.next_action || '').trim()

      let mainText = reportText || summaryText || ''
      let nextText = nextActionText || ''

      if (!mainText && nextText) {
        mainText = nextText
        nextText = ''
      }

      if (!mainText) {
        mainText = '这一轮已经形成了一些线索，但当前返回内容还不够完整。'
      }

      return {
        main: mainText,
        next: nextText
      }
    },

    applyDraftReportResult(data) {
      const parts = this.splitDraftReport(data)
      this.draftReport = parts.main
      this.draftReportMain = parts.main
      this.draftReportNextAction = parts.next
      this.interactionMode = 'draft_report'
      this.requestingSummary = false
      this.answerRevealReady = true
      this.resetAskStreamingState()
    },

    handleStreamPayload(payload) {
      if (payload.event === 'error') {
        throw new Error(payload.message || '流式生成失败')
      }

      if (payload.event === 'chunk') {
        this.rawAskBuffer += payload.content || ''
        const partialQuestion = this.extractQuestionFromBuffer(this.rawAskBuffer)

        if (partialQuestion && partialQuestion.length > this.targetQuestionText.length) {
          this.targetQuestionText = partialQuestion
          this.playingQuestion = true
          this.ensurePlaybackRunning()
        }
        return
      }

      if (payload.event === 'done') {
        const data = payload.data || {}
        const status = data.status || ''

        if (status === 'ask' || status === 'clarify') {
          this.applyAskResult(data)
          return
        }

        if (
          status === 'stage_summary' ||
          status === 'final_report' ||
          status === 'draft_report' ||
          status === 'action_plan'
        ) {
          this.applyDraftReportResult(data)
          return
        }

        throw new Error(`未识别的返回状态: ${status || 'empty'}`)
      }
    },

    async readNdjsonStream(response) {
      const reader = response.body.getReader()
      const decoder = new TextDecoder('utf-8')
      let buffer = ''

      let done = false
      while (!done) {
        const result = await reader.read()
        done = result.done
        const value = result.value

        if (value) {
          buffer += decoder.decode(value, { stream: !done })
        }

        const lines = buffer.split('\n')
        buffer = lines.pop() || ''

        for (const line of lines) {
          if (!line.trim()) continue
          const payload = JSON.parse(line)
          this.handleStreamPayload(payload)
        }

        if (done) break
      }

      if (buffer.trim()) {
        const payload = JSON.parse(buffer.trim())
        this.handleStreamPayload(payload)
      }
    },

    async fetchFirstQuestion() {
      this.loading = true
      this.errorMessage = ''

      try {
        const response = await fetch('http://127.0.0.1:8002/api/advice/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            type: 'self_value',
            mode: 'self_value',
            stage: 'start'
          })
        })

        const data = await response.json()

        if (!response.ok) {
          throw new Error(data.error || '请求失败')
        }

        this.applyFirstQuestion(data)
      } catch (error) {
        this.errorMessage = `获取第一题失败：${error.message}`
      } finally {
        this.loading = false
      }
    },

    async goNext() {
      if (this.isQuestionBusy || !this.answerRevealReady) return

      const currentAnswer = this.getCurrentAnswer()

      if (!this.validateCurrentAnswer(currentAnswer)) {
        this.errorMessage = this.questionType === 'single_choice'
          ? '请先选择一个选项。'
          : '请先输入你的回答。'
        return
      }

      this.requestingQuestion = true
      this.playingQuestion = false
      this.answerRevealReady = false
      this.errorMessage = ''
      this.resetAskStreamingState()

      this.lockedStreamingLengthHint = 'medium'

      this.qaHistory.push({
        round: this.round,
        question: this.currentQuestion,
        type: this.questionType,
        options: this.questionType === 'single_choice' ? [...this.questionOptions] : [],
        answer: currentAnswer
      })

      try {
        const response = await fetch('http://127.0.0.1:8002/api/advice/stream/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            type: 'self_value',
            mode: 'self_value',
            stage: 'continue',
            answer: currentAnswer,
            round: this.round,
            qa_history: this.qaHistory
          })
        })

        if (!response.ok || !response.body) {
          throw new Error('流式请求失败')
        }

        await this.readNdjsonStream(response)
      } catch (error) {
        this.errorMessage = `获取下一题失败：${error.message}`
        this.finishAskStreaming()
      }
    },

    async summarizeNow() {
      if (this.isQuestionBusy || !this.answerRevealReady || !this.canSummarize) return

      this.requestingSummary = true
      this.errorMessage = ''
      this.interactionMode = 'stage_transition'

      try {
        const response = await fetch('http://127.0.0.1:8002/api/advice/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            type: 'self_value',
            mode: 'self_value',
            stage: 'summarize',
            round: this.round,
            qa_history: this.qaHistory
          })
        })

        const data = await response.json()

        if (!response.ok) {
          throw new Error(data.error || '生成阶段整理失败')
        }

        this.applyDraftReportResult(data)
      } catch (error) {
        this.requestingSummary = false
        this.interactionMode = 'ask'
        this.errorMessage = `生成阶段整理失败：${error.message}`
      }
    },

    continueDeeper() {
      if (this.isQuestionBusy) return
      this.interactionMode = 'ask'
      this.draftReport = ''
      this.draftReportMain = ''
      this.draftReportNextAction = ''
      this.errorMessage = ''
      this.answerRevealReady = true
    },

    async acceptDraftReport() {
      if (this.isQuestionBusy) return

      this.savingDraftReport = true
      const finalReport = this.draftReportMain || this.draftReport || ''

      this.$store.commit('set_self_value_report', finalReport)

      try {
        const saveResponse = await fetch('http://127.0.0.1:8002/api/selfvalue/save-report/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            report: finalReport,
            qa_history: this.qaHistory
          })
        })

        const saveData = await saveResponse.json()

        if (!saveResponse.ok) {
          throw new Error(saveData.error || '保存报告失败')
        }

        const reportId = saveData.id

        this.$router.push({
          path: '/self-value/report',
          query: { id: reportId }
        })
      } catch (error) {
        console.error('保存报告失败：', error.message)
        this.$router.push('/self-value/report')
      } finally {
        this.savingDraftReport = false
      }
    }
  },

  beforeUnmount() {
    if (this.playbackRafId) {
      window.cancelAnimationFrame(this.playbackRafId)
      this.playbackRafId = null
    }
    this.clearAnswerRevealTimer()
  },

  mounted() {
    this.tickQuestionPlayback = this.tickQuestionPlayback.bind(this)

    if (this.prefetchedFirstQuestionReady && this.prefetchedFirstQuestion) {
      this.applyFirstQuestion(this.prefetchedFirstQuestion)
      this.$store.commit('reset_first_question')
      return
    }

    this.fetchFirstQuestion()
  }
}
</script>

<style scoped>
.questions-page {
  position: relative;
  min-height: 100vh;
  overflow: hidden;
  background:
    radial-gradient(circle at top left, rgba(244, 242, 238, 0.97), rgba(248, 246, 242, 0.99) 42%, #f7f5f2 100%);
  transition: background 0.35s ease;
}

.questions-page--thinking {
  background:
    radial-gradient(circle at top left, rgba(241, 239, 235, 0.98), rgba(247, 245, 241, 1) 42%, #f5f2ee 100%);
}

.questions-page-bg {
  position: absolute;
  border-radius: 999px;
  filter: blur(96px);
  opacity: 0.38;
  pointer-events: none;
  transform-origin: center;
  transition: opacity 0.35s ease, transform 0.35s ease;
}

.questions-page--thinking .questions-page-bg {
  opacity: 0.45;
  transform: scale(1.015);
}

.questions-bg-a {
  width: 460px;
  height: 460px;
  left: -130px;
  top: -110px;
  background: radial-gradient(circle, rgba(190, 214, 255, 0.72) 0%, rgba(190, 214, 255, 0) 72%);
}

.questions-bg-b {
  width: 460px;
  height: 460px;
  right: -120px;
  bottom: -150px;
  background: radial-gradient(circle, rgba(255, 221, 232, 0.56) 0%, rgba(255, 221, 232, 0) 72%);
}

.questions-shell {
  position: relative;
  z-index: 1;
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 26px 20px 28px;
}

.questions-container {
  width: 100%;
  max-width: 760px;
}

.questions-kicker {
  font-size: 13px;
  line-height: 1.6;
  letter-spacing: 0.08em;
  color: #857d72;
}

.questions-kicker--soft {
  color: #938a7d;
}

.questions-main {
  position: relative;
  display: grid;
  grid-template-rows: 210px 300px;
  gap: 10px;
}

.questions-main--transition {
  display: block;
}

.question-stage {
  height: 210px;
}

.question-title-wrap {
  position: relative;
  height: 210px;
  padding: 12px 48px 8px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  transition: transform 0.25s ease;
}

.question-title-wrap--thinking {
  transform: translateY(-1px);
}

.question-title-wrap::before,
.question-title-wrap::after {
  position: absolute;
  font-family:
    "PingFang SC",
    "Hiragino Sans GB",
    "Microsoft YaHei",
    "Noto Sans SC",
    sans-serif;
  line-height: 1;
  font-weight: 300;
  color: rgba(177, 168, 154, 0.14);
  pointer-events: none;
  z-index: 0;
}

.question-title-wrap::before {
  content: "“";
  top: 10px;
  left: 6px;
  font-size: 56px;
}

.question-title-wrap::after {
  content: "”";
  right: 6px;
  bottom: 8px;
  font-size: 56px;
}

.question-title-wrap > * {
  position: relative;
  z-index: 1;
}

.questions-title {
  margin: 0;
  max-width: 720px;
  min-height: 5.2em;
  overflow: hidden;
  color: #26261f;
  word-break: break-word;
  overflow-wrap: break-word;
  text-align: left;
  transition: font-size 0.2s ease, line-height 0.2s ease;
}

.questions-title--short {
  font-size: 31px;
  line-height: 1.62;
  font-weight: 430;
  letter-spacing: -0.005em;
}

.questions-title--medium {
  font-size: 29px;
  line-height: 1.66;
  font-weight: 430;
  letter-spacing: -0.005em;
}

.questions-title--long {
  font-size: 27px;
  line-height: 1.7;
  font-weight: 425;
  letter-spacing: 0;
}

.stream-char {
  color: rgba(38, 38, 31, 0.08);
  animation: streamCharFade 420ms ease-out forwards;
}

.questions-hint {
  margin: 10px auto 0;
  max-width: 600px;
  min-height: 1.95em;
  overflow: hidden;
  font-size: 15px;
  line-height: 1.95;
  letter-spacing: 0.02em;
  color: #847c71;
  text-align: center;
  transition: color 0.25s ease;
}

.question-title-wrap--thinking .questions-hint {
  color: #7a7368;
}

.questions-status {
  margin-top: 4px;
  font-size: 15px;
  line-height: 1.8;
  color: #7b7469;
}

.answer-stage {
  height: 300px;
}

.question-answer-area {
  height: 300px;
  transition: opacity 0.28s ease, filter 0.28s ease;
}

.question-answer-area--thinking {
  opacity: 0.56;
  filter: blur(1px) saturate(0.9);
  pointer-events: none;
}

.question-side-link-row {
  display: flex;
  justify-content: flex-end;
  margin-top: 10px;
  margin-bottom: 6px;
}

.question-side-link {
  appearance: none;
  border: none;
  background: transparent;
  padding: 4px 10px;
  border-radius: 999px;
  display: inline-flex;
  align-items: center;
  gap: 7px;
  font-size: 13px;
  line-height: 1.6;
  color: #8b8276;
  cursor: pointer;
  transition:
    color 0.18s ease,
    opacity 0.18s ease,
    background-color 0.18s ease;
  position: relative;
}

.question-side-link:hover {
  color: #645c52;
  background: rgba(210, 170, 110, 0.08);
}

.question-side-link:disabled {
  opacity: 0.45;
  cursor: not-allowed;
  background: transparent;
}
.question-side-link:hover {
  color: #645c52;
}

.question-side-link:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

.question-side-link__icon {
  width: 15px;
  height: 15px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex: 0 0 auto;
}

.question-side-link__icon svg {
  width: 100%;
  height: 100%;
  display: block;
}

.question-side-link__text {
  position: relative;
  top: 0.5px;
}


.question-side-link-row--intro .question-side-link {
  animation: summarizeLinkIntroBg 1.85s ease-out 1;
}

.question-side-link-row--intro .question-side-link__icon {
  animation: summarizeIconIntroBg 1.85s ease-out 1;
}

@keyframes summarizeLinkIntroBg {
  0% {
    opacity: 0;
    transform: translateY(3px);
    color: #a79f94;
    background-color: rgba(214, 160, 74, 0);
    box-shadow: 0 0 0 rgba(214, 160, 74, 0);
  }

  28% {
    opacity: 1;
    transform: translateY(0);
    color: #ffff00;
    background-color: rgba(232, 191, 118, 0.3);
    box-shadow: 0 0 0 6px rgba(232, 191, 118, 0.08);
  }

  52% {
    color: #6a5840;
    background-color: rgba(232, 191, 118, 0.2);
    box-shadow: 0 0 0 3px rgba(232, 191, 118, 0.04);
  }

  100% {
    opacity: 1;
    transform: translateY(0);
    color: #8b8276;
    background-color: rgba(214, 160, 74, 0);
    box-shadow: 0 0 0 rgba(214, 160, 74, 0);
  }
}

@keyframes summarizeIconIntroBg {
  0% {
    transform: scale(0.92);
    opacity: 0.72;
  }

  30% {
    transform: scale(1.08);
    opacity: 1;
  }

  100% {
    transform: scale(1);
    opacity: 1;
  }
}


.question-input-wrap,
.question-options-wrap {
  margin-top: 0;
}

.question-breath-wrap {
  position: relative;
  border-radius: 28px;
}

.question-breath-wrap::before {
  content: '';
  position: absolute;
  inset: -18px;
  border-radius: 38px;
  background:
    radial-gradient(circle at 18% 24%, rgba(182, 208, 255, 0.3), transparent 34%),
    radial-gradient(circle at 82% 76%, rgba(255, 218, 229, 0.26), transparent 36%),
    radial-gradient(circle at 50% 50%, rgba(255, 255, 255, 0.5), transparent 56%);
  filter: blur(26px);
  opacity: 0.84;
  z-index: 0;
  pointer-events: none;
  animation: localGlow 6.8s ease-in-out infinite;
}

.question-breath-wrap > * {
  position: relative;
  z-index: 1;
}

.question-textarea {
  width: 100%;
  height: 248px;
  padding: 22px 22px 20px;
  border: 1px solid rgba(198, 190, 178, 0.56);
  border-radius: 26px;
  background: rgba(255, 253, 250, 0.9);
  box-shadow:
    0 8px 30px rgba(54, 45, 33, 0.04),
    inset 0 1px 0 rgba(255, 255, 255, 0.46);
  backdrop-filter: blur(8px);
  font-size: 17px;
  line-height: 1.9;
  color: #1f1c17;
  outline: none;
  resize: none;
  transition: border-color 0.22s ease, box-shadow 0.22s ease, background 0.22s ease;
}

.question-textarea:focus {
  border-color: rgba(154, 144, 130, 0.78);
  box-shadow:
    0 10px 34px rgba(54, 45, 33, 0.06),
    inset 0 1px 0 rgba(255, 255, 255, 0.58);
  background: rgba(255, 253, 250, 0.96);
}

.question-textarea::placeholder {
  color: #a39a8d;
}

.question-options {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.question-option {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 16px 18px;
  border: 1px solid rgba(202, 194, 183, 0.6);
  border-radius: 20px;
  background: rgba(255, 253, 250, 0.84);
  box-shadow: 0 6px 20px rgba(54, 45, 33, 0.03);
  cursor: pointer;
  transition:
    border-color 0.2s ease,
    background 0.2s ease,
    box-shadow 0.2s ease,
    opacity 0.2s ease;
}

.question-option:hover {
  border-color: rgba(171, 159, 143, 0.72);
  background: rgba(255, 253, 250, 0.96);
}

.question-option--active {
  border-color: rgba(126, 120, 110, 0.78);
  background: rgba(255, 251, 246, 0.99);
  box-shadow: 0 10px 24px rgba(54, 45, 33, 0.05);
}

.question-option input {
  margin-top: 3px;
  flex: 0 0 auto;
}

.question-option span {
  display: block;
  font-size: 16px;
  line-height: 1.78;
  color: #2a2620;
}

.question-answer-area--thinking .question-textarea,
.question-answer-area--thinking .question-option {
  background: rgba(250, 247, 242, 0.72);
  border-color: rgba(198, 190, 178, 0.42);
  box-shadow:
    0 4px 18px rgba(54, 45, 33, 0.025),
    inset 0 1px 0 rgba(255, 255, 255, 0.28);
}

.transition-stage {
  margin-bottom: 14px;
}

.transition-panel-wrap {
  position: relative;
  margin-top: 8px;
}

.transition-panel {
  border: 1px solid rgba(198, 190, 178, 0.5);
  border-radius: 28px;
  padding: 26px 24px;
  min-height: 110px;
  background: rgba(255, 253, 250, 0.9);
  box-shadow:
    0 8px 30px rgba(54, 45, 33, 0.04),
    inset 0 1px 0 rgba(255, 255, 255, 0.42);
  backdrop-filter: blur(8px);
  font-size: 17px;
  line-height: 1.9;
  color: #524b42;
  display: flex;
  align-items: center;
  justify-content: center;
}

.report-page {
  display: block;
}

.report-topline {
  margin-bottom: 14px;
}

.report-hero {
  margin-bottom: 22px;
}

.report-title {
  min-height: auto;
  margin: 0;
  text-align:center
}

.report-subtitle {
  margin: 12px 0 0;
  max-width: 640px;
  font-size: 15px;
  line-height: 1.9;
  color: #7f776c;
  text-align: center;
 
}

.report-stack {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.report-card {
  position: relative;
  border: 1px solid rgba(198, 190, 178, 0.56);
  border-radius: 28px;
  background: rgba(255, 253, 250, 0.92);
  box-shadow:
    0 8px 30px rgba(54, 45, 33, 0.04),
    inset 0 1px 0 rgba(255, 255, 255, 0.42);
  backdrop-filter: blur(8px);
  overflow: hidden;
}

.report-card--primary {
  padding: 24px 24px 22px;
}

.report-card--secondary {
  padding: 22px 24px 20px;
}

.report-card-head {
  margin-bottom: 12px;
}

.report-card-kicker {
  font-size: 13px;
  line-height: 1.6;
  letter-spacing: 0.06em;
  color: #8f867a;
}

.report-card-body {
  white-space: pre-wrap;
  word-break: break-word;
  color: #201d18;
  padding:0px 15px 15px;
}

.report-main-content {
  font-size: 17px;
  line-height: 2;
  text-align:left;
}

.report-next-content {
  font-size: 16px;
  line-height: 1.95;
  color: #4d473f;
  text-align:left;
}

.questions-actions {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 12px;
  flex-wrap: nowrap;
  margin-top: 14px;
  transition: opacity 0.28s ease, filter 0.28s ease;
}

.questions-actions--thinking {
  opacity: 0.5;
  filter: saturate(0.88);
}

.questions-actions--draft {
  margin-top: 24px;
}

.report-actions {
  justify-content: center;
  margin-top: 22px;
}

.question-btn {
  appearance: none;
  border-radius: 999px;
  padding: 14px 24px;
  min-width: 132px;
  font-size: 15px;
  line-height: 1;
  letter-spacing: 0.01em;
  cursor: pointer;
  transition:
    transform 0.18s ease,
    background 0.18s ease,
    border-color 0.18s ease,
    color 0.18s ease,
    box-shadow 0.18s ease,
    opacity 0.18s ease;
}

.question-btn:hover {
  transform: translateY(-1px);
}

.question-btn:disabled {
  opacity: 0.58;
  cursor: not-allowed;
  transform: none;
}

.question-btn--solid {
  border: none;
  color: #ffffff;
  background: #4d5965;
  box-shadow: 0 10px 20px rgba(62, 71, 80, 0.16);
}

.question-btn--solid:hover {
  background: #444f5a;
}

.question-btn--ghost {
  border: 1px solid rgba(179, 170, 158, 0.8);
  color: #4f4942;
  background: rgba(255, 253, 250, 0.72);
}

.question-btn--ghost:hover {
  background: rgba(250, 246, 241, 0.92);
  border-color: rgba(157, 146, 132, 0.88);
}

.questions-error {
  margin-top: 12px;
  font-size: 14px;
  line-height: 1.8;
  color: #b42318;
  text-align: center;
}

.gray {
  color: gray;
}

.thinking-caret {
  display: inline-block;
  width: 0.55em;
  height: 1.05em;
  margin-left: 6px;
  vertical-align: -0.08em;
  border-right: 2px solid rgba(92, 86, 77, 0.62);
  animation: caretBlink 1.05s steps(1, end) infinite;
}

@keyframes streamCharFade {
  0% { color: rgba(38, 38, 31, 0.05); }
  100% { color: rgba(38, 38, 31, 1); }
}

@keyframes localGlow {
  0% { opacity: 0.6; transform: scale(0.985); }
  50% { opacity: 0.92; transform: scale(1.05); }
  100% { opacity: 0.55; transform: scale(0.985); }
}

@keyframes caretBlink {
  0%, 48% { opacity: 1; }
  50%, 100% { opacity: 0.18; }
}

@media (max-width: 768px) {
  .questions-shell {
    align-items: flex-start;
    padding: 20px 16px 18px;
  }

  .questions-main {
    grid-template-rows: 188px 284px;
    gap: 8px;
  }

  .question-stage,
  .question-title-wrap {
    height: 188px;
  }

  .question-title-wrap {
    padding: 8px 26px 8px;
  }

  .question-title-wrap::before {
    top: 8px;
    left: 0;
    font-size: 40px;
  }

  .question-title-wrap::after {
    right: 0;
    bottom: 2px;
    font-size: 40px;
  }

  .questions-title {
    min-height: 5.55em;
  }

  .questions-title--short {
    font-size: 26px;
    line-height: 1.66;
  }

  .questions-title--medium {
    font-size: 25px;
    line-height: 1.7;
  }

  .questions-title--long {
    font-size: 23px;
    line-height: 1.74;
  }

  .questions-hint {
    margin-top: 8px;
    font-size: 14px;
    line-height: 1.82;
  }

  .answer-stage,
  .question-answer-area {
    height: 284px;
  }

  .question-textarea {
    height: 228px;
    font-size: 16px;
    line-height: 1.88;
    padding: 18px 18px 16px;
    border-radius: 24px;
  }

  .question-option {
    padding: 15px 16px;
    border-radius: 18px;
  }

  .question-option span {
    font-size: 15px;
    line-height: 1.74;
  }

  .question-side-link-row {
    margin-top: 8px;
    margin-bottom: 4px;
  }

  .question-side-link {
    font-size: 12px;
    gap: 6px;
    padding:4px 8px;
  }

  .question-side-link__icon {
    width: 14px;
    height: 14px;
  }

  .transition-panel {
    min-height: 96px;
    padding: 22px 18px;
    font-size: 16px;
  }

  .report-subtitle {
    font-size: 14px;
    line-height: 1.82;
  }

  .report-card--primary,
  .report-card--secondary {
    padding: 20px 18px 18px;
  }

  .report-main-content {
    font-size: 16px;
    line-height: 1.92;
  }

  .report-next-content {
    font-size: 15px;
    line-height: 1.86;
  }

  .questions-actions {
    margin-top: 12px;
    gap: 10px;
  }

  .question-btn {
    min-width: 0;
    width: calc(50% - 5px);
    padding: 14px 12px;
  }

  .report-actions .question-btn {
    width: calc(50% - 5px);
  }

  .questions-page-bg {
    filter: blur(74px);
    opacity: 0.3;
  }
}

@media (max-width: 430px) {
  .questions-main {
    grid-template-rows: 180px 270px;
  }

  .question-stage,
  .question-title-wrap {
    height: 180px;
  }

  .questions-title--short {
    font-size: 24px;
  }

  .questions-title--medium {
    font-size: 23px;
  }

  .questions-title--long {
    font-size: 22px;
  }

  .questions-kicker,
  .report-card-kicker {
    font-size: 12px;
  }

  .answer-stage,
  .question-answer-area {
    height: 270px;
  }

  .question-textarea {
    height: 214px;
  }

  .transition-panel {
    min-height: 88px;
  }

  .question-btn,
  .report-actions .question-btn {
    width: 100%;
  }

  .questions-actions,
  .report-actions {
    flex-direction: column;
  }
}
</style>
