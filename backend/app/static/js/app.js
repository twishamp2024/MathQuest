/**
 * MathQuest Child-Facing Web Application Logic.
 */

const App = {
  state: {
    learner: null,
    session: null,
    currentQuestion: null,
    questionStartTime: 0,
    hintsUsedThisQuestion: 0,
    selectedOption: null,
    numericInputVal: '',
    selectedTopicFilter: null,
  },

  init() {
    this.bindEvents();
    this.loadSavedProfile();
    this.checkBackendHealth();
  },

  async checkBackendHealth() {
    try {
      const health = await API.getHealth();
      console.log("Backend healthy:", health);
    } catch (e) {
      console.warn("Backend connectivity issue:", e);
    }
  },

  bindEvents() {
    // Navigation tabs
    document.querySelectorAll('.nav-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        sounds.playClick();
        document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
        document.querySelectorAll('.view-section').forEach(s => s.classList.remove('active'));
        btn.classList.add('active');
        const target = btn.dataset.tab;
        document.getElementById(`tab-${target}`).classList.add('active');
        if (target === 'mastery' && this.state.learner) {
          this.renderMasteryScreen();
        }
      });
    });

    // Create profile button
    const createBtn = document.getElementById('btn-create-profile');
    if (createBtn) {
      createBtn.addEventListener('click', () => this.handleCreateProfile());
    }

    // Resume profile button
    const resumeBtn = document.getElementById('btn-resume-profile');
    if (resumeBtn) {
      resumeBtn.addEventListener('click', () => this.handleResumeProfile());
    }

    // Start learning session button
    const startBtn = document.getElementById('btn-start-session');
    if (startBtn) {
      startBtn.addEventListener('click', () => this.handleStartSession());
    }

    // Hint buttons
    const hint1Btn = document.getElementById('btn-hint-1');
    if (hint1Btn) {
      hint1Btn.addEventListener('click', () => this.requestHint(1));
    }
    const hint2Btn = document.getElementById('btn-hint-2');
    if (hint2Btn) {
      hint2Btn.addEventListener('click', () => this.requestHint(2));
    }

    // Next question button
    const nextBtn = document.getElementById('btn-next-question');
    if (nextBtn) {
      nextBtn.addEventListener('click', () => this.fetchNextQuestion());
    }

    // Keypad numeric buttons
    document.querySelectorAll('.key-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        sounds.playClick();
        const action = btn.dataset.key;
        this.handleKeypadInput(action);
      });
    });

    // Submit numeric answer button
    const submitNumBtn = document.getElementById('btn-submit-numeric');
    if (submitNumBtn) {
      submitNumBtn.addEventListener('click', () => {
        if (this.state.numericInputVal.trim().length > 0) {
          this.submitAnswer(this.state.numericInputVal.trim());
        }
      });
    }

    // Switch profile button
    const switchBtn = document.getElementById('btn-switch-learner');
    if (switchBtn) {
      switchBtn.addEventListener('click', () => {
        localStorage.removeItem('mathquest_learner_id');
        this.state.learner = null;
        this.state.session = null;
        this.updateProfileUI();
        document.getElementById('screen-welcome').style.display = 'block';
        document.getElementById('screen-play').style.display = 'none';
      });
    }
  },

  async loadSavedProfile() {
    const savedId = localStorage.getItem('mathquest_learner_id');
    if (savedId) {
      try {
        const profile = await API.getLearner(savedId);
        this.setLearner(profile);
      } catch (err) {
        localStorage.removeItem('mathquest_learner_id');
      }
    }
  },

  setLearner(profile) {
    this.state.learner = profile;
    localStorage.setItem('mathquest_learner_id', profile.id);
    this.updateProfileUI();
    document.getElementById('screen-welcome').style.display = 'none';
    document.getElementById('screen-play').style.display = 'block';
    this.populateTopicSelector();
  },

  updateProfileUI() {
    const aliasEl = document.getElementById('header-learner-alias');
    const streakEl = document.getElementById('header-streak-count');
    if (this.state.learner) {
      aliasEl.textContent = this.state.learner.display_alias;
      streakEl.textContent = `🔥 ${this.state.learner.current_streak}`;
    } else {
      aliasEl.textContent = 'Guest Learner';
      streakEl.textContent = '🔥 0';
    }
  },

  async handleCreateProfile() {
    sounds.playClick();
    const aliasInput = document.getElementById('input-alias');
    const alias = aliasInput ? aliasInput.value.trim() : '';
    try {
      const profile = await API.createLearner(alias || null);
      this.setLearner(profile);
    } catch (err) {
      alert("Failed to create profile: " + err.message);
    }
  },

  async handleResumeProfile() {
    sounds.playClick();
    const idInput = document.getElementById('input-resume-id');
    const id = idInput ? idInput.value.trim() : '';
    if (!id) {
      alert("Please enter a valid Learner ID token.");
      return;
    }
    try {
      const profile = await API.getLearner(id);
      this.setLearner(profile);
    } catch (err) {
      alert("Profile not found. Check the ID token and try again.");
    }
  },

  async populateTopicSelector() {
    const selectEl = document.getElementById('select-topic-filter');
    if (!selectEl) return;
    try {
      const curriculum = await API.getCurriculum();
      selectEl.innerHTML = '<option value="">🎯 All Topics (Adaptive Journey)</option>';
      curriculum.topics.forEach(t => {
        const opt = document.createElement('option');
        opt.value = t.id;
        opt.textContent = `${t.order}. ${t.title}`;
        selectEl.appendChild(opt);
      });
    } catch (e) {
      console.warn("Could not load topics list:", e);
    }
  },

  async handleStartSession() {
    sounds.playClick();
    if (!this.state.learner) return;

    const selectEl = document.getElementById('select-topic-filter');
    this.state.selectedTopicFilter = (selectEl && selectEl.value) ? selectEl.value : null;

    try {
      const session = await API.startSession(
        this.state.learner.id,
        this.state.selectedTopicFilter,
        'adaptive'
      );
      this.state.session = session;
      document.getElementById('session-start-box').style.display = 'none';
      document.getElementById('question-active-box').style.display = 'block';
      this.fetchNextQuestion();
    } catch (err) {
      alert("Could not start learning session: " + err.message);
    }
  },

  async fetchNextQuestion() {
    sounds.playClick();
    this.resetQuestionUI();
    document.getElementById('btn-next-question').style.display = 'none';

    try {
      const question = await API.getNextQuestion(
        this.state.learner.id,
        this.state.session ? this.state.session.id : null,
        this.state.selectedTopicFilter
      );
      this.renderQuestion(question);
    } catch (err) {
      alert("Error loading question: " + err.message);
    }
  },

  renderQuestion(q) {
    this.state.currentQuestion = q;
    this.state.questionStartTime = Date.now();
    this.state.hintsUsedThisQuestion = 0;
    this.state.numericInputVal = '';

    // Header info
    document.getElementById('q-topic-tag').textContent = q.topic_title;
    document.getElementById('q-difficulty-stars').textContent = '★'.repeat(q.difficulty) + '☆'.repeat(5 - q.difficulty);
    document.getElementById('q-prompt-text').textContent = q.question_text;
    document.getElementById('q-recommendation-note').textContent = q.recommendation_reason || '';

    // Render answer controls based on format
    const optsContainer = document.getElementById('options-container');
    const keypadContainer = document.getElementById('keypad-container');

    if (q.question_format === 'multiple_choice' || q.question_format === 'comparison') {
      optsContainer.style.display = 'grid';
      keypadContainer.style.display = 'none';
      optsContainer.innerHTML = '';

      (q.options || []).forEach(opt => {
        const btn = document.createElement('button');
        btn.className = 'option-btn';
        btn.textContent = opt;
        btn.addEventListener('click', () => {
          sounds.playClick();
          this.submitAnswer(opt);
        });
        optsContainer.appendChild(btn);
      });
    } else {
      // Numeric or text entry
      optsContainer.style.display = 'none';
      keypadContainer.style.display = 'block';
      document.getElementById('numeric-display').textContent = '0';
    }
  },

  handleKeypadInput(key) {
    let current = this.state.numericInputVal;
    if (key === 'clear') {
      current = '';
    } else if (key === 'backspace') {
      current = current.slice(0, -1);
    } else if (key === '-' && current.length === 0) {
      current = '-';
    } else if (key === '/' && !current.includes('/')) {
      current += '/';
    } else if (key === '.' && !current.includes('.')) {
      current += '.';
    } else if (!isNaN(parseInt(key))) {
      if (current.length < 12) current += key;
    }
    this.state.numericInputVal = current;
    document.getElementById('numeric-display').textContent = current || '0';
  },

  async requestHint(level) {
    sounds.playClick();
    if (!this.state.currentQuestion) return;

    this.state.hintsUsedThisQuestion++;
    try {
      const hintRes = await API.getHint(
        this.state.learner.id,
        this.state.currentQuestion.question_id,
        level
      );
      const hintCard = document.getElementById('hint-display-card');
      hintCard.innerHTML = `<strong>💡 Hint (Level ${level}):</strong> ${hintRes.hint_text}`;
      if (hintRes.step_by_step && hintRes.step_by_step.length > 0) {
        hintCard.innerHTML += `<br><span style="font-size:0.85rem">Steps: ${hintRes.step_by_step.join(' &rarr; ')}</span>`;
      }
      hintCard.classList.add('show');
    } catch (e) {
      console.warn("Hint error:", e);
    }
  },

  async submitAnswer(submittedAnswer) {
    if (!this.state.currentQuestion) return;

    const responseTimeMs = Date.now() - this.state.questionStartTime;
    const qId = this.state.currentQuestion.question_id;
    const sessId = this.state.session ? this.state.session.id : null;

    // Disable all options buttons to prevent double-submits
    document.querySelectorAll('.option-btn').forEach(b => (b.disabled = true));

    try {
      const result = await API.submitAnswer(
        this.state.learner.id,
        qId,
        sessId,
        submittedAnswer,
        responseTimeMs,
        this.state.hintsUsedThisQuestion
      );

      // Audio & Visual feedback
      if (result.is_correct) {
        sounds.playCorrect();
        if (result.current_streak >= 3 && result.current_streak % 3 === 0) {
          sounds.playStreakFanfare();
        }
      } else {
        sounds.playIncorrect();
      }

      this.showAnswerFeedback(result);

      // Update cached profile streak
      if (this.state.learner) {
        this.state.learner.current_streak = result.current_streak;
        if (result.highest_streak > this.state.learner.highest_streak) {
          this.state.learner.highest_streak = result.highest_streak;
        }
        this.updateProfileUI();
      }
    } catch (err) {
      alert("Submission error: " + err.message);
    }
  },

  showAnswerFeedback(res) {
    const feedbackBox = document.getElementById('answer-feedback-box');
    feedbackBox.className = `feedback-box show ${res.is_correct ? 'correct' : 'incorrect'}`;

    let html = `<strong>${res.is_correct ? '🎉 Correct!' : '❌ Not Quite'}</strong> ${res.feedback_message}`;
    if (res.detected_misconception) {
      html += `<br><div style="margin-top:0.5rem; font-weight:600;">🧠 Insight: ${res.detected_misconception}</div>`;
    }
    feedbackBox.innerHTML = html;

    // Highlight correct option if multiple choice
    document.querySelectorAll('.option-btn').forEach(btn => {
      if (btn.textContent.trim() === res.correct_answer.trim()) {
        btn.classList.add('correct-highlight');
      } else if (btn.textContent.trim() === res.submitted_answer.trim() && !res.is_correct) {
        btn.classList.add('wrong-highlight');
      }
    });

    // Show Next Question button
    document.getElementById('btn-next-question').style.display = 'block';
  },

  resetQuestionUI() {
    const feedbackBox = document.getElementById('answer-feedback-box');
    feedbackBox.className = 'feedback-box';
    feedbackBox.innerHTML = '';
    const hintCard = document.getElementById('hint-display-card');
    hintCard.className = 'hint-card';
    hintCard.innerHTML = '';
    document.querySelectorAll('.option-btn').forEach(b => {
      b.className = 'option-btn';
      b.disabled = false;
    });
  },

  async renderMasteryScreen() {
    if (!this.state.learner) return;
    const container = document.getElementById('mastery-topics-container');
    container.innerHTML = '<p>Loading curriculum and your mastery scores...</p>';

    try {
      const stats = await API.getLearnerStats(this.state.learner.id);
      const curriculum = await API.getCurriculum();

      container.innerHTML = '';
      curriculum.topics.forEach(topic => {
        const score = stats.mastery_by_topic[topic.id] || 0.50;
        const pct = Math.round(score * 100);

        const card = document.createElement('div');
        card.className = 'topic-card';
        card.innerHTML = `
          <div class="topic-card-title">
            <span>${topic.order}. ${topic.title}</span>
            <span>${pct}%</span>
          </div>
          <div class="progress-bar-wrap">
            <div class="progress-fill" style="width: ${pct}%;"></div>
          </div>
          <div style="font-size: 0.85rem; color: #64748b;">
            ${topic.concepts.map(c => c.title).join(' • ')}
          </div>
        `;
        container.appendChild(card);
      });
    } catch (err) {
      container.innerHTML = `<p style="color:red">Failed to load mastery data: ${err.message}</p>`;
    }
  },
};

document.addEventListener('DOMContentLoaded', () => App.init());
