# Cart2Insights Data Dictionary

![ER Diagram](er_diagram.png)

### customers (99,441 rows)
| Column | Type | Key | Description |
|---|---|---|---|
| customer_id | CHAR(32) | PK | Unique key per order; does not identify a unique person |
| customer_unique_id | CHAR(32) | — | Unique key per actual customer (stable across multiple orders) |
| customer_zip_code_prefix | CHAR(5) | — | First 5 digits of customer postal code |
| customer_city | VARCHAR(60) | — | Customer city name |
| customer_state | CHAR(2) | — | Customer Brazilian state code |

### geolocation (19,015 rows after cleaning)
| Column | Type | Key | Description |
|---|---|---|---|
| geolocation_zip_code_prefix | CHAR(5) | PK | First 5 digits of postal code |
| geolocation_lat | DOUBLE | — | Latitude coordinate (mean, aggregated from raw 1,000,163 rows down to one row per zip prefix) |
| geolocation_lng | DOUBLE | — | Longitude coordinate (mean) |
| geolocation_city | VARCHAR(60) | — | Most common city name for this zip prefix |
| geolocation_state | CHAR(2) | — | Most common Brazilian state code for this zip prefix |

### order_items (112,650 rows)
| Column | Type | Key | Description |
|---|---|---|---|
| order_id | CHAR(32) | PK, FK | Foreign key to `orders.order_id` (Composite PK with `order_item_id`) |
| order_item_id | INT | PK | Sequential number identifying item inside the same order |
| product_id | CHAR(32) | FK | Foreign key to `products.product_id` |
| seller_id | CHAR(32) | FK | Foreign key to `sellers.seller_id` |
| shipping_limit_date | DATETIME | — | Seller shipping limit date for handling order |
| price | DECIMAL(10,2) | — | Item price |
| freight_value | DECIMAL(10,2) | — | Item freight (shipping) cost |

### order_payments (103,881 rows after cleaning)
| Column | Type | Key | Description |
|---|---|---|---|
| order_id | CHAR(32) | PK, FK | Foreign key to `orders.order_id` (Composite PK with `payment_sequential`) |
| payment_sequential | INT | PK | Sequence number for multi-payment orders |
| payment_type | VARCHAR(20) | — | Payment method (credit_card, boleto, voucher, debit_card) — `not_defined` rows removed in cleaning |
| payment_installments | INT | — | Number of installments chosen by customer |
| payment_value | DECIMAL(10,2) | — | Total transaction value of the payment |

### order_reviews (98,673 rows after cleaning)
| Column | Type | Key | Description |
|---|---|---|---|
| order_id | CHAR(32) | PK, FK | Foreign key to `orders.order_id`; one review kept per order (latest, by answer timestamp) |
| review_id | CHAR(32) | — | Original review identifier (not unique as a key in source data — some orders had multiple reviews) |
| review_score | TINYINT | — | Customer satisfaction rating from 1 to 5 |
| review_comment_title | VARCHAR(255) | — | Title of customer review comment |
| review_comment_message | TEXT | — | Body text of customer review comment |
| review_creation_date | DATETIME | — | Timestamp when survey was sent to customer |
| review_answer_timestamp | DATETIME | — | Timestamp when customer submitted review |

### orders (99,441 rows)
| Column | Type | Key | Description |
|---|---|---|---|
| order_id | CHAR(32) | PK | Unique identifier for each order |
| customer_id | CHAR(32) | FK | Foreign key to `customers.customer_id` |
| order_status | VARCHAR(20) | — | Status of the order (e.g., delivered, shipped, canceled) |
| order_purchase_timestamp | DATETIME | — | Timestamp when the order was placed |
| order_approved_at | DATETIME | — | Timestamp when payment was approved |
| order_delivered_carrier_date | DATETIME | — | Timestamp when order was handed to logistics partner |
| order_delivered_customer_date | DATETIME | — | Actual delivery date to customer (nulled if earlier than purchase date — data error) |
| order_estimated_delivery_date | DATETIME | — | Estimated delivery date promised to customer |

### products (32,951 rows)
| Column | Type | Key | Description |
|---|---|---|---|
| product_id | CHAR(32) | PK | Unique identifier for each product |
| product_category_name | VARCHAR(80) | FK | Foreign key to `product_category_translation.product_category_name`; missing values filled as `'unknown'` |
| product_name_length | INT | — | Character length of product title (renamed from raw `product_name_lenght`) |
| product_description_length | INT | — | Character length of product description (renamed from raw `product_description_lenght`) |
| product_photos_qty | INT | — | Number of product photos published |
| product_weight_g | DOUBLE | — | Product weight in grams |
| product_length_cm | DOUBLE | — | Product length in centimeters |
| product_height_cm | DOUBLE | — | Product height in centimeters |
| product_width_cm | DOUBLE | — | Product width in centimeters |

### sellers (3,095 rows)
| Column | Type | Key | Description |
|---|---|---|---|
| seller_id | CHAR(32) | PK | Unique identifier for each seller |
| seller_zip_code_prefix | CHAR(5) | — | First 5 digits of seller postal code |
| seller_city | VARCHAR(60) | — | Seller city location |
| seller_state | CHAR(2) | — | Seller Brazilian state code |

### product_category_translation (74 rows after cleaning)
| Column | Type | Key | Description |
|---|---|---|---|
| product_category_name | VARCHAR(80) | PK | Category name in Portuguese (71 raw + 3 added for categories present in `products` but missing from the original translation file) |
| product_category_name_english | VARCHAR(80) | — | Category name translated into English |

## Relationships

- `orders.customer_id` → `customers.customer_id`
- `order_items.order_id` → `orders.order_id`
- `order_items.product_id` → `products.product_id`
- `order_items.seller_id` → `sellers.seller_id`
- `order_payments.order_id` → `orders.order_id`
- `order_reviews.order_id` → `orders.order_id`
- `products.product_category_name` → `product_category_translation.product_category_name`
- `customers.customer_zip_code_prefix` / `sellers.seller_zip_code_prefix` → `geolocation.geolocation_zip_code_prefix` (Logical link only, not enforced as a DB constraint, since zip prefixes repeat across many individual addresses)

## Key distinction: customer_id vs customer_unique_id

`customer_id` is generated fresh for every order — one customer placing 3 orders gets 3 different `customer_id`s. `customer_unique_id` is the one that's stable per person. **Any repeat-customer or customer-lifetime analysis must group by `customer_unique_id`, not `customer_id`**, or every customer looks like a first-time buyer.