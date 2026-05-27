## Rapport Labo 02

**Question 1** : Lorsque l'application démarre, la synchronisation entre Redis et MySQL est-elle initialement déclenchée par quelle méthode ? Veuillez inclure le code pour illustrer votre réponse.

Au démarrage, la synchronisation est déclenchée par la méthode sync_all_orders_to_redis(). Cette méthode vérifie d’abord si Redis contient déjà des commandes. Si aucune commande n’est présente dans Redis, elle charge les commandes avec get_orders_from_mysql() puis les insère dans Redis.

Code de synchronisation: 

    def sync_all_orders_to_redis():
        r = get_redis_conn()
        orders_in_redis = r.keys("order:*")

        if len(orders_in_redis) == 0:
            orders_from_mysql = get_orders_from_mysql()

            for order in orders_from_mysql:
                add_order_to_redis(
                    order.id,
                    order.user_id,
                    order.total_amount,
                    []
                )

-------------------------
**Question 2** : Quelles méthodes avez-vous utilisées pour lire des données à partir de Redis ? Veuillez inclure le code pour illustrer votre réponse.

Pour lire les données à partir de Redis, j’ai utilisé get_orders_from_redis(). Pour chaque clé, j’ai utilisé hgetall(key) afin de récupérer les champs de la commande stockée sous forme de hash Redis.

Code pour les commandes a partir de redis:

    def get_orders_from_redis(limit=9999):
        r = get_redis_conn()
        orders_in_redis = r.keys("order:*")
        orders = []

        for key in orders_in_redis:
            order_data = r.hgetall(key)

            decoded_order = {}
            for field, value in order_data.items():
                field = field.decode("utf-8") if isinstance(field, bytes) else field
                value = value.decode("utf-8") if isinstance(value, bytes) else value
                decoded_order[field] = value

            orders.append(SimpleNamespace(
                id=int(decoded_order["id"]),
                user_id=int(decoded_order["user_id"]),
                total_amount=float(decoded_order["total_amount"])
            ))

        orders = sorted(orders, key=lambda order: order.id, reverse=True)

        return orders[:limit]

-------------------------

**Question 3** : Quelles méthodes avez-vous utilisées pour ajouter des données dans Redis ? Veuillez inclure le code pour illustrer votre réponse.

Pour ajouter les commandes dans Redis, j’ai utilisé la méthode hset() de Redis. Chaque commande est stockée avec une clé unique au format order:{order_id}. Les champs id, user_id et total_amount sont enregistrés dans un hash Redis afin de pouvoir être relus rapidement par les requêtes.

Code pour ajouter a Redis:

    def add_order_to_redis(order_id, user_id, total_amount, items):
        """Insert order to Redis"""
        r = get_redis_conn()

        r.hset(
            f"order:{order_id}",
            mapping={
                "id": order_id,
                "user_id": user_id,
                "total_amount": total_amount
            }
        )

-------------------------

**Question 4** : Quelles méthodes avez-vous utilisées pour supprimer des données dans Redis ? Veuillez inclure le code pour illustrer votre réponse.

Pour supprimer une commande dans Redis, j’ai utilisé la méthode delete() de Redis. La commande est identifiée par sa clé unique au format order:{order_id}. Lorsqu’une commande est supprimée de MySQL, la même clé est supprimée de Redis afin de garder les données synchronisées.

Code pour supprimer une commande dans Redis:

    def delete_order_from_redis(order_id):
        """Delete order from Redis"""
        r = get_redis_conn()
        r.delete(f"order:{order_id}")

-------------------------

**Question 5** : Si nous souhaitions créer un rapport similaire, mais présentant les produits les plus vendus, les informations dont nous disposons actuellement dans Redis sont-elles suffisantes, ou devrions-nous chercher dans les tables sur MySQL ? Si nécessaire, quelles informations devrions-nous ajouter à Redis ? Veuillez inclure le code pour illustrer votre réponse.

Si nous voulions créer un rapport similaire pour les produits les plus vendus, les informations actuelles dans Redis ne suffisent pas, car on n’a pas encore synchronisé la quantité vendue de chaque article (order_items).
Il faudrait ajouter dans Redis, à chaque commande ajoutée, le suivi des quantités vendues par produit. Par exemple, une clé Redis par produit : product:{product_id} et utiliser incr() pour augmenter le compteur à chaque nouvelle commande.

Code pour les plus gros acheteurs:

    def get_highest_spending_users(top_n=10):
        """Return top N users who spent the most"""
        r = get_redis_conn()
        orders_in_redis = r.keys("order:*")

        expenses_by_user = defaultdict(float)

        for key in orders_in_redis:
            order_data = r.hgetall(key)

            decoded_order = {}
            for field, value in order_data.items():
                field = field.decode("utf-8") if isinstance(field, bytes) else field
                value = value.decode("utf-8") if isinstance(value, bytes) else value
                decoded_order[field] = value

            user_id = int(decoded_order["user_id"])
            total_amount = float(decoded_order["total_amount"])

            expenses_by_user[user_id] += total_amount

        highest_spending_users = sorted(
            expenses_by_user.items(),
            key=lambda item: item[1],
            reverse=True
        )

        return highest_spending_users[:top_n]

-------------------------
