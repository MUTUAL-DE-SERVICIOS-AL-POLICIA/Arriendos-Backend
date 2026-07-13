.PHONY: test test-backend test-frontend coverage check test-all

# Coverage thresholds
BACKEND_THRESHOLD := 70
FRONTEND_THRESHOLD := 85

# Backend
test-backend:
	docker exec -w /app/Arriendos-Backend arriendos-app python -m pytest --tb=short -v

coverage-backend:
	docker exec -w /app/Arriendos-Backend arriendos-app python -m pytest --cov=customers --cov=products --cov=rooms --cov=roles --cov=leases --cov=requirements --cov=records --cov=plans --cov=financials --cov=login --cov=users --cov-report=term-missing --tb=short -v

# Frontend
test-frontend:
	cd ../arriendos-frontend && npx vitest run

coverage-frontend:
	cd ../arriendos-frontend && npx vitest run --coverage

# Coverage with thresholds
check-backend:
	@echo "=== Backend Coverage Check (threshold: $(BACKEND_THRESHOLD)%) ==="
	@docker exec -w /app/Arriendos-Backend arriendos-app python -m pytest --cov=customers --cov=products --cov=rooms --cov=roles --cov=leases --cov=requirements --cov=records --cov=plans --cov=financials --cov=login --cov=users --cov-fail-under=$(BACKEND_THRESHOLD) --tb=short -v

check-frontend:
	@echo "=== Frontend Coverage Check (threshold: $(FRONTEND_THRESHOLD)%) ==="
	cd ../arriendos-frontend && npx vitest run --coverage --coverage.thresholds.lines=$(FRONTEND_THRESHOLD)

# Run all tests
test-all: test-backend test-frontend
	@echo "=== All tests passed ==="

# Run all with coverage gates
check: check-backend check-frontend
	@echo "=== Coverage thresholds met ==="

# Quick test (no coverage)
quick: test-backend test-frontend
