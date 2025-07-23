from flask import Flask, render_template, request, redirect, url_for
from supabase import create_client, Client
import pandas as pd
import matplotlib.pyplot as plt
import os
from datetime import datetime

app = Flask(__name__)




supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Создаем папку static если её нет
if not os.path.exists('static'):
    os.makedirs('static')


def process_data():
    """Функция для обработки данных из Supabase"""
    try:
        # Получаем данные из Supabase
        response = supabase.table('sales').select("*").execute()
        data = response.data

        if not data:
            return {'Сообщение': 'Нет данных о продажах'}

        df = pd.DataFrame(data)

        # Проверяем наличие нужных колонок
        required_columns = {'date', 'product', 'quantity'}
        if not required_columns.issubset(df.columns):
            return {'Ошибка': 'В таблице нет нужных столбцов: date, product, quantity'}

        df['date'] = pd.to_datetime(df['date'])
        df['month'] = df['date'].dt.month

        # Топ-3 товаров
        top3_products = df.groupby('product')['quantity'].sum().nlargest(3)

        # График
        monthly_sales = df.groupby('month')['quantity'].sum()

        plt.figure(figsize=(10, 6))
        plt.bar(monthly_sales.index, monthly_sales.values,
                color='skyblue', edgecolor='navy')
        plt.xlabel('Месяц')
        plt.ylabel('Количество проданных товаров')
        plt.title('Продажи по месяцам')

        # Определяем подписи месяцев
        months = {1: 'Янв', 2: 'Фев', 3: 'Мар', 4: 'Апр', 5: 'Май', 6: 'Июн',
                  7: 'Июл', 8: 'Авг', 9: 'Сен', 10: 'Окт', 11: 'Ноя', 12: 'Дек'}
        month_labels = [months.get(m, str(m)) for m in monthly_sales.index]
        plt.xticks(monthly_sales.index, month_labels)

        plt.grid(axis='y', alpha=0.3)
        plt.tight_layout()
        plt.savefig('static/sales_by_month.png')
        plt.close()

        return top3_products

    except Exception as e:
        return {'Ошибка': str(e)}


@app.route('/')
def dashboard():
    top_products = process_data()
    return render_template('dashboard.html', top_products=top_products)


@app.route('/add', methods=['GET', 'POST'])
def add_sale():
    if request.method == 'POST':
        try:
            sale_data = {
                'date': request.form['date'],
                'product': request.form['product'],
                'quantity': int(request.form['quantity']),
                'price': float(request.form['price'])
            }

            supabase.table('sales').insert(sale_data).execute()
            return redirect(url_for('dashboard'))

        except Exception as e:
            return f"Ошибка при добавлении: {str(e)}"

    return '''
    <h2>Добавить продажу</h2>
    <form method="post">
        Дата: <input type="date" name="date" required><br><br>
        Товар: <input type="text" name="product" required><br><br>
        Количество: <input type="number" name="quantity" min="1" required><br><br>
        Цена: <input type="number" step="0.01" name="price" min="0" required><br><br>
        <input type="submit" value="Добавить продажу">
    </form>
    <br>
    <a href="/">← Назад к дашборду</a>
    '''


@app.route('/api/sales')
def api_sales():
    """API endpoint для получения всех продаж"""
    try:
        response = supabase.table('sales').select("*").execute()
        return {'data': response.data}
    except Exception as e:
        return {'error': str(e)}, 500


if __name__ == '__main__':
    app.run(debug=True)
