
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export interface LoginCredentials {
  login: string;
  password: string;
}

export interface RegisterData {
  login: string;
  email: string;
  password: string;
  role?: string;
}

export interface User {
  id: number;
  login: string;
  email: string;
  role: string;
  portfolios_created: Record<string, any>;
  created_at: string;
  profile_image?: string | null;
}

export interface AuthResponse {
  message: string;
  user: User;
  tokens: {
    access_token: string;
    refresh_token: string;
  };
}

export interface ApiError {
  error: string;
}

export interface Exchange {
  id: number;
  name: string;
  trading_volume: string;
  coins_listed: number;
  rating: string;
}

export interface ExchangesResponse {
  status: string;
  count: number;
  exchanges: Exchange[];
}

export interface Cryptocurrency {
  id: number;
  name: string;
  pair: string;
}

export interface CryptocurrenciesResponse {
  status: string;
  count: number;
  cryptocurrencies: Cryptocurrency[];
}

export interface NewsItem {
  id: number;
  title: string;
  content: string;
  published_at: string | null;
  photo: string | null;
  user_id: number;
  user_login: string;
}

export interface NewsResponse {
  status: string;
  count: number;
  news: NewsItem[];
}

export interface SingleNewsResponse {
  status: string;
  news: NewsItem;
}

export interface CreateNewsData {
  title: string;
  content: string;
  photo?: string;
  photo_file?: File;
  published_at?: string;
}

export interface Portfolio {
  id: number;
  user_id: number;
  user_login: string;
  risk: string;
  annual_return: string;
  is_active: boolean;
  created_at: string;
}

export interface PortfoliosResponse {
  status: string;
  count: number;
  portfolios: Portfolio[];
}

export interface CreatePortfolioData {
  risk: string;
  annual_return?: number;
}

export const tokenStorage = {
  getAccessToken: (): string | null => {
    return localStorage.getItem('access_token');
  },
  getRefreshToken: (): string | null => {
    return localStorage.getItem('refresh_token');
  },
  setTokens: (accessToken: string, refreshToken: string): void => {
    localStorage.setItem('access_token', accessToken);
    localStorage.setItem('refresh_token', refreshToken);
  },
  clearTokens: (): void => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
  },
  setUser: (user: User): void => {
    localStorage.setItem('user', JSON.stringify(user));
  },
  getUser: (): User | null => {
    const userStr = localStorage.getItem('user');
    return userStr ? JSON.parse(userStr) : null;
  }
};

async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;

  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...options.headers,
  };

  const accessToken = tokenStorage.getAccessToken();
  if (accessToken) {
    headers['Authorization'] = `Bearer ${accessToken}`;
  }

  const response = await fetch(url, {
    ...options,
    headers,
    credentials: 'include',
  });


  if (response.status === 401 && tokenStorage.getRefreshToken()) {
    const refreshed = await refreshAccessToken();
    if (refreshed) {

      headers['Authorization'] = `Bearer ${tokenStorage.getAccessToken()}`;
      const retryResponse = await fetch(url, {
        ...options,
        headers,
        credentials: 'include',
      });

      if (retryResponse.ok) {
        return retryResponse.json();
      }
    }
  }

  if (!response.ok) {
    const error: ApiError = await response.json().catch(() => ({
      error: `HTTP ${response.status}: ${response.statusText}`,
    }));
    throw new Error(error.error || `HTTP ${response.status}`);
  }

  return response.json();
}


