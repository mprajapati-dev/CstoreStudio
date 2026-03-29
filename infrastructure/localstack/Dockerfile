FROM localstack/localstack
COPY init-aws.sh /etc/localstack/init/ready.d/init-aws.sh
COPY cors.json /etc/localstack/init/ready.d/cors.json
RUN chmod +x /etc/localstack/init/ready.d/init-aws.sh
