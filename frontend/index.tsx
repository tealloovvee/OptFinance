
import React, { useState, useEffect } from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import { api, tokenStorage, type User, type Cryptocurrency, type NewsItem, type Exchange } from './api';

const Header = ({ activePage, setActivePage, onProfileClick, user }) => (
    <header className="app-header">
        <div className="header-left">
            <div className="logo">
                <div className="logo-icon">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M4 16V20M10 12V20M16 4V20" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                    </svg>
                </div>
                <span>OptFinance</span>
            </div>
            <nav>
                <a href="#" className={activePage === 'exchanges' ? 'active' : ''} onClick={(e) => { e.preventDefault(); setActivePage('exchanges'); }}>Биржи</a>
                <a href="#" className={activePage === 'news' ? 'active' : ''} onClick={(e) => { e.preventDefault(); setActivePage('news'); }}>Новости</a>
                <a href="#" className={activePage === 'crypto' ? 'active' : ''} onClick={(e) => { e.preventDefault(); setActivePage('crypto'); }}>Криптовалюты</a>
            </nav>
        </div>
        <div className="header-right">
            <img
                src="https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?q=80&w=2070&auto=format&fit=crop"
                alt="User Avatar"
                className="profile-avatar"
                onClick={onProfileClick}
            />
        </div>
    </header>
);

const Sparkline = ({ data, positive }) => {
    const width = 100;
    const height = 40;
    const min = Math.min(...data);
    const max = Math.max(...data);
    const range = max - min === 0 ? 1 : max - min;

    const points = data
        .map((d, i) => {
            const x = (i / (data.length - 1)) * width;
            const y = height - ((d - min) / range) * height;
            return `${x},${y}`;
        })
        .join(' ');

    return (
        <div className="sparkline-container">
            <svg viewBox={`0 0 ${width} ${height}`} preserveAspectRatio="none">
                <polyline
                    fill="none"
                    stroke={positive ? 'var(--positive-change)' : 'var(--negative-change)'}
                    strokeWidth="2"
                    points={points}
                />
            </svg>
        </div>
    );
};

