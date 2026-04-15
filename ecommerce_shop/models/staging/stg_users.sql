{{config(
    materialized = 'view',
)}}

select id as user_id,name,email,created_at,country from {{ref('raw_users')}}
