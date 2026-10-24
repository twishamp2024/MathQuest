/**
 * MathQuest Web Audio API Sound Synthesizer.
 * Provides authentic hardware buzzer and cheerful game sound effects with zero external asset dependencies.
 */

class SoundEngine {
  constructor() {
    this.ctx = null;
    this.enabled = true;
  }

  init() {
    if (!this.ctx) {
      const AudioContext = window.AudioContext || window.webkitAudioContext;
      if (AudioContext) {
        this.ctx = new AudioContext();
      }
    }
    if (this.ctx && this.ctx.state === 'suspended') {
      this.ctx.resume();
    }
  }

  playTone(freq, type = 'sine', duration = 0.12, volume = 0.15) {
    if (!this.enabled) return;
    this.init();
    if (!this.ctx) return;

    try {
      const osc = this.ctx.createOscillator();
      const gain = this.ctx.createGain();

      osc.type = type;
      osc.frequency.setValueAtTime(freq, this.ctx.currentTime);

      gain.gain.setValueAtTime(volume, this.ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.001, this.ctx.currentTime + duration);

      osc.connect(gain);
      gain.connect(this.ctx.destination);

      osc.start();
      osc.stop(this.ctx.currentTime + duration);
    } catch (e) {
      console.warn("Audio playTone error:", e);
    }
  }

  // Cheerful correct chime
  playCorrect() {
    this.init();
    const notes = [523.25, 659.25, 783.99, 1046.50]; // C5, E5, G5, C6
    notes.forEach((freq, idx) => {
      setTimeout(() => {
        this.playTone(freq, 'triangle', 0.18, 0.18);
      }, idx * 75);
    });
  }

  // Gentle error buzz
  playIncorrect() {
    this.init();
    this.playTone(180, 'sawtooth', 0.25, 0.18);
    setTimeout(() => {
      this.playTone(140, 'sawtooth', 0.35, 0.20);
    }, 120);
  }

  // Key click / button press
  playClick() {
    this.playTone(800, 'sine', 0.04, 0.08);
  }

  // Hardware ESP32 Buzzer Beep
  playHwBeep(freq = 2400, duration = 0.08) {
    // Authentic piezo square wave
    this.playTone(freq, 'square', duration, 0.12);
  }

  playStreakFanfare() {
    this.init();
    const notes = [587.33, 659.25, 783.99, 880.00, 1046.50];
    notes.forEach((freq, idx) => {
      setTimeout(() => {
        this.playTone(freq, 'sine', 0.22, 0.20);
      }, idx * 80);
    });
  }
}

const sounds = new SoundEngine();
