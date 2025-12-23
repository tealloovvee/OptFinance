
import React, { useState, useEffect, useRef, createContext, useContext } from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import { api, tokenStorage, type User, type Cryptocurrency, type NewsItem, type Exchange, type Portfolio } from './api';
import { translations, type Language, getTranslation } from './locales';

type Theme = 'light' | 'dark';

interface AppContextType {
  theme: Theme;
  setTheme: (theme: Theme) => void;
  language: Language;
  setLanguage: (lang: Language) => void;
  t: (key: string) => string;
}

const AppContext = createContext<AppContextType | null>(null);

const useApp = () => {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useApp must be used within AppProvider');
  }
  return context;
};

const SettingsPage = ({ onBackClick, user, onProfileUpdate }) => {
    const { t } = useApp();
    const [email, setEmail] = useState(user?.email || '');
    const [login, setLogin] = useState(user?.login || '');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string>('');

    const handleSave = async () => {
        if (!email.trim() || !login.trim()) {
            setError('Заполните все поля');
            return;
        }

        setLoading(true);
        setError('');

        try {
            await api.updateProfile({ email, login });
            if (onProfileUpdate) {
                await onProfileUpdate();
            }
            onBackClick();
        } catch (err: any) {
            setError(err.message || 'Ошибка сохранения');
        } finally {
            setLoading(false);
        }
    };

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
                    <h1 className="profile-greeting">{t('settings')}</h1>
                    {error && (
                        <div style={{ color: 'red', marginBottom: '1rem', fontSize: '14px' }}>
                            {error}
                        </div>
                    )}
                    <div style={{ width: '100%', maxWidth: '400px', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                        <div>
                            <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '14px', color: 'var(--text-secondary)' }}>
                                {t('email')}
                            </label>
                            <input
                                type="email"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                style={{
                                    width: '100%',
                                    background: 'var(--background-dark)',
                                    border: '1px solid var(--border-color)',
                                    borderRadius: '0.5rem',
                                    padding: '0.75rem 1rem',
                                    color: 'var(--text-primary)',
                                    fontSize: '1rem',
                                    boxSizing: 'border-box'
                                }}
                                disabled={loading}
                            />
                        </div>
                        <div>
                            <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '14px', color: 'var(--text-secondary)' }}>
                                {t('login')}
                            </label>
                            <input
                                type="text"
                                value={login}
                                onChange={(e) => setLogin(e.target.value)}
                                style={{
                                    width: '100%',
                                    background: 'var(--background-dark)',
                                    border: '1px solid var(--border-color)',
                                    borderRadius: '0.5rem',
                                    padding: '0.75rem 1rem',
                                    color: 'var(--text-primary)',
                                    fontSize: '1rem',
                                    boxSizing: 'border-box'
                                }}
                                disabled={loading}
                            />
                        </div>
                        <div style={{ display: 'flex', gap: '1rem', marginTop: '1rem' }}>
                            <button
                                className="filter-button"
                                onClick={onBackClick}
                                disabled={loading}
                            >
                                {t('cancel')}
                            </button>
                            <button
                                className="filter-button"
                                onClick={handleSave}
                                disabled={loading}
                                style={{
                                    background: 'var(--accent-orange)',
                                    borderColor: 'var(--accent-orange)',
                                    color: 'var(--background-dark)',
                                    fontWeight: 600
                                }}
                            >
                                {loading ? t('loading') : t('save')}
                            </button>
                        </div>
                    </div>
                </div>
            </main>
        </div>
    );
};

