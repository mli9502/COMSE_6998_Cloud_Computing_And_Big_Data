docker_build:
	docker build -t guignol/hw0 .
docker_run:
	# -p host_port:docker_port
	docker run -p 9090:9000 -d guignol/hw0
docker_kill:
	docker kill $$(docker ps -q)
