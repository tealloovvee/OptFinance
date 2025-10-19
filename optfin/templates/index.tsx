/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
*/

import React, { useState } from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';

const cryptoData = [
    { name: 'Bitcoin', ticker: 'BTC', price: '68,500.25', change: 3.50, volume: '12.2B', sparklineData: [30, 40, 20, 50, 45, 60, 55] },
    { name: 'Ripple', ticker: 'XRP', price: '0.55', change: -1.80, volume: '22.1B', sparklineData: [40, 35, 50, 42, 38, 30, 25] },
    { name: 'Solana', ticker: 'SOL', price: '180.30', change: 7.10, volume: '3.8B', sparklineData: [20, 30, 25, 45, 50, 65, 70] },
    { name: 'Cardano', ticker: 'ADA', price: '0.40', change: -0.99, volume: '0.9B', sparklineData: [60, 55, 40, 45, 30, 20, 25] },
];

const newsData = [
    {
        title: 'Азиатские акции снижаются вслед за ослаблением Уолл-стрит на фоне потерь в технологическом секторе',
        source: 'Investing.com',
        excerpt: 'Большинство азиатских акций снизились в среду вслед за ночными потерями на Уолл-стрит на фоне растущей неопределенности относительно траектории процентных ставок США, при этом технологические акции продолжили терять позиции после сильного ралли в последние недели.',
    },
    {
        title: 'Топ-5 золотых акций, за которыми стоит следить при рекордных ценах на золото: мнение UBS',
        source: 'Investing.com',
        excerpt: 'Investing.com -- Акции золотодобывающих компаний демонстрируют различные результаты в последние месяцы, при этом несколько компаний позиционируют себя для получения высокой доходности в будущем на фоне того, что цены на золото торгуются вблизи рекордных максимумов.',
    },
];

const calculationHistory = [
    { id: 1, description: 'Пополнение баланса', date: '2024-07-25', amount: '+50.00 USD', type: 'deposit' },
    { id: 2, description: 'Покупка BTC', date: '2024-07-24', amount: '-25.00 USD', type: 'withdrawal' },
    { id: 3, description: 'Продажа ETH', date: '2024-07-23', amount: '+15.00 USD', type: 'deposit' },
    { id: 4, description: 'Вывод средств', date: '2024-07-22', amount: '-10.00 USD', type: 'withdrawal' },
    { id: 5, description: 'Пополнение баланса', date: '2024-07-21', amount: '+100.00 USD', type: 'deposit' },
    { id: 6, description: 'Покупка SOL', date: '2024-07-20', amount: '-75.00 USD', type: 'withdrawal' },
];

