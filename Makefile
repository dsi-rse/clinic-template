# Makefile for clinic-template development

.PHONY: test test-basic test-local-data test-cluster test-precommit test-examples-data-science test-dashboard clean help

help:
	@echo "Available targets:"
	@echo "  test            - Run all tests"
	@echo "  test-basic      - Test basic Docker setup"
	@echo "  test-local-data - Test local data directory config"
	@echo "  test-cluster    - Test cluster configuration"
	@echo "  test-precommit  - Test pre-commit hooks"
	@echo "  test-examples-data-science - Test data-science examples scaffold"
	@echo "  test-dashboard  - Test dashboard scaffold (yes/no generation, no-Jinja-leak, token replacement)"
	@echo "  clean           - Remove test artifacts"
	@echo "  help            - Show this help message"

# Run all tests
test: test-basic test-local-data test-cluster test-precommit test-examples-data-science test-dashboard
	@echo ""
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@echo "ALL TESTS PASSED"
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Individual test targets
test-basic:
	@chmod +x tests/scenarios/test_basic.sh
	@./tests/scenarios/test_basic.sh

test-local-data:
	@chmod +x tests/scenarios/test_local_data.sh
	@./tests/scenarios/test_local_data.sh

test-cluster:
	@chmod +x tests/scenarios/test_cluster.sh
	@./tests/scenarios/test_cluster.sh

test-precommit:
	@chmod +x tests/scenarios/test_precommit.sh
	@./tests/scenarios/test_precommit.sh

test-examples-data-science:
	@chmod +x tests/scenarios/test_examples_data_science.sh
	@./tests/scenarios/test_examples_data_science.sh

test-dashboard:
	@chmod +x tests/scenarios/test_dashboard.sh
	@./tests/scenarios/test_dashboard.sh

# Clean up test artifacts
clean:
	@rm -rf /tmp/clinic-template-test
	@echo "Cleaned up test artifacts"
