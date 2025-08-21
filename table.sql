CREATE TABLE IF NOT EXISTS expenses (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    category VARCHAR(50) NOT NULL,
    payment_method VARCHAR(50) NOT NULL
);
CREATE TABLE IF NOT EXISTS budgets (
    id SERIAL PRIMARY KEY,
    category VARCHAR(50) NOT NULL UNIQUE,
    monthly_budget DECIMAL(10, 2) NOT NULL,
    annual_budget DECIMAL(10, 2) NOT NULL
);
CREATE TABLE IF NOT EXISTS income (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    source VARCHAR(100) NOT NULL
);