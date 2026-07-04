# Makefile — Mesh Operations

NODES = 34.53.51.34 34.23.192.213 35.222.248.151 136.113.102.152 136.118.144.227
SSH_USER = openclaw
SSH_KEY = ~/.ssh/openclaw-gcp

mesh-status:
	bash mesh_status.sh

mesh-sync:
	for ip in $(NODES); do \
	  ssh -i $(SSH_KEY) $(SSH_USER)@$$ip 'cd ~/openclaw || cd ~; git pull; cp openclaw.json openclaw.json.bak; cp openclaw.json openclaw.json.last-good; openclaw config validate && openclaw config apply'; \
	done

mesh-restart:
	for ip in $(NODES); do \
	  ssh -i $(SSH_KEY) $(SSH_USER)@$$ip 'systemctl --user restart openclaw-gateway.service || sudo systemctl restart openclaw.service'; \
	done

mesh-logs:
	for ip in $(NODES); do \
	  echo "===== $$ip ====="; \
	  ssh -i $(SSH_KEY) $(SSH_USER)@$$ip 'tail -n 50 ~/openclaw/log/openclaw.log || tail -n 50 /var/log/openclaw.log'; \
	done

audit-secrets:
	for ip in $(NODES); do \
	  echo "===== $$ip ====="; \
	  ssh -i $(SSH_KEY) $(SSH_USER)@$$ip 'grep -Eir "token|secret|password" ~/openclaw || true'; \
	done

rotate-tokens:
	@echo 'Run your token rotation script or .env sync here.'
