FROM rabbitmq:3-management

ENV RABBITMQ_ERLANG_COOKIE "SWQOKODSQALRPCLNMEQG"
ENV RABBITMQ_DEFAULT_USER "rabbitmq"
ENV RABBITMQ_DEFAULT_PASS "rabbitmq"
ENV RABBITMQ_DEFAULT_VHOST "/"