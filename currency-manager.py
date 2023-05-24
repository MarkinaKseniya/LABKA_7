import uvicorn
import psycopg2
from fastapi import FastAPI, HTTPException

app = FastAPI()


def calculate_rate(source: str, target: str, sum: int):
    conn = psycopg2.connect(
        host="localhost",
        database="RPP7",
        user="postgres",
        password="postgres"
    )

    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT %(sum)s * crv.rate
            FROM public.currency_rates cr
            JOIN public.currency_rates_values crv ON cr.id = crv.currency_rate_id
            WHERE
                cr.base_currency = %(source)s
                AND crv.currency_code = %(target)s
        """, {"source": source, "target": target, "sum": sum})

        return cursor.fetchone()
    finally:
        conn.close()

@app.get("/convert")
async def convert(source: str, target: str, sum: int):
    """
        select 10 * crv.rate
        from public.currency_rates cr
        JOIN public.currency_rates_values crv ON cr.id = crv.currency_rate_id
        WHERE cr.base_currency = 'USD' AND crv.currency_code = 'RUB'
        ;

    "param_source": ""
    "param_target": ""
    :param sum:
    :return:
    """

    try:
        return {"converted": calculate_rate(source=source, target=target, sum=sum)[0]}
    except:
        raise HTTPException(status_code=500, detail="Что-то пошло не так")

@app.post("/load")
async def load(payload: dict):

    base_currency = payload["base_currency"]
    rates = payload["rates"]
    conn = psycopg2.connect(
        host="localhost",
        database="RPP7",
        user="postgres",
        password="postgres"
    )
    check_currency_lack(base_currency=base_currency)
    try:
        cursor = conn.cursor()
        cursor.execute("insert into currency_rates(base_currency) values (%(base_currency)s) RETURNING id",
                       {"base_currency": base_currency})

        base_currency_id = cursor.fetchone()

        for element in rates:
            cursor.execute("insert into currency_rates_values (currency_code, rate, currency_rate_id) values (%(currency_code)s, %(rate)s, %(currency_rate_id)s)",
                           {
                               "currency_code": element["code"],
                               "rate": element["rate"],
                               "currency_rate_id": base_currency_id
                           })

        conn.commit()
        print(f"base_currency: {base_currency}; rates: {rates}")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Не удалось сохранить данные")
    finally:
        conn.close()

def check_currency_lack(base_currency: str):
    conn = psycopg2.connect(
        host="localhost",
        database="RPP7",
        user="postgres",
        password="postgres"
    )
    cursor = conn.cursor()
    # Запрашиваем все имеющиеся валюты
    cursor.execute("SELECT 1 FROM currency_rates WHERE base_currency = %(base_currency)s",
                   {"base_currency": base_currency})
    found_currencies = cursor.fetchall()
    conn.close()
    # Если валюта уже существует, то сервис возвращает ошибку 500
    if len(found_currencies) == 1:
        raise HTTPException(status_code=500, detail="Валюта уже существует")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=10610)
