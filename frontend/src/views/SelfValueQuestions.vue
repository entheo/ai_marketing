<template>
  <div
    class="questions-page"
    :class="{
      'questions-page--thinking': isQuestionBusy,
      'questions-page--stage-open': stageDrawerOpen && !isMobileStageOverlay
    }"
  >
    <div class="questions-page-bg questions-bg-a"></div>
    <div class="questions-page-bg questions-bg-b"></div>

    <div class="questions-shell">
      <div class="questions-layout">
        <div class="questions-container">
          <section class="questions-main">
            <div ref="chatThread" class="chat-thread">
              <div
                v-for="item in dialogItems"
                :key="item.id"
                class="chat-msg"
                :class="[
                  item.role === 'user' ? 'chat-msg--user' : 'chat-msg--assistant'
                ]"
              >
                <div class="chat-msg__role">
                  {{ item.role === 'user' ? '你' : '助手' }}
                </div>
                <div class="chat-msg__text">{{ item.text }}</div>
              </div>
              <div
                v-if="requestingQuestion"
                class="chat-msg chat-msg--assistant chat-msg--streaming"
              >
                <div class="chat-msg__role">助手</div>
                <div class="chat-msg__text">
                  思考中…
                </div>
              </div>
            </div>

            <div v-if="errorMessage" class="questions-error">
              {{ errorMessage }}
            </div>

            <div class="chat-composer">
              <textarea
                v-model="answerText"
                class="chat-composer__input"
                placeholder="继续说说你的真实感受…"
                :disabled="isQuestionBusy"
                @keydown.enter.exact.prevent="goNext"
              ></textarea>
              <button
                class="question-btn question-btn--solid"
                type="button"
                :disabled="isQuestionBusy"
                @click="goNext"
              >
                {{ requestingQuestion ? '发送中…' : '发送' }}
              </button>
            </div>
          </section>
        </div>

        <aside
          v-if="stageDrawerOpen"
          class="stage-drawer"
          :class="{ 'stage-drawer--overlay': isMobileStageOverlay }"
        >
          <div class="stage-drawer-head">
            <div class="stage-drawer-title-wrap">
              <div class="stage-drawer-kicker">阶段成果区</div>
              <div class="stage-drawer-stage-line">
                <h2 class="stage-drawer-title">
                  {{ stageView.stage_name || '当前阶段' }}
                </h2>
                <span
                  v-if="stageInlineFlash"
                  class="stage-inline-dot"
                  aria-label="阶段内容有更新"
                ></span>
                <span v-if="stageMeta.current_maturity" class="stage-badge">
                  {{ stageMeta.current_maturity }}
                </span>
              </div>
            </div>

            <button
              class="stage-drawer-close"
              type="button"
              @click="closeStageDrawer"
              aria-label="关闭阶段成果区"
            >
              ×
            </button>
          </div>

          <div class="stage-drawer-body">
            <p v-if="stageView.stage_summary" class="stage-summary">
              {{ stageView.stage_summary }}
            </p>
            <p v-else class="stage-summary stage-summary--empty">
              这里会逐步沉淀当前阶段的发现与判断。
            </p>
            <div class="stage-structure-line">
              <span>发现 {{ stageStructure.findings }}</span>
              <span>判断 {{ stageStructure.judgements }}</span>
              <span>待确认 {{ stageStructure.candidates }}</span>
            </div>

            <section class="stage-block">
              <div class="stage-block-head">发现</div>
              <div v-if="normalizedFindings.length" class="stage-list">
                <div
                  v-for="item in normalizedFindings"
                  :key="item.id"
                  class="stage-list-item"
                >
                  {{ item.text }}
                </div>
              </div>
              <div v-else class="stage-empty">还没有足够清晰的发现</div>
            </section>

            <section class="stage-block">
              <div class="stage-block-head">判断</div>
              <div v-if="normalizedJudgements.length" class="stage-list">
                <div
                  v-for="item in normalizedJudgements"
                  :key="item.id"
                  class="stage-list-item"
                >
                  {{ item.text }}
                </div>
              </div>
              <div v-else class="stage-empty">还没有足够稳定的 judgements</div>
            </section>

            <section class="stage-block">
              <div class="stage-block-head">待确认</div>
              <div v-if="normalizedCandidates.length" class="stage-candidate-list">
                <div
                  v-for="item in normalizedCandidates"
                  :key="item.id"
                  class="stage-candidate-item"
                >
                  <div class="stage-candidate-text">
                    {{ item.text }}
                  </div>

                  <div class="stage-candidate-meta-row">
                    <span
                      v-if="item.blocking"
                      class="candidate-flag candidate-flag--blocking"
                    >
                      blocking
                    </span>

                    <span
                      v-if="item.statusText"
                      class="candidate-status"
                    >
                      {{ item.statusText }}
                    </span>
                  </div>

                  <div class="stage-candidate-actions">
                    <button
                      class="mini-btn mini-btn--solid"
                      type="button"
                      :disabled="feedbackBusy"
                      @click="sendStageFeedback(item.id, 'confirmed')"
                    >
                      贴近
                    </button>
                    <button
                      class="mini-btn mini-btn--ghost"
                      type="button"
                      :disabled="feedbackBusy"
                      @click="sendStageFeedback(item.id, 'rejected')"
                    >
                      不太对
                    </button>
                  </div>
                </div>
              </div>
              <div v-else class="stage-empty">当前没有待确认项</div>
            </section>
          </div>

          <div class="stage-drawer-foot">
            <div class="stage-meta-line">
              <span v-if="stageMeta.current_stage_id">
                阶段ID：{{ stageMeta.current_stage_id }}
              </span>
              <span
                v-if="stageMeta.can_transition"
                class="stage-transition-ready"
              >
                可进入下一阶段
              </span>
            </div>

            <button
              v-if="stageMeta.can_transition"
              class="question-btn question-btn--solid question-btn--wide"
              type="button"
              :disabled="transitionBusy"
              @click="enterNextStage"
            >
              {{ transitionBusy ? '正在进入…' : '进入下一阶段' }}
            </button>
          </div>
        </aside>

        <aside class="insight-panel">
          <h3 class="insight-panel__title">已留下来的</h3>
          <div v-if="insightCards.length" class="insight-panel__list">
            <div
              v-for="item in insightCards"
              :key="item.id"
              class="insight-panel__item"
            >
              {{ item.text }}
            </div>
          </div>
          <div v-else class="insight-panel__empty">
            暂时还没有确认留下的内容
          </div>
        </aside>
      </div>
    </div>

    <transition name="stage-overlay-fade">
      <div
        v-if="stageDrawerOpen && isMobileStageOverlay"
        class="stage-overlay"
        @click="closeStageDrawer"
      ></div>
    </transition>
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
      currentMainDisplayText: '',
      currentQuestionLengthHint: 'medium',
      dialogItems: [],
      questionType: 'text',
      questionOptions: [],
      answerText: '',
      selectedOption: '',
      qaHistory: [],
      round: 1,
      insightCards: [],
      pendingInsightCandidate: null,

      requestingQuestion: false,
      playingQuestion: false,
      answerRevealReady: false,
      answerRevealTimer: null,

      rawAskBuffer: '',
      targetQuestionText: '',
      targetQuestionLengthHint: 'medium',
      askStreamComplete: false,
      streamedQuestionStableText: '',
      streamedQuestionPendingChar: '',
      streamingAssistantText: '',
      playbackRafId: null,
      playbackLastTs: 0,
      playbackAccumulator: 0,
      lockedStreamingLengthHint: '',

      conversationId: '',
      feedbackBusy: false,
      transitionBusy: false,

      stageDrawerOpen: false,
      isMobileStageOverlay: false,

      stageView: {
        stage_name: '',
        stage_summary: '',
        findings: [],
        judgements: [],
        confirmation_candidates: []
      },
      stageMeta: {
        can_transition: false,
        current_stage_id: '',
        current_maturity: ''
      },
      stageState: null,

      pendingStageView: null,
      pendingStageMeta: null,
      pendingStageState: null,

      hasUnreadStageUpdate: false,
      stageUpdateCount: 0,
      lastStageDigest: '',
      hasShownAnyStagePrompt: false,
      stageInlineFlash: false,
      stageInlineFlashTimer: null
    }
  },

  computed: {
    prefetchedFirstQuestion() {
      return this.$store?.state?.first_question_data
    },

    prefetchedFirstQuestionReady() {
      return this.$store?.state?.first_question_ready
    },

    isQuestionBusy() {
      return (
        this.requestingQuestion ||
        this.playingQuestion ||
        this.feedbackBusy ||
        this.transitionBusy
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
      return this.currentMainDisplayText || this.currentQuestion || ''
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
      if (this.isQuestionBusy) return ''
      return '从你此刻最有感觉，最舒服的地方开始就可以'
    },

    normalizedFindings() {
      return this.normalizeStageList(this.stageView.findings, 'finding')
    },

    normalizedJudgements() {
      return this.normalizeStageList(this.stageView.judgements, 'judgement')
    },

    normalizedCandidates() {
      const list = Array.isArray(this.stageView.confirmation_candidates)
        ? this.stageView.confirmation_candidates
        : []

      return list
        .map((item, index) => {
          const rawStatus = item.status || item.feedback_status || ''
          return {
            id: item.candidate_id || item.id || `candidate_${index}`,
            text: this.cleanStageText(this.extractStageItemText(item)),
            blocking: item.blocking === true || item.priority === 'blocking',
            statusText: this.mapCandidateStatus(rawStatus)
          }
        })
        .filter(item => !!item.text)
    },

    showStageInsightLink() {
      return false
    },

    stageInsightLinkText() {
      if (this.stageUpdateCount >= 2) {
        return '这里出现了一些新的阶段沉淀，点开看看'
      }
      return '刚刚形成了一些新的发现，点开看看'
    },

    stageStructure() {
      const getLevel = (count, fullCount) => {
        if (count <= 0) return '○'
        if (count < fullCount) return '◐'
        return '●'
      }

      return {
        findings: getLevel(this.normalizedFindings.length, 3),
        judgements: getLevel(this.normalizedJudgements.length, 2),
        candidates: getLevel(this.normalizedCandidates.length, 2)
      }
    }
  },

  methods: {
    appendDialogItem(role, text) {
      const normalizedRole = role === 'user' ? 'user' : 'assistant'
      const normalizedText = String(text || '').trim()
      if (!normalizedText) return

      const prev = this.dialogItems[this.dialogItems.length - 1]
      if (prev && prev.role === normalizedRole && prev.text === normalizedText) {
        return
      }

      this.dialogItems.push({
        id: `dialog_${Date.now()}_${Math.random().toString(36).slice(2, 7)}`,
        role: normalizedRole,
        text: normalizedText
      })

      if (this.dialogItems.length > 14) {
        this.dialogItems = this.dialogItems.slice(-14)
      }

      this.scrollChatToBottom()
    },

    scrollChatToBottom() {
      this.$nextTick(() => {
        const el = this.$refs.chatThread
        if (!el) return
        el.scrollTop = el.scrollHeight
      })
    },

    triggerStageInlineFlash() {
      if (this.stageInlineFlashTimer) {
        clearTimeout(this.stageInlineFlashTimer)
      }
      this.stageInlineFlash = true
      this.stageInlineFlashTimer = setTimeout(() => {
        this.stageInlineFlash = false
        this.stageInlineFlashTimer = null
      }, 1100)
    },

    inferQuestionLengthHint(text) {
      const len = String(text || '').trim().length
      if (len <= 20) return 'short'
      if (len <= 30) return 'medium'
      return 'long'
    },

    buildConversationId() {
      return `conv_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`
    },

    updateViewportMode() {
      this.isMobileStageOverlay = window.innerWidth <= 980
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

    normalizeQuestionType(questionType) {
      return questionType === 'single_choice' ? 'single_choice' : 'text'
    },

    bindQuestionMetaFromMessage(message, fallbackQuestion = '') {
      const finalQuestion = this.extractQuestionText(message) || fallbackQuestion || ''
      this.currentQuestion = finalQuestion
      this.currentQuestionLengthHint =
        message?.question_length_hint || this.inferQuestionLengthHint(finalQuestion)

      const nextType = this.extractMessageQuestionType(message)
      const nextOptions = this.extractMessageOptions(message)

      this.answerText = ''
      this.selectedOption = ''
      this.questionType = nextType
      this.questionOptions = nextOptions
    },

    bindMainDisplayTextFromMessage(message, fallbackText = '') {
      this.currentMainDisplayText = this.extractMainDisplayText(message) || fallbackText || ''
    },

    extractQuestionText(message) {
      if (!message || typeof message !== 'object') return ''
      return (
        message.question ||
        message.text ||
        message.content ||
        message.display_text ||
        message.message ||
        ''
      )
    },

    extractMainDisplayText(message) {
      if (!message || typeof message !== 'object') return ''
      return (
        message.text ||
        message.message ||
        message.content ||
        message.summary ||
        message.report ||
        message.next_action ||
        message.question ||
        ''
      )
    },

    extractMessageText(message) {
      return this.extractQuestionText(message)
    },

    extractMessageQuestionType(message) {
      if (!message || typeof message !== 'object') return 'text'
      return this.normalizeQuestionType(
        message.question_type ||
        message.input_type ||
        message.answer_type ||
        'text'
      )
    },

    extractMessageOptions(message) {
      if (!message || typeof message !== 'object') return []
      if (Array.isArray(message.options)) return message.options
      if (Array.isArray(message.choices)) return message.choices
      return []
    },

    applyFirstQuestionPayload(data) {
      const message = data?.message || data || {}
      const stage = data?.stage || null
      const meta = data?.meta || null
      const stageState = data?.stage_state || null

      this.loading = false
      this.errorMessage = ''

      const firstQuestion = this.extractQuestionText(message) || '未返回问题内容'
      const firstDisplayText = this.extractMainDisplayText(message) || firstQuestion

      this.bindQuestionMetaFromMessage(
        message,
        firstQuestion
      )
      this.bindMainDisplayTextFromMessage(message, firstDisplayText)
      this.appendDialogItem('assistant', firstDisplayText)
      this.handleInsightSignals(data)

      if (stage) {
        this.receiveStagePayload(stage, meta || {}, stageState, {
          forceCommit: true,
          suppressPrompt: true
        })
      }

      this.playLocalQuestion(
        firstDisplayText,
        message?.question_length_hint || this.inferQuestionLengthHint(firstDisplayText)
      )
    },

    playLocalQuestion(questionText, lengthHint = '') {
      this.currentMainDisplayText = questionText || ''
      this.currentQuestionLengthHint = lengthHint || this.inferQuestionLengthHint(questionText)
      this.requestingQuestion = false
      this.playingQuestion = false
      this.answerRevealReady = true
    },

    getCurrentAnswer() {
      return this.answerText.trim()
    },

    validateCurrentAnswer(answer) {
      return !!String(answer || '').trim()
    },

    goBack() {
      if (this.isQuestionBusy || !this.answerRevealReady) return
      this.$router.back()
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

    applyAskMessageDone(data) {
      const message = data?.message || data || {}
      const finalQuestion = this.extractQuestionText(message) || this.currentQuestion || ''
      const finalDisplayText =
        this.extractMainDisplayText(message) ||
        this.targetQuestionText ||
        (this.streamedQuestionStableText + this.streamedQuestionPendingChar) ||
        finalQuestion ||
        '未返回内容'

      this.bindQuestionMetaFromMessage(
        { ...message, question: finalQuestion },
        finalQuestion
      )
      this.bindMainDisplayTextFromMessage(
        { ...message, text: finalDisplayText },
        finalDisplayText
      )
      this.appendDialogItem('assistant', finalDisplayText)

      this.round += 1
      this.currentQuestionLengthHint =
        message?.question_length_hint || this.inferQuestionLengthHint(finalDisplayText)
      this.requestingQuestion = false
      this.playingQuestion = false
      this.streamingAssistantText = ''
      this.answerRevealReady = true
      this.handleInsightSignals(data)
    },

    handleInsightSignals(payload) {
      if (!payload || typeof payload !== 'object') return

      const confirmedInsight = String(payload.confirmed_insight || '').trim()
      if (confirmedInsight) {
        const exists = this.insightCards.some(item => item.text === confirmedInsight)
        if (!exists) {
          this.insightCards.push({
            id: `insight_${Date.now()}_${Math.random().toString(36).slice(2, 7)}`,
            text: confirmedInsight
          })
        }
        this.pendingInsightCandidate = null
      }

      const candidateInsight = String(payload.candidate_insight || '').trim()
      const candidateId = String(payload.candidate_id || '').trim()
      if (candidateInsight && candidateId) {
        this.pendingInsightCandidate = {
          candidate_id: candidateId,
          text: candidateInsight
        }
      }
    },

    extractQuestionFromJsonText(raw) {
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

      return ''
    },

    extractPartialQuestionText(payload) {
      const directText =
        payload?.delta ||
        payload?.message?.delta ||
        payload?.message?.partial_text ||
        ''

      const direct = String(directText || '').trim()

      if (
        direct &&
        !direct.includes('"status"') &&
        !direct.includes('"question"') &&
        !direct.startsWith('{')
      ) {
        return direct
      }

      const raw =
        String(payload?.raw || '') +
        String(payload?.content || '') +
        String(payload?.delta || '')

      if (!raw) return ''

      return this.extractQuestionFromJsonText(raw)
    },

    handleStreamPayload(payload) {
      if (payload.event === 'error') {
        throw new Error(payload.message || '流式生成失败')
      }

      if (payload.event === 'message_chunk') {
        this.requestingQuestion = true
        this.scrollChatToBottom()
        return
      }

      if (payload.event === 'message_done') {
        this.applyAskMessageDone(payload.data || {})
        return
      }

      if (payload.event === 'stage_done') {
        const data = payload.data || {}
        const stage = data.stage || {}
        const meta = data.meta || {}
        const stageState = data.stage_state || null
        this.receiveStagePayload(stage, meta, stageState)
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

    async requestAdvice(payload) {
      const response = await fetch('http://127.0.0.1:8002/api/advice/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || '请求失败')
      }

      return data
    },

    async fetchFirstQuestion() {
      this.loading = true
      this.errorMessage = ''

      try {
        const data = await this.requestAdvice({
          type: 'self_value',
          conversation_id: this.conversationId,
          round: this.round,
          answer: '',
          qa_history: [],
          stage_state: null
        })

        this.applyFirstQuestionPayload(data)
      } catch (error) {
        this.errorMessage = `获取第一题失败：${error.message}`
      } finally {
        this.loading = false
      }
    },

    async goNext() {
      if (this.isQuestionBusy) return

      const currentAnswer = this.getCurrentAnswer()

      if (!this.validateCurrentAnswer(currentAnswer)) {
        this.errorMessage = '请先输入你的回答。'
        return
      }

      this.requestingQuestion = true
      this.playingQuestion = false
      this.answerRevealReady = true
      this.streamingAssistantText = ''
      this.errorMessage = ''
      this.resetAskStreamingState()

      this.qaHistory.push({
        round: this.round,
        question: this.currentQuestion,
        type: this.questionType,
        options: this.questionType === 'single_choice' ? [...this.questionOptions] : [],
        answer: currentAnswer
      })
      this.appendDialogItem('user', currentAnswer)

      try {
        const response = await fetch('http://127.0.0.1:8002/api/advice/stream/', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            type: 'self_value',
            conversation_id: this.conversationId,
            round: this.round,
            answer: currentAnswer,
            qa_history: this.qaHistory,
            stage_state: this.stageState,
            pending_insight_candidate: this.pendingInsightCandidate
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

    extractStageItemText(item) {
      if (!item) return ''

      if (typeof item === 'string') {
        return item.replace(/^\{+/, '').replace(/\}+$/, '').trim()
      }

      const text =
        item.text ||
        item.content ||
        item.summary ||
        item.label ||
        item.title ||
        item.value ||
        ''

      if (typeof text === 'string') {
        return text.trim()
      }

      try {
        return JSON.stringify(text)
      } catch (e) {
        return ''
      }
    },

    cleanStageText(text) {
      const raw = String(text || '').trim()
      if (!raw) return ''

      if (
        raw.startsWith("{'id':") ||
        raw.startsWith('{"id":') ||
        raw.includes("'content':") ||
        raw.includes('"content":') ||
        raw.includes("'text':") ||
        raw.includes('"text":')
      ) {
        const contentMatch =
          raw.match(/['"]content['"]\s*:\s*['"]([\s\S]*?)['"]\s*(,|})/) ||
          raw.match(/['"]text['"]\s*:\s*['"]([\s\S]*?)['"]\s*(,|})/) ||
          raw.match(/['"]summary['"]\s*:\s*['"]([\s\S]*?)['"]\s*(,|})/)

        if (contentMatch && contentMatch[1]) {
          return contentMatch[1].trim()
        }
      }

      return raw
    },

    normalizeStageList(list, prefix) {
      const safeList = Array.isArray(list) ? list : []
      return safeList
        .map((item, index) => ({
          id: item.id || item[`${prefix}_id`] || `${prefix}_${index}`,
          text: this.cleanStageText(this.extractStageItemText(item))
        }))
        .filter(item => !!item.text)
    },

    mapCandidateStatus(status) {
      if (!status) return ''
      if (status === 'confirmed') return '已确认'
      if (status === 'rejected') return '已拒绝'
      if (status === 'revised') return '已修正'
      if (status === 'pending') return '待处理'
      return status
    },

    buildStageView(stage) {
      return {
        stage_name: stage?.stage_name || '',
        stage_summary: stage?.stage_summary || '',
        findings: Array.isArray(stage?.findings) ? stage.findings : [],
        judgements: Array.isArray(stage?.judgements) ? stage.judgements : [],
        confirmation_candidates: Array.isArray(stage?.confirmation_candidates)
          ? stage.confirmation_candidates
          : []
      }
    },

    normalizeStageTexts(list, prefix) {
      return this.normalizeStageList(list, prefix).map(item => item.text)
    },

    isStageTextSimilar(a, b) {
      const left = String(a || '').trim()
      const right = String(b || '').trim()
      if (!left || !right) return false
      if (left === right) return true
      return left.includes(right) || right.includes(left)
    },

    pickWeakestIndex(list) {
      let weakestIndex = -1
      let weakestScore = Number.POSITIVE_INFINITY
      list.forEach((text, idx) => {
        const score = String(text || '').trim().length
        if (score < weakestScore) {
          weakestScore = score
          weakestIndex = idx
        }
      })
      return weakestIndex
    },

    mergeStageTextList(currentList, incomingList, cap) {
      const merged = [...currentList]
      for (const incoming of incomingList) {
        if (!incoming) continue
        if (merged.some(current => this.isStageTextSimilar(current, incoming))) {
          continue
        }

        if (merged.length < cap) {
          merged.push(incoming)
          continue
        }

        const weakestIndex = this.pickWeakestIndex(merged)
        if (weakestIndex < 0) continue
        const weakest = merged[weakestIndex] || ''
        const incomingScore = incoming.length
        const weakestScore = weakest.length
        if (incomingScore >= weakestScore + 6) {
          merged.splice(weakestIndex, 1, incoming)
        }
      }
      return merged.slice(0, cap)
    },

    shouldKeepCandidate(candidateText, hasJudgement) {
      if (!hasJudgement) return false
      return String(candidateText || '').trim().length >= 8
    },

    buildCandidateItemsFromTexts(texts) {
      return texts.map((text, index) => ({
        candidate_id: `candidate_${index}_${String(text || '').slice(0, 8)}`,
        content: text
      }))
    },

    mergeStageViewConservative(currentView, incomingView) {
      const caps = {
        findings: 3,
        judgements: 2,
        confirmation_candidates: 2
      }

      const currentFindings = this.normalizeStageTexts(currentView?.findings || [], 'finding')
      const incomingFindings = this.normalizeStageTexts(incomingView?.findings || [], 'finding')
      const nextFindings = this.mergeStageTextList(currentFindings, incomingFindings, caps.findings)

      const currentJudgements = this.normalizeStageTexts(currentView?.judgements || [], 'judgement')
      const incomingJudgements = this.normalizeStageTexts(incomingView?.judgements || [], 'judgement')
      const nextJudgements = this.mergeStageTextList(currentJudgements, incomingJudgements, caps.judgements)

      const currentCandidates = this.normalizeStageTexts(currentView?.confirmation_candidates || [], 'candidate')
      const incomingCandidates = this.normalizeStageTexts(incomingView?.confirmation_candidates || [], 'candidate')
      const mergedCandidateTexts = this.mergeStageTextList(
        currentCandidates,
        incomingCandidates,
        caps.confirmation_candidates
      )
      const hasJudgement = nextJudgements.length > 0
      const nextCandidateTexts = mergedCandidateTexts
        .filter(text => this.shouldKeepCandidate(text, hasJudgement))
        .slice(0, caps.confirmation_candidates)

      const currentSummary = String(currentView?.stage_summary || '').trim()
      const incomingSummary = String(incomingView?.stage_summary || '').trim()
      let stageSummary = currentSummary
      if (!stageSummary && incomingSummary) {
        stageSummary = incomingSummary
      } else if (incomingSummary && incomingSummary.length >= currentSummary.length + 8) {
        stageSummary = incomingSummary
      }

      return {
        stage_name: incomingView?.stage_name || currentView?.stage_name || '',
        stage_summary: stageSummary,
        findings: nextFindings.map((text, index) => ({ id: `finding_${index}`, content: text })),
        judgements: nextJudgements.map((text, index) => ({ id: `judgement_${index}`, content: text })),
        confirmation_candidates: this.buildCandidateItemsFromTexts(nextCandidateTexts)
      }
    },

    hasEffectiveStageIncrement(currentView, nextView, currentMeta, nextMeta) {
      const currentDigest = this.buildStageDigest(currentView, currentMeta)
      const nextDigest = this.buildStageDigest(nextView, nextMeta)
      if (currentDigest === nextDigest) return false

      const currentScore =
        this.normalizeStageTexts(currentView?.findings || [], 'finding').length * 2 +
        this.normalizeStageTexts(currentView?.judgements || [], 'judgement').length * 3 +
        this.normalizeStageTexts(currentView?.confirmation_candidates || [], 'candidate').length * 2 +
        (String(currentView?.stage_summary || '').trim() ? 1 : 0) +
        (currentMeta?.can_transition ? 1 : 0)

      const nextScore =
        this.normalizeStageTexts(nextView?.findings || [], 'finding').length * 2 +
        this.normalizeStageTexts(nextView?.judgements || [], 'judgement').length * 3 +
        this.normalizeStageTexts(nextView?.confirmation_candidates || [], 'candidate').length * 2 +
        (String(nextView?.stage_summary || '').trim() ? 1 : 0) +
        (nextMeta?.can_transition ? 1 : 0)

      return nextScore >= currentScore
    },

    buildStageDigest(stageView, meta) {
      const findings = this.normalizeStageList(stageView.findings, 'finding').map(i => i.text).join('|')
      const judgements = this.normalizeStageList(stageView.judgements, 'judgement').map(i => i.text).join('|')
      const candidates = (Array.isArray(stageView.confirmation_candidates) ? stageView.confirmation_candidates : [])
        .map(i => this.cleanStageText(this.extractStageItemText(i)))
        .join('|')

      return JSON.stringify({
        stage_name: stageView.stage_name || '',
        stage_summary: stageView.stage_summary || '',
        findings,
        judgements,
        candidates,
        current_maturity: meta?.current_maturity || '',
        can_transition: !!meta?.can_transition
      })
    },

    shouldPromptStageUpdate(newStageView, newMeta) {
      const nextFindings = this.normalizeStageList(newStageView.findings, 'finding').length
      const nextJudgements = this.normalizeStageList(newStageView.judgements, 'judgement').length
      const nextCandidates = (Array.isArray(newStageView.confirmation_candidates)
        ? newStageView.confirmation_candidates
        : []).length

      const currentFindings = this.normalizedFindings.length
      const currentJudgements = this.normalizedJudgements.length
      const currentCandidates = this.normalizedCandidates.length

      if (this.round < 3 && !this.hasShownAnyStagePrompt) {
        return false
      }

      if (nextCandidates > currentCandidates) return true
      if (nextJudgements > currentJudgements) return true

      const currentSummary = String(this.stageView.stage_summary || '').trim()
      const nextSummary = String(newStageView.stage_summary || '').trim()

      if (!currentSummary && nextSummary && this.round >= 3) return true
      if (currentSummary !== nextSummary && nextSummary.length >= 18 && this.round >= 4) return true

      if (nextFindings >= 2 && nextFindings > currentFindings && this.round >= 4) return true
      if (newMeta?.can_transition && !this.stageMeta.can_transition) return true

      return false
    },

    commitStagePayload(stageView, meta, stageState) {
      this.stageView = stageView
      this.stageMeta = {
        can_transition: !!meta?.can_transition,
        current_stage_id: meta?.current_stage_id || '',
        current_maturity: meta?.current_maturity || ''
      }
      this.stageState = stageState || this.stageState
      this.lastStageDigest = this.buildStageDigest(stageView, meta)
    },

    receiveStagePayload(stage, meta = {}, stageState = null, options = {}) {
      const rawStageView = this.buildStageView(stage)

      if (
        !rawStageView.stage_name &&
        !rawStageView.stage_summary &&
        !rawStageView.findings.length &&
        !rawStageView.judgements.length &&
        !rawStageView.confirmation_candidates.length
      ) {
        return
      }

      const stageView = this.mergeStageViewConservative(this.stageView, rawStageView)
      const nextDigest = this.buildStageDigest(stageView, meta)

      if (options.forceCommit) {
        this.commitStagePayload(stageView, meta, stageState)
        return
      }

      if (nextDigest === this.lastStageDigest) {
        return
      }

      if (this.stageDrawerOpen) {
        this.commitStagePayload(stageView, meta, stageState)
        this.hasUnreadStageUpdate = false
        this.pendingStageView = null
        this.pendingStageMeta = null
        this.pendingStageState = null
        this.triggerStageInlineFlash()
        return
      }

      const shouldPrompt =
        !options.suppressPrompt &&
        this.hasEffectiveStageIncrement(this.stageView, stageView, this.stageMeta, meta)

      if (shouldPrompt) {
        this.pendingStageView = stageView
        this.pendingStageMeta = {
          can_transition: !!meta?.can_transition,
          current_stage_id: meta?.current_stage_id || '',
          current_maturity: meta?.current_maturity || ''
        }
        this.pendingStageState = stageState || this.stageState
        this.hasUnreadStageUpdate = true
        this.stageUpdateCount += 1
        this.hasShownAnyStagePrompt = true
        return
      }
    },

    openStageDrawer() {
      if (this.pendingStageView) {
        this.stageView = this.pendingStageView
        this.stageMeta = this.pendingStageMeta || this.stageMeta
        this.stageState = this.pendingStageState || this.stageState
        this.lastStageDigest = this.buildStageDigest(this.stageView, this.stageMeta)

        this.pendingStageView = null
        this.pendingStageMeta = null
        this.pendingStageState = null
      }

      this.hasUnreadStageUpdate = false
      this.stageDrawerOpen = true
    },

    closeStageDrawer() {
      this.stageDrawerOpen = false
    },

    async sendStageFeedback(candidateId, action) {
      if (this.isQuestionBusy || !candidateId) return

      this.feedbackBusy = true
      this.errorMessage = ''

      try {
        const response = await fetch('http://127.0.0.1:8002/api/stage-feedback/', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            type: 'self_value',
            conversation_id: this.conversationId,
            stage_state: this.stageState,
            candidate_id: candidateId,
            action,
            user_note: ''
          })
        })

        const data = await response.json()

        if (!response.ok) {
          throw new Error(data.error || '阶段反馈失败')
        }

        const nextStage = this.buildStageView(data.stage || {})
        const nextMeta = {
          can_transition: !!data?.meta?.can_transition,
          current_stage_id: data?.meta?.current_stage_id || '',
          current_maturity: data?.meta?.current_maturity || ''
        }

        this.stageView = nextStage
        this.stageMeta = nextMeta

        if (data.stage_state) {
          this.stageState = data.stage_state
        } else if (data.meta?.stage_state) {
          this.stageState = data.meta.stage_state
        }

        this.lastStageDigest = this.buildStageDigest(this.stageView, this.stageMeta)
      } catch (error) {
        this.errorMessage = `阶段反馈失败：${error.message}`
      } finally {
        this.feedbackBusy = false
      }
    },

    async enterNextStage() {
      if (this.isQuestionBusy || !this.stageMeta.can_transition) return

      this.transitionBusy = true
      this.errorMessage = ''

      try {
        const response = await fetch('http://127.0.0.1:8002/api/stage-transition/', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            type: 'self_value',
            conversation_id: this.conversationId,
            stage_state: this.stageState
          })
        })

        const data = await response.json()

        if (!response.ok) {
          throw new Error(data.error || '切换阶段失败')
        }

        const nextStage = this.buildStageView(data.stage || {})
        const nextMeta = {
          can_transition: !!data?.meta?.can_transition,
          current_stage_id: data?.meta?.current_stage_id || '',
          current_maturity: data?.meta?.current_maturity || ''
        }

        this.stageView = nextStage
        this.stageMeta = nextMeta

        if (data.stage_state) {
          this.stageState = data.stage_state
        } else if (data.meta?.stage_state) {
          this.stageState = data.meta.stage_state
        }

        this.lastStageDigest = this.buildStageDigest(this.stageView, this.stageMeta)
        this.hasUnreadStageUpdate = false
      } catch (error) {
        this.errorMessage = `切换阶段失败：${error.message}`
      } finally {
        this.transitionBusy = false
      }
    }
  },

  beforeUnmount() {
    if (this.playbackRafId) {
      window.cancelAnimationFrame(this.playbackRafId)
      this.playbackRafId = null
    }
    this.clearAnswerRevealTimer()
    if (this.stageInlineFlashTimer) {
      clearTimeout(this.stageInlineFlashTimer)
      this.stageInlineFlashTimer = null
    }
    window.removeEventListener('resize', this.updateViewportMode)
  },

  mounted() {
    this.tickQuestionPlayback = this.tickQuestionPlayback.bind(this)
    this.conversationId = this.buildConversationId()
    this.updateViewportMode()
    window.addEventListener('resize', this.updateViewportMode)

    if (this.prefetchedFirstQuestionReady && this.prefetchedFirstQuestion) {
      this.applyFirstQuestionPayload(this.prefetchedFirstQuestion)
      if (this.$store?.commit) {
        this.$store.commit('reset_first_question')
      }
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
  z-index: 2;
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 26px 20px 28px;
}

.questions-layout {
  width: 100%;
  max-width: 1180px;
  display: grid;
  grid-template-columns: minmax(0, 760px);
  justify-content: center;
  align-items: start;
  gap: 22px;
  transition: grid-template-columns 0.28s ease;
}

.questions-page--stage-open .questions-layout {
  grid-template-columns: minmax(0, 720px) minmax(320px, 380px);
}

.insight-panel {
  position: fixed;
  right: 22px;
  top: 96px;
  width: 260px;
  padding: 14px 14px 12px;
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.86);
  border: 1px solid rgba(31, 32, 35, 0.08);
  box-shadow: 0 10px 30px rgba(24, 26, 31, 0.08);
  backdrop-filter: blur(8px);
  z-index: 3;
}

.insight-panel__title {
  margin: 0 0 10px;
  font-size: 14px;
  color: #2a2d35;
}

.insight-panel__list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.insight-panel__item {
  font-size: 13px;
  line-height: 1.55;
  color: #3b3f48;
  padding: 9px 10px;
  border-radius: 10px;
  background: #f4f6fb;
}

.insight-panel__empty {
  font-size: 12px;
  color: #8d92a0;
}

@media (max-width: 1200px) {
  .insight-panel {
    display: none;
  }
}

.questions-container {
  width: 100%;
  max-width: 760px;
}

.questions-main {
  position: relative;
  display: flex;
  flex-direction: column;
  min-height: calc(100vh - 150px);
  gap: 10px;
}

.chat-thread {
  display: flex;
  flex-direction: column;
  gap: 10px;
  flex: 1;
  min-height: 0;
  overflow: auto;
  padding: 8px 6px 120px;
  scrollbar-width: thin;
  scrollbar-color: rgba(130, 124, 113, 0.32) transparent;
}

.chat-msg {
  display: flex;
  flex-direction: column;
  gap: 3px;
  max-width: 92%;
  padding: 8px 10px;
  border-radius: 12px;
  border: 1px solid rgba(176, 164, 145, 0.24);
  background: rgba(255, 255, 255, 0.6);
}

.chat-msg--assistant {
  align-self: flex-start;
}

.chat-msg--user {
  align-self: flex-end;
  background: rgba(243, 236, 224, 0.66);
}

.chat-msg--streaming {
  border-style: dashed;
}

.chat-msg__role {
  font-size: 11px;
  line-height: 1.2;
  color: #9a927f;
}

.chat-msg__text {
  font-size: 14px;
  line-height: 1.6;
  color: #3c3932;
  white-space: pre-wrap;
  word-break: break-word;
}

.chat-composer {
  position: sticky;
  bottom: 0;
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 10px;
  align-items: end;
  padding: 8px 0 2px;
  background: linear-gradient(
    to top,
    rgba(246, 240, 232, 0.96) 72%,
    rgba(246, 240, 232, 0)
  );
}

.chat-composer__input {
  width: 100%;
  min-height: 72px;
  max-height: 160px;
  resize: vertical;
  border: 1px solid rgba(176, 164, 145, 0.32);
  border-radius: 14px;
  padding: 12px 14px;
  font-size: 15px;
  line-height: 1.55;
  background: rgba(255, 255, 255, 0.84);
}

.chat-thread::-webkit-scrollbar {
  width: 8px;
}

.chat-thread::-webkit-scrollbar-track {
  background: transparent;
}

.chat-thread::-webkit-scrollbar-thumb {
  background: rgba(132, 124, 110, 0.28);
  border-radius: 999px;
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
  text-align: center;
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

.question-side-link-row {
  display: flex;
  justify-content: flex-end;
  margin-top: 2px;
  margin-bottom: 2px;
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

.question-btn--wide {
  width: 100%;
}

.questions-error {
  margin-top: 12px;
  font-size: 14px;
  line-height: 1.8;
  color: #b42318;
  text-align: center;
}

.stage-drawer {
  background: rgba(250, 248, 244, 0.96);
  box-shadow: 0 8px 30px rgba(41, 36, 30, 0.08);
  border: 1px solid rgba(198, 190, 178, 0.52);
  border-radius: 28px;
  display: flex;
  flex-direction: column;
  min-height: 720px;
  max-height: calc(100vh - 52px);
  overflow: hidden;
  position: sticky;
  top: 26px;
  z-index: 5;
}

.stage-drawer--overlay {
  position: fixed;
  top: 0;
  right: 0;
  width: min(420px, 100vw);
  height: 100vh;
  max-height: 100vh;
  border-radius: 0;
  z-index: 30;
  box-shadow: -10px 0 40px rgba(41, 36, 30, 0.12);
}

.stage-overlay {
  position: fixed;
  inset: 0;
  background: rgba(35, 32, 28, 0.18);
  backdrop-filter: blur(4px);
  z-index: 20;
}

.stage-drawer-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  padding: 24px 20px 18px;
  border-bottom: 1px solid rgba(212, 204, 193, 0.52);
}

.stage-drawer-kicker {
  font-size: 13px;
  line-height: 1.6;
  letter-spacing: 0.08em;
  color: #857d72;
}

.stage-drawer-stage-line {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 8px;
  flex-wrap: wrap;
}

.stage-drawer-title {
  margin: 0;
  font-size: 22px;
  line-height: 1.4;
  color: #26261f;
  font-weight: 500;
}

.stage-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 6px 10px;
  border-radius: 999px;
  font-size: 12px;
  line-height: 1;
  color: #5e564d;
  background: rgba(217, 209, 196, 0.55);
  border: 1px solid rgba(191, 181, 166, 0.6);
  white-space: nowrap;
}

.stage-inline-dot {
  width: 8px;
  height: 8px;
  border-radius: 999px;
  background: #6f86a2;
  box-shadow: 0 0 0 0 rgba(111, 134, 162, 0.45);
  animation: stageInlinePulse 0.9s ease-out 1;
}

.stage-drawer-close {
  appearance: none;
  border: none;
  background: rgba(240, 236, 229, 0.92);
  color: #655d53;
  width: 34px;
  height: 34px;
  border-radius: 999px;
  font-size: 22px;
  line-height: 1;
  cursor: pointer;
  flex: 0 0 auto;
}

.stage-drawer-body {
  flex: 1;
  overflow-y: auto;
  padding: 18px 20px 20px;
}

.stage-summary {
  margin: 0 0 18px;
  font-size: 15px;
  line-height: 2;
  color: #4d473f;
}

.stage-summary--empty {
  color: #938a7d;
}

.stage-structure-line {
  margin: 0 0 14px;
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  font-size: 12px;
  line-height: 1.6;
  color: #8c8378;
}

.stage-block {
  border-top: 1px solid rgba(212, 204, 193, 0.52);
  padding-top: 16px;
  margin-top: 16px;
}

.stage-block:first-of-type {
  border-top: none;
  padding-top: 0;
  margin-top: 0;
}

.stage-block-head {
  font-size: 13px;
  line-height: 1.6;
  letter-spacing: 0.06em;
  color: #8f867a;
  margin-bottom: 10px;
}

.stage-list,
.stage-candidate-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.stage-list-item,
.stage-candidate-item {
  border: 1px solid rgba(202, 194, 183, 0.56);
  border-radius: 18px;
  background: rgba(255, 253, 250, 0.78);
}

.stage-list-item {
  padding: 12px 14px;
  font-size: 14px;
  line-height: 1.9;
  color: #2b2721;
}

.stage-candidate-item {
  padding: 14px;
}

.stage-candidate-text {
  font-size: 14px;
  line-height: 1.9;
  color: #2b2721;
}

.stage-candidate-meta-row {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
  margin-top: 10px;
}

.candidate-flag,
.candidate-status {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 24px;
  border-radius: 999px;
  padding: 0 9px;
  font-size: 12px;
  line-height: 1;
}

.candidate-flag--blocking {
  color: #8b2d14;
  background: rgba(252, 228, 220, 0.9);
  border: 1px solid rgba(226, 171, 150, 0.65);
}

.candidate-status {
  color: #5f564b;
  background: rgba(217, 209, 196, 0.45);
  border: 1px solid rgba(191, 181, 166, 0.55);
}

.stage-candidate-actions {
  display: flex;
  gap: 8px;
  margin-top: 12px;
}

.mini-btn {
  appearance: none;
  border-radius: 999px;
  padding: 9px 14px;
  font-size: 13px;
  line-height: 1;
  cursor: pointer;
  transition: all 0.18s ease;
}

.mini-btn:disabled {
  opacity: 0.58;
  cursor: not-allowed;
}

.mini-btn--solid {
  border: none;
  color: #fff;
  background: #5c6873;
}

.mini-btn--solid:hover {
  background: #4f5a64;
}

.mini-btn--ghost {
  border: 1px solid rgba(179, 170, 158, 0.8);
  color: #4f4942;
  background: rgba(255, 253, 250, 0.72);
}

.mini-btn--ghost:hover {
  background: rgba(250, 246, 241, 0.92);
}

.stage-empty {
  font-size: 14px;
  line-height: 1.8;
  color: #9a9083;
}

.stage-drawer-foot {
  padding: 16px 20px 18px;
  border-top: 1px solid rgba(212, 204, 193, 0.52);
  background: rgba(250, 248, 244, 0.98);
}

.stage-meta-line {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-bottom: 12px;
  font-size: 13px;
  line-height: 1.7;
  color: #857d72;
}

.stage-transition-ready {
  color: #56616a;
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

.stage-overlay-fade-enter-active,
.stage-overlay-fade-leave-active {
  transition: opacity 0.22s ease;
}

.stage-overlay-fade-enter-from,
.stage-overlay-fade-leave-to {
  opacity: 0;
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
    color: #6a5840;
    background-color: rgba(232, 191, 118, 0.22);
    box-shadow: 0 0 0 6px rgba(232, 191, 118, 0.08);
  }

  52% {
    color: #6a5840;
    background-color: rgba(232, 191, 118, 0.16);
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

@keyframes stageInlinePulse {
  0% {
    transform: scale(0.92);
    box-shadow: 0 0 0 0 rgba(111, 134, 162, 0.45);
  }
  65% {
    transform: scale(1.05);
    box-shadow: 0 0 0 7px rgba(111, 134, 162, 0);
  }
  100% {
    transform: scale(1);
    box-shadow: 0 0 0 0 rgba(111, 134, 162, 0);
  }
}

@media (max-width: 980px) {
  .questions-layout,
  .questions-page--stage-open .questions-layout {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .questions-shell {
    align-items: flex-start;
    padding: 20px 16px 18px;
  }

  .questions-main {
    grid-template-rows: 188px 284px auto auto;
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
    margin-top: 6px;
    margin-bottom: 2px;
  }

  .question-side-link {
    font-size: 12px;
    gap: 6px;
    padding: 4px 8px;
  }

  .question-side-link__icon {
    width: 14px;
    height: 14px;
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

  .questions-page-bg {
    filter: blur(74px);
    opacity: 0.3;
  }
}

@media (max-width: 430px) {
  .questions-main {
    grid-template-rows: 180px 270px auto auto;
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

  .answer-stage,
  .question-answer-area {
    height: 270px;
  }

  .question-textarea {
    height: 214px;
  }

  .question-btn {
    width: 100%;
  }

  .questions-actions {
    flex-direction: column;
  }

  .stage-candidate-actions {
    flex-direction: column;
  }

  .mini-btn {
    width: 100%;
  }
}
</style>
