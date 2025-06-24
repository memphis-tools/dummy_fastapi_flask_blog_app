FROM alpine

# set vault version
ENV VAULT_VERSION 1.17.5

# create root vault dir
RUN mkdir /vault

# download dependencies
RUN apk --no-cache add \
      bash \
      ca-certificates \
      wget \
      curl

# download and set up vault
RUN wget --quiet --max-redirect=0 --output-document=/tmp/vault.zip https://releases.hashicorp.com/vault/${VAULT_VERSION}/vault_${VAULT_VERSION}_linux_amd64.zip && \
    unzip /tmp/vault.zip -d /vault && \
    rm -f /tmp/vault.zip && \
    chmod +x /vault

# update PATH
ENV PATH="PATH=$PATH:$PWD/vault"

# add the config file
COPY ./config/vault-config.json /vault/config/vault-config.json
COPY ./policies/gitlab.json /vault/policies/gitlab.json
COPY ./scripts/build_it_up.sh /vault/scripts/build_it_up.sh
RUN chmod +x /vault/scripts/build_it_up.sh

# expose port 8200
EXPOSE 8200

# run vault
ENTRYPOINT ["/vault/scripts/build_it_up.sh"]
