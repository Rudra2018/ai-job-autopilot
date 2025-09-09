#!/bin/bash

# AI Job Autopilot - SSL Certificate Setup
# Automated SSL certificate generation with Let's Encrypt

set -e

# Configuration
DOMAIN="job-autopilot.ankitthakur.dev"
EMAIL="hacking4bucks@gmail.com"
WEBROOT="/var/www/html"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
    exit 1
}

check_prerequisites() {
    log "Checking prerequisites for SSL setup..."
    
    # Check if running as root
    if [[ $EUID -ne 0 ]]; then
        error "This script must be run as root (use sudo)"
    fi
    
    # Check if domain is accessible
    if ! ping -c 1 "$DOMAIN" &> /dev/null; then
        warn "Domain $DOMAIN is not accessible. Make sure DNS is configured properly."
    fi
    
    log "Prerequisites check completed ✅"
}

install_certbot() {
    log "Installing Certbot..."
    
    # Update package list
    apt-get update
    
    # Install Certbot
    apt-get install -y certbot python3-certbot-nginx
    
    log "Certbot installed successfully ✅"
}

setup_nginx() {
    log "Setting up Nginx configuration..."
    
    # Install Nginx if not present
    if ! command -v nginx &> /dev/null; then
        apt-get install -y nginx
    fi
    
    # Create basic configuration for certificate validation
    cat > /etc/nginx/sites-available/ai-job-autopilot-ssl << EOF
server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN;
    
    location /.well-known/acme-challenge/ {
        root $WEBROOT;
    }
    
    location / {
        return 301 https://\$server_name\$request_uri;
    }
}
EOF
    
    # Enable the site
    ln -sf /etc/nginx/sites-available/ai-job-autopilot-ssl /etc/nginx/sites-enabled/
    
    # Remove default site if it exists
    rm -f /etc/nginx/sites-enabled/default
    
    # Test and reload Nginx
    nginx -t && systemctl reload nginx
    
    log "Nginx configuration completed ✅"
}

generate_ssl_certificate() {
    log "Generating SSL certificate with Let's Encrypt..."
    
    # Create webroot directory
    mkdir -p "$WEBROOT"
    
    # Generate certificate
    certbot certonly \
        --webroot \
        --webroot-path="$WEBROOT" \
        --email "$EMAIL" \
        --agree-tos \
        --non-interactive \
        --domains "$DOMAIN,www.$DOMAIN"
    
    if [ $? -eq 0 ]; then
        log "SSL certificate generated successfully ✅"
    else
        error "Failed to generate SSL certificate"
    fi
}

install_full_nginx_config() {
    log "Installing full Nginx configuration with SSL..."
    
    # Copy our production Nginx config
    cp nginx.conf /etc/nginx/sites-available/ai-job-autopilot
    
    # Enable the site
    ln -sf /etc/nginx/sites-available/ai-job-autopilot /etc/nginx/sites-enabled/
    
    # Remove the temporary SSL setup
    rm -f /etc/nginx/sites-enabled/ai-job-autopilot-ssl
    
    # Test and reload Nginx
    nginx -t && systemctl reload nginx
    
    log "Full Nginx configuration installed ✅"
}

setup_auto_renewal() {
    log "Setting up automatic SSL certificate renewal..."
    
    # Create renewal hook
    cat > /etc/letsencrypt/renewal-hooks/post/nginx-reload << 'EOF'
#!/bin/bash
systemctl reload nginx
EOF
    
    chmod +x /etc/letsencrypt/renewal-hooks/post/nginx-reload
    
    # Test renewal process
    certbot renew --dry-run
    
    log "Auto-renewal setup completed ✅"
}

setup_firewall() {
    log "Configuring firewall rules..."
    
    # Install UFW if not present
    if ! command -v ufw &> /dev/null; then
        apt-get install -y ufw
    fi
    
    # Configure firewall rules
    ufw default deny incoming
    ufw default allow outgoing
    ufw allow ssh
    ufw allow 'Nginx Full'
    
    # Enable firewall
    echo "y" | ufw enable
    
    log "Firewall configuration completed ✅"
}

verify_ssl() {
    log "Verifying SSL installation..."
    
    # Check certificate validity
    if openssl x509 -in /etc/letsencrypt/live/$DOMAIN/fullchain.pem -text -noout | grep -q "$DOMAIN"; then
        log "SSL certificate is valid ✅"
    else
        error "SSL certificate verification failed"
    fi
    
    # Test HTTPS connection
    if curl -Is https://$DOMAIN | head -1 | grep -q "200 OK"; then
        log "HTTPS connection test successful ✅"
    else
        warn "HTTPS connection test failed - check DNS and firewall settings"
    fi
}

show_ssl_info() {
    echo -e "${BLUE}"
    echo "=================================================="
    echo "🔒 SSL Setup Completed Successfully!"
    echo "=================================================="
    echo -e "${NC}"
    
    echo -e "${GREEN}SSL Certificate Details:${NC}"
    echo "• Domain: $DOMAIN"
    echo "• Certificate Path: /etc/letsencrypt/live/$DOMAIN/"
    echo "• Auto-Renewal: ✅ Enabled"
    echo "• Firewall: ✅ Configured"
    
    echo -e "\n${GREEN}URLs:${NC}"
    echo "• HTTPS: https://$DOMAIN"
    echo "• WWW: https://www.$DOMAIN"
    
    echo -e "\n${GREEN}Certificate Expiry:${NC}"
    openssl x509 -in /etc/letsencrypt/live/$DOMAIN/fullchain.pem -dates -noout | sed 's/^/• /'
    
    echo -e "\n${YELLOW}Important Commands:${NC}"
    echo "• Renew certificates: certbot renew"
    echo "• Check certificate status: certbot certificates"
    echo "• Reload Nginx: systemctl reload nginx"
    echo "• Check Nginx status: systemctl status nginx"
    
    echo ""
}

main() {
    echo -e "${BLUE}"
    echo "=================================================="
    echo "🔒 AI Job Autopilot - SSL Certificate Setup"
    echo "=================================================="
    echo -e "${NC}"
    
    check_prerequisites
    install_certbot
    setup_nginx
    generate_ssl_certificate
    install_full_nginx_config
    setup_auto_renewal
    setup_firewall
    verify_ssl
    show_ssl_info
    
    log "🔒 SSL setup completed! Your AI Job Autopilot is now secured with HTTPS."
}

# Run main function
main "$@"