<template>
  <div class="questions-page" :class="{ 'questions-page--thinking': submitting }">
    <div class="questions-page-bg questions-bg-a"></div>
    <div class="questions-page-bg questions-bg-b"></div>

    <div class="questions-shell">
      <div class="questions-container">
        <div class="questions-head">
          <div class="questions-kicker">自我价值梳理</div>
        </div>

        <section v-if="interactionMode === 'ask'" class="questions-main">
          <div class="question-title-wrap" :class="{ 'question-title-wrap--thinking': submitting }">
            <h1 class="questions-title">
              <template v-if="submitting">
                <template v-if="streamedQuestionStableText || streamedQuestionPendingChar">
                  <span>{{ streamedQuestionStableText }}</span>
                  <span
                    v-if="streamedQuestionPendingChar"
                    class="stream-char"
                  >{{ streamedQuestionPendingChar }}</span>
                  <span class="thinking-caret"></span>
                </template>
                <template v-else>
                  正在整理下一问<span class="thinking-caret"></span>
                </template>
              </template>
              <template v-else>
                {{ currentQuestion || '正在生成第一题…' }}
              </template>
            </h1>

            <p class="questions-hint">
              {{
                submitting
                  ? '请稍等片刻，我们正在继续贴近你的表达。'
                  : '不用担心能否一次说完整。从你此刻最有感觉的地方开始就可以。'
              }}
            </p>
          </div>

          <div v-if="loading" class="questions-status">
            正在请求问题……
          </div>

          <transition name="answer-fade" mode="out-in">
            <div
              v-if="!loading"
              :key="submitting ? 'thinking' : `${questionRenderKey}-${questionType}`"
              class="question-answer-area"
              :class="{ 'question-answer-area--thinking': submitting }"
            >
              <div
                v-if="questionType === 'text'"
                class="question-breath-wrap question-input-wrap"
              >
                <textarea
                  v-model="answerText"
                  class="question-textarea"
                  placeholder="在这里慢慢写下你的想法。"
                  :disabled="submitting"
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
                      :disabled="submitting"
                    />
                    <span>{{ option }}</span>
                  </label>
                </div>
              </div>
            </div>
          </transition>
        </section>

        <section v-else-if="interactionMode === 'draft_report'" class="questions-main">
          <div class="draft-report-head question-title-wrap">
            <div class="questions-kicker questions-kicker--soft">阶段性整理</div>

            <h1 class="questions-title">
              这是当前阶段最接近你的一版理解。
            </h1>

            <p class="questions-hint">
              先看看它是否触到你真正想说的部分。如果还不够，我们可以继续往里走。
            </p>
          </div>

          <div class="question-breath-wrap draft-report-wrap">
            <div class="draft-report-box">
              {{ draftReport }}
            </div>
          </div>

          <div class="questions-actions questions-actions--draft">
            <button
              class="question-btn question-btn--ghost"
              type="button"
              :disabled="submitting"
              @click="continueDeeper"
            >
              继续深入
            </button>
            <button
              class="question-btn question-btn--solid"
              type="button"
              :disabled="submitting"
              @click="acceptDraftReport"
            >
              {{ submitting ? '正在整理…' : '这版已经接近我了' }}
            </button>
          </div>
        </section>

        <div v-if="errorMessage" class="questions-error">
          {{ errorMessage }}
        </div>

        <div v-if="interactionMode === 'ask'" class="questions-actions">
          <button
            class="question-btn question-btn--ghost"
            type="button"
            :disabled="submitting"
            @click="goBack"
          >
            返回上一页
          </button>
          <button
            class="question-btn question-btn--solid"
            type="button"
            :disabled="submitting"
            @click="goNext"
          >
            {{ submitting ? '正在整理…' : '下一步' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'SelfValueQuestions',

  data() {
    return {
      loading: true,
      errorMessage: '',
      currentQuestion: '',
      questionType: 'text',
      questionOptions: [],
      answerText: '',
      selectedOption: '',
      qaHistory: [],
      round: 1,
      interactionMode: 'ask',
      draftReport: '',
      submitting: false,
      questionRenderKey: 0,

      // 流式问题播放相关状态
      rawAskBuffer: '',
      targetQuestionText: '',
      askStreamComplete: false,
      streamedQuestionStableText: '',
      streamedQuestionPendingChar: '',
      playbackRafId: null,
      playbackLastTs: 0,
      playbackAccumulator: 0
    }
  },
  

  computed: {
  prefetchedFirstQuestion() {
    return this.$store.state.first_question_data
  },
  prefetchedFirstQuestionReady() {
    return this.$store.state.first_question_ready
  },
  prefetchedFirstQuestionLoading() {
    return this.$store.state.first_question_loading
  }
},

  methods: {

    applyFirstQuestion(data) {
  this.interactionMode = 'ask'
  this.currentQuestion = data.question || '未返回问题内容'
  this.questionType = this.normalizeQuestionType(data.question_type)
  this.questionOptions = Array.isArray(data.options) ? data.options : []
  this.questionRenderKey += 1
},

    goBack() {
      if (this.submitting) return
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

    getStepDelay(ch) {
      return /[，。！？；：,.!?;:]/.test(ch) ? 190 : 70
    },

    promotePendingChar() {
      if (this.streamedQuestionPendingChar) {
        this.streamedQuestionStableText += this.streamedQuestionPendingChar
        this.streamedQuestionPendingChar = ''
      }
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
        const nextChar = this.targetQuestionText[builtLength]
        const neededDelay = this.getStepDelay(nextChar)

        if (this.playbackAccumulator < neededDelay) break

        this.playbackAccumulator -= neededDelay
        this.promotePendingChar()
        this.streamedQuestionPendingChar = nextChar
        builtLength = this.getBuiltLength()

        const nextNextChar = this.targetQuestionText[builtLength]
        if (!nextNextChar) break

        if (/[，。！？；：,.!?;:]/.test(nextChar)) break
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
      this.submitting = false
      this.rawAskBuffer = ''
      this.targetQuestionText = ''
      this.askStreamComplete = false
      this.streamedQuestionStableText = ''
      this.streamedQuestionPendingChar = ''
    },

    resetAskStreamingState() {
      if (this.playbackRafId) {
        window.cancelAnimationFrame(this.playbackRafId)
        this.playbackRafId = null
      }
      this.rawAskBuffer = ''
      this.targetQuestionText = ''
      this.askStreamComplete = false
      this.streamedQuestionStableText = ''
      this.streamedQuestionPendingChar = ''
      this.playbackLastTs = 0
      this.playbackAccumulator = 0
    },

    applyAskResult(data) {
      const finalQuestion =
        data.question ||
        this.targetQuestionText ||
        (this.streamedQuestionStableText + this.streamedQuestionPendingChar) ||
        '未返回问题内容'

      this.interactionMode = 'ask'
      this.currentQuestion = finalQuestion
      this.questionType = this.normalizeQuestionType(data.question_type)
      this.questionOptions = Array.isArray(data.options) ? data.options : []
      this.answerText = ''
      this.selectedOption = ''
      this.round += 1
      this.questionRenderKey += 1

      if (finalQuestion.length > this.targetQuestionText.length) {
        this.targetQuestionText = finalQuestion
      }

      this.askStreamComplete = true
      this.ensurePlaybackRunning()
    },

    
    applyDraftReportResult(data) {
  const summaryText = data.summary || ''
  const reportText = data.report || ''
  const nextActionText = data.next_action || ''

  let content = reportText || summaryText

  if (!content && nextActionText) {
    content = nextActionText
  }

  if (summaryText && nextActionText && reportText === '') {
    content = `${summaryText}\n\n下一步建议：${nextActionText}`
  }

  this.interactionMode = 'draft_report'
  this.draftReport = content || '已进入阶段性整理，但暂未返回完整内容。'
  this.submitting = false
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
      this.ensurePlaybackRunning()
    }
    return
  }

  if (payload.event === 'done') {
    const data = payload.data || {}
    const status = data.status || ''

    // 1. 正常提问
    if (status === 'ask' || status === 'clarify') {
      this.applyAskResult(data)
      return
    }

    // 2. 阶段性整理 / 报告，都进入 draft_report 视图
    if (
      status === 'stage_summary' ||
      status === 'final_report' ||
      status === 'draft_report' ||
      status === 'action_plan'
    ) {
      this.applyDraftReportResult(data)
      return
    }

    // 3. 未知状态：不要覆盖当前问题，直接报错，避免掉成“未返回问题内容”
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

      // 处理流结束时最后残留的一行，避免最后一个 done 丢失
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

        this.interactionMode = 'ask'
        this.currentQuestion = data.question || '未返回问题内容'
        this.questionType = this.normalizeQuestionType(data.question_type)
        this.questionOptions = Array.isArray(data.options) ? data.options : []
        this.questionRenderKey += 1
      } catch (error) {
        this.errorMessage = `获取第一题失败：${error.message}`
      } finally {
        this.loading = false
      }
    },

    async goNext() {
      if (this.submitting) return

      const currentAnswer = this.getCurrentAnswer()

      if (!this.validateCurrentAnswer(currentAnswer)) {
        this.errorMessage = this.questionType === 'single_choice'
          ? '请先选择一个选项。'
          : '请先输入你的回答。'
        return
      }

      this.submitting = true
      this.errorMessage = ''
      this.resetAskStreamingState()

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

    continueDeeper() {
      if (this.submitting) return
      this.interactionMode = 'ask'
      this.draftReport = ''
      this.errorMessage = ''
    },

    async acceptDraftReport() {
      if (this.submitting) return

      this.submitting = true
      const finalReport = this.draftReport || ''

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
          query: {
            id: reportId
          }
        })
      } catch (error) {
        console.error('保存报告失败：', error.message)
        this.$router.push('/self-value/report')
      } finally {
        this.submitting = false
      }
    }
  },

  beforeUnmount() {
    if (this.playbackRafId) {
      window.cancelAnimationFrame(this.playbackRafId)
      this.playbackRafId = null
    }
  },

  /*mounted() {
    this.tickQuestionPlayback = this.tickQuestionPlayback.bind(this)
    this.fetchFirstQuestion()
  }*/

  mounted() {
      if (this.prefetchedFirstQuestionReady && this.prefetchedFirstQuestion) {
          this.applyFirstQuestion(this.prefetchedFirstQuestion)
          this.$store.commit('reset_first_question')
          return
          }
      this.fetchFirstQuestion()
      },
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
  opacity: 0.48;
  transform: scale(1.03);
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
  padding: 48px 20px;
}