async function refreshAccessToken(): Promise<boolean> {
  const refreshToken = tokenStorage.getRefreshToken();
  if (!refreshToken) {
    return false;
  }

  try {
    const response = await fetch(`${API_BASE_URL}/registration/auth/refresh/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ refresh_token: refreshToken }),
      credentials: 'include',
    });

    if (response.ok) {
      const data = await response.json();
      tokenStorage.setTokens(data.tokens.access_token, data.tokens.refresh_token);
      return true;
    } else {
      tokenStorage.clearTokens();
      return false;
    }
  } catch (error) {
    tokenStorage.clearTokens();
    return false;
  }
}


export const api = {
  register: async (data: RegisterData): Promise<AuthResponse> => {
    const response = await apiRequest<AuthResponse>('/registration/auth/register/', {
      method: 'POST',
      body: JSON.stringify(data),
    });
    return response;
  },

  login: async (credentials: LoginCredentials): Promise<AuthResponse> => {
    const response = await apiRequest<AuthResponse>('/registration/auth/login/', {
      method: 'POST',
      body: JSON.stringify(credentials),
    });

    if (response.tokens) {
      tokenStorage.setTokens(response.tokens.access_token, response.tokens.refresh_token);
      tokenStorage.setUser(response.user);
    }

    return response;
  },

  logout: async (): Promise<void> => {
    try {
      await apiRequest('/registration/auth/logout/', {
        method: 'POST',
      });
    } finally {
      tokenStorage.clearTokens();
    }
  },

  getProfile: async (): Promise<User> => {
    const response = await apiRequest<User>('/registration/auth/profile/');
    tokenStorage.setUser(response);
    return response;
  },

  updateProfile: async (data: { login?: string; email?: string; profile_image?: File }): Promise<User> => {
    const formData = new FormData();
    if (data.login) formData.append('login', data.login);
    if (data.email) formData.append('email', data.email);
    if (data.profile_image) formData.append('profile_image', data.profile_image);

    const accessToken = tokenStorage.getAccessToken();
    const response = await fetch(`${API_BASE_URL}/registration/users/${tokenStorage.getUser()?.id}/`, {
      method: 'PUT',
      headers: {
        'Authorization': `Bearer ${accessToken}`,
      },
      body: formData,
      credentials: 'include',
    });

    if (!response.ok) {
      const error: ApiError = await response.json().catch(() => ({
        error: `HTTP ${response.status}: ${response.statusText}`,
      }));
      throw new Error(error.error || `HTTP ${response.status}`);
    }

    const result = await response.json();
    tokenStorage.setUser(result);
    return result;
  },

  uploadProfileImage: async (file: File): Promise<{ message: string }> => {
    const formData = new FormData();
    formData.append('profile_image', file);

    const accessToken = tokenStorage.getAccessToken();
    const response = await fetch(`${API_BASE_URL}/registration/auth/upload-profile-image/`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${accessToken}`,
      },
      body: formData,
      credentials: 'include',
    });

    if (!response.ok) {
      const error: ApiError = await response.json().catch(() => ({
        error: `HTTP ${response.status}: ${response.statusText}`,
      }));
      throw new Error(error.error || `HTTP ${response.status}`);
    }

    return response.json();
  },

  refreshToken: async (): Promise<{ tokens: { access_token: string; refresh_token: string } }> => {
    const refreshToken = tokenStorage.getRefreshToken();
    if (!refreshToken) {
      throw new Error('No refresh token available');
    }

    const response = await apiRequest<{ tokens: { access_token: string; refresh_token: string } }>(
      '/registration/auth/refresh/',
      {
        method: 'POST',
        body: JSON.stringify({ refresh_token: refreshToken }),
      }
    );

    tokenStorage.setTokens(response.tokens.access_token, response.tokens.refresh_token);
    return response;
  },

  confirmEmail: async (token: string): Promise<{ message: string }> => {
    return apiRequest<{ message: string }>(`/registration/auth/confirm/${token}/`, {
      method: 'GET',
    });
  },

  getExchanges: async (): Promise<ExchangesResponse> => {
    return apiRequest<ExchangesResponse>('/exchanges/');
  },

  getExchange: async (exchangeId: number): Promise<Exchange> => {
    return apiRequest<Exchange>(`/exchanges/${exchangeId}/`);
  },

  getCryptocurrencies: async (): Promise<CryptocurrenciesResponse> => {
    return apiRequest<CryptocurrenciesResponse>('/cryptocurrencies/');
  },

  getCryptocurrency: async (coinId: number): Promise<Cryptocurrency> => {
    return apiRequest<Cryptocurrency>(`/cryptocurrencies/${coinId}/`);
  },


  getNews: async (): Promise<NewsResponse> => {
    return apiRequest<NewsResponse>('/news/');
  },

  getNewsItem: async (newsId: number): Promise<SingleNewsResponse> => {
    return apiRequest<SingleNewsResponse>(`/news/${newsId}/`);
  },

  createNews: async (data: CreateNewsData): Promise<SingleNewsResponse> => {
    // If there is a file - send multipart
    if (data.photo_file) {
      const formData = new FormData();
      formData.append('title', data.title);
      formData.append('content', data.content);
      if (data.photo_file) formData.append('photo', data.photo_file);
      if (data.published_at) formData.append('published_at', data.published_at);

      const accessToken = tokenStorage.getAccessToken();
      const response = await fetch(`${API_BASE_URL}/news/`, {
        method: 'POST',
        headers: {
          ...(accessToken ? { Authorization: `Bearer ${accessToken}` } : {}),
        },
        body: formData,
        credentials: 'include',
      });

      if (!response.ok) {
        const error: ApiError = await response.json().catch(() => ({
          error: `HTTP ${response.status}: ${response.statusText}`,
        }));
        throw new Error(error.error || `HTTP ${response.status}`);
      }
      return response.json();
    }

    return apiRequest<SingleNewsResponse>('/news/', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  updateNews: async (newsId: number, data: Partial<CreateNewsData>): Promise<SingleNewsResponse> => {
    if (data.photo_file) {
      const formData = new FormData();
      if (data.title !== undefined) formData.append('title', data.title);
      if (data.content !== undefined) formData.append('content', data.content);
      if (data.photo_file) formData.append('photo', data.photo_file);
      if (data.published_at) formData.append('published_at', data.published_at);

      const accessToken = tokenStorage.getAccessToken();
      const response = await fetch(`${API_BASE_URL}/news/${newsId}/`, {
        method: 'PUT',
        headers: {
          ...(accessToken ? { Authorization: `Bearer ${accessToken}` } : {}),
        },
        body: formData,
        credentials: 'include',
      });

      if (!response.ok) {
        const error: ApiError = await response.json().catch(() => ({
          error: `HTTP ${response.status}: ${response.statusText}`,
        }));
        throw new Error(error.error || `HTTP ${response.status}`);
      }
      return response.json();
    }

    return apiRequest<SingleNewsResponse>(`/news/${newsId}/`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  },

  getPortfolios: async (): Promise<PortfoliosResponse> => {
    return apiRequest<PortfoliosResponse>('/portfolios/');
  },

  getPortfolio: async (portfolioId: number): Promise<Portfolio> => {
    return apiRequest<Portfolio>(`/portfolios/${portfolioId}/`);
  },

  createPortfolio: async (data: CreatePortfolioData): Promise<Portfolio> => {
    return apiRequest<Portfolio>('/portfolios/create/', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  sendChatMessage: async (message: string): Promise<{ status: string }> => {
    return apiRequest<{ status: string }>('/chat/send/', {
      method: 'POST',
      body: JSON.stringify({ message }),
    });
  },
};



