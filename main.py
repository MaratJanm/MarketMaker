import asyncio
from decimal import Decimal
import requests
import random

# Параметры для подключения к пулу ликвидности на Meteor
METEOR_API_URL = "https://api.meteorblockchain.com/liquidity_pool"

# Основные параметры для маркет-мейкинга
SPREAD_PERCENT = Decimal('0.01')  # Спред в 1%
MIN_LIQUIDITY_THRESHOLD = Decimal('1000')  # Минимальная ликвидность для актива
TRADE_AMOUNT_MIN = Decimal('10')  # Минимальная сумма сделки
TRADE_AMOUNT_MAX = Decimal('100')  # Максимальная сумма сделки

# Функция для получения текущей цены и ликвидности из пула на Meteor
def get_liquidity_info_meteor():
    try:
        response = requests.get(f"{METEOR_API_URL}/kitto_usdc")
        if response.status_code == 200:
            data = response.json()
            current_price = Decimal(data["current_price"])
            liquidity = Decimal(data["liquidity"])
            return current_price, liquidity
        else:
            print(f"Ошибка получения данных о ликвидности от Meteor: {response.status_code}")
            return None, None
    except Exception as e:
        print(f"Ошибка при обращении к API Meteor: {e}")
        return None, None

# Функция для добавления ликвидности, если её недостаточно
def add_liquidity_meteor(amount):
    try:
        response = requests.post(f"{METEOR_API_URL}/add_liquidity", json={
            "amount": str(amount)
        })
        if response.status_code == 200:
            print(f"Ликвидность добавлена успешно, сумма: {amount}")
        else:
            print(f"Ошибка при добавлении ликвидности: {response.status_code}")
    except Exception as e:
        print(f"Ошибка при добавлении ликвидности через API Meteor: {e}")

# Функция для выставления ордеров в пуле
def place_order_meteor(is_buy, amount, price):
    try:
        order_type = "buy" if is_buy else "sell"
        response = requests.post(f"{METEOR_API_URL}/place_order", json={
            "order_type": order_type,
            "amount": str(amount),
            "price": str(price)
        })
        if response.status_code == 200:
            print(f"Ордер на {order_type} успешно выставлен, количество: {amount} по цене: {price}")
        else:
            print(f"Ошибка при выставлении ордера: {response.status_code}")
    except Exception as e:
        print(f"Ошибка при выставлении ордера через API Meteor: {e}")

# Основной цикл маркет-мейкинга
async def market_maker():
    try:
        while True:
            # Получить текущую цену и ликвидность из пула
            current_price, liquidity = get_liquidity_info_meteor()

            if current_price is None or liquidity is None:
                print("Не удалось получить данные о цене или ликвидности.")
                continue

            # Проверка ликвидности в пуле
            if liquidity < MIN_LIQUIDITY_THRESHOLD:
                # Добавить ликвидность, если её недостаточно
                add_liquidity_meteor(MIN_LIQUIDITY_THRESHOLD - liquidity)

            # Рассчитать цены для выставления ордеров с учётом спреда
            buy_price = current_price * (1 - SPREAD_PERCENT)
            sell_price = current_price * (1 + SPREAD_PERCENT)

            # Определение количества для сделки
            amount = Decimal(random.uniform(float(TRADE_AMOUNT_MIN), float(TRADE_AMOUNT_MAX)))

            # Выставление ордеров на покупку и продажу
            place_order_meteor(is_buy=True, amount=amount, price=buy_price)
            place_order_meteor(is_buy=False, amount=amount, price=sell_price)

            # Ожидание перед следующей итерацией
            await asyncio.sleep(random.uniform(10, 20))

    except asyncio.CancelledError:
        print("Бот маркет-мейкинга остановлен.")
    except Exception as e:
        print(f"Ошибка в процессе работы маркет-мейкера: {e}")

# Запуск бота
if __name__ == "__main__":
    try:
        asyncio.run(market_maker())
    except KeyboardInterrupt:
        print("Программа завершена пользователем.")
