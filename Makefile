.PHONY: test test-backend test-frontend coverage test-all

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

# Run all tests
test-all: test-backend test-frontend
	@echo "=== All tests passed ==="

# Quick test (no coverage)
quick: test-backend test-frontend
