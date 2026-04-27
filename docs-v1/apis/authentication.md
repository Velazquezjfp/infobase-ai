# BAMF ACTE Companion - Authentication & Authorization

## Overview

This document describes the authentication and authorization mechanisms for the BAMF ACTE Companion application.

**Current Status:** The application currently uses a **simulated authentication system** with no real validation or token management. This documentation describes the planned production authentication architecture.

---

## Table of Contents

- [Current Implementation](#current-implementation)
- [Planned Authentication Architecture](#planned-authentication-architecture)
- [Authentication Flow](#authentication-flow)
- [Token Management](#token-management)
- [Authorization & Roles](#authorization--roles)
- [Security Best Practices](#security-best-practices)
- [Implementation Examples](#implementation-examples)

---

## Current Implementation

### Frontend-Only Simulation

**Source:** `src/pages/Login.tsx`, `src/contexts/AppContext.tsx`

The current implementation:
1. User enters username (no password validation)
2. Username stored in React Context (`AppContext`)
3. User object: `{ name: string }`
4. No actual authentication or token management
5. No session persistence (cleared on refresh)

**Login Flow:**
```typescript
// src/pages/Login.tsx (line 10-17)
const handleLogin = (e: React.FormEvent) => {
  e.preventDefault();
  if (name.trim()) {
    setUser({ name: name.trim() });
    navigate('/workspace');
  }
};
```

**Route Protection:**
```typescript
// src/pages/Workspace.tsx (line 17-21)
useEffect(() => {
  if (!user) {
    navigate('/');
  }
}, [user, navigate]);
```

**Logout:**
```typescript
// src/components/workspace/WorkspaceHeader.tsx
const handleLogout = () => {
  setUser(null);
  navigate('/');
};
```

**Limitations:**
- No actual authentication
- No password validation
- No session management
- No token storage
- No role-based access control
- State lost on page refresh

---

## Planned Authentication Architecture

### JWT-Based Authentication

The production system will use **JWT (JSON Web Tokens)** for stateless authentication:

1. **Access Token:** Short-lived token (1 hour) for API requests
2. **Refresh Token:** Long-lived token (7 days) for obtaining new access tokens
3. **Token Storage:** HttpOnly cookies or secure localStorage
4. **Token Validation:** Backend validates signature and expiration

### Security Features

- Password hashing (bcrypt/Argon2)
- HTTPS-only communication
- CSRF protection
- Rate limiting on auth endpoints
- Multi-factor authentication (planned)
- Session invalidation on logout
- Automatic token refresh

---

## Authentication Flow

### 1. Login Flow

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant API
    participant Database

    User->>Frontend: Enter credentials
    Frontend->>API: POST /auth/login
    API->>Database: Validate credentials
    Database-->>API: User record
    API->>API: Generate JWT tokens
    API-->>Frontend: Access + Refresh tokens
    Frontend->>Frontend: Store tokens
    Frontend-->>User: Redirect to /workspace
```

**Implementation:**

```typescript
// Planned authentication service
async function login(username: string, password: string) {
  const response = await fetch('/api/v1/auth/login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ username, password }),
  });

  if (!response.ok) {
    throw new Error('Authentication failed');
  }

  const data = await response.json();

  // Store tokens securely
  localStorage.setItem('accessToken', data.accessToken);
  localStorage.setItem('refreshToken', data.refreshToken);
  localStorage.setItem('user', JSON.stringify(data.user));

  return data;
}
```

**Request:**
```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "username": "bamf.officer@example.de",
  "password": "SecurePassword123!"
}
```

**Response (200 OK):**
```json
{
  "accessToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyLTEyMyIsInJvbGUiOiJvZmZpY2VyIiwiaWF0IjoxNzAyNzI1NjAwLCJleHAiOjE3MDI3MjkyMDB9.signature",
  "refreshToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyLTEyMyIsInR5cGUiOiJyZWZyZXNoIiwiaWF0IjoxNzAyNzI1NjAwLCJleHAiOjE3MDMzMzA0MDB9.signature",
  "tokenType": "Bearer",
  "expiresIn": 3600,
  "user": {
    "id": "user-123",
    "username": "bamf.officer@example.de",
    "name": "Maria Schmidt",
    "role": "officer",
    "permissions": [
      "cases:read",
      "cases:write",
      "documents:upload",
      "ai:use"
    ]
  }
}
```

**Error Response (401 Unauthorized):**
```json
{
  "error": "INVALID_CREDENTIALS",
  "message": "Username or password is incorrect"
}
```

---

### 2. Authenticated Request Flow

All API requests must include the access token in the Authorization header:

```typescript
async function fetchCases() {
  const token = localStorage.getItem('accessToken');

  const response = await fetch('/api/v1/cases', {
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
  });

  if (response.status === 401) {
    // Token expired, attempt refresh
    await refreshAccessToken();
    return fetchCases(); // Retry
  }

  return response.json();
}
```

**Request:**
```http
GET /api/v1/cases
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

### 3. Token Refresh Flow

When access token expires, use refresh token to obtain new access token:

```typescript
async function refreshAccessToken() {
  const refreshToken = localStorage.getItem('refreshToken');

  const response = await fetch('/api/v1/auth/refresh', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ refreshToken }),
  });

  if (!response.ok) {
    // Refresh token expired or invalid, redirect to login
    localStorage.clear();
    window.location.href = '/';
    throw new Error('Session expired');
  }

  const data = await response.json();

  localStorage.setItem('accessToken', data.accessToken);

  return data.accessToken;
}
```

**Request:**
```http
POST /api/v1/auth/refresh
Content-Type: application/json

{
  "refreshToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response (200 OK):**
```json
{
  "accessToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "tokenType": "Bearer",
  "expiresIn": 3600
}
```

---

### 4. Logout Flow

```typescript
async function logout() {
  const token = localStorage.getItem('accessToken');

  // Invalidate token on server
  await fetch('/api/v1/auth/logout', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });

  // Clear local storage
  localStorage.removeItem('accessToken');
  localStorage.removeItem('refreshToken');
  localStorage.removeItem('user');

  // Redirect to login
  window.location.href = '/';
}
```

**Request:**
```http
POST /api/v1/auth/logout
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response (204 No Content)**

---

## Token Management

### JWT Token Structure

**Access Token Payload:**
```json
{
  "sub": "user-123",
  "username": "bamf.officer@example.de",
  "role": "officer",
  "permissions": [
    "cases:read",
    "cases:write",
    "documents:upload"
  ],
  "iat": 1702725600,
  "exp": 1702729200
}
```

**Token Properties:**
- `sub` - User ID (subject)
- `username` - User's email/username
- `role` - User role for authorization
- `permissions` - Specific permissions array
- `iat` - Issued at timestamp
- `exp` - Expiration timestamp

### Token Lifecycle

| Token Type | Expiration | Storage | Purpose |
|------------|------------|---------|---------|
| Access Token | 1 hour | localStorage | API authentication |
| Refresh Token | 7 days | localStorage (httpOnly cookie preferred) | Token renewal |

### Automatic Token Refresh

Implement an HTTP interceptor to automatically refresh tokens:

```typescript
// React Query example with automatic token refresh
import { QueryClient } from '@tanstack/react-query';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: (failureCount, error: any) => {
        // Don't retry on 401 after token refresh attempt
        if (error?.status === 401 && failureCount > 0) {
          return false;
        }
        return failureCount < 3;
      },
    },
  },
});

// HTTP interceptor
async function authenticatedFetch(url: string, options: RequestInit = {}) {
  const token = localStorage.getItem('accessToken');

  const response = await fetch(url, {
    ...options,
    headers: {
      ...options.headers,
      'Authorization': `Bearer ${token}`,
    },
  });

  // If 401, try to refresh token and retry
  if (response.status === 401) {
    try {
      await refreshAccessToken();
      const newToken = localStorage.getItem('accessToken');

      // Retry original request with new token
      return fetch(url, {
        ...options,
        headers: {
          ...options.headers,
          'Authorization': `Bearer ${newToken}`,
        },
      });
    } catch (error) {
      // Refresh failed, redirect to login
      window.location.href = '/';
      throw error;
    }
  }

  return response;
}
```

---

## Authorization & Roles

### User Roles

| Role | Description | Permissions |
|------|-------------|-------------|
| **admin** | System administrator | Full access to all resources and admin panel |
| **officer** | BAMF case officer | Read/write cases, upload documents, use AI features |
| **viewer** | Read-only user | View cases and documents only |

### Permission System

Granular permissions for fine-grained access control:

**Case Permissions:**
- `cases:read` - View cases
- `cases:write` - Create and update cases
- `cases:delete` - Delete cases

**Document Permissions:**
- `documents:read` - View documents
- `documents:upload` - Upload new documents
- `documents:delete` - Delete documents

**AI Permissions:**
- `ai:use` - Use AI operations (convert, translate, etc.)
- `ai:admin` - Configure AI settings

**Admin Permissions:**
- `admin:config` - Access admin configuration panel
- `admin:users` - Manage users and roles

### Permission Checking

**Backend (Planned):**
```typescript
// Middleware to check permissions
function requirePermission(permission: string) {
  return (req, res, next) => {
    const user = req.user; // From decoded JWT

    if (!user.permissions.includes(permission)) {
      return res.status(403).json({
        error: 'FORBIDDEN',
        message: `Permission ${permission} required`
      });
    }

    next();
  };
}

// Usage
app.post('/api/v1/cases',
  authenticate(),
  requirePermission('cases:write'),
  createCaseHandler
);
```

**Frontend (Planned):**
```typescript
// Permission checking hook
function useHasPermission(permission: string): boolean {
  const { user } = useAuth();
  return user?.permissions?.includes(permission) ?? false;
}

// Usage in component
function DocumentUpload() {
  const canUpload = useHasPermission('documents:upload');

  if (!canUpload) {
    return <div>You don't have permission to upload documents</div>;
  }

  return <UploadForm />;
}
```

### Current Role Implementation

**Source:** `src/components/workspace/WorkspaceHeader.tsx`

Currently, there's an "Admin Mode" toggle that shows/hides the admin configuration panel:

```typescript
const [isAdminMode, setIsAdminMode] = useState(false);

// Toggle between admin and normal mode
<Button onClick={() => setIsAdminMode(!isAdminMode)}>
  <Shield className="w-4 h-4" />
</Button>
```

**Planned:** Replace with actual role-based checking:
```typescript
const { user } = useAuth();
const canAccessAdmin = user?.role === 'admin' ||
                       user?.permissions?.includes('admin:config');
```

---

## Security Best Practices

### Token Storage

**Recommended:** HttpOnly Cookies
```
Set-Cookie: accessToken=xxx; HttpOnly; Secure; SameSite=Strict
```

**Alternative:** localStorage (current plan)
- Vulnerable to XSS attacks
- Should implement Content Security Policy (CSP)
- Token should have short expiration

### Password Requirements

Enforce strong passwords:
- Minimum 12 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one number
- At least one special character

### Rate Limiting

Prevent brute-force attacks:
```
POST /auth/login - 5 attempts per 15 minutes per IP
POST /auth/refresh - 10 attempts per hour per user
```

### HTTPS Only

All authentication endpoints must use HTTPS to prevent token interception.

### CSRF Protection

Use CSRF tokens for state-changing operations:
```http
POST /api/v1/cases
Authorization: Bearer xxx
X-CSRF-Token: csrf_token_here
```

### Token Revocation

Implement token blacklist for immediate logout:
- Store revoked tokens in Redis/database
- Check blacklist on each request
- Clear expired entries periodically

---

## Implementation Examples

### React Context with Authentication

```typescript
// Planned authentication context
import React, { createContext, useContext, useState, useEffect } from 'react';

interface AuthUser {
  id: string;
  username: string;
  name: string;
  role: 'admin' | 'officer' | 'viewer';
  permissions: string[];
}

interface AuthContextType {
  user: AuthUser | null;
  login: (username: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  isAuthenticated: boolean;
  isLoading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Check for existing session on mount
  useEffect(() => {
    const loadUser = async () => {
      const token = localStorage.getItem('accessToken');
      if (token) {
        try {
          // Verify token and load user
          const response = await fetch('/api/v1/auth/me', {
            headers: { 'Authorization': `Bearer ${token}` }
          });

          if (response.ok) {
            const userData = await response.json();
            setUser(userData);
          } else {
            localStorage.clear();
          }
        } catch (error) {
          console.error('Failed to load user:', error);
          localStorage.clear();
        }
      }
      setIsLoading(false);
    };

    loadUser();
  }, []);

  const login = async (username: string, password: string) => {
    const response = await fetch('/api/v1/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password }),
    });

    if (!response.ok) {
      throw new Error('Authentication failed');
    }

    const data = await response.json();

    localStorage.setItem('accessToken', data.accessToken);
    localStorage.setItem('refreshToken', data.refreshToken);

    setUser(data.user);
  };

  const logout = async () => {
    const token = localStorage.getItem('accessToken');

    try {
      await fetch('/api/v1/auth/logout', {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` },
      });
    } catch (error) {
      console.error('Logout error:', error);
    }

    localStorage.clear();
    setUser(null);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        login,
        logout,
        isAuthenticated: !!user,
        isLoading
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
}
```

### Protected Route Component

```typescript
import { Navigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';

interface ProtectedRouteProps {
  children: React.ReactNode;
  requiredPermission?: string;
  requiredRole?: string;
}

export function ProtectedRoute({
  children,
  requiredPermission,
  requiredRole
}: ProtectedRouteProps) {
  const { user, isLoading, isAuthenticated } = useAuth();

  if (isLoading) {
    return <div>Loading...</div>;
  }

  if (!isAuthenticated) {
    return <Navigate to="/" replace />;
  }

  if (requiredRole && user?.role !== requiredRole) {
    return <Navigate to="/unauthorized" replace />;
  }

  if (requiredPermission && !user?.permissions?.includes(requiredPermission)) {
    return <Navigate to="/unauthorized" replace />;
  }

  return <>{children}</>;
}

// Usage in routes
<Route
  path="/workspace"
  element={
    <ProtectedRoute>
      <Workspace />
    </ProtectedRoute>
  }
/>

<Route
  path="/admin"
  element={
    <ProtectedRoute requiredRole="admin">
      <AdminPanel />
    </ProtectedRoute>
  }
/>
```

### React Query with Authentication

```typescript
import { QueryClient } from '@tanstack/react-query';

// Configure query client with auth
export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: (failureCount, error: any) => {
        if (error?.status === 401) return false;
        return failureCount < 3;
      },
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
    mutations: {
      retry: false,
    },
  },
});

