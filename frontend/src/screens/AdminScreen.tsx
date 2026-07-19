import React, { useEffect, useState, useCallback, useRef } from 'react';
import { View, Text, TouchableOpacity, ScrollView, TextInput, RefreshControl, ActivityIndicator, Platform } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useTheme } from '../theme/ThemeContext';
import { SkeletonLoader } from '../components/SkeletonLoader';

const API_BASE = 'https://autoclipper.sir-l.web.id/api';

type Tab = 'dashboard' | 'users' | 'queue' | 'videos' | 'system';

async function apiGet(path: string) {
  const resp = await fetch(`${API_BASE}${path}`, {
    headers: { 'X-API-Key': await getApiKey() },
  });
  if (!resp.ok) throw new Error((await resp.json()).detail || 'Error');
  return resp.json();
}

async function apiPost(path: string, data?: any) {
  const resp = await fetch(`${API_BASE}${path}`, {
    method: 'POST',
    headers: { ...(data ? {'Content-Type': 'application/json'} : {}), 'X-API-Key': await getApiKey() },
    body: data ? JSON.stringify(data) : undefined,
  });
  if (!resp.ok) throw new Error((await resp.json()).detail || 'Error');
  return resp.json();
}

async function apiPut(path: string, data: any) {
  const resp = await fetch(`${API_BASE}${path}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json', 'X-API-Key': await getApiKey() },
    body: JSON.stringify(data),
  });
  if (!resp.ok) throw new Error((await resp.json()).detail || 'Error');
  return resp.json();
}

function getApiKey(): Promise<string | null> {
  return import('../services/api').then(m => m.getApiKey());
}

const statusColor = (status: string, colors: any) => {
  switch (status) {
    case 'completed': case 'ready': case 'uploaded': return colors.success;
    case 'processing': case 'downloading': case 'pending': return colors.warning;
    case 'failed': return colors.error;
    default: return colors.muted;
  }
};

const statusLabel = (status: string) => {
  switch (status) {
    case 'completed': return 'Selesai';
    case 'processing': case 'downloading': return 'Memproses';
    case 'pending': return 'Antri';
    case 'failed': return 'Gagal';
    case 'ready': return 'Siap';
    case 'uploaded': return 'Terupload';
    default: return status;
  }
};

export default function AdminScreen({ navigation }: any) {
  const { colors, isDark } = useTheme();
  const [tab, setTab] = useState<Tab>('dashboard');
  const [refreshing, setRefreshing] = useState(false);

  const tabs = [
    { key: 'dashboard' as Tab, label: 'Dashboard', icon: 'grid' },
    { key: 'users' as Tab, label: 'Users', icon: 'people' },
    { key: 'queue' as Tab, label: 'Antrian', icon: 'time' },
    { key: 'videos' as Tab, label: 'Video', icon: 'videocam' },
    { key: 'system' as Tab, label: 'Sistem', icon: 'server' },
  ];

  return (
    <View style={{ flex: 1, backgroundColor: colors.background }}>
      <View style={{
        paddingTop: Platform.OS === 'ios' ? 50 : 10,
        paddingBottom: 12, paddingHorizontal: 16,
        backgroundColor: colors.card, borderBottomWidth: 1, borderBottomColor: colors.border,
      }}>
        <Text style={{ fontSize: 20, fontWeight: '700', color: colors.text }}>Admin Panel</Text>
      </View>

      {/* Tab Navigation */}
      <View style={{
        flexDirection: 'row', paddingHorizontal: 8, paddingVertical: 8,
        borderBottomWidth: 1, borderBottomColor: colors.border,
        backgroundColor: colors.card,
      }}>
        {tabs.map(t => (
          <TouchableOpacity key={t.key} onPress={() => setTab(t.key)}
            style={{
              flex: 1, alignItems: 'center', paddingVertical: 8, borderRadius: 8,
              backgroundColor: tab === t.key ? colors.primary + '20' : 'transparent',
            }}
          >
            <Ionicons name={t.icon as any} size={18} color={tab === t.key ? colors.primary : colors.muted} />
            <Text style={{ fontSize: 11, marginTop: 2, color: tab === t.key ? colors.primary : colors.muted, fontWeight: tab === t.key ? '600' : '400' }}>
              {t.label}
            </Text>
          </TouchableOpacity>
        ))}
      </View>

      {tab === 'dashboard' && <DashboardTab colors={colors} isDark={isDark} navigation={navigation} />}
      {tab === 'users' && <UsersTab colors={colors} isDark={isDark} />}
      {tab === 'queue' && <QueueTab colors={colors} isDark={isDark} />}
      {tab === 'videos' && <VideosTab colors={colors} isDark={isDark} />}
      {tab === 'system' && <SystemTab colors={colors} isDark={isDark} />}
    </View>
  );
}

/* ─── Dashboard Tab ──────────────────────────────────── */
function DashboardTab({ colors, isDark, navigation }: any) {
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => { fetchStats(); }, []);

  const fetchStats = async () => {
    setLoading(true);
    try { setStats(await apiGet('/admin/stats')); } catch (e: any) { console.error(e.message); }
    setLoading(false);
  };

  if (loading) return <View style={{ padding: 16, gap: 8 }}><SkeletonLoader height={80} /><SkeletonLoader height={80} /></View>;

  const cards = stats ? [
    { name: 'Users', icon: 'people' as const, value: stats.total_users, color: colors.primary },
    { name: 'Videos', icon: 'videocam' as const, value: stats.total_videos, color: colors.accent },
    { name: 'Clips', icon: 'film' as const, value: stats.total_clips, color: colors.success },
    { name: 'Server', icon: 'server' as const, value: 'Aktif', color: colors.warning },
  ] : [];

  return (
    <ScrollView style={{ flex: 1, padding: 16 }} refreshControl={<RefreshControl refreshing={false} onRefresh={fetchStats} />}>
      <View style={{ flexDirection: 'row', flexWrap: 'wrap', marginHorizontal: -4 }}>
        {cards.map((item, i) => (
          <View key={i} style={{ width: '50%', paddingHorizontal: 4, marginBottom: 8 }}>
            <View style={{ padding: 16, borderRadius: 12, backgroundColor: colors.card, borderWidth: 1, borderColor: colors.border }}>
              <View style={{ flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between' }}>
                <View style={{ width: 36, height: 36, borderRadius: 12, backgroundColor: item.color + '30', alignItems: 'center', justifyContent: 'center' }}>
                  <Ionicons name={item.icon} size={20} color={item.color} />
                </View>
                <Text style={{ fontSize: 20, fontWeight: '700', color: colors.text }}>{item.value}</Text>
              </View>
              <Text style={{ color: colors.muted, fontSize: 13, marginTop: 8 }}>{item.name}</Text>
            </View>
          </View>
        ))}
      </View>

      {/* ─── Admin Test Clip ─── */}
      <View style={{ padding: 16, borderRadius: 12, marginTop: 8, backgroundColor: colors.primary + '15', borderWidth: 1, borderColor: colors.primary + '30' }}>
        <Text style={{ fontWeight: '700', color: colors.text, marginBottom: 4, fontSize: 15 }}>Coba Fitur Clip (Admin)</Text>
        <Text style={{ color: colors.muted, fontSize: 12, marginBottom: 12 }}>
          Admin bisa testing clip tanpa perlu cookie/credits.
        </Text>
        <AdminTestClipForm colors={colors} isDark={isDark} navigation={navigation} />
      </View>
    </ScrollView>
  );
}

/* ─── Admin Test Clip Form ──────────────────────────── */
function AdminTestClipForm({ colors, isDark, navigation }: any) {
  const [url, setUrl] = useState('');
  const [mode, setMode] = useState('heuristic');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);

  const handleTest = async () => {
    if (!url.trim()) return;
    setLoading(true);
    setResult(null);
    try {
      const res = await apiPost('/admin/clip/test', { url: url.trim(), mode });
      setResult(res);
    } catch (e: any) {
      setResult({ error: e.message });
    }
    setLoading(false);
  };

  return (
    <View>
      <TextInput
        value={url}
        onChangeText={setUrl}
        placeholder="https://youtube.com/watch?v=..."
        placeholderTextColor={colors.muted}
        autoCapitalize="none"
        style={{
          backgroundColor: isDark ? '#0f0f0f' : '#f8fafc',
          borderWidth: 1, borderColor: colors.border, borderRadius: 8,
          padding: 10, fontSize: 13, color: colors.text, marginBottom: 8,
        }}
      />
      <View style={{ flexDirection: 'row', gap: 6, marginBottom: 8 }}>
        {['heuristic', 'ai'].map(m => (
          <TouchableOpacity key={m} onPress={() => setMode(m)}
            style={{
              paddingHorizontal: 14, paddingVertical: 6, borderRadius: 6,
              backgroundColor: mode === m ? colors.primary : colors.border,
            }}
          >
            <Text style={{ color: mode === m ? '#fff' : colors.text, fontSize: 12, fontWeight: '500' }}>
              {m.charAt(0).toUpperCase() + m.slice(1)}
            </Text>
          </TouchableOpacity>
        ))}
      </View>
      <TouchableOpacity onPress={handleTest} disabled={loading}
        style={{ paddingVertical: 10, borderRadius: 8, backgroundColor: colors.primary, alignItems: 'center' }}
      >
        <Text style={{ color: '#fff', fontWeight: '600', fontSize: 13 }}>
          {loading ? 'Memproses...' : 'Test Clip'}
        </Text>
      </TouchableOpacity>
      {result && (
        <View style={{ marginTop: 8, padding: 10, borderRadius: 8, backgroundColor: result.error ? colors.error + '20' : colors.success + '20' }}>
          <Text style={{ color: result.error ? colors.error : colors.success, fontSize: 12 }}>
            {result.error ? `Gagal: ${result.error}` : `Video #${result.video_id} masuk antrian!`}
          </Text>
        </View>
      )}
    </View>
  );
}