const ProfileDropdown = ({ user, onProfileClick, onSettingsClick, onClose }) => {
    const { theme, setTheme, language, setLanguage, t } = useApp();
    const [showDropdown, setShowDropdown] = useState(false);
    const hoverTimeoutRef = React.useRef<NodeJS.Timeout | null>(null);

    const handleMouseEnter = () => {
        hoverTimeoutRef.current = setTimeout(() => {
            setShowDropdown(true);
        }, 300);
    };

    const handleMouseLeave = () => {
        if (hoverTimeoutRef.current) {
            clearTimeout(hoverTimeoutRef.current);
        }
        setTimeout(() => {
            setShowDropdown(false);
        }, 200);
    };

    useEffect(() => {
        return () => {
            if (hoverTimeoutRef.current) {
                clearTimeout(hoverTimeoutRef.current);
            }
        };
    }, []);

    return (
        <div
            className="profile-dropdown-container"
            onMouseEnter={handleMouseEnter}
            onMouseLeave={handleMouseLeave}
        >
            <img
                src={user?.profile_image 
                    ? `data:image/jpeg;base64,${user.profile_image}`
                    : 'https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?q=80&w=2070&auto=format&fit=crop'}
                alt="User Avatar"
                className="profile-avatar"
            />
            {showDropdown && (
                <div className={`profile-dropdown ${showDropdown ? 'show' : ''}`}>
                    <div className="dropdown-item" onClick={onProfileClick}>
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                            <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                            <circle cx="12" cy="7" r="4"></circle>
                        </svg>
                        <span>{t('profile')}</span>
                    </div>
                    <div className="dropdown-item" onClick={onSettingsClick}>
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                            <circle cx="12" cy="12" r="3"></circle>
                            <path d="M12 1v6m0 6v6m9-9h-6m-6 0H3"></path>
                        </svg>
                        <span>{t('settings')}</span>
                    </div>
                    <div className="dropdown-item dropdown-theme">
                        <span>{t('theme')}</span>
                        <div className="theme-toggle">
                            <span className={theme === 'light' ? 'active' : ''}>{t('lightTheme')}</span>
                            <label className="theme-switch">
                                <input
                                    type="checkbox"
                                    checked={theme === 'dark'}
                                    onChange={(e) => setTheme(e.target.checked ? 'dark' : 'light')}
                                />
                                <span className="slider"></span>
                            </label>
                            <span className={theme === 'dark' ? 'active' : ''}>{t('darkTheme')}</span>
                        </div>
                    </div>
                    <div className="dropdown-item dropdown-language">
                        <span>{t('language')}</span>
                        <div className="language-selector">
                            <button
                                className={language === 'ru' ? 'active' : ''}
                                onClick={() => setLanguage('ru')}
                            >
                                Русский
                            </button>
                            <button
                                className={language === 'en' ? 'active' : ''}
                                onClick={() => setLanguage('en')}
                            >
                                English
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

const Header = ({ activePage, setActivePage, onProfileClick, user, onSettingsClick }) => {
    const { t } = useApp();
    
    return (
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
                    <a href="#" className={activePage === 'exchanges' ? 'active' : ''} onClick={(e) => { e.preventDefault(); setActivePage('exchanges'); }}>{t('exchanges')}</a>
                    <a href="#" className={activePage === 'portfolios' ? 'active' : ''} onClick={(e) => { e.preventDefault(); setActivePage('portfolios'); }}>{t('portfolios')}</a>
                    <a href="#" className={activePage === 'news' ? 'active' : ''} onClick={(e) => { e.preventDefault(); setActivePage('news'); }}>{t('news')}</a>
                    <a href="#" className={activePage === 'crypto' ? 'active' : ''} onClick={(e) => { e.preventDefault(); setActivePage('crypto'); }}>{t('cryptocurrencies')}</a>
            </nav>
        </div>
        <div className="header-right">
                <ProfileDropdown
                    user={user}
                    onProfileClick={onProfileClick}
                    onSettingsClick={onSettingsClick}
                    onClose={() => {}}
            />
        </div>
    </header>
);
};

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
    const { t } = useApp();
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

    const filteredCrypto = cryptocurrencies
        .filter(coin =>
            coin.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
            coin.pair.toLowerCase().includes(searchTerm.toLowerCase())
        )
        .sort((a, b) => a.name.toLowerCase().localeCompare(b.name.toLowerCase()));

    if (loading) {
        return (
            <main className="main-content">
                <div style={{ color: 'white', textAlign: 'center', padding: '40px' }}>{t('loadingCryptocurrencies')}</div>
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
                        placeholder={t('findCoin')}
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                    />
                </div>
                <button className="filter-button">{t('category')}</button>
                <button className="filter-button">{t('sort')}</button>
                <button className="filter-button">{t('popularity')}</button>
            </div>

            <div className="table-container">
                <span className="last-updated">{t('totalCryptocurrencies')}: {filteredCrypto.length}</span>
                <table className="crypto-table">
                    <thead>
                        <tr>
                            <th>{t('exchangeId')}</th>
                            <th>{t('name')}</th>
                            <th>{t('pair')}</th>
                        </tr>
                    </thead>
                    <tbody>
                        {filteredCrypto.length === 0 ? (
                            <tr>
                                <td colSpan={3} style={{ textAlign: 'center', color: 'white', padding: '20px' }}>
                                    {searchTerm ? t('nothingFound') : t('noData')}
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
    const { t } = useApp();
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
                <div style={{ color: 'white', textAlign: 'center', padding: '40px' }}>{t('loadingNews')}</div>
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
                <h1 style={{ margin: 0, fontSize: '1.5rem', fontWeight: 600 }}>{t('news')}</h1>
                <button 
                    className="filter-button" 
                    onClick={() => setShowCreateForm(!showCreateForm)}
                    style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}
                >
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <line x1="12" y1="5" x2="12" y2="19"></line>
                        <line x1="5" y1="12" x2="19" y2="12"></line>
                    </svg>
                    {t('createNews')}
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
                            placeholder={t('newsTitle')}
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
                            placeholder={t('newsContent')}
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
                                {t('cancel')}
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
                                {createLoading ? t('creating') : t('createNews')}
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

const ProfilePage = ({ onBackClick, onLogout, user, onProfileUpdate }) => {
    const { t } = useApp();
    const [profileData, setProfileData] = useState<User | null>(user);
    const [loading, setLoading] = useState(false);
    const [uploading, setUploading] = useState(false);
    const fileInputRef = React.useRef<HTMLInputElement>(null);

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

    const handleImageUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (!file) return;

        try {
            setUploading(true);
            await api.uploadProfileImage(file);
            // Перезагружаем профиль для получения обновленной аватарки
            const profile = await api.getProfile();
            setProfileData(profile);
            // Обновляем user в родительском компоненте
            if (onProfileUpdate) {
                await onProfileUpdate();
            }
        } catch (error: any) {
            console.error('Ошибка загрузки аватарки:', error);
            alert(error.message || 'Ошибка загрузки аватарки');
        } finally {
            setUploading(false);
            if (fileInputRef.current) {
                fileInputRef.current.value = '';
            }
        }
    };

    const userName = profileData?.login || t('user');
    const avatarSrc = profileData?.profile_image 
        ? `data:image/jpeg;base64,${profileData.profile_image}`
        : 'https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?q=80&w=2070&auto=format&fit=crop';

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
                    <div style={{ position: 'relative', display: 'inline-block' }}>
                        <img 
                            src={avatarSrc} 
                            alt="User Avatar" 
                            className="profile-avatar-large" 
                        />
                        <button
                            onClick={() => fileInputRef.current?.click()}
                            disabled={uploading}
                            style={{
                                position: 'absolute',
                                bottom: 0,
                                right: 0,
                                background: 'var(--accent-orange)',
                                border: '2px solid var(--background-light)',
                                borderRadius: '50%',
                                width: '36px',
                                height: '36px',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                cursor: uploading ? 'not-allowed' : 'pointer',
                                opacity: uploading ? 0.6 : 1,
                            }}
                            title={t('changeAvatar')}
                        >
                            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2">
                                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                                <polyline points="17 8 12 3 7 8"></polyline>
                                <line x1="12" y1="3" x2="12" y2="15"></line>
                            </svg>
                        </button>
                        <input
                            ref={fileInputRef}
                            type="file"
                            accept="image/*"
                            onChange={handleImageUpload}
                            style={{ display: 'none' }}
                        />
                        </div>
                    <h1 className="profile-greeting">{t('goodDay')}, {loading ? t('loading') : userName}</h1>
                    <button className="logout-button" onClick={onLogout}>{t('logout')}</button>
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
    const { t } = useApp();
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
                <div style={{ color: 'white', textAlign: 'center', padding: '40px' }}>{t('loadingExchanges')}</div>
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
                        placeholder={t('findExchange')}
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                    />
                </div>
                <button className="filter-button">{t('sort')}</button>
                <button className="filter-button">{t('rating')}</button>
            </div>

            <div className="table-container">
                <span className="last-updated">{t('totalExchanges')}: {filteredExchanges.length}</span>
                <table className="crypto-table">
                    <thead>
                        <tr>
                            <th>{t('exchangeId')}</th>
                            <th>{t('name')}</th>
                            <th>{t('tradingVolume')}</th>
                            <th>{t('coinsListed')}</th>
                            <th>{t('rating')}</th>
                        </tr>
                    </thead>
                    <tbody>
                        {filteredExchanges.length === 0 ? (
                            <tr>
                                <td colSpan={5} style={{ textAlign: 'center', color: 'white', padding: '20px' }}>
                                    {searchTerm ? t('nothingFound') : t('noData')}
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

const PortfoliosDashboard = () => {
    const { t } = useApp();
    const [portfolios, setPortfolios] = useState<Portfolio[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string>('');
    const [searchTerm, setSearchTerm] = useState('');
    const [showCreateForm, setShowCreateForm] = useState(false);
    const [createRisk, setCreateRisk] = useState('');
    const [createAnnualReturn, setCreateAnnualReturn] = useState('');
    const [createLoading, setCreateLoading] = useState(false);
    const [createError, setCreateError] = useState<string>('');

    useEffect(() => {
        const loadPortfolios = async () => {
            try {
                setLoading(true);
                setError('');
                const response = await api.getPortfolios();
                setPortfolios(response.portfolios || []);
            } catch (err: any) {
                setError(err.message || 'Ошибка загрузки портфелей');
                console.error('Error loading portfolios:', err);
            } finally {
                setLoading(false);
            }
        };
        loadPortfolios();
    }, []);

    const handleCreatePortfolio = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!createRisk.trim()) {
            setCreateError('Заполните поле риска');
            return;
        }

        setCreateLoading(true);
        setCreateError('');

        try {
            await api.createPortfolio({
                risk: createRisk,
                annual_return: createAnnualReturn ? parseFloat(createAnnualReturn) : undefined,
            });
            setCreateRisk('');
            setCreateAnnualReturn('');
            setShowCreateForm(false);
            // Перезагружаем портфели
            const response = await api.getPortfolios();
            setPortfolios(response.portfolios || []);
        } catch (err: any) {
            setCreateError(err.message || 'Ошибка создания портфеля');
        } finally {
            setCreateLoading(false);
        }
    };

    const filteredPortfolios = portfolios.filter(portfolio =>
        portfolio.risk.toLowerCase().includes(searchTerm.toLowerCase())
    );

    if (loading) {
        return (
            <main className="main-content">
                <div style={{ color: 'white', textAlign: 'center', padding: '40px' }}>{t('loadingPortfolios')}</div>
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
                <h1 style={{ margin: 0, fontSize: '1.5rem', fontWeight: 600 }}>{t('portfolios')}</h1>
                <button 
                    className="filter-button" 
                    onClick={() => setShowCreateForm(!showCreateForm)}
                    style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}
                >
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <line x1="12" y1="5" x2="12" y2="19"></line>
                        <line x1="5" y1="12" x2="19" y2="12"></line>
                    </svg>
                    {t('createPortfolio')}
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
                    <form onSubmit={handleCreatePortfolio}>
                        {createError && (
                            <div style={{ color: 'red', marginBottom: '1rem', fontSize: '14px' }}>
                                {createError}
                            </div>
                        )}
                        <input
                            type="text"
                            placeholder={t('portfolioRiskPlaceholder')}
                            value={createRisk}
                            onChange={(e) => setCreateRisk(e.target.value)}
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
                        <input
                            type="number"
                            placeholder={t('annualReturnPlaceholder')}
                            value={createAnnualReturn}
                            onChange={(e) => setCreateAnnualReturn(e.target.value)}
                            step="0.01"
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
                        />
                        <div style={{ display: 'flex', gap: '1rem', justifyContent: 'flex-end' }}>
                            <button
                                type="button"
                                className="filter-button"
                                onClick={() => {
                                    setShowCreateForm(false);
                                    setCreateRisk('');
                                    setCreateAnnualReturn('');
                                    setCreateError('');
                                }}
                                disabled={createLoading}
                            >
                                {t('cancel')}
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
                                {createLoading ? t('creating') : t('createPortfolio')}
                            </button>
                        </div>
                    </form>
                </div>
            )}

            <div className="filters-container">
                <div className="search-bar">
                    <span className="search-icon">
                        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
                    </span>
                    <input
                        type="text"
                        placeholder={t('findPortfolio')}
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                    />
                </div>
                <button className="filter-button">{t('sort')}</button>
                <button className="filter-button">{t('risk')}</button>
            </div>

            <div className="table-container">
                <span className="last-updated">{t('totalPortfolios')}: {filteredPortfolios.length}</span>
                <table className="crypto-table">
                    <thead>
                        <tr>
                            <th>{t('exchangeId')}</th>
                            <th>{t('risk')}</th>
                            <th>{t('annualReturn')}</th>
                            <th>{t('status')}</th>
                            <th>{t('createdAt')}</th>
                        </tr>
                    </thead>
                    <tbody>
                        {filteredPortfolios.length === 0 ? (
                            <tr>
                                <td colSpan={5} style={{ textAlign: 'center', color: 'white', padding: '20px' }}>
                                    {searchTerm ? t('nothingFound') : t('noData')}
                                </td>
                            </tr>
                        ) : (
                            filteredPortfolios.map((portfolio) => (
                                <tr key={portfolio.id}>
                                    <td>{portfolio.id}</td>
                                    <td>
                                        <div className="crypto-name">
                                            <span>{portfolio.risk}</span>
                                        </div>
                                    </td>
                                    <td>{portfolio.annual_return}%</td>
                                    <td>{portfolio.is_active ? t('active') : t('inactive')}</td>
                                    <td>{new Date(portfolio.created_at).toLocaleDateString('ru-RU')}</td>
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

interface ChatMessage {
    id: number;
    from: 'admin' | 'user';
    text: string;
    createdAt: Date;
}

const ChatWidget = ({ user }: { user: User | null }) => {
    const [isOpen, setIsOpen] = useState(false);
    const [messages, setMessages] = useState<ChatMessage[]>([
        {
            id: 1,
            from: 'admin',
            text: 'Здравствуйте! Чем могу помочь?',
            createdAt: new Date(),
        },
    ]);
    const [draft, setDraft] = useState('');
    const [ws, setWs] = useState<WebSocket | null>(null);
    const [isConnecting, setIsConnecting] = useState(false);
    const messageIdCounterRef = useRef(2);

    // Get API URL - use same logic as api.ts
    const API_BASE_URL = ((import.meta as any).env?.VITE_API_URL as string) || 'http://localhost:8000';
    const WS_BASE_URL = API_BASE_URL.replace('http://', 'ws://').replace('https://', 'wss://');

    useEffect(() => {
        if (!user) return;

        let websocket: WebSocket | null = null;
        let reconnectTimeout: ReturnType<typeof setTimeout> | null = null;
        let shouldReconnect = true;

        const connectWebSocket = () => {
            if (!shouldReconnect) return;
            
            try {
                const token = tokenStorage.getAccessToken();
                if (!token) {
                    console.error('No access token available');
                    return;
                }

                const wsUrl = `${WS_BASE_URL}/ws/chat/?token=${token}`;
                websocket = new WebSocket(wsUrl);
                setIsConnecting(true);

                websocket.onopen = () => {
                    console.log('WebSocket connected');
                    setIsConnecting(false);
                    setWs(websocket);
                };

                websocket.onmessage = (event) => {
                    try {
                        const data = JSON.parse(event.data);
                        const messageText = data.message || '';
                        const from = data.from || 'admin';
                        
                        if (messageText) {
                            const newId = messageIdCounterRef.current;
                            messageIdCounterRef.current += 1;
                            setMessages((prev) => [
                                ...prev,
                                {
                                    id: newId,
                                    from: from as 'admin' | 'user',
                                    text: messageText,
                                    createdAt: new Date(),
                                },
                            ]);
                        }
                    } catch (error) {
                        console.error('Error parsing WebSocket message:', error);
                    }
                };

                websocket.onerror = (error) => {
                    console.error('WebSocket error:', error);
                    setIsConnecting(false);
                };

                websocket.onclose = () => {
                    console.log('WebSocket disconnected');
                    setIsConnecting(false);
                    setWs(null);
                    // Reconnect after 3 seconds if still should reconnect
                    if (shouldReconnect) {
                        reconnectTimeout = setTimeout(connectWebSocket, 3000);
                    }
                };
            } catch (error) {
                console.error('Error connecting WebSocket:', error);
                setIsConnecting(false);
                if (shouldReconnect) {
                    reconnectTimeout = setTimeout(connectWebSocket, 3000);
                }
            }
        };

        connectWebSocket();

        return () => {
            shouldReconnect = false;
            if (reconnectTimeout) {
                clearTimeout(reconnectTimeout);
            }
            if (websocket) {
                websocket.close();
            }
        };
    }, [user, WS_BASE_URL]);

    const toggleChat = () => setIsOpen((prev) => !prev);

    const handleSend = async () => {
        const text = draft.trim();
        if (!text || !user) return;

        // Add message to UI immediately
        const userMessage: ChatMessage = {
            id: messageIdCounterRef.current,
            from: 'user',
            text,
            createdAt: new Date(),
        };
        messageIdCounterRef.current += 1;
        setMessages((prev) => [...prev, userMessage]);
        setDraft('');

        // Send message to backend
        try {
            await api.sendChatMessage(text);
        } catch (error) {
            console.error('Error sending message:', error);
        }
    };

    const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    };

    return (
        <>
            <button
                className="chat-toggle-button"
                aria-label="Открыть чат"
                onClick={toggleChat}
            >
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M21 15c0 1.1-.9 2-2 2H7l-4 4V5c0-1.1.9-2 2-2h14c1.1 0 2 .9 2 2v10Z" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                    <path d="M7 8h10M7 12h6" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
            </button>

            <div className={`chat-panel ${isOpen ? 'open' : ''}`}>
                <div className="chat-header">
                    <div>
                        <div className="chat-admin-name">Админ</div>
                        <div className="chat-admin-status">
                            {ws && ws.readyState === WebSocket.OPEN ? 'Онлайн' : isConnecting ? 'Подключение...' : 'Офлайн'}
                        </div>
                    </div>
                    <button className="chat-close" aria-label="Закрыть чат" onClick={toggleChat}>
                        ×
                    </button>
                </div>

                <div className="chat-messages">
                    {messages.map((msg) => (
                        <div key={msg.id} className={`chat-message ${msg.from === 'admin' ? 'from-admin' : 'from-user'}`}>
                            <div className="chat-message-author">
                                {msg.from === 'admin' ? 'Админ' : user?.login || 'Вы'}
                            </div>
                            <div className="chat-message-text">{msg.text}</div>
                        </div>
                    ))}
                </div>

                <div className="chat-input-row">
                    <input
                        type="text"
                        placeholder="Введите сообщение..."
                        value={draft}
                        onChange={(e) => setDraft(e.target.value)}
                        onKeyDown={handleKeyDown}
                    />
                    <button onClick={handleSend} className="chat-send" aria-label="Отправить">
                        Отправить
                    </button>
                </div>
            </div>
        </>
    );
};

const FinanceApp = ({ onLogout, user, setUser }) => {
    const [activePage, setActivePage] = useState('crypto');
    const [view, setView] = useState('dashboard');

    const handleProfileUpdate = async () => {
        try {
            const profile = await api.getProfile();
            setUser(profile);
        } catch (error) {
            console.error('Ошибка обновления профиля:', error);
        }
    };

    const renderPage = () => {
        switch (activePage) {
            case 'news':
                return <NewsDashboard />;
            case 'exchanges':
                return <ExchangesDashboard />;
            case 'portfolios':
                return <PortfoliosDashboard />;
            case 'crypto':
                return <CryptoDashboard />;
            default:
                return <CryptoDashboard />;
        }
    };

    if (view === 'profile') {
        return <ProfilePage onBackClick={() => setView('dashboard')} onLogout={onLogout} user={user} onProfileUpdate={handleProfileUpdate} />;
    }

    if (view === 'settings') {
        return <SettingsPage onBackClick={() => setView('dashboard')} user={user} onProfileUpdate={handleProfileUpdate} />;
    }

    return (
        <div className="app-container">
            <Header 
                activePage={activePage} 
                setActivePage={setActivePage} 
                onProfileClick={() => setView('profile')} 
                onSettingsClick={() => setView('settings')}
                user={user} 
            />
            {renderPage()}
            <ChatWidget user={user} />
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
    const [theme, setTheme] = useState<Theme>(() => {
        const saved = localStorage.getItem('theme');
        return (saved as Theme) || 'dark';
    });
    const [language, setLanguage] = useState<Language>(() => {
        const saved = localStorage.getItem('language');
        return (saved as Language) || 'ru';
    });

    useEffect(() => {
        localStorage.setItem('theme', theme);
        document.documentElement.setAttribute('data-theme', theme);
    }, [theme]);

    useEffect(() => {
        localStorage.setItem('language', language);
    }, [language]);

    useEffect(() => {
        document.documentElement.setAttribute('data-theme', theme);
    }, []);

    const t = (key: string) => getTranslation(key, language);

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

    const contextValue: AppContextType = {
        theme,
        setTheme,
        language,
        setLanguage,
        t,
    };

    if (!isAuthenticated) {
        return (
            <AppContext.Provider value={contextValue}>
            <AuthPage
                onLogin={handleLogin}
                onRegister={handleRegister}
                loginError={loginError}
                registerError={registerError}
                loginLoading={loginLoading}
                registerLoading={registerLoading}
            />
            </AppContext.Provider>
        );
    }

    return (
        <AppContext.Provider value={contextValue}>
            <FinanceApp onLogout={handleLogout} user={user} setUser={setUser} />
        </AppContext.Provider>
    );
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