# Faithful local stand-in for the w3id.org front-end: Apache 2.4 with
# mod_rewrite and per-directory .htaccess, serving the AgoraOWL PID directory
# exactly the way w3id.org does (ids/<name>/.htaccess exposed at /<name>/).
FROM httpd:2.4-alpine

RUN sed -i \
      -e 's|^#LoadModule rewrite_module|LoadModule rewrite_module|' \
      -e 's|^#LoadModule headers_module|LoadModule headers_module|' \
      /usr/local/apache2/conf/httpd.conf \
 && printf '%s\n' \
      '<Directory "/usr/local/apache2/htdocs">' \
      '    AllowOverride All' \
      '    Require all granted' \
      '</Directory>' \
      'ErrorLog /proc/self/fd/2' \
      'LogLevel warn rewrite:trace2' \
      >> /usr/local/apache2/conf/httpd.conf

# The PID directory. Mirrors perma-id/w3id.org/ids/AgoraOWL/
COPY AgoraOWL/.htaccess /usr/local/apache2/htdocs/AgoraOWL/.htaccess