const CryptoDashboard = () => {
    const [cryptocurrencies, setCryptocurrencies] = useState<Cryptocurrency[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string>('');
    const [searchTerm, setSearchTerm] = useState('');

    useEffect(() => {
        const loadCryptocurrencies = async () => {
            try {
                setLoading(true);
                setError('');
                const response = await api.getCryptocurrencies();
                setCryptocurrencies(response.cryptocurrencies || []);
            } catch (err: any) {
                setError(err.message || 'Ошибка загрузки криптовалют');
                console.error('Error loading cryptocurrencies:', err);
            } finally {
                setLoading(false);
            }
        };
        loadCryptocurrencies();
    }, []);

    const filteredCrypto = cryptocurrencies.filter(coin =>
        coin.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        coin.pair.toLowerCase().includes(searchTerm.toLowerCase())
    );

    if (loading) {
        return (
            <main className="main-content">
                <div style={{ color: 'white', textAlign: 'center', padding: '40px' }}>Загрузка криптовалют...</div>
            </main>
        );
    }

    if (error) {
        return (
            <main className="main-content">
                <div style={{ color: 'red', textAlign: 'center', padding: '40px' }}>Ошибка: {error}</div>
            </main>
        );
    }

    return (
        <main className="main-content">
            <div className="filters-container">
                <div className="search-bar">
                    <span className="search-icon">
                        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
                    </span>
                    <input
                        type="text"
                        placeholder="Найти монету..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                    />
                </div>
                <button className="filter-button">Категория</button>
                <button className="filter-button">Сортировать</button>
                <button className="filter-button">Популярность</button>
            </div>

            <div className="table-container">
                <span className="last-updated">Всего криптовалют: {filteredCrypto.length}</span>
                <table className="crypto-table">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Имя</th>
                            <th>Пара</th>
                        </tr>
                    </thead>
                    <tbody>
                        {filteredCrypto.length === 0 ? (
                            <tr>
                                <td colSpan={3} style={{ textAlign: 'center', color: 'white', padding: '20px' }}>
                                    {searchTerm ? 'Ничего не найдено' : 'Нет данных'}
                                </td>
                            </tr>
                        ) : (
                            filteredCrypto.map((coin) => (
                                <tr key={coin.id}>
                                    <td>{coin.id}</td>
                                    <td>
                                        <div className="crypto-name">
                                            <span>{coin.name}</span>
                                        </div>
                                    </td>
                                    <td>{coin.pair}</td>
                                </tr>
                            ))
                        )}
                    </tbody>
                </table>
            </div>

            <div className="pagination">
                <button className="page-btn active">1</button>
            </div>
        </main>
    );
};

const NewsDashboard = () => {
    const [news, setNews] = useState<NewsItem[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string>('');
    const [showCreateForm, setShowCreateForm] = useState(false);
    const [createTitle, setCreateTitle] = useState('');
    const [createContent, setCreateContent] = useState('');
    const [createLoading, setCreateLoading] = useState(false);
    const [createError, setCreateError] = useState<string>('');

    useEffect(() => {
        const loadNews = async () => {
            try {
                setLoading(true);
                setError('');
                const response = await api.getNews();
                setNews(response.news || []);
            } catch (err: any) {
                setError(err.message || 'Ошибка загрузки новостей');
                console.error('Error loading news:', err);
            } finally {
                setLoading(false);
            }
        };
        loadNews();
    }, []);

    const handleCreateNews = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!createTitle.trim() || !createContent.trim()) {
            setCreateError('Заполните все поля');
            return;
        }

        setCreateLoading(true);
        setCreateError('');

        try {
            await api.createNews({
                title: createTitle,
                content: createContent,
            });
            setCreateTitle('');
            setCreateContent('');
            setShowCreateForm(false);
            // Перезагружаем новости
            const response = await api.getNews();
            setNews(response.news || []);
        } catch (err: any) {
            setCreateError(err.message || 'Ошибка создания новости');
        } finally {
            setCreateLoading(false);
        }
    };

    if (loading) {
        return (
            <main className="main-content">
                <div style={{ color: 'white', textAlign: 'center', padding: '40px' }}>Загрузка новостей...</div>
            </main>
        );
    }

    if (error) {
        return (
            <main className="main-content">
                <div style={{ color: 'red', textAlign: 'center', padding: '40px' }}>Ошибка: {error}</div>
            </main>
        );
    }

    return (
        <main className="main-content">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
                <h1 style={{ margin: 0, fontSize: '1.5rem', fontWeight: 600 }}>Новости</h1>
                <button 
                    className="filter-button" 
                    onClick={() => setShowCreateForm(!showCreateForm)}
                    style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}
                >
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <line x1="12" y1="5" x2="12" y2="19"></line>
                        <line x1="5" y1="12" x2="19" y2="12"></line>
                    </svg>
                    Создать новость
                </button>
            </div>

            {showCreateForm && (
                <div style={{ 
                    background: 'var(--background-light)', 
                    border: '1px solid var(--border-color)', 
                    borderRadius: '1rem', 
                    padding: '1.5rem', 
                    marginBottom: '1.5rem' 
                }}>
                    <form onSubmit={handleCreateNews}>
                        {createError && (
                            <div style={{ color: 'red', marginBottom: '1rem', fontSize: '14px' }}>
                                {createError}
                            </div>
                        )}
                        <input
                            type="text"
                            placeholder="Заголовок новости..."
                            value={createTitle}
                            onChange={(e) => setCreateTitle(e.target.value)}
                            style={{
                                width: '100%',
                                background: 'var(--background-dark)',
                                border: '1px solid var(--border-color)',
                                borderRadius: '0.5rem',
                                padding: '0.75rem 1rem',
                                color: 'var(--text-primary)',
                                fontSize: '1rem',
                                marginBottom: '1rem',
                                boxSizing: 'border-box'
                            }}
                            disabled={createLoading}
                            required
                        />
                        <textarea
                            placeholder="Содержание новости..."
                            value={createContent}
                            onChange={(e) => setCreateContent(e.target.value)}
                            rows={6}
                            style={{
                                width: '100%',
                                background: 'var(--background-dark)',
                                border: '1px solid var(--border-color)',
                                borderRadius: '0.5rem',
                                padding: '0.75rem 1rem',
                                color: 'var(--text-primary)',
                                fontSize: '1rem',
                                marginBottom: '1rem',
                                boxSizing: 'border-box',
                                resize: 'vertical',
                                fontFamily: 'inherit'
                            }}
                            disabled={createLoading}
                            required
                        />
                        <div style={{ display: 'flex', gap: '1rem', justifyContent: 'flex-end' }}>
                            <button
                                type="button"
                                className="filter-button"
                                onClick={() => {
                                    setShowCreateForm(false);
                                    setCreateTitle('');
                                    setCreateContent('');
                                    setCreateError('');
                                }}
                                disabled={createLoading}
                            >
                                Отмена
                            </button>
                            <button
                                type="submit"
                                className="filter-button"
                                style={{ 
                                    background: 'var(--accent-orange)', 
                                    borderColor: 'var(--accent-orange)',
                                    color: 'var(--background-dark)',
                                    fontWeight: 600
                                }}
                                disabled={createLoading}
                            >
                                {createLoading ? 'Создание...' : 'Создать'}
                            </button>
                        </div>
                    </form>
                </div>
            )}

            <div className="news-grid">
                {news.length === 0 ? (
                    <div style={{ color: 'white', textAlign: 'center', padding: '40px', gridColumn: '1 / -1' }}>
                        Новостей пока нет
                    </div>
                ) : (
                    news.map((article) => (
                        <div className="news-card" key={article.id}>
                            {article.photo && (
                                <img
                                    src={`data:image/jpeg;base64,${article.photo}`}
                                    alt={article.title}
                                    style={{ width: '100%', maxHeight: '200px', objectFit: 'cover', marginBottom: '10px', borderRadius: '8px' }}
                                />
                            )}
                            <h2>{article.title}</h2>
                            <p className="news-excerpt">
                                {article.content.length > 200
                                    ? `${article.content.substring(0, 200)}...`
                                    : article.content}
                            </p>
                            <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '10px' }}>
                                <span className="news-source">{article.user_login}</span>
                                {article.published_at && (
                                    <span style={{ color: '#888', fontSize: '12px' }}>
                                        {new Date(article.published_at).toLocaleDateString('ru-RU')}
                                    </span>
                                )}
                            </div>
                        </div>
                    ))
                )}
            </div>
        </main>
    );
};