/* ─── Users Tab ─────────────────────────────────────── */
function UsersTab({ colors, isDark }: any) {
  const [users, setUsers] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);
  const [newName, setNewName] = useState('');
  const [newEmail, setNewEmail] = useState('');
  const [newCredits, setNewCredits] = useState('10');
  const [newRole, setNewRole] = useState('free');
  const [createdUser, setCreatedUser] = useState<any>(null);
  const [editingCredits, setEditingCredits] = useState<{[key: number]: boolean}>({});
  const [creditValues, setCreditValues] = useState<{[key: number]: string}>({});
  const [selectedUserForCookie, setSelectedUserForCookie] = useState<number | null>(null);

  const fetchUsers = useCallback(async () => {
    setLoading(true);
    try { setUsers(await apiGet('/admin/users')); } catch (e: any) { console.error(e.message); }
    setLoading(false);
  }, []);

  useEffect(() => { fetchUsers(); }, []);

  const createUser = async () => {
    if (!newEmail.trim()) return;
    try {
      const result = await apiPost('/admin/users/create', {
        email: newEmail.trim(),
        name: newName.trim() || 'User',
        credits: parseInt(newCredits) || 3,
        role: newRole,
      });
      setCreatedUser(result);
      setNewEmail(''); setNewName(''); setNewCredits('10');
      fetchUsers();
    } catch (e: any) { alert(e.message); }
  };

  const saveCredits = async (userId: number) => {
    try {
      await apiPut(`/admin/users/${userId}/credits`, { credits: parseInt(creditValues[userId] || '0') });
      setEditingCredits({ ...editingCredits, [userId]: false });
      fetchUsers();
    } catch (e: any) { alert(e.message); }
  };

  const startEdit = (user: any) => {
    setCreditValues({ ...creditValues, [user.id]: String(user.credits) });
    setEditingCredits({ ...editingCredits, [user.id]: true });
  };

  const uploadCookieForUser = async (userId: number) => {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.json';
    input.onchange = async (e: any) => {
      const file = e.target.files?.[0];
      if (!file) return;
      const formData = new FormData();
      formData.append('file', file);
      formData.append('user_id', String(userId));
      try {
        const resp = await fetch(`${API_BASE}/admin/cookie/upload?user_id=${userId}`, {
          method: 'POST',
          headers: { 'X-API-Key': await getApiKey() },
          body: formData,
        });
        const json = await resp.json();
        if (json.status === 'ok') {
          alert('Cookie berhasil diupload!');
          fetchUsers();
        } else {
          alert('Gagal: ' + (json.detail || 'Error'));
        }
      } catch (e: any) {
        alert('Gagal upload: ' + e.message);
      }
    };
    input.click();
  };

  return (
    <ScrollView style={{ flex: 1, padding: 16 }} refreshControl={<RefreshControl refreshing={loading} onRefresh={fetchUsers} />}>
      {/* Create User Button */}
      <TouchableOpacity onPress={() => { setShowCreate(!showCreate); setCreatedUser(null); }}
        style={{ flexDirection: 'row', alignItems: 'center', marginBottom: 12, padding: 12, borderRadius: 10, backgroundColor: colors.primary + '20', borderWidth: 1, borderColor: colors.primary + '40' }}>
        <Ionicons name={showCreate ? 'chevron-up' : 'person-add'} size={18} color={colors.primary} style={{ marginRight: 8 }} />
        <Text style={{ color: colors.primary, fontWeight: '600' }}>{showCreate ? 'Tutup' : 'Buat User Baru'}</Text>
      </TouchableOpacity>

      {showCreate && (
        <View style={{ padding: 16, borderRadius: 12, backgroundColor: colors.card, borderWidth: 1, borderColor: colors.border, marginBottom: 16 }}>
          <Text style={{ fontWeight: '600', color: colors.text, marginBottom: 12 }}>Buat User Baru</Text>
          <TextInput value={newName} onChangeText={setNewName} placeholder="Nama" placeholderTextColor={colors.muted}
            style={inputStyle(colors, isDark)} />
          <TextInput value={newEmail} onChangeText={setNewEmail} placeholder="Email *" placeholderTextColor={colors.muted}
            autoCapitalize="none" style={inputStyle(colors, isDark)} />
          <TextInput value={newCredits} onChangeText={setNewCredits} placeholder="Kredit awal" placeholderTextColor={colors.muted}
            keyboardType="numeric" style={inputStyle(colors, isDark)} />
          <View style={{ flexDirection: 'row', gap: 6, marginBottom: 8 }}>
            {['free', 'paid', 'admin'].map(r => (
              <TouchableOpacity key={r} onPress={() => setNewRole(r)}
                style={{ paddingHorizontal: 12, paddingVertical: 6, borderRadius: 6, backgroundColor: newRole === r ? colors.primary : colors.border }}>
                <Text style={{ color: newRole === r ? '#fff' : colors.text, fontSize: 12 }}>{r}</Text>
              </TouchableOpacity>
            ))}
          </View>
          <TouchableOpacity onPress={createUser} style={{ paddingVertical: 12, borderRadius: 8, backgroundColor: colors.primary, alignItems: 'center', marginTop: 8 }}>
            <Text style={{ color: '#fff', fontWeight: '600' }}>Buat User</Text>
          </TouchableOpacity>
          {createdUser && (
            <View style={{ marginTop: 12, padding: 12, borderRadius: 8, backgroundColor: colors.success + '20', borderWidth: 1, borderColor: colors.success }}>
              <Text style={{ color: colors.success, fontWeight: '600', marginBottom: 4 }}>User berhasil dibuat!</Text>
              <Text style={{ color: colors.text, fontSize: 13 }}>Email: {createdUser.email}</Text>
              <Text style={{ color: colors.text, fontSize: 13 }}>Role: {createdUser.role}</Text>
              <Text style={{ color: colors.text, fontSize: 13, fontFamily: Platform.OS === 'web' ? 'monospace' : 'Courier' }}>API Key: {createdUser.api_key}</Text>
            </View>
          )}
        </View>
      )}

      {/* Users List */}
      <Text style={{ fontWeight: '600', color: colors.text, marginBottom: 8, fontSize: 15 }}>
        Pengguna ({users.length})
      </Text>
      {users.map((u: any) => (
        <View key={u.id} style={{ padding: 12, borderRadius: 10, backgroundColor: colors.card, borderWidth: 1, borderColor: colors.border, marginBottom: 6 }}>
          <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' }}>
            <View style={{ flex: 1 }}>
              <Text style={{ fontWeight: '600', color: colors.text, fontSize: 14 }}>{u.name}</Text>
              <Text style={{ color: colors.muted, fontSize: 12 }}>{u.email}</Text>
            </View>
            <View style={{ flexDirection: 'row', alignItems: 'center', gap: 4 }}>
              {/* Cookie indicator */}
              <TouchableOpacity onPress={() => uploadCookieForUser(u.id)}
                style={{ paddingHorizontal: 6, paddingVertical: 3, borderRadius: 6, backgroundColor: u.has_cookie ? colors.success + '20' : colors.warning + '20' }}>
                <Ionicons name={u.has_cookie ? "checkmark-circle" : "cloud-upload"} size={14} color={u.has_cookie ? colors.success : colors.warning} />
              </TouchableOpacity>
              {/* Role badge */}
              <View style={{ paddingHorizontal: 8, paddingVertical: 3, borderRadius: 6, backgroundColor: u.role === 'admin' ? colors.warning + '30' : colors.primary + '30' }}>
                <Text style={{ color: u.role === 'admin' ? colors.warning : colors.primary, fontSize: 11, fontWeight: '500' }}>{u.role}</Text>
              </View>
              {/* Credits edit */}
              {editingCredits[u.id] ? (
                <View style={{ flexDirection: 'row', gap: 4 }}>
                  <TextInput value={creditValues[u.id] || ''} onChangeText={(t) => setCreditValues({...creditValues, [u.id]: t})}
                    keyboardType="numeric" style={{ width: 60, padding: 4, borderRadius: 4, borderWidth: 1, borderColor: colors.border, color: colors.text, fontSize: 13, textAlign: 'center', backgroundColor: isDark ? '#0f0f0f' : '#f8fafc' }} />
                  <TouchableOpacity onPress={() => saveCredits(u.id)} style={{ padding: 4 }}><Ionicons name="checkmark" size={18} color={colors.success} /></TouchableOpacity>
                  <TouchableOpacity onPress={() => setEditingCredits({...editingCredits, [u.id]: false})} style={{ padding: 4 }}><Ionicons name="close" size={18} color={colors.error} /></TouchableOpacity>
                </View>
              ) : (
                <TouchableOpacity onPress={() => startEdit(u)} style={{ paddingHorizontal: 8, paddingVertical: 3, borderRadius: 6, backgroundColor: colors.success + '20' }}>
                  <Text style={{ color: colors.success, fontSize: 11, fontWeight: '500' }}>{u.credits} credits</Text>
                </TouchableOpacity>
              )}
            </View>
          </View>
        </View>
      ))}
    </ScrollView>
  );
}

