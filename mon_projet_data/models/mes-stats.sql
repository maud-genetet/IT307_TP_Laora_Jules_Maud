{{ config(materialized='table') }}

SELECT
    owner_user_id,
    COUNT(id) as nombre_de_posts,
    SUM(score) as score_total
FROM
    coursbigquery-477209.tp_kafka.posts
WHERE
    owner_user_id IS NOT NULL
GROUP BY
    owner_user_id
ORDER BY
    nombre_de_posts DESC
LIMIT 10