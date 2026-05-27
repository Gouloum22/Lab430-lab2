"""
Report view
SPDX - License - Identifier: LGPL - 3.0 - or -later
Auteurs : Gabriel C. Ullmann, Fabio Petrillo, 2025
"""
from views.template_view import get_template
from queries.read_order import get_highest_spending_users, get_best_selling_products

def show_highest_spending_users():
    """ Show report of highest spending users """
    highest_spending_users = get_highest_spending_users()

    rows = [
        f"<li>Utilisateur {user_id} : ${total_spent:.2f}</li>"
        for user_id, total_spent in highest_spending_users
    ]

    return get_template(f"""
        <h2>Les plus gros acheteurs</h2>
        <ul>
            {" ".join(rows)}
        </ul>
    """)

def show_best_sellers():
    """ Show report of best selling products """
    best_sellers = get_best_selling_products()

    rows = [
        f"<li>Article {product['product_id']} : {product['quantity_sold']} vendu(s)</li>"
        for product in best_sellers
    ]

    return get_template(f"""
        <h2>Les articles les plus vendus</h2>
        <ul>
            {" ".join(rows)}
        </ul>
    """)