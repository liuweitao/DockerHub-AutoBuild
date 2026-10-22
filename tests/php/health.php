<?php
header('Content-Type: application/json');
echo json_encode([
    'version' => PHP_VERSION,
    'sapi' => PHP_SAPI,
    'upload_progress' => ini_get('session.upload_progress.enabled'),
    'extensions' => get_loaded_extensions(),
]);
