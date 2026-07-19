import AsyncStorage from '@react-native-async-storage/async-storage';

// In development mode, point to local FastAPI server, otherwise production
export const API_BASE = typeof __DEV__ !== 'undefined' && __DEV__
  ? 'http://localhost:8000/api'
  : 'https://autoclipper.sir-l.web.id/api';

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

export async function getClip(clipId: number) {
  return request(`/clips/${clipId}`);
}

export async function updateClip(clipId: number, data: { title: string; start: number; end: number; subtitle: string }) {
  return request(`/clips/${clipId}/edit`, {
    method: 'PUT',
    body: JSON.stringify(data),
  });
}

export async function getPublicSettings(): Promise<{ payment_enabled: boolean; midtrans_client_key: string }> {
  // Use raw fetch because this endpoint is public and does not need authentication headers
  const resp = await fetch(`${API_BASE}/settings/public`);
  if (!resp.ok) throw new Error('Gagal memuat pengaturan publik');
  return resp.json();
}

export async function createCheckout(credits: number, amount: number): Promise<{ order_id: string; token: string; redirect_url: string }> {
  return request('/payments/checkout', {
    method: 'POST',
    body: JSON.stringify({ credits, amount }),
  });
}

export async function loginWithPassword(email: string, password: string): Promise<{ status: string; api_key: string; user: any }> {
  const resp = await fetch(`${API_BASE}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  });
  if (!resp.ok) {
    const err = await resp.json().catch(() => ({ detail: 'Login gagal' }));
    throw new Error(err.detail || 'Email atau password salah');
  }
  return resp.json();
}

export async function registerWithPassword(name: string, email: string, password: string): Promise<{ status: string; api_key: string; user: any }> {
  const resp = await fetch(`${API_BASE}/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name, email, password }),
  });
  if (!resp.ok) {
    const err = await resp.json().catch(() => ({ detail: 'Registrasi gagal' }));
    throw new Error(err.detail || 'Registrasi gagal');
  }
  return resp.json();
}
