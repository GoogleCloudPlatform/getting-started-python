.PHONY: all
all: deploy

.PHONY: create-cluster
create-cluster:
	gcloud container clusters create bookshelf \
		--scope "https://www.googleapis.com/auth/userinfo.email","cloud-platform"

.PHONY: create-bucket
create-bucket:
	gsutil mb gs://$(GCLOUD_PROJECT)
    gsutil defacl set public-read gs://$(GCLOUD_PROJECT)

.PHONY: build
build:
	docker build -t gcr.io/$(GCLOUD_PROJECT)/bookshelf .

.PHONY: push
push: build
	gcloud docker push gcr.io/$(GCLOUD_PROJECT)/bookshelf

.PHONY: template
template:
	sed -i ".tmpl" "s/\$$GCLOUD_PROJECT/$(GCLOUD_PROJECT)/g" bookshelf-frontend.yaml
	sed -i ".tmpl" "s/\$$GCLOUD_PROJECT/$(GCLOUD_PROJECT)/g" bookshelf-worker.yaml

.PHONY: deploy-frontend
deploy-frontend: push template
	kubectl create -f bookshelf-frontend.yaml

.PHONY: deploy-worker
deploy-worker: push template
	kubectl create -f bookshelf-worker.yaml

.PHONY: deploy
deploy: deploy-frontend deploy-worker

.PHONY: delete
delete:
	kubectl delete rc bookshelf-frontend
	kubectl delete rc bookshelf-worker
	kubectl delete service bookshelf-frontend
