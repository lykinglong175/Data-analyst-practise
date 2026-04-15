{{config(
    materialized='view',

)}}

select
    id          as product_id,
    name        as product_name,
    category,
    price,
    cost,
    price - cost as margin
from {{ ref('raw_products') }}