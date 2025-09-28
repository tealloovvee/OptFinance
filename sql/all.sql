
class CryptoCoin(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    pair = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.pair


class Exchange(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    trading_volume = models.DecimalField(max_digits=30, decimal_places=10)
    coins_listed = models.IntegerField()
    rating = models.DecimalField(max_digits=4, decimal_places=2)

    def __str__(self):
        return self.name

class OHLCV(models.Model):
    id = models.AutoField(primary_key=True)
    trading_pair = models.ForeignKey(CryptoCoin, on_delete=models.CASCADE)
    interval = models.CharField(max_length=20)
    open_time = models.DateTimeField()
    open_price = models.DecimalField(max_digits=20, decimal_places=8)
    high_price = models.DecimalField(max_digits=20, decimal_places=8)
    low_price = models.DecimalField(max_digits=20, decimal_places=8)
    close_price = models.DecimalField(max_digits=20, decimal_places=8)
    volume = models.DecimalField(max_digits=30, decimal_places=10)

    def __str__(self):
        return f"{self.trading_pair} {self.interval} {self.open_time}"


class News(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200)
    content = models.TextField()
    published_at = models.DateTimeField()
    photo = models.BinaryField(null=True, blank=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

class PortfolioComposition(models.Model):
    id = models.AutoField(primary_key=True)
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE)
    weight = models.JSONField(default=dict)
    name = models.JSONField(default=dict)

    def __str__(self):
        return f"{self.portfolio} - {self.trading_pair}"

class Portfolio(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    risk = models.CharField(max_length=50)
    annual_return = models.DecimalField(max_digits=5, decimal_places=2)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Portfolio {self.id} ({self.user.login})"

class User(models.Model):
    id = models.AutoField(primary_key=True)
    role = models.CharField(max_length=100)
    login = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    password_hash = models.CharField(max_length=255)
    portfolios_created = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.login

