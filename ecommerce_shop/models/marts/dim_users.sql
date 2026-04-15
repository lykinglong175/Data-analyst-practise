{{config(
    materialized='table',

)}}

with users as (
    select
        *
    from {{ ref('stg_users') }}
),

orders as (
    select * from {{ ref('stg_orders') }}
),


order_items as (
    select * from {{ ref('stg_order_items') }}
),

user_orders as (
    select
        o.user_id,
        count(distinct o.order_id) as total_orders,
        sum(oi.subtotal) as total_spent,
        min(o.order_date) as first_order_date,
        max(o.order_date) as last_order_date,
        count(case when o.status='returned' then 1 end) as total_returns
    from orders o
    left join order_items oi on o.order_id = oi.order_id
    group by o.user_id
),

final as (
    select
        u.user_id,
        u.name,
        u.email,
        u.country,
        u.created_at,
        coalesce(uo.total_orders,0) as total_orders,
        coalesce(uo.total_spent,0) as total_spent,
        coalesce(uo.total_returns,0) as total_returns,
        uo.first_order_date,
        uo.last_order_date
    from users u
    left join user_orders uo on u.user_id = uo.user_id
)

select * from final