FROM nginx:alpine

# Copy dashboard
COPY index.html /usr/share/nginx/html/index.html

# Add custom nginx config for SPA
RUN echo 'server { \
    listen 80; \
    location / { \
        root /usr/share/nginx/html; \
        try_files $uri $uri/ /index.html; \
        add_header Cache-Control "no-cache, no-store, must-revalidate"; \
    } \
}' > /etc/nginx/conf.d/default.conf

# Health check
HEALTHCHECK --interval=30s --timeout=3s \
    CMD wget --quiet --tries=1 --spider http://localhost/ || exit 1

EXPOSE 80

LABEL version="2.3.0" \
      description="Oracle v2.3 Governance Dashboard" \
      maintainer="oracle-deploy@example.com"