.questions-container {
  width: 100%;
  max-width: 760px;
}

.questions-head {
  margin-bottom: 16px;
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
}

.question-title-wrap {
  position: relative;
  padding: 20px 56px 18px;
  transition: transform 0.3s ease, opacity 0.3s ease;
}

.question-title-wrap--thinking {
  transform: translateY(-2px);
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
  color: rgba(177, 168, 154, 0.16);
  pointer-events: none;
  z-index: 0;
}

.question-title-wrap::before {
  content: "“";
  top: 14px;
  left: 8px;
  font-size: 64px;
}

.question-title-wrap::after {
  content: "”";
  right: 8px;
  bottom: 18px;
  font-size: 64px;
}

.question-title-wrap > * {
  position: relative;
  z-index: 1;
}

.questions-title {
  margin: 0;
  max-width: 720px;
  min-height: 3.4em;
  font-size: 32px;
  line-height: 1.68;
  font-weight: 430;
  letter-spacing: -0.005em;
  color: #26261f;
  word-break: normal;
  overflow-wrap: break-word;
  text-align: left;
}

.stream-char {
  color: rgba(38, 38, 31, 0.08);
  animation: streamCharFade 30020ms ease-out forwards;
}

.questions-hint {
  margin: 16px auto 0;
  max-width: 600px;
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
  margin-top: 28px;
  font-size: 15px;
  line-height: 1.8;
  color: #7b7469;
}

