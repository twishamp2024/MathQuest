/**
 * MathQuest Client API Service.
 */

const API = {
  BASE_URL: '/api/v1',

  async request(endpoint, options = {}) {
    const url = `${this.BASE_URL}${endpoint}`;
    const defaultHeaders = { 'Content-Type': 'application/json' };
    
    try {
      const response = await fetch(url, {
        ...options,
        headers: { ...defaultHeaders, ...(options.headers || {}) },
      });
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Request failed with status ${response.status}`);
      }
      return await response.json();
    } catch (err) {
      console.error(`API Error [${endpoint}]:`, err);
      throw err;
    }
  },

  async getHealth() {
    return this.request('/health');
  },

  async createLearner(displayAlias = null, avatarIcon = 'rocket') {
    return this.request('/learners', {
      method: 'POST',
      body: JSON.stringify({ display_alias: displayAlias, avatar_icon: avatarIcon }),
    });
  },

  async getLearner(learnerId) {
    return this.request(`/learners/${encodeURIComponent(learnerId)}`);
  },

  async getLearnerStats(learnerId) {
    return this.request(`/learners/${encodeURIComponent(learnerId)}/stats`);
  },

  async startSession(learnerId, topicFilter = null, gameMode = 'adaptive') {
    return this.request('/sessions', {
      method: 'POST',
      body: JSON.stringify({
        learner_id: learnerId,
        topic_filter: topicFilter,
        game_mode: gameMode,
      }),
    });
  },

  async getNextQuestion(learnerId, sessionId = null, topicFilter = null) {
    let params = new URLSearchParams({ learner_id: learnerId });
    if (sessionId) params.append('session_id', sessionId);
    if (topicFilter) params.append('topic_filter', topicFilter);
    return this.request(`/questions/next?${params.toString()}`);
  },

  async submitAnswer(learnerId, questionId, sessionId, submittedAnswer, responseTimeMs = 0, hintsUsed = 0) {
    return this.request('/questions/answer', {
      method: 'POST',
      body: JSON.stringify({
        learner_id: learnerId,
        question_id: questionId,
        session_id: sessionId,
        submitted_answer: String(submittedAnswer),
        response_time_ms: responseTimeMs,
        hints_used: hintsUsed,
      }),
    });
  },

  async getHint(learnerId, questionId, hintLevel = 1) {
    return this.request('/questions/hint', {
      method: 'POST',
      body: JSON.stringify({
        learner_id: learnerId,
        question_id: questionId,
        hint_level: hintLevel,
      }),
    });
  },

  async getCurriculum() {
    return this.request('/content/curriculum');
  },

  async checkFirmware(currentVersion = '1.0.0', deviceModel = 'esp32-devkit-v1') {
    return this.request('/firmware/check', {
      method: 'POST',
      body: JSON.stringify({
        current_version: currentVersion,
        device_model: deviceModel,
        channel: 'stable',
      }),
    });
  },
};