/* ─── Queue Tab ─────────────────────────────────────── */
function QueueTab({ colors, isDark }: any) {
  const [queue, setQueue] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchQueue = useCallback(async () => {
    setLoading(true);
    try { setQueue(await apiGet('/admin/queue')); } catch (e: any) { console.error(e.message); }
    setLoading(false);
  }, []);

  useEffect(() => { fetchQueue(); const interval = setInterval(fetchQueue, 5000); return () => clearInterval(interval); }, []);

  if (loading) return <View style={{ padding: 16 }}><SkeletonLoader height={60} /><SkeletonLoader height={60} /></View>;

  return (
    <ScrollView style={{ flex: 1, padding: 16 }} refreshControl={<RefreshControl refreshing={loading} onRefresh={fetchQueue} />}>
      <Text style={{ fontWeight: '600', color: colors.text, marginBottom: 12, fontSize: 15 }}>
        Antrian Proses ({queue.length})
      </Text>
      {queue.length === 0 ? (
        <View style={{ padding: 24, borderRadius: 12, backgroundColor: colors.card, borderWidth: 1, borderColor: colors.border, alignItems: 'center' }}>
          <Ionicons name="checkmark-circle" size={40} color={colors.success} />
          <Text style={{ color: colors.muted, marginTop: 8 }}>Tidak ada antrian</Text>
        </View>
      ) : (
        queue.map((v: any) => (
          <View key={v.id} style={{ padding: 14, borderRadius: 10, backgroundColor: colors.card, borderWidth: 1, borderColor: colors.border, marginBottom: 8 }}>
            <View style={{ flexDirection: 'row', justifyContent: 'space-between', marginBottom: 4 }}>
              <Text style={{ fontWeight: '600', color: colors.text, flex: 1, fontSize: 13 }} numberOfLines={1}>
                {v.title || 'Video ' + v.youtube_id}
              </Text>
              <View style={{ paddingHorizontal: 8, paddingVertical: 3, borderRadius: 6, backgroundColor: statusColor(v.status, colors) + '20' }}>
                <Text style={{ color: statusColor(v.status, colors), fontSize: 11, fontWeight: '500' }}>{statusLabel(v.status)}</Text>
              </View>
            </View>
            <View style={{ flexDirection: 'row', justifyContent: 'space-between' }}>
              <Text style={{ color: colors.muted, fontSize: 11 }}>User: {v.user_name}</Text>
              <Text style={{ color: colors.muted, fontSize: 11 }}>{v.queued_for}s lalu</Text>
            </View>
          </View>
        ))
      )}
    </ScrollView>
  );
}

