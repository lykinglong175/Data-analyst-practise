{{ config(materialized='view') }}

select
    id              as order_item_id,
    order_id,
    product_id,
    quantity,
    unit_price,
    quantity * unit_price as subtotal
from {{ ref('raw_order_items') }}