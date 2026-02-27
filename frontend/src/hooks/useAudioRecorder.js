import { useState, useRef, useCallback } from 'react';

const API_BASE = import.meta.env.VITE_API_URL || '';

/**
 * Pick the best available audio MIME type for high-quality recording.
 * Opus codec gives much better speech recognition than default WebM.
 */
function getBestMimeType() {
    const types = [
        'audio/webm;codecs=opus',
        'audio/ogg;codecs=opus',
        'audio/webm',
    ];
    for (const type of types) {
        if (MediaRecorder.isTypeSupported(type)) return type;
    }
    return '';
}

export function useAudioRecorder() {
    const [isRecording, setIsRecording] = useState(false);
    const [isProcessing, setIsProcessing] = useState(false);
    const mediaRecorderRef = useRef(null);
    const chunksRef = useRef([]);

    const startRecording = useCallback(async () => {
        try {
            // Request high-quality mono audio optimized for speech
            const stream = await navigator.mediaDevices.getUserMedia({
                audio: {
                    channelCount: 1,
                    sampleRate: 16000,
                    echoCancellation: true,
                    noiseSuppression: true,
                    autoGainControl: true,
                }
            });

            const mimeType = getBestMimeType();
            const options = { audioBitsPerSecond: 128000 };
            if (mimeType) options.mimeType = mimeType;

            const mediaRecorder = new MediaRecorder(stream, options);
            mediaRecorderRef.current = mediaRecorder;
            chunksRef.current = [];

            mediaRecorder.ondataavailable = (e) => {
                if (e.data.size > 0) chunksRef.current.push(e.data);
            };

            // Collect data every 250ms for smoother recording
            mediaRecorder.start(250);
            setIsRecording(true);
        } catch (err) {
            console.error('Microphone access denied:', err);
            throw new Error('Microphone access denied. Please allow microphone permissions.');
        }
    }, []);

    const stopRecording = useCallback(() => {
        return new Promise((resolve, reject) => {
            const mediaRecorder = mediaRecorderRef.current;
            if (!mediaRecorder || mediaRecorder.state === 'inactive') {
                reject(new Error('No active recording'));
                return;
            }

            mediaRecorder.onstop = async () => {
                setIsRecording(false);
                setIsProcessing(true);

                try {
                    const mimeType = mediaRecorder.mimeType || 'audio/webm';
                    const ext = mimeType.includes('ogg') ? 'ogg' : 'webm';
                    const blob = new Blob(chunksRef.current, { type: mimeType });
                    const formData = new FormData();
                    formData.append('file', blob, `recording.${ext}`);

                    const response = await fetch(`${API_BASE}/api/transcribe/live`, {
                        method: 'POST',
                        body: formData,
                    });

                    const data = await response.json();
                    setIsProcessing(false);

                    if (data.success && data.text) {
                        resolve(data.text);
                    } else {
                        reject(new Error(data.error || 'No speech detected'));
                    }
                } catch (err) {
                    setIsProcessing(false);
                    reject(err);
                }

                // Stop all tracks
                mediaRecorder.stream.getTracks().forEach(t => t.stop());
            };

            mediaRecorder.stop();
        });
    }, []);

    return { isRecording, isProcessing, startRecording, stopRecording };
}
