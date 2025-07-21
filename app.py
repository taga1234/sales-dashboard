from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import matplotlib.pyplot as plt
import os

app = Flask(__name__)

# Создаем папку static если её нет
if not os.path.exists('static'):
    os.makedirs('static')


def process_data():
    """Функция для обработки данных и создания графика"""
    try:
        df = pd.read_csv('dashboard_data.csv')
        required_columns = {'date', 'product', 'quantity'}
        if not required_columns.issubset(df.columns):
            return {'Ошибка': 'В файле нет нужных столбцов: date, product, quantity'}
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
        plt.xticks([1, 2, 3], ['Январь', 'Февраль', 'Март'])
        plt.grid(axis='y', alpha=0.3)
        plt.tight_layout()
        plt.savefig('static/sales_by_month.png')
        plt.close()  # Важно закрыть фигуру

        return top3_products
    except Exception as e:
        return {'Ошибка': str(e)}


@app.route('/')
def dashboard():
    top_products = process_data()
    return render_template('dashboard.html', top_products=top_products)


@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' in request.files:
            file = request.files['file']
            if file.filename.endswith('.csv'):
                file.save('dashboard_data.csv')
                return redirect(url_for('dashboard'))
    return '''
    <h2>Загрузка новых данных</h2>
    <form method="post" enctype="multipart/form-data">
        <input type="file" name="file" accept=".csv">
        <input type="submit" value="Загрузить">
    </form>
    <br>
    <a href="/">← Назад к дашборду</a>
    '''


if __name__ == '__main__':
    app.run(debug=True)