const ProfilePage = ({ onBackClick, onLogout, user }) => {
    const [profileData, setProfileData] = useState<User | null>(user);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        const loadProfile = async () => {
            if (tokenStorage.getAccessToken()) {
                try {
                    setLoading(true);
                    const profile = await api.getProfile();
                    setProfileData(profile);
                } catch (error) {
                    console.error('Ошибка загрузки профиля:', error);
                } finally {
                    setLoading(false);
                }
            }
        };
        loadProfile();
    }, []);

    const userName = profileData?.login || 'Пользователь';

    return (
        <div className="profile-page">
            <header className="profile-header">
                <button className="back-button" onClick={onBackClick} aria-label="Go back">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M15 18L9 12L15 6" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                    </svg>
                </button>
            </header>
            <main className="profile-main">
                <div className="profile-content">
                    <img src="https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?q=80&w=2070&auto=format&fit=crop" alt="User Avatar" className="profile-avatar-large" />
                    <h1 className="profile-greeting">Добрый день, {loading ? 'Загрузка...' : userName}</h1>
                    {profileData && (
                        <div style={{ color: 'white', marginBottom: '10px', fontSize: '14px' }}>
                            <div>Email: {profileData.email}</div>
                            <div>Роль: {profileData.role}</div>
                        </div>
                    )}
                    <div className="portfolio-calculator">
                        <label htmlFor="portfolio-input">Рассчитать портфель</label>
                        <div className="input-line"></div>
                    </div>
                    <button className="logout-button" onClick={onLogout}>Выйти</button>
                </div>
        </main>
        <footer className="profile-footer">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 5V19M12 19L19 12M12 19L5 12" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
        </footer>
    </div>
    );
};


