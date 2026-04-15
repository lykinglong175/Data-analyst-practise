{{ config(materialized='view') }}

select
    id          as order_id,
    user_id,
    created_at  as order_date,
    status
from {{ ref('raw_orders') }}