/* ─── Videos Tab ────────────────────────────────────── */
function VideosTab({ colors, isDark }: any) {
  const [videos, setVideos] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchVideos = useCallback(async () => {
    setLoading(true);
    try { setVideos(await apiGet('/admin/videos')); } catch (e: any) { console.error(e.message); }
    setLoading(false);
  }, []);

  useEffect(() => { fetchVideos(); }, []);

  if (loading) return <View style={{ padding: 16 }}><SkeletonLoader height={60} /><SkeletonLoader height={60} /></View>;

  return (
    <ScrollView style={{ flex: 1, padding: 16 }} refreshControl={<RefreshControl refreshing={loading} onRefresh={fetchVideos} />}>
      <Text style={{ fontWeight: '600', color: colors.text, marginBottom: 12, fontSize: 15 }}>
        Semua Video ({videos.length})
      </Text>
      {videos.length === 0 ? (
        <View style={{ padding: 24, borderRadius: 12, backgroundColor: colors.card, borderWidth: 1, borderColor: colors.border, alignItems: 'center' }}>
          <Ionicons name="videocam" size={40} color={colors.muted} />
          <Text style={{ color: colors.muted, marginTop: 8 }}>Belum ada video</Text>
        </View>
      ) : (
        videos.map((v: any) => (
          <View key={v.id} style={{ padding: 14, borderRadius: 10, backgroundColor: colors.card, borderWidth: 1, borderColor: colors.border, marginBottom: 8 }}>
            <View style={{ flexDirection: 'row', justifyContent: 'space-between', marginBottom: 4 }}>
              <Text style={{ fontWeight: '600', color: colors.text, flex: 1, fontSize: 13 }} numberOfLines={1}>
                {v.title || 'Video ' + v.youtube_id}
              </Text>
              <View style={{ paddingHorizontal: 8, paddingVertical: 3, borderRadius: 6, backgroundColor: statusColor(v.status, colors) + '20' }}>
                <Text style={{ color: statusColor(v.status, colors), fontSize: 11, fontWeight: '500' }}>{statusLabel(v.status)}</Text>
              </View>
            </View>
            <View style={{ flexDirection: 'row', justifyContent: 'space-between', gap: 4 }}>
              <Text style={{ color: colors.muted, fontSize: 11 }}>User: {v.user_name}</Text>
              <Text style={{ color: colors.muted, fontSize: 11 }}>
                {v.clips_count} klip · {v.duration ? Math.floor(v.duration / 60) + 'm' : '?'}
              </Text>
            </View>
            {v.error && <Text style={{ color: colors.error, fontSize: 11, marginTop: 4 }}>{v.error}</Text>}
          </View>
        ))
      )}
    </ScrollView>
  );
}

