USE cart2insights;
CREATE TABLE geolocation (
  geolocation_zip_code_prefix CHAR(5) PRIMARY KEY,
  geolocation_lat DOUBLE, geolocation_lng DOUBLE,
  geolocation_city VARCHAR(60), geolocation_state CHAR(2)
);
CREATE TABLE customers (
  customer_id CHAR(32) PRIMARY KEY,
  customer_unique_id CHAR(32) NOT NULL,
  customer_zip_code_prefix CHAR(5),
  customer_city VARCHAR(60), customer_state CHAR(2),
  INDEX idx_unique (customer_unique_id)
);
CREATE TABLE sellers (
  seller_id CHAR(32) PRIMARY KEY,
  seller_zip_code_prefix CHAR(5),
  seller_city VARCHAR(60), seller_state CHAR(2)
);
CREATE TABLE product_category_translation (
  product_category_name VARCHAR(80) PRIMARY KEY,
  product_category_name_english VARCHAR(80)
);
CREATE TABLE products (
  product_id CHAR(32) PRIMARY KEY,
  product_category_name VARCHAR(80),
  product_name_length INT, product_description_length INT, product_photos_qty INT,
  product_weight_g DOUBLE, product_length_cm DOUBLE,
  product_height_cm DOUBLE, product_width_cm DOUBLE,
  FOREIGN KEY (product_category_name) REFERENCES product_category_translation(product_category_name)
);
CREATE TABLE orders (
  order_id CHAR(32) PRIMARY KEY,
  customer_id CHAR(32) NOT NULL,
  order_status VARCHAR(20),
  order_purchase_timestamp DATETIME, order_approved_at DATETIME,
  order_delivered_carrier_date DATETIME, order_delivered_customer_date DATETIME,
  order_estimated_delivery_date DATETIME,
  FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
  INDEX idx_purchase (order_purchase_timestamp)
);
CREATE TABLE order_items (
  order_id CHAR(32), order_item_id INT,
  product_id CHAR(32) NOT NULL, seller_id CHAR(32) NOT NULL,
  shipping_limit_date DATETIME,
  price DECIMAL(10,2), freight_value DECIMAL(10,2),
  PRIMARY KEY (order_id, order_item_id),
  FOREIGN KEY (order_id) REFERENCES orders(order_id),
  FOREIGN KEY (product_id) REFERENCES products(product_id),
  FOREIGN KEY (seller_id) REFERENCES sellers(seller_id)
);
CREATE TABLE order_payments (
  order_id CHAR(32), payment_sequential INT,
  payment_type VARCHAR(20), payment_installments INT, payment_value DECIMAL(10,2),
  PRIMARY KEY (order_id, payment_sequential),
  FOREIGN KEY (order_id) REFERENCES orders(order_id)
);
CREATE TABLE order_reviews (
  order_id CHAR(32) PRIMARY KEY,
  review_id CHAR(32), review_score TINYINT,
  review_comment_title VARCHAR(255), review_comment_message TEXT,
  review_creation_date DATETIME, review_answer_timestamp DATETIME,
  FOREIGN KEY (order_id) REFERENCES orders(order_id),
  INDEX idx_review (review_id)
);