// Authenticated fetch wrapper
export async function authenticatedFetch(
  url: string,
  options: RequestInit = {}
) {
  const token = localStorage.getItem('accessToken');

  const response = await fetch(url, {
    ...options,
    headers: {
      ...options.headers,
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
  });

  if (response.status === 401) {
    // Token expired, try refresh
    try {
      await refreshAccessToken();
      // Retry with new token
      const newToken = localStorage.getItem('accessToken');
      return fetch(url, {
        ...options,
        headers: {
          ...options.headers,
          'Authorization': `Bearer ${newToken}`,
          'Content-Type': 'application/json',
        },
      });
    } catch {
      // Refresh failed, logout
      localStorage.clear();
      window.location.href = '/';
      throw new Error('Session expired');
    }
  }

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.message || 'Request failed');
  }

  return response.json();
}

// Example: Fetch cases with authentication
export function useCases() {
  return useQuery({
    queryKey: ['cases'],
    queryFn: () => authenticatedFetch('/api/v1/cases'),
  });
}
```

---

## Migration Path

### From Current to Production Authentication

**Phase 1:** Prepare Frontend
1. Create AuthContext with login/logout/token management
2. Replace current user context with AuthContext
3. Add token storage to localStorage
4. Update all components to use new AuthContext

**Phase 2:** Implement Backend
1. Set up authentication endpoints (`/auth/login`, `/auth/logout`, `/auth/refresh`)
2. Implement JWT token generation and validation
3. Add authentication middleware to protected routes
4. Implement role-based access control

**Phase 3:** Connect Frontend to Backend
1. Update login form to call actual API
2. Add token refresh logic
3. Update all API calls to include Authorization header
4. Test authentication flow end-to-end

**Phase 4:** Security Hardening
1. Implement rate limiting
2. Add CSRF protection
3. Enable HTTPS only
4. Add password requirements
5. Implement audit logging

---

**Last Updated:** 2025-12-16
**Current Implementation:** Simulated (frontend-only)
**Target Implementation:** JWT-based authentication with role-based access control