const ExchangesDashboard = () => {
    const [exchanges, setExchanges] = useState<Exchange[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string>('');
    const [searchTerm, setSearchTerm] = useState('');

    useEffect(() => {
        const loadExchanges = async () => {
            try {
                setLoading(true);
                setError('');
                const response = await api.getExchanges();
                setExchanges(response.exchanges || []);
            } catch (err: any) {
                setError(err.message || 'Ошибка загрузки бирж');
                console.error('Error loading exchanges:', err);
            } finally {
                setLoading(false);
            }
        };
        loadExchanges();
    }, []);

    const filteredExchanges = exchanges.filter(exchange =>
        exchange.name.toLowerCase().includes(searchTerm.toLowerCase())
    );

    if (loading) {
        return (
            <main className="main-content">
                <div style={{ color: 'white', textAlign: 'center', padding: '40px' }}>Загрузка бирж...</div>
            </main>
        );
    }

    if (error) {
        return (
            <main className="main-content">
                <div style={{ color: 'red', textAlign: 'center', padding: '40px' }}>Ошибка: {error}</div>
            </main>
        );
    }

    return (
        <main className="main-content">
            <div className="filters-container">
                <div className="search-bar">
                    <span className="search-icon">
                        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
                    </span>
                    <input
                        type="text"
                        placeholder="Найти биржу..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                    />
                </div>
                <button className="filter-button">Сортировать</button>
                <button className="filter-button">Рейтинг</button>
            </div>

            <div className="table-container">
                <span className="last-updated">Всего бирж: {filteredExchanges.length}</span>
                <table className="crypto-table">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Название</th>
                            <th>Торговый объем</th>
                            <th>Монет на бирже</th>
                            <th>Рейтинг</th>
                        </tr>
                    </thead>
                    <tbody>
                        {filteredExchanges.length === 0 ? (
                            <tr>
                                <td colSpan={5} style={{ textAlign: 'center', color: 'white', padding: '20px' }}>
                                    {searchTerm ? 'Ничего не найдено' : 'Нет данных'}
                                </td>
                            </tr>
                        ) : (
                            filteredExchanges.map((exchange) => (
                                <tr key={exchange.id}>
                                    <td>{exchange.id}</td>
                                    <td>
                                        <div className="crypto-name">
                                            <span>{exchange.name}</span>
                                        </div>
                                    </td>
                                    <td>{exchange.trading_volume}</td>
                                    <td>{exchange.coins_listed}</td>
                                    <td>{exchange.rating}</td>
                                </tr>
                            ))
                        )}
                    </tbody>
                </table>
            </div>

            <div className="pagination">
                <button className="page-btn active">1</button>
            </div>
        </main>
    );
};

const FinanceApp = ({ onLogout, user }) => {
    const [activePage, setActivePage] = useState('crypto');
    const [view, setView] = useState('dashboard');

    const renderPage = () => {
        switch (activePage) {
            case 'news':
                return <NewsDashboard />;
            case 'exchanges':
                return <ExchangesDashboard />;
            case 'crypto':
                return <CryptoDashboard />;
            default:
                return <CryptoDashboard />;
        }
    };

    if (view === 'profile') {
        return <ProfilePage onBackClick={() => setView('dashboard')} onLogout={onLogout} user={user} />;
    }

    return (
        <div className="app-container">
            <Header activePage={activePage} setActivePage={setActivePage} onProfileClick={() => setView('profile')} user={user} />
            {renderPage()}
        </div>
    );
};

const LoginForm = ({ onLogin, error, loading }) => {
    const [loginValue, setLoginValue] = useState('');
    const [password, setPassword] = useState('');

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        await onLogin(loginValue, password);
    };

    return (
        <form className="auth-form" onSubmit={handleSubmit}>
            {error && <div style={{ color: 'red', marginBottom: '10px', fontSize: '14px' }}>{error}</div>}
            <input
                className="auth-input"
                type="text"
                placeholder="Логин или email..."
                value={loginValue}
                onChange={(e) => setLoginValue(e.target.value)}
                required
                disabled={loading}
            />
            <input
                className="auth-input"
                type="password"
                placeholder="Пароль..."
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                disabled={loading}
            />
            <button className="auth-button" type="submit" disabled={loading}>
                {loading ? 'Вход...' : 'Войти'}
            </button>
        </form>
    );
};

const RegisterForm = ({ onRegister, error, loading }) => {
    const [email, setEmail] = useState('');
    const [login, setLogin] = useState('');
    const [password, setPassword] = useState('');

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        await onRegister(email, login, password);
    };

    return (
        <form className="auth-form" onSubmit={handleSubmit}>
            {error && <div style={{ color: 'red', marginBottom: '10px', fontSize: '14px' }}>{error}</div>}
            <input
                className="auth-input"
                type="email"
                placeholder="Почта..."
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                disabled={loading}
            />
            <input
                className="auth-input"
                type="text"
                placeholder="Логин..."
                value={login}
                onChange={(e) => setLogin(e.target.value)}
                required
                disabled={loading}
            />
            <input
                className="auth-input"
                type="password"
                placeholder="Пароль..."
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                disabled={loading}
            />
            <button className="auth-button" type="submit" disabled={loading}>
                {loading ? 'Регистрация...' : 'Зарегистрироваться'}
            </button>
        </form>
    );
};

