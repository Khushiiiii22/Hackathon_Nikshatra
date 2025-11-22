/**
 * Voice Input Service using Web Speech API
 * Handles voice recognition with error handling and fallbacks
 */

export interface VoiceRecognitionResult {
  transcript: string;
  confidence: number;
  isFinal: boolean;
}

export interface VoiceRecognitionError {
  error: string;
  message: string;
  fallback: boolean;
}

class VoiceService {
  private recognition: any = null;
  private isListening: boolean = false;
  private onResultCallback: ((result: VoiceRecognitionResult) => void) | null = null;
  private onErrorCallback: ((error: VoiceRecognitionError) => void) | null = null;
  private onStartCallback: (() => void) | null = null;
  private onEndCallback: (() => void) | null = null;

  constructor() {
    this.initializeRecognition();
  }

  /**
   * Initialize Web Speech API
   */
  private initializeRecognition(): void {
    // Check browser support
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;

    if (!SpeechRecognition) {
      console.warn('Speech recognition not supported in this browser');
      return;
    }

    try {
      this.recognition = new SpeechRecognition();
      this.recognition.continuous = false; // Stop after one result
      this.recognition.interimResults = true; // Get interim results
      this.recognition.lang = 'en-US';
      this.recognition.maxAlternatives = 1;

      // Event handlers
      this.recognition.onstart = () => {
        console.log('🎤 Voice recognition started');
        this.isListening = true;
        if (this.onStartCallback) {
          this.onStartCallback();
        }
      };

      this.recognition.onresult = (event: any) => {
        const results = event.results;
        const lastResult = results[results.length - 1];
        const transcript = lastResult[0].transcript;
        const confidence = lastResult[0].confidence;
        const isFinal = lastResult.isFinal;

        console.log('📝 Transcript:', transcript, '| Confidence:', confidence, '| Final:', isFinal);

        if (this.onResultCallback) {
          this.onResultCallback({
            transcript,
            confidence,
            isFinal,
          });
        }
      };

      this.recognition.onerror = (event: any) => {
        console.error('❌ Voice recognition error:', event.error);
        this.isListening = false;

        const errorMessages: Record<string, string> = {
          'no-speech': 'No speech detected. Please try speaking louder or closer to the microphone.',
          'audio-capture': 'Microphone not available. Please check your microphone settings.',
          'not-allowed': 'Microphone permission denied. Please enable microphone access in your browser settings.',
          'network': 'Network error. Please check your internet connection.',
          'aborted': 'Voice recognition was stopped.',
          'service-not-allowed': 'Voice recognition service is not available.',
        };

        const message = errorMessages[event.error] || 'An error occurred with voice recognition.';

        if (this.onErrorCallback) {
          this.onErrorCallback({
            error: event.error,
            message,
            fallback: true,
          });
        }
      };

      this.recognition.onend = () => {
        console.log('🛑 Voice recognition ended');
        this.isListening = false;
        if (this.onEndCallback) {
          this.onEndCallback();
        }
      };

    } catch (error) {
      console.error('Failed to initialize speech recognition:', error);
    }
  }

  /**
   * Check if voice recognition is supported
   */
  isSupported(): boolean {
    return this.recognition !== null;
  }

  /**
   * Check if currently listening
   */
  isActive(): boolean {
    return this.isListening;
  }

  /**
   * Start listening
   */
  start(): void {
    if (!this.recognition) {
      if (this.onErrorCallback) {
        this.onErrorCallback({
          error: 'not-supported',
          message: 'Voice recognition is not supported in this browser. Please type your message instead.',
          fallback: true,
        });
      }
      return;
    }

    if (this.isListening) {
      console.warn('Already listening');
      return;
    }

    try {
      this.recognition.start();
    } catch (error: any) {
      console.error('Failed to start voice recognition:', error);
      if (this.onErrorCallback) {
        this.onErrorCallback({
          error: 'start-failed',
          message: error.message || 'Failed to start voice recognition.',
          fallback: true,
        });
      }
    }
  }

  /**
   * Stop listening
   */
  stop(): void {
    if (this.recognition && this.isListening) {
      try {
        this.recognition.stop();
      } catch (error) {
        console.error('Failed to stop voice recognition:', error);
      }
    }
  }

  /**
   * Abort listening
   */
  abort(): void {
    if (this.recognition && this.isListening) {
      try {
        this.recognition.abort();
      } catch (error) {
        console.error('Failed to abort voice recognition:', error);
      }
    }
  }

  /**
   * Set result callback
   */
  onResult(callback: (result: VoiceRecognitionResult) => void): void {
    this.onResultCallback = callback;
  }

  /**
   * Set error callback
   */
  onError(callback: (error: VoiceRecognitionError) => void): void {
    this.onErrorCallback = callback;
  }

  /**
   * Set start callback
   */
  onStart(callback: () => void): void {
    this.onStartCallback = callback;
  }

  /**
   * Set end callback
   */
  onEnd(callback: () => void): void {
    this.onEndCallback = callback;
  }

  /**
   * Request microphone permission
   */
  async requestPermission(): Promise<boolean> {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      stream.getTracks().forEach(track => track.stop());
      return true;
    } catch (error: any) {
      console.error('Microphone permission denied:', error);
      if (this.onErrorCallback) {
        this.onErrorCallback({
          error: 'permission-denied',
          message: 'Microphone access is required for voice input. Please enable it in your browser settings.',
          fallback: true,
        });
      }
      return false;
    }
  }
}

// Singleton instance
const voiceService = new VoiceService();

export default voiceService;
