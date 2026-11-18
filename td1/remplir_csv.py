import sqlite3
import csv

# Connexion à la base de données (chemin basé sur ton arborescence VS Code)
conn = sqlite3.connect('data/boutique.sqlite')
cursor = conn.cursor()

# L'intégralité des 20 requêtes SQL formatées sur une ligne pour le CSV
requetes = {
    "C01": "SELECT COALESCE(SUM(o.quantity_product * p.price), 0) AS revenue_cents FROM orders o JOIN product p ON o.product_id = p.product_id WHERE o.date >= '2026-03-01 00:00:00' AND o.date < '2026-06-01 00:00:00';",
    "C02": "SELECT COALESCE(SUM(o.quantity_product * p.price), 0) AS revenue_cents FROM customers c JOIN orders o ON c.customer_id = o.customer_id JOIN product p ON o.product_id = p.product_id WHERE CAST(strftime('%Y.%m%d', '2026-09-25') - strftime('%Y.%m%d', c.birth_date) AS INTEGER) = 25;",
    "C03": "SELECT COALESCE(SUM(o.quantity_product * p.price), 0) AS revenue_cents FROM orders o JOIN product p ON o.product_id = p.product_id WHERE o.date >= '2026-01-01 00:00:00' AND o.date < '2026-07-01 00:00:00' AND p.product_id IN ('a', 'b', 'c');",
    "C04": "SELECT COALESCE(SUM(o.quantity_product * p.price), 0) AS revenue_cents FROM orders o JOIN product p ON o.product_id = p.product_id WHERE o.date >= '2026-01-01 00:00:00' AND o.date < '2026-10-01 00:00:00';",
    "C05": "SELECT COALESCE(SUM(o.quantity_product * p.price), 0) AS revenue_cents FROM orders o JOIN product p ON o.product_id = p.product_id WHERE o.date >= '2026-06-01 00:00:00' AND o.date < '2026-06-02 00:00:00';",
    "C06": "SELECT COALESCE(SUM(o.quantity_product * p.price), 0) AS revenue_cents FROM orders o JOIN product p ON o.product_id = p.product_id WHERE o.date >= '2025-01-01 00:00:00' AND o.date < '2026-01-01 00:00:00';",
    "C07": "SELECT COALESCE(SUM(o.quantity_product * p.price), 0) AS revenue_cents FROM orders o JOIN product p ON o.product_id = p.product_id WHERE o.date >= '2026-05-31 00:00:00' AND o.date < '2026-06-01 00:00:00';",
    "C08": "SELECT COALESCE(SUM(o.quantity_product * p.price), 0) AS revenue_cents FROM customers c JOIN orders o ON c.customer_id = o.customer_id JOIN product p ON o.product_id = p.product_id WHERE CAST(strftime('%Y.%m%d', '2026-09-24') - strftime('%Y.%m%d', c.birth_date) AS INTEGER) = 25;",
    "C09": "SELECT COALESCE(SUM(o.quantity_product * p.price), 0) AS revenue_cents FROM customers c JOIN orders o ON c.customer_id = o.customer_id JOIN product p ON o.product_id = p.product_id WHERE CAST(strftime('%Y.%m%d', '2026-09-26') - strftime('%Y.%m%d', c.birth_date) AS INTEGER) = 25;",
    "C10": "SELECT COALESCE(SUM(o.quantity_product * p.price), 0) AS revenue_cents FROM customers c JOIN orders o ON c.customer_id = o.customer_id JOIN product p ON o.product_id = p.product_id WHERE CAST(strftime('%Y.%m%d', o.date) - strftime('%Y.%m%d', c.birth_date) AS INTEGER) = 25;",
    "C11": "SELECT COALESCE(SUM(o.quantity_product * p.price), 0) AS revenue_cents FROM customers c JOIN orders o ON c.customer_id = o.customer_id JOIN product p ON o.product_id = p.product_id WHERE CAST(strftime('%Y.%m%d', '2026-12-01') - strftime('%Y.%m%d', c.birth_date) AS INTEGER) = 25;",
    "C12": "SELECT COALESCE(SUM(o.quantity_product * p.price), 0) AS revenue_cents FROM orders o JOIN product p ON o.product_id = p.product_id WHERE p.product_id IN ('a', 'b', 'c');",
    "C13": "SELECT COALESCE(SUM(o.quantity_product * p.price), 0) AS revenue_cents FROM orders o JOIN product p ON o.product_id = p.product_id WHERE o.date >= '2026-04-01 00:00:00' AND o.date < '2026-05-01 00:00:00' AND p.product_id IN ('a', 'c');",
    "C14": "SELECT COALESCE(SUM(o.quantity_product * p.price), 0) AS revenue_cents FROM orders o JOIN product p ON o.product_id = p.product_id WHERE o.date >= '2026-10-01 00:00:00' AND o.date < '2026-12-01 00:00:00' AND p.product_id IN ('a', 'b', 'c');",
    "C15": "SELECT COALESCE(SUM(o.quantity_product * p.price), 0) AS revenue_cents FROM customers c JOIN orders o ON c.customer_id = o.customer_id JOIN product p ON o.product_id = p.product_id WHERE o.date >= '2026-03-01 00:00:00' AND o.date < '2026-06-01 00:00:00' AND CAST(strftime('%Y.%m%d', '2026-09-25') - strftime('%Y.%m%d', c.birth_date) AS INTEGER) = 25;",
    "C16": "SELECT COALESCE(SUM(o.quantity_product * p.price), 0) AS revenue_cents FROM customers c JOIN orders o ON c.customer_id = o.customer_id JOIN product p ON o.product_id = p.product_id WHERE CAST(strftime('%Y.%m%d', '2026-09-25') - strftime('%Y.%m%d', c.birth_date) AS INTEGER) = 25 AND p.product_id IN ('a', 'b', 'c');",
    "C17": "SELECT COALESCE(SUM(o.quantity_product * p.price), 0) AS revenue_cents FROM customers c JOIN orders o ON c.customer_id = o.customer_id JOIN product p ON o.product_id = p.product_id WHERE o.date >= '2026-01-01 00:00:00' AND o.date < '2026-07-01 00:00:00' AND CAST(strftime('%Y.%m%d', '2026-09-25') - strftime('%Y.%m%d', c.birth_date) AS INTEGER) = 25 AND p.product_id IN ('a', 'b', 'c');",
    "C18": "SELECT COALESCE(SUM(o.quantity_product * p.price), 0) AS revenue_cents FROM customers c JOIN orders o ON c.customer_id = o.customer_id JOIN product p ON o.product_id = p.product_id WHERE o.date >= '2026-05-01 00:00:00' AND o.date < '2026-06-01 00:00:00' AND CAST(strftime('%Y.%m%d', o.date) - strftime('%Y.%m%d', c.birth_date) AS INTEGER) = 25;",
    "C19": "SELECT COALESCE(SUM(o.quantity_product * p.price), 0) AS revenue_cents FROM customers c JOIN orders o ON c.customer_id = o.customer_id JOIN product p ON o.product_id = p.product_id WHERE o.date >= '2026-09-01 00:00:00' AND o.date < '2026-10-01 00:00:00' AND CAST(strftime('%Y.%m%d', '2026-09-25') - strftime('%Y.%m%d', c.birth_date) AS INTEGER) = 25 AND p.product_id = 'd';",
    "C20": "SELECT COALESCE(SUM(o.quantity_product * p.price), 0) AS revenue_cents FROM orders o JOIN product p ON o.product_id = p.product_id WHERE o.date >= '2026-06-01 00:00:00' AND o.date < '2026-09-01 00:00:00';"
}

# Écriture dans le fichier CSV
with open('reference-td1.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['case_id', 'sql', 'revenue_cents'])
    for q_id, sql in requetes.items():
        cursor.execute(sql)
        resultat = cursor.fetchone()[0]
        writer.writerow([q_id, sql, resultat])

print("Fichier reference-td1.csv rempli avec succès !")
conn.close()