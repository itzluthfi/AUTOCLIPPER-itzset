import AsyncStorage from '@react-native-async-storage/async-storage';

const API_BASE = 'https://autoclipper.sir-l.web.id/api';

let apiKey: string | null = null;

export async function setApiKey(key: string) {
  apiKey = key;
  await AsyncStorage.setItem('api_key', key);
}

export async function loadApiKey() {
  const key = await AsyncStorage.getItem('api_key');
  apiKey = key;
  return key;
}

export async function getApiKey() {
  if (!apiKey) {
    apiKey = await AsyncStorage.getItem('api_key');
  }
  return apiKey;
}

export async function logout() {
  apiKey = null;
  await AsyncStorage.removeItem('api_key');
  await AsyncStorage.removeItem('user');
}

async function request(path: string, options: RequestInit = {}) {
  const key = await getApiKey();
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...((options.headers as Record<string, string>) || {}),
  };
  if (key) {
    headers['X-API-Key'] = key;
  }

  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }

  return response.json();
}

export async function getHealth() {
  return request('/../health');
}

export async function submitVideo(url: string, mode: string = 'heuristic', tracking: string = 'center') {
  return request('/videos/submit', {
    method: 'POST',
    body: JSON.stringify({ url, mode, tracking }),
  });
}

export async function listVideos() {
  return request('/videos');
}

export async function getVideo(videoId: number) {
  return request(`/videos/${videoId}`);
}

export async function downloadClip(clipId: number): Promise<string> {
  const key = await getApiKey();
  return `${API_BASE}/clips/${clipId}/download?key=${key}`;
}

export async function getCredits() {
  return request('/credits');
}

export async function getUser() {
  return request('/user/me');
}

export async function checkCookieStatus() {
  return request('/cookie/status');
}

export async function uploadCookie(file: File) {
  const key = await getApiKey();
  const formData = new FormData();
  formData.append('file', file);
  const response = await fetch(`${API_BASE}/cookie/upload`, {
    method: 'POST',
    headers: { 'X-API-Key': key || '' },
    body: formData,
  });
  if (!response.ok) {
    const err = await response.json().catch(() => ({ detail: 'Upload failed' }));
    throw new Error(err.detail);
  }
  return response.json();
}
