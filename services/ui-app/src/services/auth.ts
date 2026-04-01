export function logoutUser() {
  localStorage.removeItem('user');
  document.cookie = 'userRole=; Max-Age=0; path=/';
  window.location.href = '/';
}
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function loginUser(username: string, password: string) {
  const res = await fetch(`${API_URL}/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password })
  });
  
  const data = await res.json();
  
  if (!res.ok) {
    throw new Error(data.detail || 'Login failed');
  }
  
  const rawRole = (data.role || '').toUpperCase().trim();
  let standardRole = 'UNKNOWN';
  if (rawRole.includes('ADMIN') || rawRole.includes('SUPER')) {
    standardRole = 'ADMIN';
  } else if (rawRole.includes('MANAGER')) {
    standardRole = 'MANAGER';
  } else if (rawRole.includes('OWNER')) {
    standardRole = 'OWNER';
  } else if (rawRole.includes('VENDOR')) {
    standardRole = 'VENDOR';
  }

  return { ...data, role: standardRole };
}
