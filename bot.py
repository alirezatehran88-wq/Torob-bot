import requests
import os
import json

# توکن و آیدی از تنظیمات GitHub گرفته میشه
TOKEN = os.environ.get("8681664206:AAEhHIXFWjDV4jm2nkYt5nltcaFeW49P_wE")
CHAT_ID = os.environ.get("50072161")

# ✅ لیست محصولات
PRODUCTS = [
    {
        "url": "https://torob.com/p/1d522479-af35-4596-8149-7ccc5ab86c7b/",
        "name": "اسکنر اثر انگشت"
    },
    # محصولات دیگه رو اینجا اضافه کن
]

# فایل ذخیره قیمت‌های قبلی
PRICES_FILE = "prices.json"


def get_torob_price(url):
    try:
        product_id = url.split("/p/")[1].split("/")[0]
    except:
        return None, None
    
    api_url = f"https://api.torob.com/v4/base-product/details/?prk={product_id}"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    try:
        response = requests.get(api_url, headers=headers, timeout=15)
        data = response.json()
        price = data.get("price")
        name = data.get("name1") or "محصول"
        if price and price > 0:
            return int(price) // 10, name
        return None, None
    except Exception as e:
        print("خطا:", e)
        return None, None


def send_telegram(message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    try:
        requests.post(url, json=payload, timeout=15)
    except Exception as e:
        print("خطا در ارسال:", e)


def load_last_prices():
    if os.path.exists(PRICES_FILE):
        with open(PRICES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_last_prices(prices):
    with open(PRICES_FILE, "w", encoding="utf-8") as f:
        json.dump(prices, f, ensure_ascii=False, indent=2)


# شروع برنامه
print("شروع چک کردن قیمت‌ها...")

last_prices = load_last_prices()

for product in PRODUCTS:
    url = product["url"]
    custom_name = product["name"]
    
    price, real_name = get_torob_price(url)

    if price:
        print(f"{custom_name}: {price:,} تومان")

        if url not in last_prices:
            last_prices[url] = price
            send_telegram(f"📦 {custom_name}\n💰 قیمت فعلی: {price:,} تومان")

        elif price != last_prices[url]:
            old_price = last_prices[url]
            
            if price < old_price:
                emoji = "📉 ارزون شد!"
            else:
                emoji = "📈 گرون شد!"

            message = f"{emoji}\n\n📦 {custom_name}\n\n💰 قیمت قبلی: {old_price:,}\n💵 قیمت جدید: {price:,}"
            send_telegram(message)
            last_prices[url] = price
    else:
        print(f"نتوانستم قیمت {custom_name} رو بگیرم")

save_last_prices(last_prices)
print("تمام!")