const AuthPage = ({ onLogin, onRegister, loginError, registerError, loginLoading, registerLoading }) => {
    const [isLoginView, setIsLoginView] = useState(true);

    return (
        <div className="auth-container">
            <div className="auth-card">
                <div className="auth-logo">
                    <div className="logo-icon">
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M4 16V20M10 12V20M16 4V20" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                        </svg>
                    </div>
                </div>
                <h1 className="auth-title">{isLoginView ? 'Вход' : 'Регистрация'}</h1>
                {isLoginView ? (
                    <LoginForm onLogin={onLogin} error={loginError} loading={loginLoading} />
                ) : (
                    <RegisterForm onRegister={onRegister} error={registerError} loading={registerLoading} />
                )}
                <p className="auth-toggle">
                    {isLoginView ? 'Нет аккаунта? ' : 'Уже есть аккаунт? '}
                    <span onClick={() => setIsLoginView(!isLoginView)} style={{ cursor: 'pointer', textDecoration: 'underline' }}>
                        {isLoginView ? 'Зарегистрироваться' : 'Войти'}
                    </span>
                </p>
            </div>
        </div>
    );
};

const App = () => {
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [user, setUser] = useState<User | null>(null);
    const [loginError, setLoginError] = useState<string>('');
    const [registerError, setRegisterError] = useState<string>('');
    const [loginLoading, setLoginLoading] = useState(false);
    const [registerLoading, setRegisterLoading] = useState(false);
    const [checkingAuth, setCheckingAuth] = useState(true);

    useEffect(() => {
        const checkAuth = async () => {
            const storedUser = tokenStorage.getUser();
            const accessToken = tokenStorage.getAccessToken();

            if (accessToken && storedUser) {
                try {
                    const profile = await api.getProfile();
                    setUser(profile);
                    setIsAuthenticated(true);
                } catch (error) {
                    tokenStorage.clearTokens();
                    setUser(null);
                    setIsAuthenticated(false);
                }
            }
            setCheckingAuth(false);
        };
        checkAuth();
    }, []);

    const handleLogin = async (loginOrEmail: string, password: string) => {
        setLoginError('');
        setLoginLoading(true);

        try {
            const response = await api.login({ login: loginOrEmail, password });
            setUser(response.user);
            setIsAuthenticated(true);
        } catch (error: any) {
            setLoginError(error.message || 'Ошибка входа. Проверьте данные.');
            setIsAuthenticated(false);
        } finally {
            setLoginLoading(false);
        }
    };

    const handleRegister = async (email: string, login: string, password: string) => {
        setRegisterError('');
        setRegisterLoading(true);

        try {
            const response = await api.register({ email, login, password });
            setRegisterError(`Регистрация успешна! Проверьте почту ${email} для подтверждения аккаунта.`);
            setTimeout(() => {
                setRegisterError('');
            }, 5000);
        } catch (error: any) {
            setRegisterError(error.message || 'Ошибка регистрации. Попробуйте снова.');
        } finally {
            setRegisterLoading(false);
        }
    };

    const handleLogout = async () => {
        try {
            await api.logout();
        } catch (error) {
            console.error('Ошибка при выходе:', error);
        } finally {
            tokenStorage.clearTokens();
            setUser(null);
            setIsAuthenticated(false);
        }
    };

    if (checkingAuth) {
        return (
            <div className="auth-container">
                <div style={{ color: 'white', textAlign: 'center' }}>Загрузка...</div>
            </div>
        );
    }

    if (!isAuthenticated) {
        return (
            <AuthPage
                onLogin={handleLogin}
                onRegister={handleRegister}
                loginError={loginError}
                registerError={registerError}
                loginLoading={loginLoading}
                registerLoading={registerLoading}
            />
        );
    }

    return <FinanceApp onLogout={handleLogout} user={user} />;
};

const rootElement = document.getElementById('root');
if (rootElement) {
    const root = ReactDOM.createRoot(rootElement);
    root.render(
        <React.StrictMode>
            <App />
        </React.StrictMode>
    );
}