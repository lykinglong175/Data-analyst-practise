{{ config(materialized='table') }}

{% set order_statuses = ['completed', 'returned'] %}

with products as (
    select * from {{ ref('stg_products') }}
),

order_items as (
    select * from {{ ref('stg_order_items') }}
),

orders as (
    select * from {{ ref('stg_orders') }}
),

product_sales as (
    select
        oi.product_id,
        {% for status in order_statuses %}
        sum(case when o.status = '{{ status }}'
            then oi.quantity else 0 end)    as {{ status }}_quantity,
        sum(case when o.status = '{{ status }}'
            then oi.subtotal else 0 end)    as {{ status }}_revenue,
        {% endfor %}
        sum(oi.quantity)                    as total_quantity,
        sum(oi.subtotal)                    as total_revenue
    from order_items oi
    left join orders o on oi.order_id = o.order_id
    group by oi.product_id
),

final as (
    select
        p.product_id,
        p.product_name,
        p.category,
        p.price,
        p.cost,
        p.margin,
        coalesce(ps.total_quantity, 0)      as total_quantity_sold,
        coalesce(ps.total_revenue, 0)       as total_revenue,
        coalesce(ps.completed_quantity, 0)  as completed_quantity,
        coalesce(ps.completed_revenue, 0)   as completed_revenue,
        coalesce(ps.returned_quantity, 0)   as returned_quantity,
        coalesce(ps.returned_revenue, 0)    as returned_revenue
    from products p
    left join product_sales ps on p.product_id = ps.product_id
)

select * from final