const Header = ({ activePage, setActivePage, onProfileClick }) => (
    <header className="app-header">
        <div className="header-left">
            <div className="logo">
                <div className="logo-icon">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M4 16V20M10 12V20M16 4V20" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                    </svg>
                </div>
                <span>Oetfinance</span>
            </div>
            <nav>
                <a href="#" className={activePage === 'exchanges' ? 'active' : ''} onClick={(e) => { e.preventDefault(); setActivePage('exchanges'); }}>Биржи</a>
                <a href="#" className={activePage === 'news' ? 'active' : ''} onClick={(e) => { e.preventDefault(); setActivePage('news'); }}>Новости</a>
                <a href="#" className={activePage === 'crypto' ? 'active' : ''} onClick={(e) => { e.preventDefault(); setActivePage('crypto'); }}>Криптовалюты</a>
            </nav>
        </div>
        <div className="header-right">
            <div className="balance">
                <div className="balance-label">Баланс:</div>
                <div className="balance-amount">25USD</div>
            </div>
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

const CryptoDashboard = () => (
    <main className="main-content">
        <div className="filters-container">
            <div className="search-bar">
                <span className="search-icon">
                    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
                </span>
                <input type="text" placeholder="Найти монету..." />
            </div>
            <button className="filter-button">Категория</button>
            <button className="filter-button">Сортировать</button>
            <button className="filter-button">Популярность</button>
        </div>

        <div className="table-container">
            <span className="last-updated">Последнее обновление</span>
            <table className="crypto-table">
                <thead>
                    <tr>
                        <th>Имя</th>
                        <th>Тикер</th>
                        <th>Цена (USD)</th>
                        <th>24h %</th>
                        <th>Объем (USD)</th>
                        <th>График за 7 дней</th>
                    </tr>
                </thead>
                <tbody>
                    {cryptoData.map((coin, index) => (
                        <tr key={index}>
                            <td>
                                <div className="crypto-name">
                                    <span>{coin.name}</span>
                                </div>
                            </td>
                            <td>{coin.ticker}</td>
                            <td>${coin.price}</td>
                            <td className={coin.change >= 0 ? 'positive' : 'negative'}>
                                {coin.change >= 0 ? '+' : ''}{coin.change.toFixed(2)}%
                            </td>
                            <td>${coin.volume}</td>
                            <td>
                                <Sparkline data={coin.sparklineData} positive={coin.change >= 0} />
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>

        <div className="pagination">
            <button className="page-btn active">1</button>
            <button className="page-btn">2</button>
            <button className="page-btn">3</button>
            <button className="page-btn">&rarr;</button>
        </div>
    </main>
);

const NewsDashboard = () => (
    <main className="main-content">
        <div className="news-grid">
            {newsData.map((article, index) => (
                <div className="news-card" key={index}>
                    <h2>{article.title}</h2>
                    <p className="news-excerpt">{article.excerpt}</p>
                    <span className="news-source">{article.source}</span>
                </div>
            ))}
        </div>
    </main>
);

const ProfilePage = ({ onBackClick, onLogout }) => (
    <div className="profile-page">
        <header className="profile-header">
            <button className="back-button" onClick={onBackClick} aria-label="Go back">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M15 18L9 12L15 6" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
            </button>
            <div className="balance-info">25USD</div>
        </header>
        <main className="profile-main">
            <div className="profile-content">
                <img src="https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?q=80&w=2070&auto=format&fit=crop" alt="User Avatar" className="profile-avatar-large" />
                <h1 className="profile-greeting">Добрый день, Альберт</h1>
                <div className="portfolio-calculator">
                    <label htmlFor="portfolio-input">Рассчитать портфель</label>
                    <div className="input-line"></div>
                </div>
                <button className="logout-button" onClick={onLogout}>Выйти</button>
            </div>

            <div className="calculation-history">
                <div className="history-header">
                    <svg className="scroll-up-icon" width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M12 19V5M12 5L19 12M12 5L5 12" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                    </svg>
                    <h2 className="history-title">История расчетов</h2>
                </div>
                <div className="history-divider"></div>
                <ul className="history-list">
                    {calculationHistory.map(item => (
                        <li key={item.id} className="history-item">
                            <div className="item-details">
                                <span className="item-description">{item.description}</span>
                                <span className="item-date">{item.date}</span>
                            </div>
                            <span className={`item-amount ${item.type === 'deposit' ? 'positive' : 'negative'}`}>
                                {item.amount}
                            </span>
                        </li>
                    ))}
                </ul>
            </div>
        </main>
        <footer className="profile-footer">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 5V19M12 19L19 12M12 19L5 12" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
        </footer>
    </div>
);


const FinanceApp = ({ onLogout }) => {
    const [activePage, setActivePage] = useState('crypto');
    const [view, setView] = useState('dashboard');

    const renderPage = () => {
        switch (activePage) {
            case 'news':
                return <NewsDashboard />;
            case 'crypto':
            case 'exchanges':
                return <CryptoDashboard />;
            default:
                return <CryptoDashboard />;
        }
    };

    if (view === 'profile') {
        return <ProfilePage onBackClick={() => setView('dashboard')} onLogout={onLogout} />;
    }

    return (
        <div className="app-container">
            <Header activePage={activePage} setActivePage={setActivePage} onProfileClick={() => setView('profile')} />
            {renderPage()}
        </div>
    );
};

const LoginForm = ({ onLogin }) => (
    <form className="auth-form" onSubmit={(e) => { e.preventDefault(); onLogin(); }}>
        <input className="auth-input" type="email" placeholder="Почта..." required />
        <input className="auth-input" type="password" placeholder="Пароль..." required />
        <button className="auth-button" type="submit">Войти</button>
    </form>
);

const RegisterForm = ({ onRegister }) => (
    <form className="auth-form" onSubmit={(e) => { e.preventDefault(); onRegister(); }}>
        <input className="auth-input" type="email" placeholder="Почта..." required />
        <input className="auth-input" type="text" placeholder="Логин..." required />
        <input className="auth-input" type="password" placeholder="Пароль..." required />
        <button className="auth-button" type="submit">Зарегистрироваться</button>
    </form>
);

const AuthPage = ({ onLogin, onRegister }) => {
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
                {isLoginView ? <LoginForm onLogin={onLogin} /> : <RegisterForm onRegister={onRegister} />}
                <p className="auth-toggle">
                    {isLoginView ? 'Нет аккаунта? ' : 'Уже есть аккаунт? '}
                    <span onClick={() => setIsLoginView(!isLoginView)}>
                        {isLoginView ? 'Зарегистрироваться' : 'Войти'}
                    </span>
                </p>
            </div>
        </div>
    );
};

const App = () => {
    const [isAuthenticated, setIsAuthenticated] = useState(false);

    const handleLogin = () => {
        setIsAuthenticated(true);
    };

    const handleRegister = () => {
        setIsAuthenticated(true);
    };

    const handleLogout = () => {
        setIsAuthenticated(false);
    };

    if (!isAuthenticated) {
        return <AuthPage onLogin={handleLogin} onRegister={handleRegister} />;
    }

    return <FinanceApp onLogout={handleLogout} />;
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