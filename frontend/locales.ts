export type Language = 'ru' | 'en';

export const translations = {
  ru: {
    // Header
    exchanges: 'Биржи',
    portfolios: 'Портфели',
    news: 'Новости',
    cryptocurrencies: 'Криптовалюты',
    
    // Profile dropdown
    profile: 'Профиль',
    settings: 'Настройки',
    theme: 'Тема',
    language: 'Язык',
    lightTheme: 'Светлая',
    darkTheme: 'Темная',
    
    // Profile page
    goodDay: 'Добрый день',
    logout: 'Выйти',
    loading: 'Загрузка...',
    user: 'Пользователь',
    
    // Settings
    email: 'Email',
    login: 'Логин',
    save: 'Сохранить',
    cancel: 'Отмена',
    changeAvatar: 'Изменить аватар',
    
    // Exchanges
    findExchange: 'Найти биржу...',
    sort: 'Сортировать',
    rating: 'Рейтинг',
    totalExchanges: 'Всего бирж',
    exchangeId: 'ID',
    name: 'Название',
    tradingVolume: 'Торговый объем',
    coinsListed: 'Монет на бирже',
    nothingFound: 'Ничего не найдено',
    noData: 'Нет данных',
    loadingExchanges: 'Загрузка бирж...',
    
    // Portfolios
    findPortfolio: 'Найти портфель...',
    risk: 'Риск',
    createPortfolio: 'Создать портфель',
    annualReturn: 'Годовая доходность',
    status: 'Статус',
    active: 'Активен',
    inactive: 'Неактивен',
    createdAt: 'Дата создания',
    totalPortfolios: 'Всего портфелей',
    loadingPortfolios: 'Загрузка портфелей...',
    portfolioRiskPlaceholder: 'Риск (например: low, medium, high)...',
    annualReturnPlaceholder: 'Годовая доходность (%)...',
    creating: 'Создание...',
    
    // News
    createNews: 'Создать новость',
    newsTitle: 'Заголовок новости...',
    newsContent: 'Содержание новости...',
    loadingNews: 'Загрузка новостей...',
    noNews: 'Новостей пока нет',
    
    // Crypto
    findCoin: 'Найти монету...',
    category: 'Категория',
    popularity: 'Популярность',
    totalCryptocurrencies: 'Всего криптовалют',
    pair: 'Пара',
    loadingCryptocurrencies: 'Загрузка криптовалют...',
    
    // Auth
    loginTitle: 'Вход',
    registerTitle: 'Регистрация',
    loginOrEmail: 'Логин или email...',
    password: 'Пароль...',
    emailPlaceholder: 'Почта...',
    loginPlaceholder: 'Логин...',
    enter: 'Войти',
    register: 'Зарегистрироваться',
    noAccount: 'Нет аккаунта?',
    haveAccount: 'Уже есть аккаунт?',
    registerLink: 'Зарегистрироваться',
    loginLink: 'Войти',
    loggingIn: 'Вход...',
    registering: 'Регистрация...',
  },
  en: {
    // Header
    exchanges: 'Exchanges',
    portfolios: 'Portfolios',
    news: 'News',
    cryptocurrencies: 'Cryptocurrencies',
    
    // Profile dropdown
    profile: 'Profile',
    settings: 'Settings',
    theme: 'Theme',
    language: 'Language',
    lightTheme: 'Light',
    darkTheme: 'Dark',
    
    // Profile page
    goodDay: 'Good day',
    logout: 'Logout',
    loading: 'Loading...',
    user: 'User',
    
    // Settings
    email: 'Email',
    login: 'Login',
    save: 'Save',
    cancel: 'Cancel',
    changeAvatar: 'Change avatar',
    
    // Exchanges
    findExchange: 'Find exchange...',
    sort: 'Sort',
    rating: 'Rating',
    totalExchanges: 'Total exchanges',
    exchangeId: 'ID',
    name: 'Name',
    tradingVolume: 'Trading volume',
    coinsListed: 'Coins listed',
    nothingFound: 'Nothing found',
    noData: 'No data',
    loadingExchanges: 'Loading exchanges...',
    
    // Portfolios
    findPortfolio: 'Find portfolio...',
    risk: 'Risk',
    createPortfolio: 'Create portfolio',
    annualReturn: 'Annual return',
    status: 'Status',
    active: 'Active',
    inactive: 'Inactive',
    createdAt: 'Created at',
    totalPortfolios: 'Total portfolios',
    loadingPortfolios: 'Loading portfolios...',
    portfolioRiskPlaceholder: 'Risk (e.g.: low, medium, high)...',
    annualReturnPlaceholder: 'Annual return (%)...',
    creating: 'Creating...',
    
    // News
    createNews: 'Create news',
    newsTitle: 'News title...',
    newsContent: 'News content...',
    loadingNews: 'Loading news...',
    noNews: 'No news yet',
    
    // Crypto
    findCoin: 'Find coin...',
    category: 'Category',
    popularity: 'Popularity',
    totalCryptocurrencies: 'Total cryptocurrencies',
    pair: 'Pair',
    loadingCryptocurrencies: 'Loading cryptocurrencies...',
    
    // Auth
    loginTitle: 'Login',
    registerTitle: 'Register',
    loginOrEmail: 'Login or email...',
    password: 'Password...',
    emailPlaceholder: 'Email...',
    loginPlaceholder: 'Login...',
    enter: 'Enter',
    register: 'Register',
    noAccount: 'No account?',
    haveAccount: 'Already have an account?',
    registerLink: 'Register',
    loginLink: 'Login',
    loggingIn: 'Logging in...',
    registering: 'Registering...',
  },
};

export const getTranslation = (key: string, lang: Language): string => {
  return translations[lang][key as keyof typeof translations.ru] || key;
};