.question-answer-area {
  transition: opacity 0.32s ease, transform 0.32s ease, filter 0.32s ease;
}

.question-answer-area--thinking {
  opacity: 0.36;
  transform: translateY(8px);
  filter: blur(1px) saturate(0.92);
  pointer-events: none;
}

.question-input-wrap,
.question-options-wrap,
.draft-report-wrap {
  margin-top: 32px;
}

.question-breath-wrap {
  position: relative;
  border-radius: 30px;
}

.question-breath-wrap::before {
  content: '';
  position: absolute;
  inset: -28px;
  border-radius: 46px;
  background:
    radial-gradient(circle at 18% 24%, rgba(182, 208, 255, 0.34), transparent 34%),
    radial-gradient(circle at 82% 76%, rgba(255, 218, 229, 0.3), transparent 36%),
    radial-gradient(circle at 50% 50%, rgba(255, 255, 255, 0.52), transparent 56%);
  filter: blur(30px);
  opacity: 0.9;
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
  min-height: 248px;
  padding: 24px 24px 22px;
  border: 1px solid rgba(198, 190, 178, 0.56);
  border-radius: 28px;
  background: rgba(255, 253, 250, 0.9);
  box-shadow:
    0 8px 30px rgba(54, 45, 33, 0.04),
    inset 0 1px 0 rgba(255, 255, 255, 0.46);
  backdrop-filter: blur(8px);
  font-size: 17px;
  line-height: 1.95;
  color: #1f1c17;
  outline: none;
  resize: vertical;
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
  gap: 14px;
}

