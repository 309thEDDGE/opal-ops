# Cloudflare Configs for OPAL

## Initial setup

Run the following from this directory:

``` sh
export DC_HOME=$(dirname "$PWD")
cp -r templates resources
pushd resources
```

## Set up ENV file

Run the following to generate random account passwords for initial users (note you may need to install apg if it is not already on your system):

``` sh
export OPAL_PASS=$(apg -MSNCL -n 1 -m 16)
export ADMIN_PASS=$(apg -MSNCL -n 1 -m 16)
export MINIO_PASS=$(apg -MSNCL -n 1 -m 16)
sed -i "s/{{ opal_password }}/$OPAL_PASS/g" .cf.env
sed -i "s/{{ opal_admin_password }}/$ADMIN_PASS/g" .cf.env
sed -i "s/{{ minio_password }}/$MINIO_PASS/g" .cf.env
```

## Substitute URLs

The URLs have been stripped from these configs for confidentiality. To restore them or add a new custom domain, run the following:

``` sh
export DOMAIN=<desired domain>
find . -type f -exec sed -i "s/{{ domain }}/$DOMAIN/g" {} +
cp docker-compose.yml cf.docker-compose.json $DC_HOME
cp .cf.env $DC_HOME
```

## Set Cloudflare email

Run the following to set the email address for traefik"s ACME configuration:

``` sh
export EMAIL=<cloudflare email address>
sed -i "s/{{ email }}/$EMAIL/g" traefik/traefik.yml
cp traefik.yml traefik-dynamic.yml $DC_HOME/traefik
```

## Set Cloudflare API token secrets

In `opal-ops/docker-compose`, add the following line, replacing `<token>` with your own api token:

``` sh
export API_TOKEN=<token> # This token should be scoped "Zone/DNS/Write" and "Zone/Zone/Read" to allow letsencrypt to validate the domain
echo "CF_DNS_API_TOKEN=$API_TOKEN" >> $DC_HOME/.env.secrets
```

## Final Steps

Run:

``` sh
pushd $DC_HOME
sudo mkdir -p letsencrypt/certs && chown -R root:root letsencrypt
```

This will create a directory that is accessible by both the traefik and cert-dumper containers

## Run

To start OPAL with automatic certificate generation, run:

``` sh
sudo docker-compose -f docker-compose.yml -f cf.docker-compose.json up -d
```

Once all services show as `healthy` or `started`, if your cloudflare credentials are correct, you should be able to access OPAL at your configured domain, without manually adding certificates.
