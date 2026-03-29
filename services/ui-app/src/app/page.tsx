'use client';
import { useState } from 'react';
import { useRouter } from 'next/navigation';

export default function Home() {
  const router = useRouter();
  const [username, setUsername] = useState('manager');
  const [password, setPassword] = useState('manager');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    
    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
      });
      
      const data = await res.json();
      
      if (!res.ok) {
        setError(data.detail || 'Login failed');
        setLoading(false);
        return;
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

      // Ensure the standard role is passed into localStorage so the whole app knows
      const normalizedData = { ...data, role: standardRole };
      localStorage.setItem('user', JSON.stringify(normalizedData));
      
      // Redirect based on standard role
      switch (standardRole) {
        case 'ADMIN':
          router.push('/portal/admin');
          break;
        case 'MANAGER':
          router.push('/portal/manager');
          break;
        case 'OWNER':
          router.push('/portal/owner');
          break;
        case 'VENDOR':
          router.push('/portal/vendor');
          break;
        default:
          setError('Unknown role: ' + rawRole);
          break;
      }
    } catch (err) {
      setError('Connection error');
    }
    setLoading(false);
  };

  return (
    <main className="min-h-screen bg-gray-100 flex flex-col items-center justify-center p-8">
      <div className="w-full max-w-md bg-white p-8 rounded-xl shadow-lg">
        <h1 className="text-3xl font-bold text-center mb-6 text-gray-900">CstoreStudio Login</h1>
        
        {error && <div className="bg-red-50 text-red-600 p-3 rounded mb-4 text-sm text-center">{error}</div>}
        
        <form onSubmit={handleLogin} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Username</label>
            <input 
              type="text" 
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full p-3 border rounded focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-gray-900" 
              required 
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Password</label>
            <input 
              type="password" 
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full p-3 border rounded focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-gray-900" 
              required 
            />
          </div>
          <button 
            type="submit" 
            disabled={loading}
            className="w-full bg-blue-600 text-white font-bold p-3 rounded hover:bg-blue-700 transition"
          >
            {loading ? "Logging in..." : "Login"}
          </button>
        </form>

        <div className="mt-8 text-sm text-gray-500">
           <p className="font-bold border-b pb-1 mb-2">Demo Credentials:</p>
           <ul className="space-y-1">
             <li><span className="font-mono bg-gray-100 px-1">manager/manager</span> - Create tickets, Verify</li>
             <li><span className="font-mono bg-gray-100 px-1">owner/owner</span> - Approval, Payment</li>
             <li><span className="font-mono bg-gray-100 px-1">vendor1/vendor1</span> - Fixes, Invoices</li>
             <li><span className="font-mono bg-gray-100 px-1">admin/admin</span> - Full Access</li>
           </ul>
        </div>
      </div>
    </main>
  );
}
