<?php
// Development equivalent of Apache's production clean-URL rules.
$root = dirname(__DIR__);
$path = parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH);
$query = parse_url($_SERVER['REQUEST_URI'], PHP_URL_QUERY);
if (preg_match('~^/([a-zA-Z0-9-]+)\.html$~D', $path, $match)) {
    header('Location: ' . ($match[1] === 'index' ? '/' : '/' . $match[1]) . ($query !== null ? '?' . $query : ''), true, 301);
    return true;
}
if (preg_match('~^/([a-zA-Z0-9-]+)$~D', $path, $match) && is_file($root . '/' . $match[1] . '.html')) {
    header('Content-Type: text/html; charset=utf-8');
    readfile($root . '/' . $match[1] . '.html');
    return true;
}
if ($path === '/' || (realpath($root . $path) !== false && str_starts_with(realpath($root . $path), $root . DIRECTORY_SEPARATOR))) {
    return false;
}
http_response_code(404);
header('Content-Type: text/html; charset=utf-8');
readfile($root . '/404.html');
return true;
