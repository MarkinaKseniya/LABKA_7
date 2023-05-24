create table currency_rates (
	id SERIAL PRIMARY KEY,
	base_currency VARCHAR(3) NOT NULL
);

create table currency_rates_values (
	id SERIAL PRIMARY KEY,
	currency_code VARCHAR(3) NOT NULL,
	rate NUMERIC NOT NULL,
	currency_rate_id INTEGER REFERENCES currency_rates(id)
);

create table admins (
	id INTEGER PRIMARY KEY,
	chat_id VARCHAR(10)
);