.question-option {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 18px 20px;
  border: 1px solid rgba(202, 194, 183, 0.6);
  border-radius: 22px;
  background: rgba(255, 253, 250, 0.84);
  box-shadow: 0 6px 20px rgba(54, 45, 33, 0.03);
  cursor: pointer;
  transition:
    border-color 0.2s ease,
    background 0.2s ease,
    transform 0.2s ease,
    box-shadow 0.2s ease;
}

.question-option:hover {
  border-color: rgba(171, 159, 143, 0.72);
  background: rgba(255, 253, 250, 0.96);
  transform: translateY(-1px);
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
  line-height: 1.85;
  color: #2a2620;
}

.draft-report-head {
  margin-bottom: 10px;
}

.draft-report-box {
  border: 1px solid rgba(198, 190, 178, 0.58);
  border-radius: 28px;
  padding: 26px 24px;
  background: rgba(255, 253, 250, 0.92);
  box-shadow:
    0 8px 30px rgba(54, 45, 33, 0.04),
    inset 0 1px 0 rgba(255, 255, 255, 0.42);
  backdrop-filter: blur(8px);
  font-size: 17px;
  line-height: 2;
  color: #1f1c17;
  white-space: pre-wrap;
}

.questions-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  margin-top: 30px;
}

.questions-actions--draft {
  margin-top: 24px;
}

.question-btn {
  appearance: none;
  border-radius: 999px;
  padding: 15px 26px;
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
  margin-top: 18px;
  font-size: 14px;
  line-height: 1.8;
  color: #b42318;
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

.answer-fade-enter-active,
.answer-fade-leave-active {
  transition: opacity 0.28s ease, transform 0.28s ease;
}

.answer-fade-enter-from,
.answer-fade-leave-to {
  opacity: 0;
  transform: translateY(10px);
}

@keyframes streamCharFade {
  0% {
    color: rgba(38, 38, 31, 0.05);
  }
  100% {
    color: rgba(38, 38, 31, 1);
  }
}

@keyframes localGlow {
  0% {
    opacity: 0.6;
    transform: scale(0.985);
  }
  50% {
    opacity: 0.92;
    transform: scale(1.05);
  }
  100% {
    opacity: 0.55;
    transform: scale(0.985);
  }
}

@keyframes caretBlink {
  0%,
  48% {
    opacity: 1;
  }
  50%,
  100% {
    opacity: 0.18;
  }
}

@media (max-width: 1024px) {
  .questions-shell {
    padding: 40px 24px;
  }

  .questions-title {
    font-size: 31px;
    line-height: 1.58;
  }

  .question-textarea,
  .draft-report-box {
    font-size: 16px;
  }
}

@media (max-width: 768px) {
  .questions-shell {
    align-items: flex-start;
    padding: 30px 18px 36px;
  }

  .questions-container {
    max-width: 100%;
  }

  .questions-head {
    margin-bottom: 12px;
  }

  .question-title-wrap {
    padding: 12px 30px 12px;
  }

  .question-title-wrap::before {
    top: 12px;
    left: 0;
    font-size: 42px;
    color: rgba(177, 168, 154, 0.12);
  }

  .question-title-wrap::after {
    right: 0;
    bottom: 4px;
    font-size: 42px;
    color: rgba(177, 168, 154, 0.12);
  }

  .questions-title {
    max-width: 100%;
    min-height: 3.6em;
    font-size: 26px;
    line-height: 1.72;
    letter-spacing: 0.01em;
    font-weight: 430;
  }

  .questions-hint {
    margin-top: 14px;
    font-size: 14px;
    line-height: 1.82;
    max-width: 100%;
  }

  .question-input-wrap,
  .question-options-wrap,
  .draft-report-wrap {
    margin-top: 24px;
  }

  .question-textarea {
    min-height: 220px;
    padding: 20px 18px 18px;
    border-radius: 24px;
    font-size: 16px;
    line-height: 1.9;
  }

  .question-option {
    padding: 16px 16px;
    border-radius: 18px;
  }

  .question-option span {
    font-size: 15px;
    line-height: 1.78;
  }

  .draft-report-box {
    padding: 22px 18px;
    border-radius: 24px;
    font-size: 16px;
    line-height: 1.92;
  }

  .questions-actions {
    flex-direction: column;
    margin-top: 24px;
  }

  .question-btn {
    width: 100%;
    padding: 15px 20px;
  }

  .questions-page-bg {
    filter: blur(78px);
    opacity: 0.3;
  }
}

@media (max-width: 430px) {
  .questions-title {
    font-size: 24px;
    line-height: 1.62;
  }

  .questions-kicker {
    font-size: 12px;
  }

  .question-textarea {
    min-height: 190px;
  }
}
</style>
