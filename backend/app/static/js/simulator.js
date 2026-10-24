/**
 * Virtual ESP32 Toy Hardware Simulator.
 * Emulates the SSD1306 128x64 OLED display, 4 tactile buttons, 3 LEDs, and Piezo buzzer.
 */

const Simulator = {
  state: {
    hwState: 'BOOT', // BOOT, READY, FETCHING, QUESTION, FEEDBACK
    cursorIndex: 0,
    currentQuestion: null,
    learnerId: null,
    sessionId: null,
    feedbackText: '',
    isCorrect: false,
    wifiConnected: false,
  },

  init() {
    this.bindButtons();
    this.bootSequence();
  },

  bindButtons() {
    // Physical button clicks
    const btnUp = document.getElementById('hw-btn-up');
    const btnDown = document.getElementById('hw-btn-down');
    const btnSelect = document.getElementById('hw-btn-select');
    const btnHint = document.getElementById('hw-btn-hint');

    if (btnUp) btnUp.addEventListener('click', () => this.handleButton('UP'));
    if (btnDown) btnDown.addEventListener('click', () => this.handleButton('DOWN'));
    if (btnSelect) btnSelect.addEventListener('click', () => this.handleButton('SELECT'));
    if (btnHint) btnHint.addEventListener('click', () => this.handleButton('HINT'));

    // Keyboard navigation when Simulator tab is focused
    window.addEventListener('keydown', (e) => {
      const simTab = document.getElementById('tab-simulator');
      if (!simTab || !simTab.classList.contains('active')) return;

      if (e.key === 'ArrowUp' || e.key === 'w' || e.key === 'W') {
        e.preventDefault();
        this.handleButton('UP');
      } else if (e.key === 'ArrowDown' || e.key === 's' || e.key === 'S') {
        e.preventDefault();
        this.handleButton('DOWN');
      } else if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        this.handleButton('SELECT');
      } else if (e.key === 'h' || e.key === 'H' || e.key === 'Escape') {
        e.preventDefault();
        this.handleButton('HINT');
      }
    });
  },

  setLed(name, active) {
    const el = document.getElementById(`led-${name}`);
    if (el) {
      if (active) el.classList.add('active');
      else el.classList.remove('active');
    }
  },

  pulseLed(name, durationMs = 800) {
    this.setLed(name, true);
    setTimeout(() => this.setLed(name, false), durationMs);
  },

  async bootSequence() {
    this.state.hwState = 'BOOT';
    this.renderOled("MATHQUEST ESP32", "Booting firmware v1.0.0...", "Connecting Wi-Fi...");
    sounds.playHwBeep(1800, 0.05);

    // Flash blue LED
    this.pulseLed('wifi', 1200);

    setTimeout(async () => {
      try {
        await API.getHealth();
        this.state.wifiConnected = true;
        this.setLed('wifi', true);

        // Auto-assign or retrieve learner
        const savedId = localStorage.getItem('mathquest_learner_id');
        if (savedId) {
          this.state.learnerId = savedId;
        } else {
          const profile = await API.createLearner('Toy Explorer');
          this.state.learnerId = profile.id;
          localStorage.setItem('mathquest_learner_id', profile.id);
        }

        sounds.playHwBeep(2400, 0.08);
        this.state.hwState = 'READY';
        this.renderOled(
          "MATHQUEST READY",
          `User: ${this.state.learnerId.slice(0, 8)}`,
          "Press [SEL] to start!"
        );
      } catch (err) {
        this.renderOled("ERR: NO WI-FI", "Cannot reach backend", "Check server port 8000");
        this.pulseLed('error', 1500);
      }
    }, 1500);
  },

  renderOled(title, line1, line2, line3 = "") {
    document.getElementById('oled-status-left').textContent = title || "MATHQUEST";
    document.getElementById('oled-status-right').textContent = this.state.wifiConnected ? "WIFI:OK" : "NO-WIFI";

    const bodyEl = document.getElementById('oled-content-body');
    bodyEl.innerHTML = `<div>${line1}</div><div style="margin-top:4px;">${line2}</div><div style="margin-top:4px;">${line3}</div>`;
    document.getElementById('oled-footer-text').textContent = "[UP/DN] Move  [SEL] Enter";
  },

  renderQuestionOled() {
    const q = this.state.currentQuestion;
    if (!q) return;

    document.getElementById('oled-status-left').textContent = `D${q.difficulty} | ${q.topic_id.slice(0, 8)}`;
    document.getElementById('oled-status-right').textContent = "ONLINE";

    const bodyEl = document.getElementById('oled-content-body');
    const opts = q.options || ["1", "2", "3", "4"];

    let optsHtml = '<div style="margin-top:6px;">';
    opts.forEach((opt, idx) => {
      const isSel = idx === this.state.cursorIndex;
      const marker = isSel ? '▶ ' : '  ';
      optsHtml += `<div class="oled-opt-item ${isSel ? 'selected' : ''}">${marker}${opt}</div>`;
    });
    optsHtml += '</div>';

    bodyEl.innerHTML = `
      <div style="font-weight:bold; color:#fff;">${q.question_text}</div>
      ${optsHtml}
    `;

    document.getElementById('oled-footer-text').textContent = "[▲▼] Select  [SEL] Submit";
  },

  async handleButton(btn) {
    sounds.playHwBeep(2200, 0.04);

    if (this.state.hwState === 'READY') {
      if (btn === 'SELECT') {
        await this.fetchNextHardwareQuestion();
      }
      return;
    }

    if (this.state.hwState === 'FEEDBACK') {
      if (btn === 'SELECT') {
        await this.fetchNextHardwareQuestion();
      }
      return;
    }

    if (this.state.hwState === 'QUESTION') {
      const opts = this.state.currentQuestion ? this.state.currentQuestion.options : [];
      const count = opts ? opts.length : 4;

      if (btn === 'UP') {
        this.state.cursorIndex = (this.state.cursorIndex - 1 + count) % count;
        this.renderQuestionOled();
      } else if (btn === 'DOWN') {
        this.state.cursorIndex = (this.state.cursorIndex + 1) % count;
        this.renderQuestionOled();
      } else if (btn === 'SELECT') {
        await this.submitHardwareAnswer();
      } else if (btn === 'HINT') {
        await this.showHardwareHint();
      }
    }
  },

  async fetchNextHardwareQuestion() {
    this.state.hwState = 'FETCHING';
    this.renderOled("FETCHING...", "Loading next adaptive", "question from AI/Engine...");

    try {
      const q = await API.getNextQuestion(this.state.learnerId, this.state.sessionId);
      this.state.currentQuestion = q;
      this.state.cursorIndex = 0;
      this.state.hwState = 'QUESTION';
      this.renderQuestionOled();
    } catch (err) {
      this.renderOled("FETCH ERROR", "Failed loading question", "Press [SEL] to retry");
      this.pulseLed('error', 1000);
      this.state.hwState = 'READY';
    }
  },

  async submitHardwareAnswer() {
    if (!this.state.currentQuestion) return;

    const q = this.state.currentQuestion;
    const chosenAnswer = q.options ? q.options[this.state.cursorIndex] : "0";

    this.renderOled("EVALUATING...", `Answer: ${chosenAnswer}`, "Verifying with server...");

    try {
      const result = await API.submitAnswer(
        this.state.learnerId,
        q.question_id,
        this.state.sessionId,
        chosenAnswer,
        5000,
        0
      );

      this.state.hwState = 'FEEDBACK';
      if (result.is_correct) {
        this.pulseLed('success', 1200);
        sounds.playCorrect();
        this.renderOled(
          "★ CORRECT! ★",
          `Streak: ${result.current_streak}`,
          "Mastery updated! [SEL] Next"
        );
      } else {
        this.pulseLed('error', 1200);
        sounds.playIncorrect();
        this.renderOled(
          "✖ INCORRECT ✖",
          `Ans: ${result.correct_answer}`,
          "[SEL] Try Next Question"
        );
      }
    } catch (err) {
      this.renderOled("SUBMIT ERROR", "Network failure", "Press [SEL] to retry");
      this.state.hwState = 'READY';
    }
  },

  async showHardwareHint() {
    if (!this.state.currentQuestion) return;
    try {
      const hintRes = await API.getHint(this.state.learnerId, this.state.currentQuestion.question_id, 1);
      const hintText = hintRes.hint_text.slice(0, 50);
      this.renderOled("💡 HINT", hintText, "Press [SEL] to resume");
      sounds.playHwBeep(1500, 0.08);
      setTimeout(() => {
        if (this.state.hwState === 'QUESTION') {
          this.renderQuestionOled();
        }
      }, 3500);
    } catch (e) {
      console.warn("Hint error:", e);
    }
  },
};

document.addEventListener('DOMContentLoaded', () => Simulator.init());