/* ─── System Tab ────────────────────────────────────── */
function SystemTab({ colors, isDark }: any) {
  const [sys, setSys] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try { setSys(await apiGet('/admin/system')); } catch (e: any) { console.error(e.message); }
      setLoading(false);
    })();
  }, []);

  if (loading) return <View style={{ padding: 16 }}><SkeletonLoader height={60} /></View>;
  if (!sys) return null;

  const items = [
    { label: 'CPU', value: sys.cpu_percent + '%', color: sys.cpu_percent > 80 ? (colors.error||'red') : (colors.success||'green') },
    { label: 'RAM', value: sys.memory_used_gb + 'GB / ' + sys.memory_total_gb + 'GB (' + sys.memory_percent + '%)', color: sys.memory_percent > 80 ? (colors.error||'red') : (colors.success||'green') },
    { label: 'Disk', value: sys.disk_used_gb + 'GB / ' + sys.disk_total_gb + 'GB (' + sys.disk_percent.toFixed(1) + '%)', color: sys.disk_percent > 85 ? (colors.error||'red') : (colors.warning||'orange') },
  ];

  return (
    <ScrollView style={{ flex: 1, padding: 16 }}>
      <Text style={{ fontWeight: '600', color: colors.text, marginBottom: 12, fontSize: 15 }}>Sistem Server</Text>
      {items.map((item, i) => (
        <View key={i} style={{ padding: 14, borderRadius: 10, backgroundColor: colors.card, borderWidth: 1, borderColor: colors.border, marginBottom: 8 }}>
          <View style={{ flexDirection: 'row', justifyContent: 'space-between', marginBottom: 6 }}>
            <Text style={{ fontWeight: '600', color: colors.text, fontSize: 14 }}>{item.label}</Text>
            <Text style={{ color: item.color, fontWeight: '600', fontSize: 13 }}>{item.value}</Text>
          </View>
          <View style={{ height: 6, borderRadius: 3, backgroundColor: isDark ? '#2a2a2a' : '#e2e8f0', overflow: 'hidden' }}>
            <View style={{
              width: item.label === 'CPU' ? sys.cpu_percent + '%' : item.label === 'RAM' ? sys.memory_percent + '%' : sys.disk_percent.toFixed(1) + '%',
              height: '100%', borderRadius: 3, backgroundColor: item.color,
            }} />
          </View>
        </View>
      ))}
      <View style={{ padding: 14, borderRadius: 10, backgroundColor: colors.card, borderWidth: 1, borderColor: colors.border }}>
        <Text style={{ fontWeight: '600', color: colors.text, marginBottom: 4, fontSize: 14 }}>Disk Free</Text>
        <Text style={{ color: colors.muted, fontSize: 13 }}>{sys.disk_free_gb} GB tersisa</Text>
      </View>
    </ScrollView>
  );
}

function inputStyle(colors: any, isDark: boolean) {
  return {
    backgroundColor: isDark ? '#0f0f0f' : '#f8fafc',
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: 8,
    padding: 10,
    fontSize: 14,
    color: colors.text,
    marginBottom: 8,
  };
}
