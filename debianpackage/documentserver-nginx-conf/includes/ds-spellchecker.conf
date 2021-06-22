location ~ ^(\/[\d]+\.[\d]+\.[\d]+[\.|-][\d]+)?(\/spellchecker)(\/.*)$ {
  proxy_pass http://spellchecker$3;
  proxy_http_version 1.1;
}
