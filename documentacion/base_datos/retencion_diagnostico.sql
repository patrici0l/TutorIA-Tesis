-- Diagnóstico interno sin contenido ni secretos; no ejecuta purga ni define TTL.
BEGIN TRANSACTION READ ONLY;

SELECT status, count(*) AS generation_records,
       count(generation_started_at) AS persistent_reservations,
       count(adaptation_snapshot) AS profile_snapshots,
       count(resource) AS resource_snapshots
FROM generaciones_contenido
GROUP BY status ORDER BY status;

SELECT count(*) AS generations_referencing_unavailable_documents
FROM generaciones_contenido AS g
WHERE EXISTS (
    SELECT 1
    FROM jsonb_array_elements(g.sources_snapshot) AS source
    LEFT JOIN documentos AS d
      ON d.id = (source->>'document_id')::uuid AND d.owner_id = g.owner_id
    WHERE d.id IS NULL OR d.deleted_at IS NOT NULL
);

COMMIT;
