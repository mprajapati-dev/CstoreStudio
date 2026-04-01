import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;
  
  if (pathname.startsWith('/portal/')) {
    const roleCookie = request.cookies.get('userRole')?.value;
    
    if (!roleCookie) {
      return NextResponse.redirect(new URL('/', request.url));
    }

    const role = roleCookie.toUpperCase();

    const portalRoleMap: Record<string, string> = {
      '/portal/manager': 'MANAGER',
      '/portal/owner': 'OWNER',
      '/portal/vendor': 'VENDOR',
      '/portal/admin': 'ADMIN'
    };

    // Find if the path requires a specific role
    for (const [route, expectedRole] of Object.entries(portalRoleMap)) {
      if (pathname.startsWith(route)) {
        if (role !== expectedRole && role !== 'ADMIN') {
          // If trying to access owner but is manager, redirect to manager
          // Or strictly fallback to their own portal
          const fallbackPath = portalRoleMap[`/portal/${role.toLowerCase()}`] ? `/portal/${role.toLowerCase()}` : '/';
          return NextResponse.redirect(new URL(fallbackPath, request.url));
        }
      }
    }
  }

  return NextResponse.next();
}

export const config = {
  matcher: ['/portal/:path*']
};
