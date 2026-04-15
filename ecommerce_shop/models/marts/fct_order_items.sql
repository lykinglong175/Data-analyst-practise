{{config(
    materialized='incremental',
    unique_key='order_item_id'
)}}

with order_items as (
    select * from {{ ref('stg_order_items') }}
),

orders as (
    select * from {{ref('stg_orders')}}

    {% if is_incremental() %}
        where order_date > (select max(order_date) from {{ this }})
    {% endif %}
),

product as (
    select * from {{ ref('stg_products') }}
),


final as (
    select
        oi.order_item_id,
        oi.order_id,
        o.user_id,
        o.order_date,
        o.status,
        p.product_id,
        p.product_name,
        p.category,
        oi.quantity,
        oi.unit_price,
        oi.subtotal,
        p.cost * oi.quantity as total_cost,
        oi.subtotal - (p.cost * oi.quantity) as gross_profit
    from order_items oi
    left join orders o on oi.order_id = o.order_id
    left join product p on oi.product_id = p.product_id
)

select * from final