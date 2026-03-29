import { useEffect, useState } from 'react';
import { useRouter, usePathname } from 'next/navigation';

export function useAuth() {
  const router = useRouter();
  const pathname = usePathname();
  const [user, setUser] = useState<{username: string, role: string, permissions: string[]} | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const storedUser = localStorage.getItem('user');
    if (!storedUser) {
      if (pathname !== '/') router.push('/');
    } else {
      const parsedUser = JSON.parse(storedUser);
      setUser(parsedUser);
      
      // The login handler now guarantees that role is strictly mapped
      // to ADMIN, MANAGER, OWNER, or VENDOR before it enters localStorage
      const role = (parsedUser.role || '').toUpperCase();
      if (pathname.includes('/portal')) {
        if (role === 'VENDOR' && !pathname.includes('/portal/vendor')) {
          router.push('/portal/vendor');
        } else if (role === 'OWNER' && !pathname.includes('/portal/owner')) {
          router.push('/portal/owner');
        } else if (role === 'MANAGER' && !pathname.includes('/portal/manager')) {
          router.push('/portal/manager');
        } else if (role === 'ADMIN' && !pathname.includes('/portal/admin')) {
          router.push('/portal/admin');
        }
      }
    }
    setLoading(false);
  }, [router, pathname]);
  return { user, loading };
}
